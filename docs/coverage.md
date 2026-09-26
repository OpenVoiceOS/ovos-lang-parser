# Coverage and data model

## Languages you can parse names in

`extract_langcode`, `pronounce_lang`, and `get_lang_data` all take a `lang` argument:
the language the *names* are written in. The library ships wordlists for **21** of them:

| Code | Language | Code | Language | Code | Language |
|------|----------|------|----------|------|----------|
| `an` | Aragonese | `de` | German | `it` | Italian |
| `ar` | Arabic | `en` | English | `kab` | Kabyle |
| `ast` | Asturian | `es` | Spanish | `nl` | Dutch |
| `bg` | Bulgarian | `eu` | Basque | `oc` | Occitan |
| `ca` | Catalan | `fr` | French | `pt` | Portuguese |
| `da` | Danish | `fy` | Frisian | `ro` | Romanian |
| | | `gl` | Galician | `sk` | Slovak |
| | | `hr` | Croatian | | |

The authoritative, runtime list is always:

```python
import ovos_lang_parser
ovos_lang_parser.LANGS
```

A `lang` value does not have to be an exact member. It is matched to the closest wordlist,
so regional variants like `en-us` or `pt-pt` resolve to `en` / `pt`. A `lang` too far from
any bundled list raises `ValueError`.

## What each wordlist covers

Each wordlist maps a few hundred **target** languages (keyed by ISO 639 code) to their names
in that language. So the `en` wordlist knows the English names of hundreds of languages, the
`pt` wordlist their Portuguese names, and so on. The target set is far broader than the 21
name languages above. You can resolve "Swahili", "Tibetan", or "Esperanto" even though the
library cannot parse names *written in* those languages.

Approximate distinct target codes per wordlist:

| `lang` | targets | `lang` | targets | `lang` | targets |
|--------|--------:|--------|--------:|--------|--------:|
| `an` | 242 | `es` | 153 | `nl` | 153 |
| `ar` | 134 | `eu` | 140 | `oc` | 156 |
| `ast` | 182 | `fr` | 153 | `pt` | 186 |
| `bg` | 148 | `fy` | 169 | `ro` | 153 |
| `ca` | 153 | `gl` | 153 | `sk` | 148 |
| `da` | 153 | `hr` | 148 | | |
| `de` | 184 | `it` | 153 | | |
| `en` | 153 | `kab` | 134 | | |

## The data model

Wordlists live under `ovos_lang_parser/res/<lang>/langs.json`. Each file is a JSON object
keyed by BCP-47 code:

```json
{
  "de": "German",
  "pt": "Portuguese",
  "pt-br": "Brazilian Portuguese",
  "en-us": "American English"
}
```

A value may also be a **template** using `(a|b)` alternation, which the loader expands into
every spelling. For example `"Bislamá Bichlamar"` and templated forms like
`"(Modern |)Greek"` become multiple accepted names, all mapping to the same code. The
**first** name listed for a code is treated as canonical. It is what `pronounce_lang`
returns.

At load time (`get_lang_data` / the internal loader):

- codes are normalized to modern lowercase form (legacy `iw` → `he`, `jw` → `jv`,
  `mo` → `ro`), so duplicate aliases merge onto one code
- templates are expanded to individual names
- results are memoized so a wordlist is parsed only once.

Both full and base tags coexist: `pt` and `pt-br` are separate keys, which is what lets
`extract_langcode` return `pt-br` for "Brazilian Portuguese" while `pronounce_lang("pt-br",
…)` falls back to the `pt` name when a region-specific one is absent.

To add a language, see [extending.md](extending.md).

---
[← API reference](api.md) · [Home](../README.md) · [Extending →](extending.md)
