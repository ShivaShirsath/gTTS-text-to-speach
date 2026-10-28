"""Read CSV/XLSX sheets and pick columns."""
import csv
import re
import sys
import unicodedata

from .config import CSV_DELIMITERS, MAX_NAME_LEN
from .deps import ensure_package
from .language import column_hint


def read_sheet(path, sheet, delimiter):
    if path.lower().endswith((".xlsx", ".xlsm")):
        openpyxl = ensure_package("openpyxl")
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb[sheet] if sheet else wb.worksheets[0]
        return [["" if v is None else str(v) for v in row] for row in ws.iter_rows(values_only=True)]
    with open(path, newline="", encoding="utf-8-sig") as f:
        if not delimiter:
            first_line = f.readline()
            delimiter = max(CSV_DELIMITERS, key=first_line.count)
            f.seek(0)
        return list(csv.reader(f, delimiter=delimiter))


def load_rows(args):
    """-> (header, data rows)"""
    rows = read_sheet(args.sheet_path, args.sheet, args.delimiter)
    if not rows:
        sys.exit("Sheet is empty")
    if args.no_header:
        return [str(i) for i in range(max(len(r) for r in rows))], rows
    return [h.strip() for h in rows[0]], rows[1:]


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
