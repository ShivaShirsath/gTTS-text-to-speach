/**
 * Adds a "<Language> Audio" column right after each language column
 * (English, Hindi, ...) with a link to that row's audio file in Google Drive,
 * plus a sidebar player to listen to clips without leaving the sheet.
 *
 * Expects the generated folder uploaded to Drive:
 *   output/english/A01.wav, output/hindi/A01.wav, ...
 * OUTPUT_FOLDER_ID may be "output" or any folder above it; language folders
 * are found at any depth.
 *
 * Setup: Extensions -> Apps Script -> paste this file -> set OUTPUT_FOLDER_ID -> Save
 * Run:   reload the sheet, then menu "Audio" -> "Add audio links"
 * Play:  menu "Audio" -> "Open audio player", then click any ▶ cell
 * Safe to re-run: existing "<Language> Audio" columns are updated, not duplicated.
 */

// Drive folder ID of the uploaded "output" folder:
// https://drive.google.com/drive/folders/<THIS_PART>
const OUTPUT_FOLDER_ID = 'PASTE_OUTPUT_FOLDER_ID_HERE';
const ID_COLUMN = 'ID';
const HEADER_ROW = 1;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Audio')
    .addItem('Add audio links', 'addAudioLinks')
    .addItem('Open audio player', 'openPlayer')
    .addToUi();
}

/** Popup in the sheet; Execution log when run from the Apps Script editor. */
function notify_(title, message) {
  Logger.log(`${title}\n${message}`);
  try {
    const ui = SpreadsheetApp.getUi();
    ui.alert(title, message, ui.ButtonSet.OK);
  } catch (e) {
    // No UI when run from the editor; the log above has the report
  }
}

function addAudioLinks() {
  const sheet = SpreadsheetApp.getActiveSheet();
  if (!sheet) {
    throw new Error('No sheet found. Open the Google Sheet and use Extensions -> Apps Script ' +
      'to create this script, so it is attached to the sheet.');
  }
  const audio = loadAudioFiles_(DriveApp.getFolderById(OUTPUT_FOLDER_ID));

  const header = sheet.getRange(HEADER_ROW, 1, 1, sheet.getLastColumn()).getValues()[0]
    .map(h => String(h).trim());
  const idCol = header.findIndex(h => h.toLowerCase() === ID_COLUMN.toLowerCase());
  if (idCol < 0) {
    notify_('No ID column', `No "${ID_COLUMN}" column in row ${HEADER_ROW} of sheet "${sheet.getName()}".`);
    return;
  }

  const numRows = sheet.getLastRow() - HEADER_ROW;
  if (numRows < 1) return;
  const ids = sheet.getRange(HEADER_ROW + 1, idCol + 1, numRows, 1).getValues()
    .map(r => String(r[0]).trim());

  const report = [];
  // Right to left, so inserting a column never shifts one we still have to visit
  for (let c = header.length - 1; c >= 0; c--) {
    const files = audio[header[c].toLowerCase()];
    if (!files) continue;

    const audioHeader = `${header[c]} Audio`;
    const audioCol = c + 2; // 1-based column right after the language column
    if (header[c + 1] !== audioHeader) sheet.insertColumnAfter(c + 1);

    sheet.getRange(HEADER_ROW, audioCol).setValue(audioHeader).setFontWeight('bold');
    const links = ids.map(id =>
      [files[id] ? `=HYPERLINK("${files[id]}", "▶ ${id}")` : '']);
    sheet.getRange(HEADER_ROW + 1, audioCol, numRows, 1).setValues(links);

    const matched = links.filter(l => l[0]).length;
    report.unshift(`${header[c]}: ${matched} / ${numRows} rows linked`);
  }

  if (!report.length) {
    notify_(
      'No audio linked',
      `No Drive folder matches a column header.\n\n` +
      `Sheet: ${sheet.getName()}\n` +
      `Column headers: ${header.join(', ')}\n` +
      `Folders found: ${Object.keys(audio).join(', ') || '(none)'}\n\n` +
      `Check that OUTPUT_FOLDER_ID is the uploaded "output" folder ` +
      `(it should contain english, hindi, ... sub-folders).`);
    return;
  }
  const sample = Object.keys(Object.values(audio)[0] || {}).slice(0, 3).join(', ');
  notify_('Audio links added',
    `Sheet: ${sheet.getName()}\n` + report.join('\n') +
    `\n\nIf rows are 0, IDs don't match file names (files look like: ${sample}).` +
    `\nTo listen: Audio -> Open audio player, then click a ▶ cell.`);
}

/** { english: { A01: url, ... }, hindi: { ... } } from every folder under root */
function loadAudioFiles_(root, audio = {}) {
  const folders = root.getFolders();
  while (folders.hasNext()) {
    const folder = folders.next();
    const key = folder.getName().trim().toLowerCase();
    const files = audio[key] || {};
    const it = folder.getFiles();
    while (it.hasNext()) {
      const file = it.next();
      files[file.getName().replace(/\.[^.]+$/, '').trim()] = file.getUrl();
    }
    if (Object.keys(files).length) audio[key] = files;
    loadAudioFiles_(folder, audio);
  }
  return audio;
}

// ---------------------------------------------------------------- player

function openPlayer() {
  const html = HtmlService.createHtmlOutput(PLAYER_HTML).setTitle('Audio player');
  SpreadsheetApp.getUi().showSidebar(html);
}

/** Drive file ID of the selected ▶ cell, or null. Called by the sidebar. */
function getSelectedAudio() {
  const formula = SpreadsheetApp.getActiveRange().getFormula();
  const match = formula.match(/\/file\/d\/([\w-]+)/);
  return match ? match[1] : null;
}

/** Audio as a data URI, read with the viewer's own Drive access. */
function getAudioData(fileId) {
  const file = DriveApp.getFileById(fileId);
  const bytes = file.getBlob().getBytes();
  return {
    name: `${file.getParents().next().getName()} / ${file.getName()}`,
    src: `data:${file.getMimeType()};base64,${Utilities.base64Encode(bytes)}`,
  };
}

const PLAYER_HTML = `
<div style="font-family: sans-serif; padding: 8px">
  <p id="name" style="color:#555">Click a ▶ cell in an Audio column.</p>
  <audio id="player" controls style="width:100%"></audio>
</div>
<script>
  let current = null;
  function poll() {
    google.script.run
      .withSuccessHandler(id => {
        if (id && id !== current) {
          current = id;
          document.getElementById('name').textContent = 'Loading…';
          google.script.run
            .withSuccessHandler(a => {
              document.getElementById('name').textContent = a.name;
              const player = document.getElementById('player');
              player.src = a.src;
              player.play().catch(() => {});
            })
            .withFailureHandler(e => {
              document.getElementById('name').textContent = 'Cannot open file: ' + e.message;
            })
            .getAudioData(id);
        }
        setTimeout(poll, 800);
      })
      .withFailureHandler(() => setTimeout(poll, 2000))
      .getSelectedAudio();
  }
  poll();
</script>`;
