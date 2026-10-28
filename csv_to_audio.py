#!/usr/bin/env python3
"""
Convert text from a CSV/XLSX sheet into speech, one audio file per text:
    output/<language>/<ID>.wav      e.g. output/english/A01.wav

- Language comes from the column header (hindi, marathi_sentence, tamil_word, ...)
  and from each text's Unicode script, so new language columns work automatically.
  Devanagari is shared by Hindi/Marathi/Nepali: name the column or use --lang-map.
- Audio matches 'text to wav single.py': Google TTS (gTTS), 400 ms leading
  silence, atempo=0.9, 16-bit wav. --engine auto uses Microsoft Edge neural
  voices instead (more human-like, gTTS for languages Edge lacks).
- Missing Python packages (edge-tts, gTTS, openpyxl) are pip-installed on first
  use; ffmpeg is installed with Homebrew if needed for wav/m4a output.

Examples:
  python3 csv_to_audio.py sample.csv                        # every language column (skips ID)
  python3 csv_to_audio.py sample.csv -c Hindi Marathi       # only these columns
  python3 csv_to_audio.py sample.csv --tempo 0.85           # slower
  python3 csv_to_audio.py sample.csv --engine auto --gender male   # Edge neural voices
  python3 csv_to_audio.py sheet.xlsx --sheet Words
  python3 csv_to_audio.py sheet.xlsx -o /path/to/audio      # different output folder
  python3 csv_to_audio.py sheet.xlsx --name-by none         # name files by their text instead of ID
  python3 csv_to_audio.py sample.csv -l text=mr             # force a column's language
  python3 csv_to_audio.py sample.csv -e auto -v hi=hi-IN-MadhurNeural
  python3 csv_to_audio.py sample.csv --list-voices hi
"""
import argparse
import asyncio
import csv
import importlib
import os
import re
import shutil
import subprocess
import sys
import unicodedata
from collections import Counter

MAX_NAME_LEN = 120
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# code: (folder/column name, Unicode script)
LANGUAGES = {
    "en": ("english", "LATIN"),
    "hi": ("hindi", "DEVANAGARI"),
    "mr": ("marathi", "DEVANAGARI"),
    "ne": ("nepali", "DEVANAGARI"),
    "sa": ("sanskrit", "DEVANAGARI"),
    "te": ("telugu", "TELUGU"),
    "ta": ("tamil", "TAMIL"),
    "kn": ("kannada", "KANNADA"),
    "ml": ("malayalam", "MALAYALAM"),
    "gu": ("gujarati", "GUJARATI"),
    "bn": ("bengali", "BENGALI"),
    "as": ("assamese", "BENGALI"),
    "pa": ("punjabi", "GURMUKHI"),
    "or": ("odia", "ORIYA"),
    "ur": ("urdu", "ARABIC"),
}
NAME_TO_CODE = {name: code for code, (name, _) in LANGUAGES.items()}
NAME_TO_CODE.update({"bangla": "bn", "oriya": "or"})

# Language assumed when a column header gives no hint
SCRIPT_DEFAULT = {
    "LATIN": "en", "DEVANAGARI": "hi", "TELUGU": "te", "TAMIL": "ta",
    "KANNADA": "kn", "MALAYALAM": "ml", "GUJARATI": "gu", "BENGALI": "bn",
    "GURMUKHI": "pa", "ORIYA": "or", "ARABIC": "ur",
}

# Voices used by --engine say (macOS) when no --voice is given
SAY_VOICES = {"hi": "Lekha", "te": "Geeta"}

NATIVE_FORMAT = {"edge": "mp3", "gtts": "mp3", "say": "aiff"}


# ---------------------------------------------------------------- setup

def ensure_package(module, pip_name=None):
    """Import a module, pip-installing it into the current interpreter if missing."""
    try:
        return importlib.import_module(module)
    except ImportError:
        pass
    pip_name = pip_name or module
    print(f"Installing {pip_name} ...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", pip_name], check=True)
    except subprocess.CalledProcessError:
        sys.exit(
            f"Could not install {pip_name}. Use a virtualenv and retry:\n"
            "  python3 -m venv .venv && source .venv/bin/activate"
        )
    importlib.invalidate_caches()
    return importlib.import_module(module)


