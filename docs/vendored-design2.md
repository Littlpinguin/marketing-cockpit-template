# Vendoring — chantier complémentaire n°1 (design-taste, design-redesign, brandkit, humanize-writing, translation)

> Vendorisation réalisée le **2026-07-02**, sur la base des recommandations de `docs/etat-de-lart/ecosysteme-skills.md` (recherche du 2026-07-02). Complète `docs/vendored-design.md` (ui-ux-pro-max → design-system / design-direction).
>
> Méthode : fetch direct des fichiers depuis GitHub (raw.githubusercontent.com + API), **licence vérifiée sur le fichier LICENSE de chaque repo au moment du fetch**, condensation et adaptation en français aux conventions du template (étape 0 de chargement des tokens `01-brand/`, placeholders `{{...}}`, articulation avec les skills existantes). Aucune copie brute de fichiers inutiles.

---

## 1. taste-skill (Leonxlnx) → `design-taste`, `design-redesign`, `brandkit`

| | |
|---|---|
| **Source** | https://github.com/Leonxlnx/taste-skill |
| **Licence constatée au fetch** | MIT — `LICENSE` : « Copyright (c) 2026 Leonxlnx » |
| **Version / état au fetch** | branche `main`, commit `06d6028` (2026-06-20). `taste-skill` = **v2 (experimental)**, nouveau défaut depuis le rewrite v2 (cf. CHANGELOG du repo) ; ~54,7k★ |
| **Fichiers sources utilisés** | `skills/taste-skill/SKILL.md` (v2, 87 Ko), `skills/redesign-skill/SKILL.md` (15 Ko), `skills/brandkit/SKILL.md` (16 Ko), `LICENSE`, `CHANGELOG.md` |

### Sélection faite (3 skills sur 13, conformément à l'audit)

