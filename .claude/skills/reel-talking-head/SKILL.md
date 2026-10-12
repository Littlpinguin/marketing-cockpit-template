---
name: reel-talking-head
description: Chef d'orchestre de la filière face caméra pour {{COMPANY_NAME}}. Transforme une vidéo brute face caméra (client, dirigeant, expert ; visio, smartphone, WhatsApp) en reel vertical monté. Analyse, script de montage, storyboard, assets IA, montage, QA (qa-video.py, agent video-reviewer), avec deux points d'arrêt de validation obligatoires avant toute dépense. Appelée par video-production, dont elle suit le dossier de projet. S'appuie sur video-generation, video-matting, video-editing et captions.
---

# reel-talking-head : d'une vidéo brute à un reel monté

Vous orchestrez la chaîne complète. Chaque étape a sa skill spécialisée ; celle-ci tient l'ordre, les validations et le budget.

La skill est appelée par `video-production`, point d'entrée de toute demande vidéo, qui a cadré l'objectif business et ouvert le projet `08-video/projets/<slug>/` (slug daté `AAAA-MM-JJ-<sujet>`). Elle suit sa structure de projet (`brief.md`, `REPRISE.md`, `decisions.md`, `couts.md`, `script.md` avec son frontmatter `date`, `subject`, `statut`, `storyboard.md`) et son contrat de coût, et y ajoute ses propres fichiers (section « Structure de projet »).

## Les deux règles qui gouvernent tout

**1. Deux points d'arrêt durs.**
- Pas de storyboard tant que le **script** n'est pas validé.
- **Aucun crédit dépensé** tant que le **storyboard** n'est pas validé.

Le script dit quoi générer, pour quelle durée, à quel timecode. Générer avant, c'est jeter du travail et des crédits (retour d'expérience : plusieurs milliers de crédits perdus sur un seul plan généré avant validation de son emplacement).

**2. Contrôler la fidélité du texte de chaque rush généré, avant de le monter.** Un modèle peut faire dire autre chose à la personne filmée, avec une synchro parfaite (skill `video-generation`, section « Fidélité du texte »). C'est le contrôle qui protège le client.

## Déroulé

### Temps 1 : analyse de la source (gratuit)

```bash
ffprobe -v error -show_streams rushes/source.mp4   # rotation en métadonnées (WhatsApp : 1024×576 annoncé = 576×1024 réel)
whisper-cli -m <modèle> -f rushes/audio.wav -l fr -oj -ml 1   # -ml 1 : timings PAR MOT (karaoké et coupes au mot)
ffmpeg -i rushes/source.mp4 -af silencedetect=noise=-30dB:d=0.3 -f null -   # les VRAIS silences (whisper aligne bord à bord)
```

`<modèle>` est le chemin déclaré dans `.env` (`WHISPER_MODEL`). Extraire aussi des images aux moments clés : références pour les générations.

### Temps 2 : script de montage, puis **VALIDATION**

Structure narrative (accroche, problème, bascule, développement, chute), puis découpage. L'accroche et la longueur suivent `08-video/formats.md` § « Format court : repères de production » (première seconde lisible à l'arrêt sur image, trois variantes d'accroche, longueur mesurée). On coupe presque toujours : l'amorce muette, les redites orales, **l'aparté final** (la personne continue de parler après sa chute), et l'on **resserre les respirations vers 0,12 s sans les supprimer**. Repère mesuré : environ 20 % de gras sur un débit rapide ; **ne pas promettre 30 s si le contenu en fait 55**. Livrer le script minuté dans `script.md` et **attendre la validation explicite** (validation 2 de `video-production`).

### Temps 3 : storyboard, puis **VALIDATION**

