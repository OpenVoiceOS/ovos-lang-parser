#!/usr/bin/env python3
"""Entity extraction / NER: pull the language mentioned in free text.

Standalone, no OVOS stack required:

    pip install ovos-lang-parser
    python examples/ner_language_mentions.py

`extract_langcode` always returns a best-guess match, so we apply a confidence
threshold to decide whether a language was really mentioned.
"""
import _bootstrap  # noqa: F401  (repo-local path + quiet logging; see _bootstrap.py)

from ovos_lang_parser import extract_langcode, pronounce_lang

THRESHOLD = 0.7

# Free text in English that may or may not name a language.
SAMPLES = [
    "translate this to Brazilian Portuguese",
    "can you say it in Mandarin Chinese",
    "I'd like the subtitles in Greek",
    "I need this dubbed into Korean",
    "put the captions in Japanese",
    "the weather looks nice today",   # no language mentioned
]


def detect_language_mention(text, written_in="en"):
    code, conf = extract_langcode(text, written_in)
    if conf < THRESHOLD:
        return None
    return code, conf


def main():
    for text in SAMPLES:
        hit = detect_language_mention(text, "en")
        if hit is None:
            print(f"[  -- ] {text!r}\n        no language mentioned")
        else:
            code, conf = hit
            english_name = pronounce_lang(code, "en")
            print(f"[{code:>5}] {text!r}\n        -> {english_name} (confidence {conf:.2f})")


if __name__ == "__main__":
    main()
