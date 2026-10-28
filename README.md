# gTTS-text-to-speach

Turn a spreadsheet of multilingual text into ready-to-use voice clips: one `.wav` per row and language.

| ID | English | Hindi | ... | ... | ... | Marathi |
|---|---|---|---|---|---|---|
| S01 | The ball is red. | गेंद लाल है। | ... | ... | ... | चेंडू लाल आहे. |


```bash
python3 main.py Sheet.xlsx
```

```
output/
├── english/  A01.wav  A02.wav  ...
├── hindi/    A01.wav  A02.wav  ...
├── telugu/   ...
├── tamil/    ...
├── kannada/  ...
└── marathi/  ...
```

## Features

- **CSV or Excel input.** Comma- or tab-separated CSV, or any worksheet in an `.xlsx`.
- **Language from the column header.** Columns named `English`, `Hindi`, `Marathi`, `tamil_sentence` and so on are converted. Other columns, such as `ID` and `Stage`, are skipped.
- **79 languages.** Add a column named after any [supported language](#supported-languages) and it's picked up with no code changes. If a header isn't a language name, the language is detected from the text's script (Devanagari, Tamil, Arabic, Cyrillic, Chinese, Japanese, ...).
- **Best available voice for each language.** Google TTS is used by default. Languages Google doesn't cover switch to Microsoft Edge neural voices automatically.
- **Files named by ID.** `output/<language>/<ID>.wav`, so an app can look up any clip by row ID and language.
- **Clear speech for learners.** 400 ms of silence before each clip, and speech slowed to 0.9× without changing pitch.
- **Installs its own dependencies.** Missing Python packages are pip-installed on first run, and ffmpeg is installed with Homebrew if needed.
- **Safe to re-run.** Existing files are skipped, so only new rows are generated. Use `--overwrite` to rebuild everything.

## Supported languages

79 languages. Name a column after the language, for example `Hindi`, `French` or `Chinese`. Headers like `hindi_sentence` and `Chinese (Simplified)` also work, and letter case doesn't matter.

The **Voice** column shows which engine can speak each language. Google is used when available, unless you pass `--engine auto` to prefer Edge.

### Indian languages

| Language | Code | Voice | Language | Code | Voice |
|---|---|---|---|---|---|
| Bengali | `bn` | Google + Edge | Marathi | `mr` | Google + Edge |
| English | `en` | Google + Edge | Nepali | `ne` | Google + Edge |
| Gujarati | `gu` | Google + Edge | Punjabi | `pa` | Google |
| Hindi | `hi` | Google + Edge | Tamil | `ta` | Google + Edge |
| Kannada | `kn` | Google + Edge | Telugu | `te` | Google + Edge |
| Malayalam | `ml` | Google + Edge | Urdu | `ur` | Google + Edge |

<details>
<summary><b>All other languages (67)</b></summary>

| Language | Code | Voice | Language | Code | Voice | Language | Code | Voice |
|---|---|---|---|---|---|---|---|---|
| Afrikaans | `af` | Google + Edge | Greek | `el` | Google + Edge | Persian | `fa` | Edge |
| Albanian | `sq` | Google + Edge | Hausa | `ha` | Google | Polish | `pl` | Google + Edge |
| Amharic | `am` | Google + Edge | Hebrew | `he` | Google + Edge | Portuguese | `pt` | Google + Edge |
| Arabic | `ar` | Google + Edge | Hungarian | `hu` | Google + Edge | Romanian | `ro` | Google + Edge |
| Azerbaijani | `az` | Edge | Icelandic | `is` | Google + Edge | Russian | `ru` | Google + Edge |
| Basque | `eu` | Google | Indonesian | `id` | Google + Edge | Serbian | `sr` | Google + Edge |
| Bosnian | `bs` | Google + Edge | Irish | `ga` | Edge | Sinhala | `si` | Google + Edge |
| Bulgarian | `bg` | Google + Edge | Italian | `it` | Google + Edge | Slovak | `sk` | Google + Edge |
| Burmese | `my` | Google + Edge | Japanese | `ja` | Google + Edge | Slovenian | `sl` | Edge |
| Cantonese | `yue` | Google + Edge | Javanese | `jv` | Google + Edge | Somali | `so` | Edge |
| Catalan | `ca` | Google + Edge | Kazakh | `kk` | Edge | Spanish | `es` | Google + Edge |
| Chinese | `zh` | Google + Edge | Khmer | `km` | Google + Edge | Sundanese | `su` | Google + Edge |
| Croatian | `hr` | Google + Edge | Korean | `ko` | Google + Edge | Swahili | `sw` | Google + Edge |
| Czech | `cs` | Google + Edge | Lao | `lo` | Edge | Swedish | `sv` | Google + Edge |
| Danish | `da` | Google + Edge | Latin | `la` | Google | Thai | `th` | Google + Edge |
| Dutch | `nl` | Google + Edge | Latvian | `lv` | Google + Edge | Turkish | `tr` | Google + Edge |
| Estonian | `et` | Google + Edge | Lithuanian | `lt` | Google + Edge | Ukrainian | `uk` | Google + Edge |
| Filipino | `fil` | Google + Edge | Macedonian | `mk` | Edge | Uzbek | `uz` | Edge |
| Finnish | `fi` | Google + Edge | Malay | `ms` | Google + Edge | Vietnamese | `vi` | Google + Edge |
| French | `fr` | Google + Edge | Maltese | `mt` | Edge | Welsh | `cy` | Google + Edge |
| Galician | `gl` | Google + Edge | Mongolian | `mn` | Edge | Zulu | `zu` | Edge |
| Georgian | `ka` | Edge | Norwegian | `nb` | Google + Edge | | | |
| German | `de` | Google + Edge | Pashto | `ps` | Edge | | | |

</details>

You can also print this list: `python3 main.py --list-languages`.

**Not available:** Assamese, Odia, Sanskrit and Inuktitut have no working voice in either engine. Columns in these languages are skipped with a warning.

**Shared scripts:** some languages share a script, so name the column, or set its language with `-l <column>=<code>`:
- Hindi, Marathi and Nepali (Devanagari). Unnamed columns default to Hindi.
- Arabic, Urdu, Persian and Pashto (Arabic script). Unnamed columns default to Urdu.
- Russian, Ukrainian, Bulgarian and others (Cyrillic). Unnamed columns default to Russian.
- Most European and African languages (Latin script). Unnamed columns default to English.

**Regional variants:** Google's `fr-CA`, `pt-PT` and `zh-TW` work with `-l <column>=fr-CA`. For other accents with Edge voices, use `--voice`, for example `-v es=es-MX-DaliaNeural`.

## Setup

Requires Python 3.9+ and ffmpeg (installed automatically on macOS with Homebrew).

```bash
git clone https://github.com/ShivaShirsath/gTTS-text-to-speach.git && cd gTTS-text-to-speach
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # optional; the script installs what's missing
```

## Quick start with the sample

[`examples/sample.csv`](examples/sample.csv) has 3 words and 3 sentences in 6 languages, in the same layout as a real sheet:

| ID | Stage | English | Hindi | Telugu | Tamil | Kannada | Marathi |
|---|---|---|---|---|---|---|---|
| W01 | Words | apple | सेब | ఆపిల్ | ஆப்பிள் | ಸೇಬು | सफरचंद |
| S01 | Sentences | The ball is red. | गेंद लाल है। | బంతి ఎరుపు రంగులో ఉంది. | பந்து சிவப்பு நிறத்தில் உள்ளது. | ಚೆಂಡು ಕೆಂಪು ಬಣ್ಣದ್ದಾಗಿದೆ. | चेंडू लाल आहे. |

```bash
python3 main.py examples/sample.csv
```

This creates 36 clips (6 rows × 6 languages):

```
output/
├── english/  W01.wav W02.wav W03.wav S01.wav S02.wav S03.wav
├── hindi/    W01.wav ...
└── ...
```

To use your own data, keep the same layout: an `ID` column, then one column per language, named after the language. Extra columns such as `Stage` are ignored.

## Usage

```bash
# All language columns -> output/<language>/<ID>.wav
python3 main.py Sheet.xlsx

# Only some languages
python3 main.py sheet.xlsx -c Hindi Marathi

# A different output folder or worksheet
python3 main.py sheet.xlsx -o ~/audio --sheet "Audio Bank"

# Slower speech, no leading silence
python3 main.py sheet.xlsx --tempo 0.8 --lead-silence 0

# More natural-sounding voices (Microsoft Edge neural TTS)
python3 main.py sheet.xlsx --engine auto --gender male

# Show every supported language, or the Edge voices for one language
python3 main.py --list-languages
python3 main.py --list-voices mr
```

### Options

| Option | Default | Description |
|---|---|---|
| `-c, --columns` | all language columns | Columns to convert (name or 0-based index, any letter case) |
| `-o, --out` | `output/` | Output folder |
| `--name-by` | `ID` | Column used for file names; `none` names files by their text |
| `--sheet` | first sheet | Worksheet name for `.xlsx` |
| `-f, --format` | `wav` | `wav`, `mp3` or `m4a` |
| `--tempo` | `0.9` | Playback speed with pitch kept (0.5–2.0, `1` = off) |
| `--lead-silence` | `400` | Silence before speech, in ms |
| `--sample-rate` | source (24 kHz) | Resample, e.g. `16000` |
| `-e, --engine` | `gtts` | `gtts` (Google first), `auto`/`edge` (Edge neural voices first), `say` (macOS). Each falls back to the other engine for languages it lacks. |
| `--gender` | `female` | Edge voice gender |
| `-v, --voice` | | Pick an Edge voice, e.g. `hi=hi-IN-MadhurNeural` |
| `--list-voices` | | List Edge voices for a language, e.g. `--list-voices ta` |
| `--list-languages` | | List all supported languages and which engine speaks each one |
| `-l, --lang-map` | | Set a column's language, e.g. `Text=mr` or `Text=fr-CA` |
| `--overwrite` | off | Regenerate files that already exist |

## Add the audio to Google Sheets

[`google_sheets/google_sheet_audio_links.gs`](google_sheets/google_sheet_audio_links.gs) adds a **`<Language> Audio`** column next to each language column. Each cell links to that row's clip in Google Drive, and a sidebar player plays clips inside the sheet.

| ID | English | English Audio | Hindi | Hindi Audio | ... | Marathi | Marathi Audio |
|---|---|---|---|---|---|---|---|
| S01 | The ball is red. | ▶ S01 | गेंद लाल है। | ▶ S01 | ... | चेंडू लाल आहे. | ▶ S01 |

The steps below use `sample.csv`. They work the same for any sheet.

### Step 1: Generate the audio

```bash
python3 main.py examples/sample.csv
```

### Step 2: Put the data in Google Sheets

1. Open [sheets.new](https://sheets.new) to create a blank Google Sheet.
2. Go to **File → Import → Upload** and choose `sample.csv`.
3. In the import dialog, set **Import location** to **Replace current sheet**. Untick **Convert text to numbers, dates and formulas**, so IDs such as `001` keep their leading zeros and still match the file names.
4. Click **Import data**.

If your data is in an `.xlsx` file, upload it to Drive and open it, then choose **File → Save as Google Sheets**. Apps Script only works on a real Google Sheet, not an Excel file opened in Drive.

### Step 3: Upload the audio to Google Drive

1. In [Google Drive](https://drive.google.com), choose **New → Folder upload** and select the `output` folder.
2. Open the uploaded `output` folder and copy its ID, the last part of the URL: `drive.google.com/drive/folders/`**`1AbC...xyz`**.
3. Share the folder with everyone who uses the sheet, for example **Share → General access → Anyone in your organization with the link → Viewer**. Without access, the links won't play for them.

### Step 4: Add the linking script

1. In the Google Sheet, go to **Extensions → Apps Script**.
2. Delete everything in `Code.gs`, then paste in the contents of [`google_sheets/google_sheet_audio_links.gs`](google_sheets/google_sheet_audio_links.gs).
3. Replace `PASTE_OUTPUT_FOLDER_ID_HERE` with the folder ID from Step 3:
   ```js
   const OUTPUT_FOLDER_ID = '1AbC...xyz';
   ```
4. Save with **Ctrl/Cmd + S**.

### Step 5: Link the audio

You can run the script in either of two ways:

- **From the sheet (recommended).** Reload the sheet tab. A new **Audio** menu appears. Choose **Audio → Add audio links**.
- **From the editor.** In the dropdown next to **Debug**, select **`addAudioLinks`** (not `onOpen`), then click **Run**. The report appears in the **Execution log**. The links go into the sheet tab that was open last.

The first run asks for permission to use Drive: **Review permissions → choose your account → Advanced → Go to project (unsafe) → Allow**. This is Google's standard warning for scripts you write yourself.

A report then shows the linked rows per language, for example `Hindi: 6 / 6 rows linked`. A **`<Language> Audio`** column now sits next to each language column.

### Step 6: Listen

- Choose **Audio → Open audio player** and click any **▶** cell. The clip plays in the sidebar on the right. Click another **▶** cell to switch clips.
- Clicking a **▶** link opens the clip in Drive's own player instead.

To add more rows later, generate the new audio, upload the new files into the same Drive folders, and run **Add audio links** again. Existing audio columns are updated, not duplicated.

### Troubleshooting

| Problem | Fix |
|---|---|
| No **Audio** menu | Save the script, then reload the sheet tab. |
| `Cannot call SpreadsheetApp.getUi() from this context` | You ran `onOpen` from the editor. Run `addAudioLinks` instead, or use the menu in the sheet. |
| `No sheet found` | The script was created at script.google.com, so it isn't attached to the sheet. Create it from the sheet with **Extensions → Apps Script**. |
| "No audio linked" | `OUTPUT_FOLDER_ID` isn't the `output` folder. The report lists the folders it found next to your column headers. |
| `0 / N rows linked` | The `ID` values don't match the file names. Check for numbers that lost their leading zeros on import (`001` → `1`). |
| A link opens but won't play for a teammate | Share the Drive folder with them, or have them use the sidebar player. |

## Change the defaults

Every setting lives in [`text2audio/config.py`](text2audio/config.py). Edit a value there to change it for every run, or override it for one run with a command-line option.

```python
OUTPUT_DIR = PROJECT_ROOT / "output"   # where clips are saved
ENGINE = "gtts"                         # gtts | auto | edge | say
TEMPO = 0.9                             # playback speed, pitch kept
LEAD_SILENCE_MS = 400                   # silence before speech
FORMAT = "wav"                          # wav | mp3 | m4a
NAME_BY = "ID"                          # column used for file names
GENDER = "female"                       # Edge voice gender
CONCURRENCY = 4                         # parallel TTS requests
```

To add a language or change a language's voice, edit the `LANGUAGES` table in the same file.

## How it works

1. **Read the sheet** (`sheet.py`). The script loads the CSV or worksheet, and `language.py` works out each column's language from its header, or from the script the text is written in.
2. **Choose the voices** (`pipeline.py`). Each language gets Google TTS or an Edge voice, following `ENGINE_ORDER` in `config.py`.
3. **Synthesize the speech** (`audio.py`). Each text is sent to its engine, a few requests at a time, with retries.
4. **Process the audio** (`audio.py`). ffmpeg adds the leading silence, applies `atempo` and writes 16-bit mono WAV, the same processing as `examples/text_to_wav_single.py`.
5. **Save the file.** Each clip is saved as `output/<language>/<ID>.wav`.

## Project structure

```
.
├── main.py                     # Entry point: python3 main.py <sheet> [options]
├── text2audio/                 # The package
│   ├── config.py               # All settings and the language table
│   ├── cli.py                  # Command-line options (defaults from config.py)
│   ├── pipeline.py             # Sheet → jobs → voice choice → audio files
│   ├── sheet.py                # Read CSV/XLSX, pick columns, build file names
│   ├── language.py             # Language detection and engine language codes
│   ├── audio.py                # gTTS / Edge / say engines and ffmpeg processing
│   ├── deps.py                 # Install missing packages and ffmpeg on first use
│   └── __main__.py             # Also runnable as: python3 -m text2audio <sheet>
├── examples/
│   ├── sample.csv              # 6 rows in 6 languages
│   └── text_to_wav_single.py   # Original single-text version (same audio settings)
├── google_sheets/
│   └── google_sheet_audio_links.gs   # Apps Script: audio links and player in Google Sheets
├── output/                     # Generated audio: output/<language>/<ID>.wav
└── requirements.txt
```

The modules depend on each other in one direction only: `main.py → cli → pipeline → sheet / language / audio / deps → config`.

## Notes

- Both gTTS and Edge TTS need an internet connection.
- Edge voices (`--engine auto`, and the automatic fallback for languages Google lacks) come from the unofficial Microsoft Edge read-aloud service, which may change or be rate-limited. For production, use Azure Speech (same voices) or Google Cloud TTS.
- `edge-tts` is only installed the first time a sheet needs an Edge voice.
