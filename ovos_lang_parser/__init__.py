"""Multilingual language-name parsing.

Maps between spoken language names (e.g. "Portuguese", "Portugiesisch",
"Português") and IETF language codes (e.g. "pt"), in both directions,
using per-language wordlists bundled under ``res/``.

BCP-47 tag resolution — standardizing a tag, and picking the closest wordlist
for a requested language — is delegated to the OVOS-spec reference matcher
(``ovos_spec_tools.language``: ``standardize_lang``, ``closest_lang``,
``lang_distance``), so this library ranks dialects identically to the rest of
the stack (OVOS-INTENT-2 §2.2). Matching a spoken *name* against the wordlist
(fuzzy, order-insensitive) is a separate concern and stays with ``match_one``.

Region and private-use dialect subtags
---------------------------------------
A code may carry a region (``ar-EG``, ``pt-AO``) or a private-use dialect
subtag (``an-x-ansotano``, ``pt-BR-x-caipira``, ``ar-IQ-x-qeltu``). The
wordlists name languages and, for a handful of cases, specific regional
varieties — they do not name every dialect. The contract is explicit:

- Standardization **preserves** region and ``-x-`` private-use subtags; a tag
  is never silently collapsed to its base language, and a private-use tag
  never raises.
- :func:`pronounce_lang` returns the most specific spoken name it has: the full
  tag's name when one exists, otherwise an explicit, documented fall back to
  the **base-language** name (``ar-EG`` -> the name of ``ar``). This is a
  lossy-but-safe fallback, not a failure — the base name is an acceptable
  answer when no dialect-specific name is bundled.
"""
import json
import os.path
import re
from functools import lru_cache
from typing import Dict, List, Tuple

from ovos_spec_tools.language import closest_lang, lang_distance, standardize_lang
from ovos_utils.parse import match_one, MatchStrategy

RES_DIR = f"{os.path.dirname(__file__)}/res"

# languages with a bundled wordlist
LANGS = sorted(entry for entry in os.listdir(RES_DIR)
               if os.path.isfile(f"{RES_DIR}/{entry}/langs.json"))


def _expand(template: str) -> List[str]:
    """Expand ``(a|b)`` alternations in a template into all variants."""
    match = re.search(r"\(([^()]*)\)", template)
    if not match:
        text = " ".join(template.split())
        return [text] if text else []
    variants = []
    for option in match.group(1).split("|"):
        expanded = template[:match.start()] + option + template[match.end():]
        for variant in _expand(expanded):
            if variant not in variants:
                variants.append(variant)
    return variants


def _normalize_code(lang_code: str) -> str:
    """Normalize a language code to its modern lowercase IETF form.

    Legacy tags are updated (e.g. ``iw`` -> ``he``, ``jw`` -> ``jv``,
    ``mo`` -> ``ro``) so the same code is returned regardless of which
    alias a wordlist (or caller) uses. Region and ``-x-`` private-use
    subtags are preserved (``an-x-ansotano`` stays ``an-x-ansotano``);
    tag comparison is case-insensitive, so the result is lowercased.

    Standardization is the OVOS-spec matcher (:func:`standardize_lang`),
    which never raises — a malformed tag is returned in a best-effort
    normalized form rather than aborting.
    """
    return standardize_lang(lang_code).lower()


@lru_cache(maxsize=None)
def _load_wordlist(lang: str) -> Tuple[Tuple[str, Tuple[str, ...]], ...]:
    """Load the wordlist for ``lang`` as (code, spoken names) pairs.

    ``lang`` must be one of ``LANGS``; codes are normalized and the order
    of spoken names from the resource file is preserved (first name is
    the canonical one).
    """
    resource_file = f"{RES_DIR}/{lang}/langs.json"
    with open(resource_file, encoding="utf-8") as f:
        data = json.load(f)
    entries = {}
    for code, names in data.items():
        if isinstance(names, str):
            names = _expand(names)
        code = _normalize_code(code)
        entries.setdefault(code, [])
        entries[code] += [n for n in names if n not in entries[code]]
    return tuple((code, tuple(names)) for code, names in entries.items())


def _closest_wordlist(lang: str) -> str:
    """Match ``lang`` against the languages with a bundled wordlist.

    Uses the OVOS-spec §2.2 fallback (:func:`closest_lang`) so a regional
    request resolves to its base wordlist (``pt-br`` -> ``pt``). Raises
    ValueError when nothing is close enough.
    """
    match = closest_lang(lang, LANGS)
    if match is None:
        raise ValueError(f"Unsupported language '{lang}' not in {LANGS}")
    return match


def get_lang_data(lang: str) -> Dict[str, str]:
    """Map spoken language names in ``lang`` to language codes.

    Multiple valid spellings may exist for the same code; every known
    spelling appears as a key. Raises ValueError if ``lang`` has no
    bundled wordlist.
    """
    return {name: code
            for code, names in _load_wordlist(_closest_wordlist(lang))
            for name in names}


def extract_langcode(text: str, lang: str) -> Tuple[str, float]:
    """Extract the language code best matching a language name in ``text``.

    ``lang`` is the language the utterance is spoken in. Returns a
    ``(langcode, confidence)`` tuple; confidence is between 0 and 1.
    A non-string or blank ``text`` yields ``("", 0.0)`` rather than raising.
    """
    langs = get_lang_data(lang)
    if not isinstance(text, str) or not text.strip():
        return "", 0.0
    tokens = text.casefold().split()
    query = " ".join(tokens)
    # An exact name match always wins over fuzzy matching. A name that
    # appears verbatim as a run of whole words in a longer utterance
    # ("quiero aprender japonés") counts as exact too; the most specific
    # (longest) such name wins, so "American English" beats "English".
    best = None  # (span, -start, code)
    for name, code in langs.items():
        name_tokens = name.casefold().split()
        span = len(name_tokens)
        for i in range(len(tokens) - span + 1) if span else ():
            if tokens[i:i + span] == name_tokens:
                key = (span, -i, code)
                if best is None or key[:2] > best[:2]:
                    best = key
                break
    if best is not None:
        return best[2], 1.0
    code, conf = match_one(query, langs, strategy=MatchStrategy.TOKEN_SET_RATIO)
    # a zero-confidence "match" is no match at all; don't return an
    # arbitrary code for it
    if not conf:
        return "", 0.0
    return code, conf


def pronounce_lang(lang_code: str, lang: str) -> str:
    """Get the spoken name of ``lang_code`` in ``lang``.

    Resolution is most-specific-first: the full tag's dedicated name when
    the wordlist has one, otherwise an explicit fall back to the
    **base-language** name. A region (``ar-EG`` -> the name of ``ar``) or a
    private-use dialect subtag (``pt-BR-x-caipira`` -> the name of ``pt``,
    ``ar-IQ-x-qeltu`` -> the name of ``ar``) that has no dedicated wordlist
    name resolves to the base-language name — a documented, lossy-but-safe
    fallback, never a crash. When the wordlist has no name for the base
    language either, ``lang_code`` is returned unchanged.
    """
    if not isinstance(lang_code, str):
        return lang_code
    names = {code: spoken[0]
             for code, spoken in _load_wordlist(_closest_wordlist(lang))
             if spoken}
    full_code = _normalize_code(lang_code)
    # base language of a regioned / private-use tag: "pt-br" -> "pt",
    # "an-x-ansotano" -> "an". The "-x-" subtag carries no base name of its
    # own, so the primary subtag is the fallback lookup key.
    base_code = full_code.split("-")[0]
    return names.get(full_code) or names.get(base_code) or lang_code
