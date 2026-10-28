"""
All settings and lookup tables in one place.

Change a default here to change it everywhere; every setting can also be
overridden for a single run from the command line (see `python3 main.py -h`).
"""
from pathlib import Path

# ---------------------------------------------------------------- paths

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"          # output/<language>/<ID>.wav

# ---------------------------------------------------------------- input

NAME_BY = "ID"                # column used for file names ("none" = name by text)
CSV_DELIMITERS = ",\t;|"      # auto-detected from the header line
MAX_NAME_LEN = 120            # bytes, for file names built from text

# ---------------------------------------------------------------- voice

ENGINE = "gtts"               # gtts | auto | edge | say
# Engines tried in order; the next one covers languages the previous lacks
ENGINE_ORDER = {
    "gtts": ["gtts", "edge"],
    "auto": ["edge", "gtts"],
    "edge": ["edge", "gtts"],
    "say": ["say"],
}
GENDER = "female"             # Edge voices: female | male
ENGLISH_LOCALE = "en-IN"      # Edge accent for English: en-IN, en-US, en-GB, ...
RATE = 0                      # Edge speaking rate in %
PITCH = 0                     # Edge pitch in Hz
SAY_VOICES = {"hi": "Lekha", "te": "Geeta"}   # macOS voices for --engine say

# ---------------------------------------------------------------- audio
# Same processing as examples/text_to_wav_single.py

FORMAT = "wav"
FORMATS = ["wav", "mp3", "m4a"]
TEMPO = 0.9                   # playback speed, pitch kept (1 = off)
TEMPO_RANGE = (0.5, 2.0)      # limits of ffmpeg's atempo filter
LEAD_SILENCE_MS = 400         # silence before speech (0 = off)
SAMPLE_RATE = None            # None keeps the engine's rate (24 kHz)
NATIVE_FORMAT = {"edge": "mp3", "gtts": "mp3", "say": "aiff"}

# ---------------------------------------------------------------- run

CONCURRENCY = 4               # parallel TTS requests
RETRIES = 3                   # attempts per clip, with 1s/2s/4s back-off

# pip package for each importable module, installed on first use
PACKAGES = {"gtts": "gTTS", "edge_tts": "edge-tts", "openpyxl": "openpyxl"}

# ---------------------------------------------------------------- languages

