---
name: seo
description: Production SEO pour {{COMPANY_NAME}} — briefs de contenu, articles longs, clusters thématiques, optimisation on-page et AEO (citations LLM), dans 09-seo/. L'analyse (audits techniques, SERP, mots-clés, backlinks) est déléguée aux agents du plugin claude-seo. Couplage Google Search Console / GA4 configuré via /tools-setup.
---

# seo — production blog & SEO {{COMPANY_NAME}}

Tu pilotes la stratégie de contenu long-format et sa production, optimisée pour les moteurs de recherche (Google) et les moteurs de réponse (ChatGPT, Claude, Perplexity, Gemini).

## Étape 0 — Doctrine de marque (OBLIGATOIRE)

Avant de rédiger un brief ou un article :

1. Charger `01-brand/checklist-pre-composition.md` — règles de voix, anti-style-IA, typographie, assets, réutilisation.
2. Charger `01-brand/voice.md` — position de voix, vocabulaire, interdits.

**Ne jamais produire sans.** Si l'un des deux fichiers manque ou contient encore des `{{...}}`, arrêter et lancer `/start-copilot`. Les articles SEO sont le format le plus exposé au style IA (règle de trois, méta-commentaire, emphase gonflée) : le filtre anti-style-IA conditionne aussi la citabilité par les LLM.

## Division du travail — analyse vs production

**Cette skill produit. Elle n'audite pas.** L'analyse s'appuie sur le plugin **claude-seo** (AgriciDaniel) et ses agents spécialisés :

| Besoin d'analyse | Déléguer à |
|---|---|
| Audit complet du site, technique (crawl, indexation, CWV) | `claude-seo:seo-audit` / agent `seo-technical` |
| Qualité de contenu, E-E-A-T, contenu mince | agent `seo-content` |
| Clustering sémantique, architecture hub-and-spoke | agent `seo-cluster` |
| Schema markup, données structurées | agent `seo-schema` |
| GEO / AI Overviews / citabilité LLM | agent `seo-geo` |
| Données CrUX, GSC, GA4 | agent `seo-google` |
| Backlinks, pages concurrentes, dérive SEO | agents `seo-backlinks`, `seo-competitor-pages`, `seo-drift` |

Workflow type : lancer l'analyse via le plugin → récupérer les conclusions (mots-clés, intentions, gaps, structure recommandée) → **produire** ici (briefs, articles, clusters) dans `09-seo/`.

## Données de performance — GSC / GA4

Le couplage **Google Search Console + GA4** se configure via `/tools-setup`. Une fois actif :

- Prioriser les sujets d'après les requêtes réelles (impressions sans clic = opportunité de brief).
- Alimenter le cycle de refresh (article > 6 mois avec positions en baisse → mise à jour prioritaire).
- Vérifier l'indexation des articles publiés.

Si le couplage n'est pas configuré, le signaler à l'utilisateur et travailler à partir des clusters et des personas.

## Préflight production (après l'étape 0)

1. Lire `09-seo/CLAUDE.md` — workflow complet, clusters, frontmatter.
2. Lire `01-brand/messaging-framework.md` — chiffres et affirmations utilisables.
3. **Anti-répétition** : scanner `09-seo/articles/` pour recouvrement de sujet, consulter `_templates/inventory.md`, et vérifier les positions déjà établies dans `01-brand/messaging-framework.md`.
4. **Règle critique** : chaque affirmation factuelle de l'article est adossée à un chiffre de la doctrine ou à une source externe citée. Les moteurs (classiques et LLM) pénalisent le contenu non sourcé.

## Clusters thématiques

{{SEO_CLUSTERS}}

## Workflow de production en 7 étapes

### 1. Recherche de mots-clés (via plugin)

- Identifier le cluster cible.
- Déléguer la collecte (volumes, difficulté, SERP top 5, questions des personas) aux agents claude-seo.
- Consigner dans `09-seo/keyword-research/<cluster>/YYYY-MM-<sujet>.md`.

### 2. Brief de contenu

Fichier `09-seo/content-briefs/brief-<slug>.md` avec :
- Mot-clé principal + secondaires (3-5)
- Intention de recherche (informationnelle / commerciale / transactionnelle)
- Structure proposée (H1, H2, H3)
- Sources à intégrer (doctrine, données externes, conclusions d'agents claude-seo)
- CTA principal
- Persona cible
- Longueur cible (1500-2500 mots typique)

### 3. Rédaction

- Suivre le brief et la doctrine de voix (étape 0).
- Intégrer données et citations de l'étape 1.
- Fichier `09-seo/articles/YYYY-MM-DD-<slug>.md`, frontmatter complet (modèle ci-dessous).

### 4. On-page SEO

- Title tag : < 60 caractères, mot-clé en tête
- Meta description : < 155 caractères, CTA implicite
- Slug : court, minuscules, mot-clé
- H1 unique ; H2 avec variantes du mot-clé
- Maillage interne : minimum 3 liens vers d'autres pages `{{COMPANY_WEBSITE}}`
- Images : alt descriptif, noms de fichiers avec mot-clé
- Schema markup : Article, FAQ (si pertinent), Organization — validation via l'agent `seo-schema`

### 5. AEO (Answer Engine Optimization)

Pour être cité par ChatGPT, Perplexity, Claude, Gemini :
- Réponse factuelle en début de paragraphe
- Balisage sémantique clair (H2 = question, paragraphe = réponse)
- Sources citées avec liens
- Chiffres précis et sourcés
- Aucune formulation floue qu'un LLM ne peut pas reformater proprement
- Audit de citabilité : agent `seo-geo` du plugin

### 6. Brand-check (obligatoire)

Invoquer `brand-check` avant toute publication.

### 7. Publication

- Push vers {{BLOG_CMS}} — dry-run d'abord : `python3 scripts/dry-run-push.py --target {{BLOG_CMS}} --file <article>`.
- Ajouter images et meta tags dans le CMS.
- Configurer catégories et tags.
- Soumettre à Google Search Console (via le couplage `/tools-setup` si actif).
- Mettre à jour le statut dans le calendrier éditorial.

## Frontmatter d'article

```yaml
---
title: "Titre de l'article"
slug: slug-article
date: YYYY-MM-DD
author: {{COMPANY_NAME}}
category: [pilier]
tags: [tag1, tag2, tag3]
keyword_primary: "mot-clé principal"
keywords_secondary: ["kw2", "kw3", "kw4"]
meta_title: "..."
meta_description: "155 caractères max"
status: draft | review | published
language: en | fr
word_count: XXXX
cluster: "..."
---
```

## Règles SEO

### Contenu
- Data d'abord : ≥ 3 chiffres sourcés par article
- Pas de keyword stuffing — densité naturelle
- Maillage interne : ≥ 3 liens par article
- Liens externes : 1-2 sources d'autorité
- Refresh : revisiter tous les 6 mois (prioriser via GSC si couplé)

### Jamais
- Contenu IA générique sans valeur spécifique {{COMPANY_NAME}} (cf. filtre anti-style-IA de l'étape 0)
- Articles sous 800 mots
- Duplication inter-langues (adaptation culturelle, pas traduction mécanique)
- Link-building artificiel

## Personnalisation par marque

{{SEO_SPECIFIC_RULES}}

## Skills associées

- `claude-seo:*` (plugin) — audits et analyses (technique, contenu, clusters, schema, GEO, GSC/GA4)
- `copywriting` — rédaction narrative
- `copy-editing` — relecture 7 passes orientée SEO
- `content-strategy` — planification globale
- `image-generation` — visuels d'article
- `brand-check` — validation finale obligatoire
