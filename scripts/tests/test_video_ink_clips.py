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


def _est_une_pose_de_reference(clip):
    """Pose de calibration de la base CMU : les deux mains à hauteur d'épaule (à 0,08 près ; elle
    mesure 0,04 à 0,05 sous l'épaule) et, pour un clip frontal, écartées de plus de 0,25 des épaules.
    De profil (plan sagittal), les bras en T se superposent : l'écart horizontal ne peut jamais
    dépasser 0,25, seule la hauteur compte."""
    i = {a: k for k, a in enumerate(clip["articulations"])}
    image = clip["images"][0]
    frontal = clip["plan"] == "frontal"

    def bras(main, epaule):
        a_hauteur = abs(image[i[main]][1] - image[i[epaule]][1]) < 0.08
        ecarte = abs(image[i[main]][0] - image[i[epaule]][0]) > 0.25
        return a_hauteur and (ecarte or not frontal)

    return bras("main_g", "epaule_g") and bras("main_d", "epaule_d")


def test_premiere_image_n_est_pas_une_pose_de_reference():
    """La base CMU commence parfois par une pose en T : bras à l'horizontale, écartés."""
    for nom in ATTENDUS:
        clip = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))
        assert not _est_une_pose_de_reference(clip), f"{nom} commence par une pose en T : relancer avec --debut"


def test_detection_de_la_pose_de_reference():
    """Le détecteur voit la vraie pose de calibration (mesurée sur les BVH convertis avec --debut 0 :
    mains à 0,04 ou 0,05 sous l'épaule, écartées de 0,31 à 0,37 en frontal, superposées de profil)
    et ne se trompe pas sur une première image de mouvement."""
    for nom, plan in (("salut", "frontal"), ("marche", "sagittal")):
        clip = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))
        assert clip["plan"] == plan and not _est_une_pose_de_reference(clip)
        i = {a: k for k, a in enumerate(clip["articulations"])}
        image = clip["images"][0]
        for cote, signe in (("g", 1), ("d", -1)):
            epaule = image[i[f"epaule_{cote}"]]
            image[i[f"main_{cote}"]] = [epaule[0] + (signe * 0.36 if plan == "frontal" else 0.0), epaule[1] - 0.05]
        assert _est_une_pose_de_reference(clip), f"pose en T {plan} non détectée"


def test_pas_de_saut_brusque_entre_les_deux_premieres_images():
    """La première image d'un BVH CMU est une pose de calibration (bras écartés, parfois un peu
    sous l'horizontale, ou invisibles de profil) : si elle reste dans le clip, la pose saute dès
    l'image suivante. Au rythme normal des clips, une articulation bouge de moins de 0,11 d'une
    image à l'autre ; la pose de calibration provoque des sauts de 0,26 à 0,50."""
    for nom in ATTENDUS:
        images = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))["images"]
        ecart = max(abs(a - b) for pa, pb in zip(images[0], images[1]) for a, b in zip(pa, pb))
        assert ecart < 0.15, f"{nom} : saut de {ecart:.2f} entre l'image 0 et l'image 1, relancer avec --debut 0.1"


def _couture(nom):
    """(écart entre la dernière et la première image, plus grand pas entre deux images voisines)."""
    images = json.loads((CLIPS / f"{nom}.json").read_text(encoding="utf-8"))["images"]

    def ecart(p, q):
        return max(abs(a - b) for pa, pb in zip(p, q) for a, b in zip(pa, pb))

    return ecart(images[-1], images[0]), max(ecart(p, q) for p, q in zip(images, images[1:]))


def test_marche_boucle_sans_couture():
    """La marche sert de base en boucle : sa fenêtre est un cycle de pas complet, la dernière
    image rejoint la première sans saut (au plus un pas de 0,1, et pas plus de deux fois le plus
    grand pas du clip)."""
    couture, pas = _couture("marche")
    assert couture < 0.1 and couture <= 2 * pas, f"saut de {couture:.2f} entre la dernière et la première image"


def test_course_boucle_sans_couture():
    """La course est enregistrée à 60 i/s sur exactement un cycle de deux pas (45 images, 0,75 s) :
    le fichier CMU ne dure que 1,2 s, un cycle à 30 i/s n'atteindrait pas les 30 images exigées.
    Même critère que la marche."""
    clip = json.loads((CLIPS / "course.json").read_text(encoding="utf-8"))
    assert clip["fps"] == 60
    couture, pas = _couture("course")
    assert couture < 0.1 and couture <= 2 * pas, f"saut de {couture:.2f} entre la dernière et la première image"


