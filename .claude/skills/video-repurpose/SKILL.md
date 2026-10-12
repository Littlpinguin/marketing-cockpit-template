---
name: video-repurpose
description: Transforme une vidéo longue de {{COMPANY_NAME}} (webinar, podcast filmé, interview, live, conférence) en clips sociaux. Transcription horodatée au mot, repérage des candidats, notation sur cinq critères, test « se comprend sans contexte », validation humaine de la liste avant tout montage, coupe au mot, recadrage 9:16 et 1:1, sous-titres et habillage, QA par clip avec qa-video.py, une entrée de calendrier par clip. Appelée par video-production ; le montage passe par video-editing, les sous-titres par captions. Ne publie pas, n'écrit pas les posts d'accompagnement, ne fait jamais dire à quelqu'un ce qu'il n'a pas dit.
---

# video-repurpose : d'une vidéo longue à des clips sociaux

Une vidéo longue contient des moments qui tiennent seuls. Cette skill les trouve, les note, les fait valider, puis les fait monter un par un pour la plateforme visée. Elle est appelée par `video-production`, qui a ouvert le projet (`08-video/projets/<slug>/`), écrit le brief et tient le budget.

## Références à charger

- `08-video/formats.md` : durées, toiles, zones de sécurité, sous-titres, repères du format court.
- `08-video/montage.md` : coupe au mot, respirations, son.
- `08-video/narration.md` : seulement si un carton ou une voix d'introduction s'ajoute au propos d'origine.
- `02-strategy/calendar/calendar.md` et `_templates/inventory.md` : ce qui est prévu, ce qui a déjà été publié.
- `01-brand/voice.md`, `01-brand/droits.md`, `01-brand/divulgation-ia.md`.

## Avant de couper : droits et source

- **Droits.** Accord des personnes filmées pour une réutilisation en clips, invités compris : vérifier que l'accord donné pour l'événement couvre des extraits diffusés sur les réseaux, et le noter dans `decisions.md`. Sans accord établi, s'arrêter et le dire.
- **Nature de la source.** Vidéo ou audio seul ; une personne, un entretien ou une table ronde ; qualité du son. Une source audio seule donne des clips sans visage à recadrer : visuel de marque animé par `motion-design` et sous-titres. Un son médiocre se nettoie avant la transcription.
- **Rangement.** La source dans `rushes/`, la notation dans `candidats.md`, les extraits de texte des clips dans `clips/`, les rendus dans `exports/`.

## Étape 1 : transcription horodatée au mot

```bash
ffmpeg -i rushes/source.mp4 -vn -ac 1 -ar 16000 rushes/source.wav
whisper-cli -m <modèle> -f rushes/source.wav -l fr -oj -ml 1 -sow -of rushes/transcription
```

- `-ml 1 -sow` : un mot par segment, avec son début et sa fin en millisecondes, dans `rushes/transcription.json`. `<modèle>` est le chemin déclaré dans `.env` (`WHISPER_MODEL`).
- Autre voie : `npx hyperframes transcribe rushes/source.mp4`, la transcription au mot d'HyperFrames (par le lanceur du plugin quand HyperFrames est installé en plugin).
- whisper n'identifie pas les intervenants : sur un entretien ou une table ronde, vérifier à l'écoute qui dit quoi avant d'attribuer une phrase.
- Les vrais silences, que la transcription aligne bord à bord : `ffmpeg -i rushes/source.wav -af silencedetect=noise=-30dB:d=0.3 -f null -`.

## Étape 2 : repérer les candidats

- **Unités de sens de 20 à 90 s** : une idée complète, avec son entrée et sa chute. Fourchette de travail, à resserrer selon la plateforme visée (`08-video/formats.md`).
- Moments à chercher : une idée dite simplement, une affirmation qui surprend, un conseil applicable, une histoire courte, un désaccord, une formule qui reste.
- Couvrir toute la source, pas seulement la première demi-heure ; varier les intervenants et les sujets.
- Noter chaque candidat dans `candidats.md` : numéro, début et fin, intervenant, première et dernière phrase, sujet.

## Étape 3 : noter

Cinq critères, chacun de 1 à 5 :

1. **Accroche** : les trois premières secondes du clip, seules, donnent-elles envie de rester ?
2. **Autonomie** : le clip se comprend-il sans le reste de la vidéo (test ci-dessous) ?
3. **Valeur pour la persona** : apprend-elle, gagne-t-elle quelque chose (`01-brand/personas.md`) ?
4. **Énergie** : voix, rythme, conviction.
5. **Adéquation à la plateforme** : durée, ton et sujet conformes à la plateforme visée.