Un tableau ne suffit pas : générer les **vignettes au vrai recadrage** de chaque plan, dans `storyboard.md`. Le rythme vient de **trois sources** (doctrine : `08-video/montage.md`) :
1. les **échelles** du plan face (recadrages avec des écarts d'au moins 20 %, sinon jump cut) ;
2. les **angles de côté** générés, un par acte narratif, sans alternance mécanique ;
3. les **b-rolls**, peu nombreux et courts.

Livrer le storyboard et **attendre la validation explicite** (validation 3 de `video-production`).

### Temps 4 : assets

1. Lister ce qui manque, d'après le storyboard validé : noir sur blanc, avec durées.
2. Écrire les prompts (mouvement d'abord, en anglais, interdits de raccord) : skill `video-generation`.
3. Itérer là où c'est inclus (application web), valider la **direction** en basse résolution, produire les définitifs par le MCP. Un exemplaire avant toute série, sous le contrat de coût de `video-production` (annonce, `couts.md`).

### Temps 5 : préparation technique

- Détourage si le décor change : skill `video-matting` (et sa mise en garde : régénérer plutôt que rattraper une source molle).
- Synchronisation labiale : passage séparé, audio à la durée exacte du clip.
- **Contrôle de fidélité du texte de chaque rush** (corrélation d'enveloppe), avant de le poser dans le montage.

### Temps 6 : montage, par `video-editing`

Plans selon le script, échelles et punch-ins, étalonnage, sous-titres karaoké (skill `captions`), cartons, plan sonore (`08-video/montage.md`). Deux voies de rendu :

- **`hyperframes:general-video`**, la voie ordinaire d'un reel : coupes, échelles, punch-ins, angles générés et b-rolls se composent dans HyperFrames.
- **`hyperframes:talking-head-recut`**, seulement pour poser un habillage designé (cartons, lower-thirds) : ce workflow passe la séquence telle quelle. Coupes, changements d'échelle, punch-ins et étalonnage y entrent donc déjà faits, par le plan ffmpeg de `video-editing` (voie B) ou par les outils de `hyperframes:media-use`.

Ou tout le montage par le plan ffmpeg. Dans tous les cas, export H.264 normalisé (skill `video-editing`, étape 5).

### Temps 7 : passe d'ajustement

Le storyboard se valide sur le papier ; **le rythme ne se juge qu'à la lecture**. Prévoir explicitement une passe après le premier export : c'est là qu'on voit si l'ouverture tient, si un insert claque trop, si un plan traîne.

### Temps 8 : QA, livraison et capitalisation

- **QA mesurée** avant toute validation humaine :

```bash
python3 08-video/scripts/qa-video.py 08-video/projets/<slug>/exports/<slug>-<plateforme>.mp4 \
  --plateforme <reels|tiktok|shorts|linkedin> --duree <secondes> --script 08-video/projets/<slug>/script.md
```

  Le `--script` fait **transcrire le master final** et le compare au texte d'origine (le montage a pu bouger après un export) : le constat `transcription-couverture` signale un passage manquant. Le rythme du reel tient des plans courts : le contrôle `plan-long` (4 s par défaut) s'y applique tel quel.
- **Revue de l'agent `video-reviewer`** (lecture seule) avec le rendu, `brief.md`, `script.md` et la plateforme ; deux tours de correction au plus, comme dans `video-production`.
- **Validation humaine du rendu final**, ensuite seulement.
- **Accord explicite de la personne filmée** dès qu'un plan est régénéré ou synchronisé : sa voix et son propos sont intacts, mais son image est recomposée.
- Mention « Vidéo générée par IA » en légende, jamais sur le média, selon `01-brand/divulgation-ia.md`.
- Prompts validés capitalisés dans `decisions.md` ; **documenter aussi les échecs avec leur raison**, sinon ils seront retentés.

## Structure de projet

Les fichiers de `video-production`, plus ceux de cette filière :

```
08-video/projets/<slug>/
├── brief.md, REPRISE.md, decisions.md, couts.md   ← communs (video-production) ; REPRISE.md se lit en premier
├── script.md             ← script minuté validé (validation 2)
├── storyboard.md         ← plans et vignettes au vrai recadrage (validation 3)
├── script-montage.md     ← le montage plan par plan (généré, pas édité à la main)
├── workflow.md           ← comment chaque élément a été fabriqué (réussites ET échecs)
├── scripts/              ← tout ce qui est réexécutable
├── assets/               ← vignettes du storyboard
├── rushes/               ← source, rushes générés et leurs sidecars .json, intermédiaires dans rushes/tmp/ (non versionnés)
├── hyperframes/          ← projet HyperFrames, si le montage passe par la voie A de video-editing
├── exports/              ← masters et livrables par plateforme (non versionnés)
└── qa/                   ← rapports et planches de qa-video.py
```

## Repères chiffrés (mesurés en production)

| | Valeur |
|---|---|
| Brut → monté | environ 20 % de réduction (amorce, redites, respirations, aparté) |
| Plan moyen | environ 1,5 à 2,5 s ; tenues de 4 à 5 s réservées aux temps émotionnels |
| Écart sans rupture forte | jamais plus de 4 s |
| Répartition type | environ 65 % face, 25 % angles générés, 10 % b-rolls |
| Poste le plus cher | les plans de côté (génération et synchronisation labiale) |

## Ce que cette skill ne fait pas

- Générer sans script et storyboard validés : jamais, c'est sa raison d'être.
- Publier : validation humaine.
- Le détail technique de chaque étape : skills spécialisées.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
