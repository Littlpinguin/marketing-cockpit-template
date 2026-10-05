---
title: "Politique de divulgation IA de {{COMPANY_NAME}}"
type: brand-reference
version: 1.0
updated: {{SETUP_DATE}}
status: à-valider
tags: [ia, divulgation, publication, assets, ethique]
---

# Politique de divulgation IA

Référence unique : les rappels de `CLAUDE.md`, `SECURITY.md`, des dossiers de rôle et des skills de production renvoient ici et ne redéfinissent rien. En cas de contradiction, ce fichier fait foi.

## Principe

{{COMPANY_SHORT_NAME}} dit ce qui est généré quand c'est visible et public. On ne cache jamais l'intervention de l'IA, et on n'alourdit jamais un contenu pour l'annoncer : une ligne, à sa place, dans la langue du contenu, suffit.

La règle se lit dans les deux sens. Un visuel qu'un lecteur peut prendre pour une photo ou pour le travail d'un illustrateur porte une mention. Un fond, un grain, un aplat décoratif ne représentent rien et n'en portent pas.

La raison première est la confiance, pas le droit : une marque qui masque ses propres outils perd du crédit dès que le lecteur le découvre. S'y ajoute, sur un périmètre étroit, une obligation réglementaire : l'article 50 du règlement européen sur l'IA vise les contenus qui imitent une personne ou une réalité (voix et vidéos synthétiques, hypertrucages) et impose de les signaler comme artificiels. Il ne concerne ni une illustration, ni un fond décoratif, ni un texte relu par un humain. **À faire vérifier** par une personne qui suit le texte, et selon les juridictions où la marque publie.

## Par type de contenu

| Type | Diffusion publique | Ce qu'on écrit |
|---|---|---|
| Illustration ou scène générée | Mention | Crédit court, au format du canal (tableau suivant) |
| Portrait d'une personne réelle, généré depuis sa photo | Mention | Mention dans l'alt-text ou la légende. La personne a validé son portrait avant publication, sans exception (voir `droits.md`) |
| Fond, texture, grain, élément décoratif | Aucune | Rien : ces éléments ne représentent ni une personne ni une scène |
| Mockup d'écran ou d'interface | Mention | Crédit court, et l'interface ne se fait jamais passer pour un produit client réel |
| Texte rédigé avec l'IA puis relu et validé par un humain | Aucune | Rien : la responsabilité éditoriale est humaine et signée |
| Voix ou vidéo synthétique | Mention obligatoire, en tête | Au début du contenu, pas en fin de description |

**Le critère qui tranche** : l'image représente-t-elle quelque chose ? Une scène, un lieu, un objet, une personne, une interface : elle représente, donc elle se mentionne. Un fond, un grain, une texture ne représentent rien, ils habillent : aucune mention. En cas d'hésitation, c'est le sujet que le lecteur y voit qui décide.

Un contenu interne (note, brouillon, moodboard, maquette de travail) ne relève pas de cette politique : la divulgation porte sur ce qui est publié.

## Formulations par canal

Les mentions publiées suivent la langue du contenu (langue par défaut de la marque : {{BRAND_DEFAULT_LANGUAGE}}). Les formulations ci-dessous sont des propositions par défaut, à valider puis à réutiliser telles quelles plutôt qu'à réinventer à chaque livrable.

| Canal | Emplacement | Formulation FR | Formulation EN |
|---|---|---|---|
| Réseaux sociaux | Dernière ligne du post | `Visuel créé avec l'aide de l'IA` | `Visual created with AI assistance` |
| Site web | Alt-text de l'image, plus un crédit en pied de page | `Illustration créée avec l'aide de l'IA` | `Illustration created with AI assistance` |
| Deck ou présentation | Page de fin ou colophon | `Illustrations créées avec l'aide de l'IA par l'équipe {{COMPANY_SHORT_NAME}}` | `Illustrations created with AI assistance by the {{COMPANY_SHORT_NAME}} team` |
| Imprimé | Colophon, au même corps que les crédits d'impression | Idem deck | Idem deck |
| Newsletter | Crédit en pied, sous le bloc d'adresse | `Visuels créés avec l'aide de l'IA` | `Visuals created with AI assistance` |
| Vidéo, voix de synthèse | Carton d'ouverture, ou première ligne de la description | `Voix de synthèse` | `Synthetic voice` |
| Vidéo générée sans voix de synthèse | Carton d'ouverture, ou première ligne de la description | `Vidéo générée par IA` | `AI-generated video` |