# code: (folder/column name, Unicode scripts, gTTS code, Edge locale); None = engine lacks it
LANGUAGES = {
    "af": ("afrikaans", "LATIN", "af", "af-ZA"),
    "am": ("amharic", "ETHIOPIC", "am", "am-ET"),
    "ar": ("arabic", "ARABIC", "ar", "ar-SA"),
    "as": ("assamese", "BENGALI", None, None),
    "az": ("azerbaijani", "LATIN", None, "az-AZ"),
    "bg": ("bulgarian", "CYRILLIC", "bg", "bg-BG"),
    "bn": ("bengali", "BENGALI", "bn", "bn-IN"),
    "bs": ("bosnian", "LATIN", "bs", "bs-BA"),
    "ca": ("catalan", "LATIN", "ca", "ca-ES"),
    "cs": ("czech", "LATIN", "cs", "cs-CZ"),
    "cy": ("welsh", "LATIN", "cy", "cy-GB"),
    "da": ("danish", "LATIN", "da", "da-DK"),
    "de": ("german", "LATIN", "de", "de-DE"),
    "el": ("greek", "GREEK", "el", "el-GR"),
    "en": ("english", "LATIN", "en", "en-IN"),
    "es": ("spanish", "LATIN", "es", "es-ES"),
    "et": ("estonian", "LATIN", "et", "et-EE"),
    "eu": ("basque", "LATIN", "eu", None),
    "fa": ("persian", "ARABIC", None, "fa-IR"),
    "fi": ("finnish", "LATIN", "fi", "fi-FI"),
    "fil": ("filipino", "LATIN", "tl", "fil-PH"),
    "fr": ("french", "LATIN", "fr", "fr-FR"),
    "ga": ("irish", "LATIN", None, "ga-IE"),
    "gl": ("galician", "LATIN", "gl", "gl-ES"),
    "gu": ("gujarati", "GUJARATI", "gu", "gu-IN"),
    "ha": ("hausa", "LATIN", "ha", None),
    "he": ("hebrew", "HEBREW", "iw", "he-IL"),
    "hi": ("hindi", "DEVANAGARI", "hi", "hi-IN"),
    "hr": ("croatian", "LATIN", "hr", "hr-HR"),
    "hu": ("hungarian", "LATIN", "hu", "hu-HU"),
    "id": ("indonesian", "LATIN", "id", "id-ID"),
    "is": ("icelandic", "LATIN", "is", "is-IS"),
    "it": ("italian", "LATIN", "it", "it-IT"),
    "iu": ("inuktitut", "CANADIAN LATIN", None, None),  # Edge lists iu voices but rejects them
    "ja": ("japanese", "JAPANESE CJK", "ja", "ja-JP"),
    "jv": ("javanese", "LATIN", "jw", "jv-ID"),
    "ka": ("georgian", "GEORGIAN", None, "ka-GE"),
    "kk": ("kazakh", "CYRILLIC", None, "kk-KZ"),
    "km": ("khmer", "KHMER", "km", "km-KH"),
    "kn": ("kannada", "KANNADA", "kn", "kn-IN"),
    "ko": ("korean", "HANGUL", "ko", "ko-KR"),
    "la": ("latin", "LATIN", "la", None),
    "lo": ("lao", "LAO", None, "lo-LA"),
    "lt": ("lithuanian", "LATIN", "lt", "lt-LT"),
    "lv": ("latvian", "LATIN", "lv", "lv-LV"),
    "mk": ("macedonian", "CYRILLIC", None, "mk-MK"),
    "ml": ("malayalam", "MALAYALAM", "ml", "ml-IN"),
    "mn": ("mongolian", "CYRILLIC", None, "mn-MN"),
    "mr": ("marathi", "DEVANAGARI", "mr", "mr-IN"),
    "ms": ("malay", "LATIN", "ms", "ms-MY"),
    "mt": ("maltese", "LATIN", None, "mt-MT"),
    "my": ("burmese", "MYANMAR", "my", "my-MM"),
    "nb": ("norwegian", "LATIN", "no", "nb-NO"),
    "ne": ("nepali", "DEVANAGARI", "ne", "ne-NP"),
    "nl": ("dutch", "LATIN", "nl", "nl-NL"),
    "or": ("odia", "ORIYA", None, None),
    "pa": ("punjabi", "GURMUKHI", "pa", None),
    "pl": ("polish", "LATIN", "pl", "pl-PL"),
    "ps": ("pashto", "ARABIC", None, "ps-AF"),
    "pt": ("portuguese", "LATIN", "pt", "pt-BR"),
    "ro": ("romanian", "LATIN", "ro", "ro-RO"),
    "ru": ("russian", "CYRILLIC", "ru", "ru-RU"),
    "sa": ("sanskrit", "DEVANAGARI", None, None),
    "si": ("sinhala", "SINHALA", "si", "si-LK"),
    "sk": ("slovak", "LATIN", "sk", "sk-SK"),
    "sl": ("slovenian", "LATIN", None, "sl-SI"),
    "so": ("somali", "LATIN", None, "so-SO"),
    "sq": ("albanian", "LATIN", "sq", "sq-AL"),
    "sr": ("serbian", "CYRILLIC LATIN", "sr", "sr-RS"),
    "su": ("sundanese", "LATIN", "su", "su-ID"),
    "sv": ("swedish", "LATIN", "sv", "sv-SE"),
    "sw": ("swahili", "LATIN", "sw", "sw-KE"),
    "ta": ("tamil", "TAMIL", "ta", "ta-IN"),
    "te": ("telugu", "TELUGU", "te", "te-IN"),
    "th": ("thai", "THAI", "th", "th-TH"),
    "tr": ("turkish", "LATIN", "tr", "tr-TR"),
    "uk": ("ukrainian", "CYRILLIC", "uk", "uk-UA"),
    "ur": ("urdu", "ARABIC", "ur", "ur-IN"),
    "uz": ("uzbek", "LATIN", None, "uz-UZ"),
    "vi": ("vietnamese", "LATIN", "vi", "vi-VN"),
    "yue": ("cantonese", "CJK", "yue", "zh-HK"),
    "zh": ("chinese", "CJK", "zh-CN", "zh-CN"),
    "zu": ("zulu", "LATIN", None, "zu-ZA"),
}

# Other names a column header may use for a language
LANGUAGE_ALIASES = {
    "bangla": "bn", "oriya": "or", "farsi": "fa", "tagalog": "fil", "mandarin": "zh",
    "myanmar": "my", "bokmal": "nb", "azeri": "az", "slovene": "sl", "panjabi": "pa",
}

# Language assumed when a column header gives no hint
SCRIPT_DEFAULT = {
    "LATIN": "en", "DEVANAGARI": "hi", "BENGALI": "bn", "GURMUKHI": "pa",
    "GUJARATI": "gu", "ORIYA": "or", "TAMIL": "ta", "TELUGU": "te", "KANNADA": "kn",
    "MALAYALAM": "ml", "SINHALA": "si", "ARABIC": "ur", "CYRILLIC": "ru", "GREEK": "el",
    "HEBREW": "he", "THAI": "th", "LAO": "lo", "KHMER": "km", "MYANMAR": "my",
    "GEORGIAN": "ka", "ETHIOPIC": "am", "HANGUL": "ko", "JAPANESE": "ja", "CJK": "zh",
    "CANADIAN": "iu",
}
