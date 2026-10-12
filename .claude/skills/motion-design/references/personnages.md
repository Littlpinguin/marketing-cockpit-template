# Référence personnages : de la fiche au mouvement

Chargée par `motion-design` quand une vidéo met en scène un personnage. Doctrine courte dans `08-video/motion.md` § « Personnages ». Méthode en quatre temps : fiche personnage, plan de rig, bibliothèque de poses, timeline d'actions ; puis la technique de rendu.

## Quand un personnage aide

- La vidéo raconte : quelqu'un vit le problème, essaie, trouve. Le spectateur suit une personne plutôt qu'un schéma.
- La marque a une mascotte, ou en veut une (décision de marque, consignée dans `01-brand/`).
- Un geste humain dit le message mieux qu'un texte : montrer, pointer, hésiter, se réjouir.

Il n'aide pas quand il est ajouté pour « humaniser » un sujet qui n'en a pas besoin, ni quand il occupe l'écran pendant que le texte fait tout le travail.

Commencer avec un seul personnage ; un second seulement si l'histoire repose sur un échange entre deux.

## Fiche personnage

Écrite avant tout dessin, validée avec le concept :

- **Silhouette** : reconnaissable en ombre chinoise, sans détail intérieur.
- **Proportions** : rapport tête et corps, longueur des membres, carrure. Elles ne changent plus ensuite.
- **Palette** : uniquement les couleurs de la marque, par les variables de `brand.css`, et la façon dont elles se répartissent (peau ou corps, vêtement, accessoire, contour).
- **Expressions** : celles que le script appelle, plan par plan (par exemple neutre, perplexe, satisfait).
- **Vues** : commencer par une seule (face, trois quarts ou profil) ; en ajouter une quand un plan l'exige.
- **Accessoires** : ce qu'il porte ou tient, attachés à une partie du corps.
- **Ce qu'il ne fait jamais** : gestes, attitudes, situations exclues (ce qui trahirait le ton de la marque).

## Plan de rig

Le rig décrit comment le personnage bouge :

- **Parties** : le personnage découpé en éléments qui bougent indépendamment, de la tête aux accessoires.
- **Pivots** : pour chaque partie mobile, le point autour duquel elle tourne (épaule, coude, cou, hanche).
- **Ordre des calques** : ce qui passe devant quoi (le bras du fond derrière le corps, celui de devant par-dessus).
- **Butées** : l'angle maximal de chaque articulation, noté dans la fiche.

## Bibliothèque de poses

- Des poses nommées (`debout`, `pointe-droite`, `hausse-epaules`…), chacune décrite par l'état des parties qui changent.
- La liste des poses se tire du storyboard, plan par plan, et s'arrête là.

## Timeline d'actions

Les actions se calent sur les temps forts du script, pas l'inverse :

1. Relever dans la transcription de la narration l'instant de chaque mot qui déclenche une action (le chiffre, le « mais », la conclusion).
2. Placer l'anticipation juste avant ce mot, l'action dessus, le retour au calme après.
3. Entre deux actions, une pose tenue ou un cycle d'attente, jamais une immobilité totale prolongée sur un personnage censé vivre.

## Techniques

- **Lottie**, par l'adaptateur Lottie d'HyperFrames (skill `hyperframes:hyperframes-animation`, `adapters/lottie.md`). Le personnage est animé dans After Effects et exporté en JSON Lottie, ou fourni par un animateur. Fichier local dans `assets/`, lecture jamais automatique (`autoplay: false`), boucle déclarée explicitement (`loop`), chaque animation enregistrée sur `window.__hfLottie`. HyperFrames lit toutes les animations Lottie sur le temps de la composition, sans décalage de départ propre à chacune : une action qui commence à 4 s commence à 4 s dans le fichier, donc toute la performance d'un personnage tient dans un seul fichier. Le décor et les textes autour se posent sur la timeline GSAP. Exemple fonctionnel dans le registre : `npx hyperframes add lottie-character-walk`.
- **Marionnette SVG articulée**. Un groupe `<g>` par partie du rig, imbriqués comme le squelette (l'avant-bras dans le bras), le pivot réglé avec `transformOrigin` (ou `svgOrigin`, en coordonnées du SVG) de GSAP. Une pose est un jeu d'angles ; passer d'une pose à l'autre, c'est animer ces angles sur la timeline en pause. Couleurs par les variables de `brand.css`, aucune `transform` CSS de départ sur ce que GSAP anime.
- **Silhouette à l'encre**, avec `ink-puppet` (`08-video/lib/ink-theater/ink-puppet.js`) : un bonhomme en traits d'encre, animé par des clips de capture de mouvement réels. Le mouvement vient des clips de `InkClips`, ou d'un clip ajouté avec `bvh2clip.py` ; la composition règle la position, l'échelle et l'enchaînement. Voir `references/encre.md`.

## Limites

- Pas de synchronisation labiale dessinée image par image. Un personnage qui parle à l'écran se limite à deux ou trois formes de bouche basculées sur les syllabes appuyées ; sinon, la voix est off et le personnage réagit.
- Pas de visage réaliste généré pour un personnage dessiné : le style reste celui de la fiche.

## Droits

- Personnage inspiré d'une personne réelle (dirigeant, salarié, client) : accord écrit de la personne, conservé avec le projet et cité dans `decisions.md`.
- Mascotte existante ou personnage fourni par un tiers : droits d'usage vérifiés dans `01-brand/droits.md`.
- Jamais un personnage repris d'une autre marque, d'une série ou d'un site.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
