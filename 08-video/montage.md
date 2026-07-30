# Doctrine de montage — le langage documentaire

Règles de coupe, de rythme et de son pour tout montage narratif (talking-head, interview, documentaire, reel expert). Chargées par `video-editing` et `reel-talking-head`. Tout est **mesurable** : c'est une check-list avant export, pas une inspiration.

## Transitions — presque aucun effet

**Contre-intuitif mais central : un montage haut de gamme n'utilise presque aucun effet de transition.** ~90 % des coupes sont des cuts francs. L'élégance vient du son et des raccords, jamais d'un effet visuel.

| Règle | Application |
|---|---|
| **Cut franc partout** | Aucun fondu enchaîné dans le corps du film |
| **J-cut / L-cut** | L'image et le son ne coupent pas au même endroit — *la* signature du montage documentaire. Sur une voix continue : faire démarrer un riser ou une nappe 4-8 images **avant** la coupe image |
| **Couper dans le mouvement** | Placer la coupe pendant un geste, jamais sur un temps mort — le mouvement masque la coupe |
| **Raccord d'échelle ≥ 20 %** | Deux cadrages trop proches produisent un jump cut. Trois échelles types (large / serré / très gros plan) espacées d'au moins 20 % |
| **Punch-in continu** | Chaque plan fixe porte un zoom très lent (2-4 % sur la durée du plan), imperceptible — c'est ce qui sépare un plan fixe amateur d'un plan documentaire |

**Les seuls effets tolérés** : ouverture depuis le noir (~0,3 s), fermeture (~0,5 s), éventuellement un fondu de 4-6 images à l'entrée/sortie d'un b-roll clair sur un montage sombre — à tester contre le cut franc, qui gagne souvent. **Jamais de fondu au noir en cours de film** : sur un reel, c'est une invitation à scroller.

**À proscrire** : speed ramp, zoom-transition, glitch, flash blanc, wipe, spin — le langage YouTube générique, qui date immédiatement un montage. Le whoosh de transition est le marqueur amateur n° 1.

## Rythme — les chiffres qui font pro

- **Médiane des plans 2,0-2,5 s** (rythme neutre 2-4 s) + **2-3 tenues de 4-5 s** réservées aux beats émotionnels (énumération qui atterrit, question laissée en suspens). Le sur-découpage (médiane < 2 s sans tenues) fatigue et aplatit.
- **Jamais plus de 4 s sans rupture** (changement d'échelle, d'angle ou d'image).
- Le rythme vient de **trois sources** — échelles du plan principal, angles alternatifs (un par acte narratif, pas d'alternance mécanique), b-rolls rares et courts. Au-delà de 3 b-rolls clairs sur un montage sombre, effet stroboscope.
- **Les 5-7 premières secondes en adresse caméra directe**, sans angle ni b-roll : le regard direct est ce qui accroche.

## Son — la moitié du montage

- **Voix d'abord** : débruiter avant tout traitement (jamais normaliser avant de débruiter), passe-haut ~85 Hz, normalisation en dernier. Cible master : **−14 LUFS intégré** (contrôle : `ffmpeg -af ebur128`), crête vraie ≤ −1,5 dBTP.
- **Musique** : entrée fondue après l'accroche, ducking net sous la voix (~10-12 dB d'écart voix/musique), et **au moins un silence total** posé sur le moment le plus fort — le moment le plus puissant d'un plan sonore est un silence, pas un effet.
- **SFX : 5 maximum par film, ≥ 6 dB sous la voix, sons de banque** (la synthèse n'a pas la texture ; l'éditeur importe n'importe quelle URL HTTPS de banque). Impacts posés sur les mots durs, ticks discrets sur les cartons (2 frames avant l'apparition).
- **J-cut sonore** : whoosh ou riser posé quelques frames **avant** la coupe image, jamais dessus.
- Après toute réparation/repose d'un clip SFX, **reposer son gain** — un effet recréé revient à plein volume et traverse tous les contrôles.

## Sous-titres et cartons

- Karaoké mot à mot : → skill `captions` (méthode éditeur, timings par token).
- Cartons : peu, courts (~2 s), un style unique (pastille de marque, police du style-guide), calés sur le mot qu'ils illustrent.

## Check-list mesurable avant export

- [ ] Médiane des plans entre 2,0 et 2,5 s ; 2-3 tenues ≥ 4 s aux beats
- [ ] Aucun écart > 4 s sans rupture ; raccords d'échelle ≥ 20 %
- [ ] Zéro effet de transition hors ouverture/fermeture
- [ ] Punch-in continu sur tous les plans fixes
- [ ] ≤ 5 SFX, ≥ 6 dB sous la voix, gains vérifiés après toute retouche
- [ ] Un silence total posé sur le beat principal
- [ ] Master à −14 LUFS, crête ≤ −1,5 dBTP
- [ ] Transcription du master comparée au texte attendu (fidélité mot à mot)
