---
title: Catalogue des assets de la marque
type: asset-catalog
version: 1.0
naming: "[categorie]_[sujet]_[variante]_[taille].[ext]"
root: 01-brand/assets/
categories: [logos, icons, illustrations, patterns, photos, banners, archive, docs, sources]
promote_tool: 06-graphic-design/scripts/promote-asset.py
droits: 01-brand/droits.md   # licences, autorisations, droit à l'image : registre unique
---

# Catalogue des assets (couche 3 du cerveau de marque : les exemples)

> **But** : un agent (ou une personne) choisit le bon visuel pour le bon contexte **en lisant uniquement ce catalogue**, sans ouvrir les fichiers. Chaque fiche décrit un asset ou un groupe de variantes.
>
> **Comment l'utiliser** : repérer la catégorie, lire « rôle » et « quand utiliser / ne pas utiliser », prendre le `chemin`. Tous les chemins sont relatifs à `01-brand/assets/`.

## Conventions

- **Nommage** : `[categorie]_[sujet]_[variante]_[taille].[ext]` : minuscules, `_` entre les champs, `-` dans un sujet composé, sans accent.
- **Version canonique** : par groupe, on retient la vectorielle, sinon la plus récente, puis la mieux nommée, puis la meilleure résolution. Les variantes obsolètes vont dans `archive/`.
- **Palette** : la source de vérité est `../tokens.json` (lecture humaine : `../style-guide.md`). Aucune couleur n'est recopiée ici.
- **Droits** : aucun asset n'entre sans source, droits et auteur. Un statut inconnu s'écrit « à confirmer » et s'inscrit au registre `../droits.md` : c'est une question ouverte, jamais une autorisation.
- **Images générées** : leur provenance (modèle, extrait du prompt, empreinte) est ajoutée à la fiche par `promote-asset.py`, via `genmeta.py`. La mention à faire au moment de publier suit `../divulgation-ia.md`.

## Ajouter un asset

Un asset validé entre dans la bibliothèque par le script, jamais à la main :

```bash
python3 06-graphic-design/scripts/promote-asset.py <fichier-source> \
  --dest <categorie>/<nom-conforme.ext> --role "<à quoi il sert>" \
  --source "<d'où il vient>" --droits "<licence ou autorisation>" --auteur "<qui l'a créé>" \
  --ia non   # « oui » pour une image générée : la provenance est alors ajoutée à la fiche
```

Le script range le fichier, contrôle le nom, refuse d'écraser un asset existant et insère la fiche sous la bonne section ci-dessous.

---

## logos/

## icons/

## illustrations/

## patterns/

## photos/

## banners/

## docs/ · sources/

## archive/

---

## Index par cas d'usage

À compléter au fil des promotions : pour chaque contexte (post social, carrousel, slide de couverture, landing, signature email, imprimé), les deux ou trois assets à prendre d'abord.

## Manques détectés

À compléter : les assets que les productions ont réclamés et qui n'existent pas encore (logo sur fond sombre, portraits, illustration de couverture…).
