# Inventaire des livrables de {{COMPANY_NAME}}

> Tableau généré par `python3 scripts/build-inventory.py`. Ne pas l'éditer à la main : relancer une reconstruction en cas de doute.
> Dernière mise à jour : aucun livrable indexé (lancer `python3 scripts/build-inventory.py` après les premières productions)

| Date | Canal | Type | Sujet | Chemin | Statut |
|---|---|---|---|---|---|

## Note d'usage

- **Rôle** : index unique des livrables produits par le cockpit (posts, carrousels, emails, articles, decks, landing pages, plans de com). C'est la mémoire de production du repo : **toute skill de production le consulte avant de créer** (anti-répétition), et y ajoute sa ligne après livraison avec `python3 scripts/build-inventory.py --add <chemin>`.
- **Tri** : du plus récent au plus ancien (nouvelle ligne en tête de tableau).
- **Date** : date de création du livrable (`YYYY-MM-DD`), pas la date d'indexation. Le script la prend dans le champ `date` du frontmatter, sinon dans le nom du fichier, sinon dans celui du dossier. Un livrable sans date exploitable n'est pas indexé et le script le signale : le renommer en `AAAA-MM-JJ-…` suffit à le faire entrer.
- **Canal** : `linkedin`, `discord`, `whatsapp`, `newsletter`, `email-promo`, `web`, `blog`, `event`, `slides`, `visuel`. Les emails de prospection et de nurturing sont indexés sous `email-promo` ; leur chemin les distingue des promos.
- **Type** : `post`, `carrousel`, `email`, `article`, `landing`, `deck`, `image`, `plan-comm`.
- **Sujet** : 5-10 mots, assez précis pour détecter un doublon à la lecture. Source, dans l'ordre : `subject` du frontmatter, titre (`# ` en markdown, `<title>` ou `<h1>` en HTML), premiers mots du corps, nom du dossier. Les tirets longs des titres d'origine deviennent des points médians.
- **Chemin** : relatif à la racine du repo.
- **Statut** : `brouillon`, `validé`, `publié`, `archivé`. Le script lit `statut` s'il est déclaré, sinon il écrit `publié` dès qu'un champ de diffusion (`sent`, `url`, `likes`) est renseigné, et `validé` sinon ; un contenu `rejeté` ou `abandonné` devient `archivé`. Mettre à jour la ligne existante à chaque changement de statut, ne jamais dupliquer.

**Périmètre du scan** : déclaré dans `scripts/build-inventory.toml` (un `[[sources]]` par dossier de production, avec ses motifs, son canal et son type). Extensions retenues : `.md` et `.html`. Les PDF, images et exports sont ignorés, ainsi que les fichiers de service (`README.md`, `CLAUDE.md`, `playbook.md`, `index.md`…) et tout ce qui vit sous un dossier `templates/`.

**Lecture avant de rédiger** : filtrer sur le canal visé, garder les 90 derniers jours, puis relire les 3 contenus les plus proches du sujet demandé. Si un livrable très proche existe, changer d'angle ou le compléter plutôt que le paraphraser.

**Contrôle** : `python3 scripts/build-inventory.py --check` sort 1 si le tableau a dérivé des dossiers, et signale les fichiers sans date. Format complet et modes (reconstruction / incrément) : voir `.claude/skills/inventory/SKILL.md` et l'en-tête de `scripts/build-inventory.py`.
