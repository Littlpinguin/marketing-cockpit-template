# Marketing Copilot Template

> 🇬🇧 [Read in English](README.md)

> Un scaffolding opinionné et organisé par rôle pour transformer Claude Code en copilot marketing complet. Mémoire sémantique, hooks de validation de marque, intégrations tool-agnostic. Bootstrap en 30 minutes pour n'importe quelle entreprise.

**Modèle recommandé** : Claude Opus 4.6. Le système est conçu pour tirer parti du raisonnement long-contexte et de la planification stratégique d'Opus. Les modèles plus petits fonctionnent mais avec une dégradation notable sur les tâches de stratégie éditoriale, brand-check et relecture.

---

## Ce que c'est

Un scaffolding complet et opinionné pour transformer Claude Code en un copilot marketing full-stack pour ton entreprise. Il part du principe que :

- Tu as une marque (voix, valeurs, personas, preuves) qui mérite d'être appliquée de façon cohérente
- Tu publies du contenu sur plusieurs canaux (LinkedIn, newsletters, blog, événements, web)
- Tu veux des agents IA qui apprennent de ton contenu passé, pas qui inventent à chaque fois
- Tu veux une conformité de marque déterministe, pas un "je vais essayer de me souvenir des règles"

Le template fournit :

- **9 dossiers de rôle** organisés comme une équipe marketing : `01-brand/`, `02-strategy/`, `03-social-media/`, `04-email/`, `05-web-content/`, `06-graphic-design/`, `07-events/`, `08-mail-signatures/`, `09-blog-seo/`. Chaque dossier a un `CLAUDE.md` qui apprend à Claude Code comment opérer dans ce rôle.
- **9 skills** (dans `.agents/skills/`) qui encodent les bonnes pratiques marketing adaptées à ta marque : `brand-check`, `social-content`, `email`, `copywriting`, `copy-editing`, `content-strategy`, `seo`, `event-marketing`, et `image-generation` (visuels brand-compliant via Gemini nano-banana-pro).
- **Une mémoire sémantique basée sur Qdrant** (`_integrations/qdrant/`) qui ingère tout ce que tu publies et toute ta doctrine de marque, pour que chaque agent puisse demander "est-ce qu'on a déjà dit ça ?" et "que dit la doctrine sur X ?" en 500 ms.
- **Génération d'images conformes à la marque** via Gemini `gemini-3-pro-image-preview` (nano-banana-pro). Chaque prompt est automatiquement préfixé avec ta palette, ta typo, ton style illustratif et tes interdits visuels, pour que chaque image générée respecte la marque sans prompt manuel.
- **Un hook brand-check** qui se déclenche automatiquement après chaque écriture de contenu et bloque la livraison si le draft viole les standards.
- **Un sync hebdomadaire multi-sources** (launchd macOS) qui maintient la mémoire à jour sans que tu y penses.
- **Un bootstrap interview** qui onboard ton entreprise en environ 30 minutes, en partant de l'URL de ton site et de tes documents de marque existants.

## Philosophie

Trois principes guident chaque décision de design :

1. **Brand as truth** — `01-brand/` est la source de vérité. Tous les autres rôles s'y réfèrent. Toute contradiction est signalée avant publication, pas après.
2. **Retrieval-first** — Chaque acte créatif est précédé d'une recherche sémantique : "est-ce que ça a déjà été dit ?", "quelle est la formulation canonique ?", "quels chiffres sont validés par la doctrine ?" Pas d'invention sans vérification.
3. **Hook-enforced** — C'est le harness qui impose le workflow, pas la volonté de Claude. Un hook PostToolUse déclenche le brand check chaque fois que du contenu est écrit dans un dossier de production. Le système est déterministe, pas optimiste.

## Pour qui c'est fait

**Bon fit** :
- Entreprises SaaS avec une voix de marque claire et plusieurs canaux de contenu
- Agences qui publient pour elles-mêmes (pas directement pour leurs clients)
- Collectifs et groupes de freelances qui ont besoin de cohérence sans un éditeur à temps plein
- Cabinets avec des données propriétaires (benchmarks, reports, cas clients) à mettre en avant
- Toute équipe qui publie 5+ pièces de contenu par semaine sur 2+ canaux

**Mauvais fit** :
- B2C grand public sans doctrine forte (chaque pièce est un one-off)
- Publisher mono-canal (juste LinkedIn, juste un blog) qui n'a pas besoin de coordination cross-canal
- Équipes qui n'ont pas encore de guidelines de marque (commence par les construire, reviens après)

## Architecture en un coup d'œil

