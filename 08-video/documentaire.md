# Doctrine du montage documentaire sur archives

Chargée par `video-documentary` pour tout film monté à partir d'archives libres : images d'époque, fonds publics, banques de vidéos sous licence ouverte. L'outillage est `08-video/scripts/corpus.py` ; la narration suit `narration.md`, la coupe et le son suivent `montage.md`.

## Ton

Un essai filmé : un montage d'archives au service d'une thèse, que le spectateur peut formuler en une phrase à la fin. Le sens naît du rapprochement des plans ; la narration, quand il y en a une, oriente sans tout dire.

Ce qui le distingue d'un explainer (`narration.md`) : dans l'explainer, l'image illustre ce que dit la voix ; ici, l'image réelle porte la preuve. Une archive montre que quelque chose a eu lieu, d'où l'exigence sur ce qu'elle montre vraiment, sur sa date et sur sa source.

Avant tout, formuler la question du film en une ligne (« qu'est-ce qu'un geste transmet qu'une machine ne transmet pas ? »). Trop vague (« un film sur l'artisanat »), elle ne donne pas de film ; trop précise (une liste de plans), elle ne donne pas de thèse. Puis choisir un seul registre (grave, ironique, contemplatif, urgent) et le tenir jusqu'au bout : il règle la longueur des plans, la musique et l'étalonnage.

## Du thème aux emplacements

Le brief thématique se découpe en **emplacements** : un emplacement est un plan ou une courte séquence du film, à un endroit précis de l'arc. Chacun est décrit en langage visuel, comme une image qu'on voit :

- le sujet (qui ou quoi) ;
- l'action (ce qui bouge) ;
- le cadre (gros plan, plan large, plongée) ;
- l'époque (années, texture : noir et blanc, couleur passée, numérique) ;
- la lumière (atelier, plein jour, nuit).

Chaque emplacement reçoit deux ou trois requêtes de recherche en anglais, langue dans laquelle les archives sont indexées : une requête littérale, une requête latérale (la même idée sous un autre angle ou à une autre échelle) et, au besoin, une requête de texture (l'ambiance ou l'époque seule).

Le découpage s'écrit dans `08-video/corpus/themes/<nom>.toml`, sur le modèle du thème livré `08-video/corpus/themes/exemple-savoir-faire.toml` :

```toml
nom = "savoir-faire"                    # nom du corpus : 08-video/corpus/savoir-faire/
sources = ["archive", "wikimedia", "nasa", "pexels", "pixabay"]
par_requete = 3                         # résultats gardés par requête et par source
duree_max = 120                         # secondes ; un clip plus long est écarté
# licences = ["domaine-public", "cc0", "cc-by", "pexels", "pixabay"]   # défaut

[[emplacements]]
id = "geste"
description = "close-up of a hand tool shaping a piece, wood shavings or sparks"
requetes = ["wood shavings plane tool", "metal grinding sparks"]
```

