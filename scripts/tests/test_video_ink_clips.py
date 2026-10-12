"""Tests des livrables d'ink-theater : clips, catalogue, bundle, police, notices, exemple."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOSSIER = REPO / "08-video" / "lib" / "ink-theater"
CLIPS = DOSSIER / "clips"
ATTENDUS = {"marche": "02_01", "course": "09_01", "saut": "13_11", "salut": "111_37",
            "assis": "143_18", "danse": "05_02", "coup-de-pied": "10_01"}


def test_clips_et_catalogue_concordent():
    catalogue = json.loads((CLIPS / "catalogue.json").read_text(encoding="utf-8"))
    noms = {c["nom"] for c in catalogue["clips"]}
    assert noms == set(ATTENDUS)
    for entree in catalogue["clips"]:
        clip = json.loads((CLIPS / entree["fichier"]).read_text(encoding="utf-8"))
        assert clip["source"] == f"CMU {ATTENDUS[clip['nom']]}"
        assert len(clip["images"]) == entree["images"] >= 30
        assert 0 < entree["duree"] <= 6.1


@pytest.mark.skipif(shutil.which("node") is None, reason="node absent")
def test_clips_valides_par_le_moteur():
    code = (f"const P = require({json.dumps((DOSSIER / 'ink-puppet.js').as_posix())});"
            f"const C = require({json.dumps((CLIPS / 'clips.js').as_posix())});"
            "for (const [n, c] of Object.entries(C)) P.valider(c);"
            "console.log(JSON.stringify(Object.keys(C).sort()));")
    res = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert json.loads(res.stdout) == sorted(ATTENDUS)


def test_premiere_image_n_est_pas_une_pose_de_reference():
    """La base CMU commence parfois par une pose en T : bras à l'horizontale, écartés."""
    for nom in ATTENDUS:
        clip = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))
        i = {a: k for k, a in enumerate(clip["articulations"])}
        image = clip["images"][0]
        bras_g = abs(image[i["main_g"]][1] - image[i["epaule_g"]][1]) < 0.04 and \
            abs(image[i["main_g"]][0] - image[i["epaule_g"]][0]) > 0.25
        bras_d = abs(image[i["main_d"]][1] - image[i["epaule_d"]][1]) < 0.04 and \
            abs(image[i["main_d"]][0] - image[i["epaule_d"]][0]) > 0.25
        assert not (bras_g and bras_d), f"{nom} commence par une pose en T : relancer avec --debut"


def test_pas_de_saut_brusque_entre_les_deux_premieres_images():
    """La première image d'un BVH CMU est une pose de calibration (bras écartés, parfois un peu
    sous l'horizontale, ou invisibles de profil) : si elle reste dans le clip, la pose saute dès
    l'image suivante. Au rythme normal des clips, une articulation bouge de moins de 0,11 d'une
    image à l'autre ; la pose de calibration provoque des sauts de 0,26 à 0,50."""
    for nom in ATTENDUS:
        images = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))["images"]
        ecart = max(abs(a - b) for pa, pb in zip(images[0], images[1]) for a, b in zip(pa, pb))
        assert ecart < 0.15, f"{nom} : saut de {ecart:.2f} entre l'image 0 et l'image 1, relancer avec --debut 0.1"


def test_marche_boucle_sans_couture():
    """La marche sert de base en boucle : sa fenêtre est un cycle de pas complet, la dernière
    image rejoint la première sans saut (au plus un pas de 0,1)."""
    images = json.loads((CLIPS / "marche.json").read_text(encoding="utf-8"))["images"]
    couture = max(abs(a - b) for pa, pb in zip(images[-1], images[0]) for a, b in zip(pa, pb))
    assert couture < 0.1, f"saut de {couture:.2f} entre la dernière et la première image"


def test_police_et_notices():
    police = DOSSIER / "fonts" / "PatrickHand-Regular.ttf"
    assert police.exists() and police.stat().st_size > 10_000
    assert "SIL OPEN FONT LICENSE" in (DOSSIER / "fonts" / "OFL.txt").read_text(encoding="utf-8").upper()
    notices = (DOSSIER / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "mocap.cs.cmu.edu" in notices and "Patrick Hand" in notices
    for trial in ATTENDUS.values():
        assert trial in notices


def test_readme_documente_l_api():
    readme = (DOSSIER / "README.md").read_text(encoding="utf-8")
    for terme in ("InkTheater.attach", "drawPath", "writeText", "paper", "InkPuppet.create",
                  "InkClips", "bvh2clip.py", "hf-seek", "ink/"):
        assert terme in readme, terme


def test_composition_d_exemple():
    html = (DOSSIER / "examples" / "demo" / "index.html").read_text(encoding="utf-8")
    for attendu in ('data-composition-id="ink-demo"', 'data-width="1080"', 'data-height="1920"',
                    'data-duration="6"', 'window.__timelines["ink-demo"]', "ink/ink-theater.js",
                    "ink/ink-puppet.js", "ink/clips/clips.js", "InkTheater.attach", "document.fonts.ready"):
        assert attendu in html, attendu
    assert "Math.random" not in html and "Date.now" not in html
