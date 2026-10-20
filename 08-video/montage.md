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

- **Voix d'abord** : débruiter avant tout traitement (jamais normaliser avant de débruiter), passe-haut ~85 Hz, normalisation en dernier. Cible master (contrôle : `ffmpeg -af ebur128`) : **−14 LUFS intégré** pour un export de plateforme (cible de `scripts/plateformes.toml`), **−16 LUFS** pour une vidéo lue sur le web hors plateforme (un site, un lecteur intégré), où −14 sonne trop fort. Crête vraie ≤ −1,5 dBTP dans tous les cas.
- **Musique composée en code, calée au mot près** : partition, choix des sons, effets et mixage s'écrivent en code dans `projets/<slug>/musique/`, calés sur la ligne de temps de la voix : une retombée sur le mot choisi, un arrêt sur un temps fort. Une piste toute faite ou une musique générée par IA n'entre qu'à la demande de l'humain (`video-production` § « Contrat de coût »).
- **De la matière enregistrée sous la partition** : une musique de purs oscillateurs sonne pauvre et se ressemble d'un film à l'autre. Mélanger des instruments enregistrés sous licence CC0 (par exemple VCSL : claviers, percussions, carillons), des synthés de production joués en code (Surge XT par ses liaisons Python, surgepy) et des sons d'interface réels (uisfx, Kenney). Les prises enregistrées apportent l'attaque, la variation et la salle. Les outils s'installent une fois, hors du dépôt : un environnement Python dédié (pedalboard, DawDreamer, mido, pyloudnorm, librosa), Surge XT compilé avec ses liaisons Python, les banques téléchargées une seule fois et ignorées par Git.
- **Une idée sonore propre au film**, tirée de son objet : par exemple, chacun des outils d'un « mur d'outils » a sa vraie notification, désaccordée quand les outils tombent en vrac, accordée sur la gamme quand ils se rangent. Le son raconte la même chose que l'image.
- **Musique sous la voix** : entrée fondue après l'accroche, environ 12 dB sous la voix pendant la parole et 6 à 8 dB dans les respirations ; le registre de la voix se creuse légèrement dans la musique pendant la parole. **Au moins un silence total** posé sur le moment le plus fort : le moment le plus puissant d'un plan sonore est un silence, pas un effet.
- **Bruitages attachés aux gestes, en couches, ≥ 6 dB sous la voix** : une prise enregistrée (accordée à la tonalité quand elle sonne), un corps synthétisé dessous, des prises qui alternent pour qu'aucune répétition ne s'entende. Un bruitage par geste prévu au storyboard ; 5 au plus si le storyboard n'en prévoit pas (impacts sur les mots durs, ticks discrets sur les cartons, 2 frames avant l'apparition). Un son se télécharge dans le dossier du projet, jamais lu depuis une URL au rendu.
- **Une seule feuille de repères pour le son et l'image** : un script date chaque geste (pas, chocs, clics, envols) et écrit un fichier que lisent à la fois les bruitages et la construction HyperFrames. L'image se cale sur ces temps : une marche pose un pied sur chaque pas entendu et avance du pas dessiné de son personnage, pour que les pieds ne glissent pas. Si une animation impose un autre temps, on corrige le repère et on refait le son, jamais l'inverse.
- **Esquisse, puis son validé avant la construction** : l'humain écoute une esquisse sous la voix montée ; la construction commence sur un son validé.
- **Licences** : pedalboard, DawDreamer et Surge XT sont sous GPL-3. Le son rendu n'est pas couvert, mais un script qui les importe ne se publie pas dans un dépôt sous licence MIT : ces scripts restent dans le dépôt privé du projet. Les banques citées sont sous CC0. Chaque film a son `credits.md`.
- **J-cut sonore** : whoosh ou riser posé quelques frames **avant** la coupe image, jamais dessus.
- Après toute réparation/repose d'un clip SFX, **reposer son gain** — un effet recréé revient à plein volume et traverse tous les contrôles.

## Sous-titres et cartons

- Karaoké mot à mot : skill `captions`, section « Karaoké mot à mot » (timings au mot).
- Cartons : peu, courts (~2 s), un style unique (pastille de marque, police du style-guide), calés sur le mot qu'ils illustrent.

## Démo produit et capture d'écran

Pour toute vidéo qui montre un logiciel, une application ou un site en fonctionnement : démo, tutoriel, vidéo de lancement.

**Capture.**

- Enregistrer à la résolution native de l'écran : plus la capture dépasse la toile de sortie, plus on peut zoomer avant que le texte devienne flou.
- Couper les notifications, fermer les fenêtres et onglets sans rapport, masquer favoris et barres personnelles.
- Données fictives ou anonymisées uniquement : un compte de démonstration, jamais l'espace d'un vrai client (noms, courriels, montants, adresses). Ce qui aurait échappé à la capture se floute au montage, sur toute la durée où c'est visible.
- Agrandir le curseur dans les réglages du système avant d'enregistrer.

**Montage.**

- Une action par plan : un clic, une saisie, un résultat.
- Zoomer sur la zone d'action au moment où elle se produit, puis revenir au plan large, pour qu'on sache toujours où l'on est dans l'écran. Pas de zoom décoratif.
- Annotations sobres aux couleurs de la marque (variables de `brand.css`) : une seule à la fois, qui pointe l'élément concerné et disparaît une fois l'action faite.
- Temps morts (chargement, saisie longue, installation) : les accélérer, avec un repère discret si besoin, plutôt que couper sec au milieu d'une interaction, ce qui fait sauter l'écran sans explication. L'accélération s'arrête quand le résultat apparaît.
- Mouvement du curseur lissé, sans tremblement.
- Tenir chaque écran le temps de le lire (même règle que les cartons, `formats.md` § « Texte à l'écran »).

**Recadrage par format.**

- 16:9 : l'écran entier tient dans la toile.
- 9:16 et 1:1 : recadrer sur la zone utile de chaque plan plutôt que réduire l'écran entier, illisible sur un téléphone.
- Si un écran reste illisible une fois recadré en vertical, le signaler au storyboard et proposer à l'humain soit une version 16:9 seule, soit une version verticale qui montre moins d'écrans.

**Habillage.** Titres, chiffres, annotations animées et plan de fin passent par la skill `motion-design`. Pour une démo marketing tirée d'un site ou d'une application, la filière est `hyperframes:product-launch-video` (choix de filière dans `video-production`).

## Check-list mesurable avant export

- [ ] Médiane des plans entre 2,0 et 2,5 s ; 2-3 tenues ≥ 4 s aux beats
- [ ] Aucun écart > 4 s sans rupture ; raccords d'échelle ≥ 20 %
- [ ] Zéro effet de transition hors ouverture/fermeture
- [ ] Punch-in continu sur tous les plans fixes
- [ ] Musique et bruitages composés en code sur de la matière enregistrée (piste toute faite ou génération seulement à la demande de l'humain) ; esquisse, puis son validé avant la construction
- [ ] Bruitages calés sur les gestes et la feuille de repères, ≥ 6 dB sous la voix (5 au plus si le storyboard n'en prévoit pas), gains vérifiés après toute retouche
- [ ] Un silence total posé sur le beat principal
- [ ] Master à −14 LUFS pour une plateforme, −16 LUFS pour le web hors plateforme, crête ≤ −1,5 dBTP
- [ ] Transcription du master comparée au texte attendu (fidélité mot à mot)
- [ ] Démo produit : aucune donnée réelle de client à l'écran

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
