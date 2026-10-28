"""TTS engines and ffmpeg post-processing."""
import asyncio
import os
import subprocess

from .config import NATIVE_FORMAT
from .language import edge_locale


async def list_edge_voices(edge_tts, lang):
    for v in await edge_tts.list_voices():
        if v["Locale"].split("-")[0] == lang:
            print(f'{v["ShortName"]:40} {v["Gender"]}')


async def pick_edge_voices(edge_tts, langs, gender, english_locale, overrides):
    voices = await edge_tts.list_voices()
    chosen = {}
    for lang in langs:
        if lang in overrides:
            chosen[lang] = overrides[lang]
            continue
        preferred = english_locale if lang == "en" else edge_locale(lang)
        if not preferred:
            continue
        base = preferred.split("-")[0]
        candidates = [v for v in voices if v["Locale"].split("-")[0] == base]
        candidates.sort(key=lambda v: (
            v["Locale"] != preferred,
            v["Gender"].lower() != gender,
            "Multilingual" in v["ShortName"],
        ))
        if candidates:
            chosen[lang] = candidates[0]["ShortName"]
    return chosen


def audio_filters(args):
    """Leading silence, then tempo change (same as examples/text_to_wav_single.py)."""
    filters = []
    if args.lead_silence:
        filters.append(f"adelay={args.lead_silence}:all=1")
    if args.tempo != 1:
        filters.append(f"atempo={args.tempo}")
    return filters


def needs_ffmpeg(args, engines):
    return (any(NATIVE_FORMAT[e] != args.format for e in engines)
            or args.sample_rate or audio_filters(args))


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
