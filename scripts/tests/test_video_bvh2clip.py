"""Tests de 08-video/scripts/bvh2clip.py (BVH → clips 2D d'ink-theater).

Les squelettes sont fabriqués dans le test : aucun fichier de capture réel
n'est nécessaire.
"""
from __future__ import annotations

import importlib.util
import json
import math
import os
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


def _chaine(rot_racine: str, rot_bras: str = "0 0 0", offset: str = "0 1 0",
            ordre: str = "Zrotation Xrotation Yrotation") -> str:
    """Racine + un bras d'un os + son extrémité ; valeurs de rotation de la racine puis du bras."""
    return ("HIERARCHY ROOT Hips { OFFSET 0 0 0 CHANNELS 6 Xposition Yposition Zposition "
            f"{ordre} JOINT Arm {{ OFFSET {offset} {ROT} End Site {{ OFFSET {offset} }} }} }} "
            f"MOTION Frames: 1 Frame Time: 0.1 0 0 0 {rot_racine} {rot_bras}")


def _zero_negatif(clip: dict) -> list:
    """Coordonnées égales à -0.0 (elles s'écriraient « -0.0 » dans le JSON)."""
    return [(i, j, k) for i, image in enumerate(clip["images"]) for j, point in enumerate(image)
            for k, v in enumerate(point) if v == 0 and math.copysign(1.0, v) < 0]


def test_composition_parent_enfant():
    """Racine Zrotation 90 puis bras Xrotation 90 : les rotations du parent s'appliquent d'abord."""
    bvh = b2c.lire_bvh(_chaine("90 0 0", "0 90 0"))
    pos = b2c.positions(bvh, bvh.images[0])
    assert pos[1] == pytest.approx((-1.0, 0.0, 0.0), abs=1e-9)
    assert pos[2] == pytest.approx((-1.0, 0.0, 1.0), abs=1e-9)


def test_rotation_autour_de_y():
    """Yrotation 90 envoie +X vers -Z (repère main droite, Y vers le haut)."""
    bvh = b2c.lire_bvh(_chaine("0 0 90", offset="1 0 0"))
    pos = b2c.positions(bvh, bvh.images[0])
    assert pos[1] == pytest.approx((0.0, 0.0, -1.0), abs=1e-9)
    assert pos[2] == pytest.approx((0.0, 0.0, -2.0), abs=1e-9)


def test_canal_inconnu_et_axe_inconnu():
    with pytest.raises(b2c.ErreurBVH, match="Wposition"):
        b2c.lire_bvh(squelette(repos(2)).replace("Xposition", "Wposition", 1))
    with pytest.raises(b2c.ErreurBVH, match="axe"):
        b2c._rotation("W", 10.0)


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
    assert hanche == [0.0, 0.0] and all(math.copysign(1.0, v) > 0 for v in hanche)
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


def test_image_unique():
    bvh = b2c.lire_bvh(squelette(repos(1)))
    with pytest.raises(b2c.ErreurBVH, match="deux images"):
        b2c.convertir(bvh, nom="x", source="x")


def test_hauteur_tete_pieds_meme_main_levee():
    """L'échelle est la hauteur tête-pieds, pas l'étendue de tous les points (main au-dessus de la tête)."""
    bvh = b2c.lire_bvh(squelette(repos(3, c15=lambda i: 90)))     # LeftArm Zrotation 90 : bras levé
    clip = b2c.convertir(bvh, nom="test", source="test", fps=30, plan="frontal")
    premiere = clip["images"][0]
    tete, main = premiere[b2c.ARTICULATIONS.index("tete")], premiere[b2c.ARTICULATIONS.index("main_g")]
    pied = premiere[b2c.ARTICULATIONS.index("pied_g")]
    assert main[1] > tete[1], "la main est bien au-dessus de la tête"
    assert tete[1] - pied[1] == pytest.approx(1.0, abs=1e-3)