def ensure_ffmpeg():
    if shutil.which("ffmpeg"):
        return
    if shutil.which("brew"):
        print("Installing ffmpeg with Homebrew ...")
        subprocess.run(["brew", "install", "ffmpeg"], check=True)
        if shutil.which("ffmpeg"):
            return
    sys.exit("ffmpeg is required for this format. Install it (brew/apt install ffmpeg) or use --format mp3.")


# ---------------------------------------------------------------- input

def read_sheet(path, sheet, delimiter):
    if path.lower().endswith((".xlsx", ".xlsm")):
        openpyxl = ensure_package("openpyxl")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        return [["" if v is None else str(v) for v in row] for row in ws.iter_rows(values_only=True)]
    with open(path, newline="", encoding="utf-8-sig") as f:
        if not delimiter:
            first_line = f.readline()
            delimiter = max(",\t;|", key=first_line.count)
            f.seek(0)
        return list(csv.reader(f, delimiter=delimiter))


def resolve_columns(header, wanted):
    """Default: columns named after a language (skips ID, ...), else all."""
    if not wanted:
        named = [i for i, h in enumerate(header) if column_hint(h)]
        return named or list(range(len(header)))
    lower = [h.lower() for h in header]
    indices = []
    for col in wanted:
        if col.lower() in lower:
            indices.append(lower.index(col.lower()))
        elif col.isdigit() and int(col) < len(header):
            indices.append(int(col))
        else:
            sys.exit(f"Column '{col}' not found. Available: {header}")
    return indices


def find_column(header, name):
    lower = [h.lower() for h in header]
    return lower.index(name.lower()) if name and name.lower() in lower else None


def safe_filename(text):
    """Turn the spoken text into a filesystem-safe name (keeps unicode letters)."""
    name = unicodedata.normalize("NFC", text).strip()
    name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", name)
    name = re.sub(r"\s+", " ", name).strip(" .")
    if len(name.encode("utf-8")) > MAX_NAME_LEN:
        name = name.encode("utf-8")[:MAX_NAME_LEN].decode("utf-8", "ignore").rstrip()
    return name or "untitled"


# ---------------------------------------------------------------- language

def dominant_script(text):
    scripts = Counter(unicodedata.name(ch, "").split(" ")[0] for ch in text if ch.isalpha())
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
    if hint and hint in LANGUAGES and LANGUAGES[hint][1] == script:
        return hint
    return SCRIPT_DEFAULT.get(script)


def folder_for(lang):
    return LANGUAGES.get(lang, (lang,))[0]


# ---------------------------------------------------------------- engines

async def pick_edge_voices(edge_tts, langs, gender, english_locale, overrides):
    voices = await edge_tts.list_voices()
    chosen = {}
    for lang in langs:
        if lang in overrides:
            chosen[lang] = overrides[lang]
            continue
        preferred = english_locale if lang == "en" else f"{lang}-IN"
        candidates = [v for v in voices if v["Locale"].split("-")[0] == lang]
        candidates.sort(key=lambda v: (
            v["Locale"] != preferred,
            v["Gender"].lower() != gender,
            "Multilingual" in v["ShortName"],
        ))
        if candidates:
            chosen[lang] = candidates[0]["ShortName"]
    return chosen


def audio_filters(args):
    """Leading silence, then tempo change (same as 'text to wav single.py')."""
    filters = []
    if args.lead_silence:
        filters.append(f"adelay={args.lead_silence}:all=1")
    if args.tempo != 1:
        filters.append(f"atempo={args.tempo}")
    return filters


def convert(src, dst, args):
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-ac", "1"]
    filters = audio_filters(args)
    if filters:
        cmd += ["-af", ",".join(filters)]
    if args.sample_rate:
        cmd += ["-ar", str(args.sample_rate)]
    subprocess.run(cmd + [dst], check=True)


