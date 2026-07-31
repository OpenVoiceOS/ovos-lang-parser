# Adding a language

Teaching the parser to read language names written in a new language means adding one
wordlist. No code changes are required. `LANGS` is discovered from the filesystem at import
time.

## Steps

1. **Create the directory and file:**

   ```
   ovos_lang_parser/res/<lang>/langs.json
   ```

   where `<lang>` is the BCP-47 code of the language the names are written in (for example
   `sv` for Swedish).

2. **Fill in `{code: name}` pairs.** Key each entry by the BCP-47 code of the *target*
   language; the value is that language's name in `<lang>`:

   ```json
   {
     "en": "engelska",
     "de": "tyska",
     "pt": "portugisiska",
     "pt-br": "brasiliansk portugisiska"
   }
   ```

   - The **first** name for a code is canonical. It is what `pronounce_lang` returns. List
     the most natural spelling first.
   - Provide both base and regional tags where they differ (`pt` and `pt-br`). A regional tag
     with no entry falls back to the base name automatically.

3. **Add spelling variants with templates** when several forms should all resolve to one
   code. Use `(a|b)` alternation in a single string value:

   ```json
   { "el": "(nygrekiska|grekiska)" }
   ```

   Both "nygrekiska" and "grekiska" become accepted names for `el`. Alternations can appear
   anywhere in the string and nest.

That is the whole contribution. Drop the file in, and the new code appears in `LANGS`
automatically.

## Verifying your wordlist

```python
import ovos_lang_parser
from ovos_lang_parser import extract_langcode, pronounce_lang, get_lang_data

assert "<lang>" in ovos_lang_parser.LANGS

# names resolve back to codes
assert extract_langcode("<a name from your file>", "<lang>")[0] == "<expected code>"

# codes resolve back to your canonical names
print(pronounce_lang("de", "<lang>"))

# inspect the whole table
print(len(get_lang_data("<lang>")), "names loaded")
```

## Conventions

- Codes are normalized to modern lowercase form on load, so you may use legacy aliases
  (`iw`, `jw`, `mo`). They merge onto the current code (`he`, `jv`, `ro`). Prefer the modern
  code when authoring.
- Keep the file UTF-8 and valid JSON. The loader reads it directly.
- Names are matched case-insensitively at runtime, so casing in the file is only cosmetic.
  Keep it natural for `pronounce_lang` output.

---
[← Coverage](coverage.md) · [Home](../README.md)
