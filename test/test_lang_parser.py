import unittest

from ovos_lang_parser import (LANGS, extract_langcode, get_lang_data,
                              pronounce_lang)

# hand-verified (utterance language, spoken name, expected code) triples
EXTRACTION_SAMPLES = [
    ("an", "Portugués", "pt"),
    ("an", "Anglés", "en"),
    ("an", "Alemán", "de"),
    ("ast", "Portugués", "pt"),
    ("ast", "Inglés", "en"),
    ("ast", "Castellanu", "es"),
    ("ar", "العربية", "ar"),
    ("ar", "الإنجليزية", "en"),
    ("ar", "البرتغالية", "pt"),
    ("ar", "الألمانية", "de"),
    ("ar", "الفرنسية", "fr"),
    ("ar", "الصينية", "zh"),
    ("ca", "Portuguès", "pt"),
    ("ca", "Anglès", "en"),
    ("ca", "Croat", "hr"),
    ("ca", "Bosnià", "bs"),
    ("da", "portugisisk", "pt"),
    ("da", "engelsk", "en"),
    ("da", "tysk", "de"),
    ("de", "Portugiesisch", "pt"),
    ("de", "Englisch", "en"),
    ("de", "Deutsch", "de"),
    ("de", "Niederländisch", "nl"),
    ("en", "Portuguese", "pt"),
    ("en", "English", "en"),
    ("en", "German", "de"),
    ("en", "Hebrew", "he"),
    ("es", "Portugués", "pt"),
    ("es", "Inglés", "en"),
    ("es", "Alemán", "de"),
    ("eu", "Portuguesa", "pt"),
    ("eu", "Ingelesa", "en"),
    ("eu", "Galiziera", "gl"),
    ("fr", "Portugais", "pt"),
    ("fr", "Anglais", "en"),
    ("fr", "Allemand", "de"),
    ("fy", "Frânsk", "fr"),
    ("fy", "Ingelsk", "en"),
    ("fy", "Dútsk", "de"),
    ("gl", "Portugués", "pt"),
    ("gl", "Inglés", "en"),
    ("it", "Portoghese", "pt"),
    ("it", "Inglese", "en"),
    ("it", "Tedesco", "de"),
    ("nl", "Portugees", "pt"),
    ("oc", "Portugués", "pt"),
    ("oc", "Anglés", "en"),
    ("oc", "Alemand", "de"),
    ("oc", "Occitan", "oc"),
    ("oc", "Catalan", "ca"),
    ("nl", "Engels", "en"),
    ("nl", "Duits", "de"),
    ("pt", "Português", "pt"),
    ("pt", "Inglês", "en"),
    ("pt", "Alemão", "de"),
    ("pt", "Francês", "fr"),
    ("pt", "Holandês", "nl"),
    ("pt", "Tcheco", "cs"),
]

# hand-verified (utterance language, code, expected spoken name) triples
PRONUNCIATION_SAMPLES = [
    ("an", "pt", "Portugués"),
    ("ar", "pt", "البرتغالية"),
    ("ar", "en", "الإنجليزية"),
    ("ar", "ja", "اليابانية"),
    ("ast", "pt", "Portugués"),
    ("ca", "pt", "Portuguès"),
    ("da", "pt", "portugisisk"),
    ("de", "pt", "Portugiesisch"),
    ("en", "pt", "Portuguese"),
    ("en", "nn", "Norwegian Nynorsk"),
    ("es", "pt", "Portugués"),
    ("eu", "pt", "Portuguesa"),
    ("fr", "pt", "Portugais"),
    ("fy", "pt", "Portegeesk"),
    ("gl", "pt", "Portugués"),
    ("it", "pt", "Portoghese"),
    ("nl", "pt", "Portugees"),
    ("oc", "pt", "Portugués"),
    ("oc", "en", "Anglés"),
    ("oc", "es", "Espanhòl"),
    ("pt", "pt", "Português"),
    ("pt", "de", "Alemão"),
    ("pt", "zh", "Chinês"),
]


class TestLangs(unittest.TestCase):
    def test_supported_languages(self):
        self.assertEqual(LANGS, sorted(LANGS))
        for lang in ["an", "ast", "ca", "da", "de", "en", "es", "eu",
                     "fr", "fy", "gl", "it", "nl", "oc", "pt"]:
            self.assertIn(lang, LANGS)