async def synthesize(mods, engine, voice, text, out_path, args):
    native = NATIVE_FORMAT[engine]
    tmp = f"{out_path}.part.{native}"
    try:
        if engine == "edge":
            communicate = mods["edge"].Communicate(
                text, voice, rate=f"{args.rate:+d}%", pitch=f"{args.pitch:+d}Hz"
            )
            await communicate.save(tmp)
        elif engine == "gtts":
            await asyncio.to_thread(mods["gtts"].gTTS(text=text, lang=voice).save, tmp)
        else:
            cmd = ["say"] + (["-v", voice] if voice else []) + ["-o", tmp, text]
            await asyncio.to_thread(subprocess.run, cmd, check=True)

        if native == args.format and not args.sample_rate and not audio_filters(args):
            os.replace(tmp, out_path)
        else:
            await asyncio.to_thread(convert, tmp, out_path, args)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


# ---------------------------------------------------------------- main

def parse_pairs(items, what):
    pairs = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep:
            sys.exit(f"Bad {what} '{item}', expected KEY=VALUE")
        pairs[key.strip()] = value.strip()
    return pairs


async def run(args):
    mods = {}

    if args.list_voices:
        mods["edge"] = ensure_package("edge_tts", "edge-tts")
        for v in await mods["edge"].list_voices():
            if v["Locale"].split("-")[0] == args.list_voices:
                print(f'{v["ShortName"]:40} {v["Gender"]}')
        return

    if not args.sheet_path:
        sys.exit("Pass a CSV/XLSX file (or --list-voices LANG)")
    rows = read_sheet(args.sheet_path, args.sheet, args.delimiter)
    if not rows:
        sys.exit("Sheet is empty")
    if args.no_header:
        header = [str(i) for i in range(max(len(r) for r in rows))]
    else:
        header = [h.strip() for h in rows.pop(0)]

    lang_map = {k.lower(): v for k, v in parse_pairs(args.lang_map, "--lang-map").items()}
    voice_map = parse_pairs(args.voice, "--voice")

    name_idx = find_column(header, args.name_by)
    if args.name_by.lower() != "none" and name_idx is None:
        print(f"[warn] no '{args.name_by}' column, naming files by their text")

    # (lang, filename) -> text
    jobs = {}
    unknown = Counter()
    for idx in resolve_columns(header, args.columns):
        col = header[idx]
        forced, hint = lang_map.get(col.lower()), column_hint(col)
        for row in rows:
            text = row[idx].strip() if idx < len(row) else ""
            if not text:
                continue
            name = text
            if name_idx is not None and name_idx < len(row) and row[name_idx].strip():
                name = row[name_idx]
            lang = forced or detect_language(text, hint)
            if lang:
                key = (lang, safe_filename(name))
                if key in jobs and jobs[key] != text:
                    # two columns of one language on the same row, e.g. hindi + hindi_sentence
                    key = (lang, safe_filename(f"{name}_{col}"))
                jobs.setdefault(key, text)
            elif dominant_script(text):
                unknown[col] += 1
    for col, n in unknown.items():
        print(f"[warn] column '{col}': {n} text(s) in an unknown script, use --lang-map {col}=<code>")
    if not jobs:
        sys.exit("No text found to convert")

    # Choose engine + voice per language
    langs = sorted({lang for lang, _ in jobs})
    plan = {}
    if args.engine == "say":
        for lang in langs:
            plan[lang] = ("say", voice_map.get(lang) or SAY_VOICES.get(lang))
    if args.engine in ("auto", "edge"):
        mods["edge"] = ensure_package("edge_tts", "edge-tts")
        try:
            voices = await pick_edge_voices(mods["edge"], langs, args.gender, args.english_locale, voice_map)
        except Exception as e:
            if args.engine == "edge":
                sys.exit(f"Could not reach Edge TTS: {e}")
            print(f"[warn] Edge TTS unavailable ({e}), falling back to gTTS")
            voices = {}
        for lang, voice in voices.items():
            plan[lang] = ("edge", voice)
    missing = [lang for lang in langs if lang not in plan]
    if missing and args.engine in ("auto", "gtts"):
        mods["gtts"] = ensure_package("gtts", "gTTS")
        supported = importlib.import_module("gtts.lang").tts_langs()
        for lang in missing:
            if lang in supported:
                plan[lang] = ("gtts", lang)

    for lang in langs:
        engine, voice = plan.get(lang, ("-", "no voice available, skipped"))
        print(f"{folder_for(lang):10} -> {engine} {voice or 'default'}")

    if not 0.5 <= args.tempo <= 2.0:
        sys.exit("--tempo must be between 0.5 and 2.0")
    if (any(NATIVE_FORMAT[e] != args.format for e, _ in plan.values())
            or args.sample_rate or audio_filters(args)):
        ensure_ffmpeg()

    todo = []
    skipped = 0
    for (lang, name), text in jobs.items():
        if lang not in plan:
            continue
        out_dir = os.path.join(args.out, folder_for(lang))
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{name}.{args.format}")
        if os.path.exists(out_path) and not args.overwrite:
            skipped += 1
            continue
        todo.append((lang, text, out_path))

    sem = asyncio.Semaphore(args.concurrency)

    async def one(lang, text, out_path):
        engine, voice = plan[lang]
        async with sem:
            for attempt in range(3):
                try:
                    await synthesize(mods, engine, voice, text, out_path, args)
                    print(f"[ok]   {out_path}")
                    return True
                except Exception as e:
                    error = e
                    await asyncio.sleep(2 ** attempt)
            print(f"[fail] {text!r}: {error}", file=sys.stderr)
            return False

    results = await asyncio.gather(*(one(*job) for job in todo))
    created = sum(results)
    print(f"\nDone. created={created} skipped={skipped} failed={len(results) - created} -> {args.out}/")


