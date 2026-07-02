# Conventions n8n — référentiel de conception du module

Portage fidèle d'un système de production réel : création de workflows n8n de haute qualité via Claude Code, assisté par le serveur MCP `n8n-mcp`, les skills n8n et une bibliothèque de **5 100+ templates** de référence (voir `bibliotheques.md`). Ces conventions s'appliquent à **tout** workflow créé ou modifié dans le cadre de ce copilot.

---

## Outils disponibles

- **n8n-mcp** : serveur MCP pour interagir directement avec l'instance n8n (CRUD workflows, exécutions, documentation des nodes, validation) — configuration dans `mcp-setup.md`
- **Skills n8n** : si un skillset n8n est installé (patterns, configuration des nodes, validation), l'invoquer avant de concevoir un workflow
- **Bibliothèques de templates** : 3 repos locaux clonés dans `libraries/` (gitignoré) — 5 100+ workflows réels à consulter AVANT de construire (voir `bibliotheques.md`)

**Quand les utiliser :**

- Toujours consulter les patterns n8n (skills) avant de concevoir un workflow
- Utiliser `n8n-mcp` pour créer, lire, modifier et tester les workflows sur l'instance
- Après modification, vérifier l'état du workflow via `n8n-mcp` avant de considérer la tâche terminée
- Consulter les bibliothèques de templates en phase de conseil et de conception

## Méthode de travail — 5 phases

1. **Conseil** : comprendre le besoin, chercher des templates similaires dans les 3 bibliothèques, challenger l'approche avec des alternatives concrètes (« ce template fait X de cette façon, as-tu envisagé Y ? »)
2. **Plan** : explorer le besoin, identifier le pattern adapté, produire un design + plan enrichi par les templates de référence (format : `plans/plan-template.md`)
3. **Validation** : faire valider le plan par l'humain avant toute exécution
4. **Exécution** : implémenter via `n8n-mcp`, tester, vérifier
5. **Capitalisation** : export JSON sanitisé dans `workflows/`, REX (`rex-template.md`), mise à jour du repo

**Ne jamais implémenter directement sans plan validé pour les workflows non triviaux.**

---

## Architecture & design de workflows

### Pattern par défaut

```
Trigger → Validation (input) → Traitement → Sortie → Error Handler
```

- **Trigger** : webhook, cron, event — toujours nommé explicitement
- **Validation** : vérifier la structure et les champs requis de l'input
- **Traitement** : logique métier, appels API, transformations
- **Sortie** : réponse, stockage, notification
- **Error Handler** : workflow-level error trigger, log + notification en cas d'échec (placeholder `{{ERROR_WORKFLOW_ID}}` dans les exports)

### Principes de modularité

- **Sub-workflows** : découper les workflows complexes via `Execute Sub-workflow`. Chaque workflow = une seule responsabilité.
- **Max 4-6 nodes dans le workflow principal** : abstraire le reste en sub-workflows réutilisables.
- **Interfaces claires** : définir des inputs/outputs explicites pour chaque sub-workflow.
- **Contexte non hérité** : les sub-workflows n'héritent pas du contexte du parent. En particulier, **`$env` est interdit dans les Code nodes des sub-workflows** appelés via `executeWorkflow` (erreur `access to env vars denied`, non configurable). Pour les APIs à token, utiliser un HTTP Request avec credential n8n ; si un Code node a besoin d'un secret, le passer en paramètre d'entrée depuis le parent.

### Versioning

- Dupliquer le workflow avant chaque modification significative
- Convention : `Customer-Onboarding_v2`, `Daily-Report_v2.1`
- Exporter les workflows en JSON pour backup et contrôle de version Git (`workflows/` de votre fork privé — voir `workflows/README.md`)

### Discipline Git (branches + tags)

- **Ne JAMAIS commiter directement sur `main`** — toujours créer une branche dédiée
- **Convention de branches** : `feat/nom-du-workflow`, `fix/nom-du-correctif`, `docs/sujet`
- **Workflow Git** :
  1. `git checkout -b feat/nouveau-workflow` avant de commencer
  2. Commiter à chaque étape clé (design, plan, implémentation, REX)
  3. Quand validé : `git checkout main && git merge feat/... && git branch -d feat/...`
- **Tags de version** : créer un tag annoté après chaque mise en production
  - Format : `vX.Y` — ex : `v1.3`, `v2.0`
  - Commande : `git tag -a vX.Y -m "Description de la version"`
  - Pousser : `git push origin --tags`