Une seule mention **visible** par support, jamais une par image : si un deck contient douze visuels générés, le colophon les couvre tous. L'alt-text, lui, n'est pas visible : il se renseigne image par image, sur chaque visuel généré, sans compter comme une mention de plus.

## Registre des assets générés

Chaque asset généré porte `généré-par-ia: oui` dans sa fiche du catalogue d'assets (`01-brand/assets/`), au même titre que sa palette ou sa transparence. Un asset photographié, dessiné à la main ou hérité de la charte porte `généré-par-ia: non`. Le champ se renseigne au moment où l'asset entre dans la bibliothèque ; sur une fiche ancienne, l'absence du champ ne vaut pas « non ».

Ce registre répond vite à une question simple : ce visuel qu'on republie deux ans plus tard, faut-il encore le créditer ?

## Ce qui n'est jamais généré

Cette liste ne relève pas de la divulgation : ces éléments ne se déclarent pas, ils ne se produisent pas.

- **Le logo**, les emblèmes et les tampons de la marque : le vrai fichier vectoriel est inséré, jamais une imitation générée ou tapée au clavier.
- **Les chiffres et les preuves** : ils viennent de `messaging-framework.md`, jamais d'un modèle.
- **Le texte de marque** posé dans un visuel : il est composé en HTML, pas généré dans l'image.
- **Une photo présentée comme réelle** : les vraies photos vivent dans `01-brand/assets/`, et rien de généré n'y entre sous ce statut.
- **Une mise en scène d'une personne réelle dans un visuel généré** : la personne dont un contenu parle est celle qu'on photographie, jamais un substitut généré.
- **Une voix clonée, un visage imité ou le style d'un artiste vivant présentés comme authentiques** : au-delà de l'éthique, c'est un risque légal dans la plupart des juridictions (rappel de `SECURITY.md`).

## Cas limites

**Retouche légère d'une vraie photo** (recadrage, exposition, détourage, effacement d'un objet parasite) : pas de mention, cela reste une photo. La mention redevient obligatoire dès qu'un ajout ou un remplacement change ce que la scène montre (un visage, un lieu, un objet que personne n'a vu ce jour-là).

**Agrandissement ou débruitage** : pas de mention, on n'invente pas de contenu. Vérifier tout de même le rendu d'un visage : un outil qui redessine des traits bascule dans le cas précédent.

**Sous-titres transcrits par IA puis relus** : pas de mention, la relecture humaine engage la responsabilité éditoriale.

**Portrait validé par la personne** : la validation ne remplace pas la mention. Elle conditionne la publication, la mention documente la fabrication. Les deux sont requises.

**Doute** : on mentionne. Une mention de trop coûte une ligne, une mention manquante coûte la confiance.

## Points à valider

Statut `à-valider` : ce texte est une politique par défaut, posée par le gabarit du cockpit. Il s'applique dès maintenant et attend l'arbitrage de {{COMPANY_MAIN_CONTACT}} sur cinq points :

1. **Un texte rédigé avec l'IA puis relu par un humain ne porte aucune mention.** C'est la décision la plus lourde.
2. **Une seule mention visible par support**, l'alt-text mis à part.
3. **Le contenu interne est hors périmètre** : moodboards, maquettes de travail, notes.
4. **La portée de l'article 50** telle qu'elle est décrite plus haut, à faire vérifier.
5. **Les formulations de référence** : aucune n'a encore été éprouvée sur un livrable publié.
