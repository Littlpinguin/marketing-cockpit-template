# Doctrine de narration : écrire pour l'oreille, diriger la voix

## Rôle de ce fichier

Chargé par `video-production`, `video-editing`, `video-documentary` et `video-repurpose` pour toute vidéo avec voix off, humaine ou de synthèse. Il règle le texte dit (structure, écriture, longueur), la direction de la voix, le mix et la divulgation. Les règles de coupe et de son du montage sont dans `montage.md`, les specs par plateforme dans `formats.md`. Pour le vocabulaire et le ton, `01-brand/voice.md` prime.

## Arc d'un explainer

Cinq temps, dans cet ordre :

1. **Accroche** : poser une tension ou une idée reçue, en une ou deux phrases. Quand le sujet s'y prête, ouvrir sur ce que la persona croit vrai et que la vidéo va corriger : la correction devient le fil de la vidéo.
2. **Mécanisme** : expliquer comment ça marche, pas à pas, une idée par plan. Chaque pas s'appuie sur le précédent.
3. **Preuve** : un chiffre sourcé (`01-brand/messaging-framework.md` ou une source citée) ou un cas réel. Une preuve forte vaut mieux que trois faibles.
4. **Conséquence** : ce que cela change pour la persona, dans ses mots à elle (`01-brand/personas.md`).
5. **Appel à l'action** : un seul, à la fin, formulé comme la suite logique de ce qui précède.

Enchaîner les temps par « mais » et « donc », jamais par « et puis » : chaque transition contredit ou déduit. Un script qui avance en « et puis » est une liste, pas une explication. Test : relire les débuts de paragraphes du script. S'ils peuvent changer d'ordre sans perte, l'arc manque.

Dans un format court, accroche, mécanisme et preuve se resserrent. Structure et durées sourcées du format court : `docs/etat-de-lart/video-courte.md`.

## Écrire pour l'oreille

Le spectateur ne peut pas revenir en arrière : une phrase mal comprise est perdue.

- Phrases courtes, une information par phrase. Le sujet et le verbe arrivent tôt.
- Un chiffre par phrase, arrondi pour l'oral (« près d'un tiers » plutôt que « 31,7 % »). L'arrondi reste fidèle à la source ; la valeur exacte et sa source vont à l'écran ou en légende.
- Ni parenthèse, ni incise longue : à l'oral, elles se perdent. Aucun sigle que la voix ne prononcera pas tel quel : l'écrire comme il se dit, ou le développer la première fois.
- Verbes concrets, sujets qui agissent, peu d'adjectifs.
- Répéter le mot clé plutôt que lui chercher des synonymes : à l'oral, un synonyme fait croire qu'on parle d'autre chose.
- Écrire nombres, unités et noms propres comme ils doivent se prononcer, surtout pour une voix de synthèse.
- Lire le script à voix haute, au débit réel, avant de le présenter à validation. Toute phrase sur laquelle on bute se réécrit.
- Vocabulaire interdit et tics de style IA : `01-brand/voice.md` et `01-brand/anti-ai-writing-style.md`. Premier contrôle : `python3 scripts/lint-brand.py <script.md>`.

## Calibrer la longueur

La durée vient du brief ; le nombre de mots en découle. Aucun débit standard n'est retenu ici : il varie avec la voix, la langue et le ton, donc il se mesure.

1. Choisir la voix (section suivante) et produire l'échantillon de 10 à 15 s.
2. Débit mesuré : mots de l'échantillon divisés par sa durée en secondes, pauses comprises.
3. Budget de mots : débit multiplié par la durée visée diminuée des marges. Les marges couvrent les respirations entre les temps, le silence posé sur le temps fort, un éventuel plan d'ouverture sans voix et la tenue du carton final. Exemple de calcul, avec des valeurs fictives : une voix mesurée à 2,5 mots par seconde, pour une vidéo de 40 s avec 6 s de marges, donne 2,5 × 34 = 85 mots.
4. Couper le texte jusqu'à tenir le budget, **avant** de générer la narration complète. Jamais accélérer la voix, ni au rendu de la synthèse ni au montage, pour faire entrer un texte trop long : la précipitation s'entend.
5. Après génération : durée de la narration inférieure ou égale à la durée de la vidéo, vérifiée au contrôle avant rendu de `video-production`.

## Direction de voix (TTS)