- **Retour arrière** : `git checkout vX.Y` pour revenir à une version stable

---

## Conventions de nommage

### Workflows

- Format : `[Domaine] - [Action] - [Cible]`
- Exemples : `CRM - Sync - Contacts HubSpot`, `Finance - Alert - Factures impayées`
- Toujours en minuscules pour les tags, majuscules sur les mots du nom

### Nodes

- Nommer chaque node de manière descriptive (jamais le nom par défaut)
- Format : `Verbe + Objet` — ex : `Valider payload`, `Récupérer commandes`, `Envoyer notification Slack`
- Préfixer les nodes d'erreur : `[Erreur] Notifier admin`

### Variables et expressions

- Noms de variables en `camelCase`
- Documenter les expressions complexes avec une sticky note

---

## Gestion des erreurs

### Principes

- **Design for Failure** : toujours supposer que les services externes vont échouer
- **Error Workflow dédié** : créer un workflow avec `Error Trigger` → notification (Slack, Email). L'assigner via *Options → Settings → Error workflow*
- **Retry on Fail** : activer sur tous les nodes HTTP/API susceptibles de timeout

### Pattern Try/Catch avec IF node

1. Activer `continueOnFail: true` (ou `onError`) sur le node risqué
2. Ajouter un node IF après pour vérifier `$json.error`
3. Router les échecs séparément (log, alerte, retry avec paramètres différents)

### Validation des données en amont

- Nodes `IF` pour vérifier les données entrantes AVANT traitement
- Vérifier : format email, dates valides, champs requis non vides
- Rejeter les événements trop anciens (ex : > 5 minutes)
- Détecter les doublons via un mécanisme d'event ID

### Programmation défensive

- **`toArray()` systématique** sur les outputs LLM — un LLM renvoie parfois une string là où on attend un array :

  ```javascript
  const toArray = (v) => Array.isArray(v) ? v : (typeof v === 'string' && v ? [v] : []);
  ```

- **`alwaysOutputData: true`** sur tout node de recherche qui alimente un IF : sinon, 0 résultat = flux bloqué silencieusement.
- **Erreurs explicites** : dans les Code nodes, `throw new Error("Champ 'transcript' manquant dans le payload webhook")` plutôt qu'un échec silencieux ou un output vide.

### Split valid/error streams (Code node)

```javascript
return [
  validRecords.map(r => ({json: r})),
  errors.map(e => ({json: e}))
];
```

---

## Performance & scalabilité

