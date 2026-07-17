# API reference

Everything is importable from the top-level package:

```python
from ovos_lang_parser import (
    extract_langcode,
    pronounce_lang,
    get_lang_data,
    LANGS,
)
```

Two ideas run through the whole API:

- A **language code** is an IETF/BCP-47 tag such as `en`, `pt`, or `pt-br`. Codes are
  normalized to their modern lowercase form, so legacy tags collapse to the current one
  (`iw` → `he`, `jw` → `jv`, `mo` → `ro`).
- The **`lang`** argument is always *the language the names are written in* — not the
  language being named. To read a French sentence, pass `lang="fr"`; the code it resolves to
  can be any language.

---

## `extract_langcode(text, lang) -> tuple[str, float]`

Find the language named in `text`, where `text` is written in `lang`.

| Parameter | Type | Meaning |
|-----------|------|---------|
| `text` | `str` | Free text that mentions a language, e.g. `"translate to German"`. |
| `lang` | `str` | The language `text` is written in (must resolve to one of `LANGS`). |

Returns `(langcode, confidence)`:

- `langcode` — the best-matching BCP-47 code.
- `confidence` — a float in `0.0`–`1.0`.

Matching works in two stages:

1. **Exact match.** If `text`, whitespace-collapsed and case-folded, equals a known name, the
   result is that code with confidence `1.0`.
2. **Fuzzy match.** Otherwise a token-set-ratio matcher scores `text` against every known
   name and returns the best one. Because it is token-set based, a clean language name
   surrounded by other words still scores `1.0` — the surrounding tokens do not count against
   it. What *does* lower the score is punctuation stuck to the name (`Chinese?`), a
   misspelling, or text with no language name at all.

```python
extract_langcode("Portuguese", "en")                  # ('pt', 1.0)   exact
extract_langcode("translate this to German", "en")    # ('de', 1.0)   name is a clean token
extract_langcode("alemão", "pt")                       # ('de', 1.0)   exact, in Portuguese
extract_langcode("inglés", "es")                       # ('en', 1.0)   exact, in Spanish
extract_langcode("say it in Mandarin Chinese?", "en")  # ('zh', 0.41)  '?' stuck to the name
```

For best results on free text, strip surrounding punctuation before calling.

### Confidence and thresholds

Because stage 2 always returns *some* best match, `extract_langcode` never signals "no
language here" on its own — text with no language mention still returns a low-confidence
guess:

```python
extract_langcode("the weather today", "en")           # e.g. ('rm', 0.45)  — noise
```

Apply a threshold suited to your input. As a rule of thumb:

- **`== 1.0`** — a clean, unambiguous name (safe to trust).
- **`>= 0.7`** — a confident mention (good default for NER/routing).
- **`< 0.5`** — treat as "no language mentioned".

Tune against your own data; noisy free text warrants a higher floor than short labels, and
stripping punctuation first keeps genuine mentions above the threshold.

### Errors

Raises `ValueError` if `lang` has no bundled wordlist and is too far from any that does.

---

## `pronounce_lang(langcode, lang) -> str`

The human-readable name of `langcode`, rendered in the language `lang`.

| Parameter | Type | Meaning |
|-----------|------|---------|
| `langcode` | `str` | The BCP-47 code to name, e.g. `"de"` or `"pt-br"`. |
| `lang` | `str` | The language the returned name should be written in. |

```python
pronounce_lang("de", "en")       # 'German'
pronounce_lang("de", "pt")       # 'Alemão'
pronounce_lang("pt-br", "en")    # 'Brazilian Portuguese'
pronounce_lang("pt-br", "pt")    # 'Português do Brasil'
```

Resolution order:

1. The name for the full tag (`pt-br`), if the wordlist has one.
2. Otherwise the name for the base subtag (`pt`).
3. Otherwise `langcode` returned unchanged (never raises for an unknown code):

```python
pronounce_lang("xx-YY", "en")    # 'xx-YY'
```

When a language has several spellings, the **first** listed in the wordlist is treated as
canonical and is what `pronounce_lang` returns.

---

## `get_lang_data(lang) -> dict[str, str]`

The full `{name: code}` lookup table for names written in `lang`. Every known spelling of a
language appears as a key, all mapping to the same code.

```python
data = get_lang_data("en")
data["German"]      # 'de'
data["Portuguese"]  # 'pt'
len(data)           # hundreds of entries
```

Use this when you want to do your own matching, build an autocomplete list, or inspect what
the library knows. Raises `ValueError` if `lang` has no bundled wordlist.

---

## `LANGS -> list[str]`

Sorted list of the language codes whose names the library can parse — i.e. valid values for
the `lang` argument.

```python
import ovos_lang_parser
ovos_lang_parser.LANGS
# ['an', 'ar', 'ast', 'bg', 'ca', 'da', 'de', 'en', 'es', 'eu', 'fr',
#  'fy', 'gl', 'hr', 'it', 'kab', 'nl', 'oc', 'pt', 'ro', 'sk']
```

`lang` does not have to be an exact member — it is matched to the closest available wordlist,
so `en-us` and `en-gb` both use the `en` list. Only a `lang` with no close match raises.

---

## Notes for advanced use

- **Caching.** Wordlists are loaded once and memoized (`lru_cache`), so repeated calls are
  cheap. The first call for a given `lang` pays the JSON-load cost.
- **Thread safety.** All functions are pure reads over immutable in-memory data; safe to call
  concurrently.
- **No network, no models.** Everything resolves from bundled JSON under the package's `res/`
  directory. See [coverage.md](coverage.md) for the data model.
