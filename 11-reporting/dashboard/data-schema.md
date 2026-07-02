# Schéma des snapshots mensuels

Chaque mois de reporting = **un fichier JSON immuable**. Le dashboard (`template.html`) ne connaît que ces fichiers : pas de base de données, pas d'API.

## Arborescence — où vivent les données

Les snapshots ont **une source unique côté repo** et sont **copiés au déploiement** :

```
02-strategy/performance/          ← SOURCE (repo client, versionnée)
├── 2026-05/
│   ├── data.json                 ← le snapshot du mois (schéma ci-dessous)
│   └── notes.md                  ← optionnel : contexte de collecte, anomalies
└── 2026-06/
    └── data.json

11-reporting/dashboard/data/      ← COPIE DE DÉPLOIEMENT (jamais éditée à la main)
├── index.json                    ← liste des mois publiés
├── 2026-05.json                  ← copie de 02-strategy/performance/2026-05/data.json
└── 2026-06.json
```

Règles :

- On **édite** dans `02-strategy/performance/YYYY-MM/data.json` (collecte + analyse).
- On **publie** en copiant vers `dashboard/data/YYYY-MM.json` + mise à jour d'`index.json` (voir `../deploy/README.md`).
- Un mois publié ne se réécrit pas, sauf correction de données assumée (le champ `genere_le` doit alors changer).
- **Jamais de données client réelles dans ce repo template** — uniquement dans le repo du client.

## `index.json` — la liste des mois publiés

```json
{
  "client": "{{COMPANY_NAME}}",
  "mois": ["2026-04", "2026-05", "2026-06"]
}
```

Le dashboard trie les mois et affiche le plus récent par défaut. Ajouter un mois ici suffit à le rendre navigable.

## `YYYY-MM.json` — le snapshot mensuel

Sources par bloc : **GA4** (trafic, conversions, top pages), **Search Console** (SEO), **Postiz** (social, par canal), **{{EMAIL_MARKETING_TOOL}}** (emailing). Tout champ absent est simplement masqué par le dashboard — un client sans emailing a un snapshot sans bloc `emailing`.

```json
{
  "periode": "2026-06",
  "libelle": "Juin 2026",
  "genere_le": "2026-07-01",
  "sources": {
    "ga4": "propriété {{GA4_PROPERTY_ID}}",
    "search_console": "https://{{COMPANY_DOMAIN}}",
    "social": "postiz",
    "emailing": "{{EMAIL_MARKETING_TOOL}}"
  },

  "kpis": {
    "trafic": {
      "sessions": 4820,
      "utilisateurs": 3910,
      "pages_vues": 11240,
      "duree_moyenne_s": 96
    },
    "conversions": {
      "total": 87,
      "taux_pct": 1.8,
      "par_objectif": [
        { "nom": "Demande de démo", "total": 34 },
        { "nom": "Inscription newsletter", "total": 53 }
      ]
    },
    "emailing": {
      "campagnes": 2,
      "emails_envoyes": 3400,
      "taux_ouverture_pct": 42.5,
      "taux_clic_pct": 4.1,
      "desabonnements": 6,
      "nouveaux_abonnes": 118
    },
    "social": {
      "posts_publies": 14,
      "impressions": 68200,
      "interactions": 2140,
      "taux_engagement_pct": 3.1,
      "nouveaux_abonnes": 210
    }
  },

  "seo": {
    "clics": 1240,
    "impressions": 88600,
    "ctr_pct": 1.4,
    "position_moyenne": 14.2,
    "top_requetes": [
      { "requete": "{{EXEMPLE_REQUETE}}", "clics": 140, "impressions": 5200, "position": 4.1 }
    ]
  },

  "top_pages": [
    { "url": "https://{{COMPANY_DOMAIN}}/blog/exemple", "titre": "Titre de la page", "sessions": 640, "conversions": 12 }
  ],

  "top_posts": [
    { "canal": "linkedin", "titre": "Accroche du post…", "date": "2026-06-12",
      "impressions": 12400, "interactions": 420, "url": "https://www.linkedin.com/…" }
  ],

  "social_par_canal": [
    { "canal": "linkedin",  "posts": 8, "impressions": 52000, "interactions": 1800, "abonnes": 3400, "nouveaux_abonnes": 180 },
    { "canal": "instagram", "posts": 6, "impressions": 16200, "interactions": 340,  "abonnes": 1210, "nouveaux_abonnes": 30 }
  ],

  "analyse_md": "## Ce qu'il faut retenir\n\nLe trafic progresse de **12 %**, porté par l'article X…\n\n- Point saillant 1\n- Point saillant 2",
  "recommandations": [
    "Recommandation actionnable n°1 pour le mois prochain.",
    "Recommandation actionnable n°2."
  ]
}
```

> Les valeurs ci-dessus sont **fictives** — elles illustrent le format, rien d'autre.

## Détail des champs

| Champ | Type | Source | Obligatoire | Notes |
|---|---|---|---|---|
| `periode` | `"YYYY-MM"` | — | ✅ | Doit correspondre au nom du fichier |
| `libelle` | string | — | ✅ | Affiché dans le sélecteur (« Juin 2026 ») |
| `genere_le` | `"YYYY-MM-DD"` | — | ✅ | Date de génération du snapshot |
| `sources` | object | — | recommandé | Traçabilité : d'où vient chaque bloc |
| `kpis.trafic` | object | GA4 | ✅ | Sessions, utilisateurs, pages vues, durée moyenne |
| `kpis.conversions` | object | GA4 (événements clés) | ✅ | `par_objectif` détaille chaque événement de conversion |
| `kpis.emailing` | object | {{EMAIL_MARKETING_TOOL}} | si canal actif | Taux en pourcentage (42.5 = 42,5 %) |
| `kpis.social` | object | Postiz (agrégé tous canaux) | si canal actif | `interactions` = réactions + commentaires + partages |
| `seo` | object | Search Console | recommandé | Période = le mois entier |
| `top_pages` | array (≤ 10) | GA4 | recommandé | Triées par sessions décroissantes |
| `top_posts` | array (≤ 10) | Postiz | recommandé | Tous canaux confondus, triés par interactions |
| `social_par_canal` | array | Postiz | recommandé | Un objet par canal actif |
| `analyse_md` | string (markdown) | skill `performance-report` | ✅ | Sous-ensemble markdown : `##`/`###`, `**gras**`, `*italique*`, listes `- ` |
| `recommandations` | array de strings | skill `performance-report` | ✅ | 2 à 4 recommandations actionnables |

## Conventions

- **Pourcentages** : toujours en valeur numérique déjà multipliée (42.5, pas 0.425), suffixe `_pct`.
- **Pas de variation pré-calculée** : le dashboard calcule lui-même les variations N vs N-1 à partir des snapshots — une seule source de vérité par mois.
- **Encodage** : UTF-8, montants et textes en français.
- **Chiffres traçables** : chaque nombre doit pouvoir être retrouvé dans son outil source (règle `02-strategy/` : aucun chiffre sans source).
