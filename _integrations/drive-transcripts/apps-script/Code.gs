/**
 * Transcripts → Markdown
 *
 * Tourne dans le compte Google Workspace {{INTEL_DRIVE_ACCOUNT}}, chaque lundi vers 5 h. Lit le Drive
 * partagé qui reçoit les notes et transcriptions Gemini des réunions et exporte chaque Google Doc
 * en Markdown dans le dossier « Transcripts-md » du Mon Drive. Drive pour
 * ordinateur ramène ces fichiers sur le Mac ; scripts/sync-intel.py les copie
 * ensuite dans 00-intel/inbox/ du cockpit.
 *
 * Copie de référence versionnée : _integrations/drive-transcripts/apps-script/Code.gs
 * Installation pas à pas      : _integrations/drive-transcripts/README.md
 *
 * Fonctions à lancer à la main depuis l'éditeur :
 *   tester()          exporte la note la plus récente dans Transcripts-md/_test.md
 *   installer()       crée le déclencheur du lundi et lance une première synchro
 *   synchroniser()    une passe de synchro (c'est ce que lance le déclencheur)
 *   reinitialiser()   le prochain passage repart des 30 derniers jours (fichiers réécrits, pas dupliqués)
 *
 * Historique : le tout premier passage exporte les réunions des 30 derniers jours, jamais au-delà.
 * Ensuite, chaque passage ne lit que les Docs créés ou modifiés depuis le passage précédent :
 * le dossier n'est jamais retéléchargé en entier.
 *
 * Le script ne fait que lire le Drive partagé : il n'y modifie et n'y supprime rien.
 */

const CONFIG = {
  SOURCE_DRIVE_ID: '{{INTEL_DRIVE_ID}}',  // ID du Drive partagé des transcriptions (commence par « 0A »)
  TARGET_FOLDER_NAME: 'Transcripts-md',    // créé à la racine du Mon Drive
  INITIAL_DAYS: 30,                        // profondeur d'historique du tout premier passage
  WEEKLY_HOUR: 5,                          // lundi entre 5 h et 6 h (fuseau du projet), avant la routine locale de 7 h
  SETTLE_MINUTES: 30,                      // une note modifiée il y a moins de 30 min attend le passage suivant
  TIME_BUDGET_MS: 4.5 * 60 * 1000,         // marge sous la limite de 6 min d'Apps Script
  // Réunions qui ne quittent jamais le Drive partagé (filtre sur le titre). Ajoutez vos propres
  // motifs, par exemple le nom de votre page de prise de rendez-vous avec les candidats.
  // Même liste que EXCLUSIONS dans scripts/sync-intel.py.
  EXCLUDE: [
    /entrevue|candidat|interview|entretien d.embauche/i, // entretiens de candidats (pas « entretiens de cadrage »)
    /accounting|comptab|\bcompta\b|\bfinance\b/i,      // comptabilité et finance
  ],
  // Quand la réunion n'est pas dans la langue réglée sur Meet, Gemini crée une note vide
  // (« A summary wasn't produced… ») puis la vraie note dans l'autre langue, suffixées
  // « (English) » et « (French) ». La note vide est écartée, quelle que soit sa langue.
  EMPTY_NOTE: /A summary wasn't produced|Aucun résumé|résumé n'a pas été (généré|produit)/i,
  EMPTY_NOTE_MAX_CHARS: 8000, // au-delà, la transcription a de la valeur même sans résumé
};

const DRIVE_API = 'https://www.googleapis.com/drive/v3';
const DOC_MIME = 'application/vnd.google-apps.document';
const FOLDER_MIME = 'application/vnd.google-apps.folder';

// ---------------------------------------------------------------- points d'entrée

function synchroniser() {
  verifierConfig_();
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(10 * 1000)) return; // une passe tourne déjà
  try {
    const started = Date.now();
    const props = PropertiesService.getScriptProperties();
    supprimerSuite_(props);
    // DEBUT : fixé au premier passage, aucune réunion antérieure n'est jamais exportée.
    // WATERMARK : date de modification du dernier Doc traité, on ne lit que ce qui est plus récent.
    let debut = props.getProperty('DEBUT');
    if (!debut) {
      debut = daysAgo_(CONFIG.INITIAL_DAYS);
      props.setProperty('DEBUT', debut);
    }
    const since = props.getProperty('WATERMARK') || debut;
    const settleLimit = new Date(Date.now() - CONFIG.SETTLE_MINUTES * 60 * 1000).toISOString();
    const target = targetFolder_();
    const counts = {};
    const errors = [];
    let incomplete = false;

    for (const f of listSource_(since)) {
      if (f.modifiedTime > settleLimit) break; // trié par date : tout ce qui suit est plus récent
      if (Date.now() - started > CONFIG.TIME_BUDGET_MS) { incomplete = true; break; }
      let result;
      try {
        result = processFile_(f, target, debut.slice(0, 10));
      } catch (e) {
        result = 'erreur';
        errors.push({ id: f.id, titre: f.name, message: String(e.message || e).slice(0, 300) });
      }
      counts[result] = (counts[result] || 0) + 1;
      props.setProperty('WATERMARK', f.modifiedTime);
    }

    upsert_(target, '_etat.json', JSON.stringify({
      derniere_execution: new Date().toISOString(),
      debut: debut,
      watermark: props.getProperty('WATERMARK'),
      compteurs: counts,
      erreurs: errors,
      reste_a_traiter: incomplete,
      fuseau: Session.getScriptTimeZone(),
    }, null, 2));
    if (incomplete) programmerSuite_(props);
    console.log(JSON.stringify({ counts, errors: errors.length, incomplete }));
  } finally {
    lock.releaseLock();
  }
}