- **Une voix par projet.** Choisie au plus tard avec le script et consignée dans `decisions.md` : fournisseur, modèle, identifiant de voix, réglages. Changer de voix en cours de projet est une nouvelle décision, consignée, avec un nouvel échantillon.
- **Indications de jeu dans le script.** Pour chaque segment, une ligne de direction : l'intention (affirmer, intriguer, rassurer), l'énergie (posée, vive), les pauses (avant un retournement, après un chiffre) et le mot appuyé. Une indication vague (« naturel », « dynamique ») ne dirige rien : la remplacer par une pause, un mot appuyé, un rythme.
- **Échantillon d'abord.** Générer 10 à 15 s sur le passage le plus exigeant du script (le retournement, le chiffre clé), pas forcément le début. Un humain l'écoute et le valide avant toute génération complète. Cet échantillon sert aussi à mesurer le débit.
- **Régénérer un segment, pas tout.** La narration se produit par segments (un par temps du script ou par plan) : une phrase ratée se refait seule.
- **Prononciation.** Noms propres, nom de la marque, sigles et termes anglais se testent dans l'échantillon. Si la voix les écorche, écrire le passage phonétiquement pour elle, sans toucher au texte des sous-titres.
- **Fournisseurs.**
  - Magnific (MCP), outil `audio_tts` : payant, sous le contrat de coût de `video-production` (annonce, échantillon, `couts.md`).
  - HyperFrames : `npx hyperframes tts`. Sans précision, la commande peut prendre un fournisseur payant dont la clé est présente ; `--provider kokoro` force le moteur local et gratuit. Kokoro n'a qu'une voix française, `ff_siwis` ([liste des voix du modèle](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)), et sa phonétisation du français demande `espeak-ng` installé sur la machine (documentation TTS de la skill `hyperframes:media-use`). Exemple : `npx hyperframes tts narration.txt --provider kokoro --voice ff_siwis --output narration.wav`.
  - Tout fournisseur payant (Magnific, HeyGen ou ElevenLabs côté HyperFrames) : coût annoncé avant l'appel, jamais de bascule silencieuse d'un fournisseur à l'autre.

## Mix voix et musique

Ordre et cibles, cohérents avec `montage.md` (section « Son ») et `08-video/scripts/plateformes.toml` :

1. Voix débruitée d'abord, normalisée en dernier : jamais normaliser avant de débruiter. Une voix de synthèse n'a rien à débruiter mais passe par la même normalisation.
2. Musique : entrée après l'accroche, pas sous la première phrase. Instrumentale sous la voix, car des paroles chantées concurrencent le texte dit. Ducking net sous la voix, avec l'écart voix et musique de `montage.md`.
3. Au moins un silence sur le temps fort : la musique se retire et la phrase clé reste seule.
4. Master : −14 LUFS intégré, crête vraie inférieure ou égale à −1,5 dBTP.
5. Contrôle : `python3 08-video/scripts/qa-video.py <rendu> --plateforme <p>`. Le constat `loudness` signale un master hors cible ; le constat `silence` signale un trou de son de 1,5 s ou plus, à vérifier : silence voulu sur le temps fort, ou trou à combler.
6. Écoute finale sur le haut-parleur d'un téléphone : la voix doit y rester intelligible.

## Divulgation

- Voix de synthèse : déclarée selon `01-brand/divulgation-ia.md`, comme tout contenu généré.
- Voix clonée d'une personne réelle : seulement avec son accord écrit, pour cet usage précis, conservé avec le projet et cité dans `decisions.md`. Sans accord, pas de clone.
- Voix enregistrée d'une personne réelle (interview, face caméra) : son propos n'est jamais remplacé par une voix de synthèse ni monté pour lui faire dire autre chose. Le contrôle de fidélité du texte est décrit dans la skill `video-generation`.

## Check-list

- [ ] Arc complet : accroche, mécanisme, preuve sourcée, conséquence, un seul appel à l'action
- [ ] Transitions en « mais » ou « donc », aucun « et puis » entre deux temps
- [ ] Script lu à voix haute ; `lint-brand.py` propre sur le script
- [ ] Voix choisie et consignée dans `decisions.md` ; indications de jeu écrites pour chaque segment
- [ ] Échantillon de 10 à 15 s validé par un humain avant la génération complète ; débit mesuré
- [ ] Nombre de mots dans le budget calculé ; narration plus courte que la vidéo, sans accélération
- [ ] `qa-video.py` sans constat `loudness` ; chaque constat `silence` vérifié
- [ ] Voix de synthèse déclarée (`01-brand/divulgation-ia.md`) ; accord écrit pour toute voix clonée d'une personne réelle

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