```
ton-copilot/
├── CLAUDE.md                         # Orchestrateur + détection bootstrap
├── 01-brand/                         # Source de vérité (charte, personas, messaging)
├── 02-strategy/                      # Planification éditoriale, piliers, KPIs
├── 03-social-media/                  # LinkedIn, Discord, WhatsApp
├── 04-email/                         # Newsletters, promos, sales outreach, nurturing
├── 05-web-content/                   # Landing pages, artefacts HTML
├── 06-graphic-design/                # Création visuelle, briefs, prompts IA
├── 07-events/                        # Plans de communication événementielle
├── 08-mail-signatures/               # Signatures HTML par membre
├── 09-blog-seo/                      # SEO long format
├── .agents/skills/                   # 9 skills par rôle
├── .claude/hooks/                    # brand-check-reminder.py
├── _integrations/qdrant/             # Pipeline de mémoire sémantique
│   ├── sync.py                       # CLI (sync, query, verify, stats)
│   ├── mcp_server.py                 # Serveur MCP (Gemini + Qdrant)
│   ├── config.yaml                   # Sources, enrichers, mapping fonctionnalités
│   ├── runbook.md                    # Documentation complète du workflow
│   └── cron/                         # Job launchd hebdomadaire avec drift detection
├── _sources/                         # Inputs bruts (transcripts, reports, veille)
└── _bootstrap/                       # Interview et templates (une fois au setup)
```

## Démarrage rapide

### 1. Prérequis

