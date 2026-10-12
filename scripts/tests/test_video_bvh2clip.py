"""Tests de 08-video/scripts/bvh2clip.py (BVH → clips 2D d'ink-theater).

Les squelettes sont fabriqués dans le test : aucun fichier de capture réel
n'est nécessaire.
"""
from __future__ import annotations

import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "08-video" / "scripts" / "bvh2clip.py"


def _charger():
    spec = importlib.util.spec_from_file_location("bvh2clip", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


b2c = _charger()

ROT = "CHANNELS 3 Zrotation Xrotation Yrotation"


def _bras(cote: str, signe: int) -> str:
    return (f"JOINT {cote}Arm {{ OFFSET {5 * signe} 8 0 {ROT} "
            f"JOINT {cote}ForeArm {{ OFFSET {6 * signe} 0 0 {ROT} "
            f"JOINT {cote}Hand {{ OFFSET {6 * signe} 0 0 {ROT} End Site {{ OFFSET {2 * signe} 0 0 }} }} }} }}")


def _jambe(cote: str, signe: int) -> str:
    return (f"JOINT {cote}UpLeg {{ OFFSET {3 * signe} 0 0 {ROT} "
            f"JOINT {cote}Leg {{ OFFSET 0 -12 0 {ROT} "
            f"JOINT {cote}Foot {{ OFFSET 0 -12 0 {ROT} End Site {{ OFFSET 0 0 3 }} }} }} }}")


HIERARCHIE = (
    "HIERARCHY\nROOT Hips\n{ OFFSET 0 0 0 CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n"
    f"JOINT Spine {{ OFFSET 0 10 0 {ROT}\n"
    f"JOINT Neck {{ OFFSET 0 10 0 {ROT} JOINT Head {{ OFFSET 0 4 0 {ROT} End Site {{ OFFSET 0 4 0 }} }} }}\n"
    f"{_bras('Left', 1)}\n{_bras('Right', -1)}\n}}\n"
    f"{_jambe('Left', 1)}\n{_jambe('Right', -1)}\n}}\n"
)
NB_CANAUX = 6 + 15 * 3


def squelette(images: list[list[float]], duree_image: float = 1 / 30) -> str:
    lignes = "\n".join(" ".join(f"{v:g}" for v in image) for image in images)
    return f"{HIERARCHIE}MOTION\nFrames: {len(images)}\nFrame Time: {duree_image}\n{lignes}\n"


def repos(n: int, **par_image) -> list[list[float]]:
    """n images au repos ; par_image : {indice_canal: fonction(i) -> valeur}."""
    images = []
    for i in range(n):
        image = [0.0] * NB_CANAUX
        for canal, f in par_image.items():
            image[int(canal.lstrip("c"))] = f(i)
        images.append(image)
    return images


def test_lecture_de_la_hierarchie():
    bvh = b2c.lire_bvh(squelette(repos(3)))
    noms = [a.nom for a in bvh.articulations]
    assert noms[0] == "Hips" and "Head_End" in noms and "LeftHand_End" in noms
    assert sum(len(a.canaux) for a in bvh.articulations) == NB_CANAUX
    assert len(bvh.images) == 3 and bvh.duree_image == pytest.approx(1 / 30)


def _mini(ordre: str, valeurs: str) -> str:
    return ("HIERARCHY ROOT Hips { OFFSET 0 0 0 CHANNELS 6 Xposition Yposition Zposition "
            f"{ordre} JOINT Arm {{ OFFSET 0 1 0 {ROT} End Site {{ OFFSET 0 1 0 }} }} }} "
            f"MOTION Frames: 1 Frame Time: 0.1 0 0 0 {valeurs} 0 0 0")


def test_cinematique_d_une_rotation_connue():
    bvh = b2c.lire_bvh(_mini("Zrotation Xrotation Yrotation", "90 0 0"))
    pos = b2c.positions(bvh, bvh.images[0])
    assert pos[1] == pytest.approx((-1.0, 0.0, 0.0), abs=1e-9)
    assert pos[2] == pytest.approx((-2.0, 0.0, 0.0), abs=1e-9)


def test_l_ordre_des_canaux_compte():
    zx = b2c.lire_bvh(_mini("Zrotation Xrotation Yrotation", "90 90 0"))
    xz = b2c.lire_bvh(_mini("Xrotation Zrotation Yrotation", "90 90 0"))
    assert b2c.positions(zx, zx.images[0])[1] == pytest.approx((0.0, 0.0, 1.0), abs=1e-9)
    assert b2c.positions(xz, xz.images[0])[1] == pytest.approx((-1.0, 0.0, 0.0), abs=1e-9)


def test_ordre_xyz_et_ordre_inverse():
    """Xrotation Yrotation Zrotation (ordre fréquent hors CMU) : Rx·Ry, pas Ry·Rx."""
    xyz = b2c.lire_bvh(_mini("Xrotation Yrotation Zrotation", "90 90 0"))
    zyx = b2c.lire_bvh(_mini("Zrotation Yrotation Xrotation", "90 90 0"))
    assert b2c.positions(xyz, xyz.images[0])[1] == pytest.approx((0.0, 0.0, 1.0), abs=1e-9)
    assert b2c.positions(zyx, zyx.images[0])[1] == pytest.approx((-1.0, 0.0, 0.0), abs=1e-9)


def test_noms_prefixes_et_articulation_manquante():
    texte = squelette(repos(2)).replace("JOINT Left", "JOINT mixamorig:Left")
    bvh = b2c.lire_bvh(texte)
    corr = b2c.correspondance([a.nom for a in bvh.articulations])
    assert set(corr) == set(b2c.ARTICULATIONS)
    with pytest.raises(b2c.ErreurBVH, match="pied_d"):
        b2c.correspondance([n for n in [a.nom for a in bvh.articulations] if n != "RightFoot"])


def test_conversion_normalise_et_reechantillonne():
    bvh = b2c.lire_bvh(squelette(repos(31)))
    clip = b2c.convertir(bvh, nom="test", source="test", fps=15, plan="frontal")
    assert clip["articulations"] == list(b2c.ARTICULATIONS)
    assert len(clip["images"]) == 16
    premiere = clip["images"][0]
    hanche = premiere[b2c.ARTICULATIONS.index("hanche")]
    assert hanche == [0.0, 0.0]
    tete = premiere[b2c.ARTICULATIONS.index("tete")]
    pied = premiere[b2c.ARTICULATIONS.index("pied_g")]
    assert tete[1] - pied[1] == pytest.approx(1.0, abs=1e-3)
    epaule_d = premiere[b2c.ARTICULATIONS.index("epaule_d")]
    assert epaule_d[0] < 0, "de face, l'épaule droite du personnage est à gauche de l'image"


def test_trajet_vu_de_profil_et_sur_place():
    images = repos(31, c2=lambda i: i * 40 / 30)          # Zposition : 40 unités vers l'avant
    bvh = b2c.lire_bvh(squelette(images))
    clip = b2c.convertir(bvh, nom="marche", source="test", fps=30)
    assert clip["plan"] == "sagittal"
    hanche = b2c.ARTICULATIONS.index("hanche")
    xs = [image[hanche][0] for image in clip["images"]]
    assert xs[-1] == pytest.approx(40 / 52, abs=1e-3) and xs == sorted(xs)
    fixe = b2c.convertir(bvh, nom="marche", source="test", fps=30, sur_place=True)
    assert all(abs(image[hanche][0]) < 1e-9 for image in fixe["images"])


def test_fenetre_vide():
    bvh = b2c.lire_bvh(squelette(repos(31)))
    with pytest.raises(b2c.ErreurBVH, match="fenêtre"):
        b2c.convertir(bvh, nom="x", source="x", debut=5.0)


def _lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_cli_ecrit_clip_catalogue_et_bundle(tmp_path):
    bvh = tmp_path / "salut.bvh"
    bvh.write_text(squelette(repos(10)), encoding="utf-8")
    sortie = tmp_path / "clips"
    for _ in range(2):
        res = _lancer(str(bvh), "--nom", "salut", "--source", "CMU 00_00", "--sortie", str(sortie))
        assert res.returncode == 0, res.stderr
    clip = json.loads((sortie / "salut.json").read_text(encoding="utf-8"))
    assert clip["source"] == "CMU 00_00" and "CMU" in clip["licence"]
    catalogue = json.loads((sortie / "catalogue.json").read_text(encoding="utf-8"))
    assert [c["nom"] for c in catalogue["clips"]] == ["salut"]
    bundle = (sortie / "clips.js").read_text(encoding="utf-8")
    assert "InkClips" in bundle and '"salut"' in bundle and "module.exports" in bundle


def test_cli_nom_invalide_et_bvh_illisible(tmp_path):
    bvh = tmp_path / "a.bvh"
    bvh.write_text(squelette(repos(2)), encoding="utf-8")
    assert _lancer(str(bvh), "--nom", "Pas Bon", "--source", "x", "--sortie", str(tmp_path)).returncode == 2
    casse = tmp_path / "casse.bvh"
    casse.write_text("HIERARCHY ROOT", encoding="utf-8")
    res = _lancer(str(casse), "--nom", "casse", "--source", "x", "--sortie", str(tmp_path))
    assert res.returncode == 1 and "ERREUR" in res.stderr
