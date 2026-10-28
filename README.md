# text2audio

Turn a spreadsheet of multilingual text into ready-to-use voice clips: one `.wav` per row and language.

```
ID   | English                         | Hindi                       | Telugu | Tamil | Kannada | Marathi
A01  | I didn't quite catch that. ...  | मुझे ठीक से सुनाई नहीं दिया। ... | ...    | ...   | ...     | ...
```

```bash
python3 csv_to_audio.py ASR_Retry_Feedback_Bank.xlsx
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
- **New languages without code changes.** Add a column and it's picked up. A header that isn't a language name is detected from its script (Telugu, Tamil, Kannada, Gujarati, Bengali, ...).
- **Files named by ID.** `output/<language>/<ID>.wav`, so an app can look up any clip by row ID and language.
- **Clear speech for learners.** 400 ms of silence before each clip, and speech slowed to 0.9× without changing pitch.
- **Installs its own dependencies.** Missing Python packages are pip-installed on first run, and ffmpeg is installed with Homebrew if needed.
- **Safe to re-run.** Existing files are skipped, so only new rows are generated. Use `--overwrite` to rebuild everything.

## Supported languages

| Language | Code | | Language | Code |
|---|---|---|---|---|
| English | `en` | | Gujarati | `gu` |
| Hindi | `hi` | | Bengali | `bn` |
| Marathi | `mr` | | Malayalam | `ml` |
| Telugu | `te` | | Punjabi | `pa` |
| Tamil | `ta` | | Urdu | `ur` |
| Kannada | `kn` | | Nepali | `ne` |

## Setup

Requires Python 3.9+ and ffmpeg (installed automatically on macOS with Homebrew).

```bash
git clone <repo-url> && cd text2audio
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt     # optional; the script installs what's missing
```

## Quick start with the sample

[`sample.csv`](sample.csv) has 3 words and 3 sentences in 6 languages, in the same layout as a real sheet:

| ID | Stage | English | Hindi | Telugu | Tamil | Kannada | Marathi |
|---|---|---|---|---|---|---|---|
| W01 | Words | apple | सेब | ఆపిల్ | ஆப்பிள் | ಸೇಬು | सफरचंद |
| S01 | Sentences | The ball is red. | गेंद लाल है। | బంతి ఎరుపు రంగులో ఉంది. | பந்து சிவப்பு நிறத்தில் உள்ளது. | ಚೆಂಡು ಕೆಂಪು ಬಣ್ಣದ್ದಾಗಿದೆ. | चेंडू लाल आहे. |

```bash
python3 csv_to_audio.py sample.csv
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
python3 csv_to_audio.py ASR_Retry_Feedback_Bank.xlsx

# Only some languages
python3 csv_to_audio.py sheet.xlsx -c Hindi Marathi

# A different output folder or worksheet
python3 csv_to_audio.py sheet.xlsx -o ~/audio --sheet "Feedback Bank"

# Slower speech, no leading silence
python3 csv_to_audio.py sheet.xlsx --tempo 0.8 --lead-silence 0

# More natural-sounding voices (Microsoft Edge neural TTS)
python3 csv_to_audio.py sheet.xlsx --engine auto --gender male
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
| `-e, --engine` | `gtts` | `gtts` (Google), `auto` (Edge neural voices, gTTS fallback), `edge`, `say` (macOS) |
| `--gender` | `female` | Edge voice gender |
| `-v, --voice` | | Pick an Edge voice, e.g. `hi=hi-IN-MadhurNeural` |
| `--list-voices` | | List Edge voices for a language, e.g. `--list-voices ta` |
| `-l, --lang-map` | | Set a column's language, e.g. `Text=mr` |
| `--overwrite` | off | Regenerate files that already exist |

Hindi, Marathi and Nepali share the Devanagari script. Name the column after the language, or set it with `-l <column>=mr`.

## Add the audio to Google Sheets

[`google_sheet_audio_links.gs`](google_sheet_audio_links.gs) adds a **`<Language> Audio`** column next to each language column. Each cell links to that row's clip in Google Drive, and a sidebar player plays clips inside the sheet.

| ID | English | English Audio | Hindi | Hindi Audio | ... |
|---|---|---|---|---|---|
| A01 | I didn't quite catch that... | ▶ A01 | मुझे ठीक से सुनाई नहीं दिया... | ▶ A01 | ... |

The steps below use `sample.csv`. They work the same for any sheet.

### Step 1: Generate the audio

```bash
python3 csv_to_audio.py sample.csv
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
2. Delete everything in `Code.gs`, then paste in the contents of [`google_sheet_audio_links.gs`](google_sheet_audio_links.gs).
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

## How it works

1. **Read the sheet.** The script reads the CSV or worksheet and finds the language of each column from its header, or from the script the text is written in.
2. **Synthesize the speech.** Each text is sent to the chosen TTS engine, a few requests at a time, with retries.
3. **Process the audio.** ffmpeg adds the leading silence, applies `atempo` and writes 16-bit mono WAV, the same processing as `text to wav single.py`.
4. **Save the file.** Each clip is saved as `output/<language>/<ID>.wav`.

## Files

| File | Purpose |
|---|---|
| `csv_to_audio.py` | Batch converter, sheet → audio |
| `text to wav single.py` | Original single-text version (same audio settings) |
| `google_sheet_audio_links.gs` | Apps Script that adds audio links and a player to Google Sheets |
| `sample.csv` | Small example input: 6 rows in 6 languages |
| `ASR_Retry_Feedback_Bank.xlsx` | Full example input: 100 retry feedback lines in 6 languages |
| `output/` | Generated audio |

## Notes

- Both gTTS and Edge TTS need an internet connection.
- `--engine auto` uses the unofficial Microsoft Edge read-aloud service, so it may change or be rate-limited. For production, use Azure Speech (same voices) or Google Cloud TTS.
- Odia has no voice in gTTS or Edge TTS and is skipped with a warning.
