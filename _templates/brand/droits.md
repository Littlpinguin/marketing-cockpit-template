---
title: "Registre des droits du patrimoine de marque de {{COMPANY_NAME}}"
type: brand-reference
version: 1.0
updated: {{SETUP_DATE}}
status: à-valider
tags: [droits, licences, droit-a-l-image, polices, logos, photos]
---

# Registre des droits

## Ce que ce registre fait, et ce qu'il ne fait pas

Ce fichier dit, pour chaque famille d'actifs de marque, d'où vient le fichier, sous quelle licence ou quelle base légale la marque l'utilise, et où il est publié. Il répond à une question précise : a-t-on le droit de publier ça, aujourd'hui, sur ce canal ?

Il ne vaut pas avis juridique et ne régularise rien par lui-même. Un statut « à confirmer » est un statut réel : il signale une question ouverte, pas une autorisation implicite. Tant qu'une ligne porte « à confirmer », l'actif reste utilisable en interne mais toute nouvelle publication se décide en connaissance de cause.

**Convention de statut** : `OK` (licence ou autorisation établie et versée au dossier) · `à confirmer` (aucune preuve au dossier) · `à régulariser` (l'usage a commencé sans base écrite).

**Convention de chemin** : un chemin qui commence par une catégorie d'assets (`logos/`, `photos/`, `illustrations/`) est relatif à `01-brand/assets/`. Tous les autres sont relatifs à la racine du dépôt.

**Méthode** : les comptes de fichiers se mesurent sur le disque, jamais de mémoire, et la date de la mesure s'écrit en tête de section. Les lignes ci-dessous marquées « exemple » montrent le format attendu : les remplacer par l'inventaire réel, puis les supprimer.

---

## 1. Polices

Une police est un logiciel sous licence. Une licence bureautique ne couvre en général ni le service du fichier en `@font-face` sur un site, ni son embarquement dans un PDF diffusé, ni sa redistribution dans un dépôt : vérifier chaque usage, pas seulement la police.

| Police | Fichiers dans le dépôt | Licence | Usages autorisés | Webfont | Embarquement PDF | Statut |
|---|---|---|---|---|---|---|
| **{{BRAND_FONT_PRIMARY}}** | À relever (fichiers `.woff2`, `.ttf` du dépôt) | À relever (ex. OFL 1.1 pour une police Google Fonts, licence commerciale de fonderie sinon) | À relever | À relever | À relever | **à confirmer** |
| (exemple) Police secondaire | `assets/fonts/exemple.woff2` | Licence commerciale, fonderie à identifier | Titres d'accent uniquement | Non vérifié | Inconnu | **à confirmer** |

Ajouter une ligne par famille réellement servie ou embarquée, y compris les polices de service (monospace des decks, polices des emails).

---

## 2. Logos de tiers

Un logo est une marque déposée. Le citer comme référence commerciale se négocie, en général au contrat ou par un accord écrit distinct. Les logos de partenaires technologiques obéissent aux règles de marque du programme partenaire, à verser au dossier.

| Marque | Fichiers | Où publié | Base | Statut |
|---|---|---|---|---|
| (exemple) Client A | `logos/clients/logo_client_exemple-a.svg` | Page références du site, deck commercial | Aucune autorisation écrite au dossier | **à confirmer** |
| (exemple) Éditeur partenaire | `logos/partners/logo_partner_exemple.svg` | Decks | Règles de marque du programme partenaire non versées | **à confirmer** |

La colonne « où publié » s'établit à partir des fichiers du dépôt qui appellent chaque logo (decks, bannières, pages), pas de mémoire.

---

## 3. Photos de personnes

Une photo de personne identifiable est une donnée personnelle (au sens du RGPD en Europe) et engage le droit à l'image. Règle de travail, indépendamment de la juridiction : on ne publie l'image reconnaissable d'une personne qu'avec son accord. Les régimes diffèrent sur la forme de l'accord et la durée de conservation : point à faire préciser par un juriste selon les pays où la marque publie.

| Dossier | Fichiers | Ce qu'on y voit | Auteur | Publié | Statut |
|---|---|---|---|---|---|
| (exemple) `photos/ambiance/<evenement>/` | À compter | Participants identifiables lors d'un événement | Photographe à préciser | Decks, réseaux sociaux | **à régulariser** |

Deux questions distinctes se posent sur une photo prise par un tiers : le **droit à l'image** des personnes visibles, et le **droit d'auteur** de la personne qui a pris la photo. Les traiter séparément.

Pour les prochains événements, prévoir une clause de consentement à l'image dans le formulaire d'inscription (photos et vidéos prises pendant l'événement, usages, durée, droit de retrait), relue par un juriste.

---

## 4. Portraits dérivés par IA

Un portrait illustré généré à partir de la photo d'une personne n'est pas une photo, mais il reste dérivé de l'image d'une personne identifiable et la représente. La politique de divulgation associée vit dans `divulgation-ia.md`, qui exige la validation du portrait par la personne avant publication.

| Groupe | Fichiers mesurés | Source | Transformation | Base légale | Statut |
|---|---|---|---|---|---|
| (exemple) Équipe | `illustrations/portraits/team/` | Photo fournie par la personne | Génération d'image, puis composition | Accord à documenter | **à confirmer par personne** |
| (exemple) Personas anonymes | `illustrations/portraits/personas/` | Aucune personne réelle | Illustration | Sans objet : personne n'est représenté | **OK** |

La validation de la personne porte sur deux choses à la fois, et une seule réponse suffit pour les deux : l'accord pour dériver son image, et l'accord pour publier le résultat.

---

## 5. Actions humaines

Ce que {{COMPANY_MAIN_CONTACT}} (ou la personne désignée) doit faire, par ordre de priorité. Aucun de ces points ne peut être traité par un agent : ils supposent un document, un tiers ou une signature.

### Priorité 1 : ce qui est publié sans base écrite

1. **Licences de polices** : retrouver la facture ou le contrat de chaque police commerciale, et vérifier que la licence couvre le service en webfont et l'embarquement PDF.
2. **Photos de personnes** : consentement écrit des personnes reconnaissables, ou retrait des vues où des tiers sont identifiables.

### Priorité 2 : ce qui engage une relation client ou partenaire

3. **Logos clients** : obtenir un accord écrit, ou vérifier si le contrat comporte une clause de référencement.
4. **Règles de marque des partenaires** : récupérer et classer celles de chaque programme partenaire dont le logo est utilisé.
5. **Portraits** : faire valider chaque portrait par la personne représentée.

### Priorité 3 : hygiène du patrimoine

6. **Notices de licence** : verser au dépôt le texte de licence de chaque police redistribuée (l'OFL, par exemple, demande que sa notice accompagne toute redistribution).
7. **Auteurs des photos** : noter qui prend les photos à chaque événement, et l'inscrire dans la fiche d'asset au moment du dépôt.

---

## Tenir ce registre à jour

Une nouvelle famille d'actifs entre ici en même temps qu'elle entre dans le catalogue d'assets (`01-brand/assets/`). La fiche du catalogue porte le statut de l'actif (`source:`, `droits:`, `auteur:`, `généré-par-ia:`), ce registre porte la règle de la famille et la trace de ce qu'il reste à obtenir. Quand une autorisation arrive, elle se note ici avec sa date, et le statut passe de « à confirmer » à « OK ».
