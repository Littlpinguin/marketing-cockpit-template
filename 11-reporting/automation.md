# Automatisation du reporting mensuel (n8n)

Le cycle mensuel décrit dans `README.md` s'automatise de bout en bout avec **n8n**, à une exception près, volontaire : la **validation humaine de l'analyse** avant mise en ligne. L'infrastructure n8n (instance, credentials, conventions de nommage des workflows) est décrite dans le module **`10-automatisations/`** — ce fichier ne décrit que le workflow de reporting.

## Vue d'ensemble du workflow

```
┌────────────┐   ┌──────────────────┐   ┌───────────────┐   ┌──────────────────┐
│ Cron       │ → │ Collecte APIs    │ → │ Génération    │ → │ Claude Code      │
│ 1er du mois│   │ GA4 · GSC ·      │   │ data.json     │   │ headless :       │
│ 06:00      │   │ Postiz · emailing│   │ (schéma)      │   │ analyse du mois  │
└────────────┘   └──────────────────┘   └───────────────┘   └────────┬─────────┘
                                                                     │
                 ┌──────────────────┐   ┌───────────────┐   ┌────────▼─────────┐
                 │ Notification     │ ← │ Déploiement   │ ← │ Validation       │
                 │ client (email)   │   │ FTP           │   │ HUMAINE (gate)   │
                 └──────────────────┘   └───────────────┘   └──────────────────┘
```

## Étape par étape

### 1. Déclencheur — Schedule Trigger

- Cron : `0 6 1 * *` (le 1er du mois à 06:00) — le mois M-1 est complet.
- GA4 consolide ses données sous 24-48 h : pour des chiffres stabilisés, préférez `0 6 3 * *` (le 3 du mois) et documentez ce choix dans le workflow.

### 2. Collecte — un nœud HTTP Request par source

| Source | API | Données extraites |
|---|---|---|
| GA4 | Data API v1 (`runReport`) | sessions, utilisateurs, pages vues, événements clés (conversions), top pages |
| Search Console | Search Analytics API | clics, impressions, CTR, position, top requêtes |
| Postiz | API de l'instance ({{POSTIZ_URL}}) | posts publiés, impressions, interactions **par canal** |
| {{EMAIL_MARKETING_TOOL}} | API campagnes | campagnes envoyées, taux d'ouverture, taux de clic, abonnés |

Credentials : stockés dans le credential store n8n (jamais dans les nœuds en clair) — voir `10-automatisations/` pour la convention. Règle racine `SECURITY.md` : vérifier les endpoints dans la doc officielle, ne pas les improviser.

### 3. Génération du snapshot — nœud Code

Un nœud Code (JavaScript) agrège les réponses au format défini dans `dashboard/data-schema.md` : blocs `kpis`, `seo`, `top_pages`, `top_posts`, `social_par_canal`, champs `periode`/`libelle`/`genere_le`/`sources`. Les champs `analyse_md` et `recommandations` restent vides à ce stade.

Écriture : commit du fichier dans le repo client à `02-strategy/performance/YYYY-MM/data.json` (nœud GitHub/Gitea, ou écriture disque si n8n tourne sur la machine qui héberge le repo).

### 4. Analyse — Claude Code headless

Un nœud Execute Command appelle Claude Code en mode non interactif sur le repo client, en invoquant la skill **`performance-report`** (skill dédiée du template — c'est elle qui porte la méthode d'analyse) :

```bash
cd /chemin/vers/repo-client && claude -p \
  "Utilise la skill performance-report pour analyser 02-strategy/performance/2026-06/data.json : \
   compare aux mois précédents, rédige l'analyse du mois et 3 recommandations, \
   et remplis les champs analyse_md et recommandations du snapshot." \
  --allowedTools "Read,Edit,Write,Glob,Grep" \
  --permission-mode acceptEdits
```

La skill lit le snapshot + l'historique, applique la voix de `01-brand/voice.md`, et écrit `analyse_md` + `recommandations` directement dans le `data.json`.

### 5. Gate de validation humaine — obligatoire

Le workflow **s'arrête** ici et notifie le responsable marketing (email ou Slack) avec le snapshot en pièce jointe / lien. Deux implémentations n8n :

- **Wait + webhook de reprise** : le nœud Wait suspend le workflow ; l'email de notification contient le lien de reprise (`$execution.resumeUrl`) à cliquer après relecture.
- **Deux workflows** : le premier s'achève sur la notification ; un second workflow (déclenché manuellement ou par webhook) exécute le déploiement.

Pas de mise en ligne d'une analyse non relue — c'est le pendant automatisé de la règle « brand-check avant livraison ».

### 6. Déploiement — FTP

Après validation : copie du snapshot vers `11-reporting/dashboard/data/YYYY-MM.json`, mise à jour d'`index.json`, puis push FTP (nœud FTP de n8n, ou Execute Command avec le `lftp` de `deploy/README.md`). Credentials FTP dans le store n8n.

### 7. Notification client — email court

Dernier nœud : email au client — objet « Votre reporting {{MOIS}} est en ligne », deux phrases, le lien vers l'espace client. Le code d'accès n'est **jamais** dans cet email (transmis une seule fois, par canal séparé — voir `acces/README.md`).

## Mode dégradé (sans n8n)

Tout le workflow se fait à la main en ~30 min/mois : collecte via les exports des outils → remplir `data.json` selon le schéma → invoquer la skill `performance-report` dans une session Claude Code → relire → déployer (`deploy/README.md`). L'automatisation est un confort, pas un prérequis du module.

## Points de vigilance

- **Idempotence** : relancer le workflow pour un mois déjà publié doit régénérer le même snapshot (mêmes périodes d'API), pas dupliquer le mois dans `index.json`.
- **Échec d'une source** : ne pas publier un snapshot partiel silencieusement — notifier et laisser le bloc absent (le dashboard masque les sections manquantes) avec une note dans `analyse_md`.
- **Coûts et quotas** : GA4 Data API et Search Console sont gratuits dans les quotas usuels ; l'appel Claude Code headless consomme des tokens — une exécution par mois par client reste négligeable.
- Référence générale des workflows, secrets et supervision n8n : **`10-automatisations/`**.
