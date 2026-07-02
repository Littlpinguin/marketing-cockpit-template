---
name: tools-setup
description: Configure les outils réellement utilisés par l'entreprise (calendrier éditorial, emailing, CRM, événements, base de connaissances, analytics, publication sociale, FTP espace client, génération d'images). Câble les connecteurs, met à jour .env.example, régénère les CLAUDE.md de rôle et le tableau d'état du README. Applique le gate de confidentialité avant tout connecteur touchant des données clients.
---

# /tools-setup — choisir et câbler les outils par catégorie

Charger d'abord la skill `copilot-setup`.

## Intention

Le template est livré agnostique. Cette commande enregistre la stack réelle de l'utilisateur — quel outil précis derrière chaque fonction — et adapte le repo : les `CLAUDE.md` de rôle disent « Notion » au lieu de `{{EDITORIAL_CALENDAR_TOOL}}`, le `.env.example` ne liste que les variables nécessaires, les stubs inutilisés sont retirés.

## Entrées

Aucune au départ. La commande pose chaque question interactivement.

## ⚠️ GATE DE CONFIDENTIALITÉ — à afficher AVANT tout connecteur touchant des données clients

Avant de configurer un connecteur qui expose des **données clients ou personnelles** à Claude — CRM, outil emailing (listes d'abonnés), GA4 / Search Console, transcriptions de meetings (`00-intel/`), scraping de prospects — afficher ce disclaimer **et attendre une réponse explicite** :

> **Confidentialité des données — lisez avant de continuer.**
>
> Ce connecteur fera transiter des données clients par Claude. Le traitement de ces données dépend de votre offre Anthropic :
>
> - **Offres commerciales (Claude Team, Claude Enterprise, API Anthropic)** : vos données ne sont **pas** utilisées pour entraîner les modèles, par défaut et contractuellement.
> - **Plans grand public (Free, Pro, Max)** : l'entraînement sur vos conversations est **activé par défaut (opt-in par défaut)** — vous devez le désactiver explicitement dans vos réglages de confidentialité si vous ne le souhaitez pas.
> - **Résidence des données en Europe** : possible en passant par l'API via **AWS Bedrock** ou **Google Vertex AI** (régions EU).
>
> Références :
> - https://privacy.claude.com/en/articles/7996868-is-my-data-used-for-model-training
> - https://trust.anthropic.com
>
> **Quel plan Claude utilisez-vous pour ce copilot ?** (team / enterprise / api / free / pro / max)

Règles du gate :
1. **Ne pas continuer sans réponse.** La réponse est consignée dans le log wizard (`.setup-completed.wizard_log`).
2. Si la réponse est **free / pro / max** : avertir que les données clients traitées ici peuvent servir à l'entraînement sauf opt-out, recommander soit l'opt-out immédiat, soit une offre commerciale, et demander une **seconde confirmation explicite** avant de configurer le connecteur.
3. Le gate s'affiche **une fois par session de configuration**, pas à chaque connecteur — mais il est ré-affiché si l'utilisateur configure plus tard un nouveau connecteur sensible (réentrée).
4. `/modules` ré-applique ce gate à l'activation des modules `veille`, `acquisition` et `reporting`.

## Flux

### Étape 1 — Charger le registre

Lire `docs/tools.json` (liste canonique des catégories et outils supportés avec le statut du connecteur).

Lire aussi `.setup-completed` s'il existe (scénario de re-run) : préserver les réponses précédentes, ne demander que les manques ou les changements.

Rappel sécurité à afficher :

> Pour chaque outil, je vous demanderai les noms des variables d'environnement et confirmation qu'elles sont renseignées dans `.env`. Je ne lirai jamais la valeur des clés. Si un outil n'a pas encore de connecteur intégré, je vous le dirai et je génèrerai un stub TODO — il faudra l'implémenter avant la première synchro ou le premier push.

**Règle de destination des tokens (à appliquer partout dans ce wizard)** — un token va SOIT :
- dans **`.env`** (local, gitignoré) quand le consommateur est un **script ou connecteur Python** qui le charge via dotenv — ex. MailerLite, Brevo, GA4/GSC, Apify, Postiz, FTP ;
- dans le **`.mcp.json` local non versionné** (gitignoré ; `cp .mcp.json.example .mcp.json` s'il n'existe pas) quand le consommateur est un **serveur MCP** — ex. n8n-mcp, Google Ads, Lemlist en mode clé API. OAuth d'abord quand le serveur le propose (Lemlist, Magnific) : aucun token à stocker.

Jamais dans un fichier tracké. Et ne jamais écrire de références `${VAR}` dans `.mcp.json` en supposant qu'elles seront lues depuis le `.env` du projet : Claude Code ne développe les `${VAR}` de `.mcp.json` que depuis l'environnement du processus (résultat : 401). Détails et hiérarchie complète : `SECURITY.md`.

### Étape 2 — Itérer les catégories

Ordre des catégories :

1. `editorial_calendar` — où le contenu est planifié (par défaut : `02-strategy/calendar/calendar.md`, aucun outil externe requis)
2. `email_marketing` — newsletters, promos ⚠️ gate de confidentialité
3. `knowledge_base` — docs internes, playbooks
4. `events_platform` — webinars, lives
5. `crm` — données leads et clients ⚠️ gate de confidentialité
6. `web_analytics` — **GA4 + Search Console** ⚠️ gate de confidentialité
7. `social_publishing` — **Postiz** (publication sociale, module `publication-sociale`)
8. `scraping` — **Apify** (veille et acquisition)
9. `image_generation` — Gemini + **Magnific** (upscale)
10. `client_space_ftp` — **FTP espace client** (partage de présentations et dashboards)

Pour chaque catégorie, présenter une question structurée (connecteurs prêts / stubs / `none`), attendre la réponse, puis traiter (étape 3).

#### 2a — Connecteurs dédiés v2

**Postiz (publication sociale)**
- Demander : instance cloud (`https://api.postiz.com`) ou self-hosted (URL) ?
- Variables : `POSTIZ_API_KEY`, `POSTIZ_BASE_URL` (self-hosted uniquement).
- Rappeler : le push reste soumis à dry-run + confirmation humaine (`SECURITY.md`), et le statut de l'entrée calendrier passe à `publié` seulement après publication effective.

**Apify (scraping veille / acquisition)**
- Variable : `APIFY_TOKEN`.
- Avertir : respecter les CGU des plateformes scrappées et le RGPD (voir `12-acquisition/CLAUDE.md`). Si les données scrappées incluent des personnes → gate de confidentialité.

**Magnific (upscale / amélioration d'images) — via MCP**
- Installation :
  ```
  claude mcp add --transport http magnific https://mcp.magnific.com
  ```
- Vérifier ensuite que le serveur apparaît dans `claude mcp list` et noter que l'authentification se fait au premier appel (**OAuth** — aucun token statique à stocker, cas idéal de la hiérarchie `SECURITY.md`). Si vous l'ajoutez en scope projet (`--scope project`), l'entrée s'écrit dans le `.mcp.json` local — non versionné, c'est voulu.
- Usage : upscale des visuels produits par `image-generation` avant publication ou impression.

**Google Analytics 4 + Search Console (web analytics)** ⚠️ gate de confidentialité
- Recommandé via MCP officiel ou service account : variables `GA4_PROPERTY_ID`, `GSC_SITE_URL`, `GOOGLE_APPLICATION_CREDENTIALS` (chemin vers le JSON du service account, **jamais committé**).
- Alimente le module `reporting` (`11-reporting/`). Sans ces accès, le module reporting fonctionne en saisie manuelle des chiffres.

#### 2b — Étape FTP (espace client)

Objectif : permettre le partage de présentations HTML et de dashboards protégés par code d'accès sur le site de l'entreprise (module `espace-client`, utilisé par `06-graphic-design/presentations/` et `11-reporting/`).

1. Demander : « Avez-vous un accès FTP/SFTP à votre site pour héberger un espace client ? (oui / non / plus tard) »
2. Si oui, collecter **les noms d'hôte et chemins uniquement** ; le mot de passe va dans `.env`, jamais dans le chat :
   - `FTP_HOST` — hôte (ex. `ftp.{{COMPANY_DOMAIN}}`)
   - `FTP_USER` — utilisateur
   - `FTP_PASSWORD` — **à renseigner par l'utilisateur directement dans `.env` (local, gitignoré, jamais commité)**
   - `FTP_REMOTE_PATH` — chemin distant de l'espace client (ex. `/www/espace-client/`)
3. Ajouter ces variables à `.env.example` (valeurs vides) et demander à l'utilisateur de confirmer qu'il a rempli `.env` de son côté.
4. Test non destructif : lister le répertoire distant (`curl --ssl-reqd ftp://…` ou `lftp -e "ls; bye"`) — jamais d'écriture pendant le setup.
5. Rappeler le principe : l'espace client est protégé par un **code d'accès léger** (voir `11-reporting/acces/`), suffisant pour du partage commercial, insuffisant pour des données sensibles.

### Étape 3 — Traiter le choix

Pour chaque outil choisi :

#### Si `connector_status == "ready"`
1. Confirmer que les variables d'env sont listées dans `.env.example`.
2. Demander l'ID de ressource si pertinent (ex. URL de database Notion → UUID). Ne jamais demander la valeur d'une clé API.
3. Enregistrer l'ID de ressource dans `docs/tools.json` (pas dans `.env` — l'utilisateur remplit `.env` lui-même).
4. Poser les questions spécifiques à l'outil (Notion : « quel label de statut marque un contenu prêt à publier ? »).

#### Si `connector_status == "stub"`
1. Expliquer : « Pas de connecteur intégré pour `<outil>`. Je génère un stub TODO à `_integrations/connectors/<outil>.py`. Vous ou votre développeur l'implémentez avant le premier push. »
2. Confirmation de l'utilisateur.
3. Générer le stub depuis `_templates/connector-stub.py.tpl` (substituer `{{TOOL_NAME}}`, `{{TOOL_CATEGORY}}`, `{{ENV_KEYS_BLOCK}}`, `{{REQUIRED_ENV_KEYS_LIST}}`).
4. Enregistrer les variables d'env attendues dans `.env.example`.

#### Si `none`
1. Désactiver la catégorie dans le registre.
2. Retirer les sections correspondantes des `CLAUDE.md` de rôle à la régénération (étape 5).
3. Ne pas ajouter de variables d'env.

### Étape 4 — Mettre à jour `.env.example`

Après toutes les catégories, réécrire `.env.example` pour n'inclure que :
- Toujours : `GOOGLE_AI_*` (génération d'images)
- Uniquement pour les outils activés : leurs variables (dont `FTP_*`, `POSTIZ_*`, `APIFY_TOKEN`, `GA4_*`/`GSC_*` le cas échéant)

Présenter le diff avant écriture :

> Voici le nouveau `.env.example`. J'écris ? (oui / montrer-seulement / annuler)

### Étape 5 — Régénérer les `CLAUDE.md` de rôle

Pour chaque dossier de rôle du cœur, lire le template `_templates/role-claudemd/<role>.md` et substituer :
- `{{EDITORIAL_CALENDAR_TOOL}}`, `{{EMAIL_MARKETING_TOOL}}`, `{{EVENTS_PLATFORM_TOOL}}`, etc. → l'outil choisi, ou suppression de la ligne si `none`
- `{{COMPANY_NAME}}`, `{{COMPANY_MAIN_CONTACT}}` → valeurs validées par `/brand-discover`
- `{{CONTENT_CADENCE_LINKEDIN}}`, `{{CONTENT_CADENCE_NEWSLETTER}}`, `{{CONTENT_CADENCE_BLOG}}` (template `02-strategy.md`) → cadences décidées à l'entretien stratégie de `/brand-discover` (lisibles dans `02-strategy/channel-strategy.md`) ; si l'entretien n'a pas eu lieu, laisser le placeholder et le signaler
- Blocs conditionnels — conserver ou retirer selon les choix enregistrés
- ⚠️ **Ne pas substituer les placeholders d'exécution** qui décrivent des motifs de nommage utilisés à runtime (ex. `plan-{{MOIS_ANNEE}}.md` dans `02-strategy.md`) — ils doivent rester tels quels dans le `CLAUDE.md` régénéré

La régénération ne touche que les `CLAUDE.md` de rôle — jamais les fichiers de contenu déjà remplis par le wizard (`02-strategy/objectifs.md`, `parcours-client.md`, `kpi-framework.md`, `channel-strategy.md`, fichiers `01-brand/`).

Écrire dans `<role>/CLAUDE.md`, avec sauvegarde préalable dans `.setup-archive/role-claudemd-<ISO8601>/`.

> Je régénère les CLAUDE.md de rôle. Revue fichier par fichier, ou en bloc ? (revue / bloc / annuler)

Les `CLAUDE.md` des **modules** (08, 10, 11, 12) ne sont pas régénérés ici — ils sont gérés par `/modules`.

### Étape 6 — Mettre à jour le tableau d'état du README

Remplacer le contenu entre `<!-- tool-status:start -->` et `<!-- tool-status:end -->` par un tableau à jour construit depuis les choix + `docs/tools.json`. Si les marqueurs n'existent pas encore dans `README.md`, ajouter une section « ## Tool status » en fin de README avec les deux marqueurs, puis la remplir.

### Étape 7 — Log wizard

Ajouter à la structure `.setup-completed` en mémoire :

```json
{ "command": "/tools-setup", "at": "ISO 8601", "tools_selected": { ... }, "privacy_gate": { "acknowledged": true, "claude_plan": "team|enterprise|api|free|pro|max" } }
```

L'écriture réelle du fichier se fait dans `/validate-setup`.

### Étape 8 — Rendre la main

> Outils configurés. Vos CLAUDE.md de rôle référencent vos vrais outils et `.env.example` ne liste que les clés utiles.
>
> Suite :
>   - `/modules` pour activer les modules optionnels (video, automatisations, reporting, acquisition, veille, publication-sociale, espace-client)
>   - `/validate-setup` pour valider et verrouiller le setup
>
> Vous pouvez relancer `/tools-setup` à tout moment pour changer d'outils.

## Modes d'échec à éviter

- **Ne jamais écrire dans `.env`.** Seulement `.env.example`. L'utilisateur remplit `.env` lui-même.
- **Ne jamais écrire un token dans un fichier tracké.** Les tokens des serveurs MCP vont dans le `.mcp.json` local (gitignoré), ceux des scripts dans `.env`. Ne jamais committer ni détracker à l'envers : `git ls-files .mcp.json` doit rester vide.
- **Ne jamais utiliser `${VAR}` dans `.mcp.json`** en croyant lire le `.env` du projet — Claude Code ne fait pas cette interpolation (connexion 401). Valeurs réelles dans le fichier local, ou OAuth quand disponible.
- **Ne jamais sauter le gate de confidentialité** pour un connecteur touchant des données clients, même en re-run.
- **Ne pas écraser un `CLAUDE.md` de rôle sans sauvegarde** dans `.setup-archive/`.
- **Ne pas laisser l'utilisateur choisir un outil « ready » sans confirmer qu'il a les credentials** : sinon avertir que l'outil est configuré mais inutilisable tant que `.env` n'est pas rempli.
- **Ne pas tester le FTP en écriture** pendant le setup — listing seulement.
- **Ne pas supprimer les connecteurs intégrés existants** — seulement ajouter des stubs pour les nouveaux outils.
