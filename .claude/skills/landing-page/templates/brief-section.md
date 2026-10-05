# Brief : <section ou lot>, landing « <nom> »

> Remplir chaque `<…>`. Un brief par agent `landing-section-builder`. Tous les briefs d'une vague partent dans un seul message.

## Contexte

- **Page** : `05-web-content/landing-pages/<slug>/index.html` (socle et sections assemblées : **lecture seule** pour toi).
- **Pilotage** : `05-web-content/landing-pages/<slug>/pilotage/`.
- **Aperçu** : <chemin ou URL locale de la page>. Le serveur éventuel est lancé par le contrôleur : ne le relance pas, ne l'arrête pas.
- **Ce qui est déjà fait** : <sections terminées, avec leurs fragments>.
- **Place de la section dans le récit** : <objection qu'elle traite, section avant, section après>.

## À lire, dans cet ordre

1. `pilotage/page-charter.md`, en entier, § 9 compris : il prime sur tout, ce brief compris.
2. `pilotage/spec.md`, § <n> : textes et comportements de cette section.
3. `pilotage/research-notes.md` : références déjà retenues pour ce besoin.
4. Les fragments déjà faits (<fichiers>), pour l'en-tête, les cartes et le mouvement ; le socle (`index.html` hors marqueurs) pour les jetons et le moteur d'apparition.
5. `.claude/skills/landing-page/references/pieges.md`, puis dans `references/sections.md` la mécanique « <nom> ».

## Ton fichier (et seulement lui)

- `pilotage/sections/<nn>-<id>.html` : la `<section id="<id>" aria-labelledby="<id>-titre">`, son `<style>` dont chaque sélecteur commence par `#<id>`, son `<script>` éventuel enfermé dans une fonction.
- <éventuellement : `assets/<id>/…`, visuels propres à la section>

Une modification ailleurs (socle, texte de la spec, autre section, jeton manquant) ne se fait pas : nomme-la dans ton rapport.

## Ce qu'il faut construire

- **Structure** : <balisage attendu, titre de niveau <n>, listes en `role="list"`>.
- **Mécanique** : <le moment orchestré, avec ses valeurs : piste, durées, déclencheurs, états>.
- **Données** : <clés de texte de la spec, configuration de l'offre lue>.
- **Responsive** : <comportement à 1100, 900, 768 et 640 px>.
- **Mouvement réduit** : <état final affiché d'emblée, rien ne bouge>.
- **Mesure** : <`data-track`, `data-cta-position` des CTA de la section>.

## Règles

- Charte : en-tête en `<div class="section-head">`, sans pastille de sur-titre ; titres sans virgule ni point, sans mot seul en fin de ligne ; fond de page jamais recouvert ; jetons du `:root`, aucune couleur en dur ; polices de la marque ; aucun tiret cadratin ; entrées par le moteur commun (`data-reveal`), en opacité et position seules ; un seul moment orchestré, 0,9 s au plus, aucun ressort.
- **Recherche** : si `research-notes.md` ne couvre pas ton besoin, cherche 4 à 6 références (`references/inspiration.md`), sur des sites tiers publics seulement.
- **Interdits** : ne commite pas ; n'écris ni dans `index.html` ni dans le fragment d'un autre ; ne supprime aucun fichier que tu n'as pas créé ; n'invente aucun chiffre, client, témoignage ni fait sur une personne.

## Vérification

- Assemble une **copie** de la page dans ton scratchpad (socle + fragments existants + le tien, même procédure que le skill, phase 5), puis :
  `python3 05-web-content/scripts/qa-landing.py <copie.html>` : aucune erreur qui vienne de ta section.
- `grep -nE "#[0-9a-fA-F]{3,8}|rgba?\(" pilotage/sections/<nn>-<id>.html` : vide.
- `python3 scripts/lint-brand.py pilotage/sections/<nn>-<id>.html` : sans erreur.

## Rapport

Écris `pilotage/reports/<nn>-<id>.md`, avec :
- les 3 références qui t'ont le plus servi (URL, et ce que tu en as pris) ;
- ce que tu as construit et les décisions prises ;
- les vérifications faites, avec leurs résultats ;
- ce qu'il faut regarder à l'œil (états, tailles d'écran) ;
- ce que tu as dû laisser de côté, et pourquoi ; les modifications demandées ailleurs.

Ne me renvoie que le statut (DONE, DONE_WITH_CONCERNS ou BLOCKED), une ligne de QA et tes points d'attention, en 8 lignes au plus.