- **Batch processing** : utiliser `Split In Batches` pour traiter par groupes de 50-100 (éviter l'épuisement mémoire)
- **Exécution parallèle** : connecter plusieurs nodes à une même sortie pour les tâches indépendantes
- **Filtres tôt** : placer les conditions et filtres le plus tôt possible dans le flux
- **Webhooks > Polling** : préférer les webhooks aux triggers polling quand possible
- **Ne pas sur-trigger** : aligner la fréquence sur les besoins métier réels

---

## Expressions & données — référence rapide

### Syntaxe de base

| Expression | Description |
|---|---|
| `{{ $json.fieldName }}` | Champ spécifique de l'item courant |
| `{{ $('Node Name').first().json.property }}` | Premier item d'un autre node |
| `{{ $('Node Name').last().json.output }}` | Dernier item d'un autre node |
| `{{ $('Node Name').item.json.value }}` | Item courant dans une boucle |
| `{{ $itemIndex }}` | Index de l'item courant (0-based) |
| `{{ $now.toFormat("yyyy-MM-dd") }}` | Date formatée |
| `{{ $workflow.id }}` / `{{ $execution.id }}` | IDs workflow/exécution |

### Expression vs Code node

- Si la transformation tient en **une ligne sans boucle** → expression
- Si multi-étapes, variables, logique complexe → Code node
- Erreurs courantes : oublier `.json`, ne pas vérifier null, confondre `===` et `==`

---

## Structure JSON des workflows n8n

### Workflow

```json
{
  "nodes": [],          // Array des définitions de nodes
  "connections": {},    // Liens entre les nodes (source → target)
  "active": false,      // Actif ou non
  "settings": {},       // Mode d'exécution, timezone
  "name": "My Workflow"
}
```

### Node

```json
{
  "parameters": { "url": "https://api.example.com", "method": "GET" },
  "name": "GET Users",
  "type": "n8n-nodes-base.httpRequest",
  "typeVersion": 4,
  "position": [250, 300],
  "id": "unique-node-id"
}
```

### Connections

```json
"connections": {
  "Source Node": {
    "main": [[
      { "node": "Target Node", "type": "main", "index": 0 }
    ]]
  }
}
```

### Data entre nodes

Toute donnée entre nodes = array d'items : `[{ "json": { ... }, "binary": {} }]`

---

## AI workflows & LangChain

### Patterns principaux

- **Agent AI** : node `@n8n/n8n-nodes-langchain.agent` + LLM + tools via sub-nodes
- **RAG** : Document → Chunking → Embedding → Vector Store → Query → LLM → Réponse. Top K = 4 par défaut. Batch de 50 pour l'indexation.
- **Multi-Agent** : plusieurs agents qui collaborent, branching/looping selon les outputs AI
- **Human-in-the-Loop** : étapes d'approbation pour actions sensibles, fallback humain si confiance faible

### Bonnes pratiques AI

- Commencer simple, ajouter la complexité itérativement
- **Préférer HTTP Request direct à LangChain pour les prompts longs** (LLM Chain tronque silencieusement)
- `responseMimeType: 'application/json'` (API Google) ou `response_format` (autres fournisseurs) pour forcer le JSON valide
- Séparer `systemInstruction` (rôle + règles) et `contents` (données) ; données d'abord, instructions à la fin
- Descriptions détaillées dans le `responseSchema` pour guider chaque champ
- Instructions positives plutôt que négatives ; fournir le contexte complet, pas seulement des scores ou résumés
- Documenter les prompts et configurations avec des sticky notes

---

## Nodes les plus utilisés — référence rapide

| Node | Type | Usage |
|---|---|---|
| `n8n-nodes-base.webhook` | Trigger | Réception d'événements HTTP |
| `n8n-nodes-base.scheduleTrigger` | Trigger | Exécution planifiée (cron) |
| `n8n-nodes-base.httpRequest` | Action | Appels API HTTP |
| `n8n-nodes-base.code` | Action | JavaScript/Python custom |
| `n8n-nodes-base.set` | Transform | Transformation de données |
| `n8n-nodes-base.if` | Logic | Routage conditionnel |
| `n8n-nodes-base.switch` | Logic | Routage multi-branches |
| `n8n-nodes-base.merge` | Transform | Fusion de données |
| `n8n-nodes-base.splitInBatches` | Transform | Traitement par lots |
| `n8n-nodes-base.executeWorkflowTrigger` | Trigger | Sub-workflows |
| `@n8n/n8n-nodes-langchain.agent` | AI | Agents AI LangChain |

**Convention** : core = `n8n-nodes-base.*`, LangChain = `@n8n/n8n-nodes-langchain.*`

---

## Patterns d'erreurs connus (REX condensé)

Leçons issues de workflows en production réelle. À relire avant de concevoir — chaque erreur ne doit être payée qu'une fois.

| Sujet | Leçon |
|---|---|
| LLM + n8n | Préférer HTTP Request direct à LangChain (troncature silencieuse des longs prompts) |
| Google Drive | Les Google Docs natifs nécessitent `googleFileConversion` à l'export (sinon binaire brut → hallucinations LLM) |
| Google Docs natifs | Pour du formatage : Drive API `files.create` + Docs API `batchUpdate` (pas `createFromText`) |
| Google Drive move | `move` ne renomme pas : le renommage est une opération `update` séparée |
| Gmail batch | `scheduleTrigger` + `Gmail getAll` (pas `gmailTrigger`, qui est incrémental) — sauf si besoin des pièces jointes en binaire, que seul le Gmail Trigger gère |
| Gmail actions | Les nodes Gmail action (addLabels, markAsRead, send) remplacent `$json` — ne pas chaîner, brancher en parallèle depuis le dernier node porteur des données |
| Gmail search | Ne pas combiner critères thread-level (labels) et message-level (`from:`) dans une même requête ; dédupliquer par `threadId` (getAll retourne des messages, pas des threads) |
| Gmail formats | Avec `simple: false`, utiliser les champs racine (`subject`, `from.text`) — jamais `headers.*` (MIME brut encodé) ; les APIs messages vs threads capitalisent différemment (`from` vs `From`) → double fallback |
| IF nodes API | Les IF nodes créés via API sont peu fiables : toujours `typeValidation: "loose"`, toujours 2 entrées dans le tableau `main` (branche FALSE = `[]`), smart parameters `branch="true"/"false"` ; en cas de corruption, `replaceConnections` |
| IF + binaire | `$binary` n'est PAS accessible dans les conditions IF — filtrer en amont (label, requête) |
| Code node | `n8n-nodes-base.code` v2 n'a qu'une sortie — pas de multi-output |
| `executeOnce` | Réservé aux nodes de config hors chemin de données principal (branches parallèles) ; dans une chaîne linéaire, il bloque les items suivants |
| Merge v3 | Plus de merge by position en mode `combine` — connecter les 2 inputs directement au node suivant |
| Outputs IA | Toujours normaliser avec un helper défensif (`toArray()`) |
| Recherches → IF | `alwaysOutputData: true` sur tout node de recherche qui alimente un IF (0 résultat = flux bloqué sinon) |
| Transcriptions | Les transcriptions vocales contiennent des erreurs phonétiques : matching fuzzy (normalisation + score de similarité) pour toute identification basée sur du texte transcrit |
| Accents Sheets | Éviter les accents dans les noms de colonnes Google Sheets (détection d'écarts par n8n) |
| Prompts n8n | Dans le `jsCode`, écrire les doubles accolades littérales via l'échappement unicode `\u007b\u007b` (sinon n8n les interprète comme une expression) |
| Sub-workflows | `$env` interdit dans les Code nodes des sub-workflows — credentials n8n ou paramètre d'entrée |
| Champs requis | Vérifier les champs requis des nodes de sortie (ex : une tâche sans `title`), pas seulement les champs optionnels |

---

## Checklist qualité (avant publish)

### Design
- [ ] Chaque node est nommé explicitement
- [ ] Sticky notes pour documenter la logique non évidente
- [ ] Workflow découpé en sub-workflows si > 6 nodes principaux
- [ ] Description du workflow documentée (surtout si exposé en MCP)

### Fiabilité
- [ ] Error workflow configuré au niveau du workflow
- [ ] Retry policy définie sur les nodes HTTP/API (au moins 1 retry, backoff)
- [ ] `continueOnFail` activé sur les nodes risqués avec routage IF
- [ ] Validation des inputs en entrée du workflow
- [ ] `alwaysOutputData` sur les recherches alimentant un IF
- [ ] Idempotence vérifiée si le workflow peut être rejoué (déduplication, upsert)
- [ ] Timeout configuré sur les nodes HTTP si pertinent

### Performance
- [ ] Batch processing pour les gros volumes (`Split In Batches`)
- [ ] Filtres placés le plus tôt possible dans le flux
- [ ] Pas de transformations de données inutiles

### Sécurité
- [ ] Pas de secrets en dur — uniquement des credentials n8n ou variables d'environnement
- [ ] Audit logging en place si données sensibles

### Déploiement
- [ ] Testé avec des données réelles ou réalistes
- [ ] Workflow versionné (copie de backup avant modification)
- [ ] Workflow désactivé par défaut jusqu'à validation finale
- [ ] REX rédigé après mise en production (`rex-template.md`)

---

## Sécurité

- **Jamais de secrets en clair** : API keys, tokens, mots de passe → toujours via credentials n8n (vault chiffré) ou variables d'environnement
- **Jamais de secrets dans les exports** : les JSON committés ne contiennent que des placeholders `{{...}}` — purger emails, IDs de credentials, IDs de documents, URLs d'instance, et vérifier par grep avant commit
- **Ne pas logger de données sensibles** : masquer les champs sensibles dans les logs
- **Webhooks** : utiliser le mode production avec authentification quand exposé ; chemin non devinable
- **Credentials** : ne jamais exporter ou afficher les credentials via MCP
- **Principe du moindre privilège** : n'accorder que les scopes/permissions nécessaires aux intégrations
- **Contrôle d'accès** : RBAC sur les plans Enterprise (owner, editor, viewer). Séparer dev/staging/production.

---

## Règles critiques MCP & construction

- **Ne JAMAIS modifier les workflows de production directement** : copier → tester → valider → déployer
- **Ne jamais faire confiance aux valeurs par défaut** : toujours configurer explicitement TOUS les paramètres (cause n°1 d'échecs runtime)
- **Validation multi-niveaux** : `validate_node(mode='minimal')` → `validate_node(mode='full')` → `validate_workflow`
- **Templates d'abord** : toujours chercher dans les bibliothèques (`bibliotheques.md`) avant de construire from scratch
- **Préférer les nodes standard au Code node** quand un node natif existe pour l'opération
- **Exporter des backups** avant toute modification de workflow existant (`scripts/backup-workflows.sh`)