def main():
    p = argparse.ArgumentParser(description="Sheet columns -> human-like text-to-speech audio files")
    p.add_argument("sheet_path", metavar="sheet", nargs="?", help="CSV or XLSX file")
    p.add_argument("--columns", "-c", nargs="+", help="Column names or 0-based indexes (default: all)")
    p.add_argument("--sheet", help="Worksheet name for XLSX (default: first)")
    p.add_argument("--name-by", default="ID",
                   help="Column for file names (default: ID -> A01.wav; falls back to the text if missing)")
    p.add_argument("--out", "-o", default=os.path.join(SCRIPT_DIR, "output"),
                   help="Output folder (default: text2audio/output)")
    p.add_argument("--format", "-f", default="wav", choices=["wav", "mp3", "m4a"])
    p.add_argument("--sample-rate", type=int, help="Resample output, e.g. 16000")
    p.add_argument("--engine", "-e", default="gtts", choices=["gtts", "auto", "edge", "say"],
                   help="gtts = Google TTS, same as 'text to wav single.py' (default); "
                        "auto = Edge neural voices, gTTS for languages Edge lacks")
    p.add_argument("--gender", default="female", choices=["female", "male"])
    p.add_argument("--rate", type=int, default=0, help="Edge voice speaking rate in %% (default: 0; slowing is done by --tempo)")
    p.add_argument("--tempo", type=float, default=0.9,
                   help="Playback tempo, pitch preserved (default: 0.9 = 10%% slower; 1 = off)")
    p.add_argument("--lead-silence", type=int, default=400,
                   help="Silence added before speech, in ms (default: 400; 0 = off)")
    p.add_argument("--pitch", type=int, default=0, help="Pitch change in Hz, e.g. -5")
    p.add_argument("--english-locale", default="en-IN", help="Accent for English (en-IN, en-US, en-GB)")
    p.add_argument("--lang-map", "-l", nargs="+", metavar="COLUMN=CODE",
                   help="Force a column's language, e.g. text=mr")
    p.add_argument("--voice", "-v", nargs="+", metavar="LANG=VOICE",
                   help="Override voice per language, e.g. hi=hi-IN-MadhurNeural")
    p.add_argument("--list-voices", metavar="LANG", help="List Edge voices for a language code and exit")
    p.add_argument("--no-header", action="store_true", help="Sheet has no header row")
    p.add_argument("--delimiter", help="CSV delimiter (default: auto-detect , tab ; |)")
    p.add_argument("--concurrency", type=int, default=4, help="Parallel requests (default: 4)")
    p.add_argument("--overwrite", action="store_true", help="Re-generate existing files")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
