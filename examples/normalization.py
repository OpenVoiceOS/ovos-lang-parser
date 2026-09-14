#!/usr/bin/env python3
"""Normalization: canonicalize messy language names to one standard code.

Standalone, no OVOS stack required:

    pip install ovos-lang-parser
    python examples/normalization.py

Aliases, autonyms, and localized spellings all collapse onto a single BCP-47
code, so labels can be deduplicated and standardized regardless of how they were
written. `pronounce_lang` then gives a single canonical display name.
"""
import _bootstrap  # noqa: F401  (repo-local path + quiet logging; see _bootstrap.py)

from collections import defaultdict

from ovos_lang_parser import extract_langcode, pronounce_lang

# Messy labels as (name, language the name is written in) from mixed sources.
# Every "German" spelling below should collapse onto the single code "de".
RAW_LABELS = [
    ("Deutsch", "de"),      # German autonym
    ("alemão", "pt"),       # German, in Portuguese
    ("German", "en"),       # German, in English
    ("allemand", "fr"),     # German, in French
    ("tedesco", "it"),      # German, in Italian
    ("English", "en"),
    ("inglés", "es"),       # English, in Spanish
    ("Français", "fr"),     # French autonym
    ("francês", "pt"),      # French, in Portuguese
]


def canonicalize(name, written_in):
    code, conf = extract_langcode(name, written_in)
    return code if conf >= 0.9 else None  # normalization wants near-exact matches


def main():
    buckets = defaultdict(list)
    for name, written_in in RAW_LABELS:
        code = canonicalize(name, written_in)
        buckets[code].append(name)

    print("Canonicalized groups (all spellings -> one code -> one display name):\n")
    for code in sorted(k for k in buckets if k is not None):
        display = pronounce_lang(code, "en")
        joined = ", ".join(buckets[code])
        print(f"  {code:>3}  {display:<8}  <-  {joined}")
    if None in buckets:
        print(f"\n  [unresolved] {buckets[None]}")


if __name__ == "__main__":
    main()
