# Registre des skills design vendorisées

Ce template fonctionne en **standalone au fork** : les meilleures skills design externes ont été copiées et adaptées dans `.claude/skills/` plutôt que référencées comme dépendances de plugins. Ce fichier est le registre de traçabilité : source, licence, adaptations, procédure de re-synchronisation.

Date de vendorisation initiale : **2026-07-02**.

## Vue d'ensemble

| Skill du template | Source | Version source | Licence | Statut |
|---|---|---|---|---|
| `.claude/skills/design-system/` | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (NextLevelBuilder) | v2.5.0 | MIT | ✅ Vendorisée |
| `.claude/skills/design-review/` | [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) (NextLevelBuilder) | v2.5.0 | MIT | ✅ Vendorisée |
| `.claude/skills/design-direction/` | [frontend-design](https://github.com/anthropics/claude-code) (plugin officiel Anthropic `claude-plugins-official`) | non versionné (cache 2026-07) | Apache-2.0 | ✅ Vendorisée |
| — | web-artifacts-builder (plugin `anthropic-agent-skills/example-skills`, Anthropic) | non versionné (cache 2026-07) | Apache-2.0 | ⛔ Non vendorisée (hors périmètre, voir plus bas) |

Licences constatées sur disque au moment de la copie :
- ui-ux-pro-max : fichier `LICENSE` à la racine du dépôt — MIT, © 2024 Next Level Builder. Confirmé par `skill.json` (`"license": "MIT"`).
- frontend-design : `LICENSE.txt` dans le dossier de la skill et `LICENSE` à la racine du plugin — Apache License 2.0.
- web-artifacts-builder : `LICENSE.txt` dans le dossier de la skill — Apache License 2.0.

Note d'audit : ui-ux-pro-max a fait l'objet d'un audit sécurité statique (verdict « install with caveats », les réserves portant sur des skills annexes du dépôt, pas sur le contenu vendorisé ici). Seules les **données** (CSV) et les règles du skill principal ont été reprises — aucun script Python n'a été copié ni exécuté.

---

## design-system

- **Source** : `ui-ux-pro-max-skill/src/ui-ux-pro-max/data/` — `styles.csv` (84 styles), `colors.csv` (161 palettes), `typography.csv` (73 pairings) — et structure de workflow de `templates/base/skill-content.md`.
- **Copie locale de la source** : `/Users/ADMIN/claude-projets/test-sécu/ui-ux-pro-max-skill/` (clone d'audit).
- **Version / date** : v2.5.0, copié le 2026-07-02.
- **Licence** : MIT (attribution conservée en pied de `SKILL.md` et en tête de chaque fichier `references/`).
- **Adaptations** :
  - Suppression totale de la dépendance aux scripts Python (`search.py`, moteur BM25) : les données sont condensées en Markdown lisible directement (`references/styles.md`, `references/palettes.md`, `references/typographie.md`).
  - Sélection web marketing : 27 styles retenus sur 84 (mobile natif, SwiftUI/Flutter/React Native, dashboards BI écartés), 28 palettes sur 161 (secteurs pertinents pour un site marketing), 27 pairings sur 73 (pairings mobile et scripts non latins écartés).
  - **Ajout de l'étape 0** : chargement obligatoire des design tokens de `01-brand/style-guide.md` — la marque prime sur tout style générique ; les références deviennent une bibliothèque de fallback/calibration avec ordre de résolution documenté (marque → dérivation → références → défaut neutre).
  - Livrable normalisé : bloc `:root` CSS + tableau de provenance des tokens, persisté à côté du livrable.
  - Rédaction en français, placeholders de marque du template (`BRAND_*`) intégrés.

## design-review

- **Source** : `ui-ux-pro-max-skill/src/ui-ux-pro-max/templates/base/quick-reference.md` (grille de priorités 1-10 + règles détaillées) et `data/ux-guidelines.csv` (99 règles).
- **Version / date** : v2.5.0, copié le 2026-07-02.
- **Licence** : MIT (attribution en pied de `SKILL.md`).
- **Adaptations** :
  - Filtrage web : règles iOS/Android/React Native/Flutter écartées (safe areas natives, haptique, gestes système, Dynamic Type natif…) ; conservation des règles `Platform: Web/All`.
  - **Ajout de la priorité P0 « conformité marque »** (bloquante) au-dessus de l'accessibilité, adossée à `01-brand/style-guide.md` et au `design-tokens.md` du livrable.
  - Ajout d'un format de rapport (`[P{n}-{sévérité}] fichier:ligne — problème → correction`), de deux modes (review/fix) et d'un verdict tri-état, alignés sur les conventions de `brand-check`.
  - Grille recomposée en 9 priorités (P0-P8) + checklist express pré-livraison ; passerelle explicite vers `brand-check` (fond éditorial).
  - Rédaction en français.

## design-direction

- **Source** : skill `frontend-design` du plugin officiel Anthropic (`~/.claude/plugins/cache/claude-plugins-official/frontend-design/unknown/skills/frontend-design/SKILL.md`).
- **Version / date** : plugin non versionné dans son manifeste ; copie du cache local le 2026-07-02.
- **Licence** : Apache-2.0 (attribution en pied de `SKILL.md`).
- **Adaptations** :
  - Traduction et réécriture en français, contenu opérationnel conservé : posture « design lead de studio », héros-thèse, structure-information, les trois looks « IA » par défaut à éviter, processus en deux passes avec critique du plan, retenue (« un seul endroit pour l'audace »), section « écrire dans le design ».
  - **Ajout de l'étape 0** : chargement des tokens `01-brand/style-guide.md` — la direction artistique s'exerce dans l'espace laissé libre par la marque ; contourner un token de marque est une faute, pas de l'audace.
  - Ancrage dans le workflow du template : renvois vers `copywriting` (copy réel via messaging-framework), `design-system` (formalisation des tokens), `design-review` (QA), `brand-check` (validation éditoriale) ; notes anti-répétition consignées dans le dossier du livrable.
  - Suppression des références aux mécanismes de mémoire spécifiques à claude.ai.

## web-artifacts-builder — non vendorisée (décision motivée)

- **Localisation** : `~/.claude/plugins/cache/anthropic-agent-skills/example-skills/575462609294/skills/web-artifacts-builder/` — licence Apache-2.0 constatée (vendorisation possible juridiquement).
- **Raison de l'exclusion** : la skill est un outillage de build d'artifacts claude.ai (React 18 + Vite + Parcel + shadcn/ui, scripts `init-artifact.sh` / `bundle-artifact.sh` produisant un HTML monolithique pour l'interface claude.ai). Le template produit des livrables **HTML statiques autonomes** (`05-web-content/`, `06-graphic-design/presentations/`) sans chaîne de build Node : vendoriser ces scripts ajouterait une dépendance lourde sans bénéfice. Son unique guideline design réutilisable (éviter le « AI slop » : layouts tout-centrés, gradients violets, radius uniformes, Inter par défaut) est déjà couverte, en plus complet, par `design-direction`.
- **Si le besoin émerge** (artifacts React complexes) : re-évaluer depuis la source, URL du dépôt : <https://github.com/anthropics/skills> (dossier `web-artifacts-builder`).

---

## Procédure de re-synchronisation

Les skills vendorisées sont des **adaptations**, pas des miroirs : ne jamais écraser un fichier du template par sa source. Procédure :

1. **Récupérer la nouvelle version de la source** :
   - ui-ux-pro-max : `git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill` (comparer le tag avec la version notée ici) ;
   - frontend-design : mise à jour du plugin officiel (`claude-plugins-official`) puis lire `skills/frontend-design/SKILL.md` dans le cache ;
   - anthropic skills : <https://github.com/anthropics/skills>.
2. **Vérifier que la licence n'a pas changé** (fichier LICENSE de la source). Si elle devient restrictive : geler la version vendorisée actuelle et le noter ici.
3. **Diff ciblé** : comparer la source avec la version notée dans ce registre (colonnes « Version source ») ; identifier les nouveautés utiles au web marketing (nouveaux styles, nouvelles règles UX, corrections de contraste).
4. **Reporter manuellement** les changements pertinents dans les fichiers du template, en préservant : l'étape 0 (marque prime), les placeholders de marque (`BRAND_*`), le français, le filtrage web, les passerelles inter-skills.
5. **Mettre à jour ce registre** : nouvelle version source, date, résumé des changements reportés.
6. **Passer `/validate-setup`** (lint des placeholders) et tester chaque skill sur un brief factice.

Audit périodique recommandé : à chaque release majeure du template, vérifier que les sources amont n'ont pas publié de correctifs d'accessibilité (contrastes WCAG des palettes notamment).