- [Claude Code](https://claude.com/claude-code) installé
- macOS (pour le cron launchd — utilisateurs Linux/WSL : adaptation en systemd ou cron)
- Python 3.11+
- Un compte [Qdrant Cloud](https://cloud.qdrant.io) (free tier = 1 Go, suffisant)
- Une clé [Google AI Studio](https://aistudio.google.com/apikey) pour Gemini

### 2. Clone et installation

```bash
git clone https://github.com/YOUR_USERNAME/marketing-copilot-template.git ton-copilot
cd ton-copilot

pip install qdrant-client google-genai python-dotenv pyyaml requests mcp
```

### 3. Ouvrir dans Claude Code

```bash
claude .
```

Claude détecte que `.setup-completed` n'existe pas et démarre automatiquement le bootstrap interview (voir `_bootstrap/interview.md`). L'interview te guide à travers :

- **Phase 0 — Discovery** : Claude analyse ton site et les documents de marque que tu dépose dans `_bootstrap/inputs/` (vision, mission, brand guide, pitch deck, exemples de contenu)
- **Phase 1 — Validation de l'identité** : Claude présente ce qu'il a compris et tu corriges ce qui est faux
- **Phase 2 — Personas** : 2 à 4 personas construits collaborativement
- **Phase 3 — Fonctionnalités** : tu choisis quelles fonctionnalités activer (calendrier éditorial, email marketing, knowledge base, événements, CRM) et quel outil backe chacune. Le système est **tool-agnostic** — tu peux brancher Notion, Airtable, MailerLite, Mailchimp, Outline, Confluence, ou un connecteur custom.
- **Phase 4 — Personnalisation des skills** : tu ajustes les 9 skills à ta voix

À la fin de l'interview, Claude :
- Écrit tes réponses dans les fichiers CLAUDE.md et skills appropriés
- Initialise la collection Qdrant (si tu l'as activée)
- Lance une ingestion initiale de tes documents de marque
- Crée le marqueur `.setup-completed`

Durée estimée : 20 à 40 minutes selon la quantité de matériel existant.

### 4. Commencer à opérer

Ouvre Claude Code et demande ce que tu veux :

```
> Rédige un post LinkedIn sur [sujet]
> Prépare la newsletter de [mois]
> Crée une landing page pour [produit]
> Plan de com complet pour [événement]
> Que dit notre doctrine sur [sujet] ?
```

Chaque requête déclenche le rôle pertinent qui consulte Qdrant pour le contenu passé et la doctrine de marque, rédige la pièce, lance le brand-check et livre.

## Features en détail

### Mémoire sémantique (Qdrant + Gemini)

Chaque pièce de contenu que tu publies, chaque transcription de réunion, chaque page de ta doctrine de marque, et chaque article de ta knowledge base est indexé avec `gemini-embedding-001` de Google (3072 dimensions natives) et stocké dans Qdrant. À la requête, le serveur MCP expose 3 outils à Claude :

- `qdrant_search(query, top, filters)` — recherche sémantique avec filtres optionnels (type, source, canal)
- `qdrant_find_similar(text, threshold, exclude_source_file)` — anti-répétition avant publication
- `qdrant_stats()` — stats de la collection et santé du registry

Chaque document est enrichi à l'ingestion avec :
- Un résumé en 2 phrases (Gemini 2.5 Flash)
- Une liste plate d'entités (clients, personnes, outils, chiffres, lieux)
- 3 à 5 claims factuels
- Un content hash (SHA-256) pour la déduplication
- Pour les réunions : décisions et action items extraits du transcript

### Hook brand-check

Chaque fois que Claude écrit ou édite un fichier Markdown ou HTML dans `03-social-media/`, `04-email/`, `05-web-content/`, `07-events/` ou `09-blog-seo/`, un hook `PostToolUse` injecte un system reminder qui force Claude à invoquer le skill `brand-check` avant de livrer. Le skill applique un filtre en 5 points (vocabulaire, ton, preuve, audience, visuel) et une vérification d'anti-répétition Qdrant. Verdicts : ✅ PASS / 🟠 FIX / 🔴 BLOCK. Aucun draft ne sort sans passer.

### Sync incrémental

`sync.py` est idempotent. Le lancer deux fois de suite ne change rien la seconde fois, parce qu'un `registry.json` local suit les content hashes et les point IDs supprimés. Sur un changement de contenu, les anciens chunks sont supprimés chirurgicalement avant réinsertion. Aucune dérive entre Qdrant et la source locale.

Automatisation hebdomadaire via launchd macOS (`cron/run-weekly-sync.sh`) couvre toutes les sources. Un audit `--verify` de dérive tourne après chaque sync ; une notification macOS s'affiche en cas de drift détecté.

### Génération d'images brand-compliant

Le skill `image-generation` wrap `gemini-3-pro-image-preview` de Google (alias nano-banana-pro) avec tes guidelines de marque injectées automatiquement. Tu décris ce dont tu as besoin en langage naturel — "une hero image pour notre landing page sur le SEO" — et le skill :

1. Lit `01-brand/style-guide.md` pour extraire ta palette, ta typo, ton style illustratif et tes interdits visuels
2. Préfixe ton prompt avec ces contraintes de façon structurée que Gemini respecte
3. Génère l'image et la sauvegarde dans `06-graphic-design/outputs/` avec un sidecar metadata qui note le prompt utilisé
4. Signale les violations visibles de ton style guide pour revue

Utilise la même clé `GOOGLE_AI_API_KEY` que les embeddings et l'enrichissement — une clé, trois capacités. L'activation est automatique si la clé est présente.

### Fonctionnalités tool-agnostic

Le `config.yaml` décrit ton stack par fonctionnalité, pas par outil :

```yaml
functionalities:
  editorial_calendar:
    tool: notion              # ou airtable, trello, google-sheets, custom, none
    enabled: true
  email_marketing:
    tool: mailerlite          # ou mailchimp, convertkit, brevo, resend, custom, none
    enabled: true
  knowledge_base:
    tool: outline             # ou notion, confluence, gitbook, custom, none
    enabled: false
```

Changer d'outil = changer une ligne. Les connecteurs built-in couvrent les outils les plus courants ; pour tout le reste, un stub "custom" est généré avec des commentaires TODO pour implémenter ton propre connecteur en moins d'une heure.

## Qdrant est-il obligatoire ?

**Techniquement non, pratiquement oui.** Le système fonctionne sans Qdrant — les skills tombent en fallback sur la lecture de fichiers directement — mais tu perds ~80 % de la valeur :

- Pas d'anti-répétition (les agents vont joyeusement écrire le même post LinkedIn deux fois)
- Pas de cohérence cross-canal (un claim dans un article de blog peut contredire la newsletter du mois dernier)
- Pas d'accès rapide à ta doctrine (chaque agent doit relire `01-brand/` à chaque session)
- Pas de remontée meeting-to-content (les transcripts restent invisibles)

Tu peux lancer le bootstrap sans Qdrant, opérer quelques semaines pour voir si le reste te convient, puis activer Qdrant plus tard via `_integrations/qdrant/init_collection.py`. L'activation prend environ 5 minutes une fois que tu as une URL de cluster et une API key.

## Contribuer

Les PRs sont bienvenues. Ce template est destiné à évoluer. Zones d'intérêt :
- Nouveaux connecteurs de sources (Airtable, Confluence, GitBook, ClickUp, ...)
- Nouveaux enrichers (sentiment, tonality match, classifier de pilier)
- Équivalents cron Linux/WSL (systemd timers)
- Plus de skills (newsletter PR, builder de cas client, ghostwriter de report)
- Traductions de l'interview bootstrap dans d'autres langues

## Credits

Inspiré du setup réel d'un collectif de consulting en transformation digitale qui avait besoin d'un copilot marketing pour maintenir 100+ membres et 8 canaux de marque alignés. L'implémentation originale est privée ; ce template est la version distillée, anonymisée et publiable.

## License

MIT. Voir [LICENSE](LICENSE).
