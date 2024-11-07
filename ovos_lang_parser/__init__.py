import json
import os.path

from ovos_utils.parse import match_one, fuzzy_match, MatchStrategy
from ovos_utils.lang import standardize_lang_tag


def extract_langcode(text, lang):
    resource_file = f"{os.path.dirname(__file__)}/langs.json"
    LANGUAGES = {}
    with open(resource_file) as f:
        for k, v in json.load(f).items():
            if isinstance(v, str):
                v = [v]
            # list of spoken names for this language
            # multiple valid spellings may exist
            for l in v:
                LANGUAGES[l] = k
    return match_one(text, LANGUAGES, strategy=MatchStrategy.TOKEN_SET_RATIO)


def pronounce_lang(lang_code, lang):
    resource_file = f"{os.path.dirname(__file__)}/langs.json"
    with open(resource_file) as f:
        LANGUAGES = json.load(f)
    lang_code = lang_code.lower()
    lang2 = lang_code.split("-")[0]
    spoken_lang = LANGUAGES.get(lang_code) or LANGUAGES.get(lang2) or lang_code
    if isinstance(spoken_lang, list):
        spoken_lang = spoken_lang[0]
    return spoken_lang
