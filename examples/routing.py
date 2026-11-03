#!/usr/bin/env python3
"""Routing: resolve a user-named target language to a code, then pick an engine.

Standalone, no OVOS stack required:

    pip install ovos-lang-parser
    python examples/routing.py

A multilingual pipeline (translation / TTS / STT) needs a canonical code before
it can choose a backend. `extract_langcode` turns what the user said into that
code; here a mock engine registry stands in for the real backends.
"""
import _bootstrap  # noqa: F401  (repo-local path + quiet logging; see _bootstrap.py)

from ovos_lang_parser import extract_langcode, pronounce_lang

THRESHOLD = 0.7

# Pretend these are the languages your TTS/translation backends support.
ENGINE_REGISTRY = {
    "de": "tts.german.v2",
    "fr": "tts.french.v2",
    "pt": "tts.portuguese.v1",
    "pt-br": "tts.portuguese-br.v1",
    "en": "tts.english.v3",
    "es": "tts.spanish.v2",
    "it": "tts.italian.v1",
}


def route(user_request, spoken_in="en"):
    code, conf = extract_langcode(user_request, spoken_in)
    if conf < THRESHOLD:
        return None, "could not identify a target language"

    # exact engine, else fall back to the base language
    engine = ENGINE_REGISTRY.get(code) or ENGINE_REGISTRY.get(code.split("-")[0])
    if engine is None:
        name = pronounce_lang(code, "en")
        return code, f"{name} ({code}) recognized but no engine available"
    return code, engine


# (request, language the request is written in)
REQUESTS = [
    ("read it back to me in German", "en"),
    ("switch the voice to Brazilian Portuguese", "en"),
    ("I want French please", "en"),
    ("italiano", "it"),                     # user names the target in Italian
    ("say something in Swahili", "en"),     # recognized but unsupported target
    ("play some music", "en"),              # no language at all
]


def main():
    for request, spoken_in in REQUESTS:
        code, result = route(request, spoken_in)
        tag = code if code else "??"
        print(f"{request!r:46} -> [{tag}] {result}")


if __name__ == "__main__":
    main()
