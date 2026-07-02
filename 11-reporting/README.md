# 11-reporting — dashboard de performances client

## Le concept

Un **dashboard HTML statique**, hébergé directement sur le site du client (mutualisé classique, déployé par FTP), protégé par un code d'accès, mis à jour **une fois par mois**. Le client ouvre une URL du type :

```
https://{{COMPANY_DOMAIN}}/espace-client/dashboard/
```

…saisit son code d'accès, et consulte ses performances marketing du mois : trafic, conversions, emailing, social — aux couleurs de sa marque, avec une **analyse rédigée** et des **recommandations concrètes** en bas de page.

Pourquoi ce choix plutôt qu'un outil SaaS de reporting :

- **Zéro abonnement, zéro backend** — un fichier HTML + des snapshots JSON, ça se déploie partout et ça ne casse jamais.
- **Aux couleurs de la marque** — le dashboard utilise les design tokens de `01-brand/style-guide.md`, pas un thème générique.
- **L'analyse humaine au centre** — les chiffres seuls ne disent rien ; chaque mois embarque une section « Analyse du mois » rédigée (via la skill `performance-report`) et des recommandations actionnables.
- **Historique navigable** — navigation mois précédent / mois suivant, chaque mois est un snapshot JSON immuable.

## Architecture du module

```
11-reporting/
├── CLAUDE.md            ← rôle, workflow, gates
├── README.md            ← ce fichier
├── automation.md        ← déclenchement mensuel via n8n (cron → collecte → analyse → déploiement)
├── dashboard/
│   ├── template.html    ← LE dashboard (HTML statique autonome, Chart.js via CDN)
│   ├── data-schema.md   ← schéma du snapshot mensuel data JSON + arborescence
│   └── data/            ← snapshots copiés ici AU DÉPLOIEMENT (source : 02-strategy/performance/)
├── acces/
│   ├── README.md        ← le système de code d'accès (protection légère, assumée comme telle)
│   └── protect.php.example
└── deploy/
    └── README.md        ← déploiement FTP (lftp / curl, credentials en .env)
```

## Le cycle mensuel

1. **Collecte** — début de mois, les données du mois écoulé sont agrégées (GA4, Search Console, Postiz, {{EMAIL_MARKETING_TOOL}}) dans un snapshot `02-strategy/performance/YYYY-MM/data.json`. Manuellement, ou automatiquement via n8n (voir `automation.md`).
2. **Analyse** — la skill `performance-report` lit le snapshot, le compare aux mois précédents, et rédige l'« Analyse du mois » + recommandations (champ `analyse_md` du JSON). Validation humaine obligatoire avant publication.
3. **Publication** — le snapshot validé est copié dans `dashboard/data/YYYY-MM.json`, le mois est ajouté à `dashboard/data/index.json`, et l'ensemble est poussé par FTP dans l'espace client (voir `deploy/README.md`).
4. **Notification** — le client reçoit un email court : « Votre reporting {{MOIS}} est en ligne » avec le lien et rien d'autre (le contenu vit dans le dashboard, pas dans l'email).

## L'« espace client »

L'espace client est **un seul dossier protégé** sur le site du client, qui regroupe tout ce qu'on partage avec lui :

```
espace-client/               ← protégé par code d'accès (voir acces/README.md)
├── index.php                ← page de saisie du code
├── protect.php              ← garde d'accès (jamais commité avec le code en dur)
├── dashboard/               ← ce module
│   ├── index.html           ← template.html renommé au déploiement
│   └── data/                ← index.json + YYYY-MM.json
└── presentations/           ← decks HTML partagés (module 06-graphic-design)
```

Même mécanisme de déploiement pour le dashboard et les présentations : un `lftp mirror` par sous-dossier (voir `deploy/README.md`).

## Prévisualiser en local

Le dashboard charge ses données en `fetch()` : il faut un serveur HTTP local (le `file://` direct ne fonctionne pas).

```bash
cd 11-reporting/dashboard
python3 -m http.server 5180
# → http://localhost:5180/template.html
```

Déposez au moins un snapshot d'exemple dans `data/` et déclarez-le dans `data/index.json` (format dans `dashboard/data-schema.md`).

## Honnêteté sur la protection

Le code d'accès est une **protection légère** : il éloigne les curieux et les moteurs de recherche, il ne résiste pas à un attaquant déterminé. C'est adapté à du reporting marketing ; ce n'est **pas** adapté à des données sensibles (données personnelles, financières, santé). Détails et limites : `acces/README.md`.

## Skills et modules liés

- `performance-report` (`.claude/skills/performance-report/`) — collecte, comparaison, rédaction de l'analyse mensuelle.
- `10-automatisations/` — les workflows n8n, dont le cron mensuel de reporting (voir `automation.md`).
- `06-graphic-design/presentations/` — les decks partagés dans le même espace client.
- `02-strategy/` — les snapshots source (`performance/YYYY-MM/`) et la lecture stratégique des KPIs.
