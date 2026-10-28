"""Work out the language of a column / text, and map it to each engine's code."""
import re
import unicodedata
from collections import Counter

from .config import LANGUAGE_ALIASES, LANGUAGES, SCRIPT_DEFAULT

NAME_TO_CODE = {lang[0]: code for code, lang in LANGUAGES.items()}
NAME_TO_CODE.update(LANGUAGE_ALIASES)


def dominant_script(text):
    scripts = Counter(unicodedata.name(ch, "").split(" ")[0] for ch in text if ch.isalpha())
    if scripts["HIRAGANA"] or scripts["KATAKANA"]:
        return "JAPANESE"  # kana marks Japanese even when kanji (CJK) dominate
    return scripts.most_common(1)[0][0] if scripts else None


def column_hint(header):
    """'hindi_sentence' -> 'hi'"""
    for token in re.split(r"[^a-z]+", header.lower()):
        if token in NAME_TO_CODE:
            return NAME_TO_CODE[token]
    return None


def detect_language(text, hint):
    script = dominant_script(text)
    if not script:
        return None
    if hint and hint in LANGUAGES and script in LANGUAGES[hint][1].split():
        return hint
    return SCRIPT_DEFAULT.get(script)


def folder_for(lang):
    return LANGUAGES.get(lang, (lang,))[0]


def gtts_code(lang):
    return LANGUAGES[lang][2] if lang in LANGUAGES else lang


def edge_locale(lang):
    return LANGUAGES[lang][3] if lang in LANGUAGES else lang


def print_languages():
    print(f"{'code':5} {'language':12} {'gTTS':5} Edge")
    for code, (name, _, gtts, edge) in LANGUAGES.items():
        print(f"{code:5} {name:12} {'yes' if gtts else '-':5} {'yes' if edge else '-'}")
