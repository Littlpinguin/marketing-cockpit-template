# Drive partagé de transcriptions → 00-intel

Fait entrer dans `00-intel/` les notes et transcriptions Gemini des réunions de l'équipe, internes et externes, pour que les routines du lundi préparent les communications et la newsletter à partir de ce qui se passe vraiment. Alternative à l'alimentation par n8n (module `automatisations`) quand l'entreprise travaille sous Google Workspace et que Gemini prend les notes de réunion dans Meet.

## Pourquoi un export

Drive pour ordinateur monte le Drive partagé sur le poste, mais un Google Doc n'y existe que sous forme de raccourci `.gdoc` de quelques centaines d'octets : un identifiant, aucun texte. Il faut donc exporter chaque Doc en Markdown côté Google (l'API Drive sait le faire : `text/markdown`) pour que Claude puisse le lire.

## La chaîne

```
Drive partagé des transcriptions   (notes Gemini, ID {{INTEL_DRIVE_ID}})
   │  Apps Script « Transcripts → Markdown », chaque lundi vers 5 h, compte {{INTEL_DRIVE_ACCOUNT}}
   ▼
Mon Drive / Transcripts-md/        (un .md par réunion + _etat.json, visible du seul compte)
   │  Drive pour ordinateur
   ▼
scripts/sync-intel.py              (copie sans IA, rejouable, --dry-run)
   ▼
00-intel/inbox/  →  interne/ · clients/<org>/ · prospects/<org>/ · partenaires/<org>/   (hors Git)
```

| Pièce | Où | Rôle |
|---|---|---|
| `apps-script/Code.gs` | script.google.com (copie de référence ici) | Exporte en Markdown les Docs nouveaux ou modifiés, écarte les réunions sensibles et les notes Gemini vides |
| `scripts/sync-intel.py` | cockpit | Copie les nouveaux exports dans `00-intel/inbox/`, retient ce qui est déjà importé dans `00-intel/.sync-state.json`, contrôle la santé de la chaîne |
| `routine-intel-hebdo.md` | tâche `intel-hebdo`, lundi 7 h | Synchro, classement avec synthèse (faits urgents marqués pour le radar), email seulement si la synchro est bloquée |
| `routine-radar-com.md` | tâche `radar-com`, lundi 8 h 30 | Urgents en tête, sujets de communication de la semaine, brief newsletter le premier lundi du mois |
| `taches-planifiees.md` | — | Texte des deux tâches planifiées, prêt à coller |

## Seules les nouveautés circulent

- **Historique** : le tout premier passage de l'Apps Script exporte les réunions des 30 derniers jours, de quoi nourrir le premier brief newsletter. Rien d'antérieur n'est jamais exporté, même si une vieille note est retouchée.
- **Côté Google** : chaque passage ne lit que les Docs créés ou modifiés depuis le passage précédent (repère `WATERMARK`). Le Drive partagé n'est jamais relu en entier ; un passage coupé par la limite de 6 minutes reprend 10 minutes plus tard.
- **Côté poste** : `sync-intel.py` reconnaît à son nom un fichier déjà importé (ou déjà écarté) et ne l'ouvre pas ; Drive pour ordinateur ne le retélécharge donc pas.
- **Côté routines** : le classement ne porte que sur l'inbox ; le radar ne lit que les synthèses de la semaine (30 jours le premier lundi du mois). Dans un export, la transcription intégrale pèse souvent 90 % du fichier : on lit les notes et on ne cherche dans la transcription que pour vérifier un fait.

## Ce qui ne sort jamais du Drive partagé

Filtre sur le titre de la réunion, appliqué par l'Apps Script (`CONFIG.EXCLUDE`) et rejoué par `sync-intel.py` (`EXCLUSIONS`) :

- entretiens de candidats : `entrevue`, `candidat`, `interview`, `entretien d'embauche` (« entretien de cadrage » n'est pas visé) ;
- comptabilité et finance : `accounting`, `comptab…`, `compta`, `finance`.

Ajoutez vos propres motifs dans les deux fichiers, par exemple le nom de votre page de prise de rendez-vous avec les candidats. Une réunion sensible dont le titre ne dit rien est repérée au classement (voir `routine-intel-hebdo.md`) ; les réunions limites sont classées avec `sensible: finance` ou `sensible: rh` et ne fournissent jamais de sujet publiable.

## Notes Gemini vides

Quand une réunion se tient dans une autre langue que celle réglée sur Meet, Gemini crée une note vide (« A summary wasn't produced… », quelques secondes de transcription) puis la vraie note dans l'autre langue ; les deux portent les suffixes « (English) » et « (French) ». La langue ne dit donc rien de la valeur : c'est le contenu qui tranche. Une note qui annonce l'absence de résumé et pèse moins de 8 000 caractères est écartée (`CONFIG.EMPTY_NOTE`, `NOTE_VIDE`), et l'Apps Script met à la corbeille l'export vide qu'il aurait produit lors d'un passage antérieur. Ne triez jamais les notes par langue : selon les équipes, la moitié des exports peut être vide.

## Installation (une fois, environ 5 minutes)

1. Ouvrir https://script.google.com connecté avec le compte qui a accès au Drive partagé ({{INTEL_DRIVE_ACCOUNT}}), puis **Nouveau projet**. Le renommer « Transcripts → Markdown ».
2. Coller le contenu de `apps-script/Code.gs` dans `Code.gs` et remplacer `{{INTEL_DRIVE_ID}}` par l'ID du Drive partagé (dans l'URL du Drive partagé, ou dans les métadonnées du dossier monté). Enregistrer (⌘S). Aucun déploiement n'est nécessaire : le déclencheur exécute la dernière version enregistrée.
3. Choisir **`tester`** dans la liste des fonctions, puis **Exécuter**. Autoriser l'accès au Drive avec le même compte. Le journal affiche le début de la note la plus récente et un fichier `_test.md` apparaît dans Mon Drive → `Transcripts-md`.
4. Choisir **`installer`** puis **Exécuter** : le déclencheur du lundi est créé et le premier passage exporte les 30 derniers jours.
5. Vérifier le fuseau horaire : il est recopié dans `Transcripts-md/_etat.json` (`fuseau`) et doit être celui du poste qui fait tourner les routines, pour que l'export de 5 h précède la routine de 7 h (Paramètres du projet sinon).
6. Sur le poste : installer Drive pour ordinateur avec le même compte, puis ajouter au `.env` du cockpit `INTEL_DRIVE_MD_DIR=<chemin du dossier Transcripts-md monté>` (sur macOS : `~/Library/CloudStorage/GoogleDrive-<compte>/Mon Drive/Transcripts-md`). Vérifier avec `python3 scripts/sync-intel.py --dry-run`.
7. Vérifier qu'aucun placeholder ne reste dans ce dossier : `python3 scripts/lint-placeholders.py --paths _integrations/drive-transcripts` ne doit plus lister que les trois marqueurs d'installation (`INTEL_DRIVE_ID` dans le Code.gs de référence, `INTEL_DRIVE_ACCOUNT`, `INTEL_REPORT_EMAIL`) ; remplacer ces deux derniers et les placeholders de marque restants.
8. Créer les deux tâches planifiées avec le texte de `taches-planifiees.md`, puis lancer une fois `intel-hebdo` à la main pour pré-approuver ses outils.

## Le lundi

Export Google vers 5 h, `intel-hebdo` à 7 h (synchro et classement), `radar-com` à 8 h 30 (urgents en tête, sujets, brief newsletter le premier lundi du mois). Les routines locales tournent quand le poste est allumé et l'application ouverte ; une routine manquée s'exécute au lancement suivant.

## Dépannage

| Symptôme | Cause probable | Remède |
|---|---|---|
| `alerte=source-introuvable` | `INTEL_DRIVE_MD_DIR` absent, Drive pour ordinateur arrêté ou compte déconnecté | Renseigner le `.env`, relancer Drive pour ordinateur, vérifier le compte |
| `alerte=etat-apps-script-absent` | Apps Script pas encore installé | Suivre l'installation |
| `alerte=apps-script-silencieux` | Aucun export depuis 8 jours : déclencheur supprimé ou autorisation révoquée | script.google.com → Exécutions, puis relancer `installer` |
| `alerte=erreurs-export` | Un Doc n'a pas pu être exporté (droits, taille) | Le titre est dans le bilan ; corriger, puis lancer `reinitialiser` et `synchroniser` |
| Une réunion classée a été modifiée sur le Drive | L'export est réécrit, mais `sync-intel.py` ne réimporte pas un `doc_id` déjà vu | Ouvrir le lien du Doc depuis le frontmatter |
| Les dates de réunion manquent dans les noms | Google écrit les dates des titres « 2026/09/30 », Drive pour ordinateur les affiche « 2026 09 30 » | Les deux formats sont gérés ; vérifier qu'un nouveau format de titre n'est pas apparu |

Repartir des 30 derniers jours (après un changement de format ou de filtre) : lancer `reinitialiser` puis `synchroniser`. Les fichiers sont réécrits, pas dupliqués, et rien de déjà importé ne revient dans `00-intel/`.
