"""Sheet -> jobs -> engine plan -> audio files."""
import asyncio
import importlib
import os
import sys
from collections import Counter

from .audio import list_edge_voices, needs_ffmpeg, pick_edge_voices, synthesize
from .config import ENGINE_ORDER, RETRIES, SAY_VOICES, TEMPO_RANGE
from .deps import ensure_ffmpeg, ensure_package
from .language import (column_hint, detect_language, dominant_script, folder_for,
                       gtts_code, print_languages)
from .sheet import find_column, load_rows, resolve_columns, safe_filename


def parse_pairs(items, what):
    pairs = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep:
            sys.exit(f"Bad {what} '{item}', expected KEY=VALUE")
        pairs[key.strip()] = value.strip()
    return pairs


def build_jobs(header, rows, args):
    """-> {(lang, filename): text}"""
    lang_map = {k.lower(): v for k, v in parse_pairs(args.lang_map, "--lang-map").items()}
    name_idx = find_column(header, args.name_by)
    if args.name_by.lower() != "none" and name_idx is None:
        print(f"[warn] no '{args.name_by}' column, naming files by their text")

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
    return jobs


async def plan_engines(langs, args, mods):
    """-> {lang: (engine, voice)}: preferred engine first, the next for what it lacks"""
    voice_map = parse_pairs(args.voice, "--voice")
    plan = {}
    for engine in ENGINE_ORDER[args.engine]:
        missing = [lang for lang in langs if lang not in plan]
        if not missing:
            break
        if engine == "say":
            for lang in missing:
                plan[lang] = ("say", voice_map.get(lang) or SAY_VOICES.get(lang))
        elif engine == "gtts":
            mods["gtts"] = ensure_package("gtts")
            supported = importlib.import_module("gtts.lang").tts_langs()
            for lang in missing:
                if gtts_code(lang) in supported:
                    plan[lang] = ("gtts", gtts_code(lang))
        else:
            mods["edge"] = ensure_package("edge_tts")
            try:
                voices = await pick_edge_voices(
                    mods["edge"], missing, args.gender, args.english_locale, voice_map)
            except Exception as e:
                print(f"[warn] Edge TTS unavailable ({e})")
                continue
            for lang, voice in voices.items():
                plan[lang] = ("edge", voice)
    return plan


def pending_files(jobs, plan, args):
    """-> ([(lang, text, out_path)], number skipped because they already exist)"""
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
    return todo, skipped


async def generate(todo, plan, mods, args):
    sem = asyncio.Semaphore(args.concurrency)

    async def one(lang, text, out_path):
        engine, voice = plan[lang]
        async with sem:
            for attempt in range(RETRIES):
                try:
                    await synthesize(mods, engine, voice, text, out_path, args)
                    print(f"[ok]   {out_path}")
                    return True
                except Exception as e:
                    error = e
                    await asyncio.sleep(2 ** attempt)
            print(f"[fail] {text!r}: {error}", file=sys.stderr)
            return False

    return await asyncio.gather(*(one(*job) for job in todo))


async def run(args):
    if args.list_languages:
        print_languages()
        return
    if args.list_voices:
        await list_edge_voices(ensure_package("edge_tts"), args.list_voices)
        return
    if not args.sheet_path:
        sys.exit("Pass a CSV/XLSX file (or --list-languages / --list-voices LANG)")
    if not TEMPO_RANGE[0] <= args.tempo <= TEMPO_RANGE[1]:
        sys.exit(f"--tempo must be between {TEMPO_RANGE[0]} and {TEMPO_RANGE[1]}")

    header, rows = load_rows(args)
    jobs = build_jobs(header, rows, args)
    if not jobs:
        sys.exit("No text found to convert")

    mods = {}
    langs = sorted({lang for lang, _ in jobs})
    plan = await plan_engines(langs, args, mods)
    for lang in langs:
        engine, voice = plan.get(lang, ("-", "no voice available, skipped"))
        print(f"{folder_for(lang):10} -> {engine} {voice or 'default'}")

    if needs_ffmpeg(args, {engine for engine, _ in plan.values()}):
        ensure_ffmpeg()

    todo, skipped = pending_files(jobs, plan, args)
    results = await generate(todo, plan, mods, args)
    created = sum(results)
    print(f"\nDone. created={created} skipped={skipped} failed={len(results) - created} -> {args.out}/")