def test_hanche_en_hauteur_reste_a_l_origine():
    """Hanche à 30 unités du sol, puis qui descend : y relatif à la hanche de la première image."""
    bvh = b2c.lire_bvh(squelette(repos(3, c1=lambda i: 30 - 5 * i)))
    clip = b2c.convertir(bvh, nom="test", source="test", fps=30, plan="frontal")
    hanche = [image[b2c.ARTICULATIONS.index("hanche")] for image in clip["images"]]
    assert hanche[0] == [0.0, 0.0] and all(math.copysign(1.0, v) > 0 for v in hanche[0])
    assert [h[1] for h in hanche] == pytest.approx([0.0, -5 / 52, -10 / 52], abs=1e-3)
    tete = clip["images"][0][b2c.ARTICULATIONS.index("tete")]
    assert tete[1] == pytest.approx(28 / 52, abs=1e-3)


def test_reechantillonnage_lineaire_a_cheval_sur_les_images():
    """7 i/s à partir de 0,05 s (entre deux images à 30 i/s) : chaque échantillon est interpolé."""
    bvh = b2c.lire_bvh(squelette(repos(31, c2=lambda i: i * 40 / 30)))     # 40 unités par seconde
    clip = b2c.convertir(bvh, nom="m", source="test", fps=7, debut=0.05, plan="sagittal")
    hanche = b2c.ARTICULATIONS.index("hanche")
    xs = [image[hanche][0] for image in clip["images"]]
    assert len(xs) == 7
    assert xs == pytest.approx([40 * n / 7 / 52 for n in range(7)], abs=1e-4)


def test_aucun_zero_negatif():
    """Un reste de calcul négatif minuscule arrondi à -0.0 s'écrit 0.0 (sinon « -0.0 » dans le JSON)."""
    bvh = b2c.lire_bvh(squelette(repos(3, c6=lambda i: 1e-5)))              # Spine Zrotation : cou et tête à x < 0
    clip = b2c.convertir(bvh, nom="test", source="test", fps=30, plan="frontal")
    assert _zero_negatif(clip) == []


def _pas_en_avant(**canaux):
    """Jambe gauche balancée vers l'avant du personnage (+Z local) : genou à 6, pied à 12 unités."""
    return repos(4, c34=lambda i: -30, **canaux)


@pytest.mark.parametrize("lacet", [0, 180])
def test_sagittal_le_personnage_regarde_vers_la_droite(lacet):
    """Sur place, vu de profil : l'avant du personnage (ici le pied levé) va vers les x croissants,
    quelle que soit son orientation dans le monde."""
    bvh = b2c.lire_bvh(squelette(_pas_en_avant(c5=lambda i: lacet)))
    clip = b2c.convertir(bvh, nom="pas", source="test", fps=30, plan="sagittal", sur_place=True)
    image = clip["images"][0]
    genou, pied = image[b2c.ARTICULATIONS.index("genou_g")], image[b2c.ARTICULATIONS.index("pied_g")]
    assert genou[0] == pytest.approx(6 / 52, abs=1e-3) and pied[0] == pytest.approx(12 / 52, abs=1e-3)


def test_sagittal_marche_arriere_va_vers_la_gauche():
    """Le sens de l'image ne dépend pas du déplacement net : reculer fait diminuer x."""
    bvh = b2c.lire_bvh(squelette(repos(31, c2=lambda i: -i * 40 / 30)))
    clip = b2c.convertir(bvh, nom="recul", source="test", fps=30, plan="sagittal")
    xs = [image[b2c.ARTICULATIONS.index("hanche")][0] for image in clip["images"]]
    assert xs[-1] == pytest.approx(-40 / 52, abs=1e-3) and xs == sorted(xs, reverse=True)


def test_epaules_confondues():
    texte = squelette(repos(2)).replace("OFFSET 5 8 0", "OFFSET 0 8 0").replace("OFFSET -5 8 0", "OFFSET 0 8 0")
    with pytest.raises(b2c.ErreurBVH, match="épaules"):
        b2c.convertir(b2c.lire_bvh(texte), nom="x", source="x")


def _lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, timeout=30)


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


