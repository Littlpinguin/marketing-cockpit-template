# Bibliothèques de templates n8n (5 100+ workflows)

Trois bibliothèques de workflows n8n réels, à cloner **localement** dans `10-automatisations/libraries/` (gitignoré — on ne redistribue pas 5 000 fichiers dans ce template). Elles sont le carburant de la **phase conseil** de la méthode (`conventions.md`) : avant de construire quoi que ce soit, on cherche comment d'autres ont résolu le même problème.

> **Règle de la méthode : templates d'abord.** Toujours chercher dans ces bibliothèques avant de construire from scratch. Un pattern éprouvé (nodes, connexions, error handling, prompts) vaut mieux qu'une architecture inventée.

---

## Vue d'ensemble

| Bibliothèque | Workflows | Focus | Licence constatée | Source |
|---|---|---|---|---|
| **awesome-n8n-templates** | ~288 | Templates curatés, ~19 catégories | CC-BY-4.0 | [enescingoz/awesome-n8n-templates](https://github.com/enescingoz/awesome-n8n-templates) |
| **n8n-workflow-templates** | ~2 053 | Couverture large, 365 intégrations | **Aucune licence publiée** | [Danitilahun/n8n-workflow-templates](https://github.com/Danitilahun/n8n-workflow-templates) |
| **ultimate-n8n-ai-workflows** | ~2 772 | AI/RAG/agents, multi-LLM | MIT | [oxbshw/ultimate-n8n-ai-workflows](https://github.com/oxbshw/ultimate-n8n-ai-workflows) |

**Note licences** (vérifiées le 2026-07) :

- **CC-BY-4.0** (awesome-n8n-templates) : réutilisation libre avec attribution — citez le repo si vous republiez un template dérivé.
- **Aucune licence** (n8n-workflow-templates) : sans licence explicite, le droit d'auteur par défaut s'applique. Usage recommandé : **consultation et inspiration locales uniquement** — ne pas redistribuer les fichiers, ne pas les committer dans votre fork.
- **MIT** (ultimate-n8n-ai-workflows) : réutilisation très permissive avec mention de la licence. Ce repo évolue rapidement (il s'est étendu en « Open Workflow Library » avec outillage de validation) — les volumes exacts varient selon la date du clone.

## Installation (clone local)

```bash
cd 10-automatisations
mkdir -p libraries && cd libraries

git clone --depth 1 https://github.com/enescingoz/awesome-n8n-templates.git
git clone --depth 1 https://github.com/Danitilahun/n8n-workflow-templates.git
git clone --depth 1 https://github.com/oxbshw/ultimate-n8n-ai-workflows.git
```

Le dossier `10-automatisations/libraries/` est dans le `.gitignore` racine : les clones restent locaux, rien n'est committé. Pour mettre à jour : `git -C libraries/<repo> pull`.

---

## Rôle de chaque bibliothèque dans la méthode

### awesome-n8n-templates — le point d'entrée « métier »

Templates curatés et organisés par catégorie d'usage. À consulter en premier pour un **pattern métier complet** (onboarding, CRM, reporting, support).

| Catégorie | Contenu typique |
|---|---|
| `AI_Research_RAG_and_Data_Analysis` | RAG, deep research, scraping + IA |
| `OpenAI_and_LLMs` | Agents IA, chatbots, voice AI, assistants |
| `Gmail_and_Email_Automation` | Automatisation email, triage, réponses IA |
| `Google_Drive_and_Google_Sheets` | Sync, reporting, data pipelines Google |
| `Slack` / `Discord` / `Telegram` / `WhatsApp` | Bots, notifications, messaging |
| `Notion` / `Airtable` | CRM, project management, bases de données |
| `PDF_and_Document_Processing` | Extraction, OCR, transformation documents |
| `HR_and_Recruitment` | Screening CV, onboarding, évaluation candidats |
| `Instagram_Twitter_Social_Media` | Social media, content creation |
| `WordPress` | Publication, SEO, content management |
| `Database_and_Storage` | Postgres, MongoDB, sync de données |
| `Forms_and_Surveys` | Typeform, Tally, formulaires |
| `devops` | CI/CD, monitoring, infrastructure |
| `Other_Integrations_and_Use_Cases` | Intégrations diverses |

### n8n-workflow-templates — la couverture d'intégrations

Fichiers JSON plats dans `workflows/`, nommés par convention `{id}_{Nodes}_{Action}_{TriggerType}.json`. Couvre 365 intégrations (Telegram, Stripe, HubSpot, Slack, Google Sheets...). À consulter pour une **intégration spécifique** : comment tel node se configure en conditions réelles.

### ultimate-n8n-ai-workflows — le spécialiste AI

- `workflows/` : workflows généraux
- `automation/` : workflows dans des sous-dossiers thématiques (SEO, scraping, agents...)
- Dossiers projet avec workflows + docs d'architecture
- `docs/` : documentation architecturale (utile pour comprendre les patterns AI avancés)

À consulter pour tout ce qui est **AI / RAG / agents / multi-LLM**.

---

## Quand et comment consulter les templates

### Phase conseil (avant plan)

- Chercher des templates similaires avec `Glob` et `Grep` dans les 3 bibliothèques
- Lire les templates pertinents pour en extraire : architecture (nodes + connexions), patterns, bonnes pratiques
- Présenter 2-3 approches alternatives inspirées des templates existants
- Challenger le besoin : « Ce template fait X de cette façon, as-tu envisagé Y ? »

### Phase plan

- Référencer les templates qui ont inspiré l'architecture retenue
- S'inspirer des configurations de nodes éprouvées (paramètres, expressions, error handling)
- Identifier les patterns récurrents dans les templates similaires

### Recherche dans les templates

```
# Chercher par nom de fichier (cas d'usage) — dans les 3 repos
Glob: libraries/awesome-n8n-templates/**/*slack*.json
Glob: libraries/n8n-workflow-templates/workflows/*Slack*.json
Glob: libraries/ultimate-n8n-ai-workflows/**/*agent*.json

# Chercher par contenu (node types, patterns)
Grep: "scheduleTrigger" dans libraries/awesome-n8n-templates/
Grep: "lmChatOpenAi" dans libraries/ultimate-n8n-ai-workflows/
Grep: "httpRequest" dans libraries/n8n-workflow-templates/workflows/
```

### Stratégie de recherche par besoin

- **Intégration spécifique** (Slack, Gmail, Sheets) → `n8n-workflow-templates` (365 intégrations) puis `awesome-n8n-templates`
- **AI / RAG / agents** → `ultimate-n8n-ai-workflows` (focus AI) puis `awesome-n8n-templates` (catégorie AI)
- **Pattern métier complet** (onboarding, CRM, reporting) → `awesome-n8n-templates` (curatés par catégorie)

### Lecture d'un template

- Les templates sont des fichiers JSON contenant la définition complète du workflow n8n
- Se concentrer sur : la liste des nodes, les connexions, les paramètres clés, les prompts IA
- **Ne pas copier les templates tels quels** — s'en inspirer pour concevoir un workflow adapté au besoin spécifique, conforme à `conventions.md` (et respecter la licence du repo source, voir tableau ci-dessus)