Tableau de notation type, dans `candidats.md` (valeurs d'exemple) :

| # | Début | Fin | Durée | Cible | Accroche | Autonomie | Valeur | Énergie | Plateforme | Total | Décision |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 00:12:04 | 00:12:51 | 47 s | LinkedIn | 4 | 5 | 4 | 3 | 4 | 20 | retenu |
| 2 | 00:31:10 | 00:32:20 | 70 s | LinkedIn | 2 | 1 | 4 | 4 | 3 | 14 | écarté : commence par « donc », renvoie à la démo |
| 3 | 00:44:30 | 00:45:02 | 32 s | Reels | 5 | 4 | 3 | 5 | 5 | 22 | retenu |

Le total classe, il ne décide pas seul : un clip noté 1 en autonomie est écarté quel que soit son total. Classer par qualité, pas par ordre d'apparition, et écarter franchement les candidats faibles plutôt que de remplir un quota.

### Test « se comprend sans contexte »

Lire la transcription du clip seule, comme quelqu'un qui n'a pas vu la vidéo :

- renvoie-t-elle à un passage antérieur (« comme on l'a vu », « sur ce slide », « pour répondre à ta question ») ?
- commence-t-elle par un connecteur (« donc », « et », « du coup », « comme je disais ») ?
- contient-elle un pronom dont on ne sait pas ce qu'il désigne (« il », « ça », « ce truc ») ?
- s'arrête-t-elle avant la chute ?

Une réponse oui : élargir le clip (reprendre la phrase d'avant), couper ailleurs, ajouter un carton de contexte d'une ligne, ou écarter. Un carton situe, il ne fait pas dire.

**Validation humaine de la liste avant tout montage.** Présenter les clips retenus (numéro, plateforme, durée, première phrase, note) et les écartés notables avec leur raison, puis attendre. Rien n'est coupé avant l'accord. La liste validée devient le `script.md` du projet (une ligne par clip : numéro, début, fin, plateforme, première phrase), ce qui l'inscrit à l'inventaire à la livraison.

## Étape 4 : couper au mot

- Entrée et sortie de chaque clip sur les horodatages des mots (`rushes/transcription.json`), ajustées sur les vrais silences.
- Respirations resserrées sans être supprimées ; hésitations et redites retirées seulement quand le sens ne change pas (`08-video/montage.md`).
- Jamais de coupe qui change le sens : le clip dit ce que la personne a dit, dans l'ordre où elle l'a dit.
- Écrire le texte du clip coupé dans `clips/clip-<nn>.txt` : il sert à la QA.

## Étape 5 : recadrer

16:9 vers 9:16, recadrage centré :

```bash
ffmpeg -i clip-03.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:v libx264 -pix_fmt yuv420p -c:a aac clip-03-9x16.mp4
```

- Sujet décentré : `crop=ih*9/16:ih:<x>:0`, avec `<x>` le bord gauche de la zone gardée, en pixels de la source.
- Intervenant qui se déplace, ou plusieurs intervenants : recadrage suivi, plan par plan. Découper le clip à chaque changement de plan ou de personne qui parle, choisir le cadre de chaque morceau ; l'assemblage se fait au montage.
- 1:1 : `crop=ih:ih,scale=1080:1080`.
- Netteté : depuis une source 1080p, un recadrage 9:16 garde une bande d'environ 608 px de large (1080 × 9/16), agrandie à 1080 px, donc plus douce. Préférer une source 4K quand elle existe.

## Étape 6 : sous-titres et habillage

- Sous-titres incrustés sur chaque clip, par la skill `captions` (vitesse de lecture et zones de sécurité : `08-video/formats.md`).
- Habillage par la skill `motion-design` : lower-third au nom et à la fonction de l'intervenant à sa première apparition (rôles `title` et `label` de `frame.md`), carton de contexte s'il a été validé, plan de fin avec un seul appel à l'action.
- Nom et fonction écrits comme la personne les a validés.

## Étape 7 : monter

Assemblage par la skill `video-editing` : coupes, recadrage, sous-titres, habillage, son au niveau de `08-video/montage.md`. Un fichier par clip et par plateforme : `exports/<slug>-clip-<nn>-<plateforme>.mp4`.

## Étape 8 : QA par clip

```bash
python3 08-video/scripts/qa-video.py 08-video/projets/<slug>/exports/<slug>-clip-03-linkedin.mp4 \
  --plateforme linkedin --duree 47 --script 08-video/projets/<slug>/clips/clip-03.txt
```

- `--script` avec le texte du clip : la couverture de la transcription signale une coupe qui a avalé une phrase.
- Puis l'agent `video-reviewer` sur chaque clip, et deux tours de correction au plus, comme dans `video-production`.

## Étape 9 : calendrier

- Une entrée par clip dans `02-strategy/calendar/calendar.md` : plateforme, date visée, statut, vidéo source.
- Espacer les publications selon la cadence du canal, et intercaler d'autres contenus : une série de clips ne se publie pas d'un bloc.
- Anti-répétition : vérifier dans le calendrier et `_templates/inventory.md` qu'un sujet n'a pas déjà été publié récemment, et ne pas publier deux clips sur la même idée la même semaine.

## Ce que cette skill ne fait pas

- Publier : décision humaine.
- Écrire les posts qui accompagnent les clips : `social-content`.
- Faire dire à quelqu'un ce qu'il n'a pas dit : pas de voix de synthèse sur son propos, pas de coupe qui en change le sens.
- Monter ou sous-titrer elle-même : `video-editing` et `captions`.

---

Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : aucun texte ni code repris. Registre : docs/vendored-video.md.