La `description` sert à la recherche CLIP (`corpus.py search <nom> --emplacement <id>`). Le modèle par défaut (`ViT-B-32`, poids `laion2b_s34b_b79k`) a été entraîné sur des légendes en anglais, et sa fiche en limite l'usage à l'anglais ([fiche du modèle](https://huggingface.co/laion/CLIP-ViT-B-32-laion2B-s34B-b79K)). Pour un corpus réel, écrire la description en anglais, avec sa traduction française en commentaire si besoin. Le thème d'exemple garde des descriptions en français pour la lecture.

Le découpage est validé par un humain avant `corpus.py build`.

## Règles de sélection

- **Une archive ne dit pas ce qu'elle ne montre pas.** Un atelier filmé en 1950 n'illustre pas « les ateliers d'aujourd'hui » ; une foule n'illustre pas une grève si rien ne dit que c'en est une. Ni contresens (un événement présenté pour un autre), ni anachronisme (une époque pour une autre, sans le dire). Vérifier date et contexte sur la fiche du clip (`08-video/corpus/<nom>/clips/<source>-<id>.json` : titre, auteur, page d'origine) et sur la page source elle-même.
- **Date et source à l'écran** quand l'archive porte un fait : elle prouve, donc elle se référence. Rôle `label` de `frame.md`, discret, en zone sûre.
- **Visages.** Aucun visage reconnaissable d'un particulier sans droit établi (`01-brand/droits.md`). En cas de doute, choisir un autre plan.
- **Le geste plutôt que le mot.** Préférer le plan qui montre un geste à celui qui illustre un mot : pour « transmission », deux mains sur un même outil plutôt qu'un livre ouvert.
- **Voisinage.** Deux plans voisins ne répètent ni le même sujet ni la même échelle ; le sens naît de leur rapprochement.
- **Le meilleur passage, pas le clip entier.** Couper dans le clip le moment qui sert l'emplacement, et sortir du plan avant la fin naturelle de l'action plutôt qu'après.
- **Traçabilité.** Chaque choix est noté dans `selections.json` (clip et instant), et un humain valide la sélection sur la planche des images clés avant le montage. Un clip écarté malgré un bon score se note dans `decisions.md` avec sa raison (époque, contresens, qualité), pour ne pas revenir à la recherche suivante.

## Étalonnage d'archives

Des sources d'époques et de qualités différentes, mises bout à bout, se voient comme plusieurs films. Choisir au cadrage un parti unique pour tout le film, jamais un traitement clip par clip :

- **noir et blanc assumé** : toutes les sources désaturées, contrastes rapprochés ;
- **grain commun** : un même grain posé sur tout le film, qui atténue les écarts de netteté ;
- **étalonnage commun** : une même table de correspondance des couleurs (LUT) appliquée à toutes les sources, après une remise à niveau de l'exposition et de la balance des blancs.

Le parti retenu se consigne dans `decisions.md`.

- **Résolution mesurée, pas supposée.** Une archive ancienne peut être en définition standard et en 4:3. Mesurer chaque clip retenu : `ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 <clip.mp4>`.
- **Recadrage par format.** Un 4:3 dans une toile 9:16 ou 16:9 se recadre sur l'action (couvrir la toile, couper le surplus), ou se pose sur un fond de marque avec sa date et sa source. Jamais étiré.
- **Agrandissement.** Un agrandissement simple adoucit l'image. Un agrandissement par IA invente du détail (visages, textes, objets) qui n'était pas dans l'archive : pas d'agrandissement par IA sur une archive qui porte un fait ; ailleurs, seulement déclaré (`01-brand/divulgation-ia.md`) et consigné dans `decisions.md`. Même règle pour la colorisation d'une archive en noir et blanc : c'est une reconstruction, elle se dit.

## Crédits et licences

Licences admises par défaut par `corpus.py`, qui filtre au moment du `build` :

- domaine public et CC0 : aucune condition ;
- CC BY : attribution obligatoire (titre, auteur, licence avec sa version, lien) ;
- licences Pexels et Pixabay : usage libre, crédit demandé par les plateformes ([API Pexels](https://www.pexels.com/api/), [documentation de l'API Pixabay](https://pixabay.com/api/docs/)).

Exclues par défaut, et pourquoi :

- **CC BY-SA** : l'œuvre modifiée doit être diffusée sous la même licence ([CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr)). Un film de marque qui monte un tel clip risque de devoir être diffusé lui-même sous CC BY-SA.
- **NC** (pas d'utilisation commerciale) : une vidéo de marque est une communication commerciale.
- **ND** (pas de modification) : couper, recadrer, étalonner ou sous-titrer un clip le modifie, et l'œuvre modifiée ne peut pas être diffusée ([CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/deed.fr)).
- **Licence inconnue** : sans licence établie, aucun droit établi.

Élargir les licences se fait par la clé `licences` du fichier thème (valeurs reconnues : celles du défaut, plus `cc-by-sa`, `cc-by-nc`, `cc-by-nd`, `cc-by-nc-sa`, `cc-by-nc-nd` et `inconnue`), seulement après une décision humaine consignée dans `decisions.md` : quelle licence, pour quel film, pourquoi, validée par qui.

Crédits : `corpus.py credits <nom> --selection <selections.json>` écrit `08-video/corpus/<nom>/credits.md`, une ligne par clip retenu (titre, auteur, source et page, licence, mention d'attribution obligatoire). Les reprendre au générique, ou dans la légende de publication quand la vidéo n'a pas de générique, et copier `credits.md` dans le dossier du projet (`08-video/projets/<slug>/`) : le dossier du corpus n'est pas versionné. Vérifier aussi `01-brand/droits.md` pour les règles de la marque sur les images de tiers.

## Outillage

`08-video/scripts/corpus.py`, une commande par étape (le dossier des corpus se change avec `--racine`) :

```bash
# Constituer le corpus : recherche par emplacement et par source, filtre de licence,
# téléchargement, une fiche par clip. Relancer reprend sans retélécharger.
python3 08-video/scripts/corpus.py build 08-video/corpus/themes/exemple-savoir-faire.toml

# Extraire les images clés (une après chaque changement de plan, au moins une toutes les 3 s)
# et construire l'index CLIP.
python3 08-video/scripts/corpus.py index savoir-faire

# Chercher un plan par description libre, ou par la description d'un emplacement du thème
# (cette forme écrit les résultats dans 08-video/corpus/savoir-faire/selections.json).
python3 08-video/scripts/corpus.py search savoir-faire "hands planing a wooden board" --top 5
python3 08-video/scripts/corpus.py search savoir-faire --emplacement geste

# Écrire credits.md pour les clips de la sélection validée.
python3 08-video/scripts/corpus.py credits savoir-faire --selection 08-video/corpus/savoir-faire/selections.json

# Inventaire : nombre de clips, licences, durée totale, index présent ou non.
python3 08-video/scripts/corpus.py list savoir-faire
```

- **Sources sans clé** : Internet Archive (`archive`), Wikimedia Commons (`wikimedia`), NASA (`nasa`).
- **Sources à clé gratuite** : Pexels (`PEXELS_API_KEY`) et Pixabay (`PIXABAY_API_KEY`), lues dans l'environnement puis dans `.env`, jamais affichées. Une source sans clé est ignorée, les autres continuent. Pixabay interdit le téléchargement massif systématique ([documentation de l'API Pixabay](https://pixabay.com/api/docs/)) : garder `par_requete` modeste.
- **Dépendances** : `build`, `credits` et `list` n'utilisent que Python, plus ffmpeg et ffprobe (conversion des fichiers webm ou ogv en mp4, mesure des durées). `index` et `search` demandent en plus les dépendances facultatives : `pip install -r 08-video/requirements-corpus.txt` (open_clip, torch, pillow ; les poids du modèle se téléchargent au premier lancement). Sans elles, ces deux commandes sortent en code 2 et affichent la commande d'installation.
- **Codes de sortie** : 0 fait ; 1 aucune source utilisable, corpus vide, ou donnée du corpus invalide ; 2 usage, thème invalide, corpus ou index absent, dépendance manquante.
- **Sans open_clip** : pas d'index, donc pas d'images clés extraites par l'outil. La sélection se fait à l'œil : une planche par clip avec ffmpeg (`ffmpeg -i <clip.mp4> -vf "fps=1/5,scale=320:-2,tile=4x3" -frames:v 1 <planche.jpg>`, une image toutes les 5 s), puis `selections.json` écrit à la main au même format que celui de `search` : `{"<emplacement>": [{"clip": "<source>-<id>.mp4", "t": <seconde>}]}`.

## Check-list

- [ ] Question du film formulée en une ligne, registre choisi
- [ ] Emplacements décrits en langage visuel, requêtes en anglais, découpage validé par un humain avant `build`
- [ ] Sélection notée dans `selections.json` et validée par un humain sur la planche des images clés
- [ ] Aucune archive à contresens ni anachronique ; date et source à l'écran quand l'archive porte un fait
- [ ] Aucun visage reconnaissable d'un particulier sans droit établi
- [ ] Un seul parti d'étalonnage pour tout le film ; aucun agrandissement par IA ni colorisation non déclarés
- [ ] Licences du défaut, ou élargissement consigné dans `decisions.md` ; `01-brand/droits.md` vérifié
- [ ] `credits.md` produit par `corpus.py credits --selection`, repris au générique ou en légende, copié dans le projet

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
