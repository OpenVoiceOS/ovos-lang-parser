import json
import os.path

from langcodes import closest_match
from ovos_utils.bracket_expansion import expand_template
from ovos_utils.parse import match_one, MatchStrategy

RES_DIR = f"{os.path.dirname(__file__)}/res"
LANGS = os.listdir(RES_DIR)


def get_lang_data(lang):
    closest_lang, distance = closest_match(lang, LANGS)
    if distance > 10:
        raise ValueError(f"Unsupported language '{lang}' not in {LANGS}")
    resource_file = f"{RES_DIR}/{closest_lang}/langs.json"
    LANGUAGES = {}
    with open(resource_file) as f:
        for k, v in json.load(f).items():
            if isinstance(v, str):
                v = expand_template(v)
            # list of spoken names for this language
            # multiple valid spellings may exist
            for l in v:
                LANGUAGES[l] = k
    return LANGUAGES


def extract_langcode(text, lang):
    langs = get_lang_data(lang)
    return match_one(text, langs, strategy=MatchStrategy.TOKEN_SET_RATIO)


def pronounce_lang(lang_code, lang):
    langs = {v: k for k, v in get_lang_data(lang).items()}
    lang_code = lang_code.lower()
    lang2 = lang_code.split("-")[0]
    spoken_lang = langs.get(lang_code) or langs.get(lang2) or lang_code
    if isinstance(spoken_lang, list):
        spoken_lang = spoken_lang[0]
    return spoken_lang