| Skill amont | Skill template | Traitement |
|---|---|---|
| `design-taste-frontend` (v2) | `.claude/skills/design-taste/` | Condensée (~87 Ko → ~24 Ko) : lecture du brief, 3 curseurs (DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY) + tables d'inférence, carte brief→design-system, stack par défaut, hard rules layout/typo/couleur/états, **squelettes GSAP canoniques conservés intégralement** (sticky-stack, pan horizontal, reveal stagger + patterns interdits), garde-fous perf/a11y, tells IA condensés, pre-flight check ramené à ~15 familles de cases |
| `redesign-existing-projects` | `.claude/skills/design-redesign/` | Quasi-intégrale (l'audit est dense et actionnable), traduite et adaptée : étape 0 marque, distinction cible template vs client externe, renvoi aux squelettes GSAP de design-taste, rappel du risque SEO relié à la skill `seo` |
| `brandkit` | `.claude/skills/brandkit/` | Condensée (~16 Ko → ~9 Ko) : ajout de **deux modes** (expression de la marque existante avec tokens verrouillés / conception d'une proposition d'identité), branchement sur la skill `image-generation` du template et le staging `06-graphic-design/outputs/`, modes visuels ramenés en table |

### Exclusions (10 skills non vendorisées)

`minimalist-skill`, `brutalist-skill`, `soft-skill` (presets redondants avec les styles d'ui-ux-pro-max), `taste-skill-v1` (remplacée par v2), `gpt-tasteskill` (portage GPT), `image-to-code-skill`, `imagegen-frontend-web`, `imagegen-frontend-mobile` (hors périmètre, la génération d'images passe par `image-generation`), `stitch-skill`, `output-skill` (outillage propre au repo amont). Également exclus : appendices d'installation par design system et l'approximation « Liquid Glass » (résumées en une ligne), le contrat de Block Library §12 (schéma interne au repo amont), les assets README.

### Adaptations clés

- **Étape 0 obligatoire** : « charger les tokens `01-brand/style-guide.md` — **la marque PRIME sur les curseurs** » et sur tout ban esthétique (ex. la règle LILA cède si la marque est violette ; la police de marque prime sur les recommandations de fontes).
- Frontmatter et corps en français, placeholders `{{COMPANY_NAME}}`.
- **Note de complémentarité** en tête de `design-taste` : taste = protocole d'exécution ; `ui-ux-pro-max` = base de données de styles ; `design-system` = tokens sous contrainte de marque ; `design-direction` = cadrage amont ; `design-redesign` = refonte de l'existant.
- Ban du cadratin aligné sur la checklist de marque (`01-brand/checklist-pre-composition.md` §2b fait foi : cadratin `—` interdit, demi-cadratin `–` autorisé — la source amont bannissait les deux).
- Politique d'images branchée sur `01-brand/assets/index.md` + skill `image-generation` (règle « un asset existant se réutilise, il ne se régénère pas »).

---

## 2. humanize-writing (jpeggdev) → `humanize-writing`

| | |
|---|---|
| **Source** | https://github.com/jpeggdev/humanize-writing |
| **Licence constatée au fetch** | MIT — `LICENSE` : « Copyright (c) 2025 jpeggdev » |
| **Version / état au fetch** | branche `main`, commit `da03340` (2026-03-14), skill v2.0.0 (frontmatter amont) |
| **Fichiers sources utilisés** | `SKILL.md` (25 Ko), `references/ai-tells.md` (10 Ko), `LICENSE` |

### Sélection et traitement

- `SKILL.md` → `.claude/skills/humanize-writing/SKILL.md` : les **8 passes** conservées (structure, inflation, vocabulaire, grammaire, rythme, hedging, transitions, voix), exemples avant/après condensés, format de sortie (tableau « Changements », mode revue-sans-réécriture avec consolidation des signalements) conservé.
- `references/ai-tells.md` → `.claude/skills/humanize-writing/references/ai-tells.md` : condensé (liste EN Tier 1/Tier 2, familles de phrases, patterns grammaticaux et structurels, heuristique de détection à 15 cases).
- Exclusions : `install-skill.js` / `uninstall-skill.js` / `package.json` (outillage npm d'installation, inutile en vendoring), README.

### Adaptations clés

- **Positionnement explicite : COMPLÈTE la checklist-pre-composition sans la remplacer** — la checklist (`01-brand/checklist-pre-composition.md` §2) reste la règle *préventive* chargée avant d'écrire ; humanize-writing est la passe *curative* sur texte existant, **invocable comme passe finale par `copy-editing`** (ordre documenté : copy-editing d'abord, humanize ensuite).
- Règles du template plus strictes que la source, documentées comme telles : parallélisme négatif = faute fatale dès la première occurrence (vs « density-based » amont) ; **zéro cadratin** (vs « compter avant de signaler » amont).
- Passe 8 (voix) subordonnée à `01-brand/voice.md` : on injecte la voix de la marque, pas une personnalité générique.
- Vocabulaire : liste EN de la source + liste FR de la checklist + `{{BRAND_VOCABULARY_BANNED}}`, cumulatifs.

---

## 3. claude-translation-skill (senshinji) → `translation`

| | |
|---|---|
| **Source** | https://github.com/senshinji/claude-translation-skill |
| **Licence constatée au fetch** | MIT — `LICENSE` : « Copyright (c) 2026 senshinji » |
| **Version / état au fetch** | branche `main`, commit `42d6c8a` (2026-03-12) |
| **Fichiers sources utilisés** | `SKILL.md` (23 Ko), `references/glossary-schema.md`, `references/anti-fabrication-checklist.md`, `references/review-feedback-schema.md`, `LICENSE` |

### Sélection et traitement

- `SKILL.md` → `.claude/skills/translation/SKILL.md` : pipeline complet conservé (phase 0 préparation + manifeste structurel + chunking, phase 1 traduction ∥ recherche terminologique — mode 1 ou 2 chercheurs selon le volume de termes, phase 2 revue indépendante, phase 3 révision protégée, phase 4 validation + mise en forme). Les contrats des `references/` (schéma de glossaire avec scores de confiance, priorités de revue FABRICATION > OMISSION > …, checklist anti-fabrication) sont **condensés dans le SKILL.md** plutôt que vendorisés en fichiers séparés.
- Exclusions : `references/typesetting-rules.md` (règles SimSun/Times New Roman sino-anglaises, résumées en une ligne de mise en page sobre), `references/test-*.sh` (harnais de test du repo amont), `references/scaling-guidelines.md` (fondu dans le dimensionnement), CI GitHub, scripts.

### Adaptations clés

- **Orchestration portée d'Agent Teams (expérimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) vers les subagents standard** (outil Agent, dispatch parallèle) — aucune dépendance à une feature flag.
- **Contexte marketing multilingue** : étape 0 charge `voice.md` + checklist (le vocabulaire interdit et les règles anti-style-IA s'appliquent dans la langue cible ; les formules signature ne se traduisent pas littéralement sans validation) ; **glossaire de marque persistant** `01-brand/glossaire-traduction.md` qui prime sur la recherche web et se capitalise mission après mission ; passe de revue « registre » étendue en « voix/registre » (conformité `voice.md`, zéro tell IA introduit).
- Intégration template : les contenus traduits passent le gate `brand-check`, se rangent dans les dossiers de canal, mettent à jour le calendrier éditorial ; export .docx/.pdf optionnel via les skills docx/pdf ; lecture de `.setup-completed` (`language`, `bilingual`).
- Exemples sinophones (术语核查, suffixes 协会/委员会) généralisés ; heuristiques chiffrées conservées (~8-10 termes/page, seuil 50 termes pour le split, seuil 10 pages pour le chunking, « 13 échecs de structure » de la révision non protégée).

---

## Textes de licence (obligation MIT : conserver copyright + permission notice)

Les trois sources sont sous licence MIT, dont le texte est identique à l'exception de la ligne de copyright :

> MIT License
>
> Copyright (c) 2026 Leonxlnx *(taste-skill)*
> Copyright (c) 2025 jpeggdev *(humanize-writing)*
> Copyright (c) 2026 senshinji *(claude-translation-skill)*
>
> Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
>
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Chaque SKILL.md vendorisée porte en pied de page l'attribution (repo, auteur, licence) et renvoie ici.

---

## Procédure de re-synchronisation

À dérouler périodiquement (suggestion : au `/health-check` trimestriel) ou quand un repo amont publie une version majeure :

1. **Vérifier l'état amont** :
   ```bash
   curl -s "https://api.github.com/repos/Leonxlnx/taste-skill/commits?per_page=1"           # dernier commit vs 06d6028
   curl -s "https://api.github.com/repos/jpeggdev/humanize-writing/commits?per_page=1"      # vs da03340
   curl -s "https://api.github.com/repos/senshinji/claude-translation-skill/commits?per_page=1"  # vs 42d6c8a
   ```
2. **Re-vérifier la licence** (`LICENSE` de chaque repo) : si elle n'est plus MIT, ne pas synchroniser et signaler.
3. **Diff ciblé** sur les seuls fichiers sources listés ci-dessus (pour taste-skill : surveiller en priorité `CHANGELOG.md` — le passage de v2 experimental à v2.0.0 stable peut changer les noms de curseurs et la structure des sections).
4. **Reporter les changements de fond** (nouvelles hard rules, nouveaux tells, nouvelles phases) dans les versions condensées **en préservant les adaptations locales** : étape 0 marque, préséance de la checklist (cadratin/demi-cadratin, parallélismes), branchements template (image-generation, brand-check, glossaire de marque, subagents standard). Ne jamais re-coller le fichier amont tel quel.
5. Mettre à jour dans ce document : commit/date de fetch, et toute évolution du périmètre (skills amont ajoutées/retirées).
6. Passer `/validate-setup` (lint des placeholders) puis tester une invocation de chaque skill modifiée.

## Récapitulatif

| Skill template | Source | Licence | Fichiers créés |
|---|---|---|---|
| `design-taste` | Leonxlnx/taste-skill (`taste-skill` v2) | MIT | `SKILL.md` |
| `design-redesign` | Leonxlnx/taste-skill (`redesign-skill`) | MIT | `SKILL.md` |
| `brandkit` | Leonxlnx/taste-skill (`brandkit`) | MIT | `SKILL.md` |
| `humanize-writing` | jpeggdev/humanize-writing v2.0.0 | MIT | `SKILL.md`, `references/ai-tells.md` |
| `translation` | senshinji/claude-translation-skill | MIT | `SKILL.md` |
