# workflows/examples/ — mode d'emploi des workflows de référence

4 workflows n8n génériques, **sanitisés** (aucun credential, email, ID de compte ni URL d'instance). Ils sont importables tels quels dans n8n, mais **ne fonctionneront qu'après remplacement des placeholders et re-création des credentials dans le vault n8n**. Vos propres workflows en production se versionnent dans le dossier parent `workflows/` (voir `../README.md`).

## Placeholders à remplacer avant import

Faites un rechercher/remplacer dans chaque JSON (ou éditez les nodes après import) :

| Placeholder | Signification | Exemple |
|---|---|---|
| `{{NOTIFICATION_EMAIL}}` | Destinataire des alertes et récaps | `equipe-marketing@exemple.com` |
| `{{SENDER_EMAIL}}` | Expéditeur (doit être autorisé par votre SMTP) | `n8n@exemple.com` |
| `{{ERROR_WORKFLOW_ID}}` | ID du workflow `error-handler` une fois importé (visible dans son URL) | `aB3xY...` |
| `{{N8N_CREDENTIAL_ID_SMTP}}` | Credential SMTP créé dans le vault n8n | — |
| `{{N8N_CREDENTIAL_ID_LLM}}` | Credential API LLM (Google Gemini par défaut) | — |
| `{{N8N_CREDENTIAL_ID_RECHERCHE}}` | Credential API de recherche (Perplexity par défaut, header auth) | — |
| `{{N8N_CREDENTIAL_ID_METRIQUES}}` | Credential de votre source de métriques | — |

**Pour les credentials, le plus simple** : importez le JSON sans toucher aux IDs, puis ouvrez chaque node marqué d'un avertissement et sélectionnez (ou créez) le credential dans l'interface n8n. Les IDs placeholder seront remplacés automatiquement. Les secrets ne transitent ainsi **jamais** par les fichiers.

## Les 4 workflows

### 1. `error-handler.json` — à installer en premier

`Error Trigger → Code (formater email HTML) → Email (alerte)`

Notification détaillée (workflow, node en erreur, message, date, lien d'exécution) pour toute erreur de n'importe quel workflow. Après import : activez-le, notez son ID, et assignez-le comme *Error workflow* dans les settings de **tous** les autres workflows.

### 2. `meeting-transcript-to-intel.json` — le flux qui alimente `00-intel/`

`Webhook → Valider payload → IF → Construire prompt → HTTP LLM → Parser (défensif) → Formater note markdown → Convertir en fichier → Écrire fichier → Notifier → Répondre 200`
(branche invalide → `Répondre 400`)

- **Entrée attendue (POST JSON)** : `{ "transcript": "...", "title": "...", "date": "AAAA-MM-JJ", "participants": ["..."] }`. Le node de validation accepte aussi `transcription`/`text` comme alias. Configurez votre outil de transcription (Google Meet + export, tl;dv, Fireflies, Whisper auto-hébergé...) pour POSTer sur le webhook.
- **Sortie** : une note markdown avec frontmatter (`type`, `classification` interne/client/prospect/veille, `entite`, `statut: a-trier`) écrite dans `/data/intel-drop/` du conteneur n8n.
- **Acheminement vers `00-intel/inbox/`** : `/data/intel-drop` est un volume monté sur le VPS (voir `INSTALL.md`). Synchronisez-le vers le dossier `00-intel/inbox/` de votre clone du repo par le moyen de votre choix : cron `rsync`, Syncthing, ou un petit script git. Variante sans fichier : remplacez les nodes `Convertir en fichier` + `Déposer` par un HTTP Request vers l'API GitHub (`PUT /repos/.../contents/00-intel/inbox/...`) pour committer la note directement.
- **Sécurité** : changez le chemin du webhook (`meeting-transcript-CHANGEZ-MOI`) pour une valeur non devinable.

### 3. `veille-hebdo.json` — veille automatisée du lundi matin

`Cron lundi 8h → Construire requête (thèmes personnalisables) → HTTP recherche (Perplexity) → Préparer scoring → HTTP LLM (scoring) → Parser propositions (score ≥ 7) → Note de veille + Email récap`
(aucune proposition → email dédié)

Personnalisez les constantes `THEMES` et `AUDIENCE` dans le node `Construire requête veille`. L'API de recherche est Perplexity par défaut (`sonar-pro`) ; remplaçable par toute API équivalente en éditant le node HTTP.

### 4. `daily-report.json` — rapport quotidien de métriques

`Cron jours ouvrés 18h → HTTP métriques → Agréger (défensif) → Générer HTML → Email`

Le node `Récupérer métriques` pointe vers une URL placeholder : branchez-y votre source réelle (API analytics, outil emailing, CRM, ou un endpoint exposé par le module `11-reporting/`). Adaptez ensuite le mapping d'indicateurs dans `Agréger indicateurs`. Pour agréger plusieurs sources : dupliquez le node HTTP et fusionnez avec un node `Merge`.

## Conventions communes

Tous ces workflows appliquent `conventions.md` :

- importés **désactivés** (`"active": false`) — activation seulement après test avec des données réalistes ;
- `errorWorkflow` assigné, `retryOnFail` sur les nodes HTTP, `onError: continueRegularOutput` sur les appels externes non critiques ;
- parsing défensif des réponses LLM (`toArray`, `throw` explicites) ;
- aucun secret dans les JSON — vault n8n uniquement ;
- sticky notes de documentation embarquées dans chaque workflow.

## Ré-exporter proprement

Si vous modifiez un workflow et voulez le committer ici : exportez le JSON, puis **re-sanitisez** (remplacez emails, IDs de credentials, IDs de documents et URLs internes par des placeholders `{{...}}`) et vérifiez avec un grep avant commit. Le backup brut (non sanitisé) reste local via `../../scripts/backup-workflows.sh`.
