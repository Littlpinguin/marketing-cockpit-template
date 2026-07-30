---
name: reel-talking-head
description: Chef d'orchestre — transforme une vidéo brute face caméra (client, dirigeant, expert ; visio, smartphone, WhatsApp) en reel vertical monté pour {{COMPANY_NAME}}. Analyse, script de montage, storyboard, assets IA, montage, avec deux points d'arrêt de validation obligatoires avant toute dépense. À utiliser dès qu'une vidéo talking-head doit être retravaillée pour les réseaux. S'appuie sur video-generation, video-matting, video-editing et captions.
---

# reel-talking-head — d'une vidéo brute à un reel monté

Vous orchestrez la chaîne complète. Chaque étape a sa skill spécialisée ; celle-ci tient l'ordre, les validations et le budget.

## Les deux règles qui gouvernent tout

**1. Deux points d'arrêt durs.**
- Pas de storyboard tant que le **script** n'est pas validé.
- **Aucun crédit dépensé** tant que le **storyboard** n'est pas validé.

Le script dit quoi générer, pour quelle durée, à quel timecode. Générer avant, c'est jeter du travail et des crédits (retour d'expérience : plusieurs milliers de crédits perdus sur un seul plan généré avant validation de son emplacement).

**2. Contrôler la fidélité du texte de chaque rush généré, avant de le monter.** Un modèle peut faire dire autre chose à la personne filmée, avec une synchro parfaite (→ `video-generation`, section fidélité). C'est le contrôle qui protège le client.

## Déroulé

### Temps 1 — Analyse de la source (gratuit)

```bash
ffprobe -v error -show_streams source.mp4      # ⚠️ rotation en métadonnées (WhatsApp : 1024×576 annoncé = 576×1024 réel)
whisper-cli -m <modele> -f audio.wav -l fr -oj -ml 1   # -ml 1 : timings PAR TOKEN (karaoké + coupes au mot)
ffmpeg -i source.mp4 -af silencedetect=noise=-30dB:d=0.3 -f null -   # les VRAIS silences (whisper aligne bord à bord)
```

Extraire aussi des frames aux moments clés : références pour les générations.

### Temps 2 — Script de montage → **VALIDATION**

Structure narrative (accroche → problème → bascule → développement → chute), puis découpage. On coupe presque toujours : l'amorce muette, les redites orales, **l'aparté final** (la personne continue de parler après sa chute), et l'on **resserre les respirations à ~0,12 s sans les supprimer**. Repère mesuré : ~20 % de gras sur un débit rapide — **ne pas promettre 30 s si le contenu en fait 55**. Livrer le script minuté et **attendre la validation explicite**.

### Temps 3 — Storyboard → **VALIDATION**

Un tableau ne suffit pas : générer les **vignettes au vrai recadrage** de chaque plan. Le rythme vient de **trois sources** (doctrine : `08-video/montage.md`) :
1. les **échelles** du plan face (recadrages avec écarts ≥ 20 %, sinon jump cut) ;
2. les **angles de côté** générés, un par acte narratif — pas d'alternance mécanique ;
3. les **b-rolls**, peu nombreux et courts.

Livrer le storyboard et **attendre la validation explicite**.

### Temps 4 — Assets

1. Lister ce qui manque, d'après le storyboard validé — noir sur blanc, avec durées.
2. Écrire les prompts (motion-first, anglais, interdits de raccord) → `video-generation`.
3. Itérer là où c'est inclus (app web), valider la **direction** en basse résolution, produire les définitifs par le MCP. Un exemplaire avant toute série.

### Temps 5 — Préparation technique

- Détourage si le décor change → `video-matting` (et sa mise en garde : régénérer plutôt que rattraper une source molle).
- Synchronisation labiale : passage séparé, audio à la durée exacte du clip.
- **Contrôle de fidélité du texte de chaque rush** (corrélation d'enveloppe) — avant import dans la timeline.

### Temps 6 — Montage → `video-editing`

Import → plans selon le script → échelles et punch-ins → étalonnage → sous-titres karaoké (→ `captions`) → cartons → plan sonore (`08-video/montage.md`) → export ProRes → transcodage.

### Temps 7 — Passe d'ajustement

Le storyboard se valide sur le papier ; **le rythme ne se juge qu'à la lecture**. Prévoir explicitement une passe après le premier export : c'est là qu'on voit si l'ouverture tient, si un insert claque trop, si un plan traîne.

### Temps 8 — Livraison et capitalisation

- **Transcrire le master final** et comparer au texte d'origine — mot à mot (le montage a pu bouger après un export).
- **Accord explicite de la personne filmée** dès qu'un plan est régénéré ou synchronisé — sa voix et son propos sont intacts, mais son image est recomposée.
- Mention « Vidéo générée par IA » en légende, jamais sur le média.
- Prompts validés capitalisés ; **documenter aussi les échecs avec leur raison**, sinon ils seront retentés.

## Structure de projet

```
08-video/projets/<slug>/
├── REPRISE.md            ← état + décisions, à lire en premier dans une nouvelle session
├── script-montage.md     ← le montage plan par plan (généré, pas édité à la main)
├── workflow.md           ← comment chaque élément a été fabriqué (réussites ET échecs)
├── scripts/              ← tout ce qui est réexécutable
├── assets/               ← storyboard, vignettes, rushes intermédiaires
└── outputs/              ← masters + livrables + sidecars + registre
```

## Repères chiffrés (mesurés en production)

| | Valeur |
|---|---|
| Brut → monté | ~20 % de réduction (amorce, redites, respirations, aparté) |
| Plan moyen | ~1,5-2,5 s · tenues de 4-5 s réservées aux beats émotionnels |
| Écart sans rupture forte | jamais plus de 4 s |
| Répartition type | ~65 % face · ~25 % angles générés · ~10 % b-rolls |
| Poste le plus cher | les plans de côté (génération + synchro labiale) |

## Ce que cette skill ne fait pas

- ❌ Générer sans script et storyboard validés — jamais, c'est sa raison d'être
- ❌ Publier (→ validation humaine)
- ❌ Le détail technique de chaque étape (→ skills spécialisées)
