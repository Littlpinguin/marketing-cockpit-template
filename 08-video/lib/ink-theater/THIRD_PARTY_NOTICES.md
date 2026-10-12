# Third-party notices

The drawing engine in this folder (`ink-theater.js`, `ink-puppet.js`) is original work, released under the MIT licence of this repository (see the `LICENSE` file at the repository root).

Two kinds of third-party material ship alongside it: a handwriting font and a set of motion clips derived from a public motion capture database. Their licences are summarised below. Anyone who copies this folder into a project (under `ink/`) must keep this file and `fonts/OFL.txt` with it.

## Patrick Hand (handwriting font)

- Files: `fonts/PatrickHand-Regular.ttf`, licence text in `fonts/OFL.txt`.
- Copyright: Copyright (c) 2010-2012 Patrick Wagesreiter (mail@patrickwagesreiter.at)
- Licence: SIL Open Font License, Version 1.1. The full text is in `fonts/OFL.txt`, and at http://scripts.sil.org/OFL.
- In practice: the font may be used in any project, commercial work included, and may be embedded in a video, a PDF or a web page and redistributed with it. It may not be sold on its own. A modified version must carry another name if the licence reserves one, and must stay under the same licence. Keep `fonts/OFL.txt` next to the font file whenever the font is redistributed.
- Obtained from the Google Fonts repository (`ofl/patrickhand`).

## Motion capture clips

- Files: `clips/*.json` (one file per clip), `clips/catalogue.json` and `clips/clips.js` (the bundle that loads every clip).
- Origin: the clips are 2D silhouettes derived, by `08-video/scripts/bvh2clip.py`, from BVH files of the CMU Graphics Lab Motion Capture Database (http://mocap.cs.cmu.edu). The BVH files were fetched from the public BVH mirror `una-dinosauria/cmu-mocap` on GitHub. Only the positions of 13 joints, projected on a plane and normalised, are kept in each clip; the BVH files themselves are not part of this repository.
- Licence: the database is free for all uses, commercial ones included. The CMU asks for the following citation, which must be kept wherever the clips are redistributed:

  > The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.

- The `source` field written inside each clip names the CMU trial and the `licence` field states the terms of the database (free for all uses). The citation above is not repeated in the clips: it is kept in this notices file.

| Clip | CMU trial | Description in the CMU index |
|---|---|---|
| `marche` | 02_01 | walk |
| `course` | 09_01 | run |
| `saut` | 13_11 | forward jump |
| `salut` | 111_37 | wave |
| `assis` | 143_18 | sit down and get up |
| `danse` | 05_02 | dance, expressive arms, pirouette |
| `coup-de-pied` | 10_01 | soccer, kick ball |

A clip added later with `bvh2clip.py` must be added to this table with its own source and licence.
