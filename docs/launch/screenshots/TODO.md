# Screenshots — état avant lancement

## Produit (2026-07-02, passe « preuves réelles »)

**Démo Meridian (fictif)** — Playwright, viewport 1440×900 ou 1600×900 @2x :

| Fichier | Note |
|---|---|
| `deck-slide-cover.jpg` / `deck-slide-waterfall.jpg` / `deck-slide-quote.jpg` | 3 slides individuelles du catalogue (layouts 01, 35, 28), mode présentation plein écran, 1600 px, JPEG q88 |
| `deck-catalogue-overview.png` | Overview 7 familles — plus référencé par le README (remplacé par les slides individuelles), conservé pour usage docs |
| `dashboard.png`, `landing-*.jpg`, `lead-magnet-roi.jpg` | Landing/lead-magnet convertis PNG→JPEG q85 (passe de compression faite, toutes < 400 Ko) |

**Preuves réelles (section « Real results, real clients »)** :

| Fichier | Source | Validation |
|---|---|---|
| `site-n2.png`, `site-n2-report-tool.png` | Playwright (bannière cookies acceptée) | Sites publics — OK |
| `site-qiplim.png`, `site-jessem.png`, `site-n2-resources.png`, `site-diagnostic-collab.png`, `site-jessem-diagnostic.png` | Captures manuelles Jessy du 02/07, renommées + compressées 1200 px | OK (déposées par Jessy) |
| `seo-results-jessem.png` | Capture GSC Jessy (478 clics +99 %, 12,6k impressions, 3 mois) — intégrée au README | OK (déposée par Jessy) |
| `carousel-ai-act-{1,2,3}.png` | Pages 1, 5, 8 du carrousel AI Act publié (marque perso Jessy, juin 2026) | OK (marque propre) |
| `visual-qiplim-{1,2}.png` | Visuels posts LinkedIn Qiplim (nouveau site, concours VivaTech) | OK (marque propre) |

Retiré : `carrousel-ai-act.pdf` (3,8 Mo — copie identique conservée dans
`jessem/brand/writing-style/linkedin-agent/outputs/carrousel-ai-act-2026-06-29/exports/`),
`deck-catalogue-slide.png` (remplacé par les 3 slides individuelles).

## Restant avant commit

### 1. `wizard-terminal.png` — à capturer À LA MAIN

- Clone frais dans un dossier jetable, `claude`, puis taper `/start-copilot`.
- Capturer le message de bienvenue/préflight (le moment où le copilot explique le flux 30–60 min).
- Recadrer sur la fenêtre du terminal ; vérifier qu'aucun chemin personnel, email ou chaîne façon clé API n'est visible.

### 2. Validation humaine des contenus clients (voir ⚠️ ci-dessus)



(atelier de co-développement, visages identifiables — client et contexte non confirmés).
Si Jessy confirme une photo de formation avec accord des personnes : compresser (~500 Ko) dans ce dossier
et l'ajouter à la section « Real results » du README.

### 4. Candidats secondaires (carrousels/visuels) — listés, non intégrés

- Qiplim : `pando-studio/qiplim-marketing/06-graphic-design/outputs/carrousel-da-vs-ia-2026-05-13/`
- À intégrer plus tard si besoin de variété (même pipeline que `carousel-ai-act-*`).

### 5. Vérification finale

Relire la preview GitHub du README pour confirmer qu'aucune image n'est cassée.
Optionnel à fort impact : un GIF de 8–12 s de navigation du catalogue (flèches + `O`) à substituer en héro du README plus tard.