function installer() {
  ScriptApp.getProjectTriggers()
    .filter(t => t.getHandlerFunction() === 'synchroniser')
    .forEach(t => ScriptApp.deleteTrigger(t));
  PropertiesService.getScriptProperties().deleteProperty('SUITE_TRIGGER');
  ScriptApp.newTrigger('synchroniser').timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY).atHour(CONFIG.WEEKLY_HOUR).create();
  console.log('Déclencheur créé : chaque lundi à ' + CONFIG.WEEKLY_HOUR + ' h, fuseau '
    + Session.getScriptTimeZone() + '. Synchro en cours…');
  synchroniser();
}

function tester() {
  verifierConfig_();
  let files = listSource_(daysAgo_(CONFIG.INITIAL_DAYS)).filter(f => f.mimeType === DOC_MIME);
  if (!files.length) files = listSource_(null).filter(f => f.mimeType === DOC_MIME);
  if (!files.length) throw new Error('Aucun Google Doc trouvé dans le Drive partagé ' + CONFIG.SOURCE_DRIVE_ID);
  const f = files[files.length - 1]; // le plus récemment modifié
  const md = exportDoc_(f.id);
  upsert_(targetFolder_(), '_test.md', frontmatter_(f) + md);
  console.log('Export de « ' + f.name + ' » : ' + md.length + ' caractères. Début :\n\n' + md.slice(0, 1500));
}

function reinitialiser() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty('WATERMARK');
  props.deleteProperty('DEBUT');
  console.log('Repères effacés : le prochain passage repart des ' + CONFIG.INITIAL_DAYS + ' derniers jours.');
}

function verifierConfig_() {
  if (CONFIG.SOURCE_DRIVE_ID.indexOf('{{') === 0) {
    throw new Error('Renseignez CONFIG.SOURCE_DRIVE_ID avec l\'ID du Drive partagé des transcriptions.');
  }
}

// Passage coupé par la limite de 6 minutes : la suite part 10 minutes plus tard
// au lieu d'attendre le lundi suivant.
function programmerSuite_(props) {
  supprimerSuite_(props);
  const t = ScriptApp.newTrigger('synchroniser').timeBased().after(10 * 60 * 1000).create();
  props.setProperty('SUITE_TRIGGER', t.getUniqueId());
}

function supprimerSuite_(props) {
  const id = props.getProperty('SUITE_TRIGGER');
  if (!id) return;
  ScriptApp.getProjectTriggers()
    .filter(t => t.getUniqueId() === id)
    .forEach(t => ScriptApp.deleteTrigger(t));
  props.deleteProperty('SUITE_TRIGGER');
}

// ---------------------------------------------------------------- traitement

function processFile_(f, target, debutDay) {
  if (CONFIG.EXCLUDE.some(re => re.test(f.name))) return 'exclu';
  if (meetingDay_(f) < debutDay) return 'avant_debut'; // vieille réunion retouchée : reste hors historique
  let body;
  if (f.mimeType === DOC_MIME) {
    body = exportDoc_(f.id);
    if (CONFIG.EMPTY_NOTE.test(body) && body.length < CONFIG.EMPTY_NOTE_MAX_CHARS) {
      trashIfExists_(target, targetName_(f)); // retire un export vide d'un passage antérieur
      return 'vide';
    }
  } else if (/\.md$/i.test(f.name)) {
    body = fetch_(DRIVE_API + '/files/' + f.id + '?alt=media&supportsAllDrives=true', true);
  } else {
    return 'ignore'; // feuilles de calcul, images, etc.
  }
  upsert_(target, targetName_(f), frontmatter_(f) + body);
  return 'exporte';
}

function exportDoc_(id) {
  const md = fetch_(DRIVE_API + '/files/' + id + '/export?mimeType=' + encodeURIComponent('text/markdown'), true);
  // Les images arrivent en base64 dans l'export : inutiles ici et très lourdes.
  return md
    .replace(/!\[[^\]]*\]\(data:[^)]*\)/g, '[image retirée]')
    .replace(/^\[image\d+\]:\s*<?data:.*$/gm, '');
}