class TestGetLangData(unittest.TestCase):
    def test_every_language_loads(self):
        for lang in LANGS:
            data = get_lang_data(lang)
            self.assertIsInstance(data, dict)
            self.assertGreater(len(data), 100, lang)
            for name, code in data.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(code, str)
                self.assertEqual(code, code.lower())

    def test_dialects_resolve_to_closest_language(self):
        self.assertEqual(get_lang_data("pt-br"), get_lang_data("pt"))
        self.assertEqual(get_lang_data("en-US"), get_lang_data("en"))

    def test_unsupported_language_raises(self):
        for lang in ["zz", "ja", "ru", "klingon"]:
            with self.assertRaises(ValueError):
                get_lang_data(lang)

    def test_legacy_codes_normalized(self):
        for lang in LANGS:
            codes = set(get_lang_data(lang).values())
            for legacy in ["iw", "jw", "mo"]:
                self.assertNotIn(legacy, codes, lang)


class TestExtractLangcode(unittest.TestCase):
    def test_exact_names(self):
        for lang, name, expected in EXTRACTION_SAMPLES:
            code, conf = extract_langcode(name, lang)
            self.assertEqual(code, expected, f"{lang}: {name}")
            self.assertEqual(conf, 1.0)

    def test_case_insensitive(self):
        self.assertEqual(extract_langcode("portuguese", "en")[0], "pt")
        self.assertEqual(extract_langcode("FRENCH", "en")[0], "fr")

    def test_name_embedded_in_utterance(self):
        code, conf = extract_langcode("I speak French fluently", "en")
        self.assertEqual(code, "fr")
        self.assertGreater(conf, 0.3)
        code, conf = extract_langcode("não falo espanhol", "pt")
        self.assertEqual(code, "es")
        code, conf = extract_langcode("eu falo alemão", "pt")
        self.assertEqual(code, "de")

    def test_regional_variants(self):
        self.assertEqual(extract_langcode("American English", "en")[0], "en-us")
        self.assertEqual(extract_langcode("Brazilian Portuguese", "en")[0],
                         "pt-br")

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError):
            extract_langcode("English", "zz")


class TestPronounceLang(unittest.TestCase):
    def test_samples(self):
        for lang, code, expected in PRONUNCIATION_SAMPLES:
            self.assertEqual(pronounce_lang(code, lang), expected)

    def test_code_case_insensitive(self):
        self.assertEqual(pronounce_lang("PT", "en"), "Portuguese")
        self.assertEqual(pronounce_lang("En-Us", "en"), "American English")

    def test_dialect_falls_back_to_primary_subtag(self):
        self.assertEqual(pronounce_lang("de-at", "en"), "German")
        self.assertEqual(pronounce_lang("fr-CA", "en"), "French")

    def test_legacy_code_aliases(self):
        self.assertEqual(pronounce_lang("iw", "en"), "Hebrew")
        self.assertEqual(pronounce_lang("jw", "en"), "Javanese")
        self.assertEqual(pronounce_lang("iw", "pt"), "Hebraico")

    def test_unknown_code_returned_unchanged(self):
        self.assertEqual(pronounce_lang("xx", "en"), "xx")

    def test_malformed_code_returned_unchanged(self):
        self.assertEqual(pronounce_lang("not a tag", "en"), "not a tag")

    def test_unsupported_language_raises(self):
        with self.assertRaises(ValueError):
            pronounce_lang("en", "zz")


class TestRoundTrip(unittest.TestCase):
    def test_pronounce_then_extract_all_languages(self):
        for lang in LANGS:
            codes = sorted(set(get_lang_data(lang).values()))
            self.assertGreater(len(codes), 100, lang)
            for code in codes:
                spoken = pronounce_lang(code, lang)
                self.assertNotEqual(spoken, code,
                                    f"{lang}: no spoken name for {code}")
                extracted, conf = extract_langcode(spoken, lang)
                self.assertEqual(extracted, code, f"{lang}: {spoken}")
                self.assertEqual(conf, 1.0, f"{lang}: {spoken}")


if __name__ == "__main__":
    unittest.main()
