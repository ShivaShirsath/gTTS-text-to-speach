"""Command-line options. Defaults come from config.py."""
import argparse
import asyncio

from . import config
from .pipeline import run

EXAMPLES = """
examples:
  python3 main.py examples/sample.csv                 every language column (skips ID)
  python3 main.py sheet.xlsx -c Hindi Marathi          only these columns
  python3 main.py sheet.xlsx -o /path/to/audio         different output folder
  python3 main.py sheet.xlsx --tempo 0.85              slower
  python3 main.py sheet.xlsx --engine auto --gender male    Edge neural voices
  python3 main.py sheet.xlsx --name-by none            name files by their text instead of ID
  python3 main.py sheet.xlsx -l Text=mr                force a column's language
  python3 main.py --list-languages
  python3 main.py --list-voices hi
"""


def build_parser():
    p = argparse.ArgumentParser(
        prog="main.py",
        description="Turn spreadsheet columns into speech: output/<language>/<ID>.wav",
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("sheet_path", metavar="sheet", nargs="?", help="CSV or XLSX file")

    src = p.add_argument_group("input")
    src.add_argument("--columns", "-c", nargs="+", help="Column names or 0-based indexes (default: all language columns)")
    src.add_argument("--sheet", help="Worksheet name for XLSX (default: first)")
    src.add_argument("--name-by", default=config.NAME_BY,
                     help=f"Column for file names (default: {config.NAME_BY}; 'none' = name by text)")
    src.add_argument("--lang-map", "-l", nargs="+", metavar="COLUMN=CODE",
                     help="Force a column's language, e.g. Text=mr or Text=fr-CA")
    src.add_argument("--no-header", action="store_true", help="Sheet has no header row")
    src.add_argument("--delimiter", help="CSV delimiter (default: auto-detect , tab ; |)")

    out = p.add_argument_group("output")
    out.add_argument("--out", "-o", default=str(config.OUTPUT_DIR), help="Output folder (default: output/)")
    out.add_argument("--format", "-f", default=config.FORMAT, choices=config.FORMATS)
    out.add_argument("--tempo", type=float, default=config.TEMPO,
                     help=f"Playback tempo, pitch kept (default: {config.TEMPO}; 1 = off)")
    out.add_argument("--lead-silence", type=int, default=config.LEAD_SILENCE_MS,
                     help=f"Silence before speech in ms (default: {config.LEAD_SILENCE_MS}; 0 = off)")
    out.add_argument("--sample-rate", type=int, default=config.SAMPLE_RATE, help="Resample, e.g. 16000")
    out.add_argument("--overwrite", action="store_true", help="Regenerate files that already exist")

    voice = p.add_argument_group("voice")
    voice.add_argument("--engine", "-e", default=config.ENGINE, choices=list(config.ENGINE_ORDER),
                       help="gtts = Google first (default); auto/edge = Edge neural voices first; "
                            "each falls back to the other for languages it lacks")
    voice.add_argument("--gender", default=config.GENDER, choices=["female", "male"], help="Edge voice gender")
    voice.add_argument("--voice", "-v", nargs="+", metavar="LANG=VOICE",
                       help="Edge voice per language, e.g. hi=hi-IN-MadhurNeural")
    voice.add_argument("--english-locale", default=config.ENGLISH_LOCALE,
                       help=f"Edge accent for English (default: {config.ENGLISH_LOCALE})")
    voice.add_argument("--rate", type=int, default=config.RATE, help="Edge speaking rate in %%")
    voice.add_argument("--pitch", type=int, default=config.PITCH, help="Edge pitch in Hz")
    voice.add_argument("--list-languages", action="store_true", help="List supported languages and exit")
    voice.add_argument("--list-voices", metavar="LANG", help="List Edge voices for a language code and exit")

    p.add_argument("--concurrency", type=int, default=config.CONCURRENCY,
                   help=f"Parallel requests (default: {config.CONCURRENCY})")
    return p


def main(argv=None):
    asyncio.run(run(build_parser().parse_args(argv)))