def test_cli_licence_bom_et_en_tete_neutre(tmp_path):
    bvh = tmp_path / "bom.bvh"
    bvh.write_bytes(b"\xef\xbb\xbf" + squelette(repos(10)).encode("utf-8"))
    sortie = tmp_path / "clips"
    res = _lancer(str(bvh), "--nom", "maison", "--source", "capture maison", "--licence", "CC0 1.0",
                  "--sortie", str(sortie))
    assert res.returncode == 0, res.stderr
    assert json.loads((sortie / "maison.json").read_text(encoding="utf-8"))["licence"] == "CC0 1.0"
    assert "CMU" not in (sortie / "clips.js").read_text(encoding="utf-8")


@pytest.mark.parametrize("fps", ["nan", "inf", "-inf", "0", "-5"])
def test_cli_fps_invalide(tmp_path, fps):
    bvh = tmp_path / "a.bvh"
    bvh.write_text(squelette(repos(5)), encoding="utf-8")
    res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--fps", fps, "--sortie", str(tmp_path / "s"))
    assert res.returncode == 2 and "Traceback" not in res.stderr


def _bvh_valide(tmp_path: Path) -> Path:
    bvh = tmp_path / "a.bvh"
    bvh.write_text(squelette(repos(5)), encoding="utf-8")
    return bvh


def test_cli_sortie_inecrivable_sans_trace(tmp_path):
    bvh = _bvh_valide(tmp_path)
    fichier = tmp_path / "un-fichier"
    fichier.write_text("x", encoding="utf-8")
    for sortie in (fichier, fichier / "sous-dossier"):
        res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
        assert res.returncode == 1 and "ERREUR" in res.stderr and "Traceback" not in res.stderr, sortie


@pytest.mark.skipif(not hasattr(os, "geteuid") or os.geteuid() == 0, reason="les droits ne s'appliquent pas à root")
def test_cli_dossier_en_lecture_seule_sans_trace(tmp_path):
    bvh = _bvh_valide(tmp_path)
    sortie = tmp_path / "ro"
    sortie.mkdir()
    sortie.chmod(0o500)
    try:
        res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
    finally:
        sortie.chmod(0o700)
    assert res.returncode == 1 and "ERREUR" in res.stderr and "Traceback" not in res.stderr


def test_cli_json_etrangers_ignores_dans_le_bundle(tmp_path):
    bvh = _bvh_valide(tmp_path)
    sortie = tmp_path / "clips"
    sortie.mkdir()
    (sortie / "package.json").write_text('{"name": "x", "version": "1"}', encoding="utf-8")
    (sortie / "liste.json").write_text("[1, 2, 3]", encoding="utf-8")
    (sortie / "texte.json").write_text('"juste une chaîne"', encoding="utf-8")
    res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
    assert res.returncode == 0 and "Traceback" not in res.stderr, res.stderr
    bundle = (sortie / "clips.js").read_text(encoding="utf-8")
    assert '"a":{' in bundle and "package" not in bundle and '"version"' not in bundle


def test_cli_json_illisible_ou_catalogue_corrompu(tmp_path):
    bvh = _bvh_valide(tmp_path)
    sortie = tmp_path / "clips"
    sortie.mkdir()
    (sortie / "catalogue.json").write_text("{pas du json", encoding="utf-8")
    res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
    assert res.returncode == 1 and "catalogue.json" in res.stderr and "Traceback" not in res.stderr
    assert not (sortie / "a.json").exists(), "rien n'est écrit tant que le catalogue est illisible"
    (sortie / "catalogue.json").write_text('{"clips": 3}', encoding="utf-8")
    res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
    assert res.returncode == 1 and "catalogue.json" in res.stderr and "Traceback" not in res.stderr
    (sortie / "catalogue.json").unlink()
    (sortie / "autre.json").write_text("{cassé", encoding="utf-8")
    res = _lancer(str(bvh), "--nom", "a", "--source", "x", "--sortie", str(sortie))
    assert res.returncode == 1 and "autre.json" in res.stderr and "Traceback" not in res.stderr
