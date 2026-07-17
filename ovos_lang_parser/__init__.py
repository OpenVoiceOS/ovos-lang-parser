"""Multilingual language-name parsing.

Maps between spoken language names (e.g. "Portuguese", "Portugiesisch",
"Português") and IETF language codes (e.g. "pt"), in both directions,
using per-language wordlists bundled under ``res/``.
"""
import json
import os.path
import re
from functools import lru_cache
from typing import Dict, List, Tuple

from langcodes import closest_match, standardize_tag
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
    alias a wordlist (or caller) uses.
    """
    try:
        return str(standardize_tag(lang_code)).lower()
    except ValueError:
        return lang_code.lower()


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


def _closest_lang(lang: str) -> str:
    """Match ``lang`` against the languages with a bundled wordlist."""
    closest_lang, distance = closest_match(lang, LANGS)
    if distance > 10:
        raise ValueError(f"Unsupported language '{lang}' not in {LANGS}")
    return closest_lang


def get_lang_data(lang: str) -> Dict[str, str]:
    """Map spoken language names in ``lang`` to language codes.

    Multiple valid spellings may exist for the same code; every known
    spelling appears as a key. Raises ValueError if ``lang`` has no
    bundled wordlist.
    """
    return {name: code
            for code, names in _load_wordlist(_closest_lang(lang))
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

    Falls back to the primary subtag (e.g. ``pt-br`` -> ``pt``) when the
    full tag has no dedicated name, and returns ``lang_code`` unchanged
    if the wordlist has no name for it at all (or is not a string).
    """
    if not isinstance(lang_code, str):
        return lang_code
    names = {code: spoken[0]
             for code, spoken in _load_wordlist(_closest_lang(lang))
             if spoken}
    full_code = _normalize_code(lang_code)
    base_code = full_code.split("-")[0]
    return names.get(full_code) or names.get(base_code) or lang_code