def _energie_moyenne(images):
    """Déplacement moyen d'une articulation d'une image à la suivante (|dx| + |dy|, en hauteurs de corps)."""
    return sum(sum(abs(a - b) for pa, pb in zip(p, q) for a, b in zip(pa, pb)) / len(p)
               for p, q in zip(images, images[1:])) / (len(images) - 1)


def _part_inactive(images, seuil=0.003):
    pas = [sum(abs(a - b) for pa, pb in zip(p, q) for a, b in zip(pa, pb)) / len(p)
           for p, q in zip(images, images[1:])]
    return sum(1 for x in pas if x < seuil) / len(pas)


def test_coup_de_pied_contient_le_coup_de_pied():
    """Dans CMU 10_01 les pieds restent au sol jusqu'à 4,2 s environ : une fenêtre qui démarre
    plus tôt ne contient que de l'attente. Dans le clip, un pied doit monter de plus de 0,15 au-dessus
    de sa hauteur de la première image (mesuré : 0,27 ; 0,02 sur les trois premières secondes du fichier)."""
    clip = json.loads((CLIPS / "coup-de-pied.json").read_text(encoding="utf-8"))
    i = {a: k for k, a in enumerate(clip["articulations"])}
    images = clip["images"]
    montee = max(im[i[pied]][1] - images[0][i[pied]][1] for im in images for pied in ("pied_g", "pied_d"))
    assert montee > 0.15, f"aucun pied ne monte : {montee:.2f}"


def test_danse_contient_la_danse():
    """CMU 05_02 reste immobile pendant les trois premières secondes (énergie de pose mesurée :
    0,0011 à 0,0014 par image sur les deux premières secondes). Une fenêtre de six secondes qui
    démarre à 0,1 s donne une énergie moyenne de 0,0094 et 42 % d'images inactives (énergie sous
    0,003) ; la fenêtre livrée (2,9 s à 8,9 s) donne 0,0130 et 6 %. Seuils : énergie moyenne
    au-dessus de 0,011 et moins de 20 % d'images inactives."""
    images = json.loads((CLIPS / "danse.json").read_text(encoding="utf-8"))["images"]
    assert _energie_moyenne(images) > 0.011
    assert _part_inactive(images) < 0.20


def test_police_et_notices():
    police = DOSSIER / "fonts" / "PatrickHand-Regular.ttf"
    assert police.exists() and police.stat().st_size > 10_000
    ofl = (DOSSIER / "fonts" / "OFL.txt").read_text(encoding="utf-8")
    assert "SIL OPEN FONT LICENSE" in ofl.upper()
    notices = (DOSSIER / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "mocap.cs.cmu.edu" in notices and "Patrick Hand" in notices
    # La ligne de copyright des notices est celle de l'OFL.txt, mot pour mot.
    copyright_ofl = ofl.splitlines()[0]
    assert copyright_ofl.startswith("Copyright (c)") and copyright_ofl in notices
    # Citation demandée par la CMU, en entier.
    assert ("The data used in this project was obtained from mocap.cs.cmu.edu. "
            "The database was created with funding from NSF EIA-0196217.") in notices
    # Chaque clip et son essai sur la même ligne du tableau.
    lignes = notices.splitlines()
    for nom, essai in ATTENDUS.items():
        ligne = next((l for l in lignes if l.startswith(f"| `{nom}` |")), None)
        assert ligne is not None, f"{nom} absent du tableau des notices"
        assert f"| {essai} |" in ligne, f"{nom} : essai {essai} attendu sur sa ligne, trouvé {ligne}"


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
    # La timeline n'est enregistrée qu'à la fin de la construction : dans le rappel de
    # document.fonts, après InkTheater.attach, une seule fois.
    enregistrement = 'window.__timelines["ink-demo"]'
    assert html.count(enregistrement) == 1
    assert html.index("document.fonts.ready") < html.index("InkTheater.attach") < html.index(enregistrement)
    apres = html[html.index(enregistrement):html.index("</script>", html.index(enregistrement))]
    assert apres.count("});") == 1, "l'enregistrement doit précéder la fermeture du rappel de document.fonts"