function listSource_(since) {
  const q = ['trashed = false', "mimeType != '" + FOLDER_MIME + "'"];
  if (since) q.push("modifiedTime > '" + since + "'");
  let files = [];
  let pageToken = null;
  do {
    const params = {
      corpora: 'drive',
      driveId: CONFIG.SOURCE_DRIVE_ID,
      includeItemsFromAllDrives: 'true',
      supportsAllDrives: 'true',
      q: q.join(' and '),
      orderBy: 'modifiedTime',
      pageSize: '200',
      fields: 'nextPageToken, files(id, name, mimeType, modifiedTime, createdTime)',
    };
    if (pageToken) params.pageToken = pageToken;
    const res = fetch_(DRIVE_API + '/files?' + qs_(params));
    files = files.concat(res.files || []);
    pageToken = res.nextPageToken;
  } while (pageToken);
  return files;
}

// ---------------------------------------------------------------- nommage et en-tête

// « Business Follow Up - 2026 09 15 15:06 CEST - Notes by Gemini »
// → « 2026-09-15 1506 Business Follow Up - Notes by Gemini [a1b2c3].md »
function targetName_(f) {
  const base = f.name.replace(/\.md$/i, '');
  const m = base.match(/(\d{4})[ _/](\d{2})[ _/](\d{2})[ _](\d{2})[:_](\d{2})/);
  const stamp = m
    ? m[1] + '-' + m[2] + '-' + m[3] + ' ' + m[4] + m[5]
    : f.createdTime.slice(0, 10);
  const title = base
    .replace(/\s*-?\s*\d{4}[ _/]\d{2}[ _/]\d{2}[ _]\d{2}[:_]\d{2}(\s+(?:GMT[+-]\d{2}:\d{2}|[A-Z]{2,5}))?\s*/, ' ')
    .replace(/[\\/:*?"<>|]/g, '-')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 120);
  return stamp + ' ' + title + ' [' + f.id.slice(-6) + '].md';
}

function frontmatter_(f) {
  const m = f.name.match(/(\d{4})[ _/](\d{2})[ _/](\d{2})[ _](\d{2})[:_](\d{2})(\s+(?:GMT[+-]\d{2}:\d{2}|[A-Z]{2,5}))?/);
  const meetingDate = m
    ? m[1] + '-' + m[2] + '-' + m[3] + ' ' + m[4] + ':' + m[5] + (m[6] || '')
    : f.createdTime;
  const link = f.mimeType === DOC_MIME
    ? 'https://docs.google.com/document/d/' + f.id + '/edit'
    : 'https://drive.google.com/file/d/' + f.id + '/view';
  return [
    '---',
    'source: drive-transcripts',
    'doc_id: ' + f.id,
    'titre: ' + JSON.stringify(f.name),
    'date_reunion: ' + JSON.stringify(meetingDate.trim()),
    'lien: ' + link,
    'modifie: ' + f.modifiedTime,
    'exporte: ' + new Date().toISOString(),
    '---',
    '',
    '',
  ].join('\n');
}

// ---------------------------------------------------------------- utilitaires

function daysAgo_(n) {
  return new Date(Date.now() - n * 24 * 60 * 60 * 1000).toISOString();
}

// Jour de la réunion (AAAA-MM-JJ) lu dans le titre Gemini, sinon date de création du Doc.
function meetingDay_(f) {
  const m = f.name.match(/(\d{4})[ _/](\d{2})[ _/](\d{2})[ _](\d{2})[:_](\d{2})/);
  return m ? m[1] + '-' + m[2] + '-' + m[3] : f.createdTime.slice(0, 10);
}

function targetFolder_() {
  const root = DriveApp.getRootFolder();
  const it = root.getFoldersByName(CONFIG.TARGET_FOLDER_NAME);
  return it.hasNext() ? it.next() : root.createFolder(CONFIG.TARGET_FOLDER_NAME);
}

function upsert_(folder, name, content) {
  const it = folder.getFilesByName(name);
  if (it.hasNext()) {
    it.next().setContent(content);
  } else {
    folder.createFile(name, content, MimeType.PLAIN_TEXT);
  }
}

// Corbeille Drive (récupérable 30 jours), et seulement pour un fichier créé par ce script.
function trashIfExists_(folder, name) {
  const it = folder.getFilesByName(name);
  while (it.hasNext()) it.next().setTrashed(true);
}

function fetch_(url, raw) {
  const res = UrlFetchApp.fetch(url, {
    headers: { Authorization: 'Bearer ' + ScriptApp.getOAuthToken() },
    muteHttpExceptions: true,
  });
  const code = res.getResponseCode();
  if (code >= 300) {
    throw new Error('Drive API ' + code + ' : ' + res.getContentText().slice(0, 300));
  }
  return raw ? res.getContentText('UTF-8') : JSON.parse(res.getContentText());
}

function qs_(params) {
  return Object.keys(params)
    .map(k => encodeURIComponent(k) + '=' + encodeURIComponent(params[k]))
    .join('&');
}

