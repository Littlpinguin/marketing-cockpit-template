#!/usr/bin/env python3
"""Convertit une capture de mouvement BVH en clip 2D pour le moteur ink-theater.

Lit la hiérarchie et les canaux d'un fichier BVH, calcule la position de chaque
articulation par cinématique directe, garde les 13 articulations d'une
silhouette (tête, cou, épaules, coudes, mains, hanche, genoux, pieds), les
projette sur un plan vertical et les normalise : hanche de la première image en
(0, 0), hauteur tête-pieds de la première image égale à 1, y vers le haut.

Plans : « frontal » (le personnage face à la caméra : gestes, danse),
« sagittal » (de profil : marche, course, saut), « auto » (de profil si la
hanche se déplace de plus d'une demi-hauteur, de face sinon).

Usage :
    python3 08-video/scripts/bvh2clip.py 02_01.bvh --nom marche --source "CMU 02_01" --sur-place --fin 4
    python3 08-video/scripts/bvh2clip.py 111_37.bvh --nom salut --source "CMU 111_37" --plan frontal

Écrit <sortie>/<nom>.json, met à jour <sortie>/catalogue.json et régénère
<sortie>/clips.js (global InkClips pour les compositions HyperFrames).
Sortie par défaut : 08-video/lib/ink-theater/clips/.

Codes de sortie : 0 écrit, 1 BVH illisible ou fenêtre vide, 2 usage.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE_DEFAUT = RACINE / "08-video" / "lib" / "ink-theater" / "clips"

ARTICULATIONS = ("tete", "cou", "epaule_g", "coude_g", "main_g", "epaule_d", "coude_d", "main_d",
                 "hanche", "genou_g", "pied_g", "genou_d", "pied_d")
# Noms BVH candidats, dans l'ordre de préférence. Dans les conversions de la
# base CMU, LeftShoulder est la clavicule et LeftArm l'épaule, LeftUpLeg la
# hanche et LeftLeg le genou ; « Head_End » est l'extrémité du crâne.
CORRESPONDANCES = {
    "tete": ("Head_End", "Head", "head"),
    "cou": ("Neck1", "Neck", "neck"),
    "epaule_g": ("LeftArm", "LeftShoulder", "l_shoulder", "lShldr"),
    "coude_g": ("LeftForeArm", "LeftElbow", "l_elbow", "lForeArm"),
    "main_g": ("LeftHand", "LeftWrist", "l_wrist", "lHand"),
    "epaule_d": ("RightArm", "RightShoulder", "r_shoulder", "rShldr"),
    "coude_d": ("RightForeArm", "RightElbow", "r_elbow", "rForeArm"),
    "main_d": ("RightHand", "RightWrist", "r_wrist", "rHand"),
    "hanche": ("Hips", "Hip", "hip", "Pelvis", "pelvis"),
    "genou_g": ("LeftLeg", "LeftKnee", "l_knee", "lShin"),
    "pied_g": ("LeftFoot", "LeftAnkle", "l_ankle", "lFoot"),
    "genou_d": ("RightLeg", "RightKnee", "r_knee", "rShin"),
    "pied_d": ("RightFoot", "RightAnkle", "r_ankle", "rFoot"),
}
LICENCE_CMU = "CMU Graphics Lab Motion Capture Database, free for all uses (http://mocap.cs.cmu.edu)"
NOM_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
IDENTITE = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


class ErreurBVH(Exception):
    """Fichier BVH illisible, articulation introuvable ou fenêtre vide."""


@dataclass
class Articulation:
    nom: str
    parent: int | None
    offset: tuple[float, float, float] = (0.0, 0.0, 0.0)
    canaux: list[str] = field(default_factory=list)


@dataclass
class BVH:
    articulations: list[Articulation]
    images: list[list[float]]
    duree_image: float


def _nom_propre(nom: str) -> str:
    """Retire un préfixe d'espace de noms (« mixamorig:LeftArm » → « LeftArm »)."""
    return nom.split(":")[-1]


def lire_bvh(texte: str) -> BVH:
    jetons = texte.split()
    position = 0

    def suivant() -> str:
        nonlocal position
        if position >= len(jetons):
            raise ErreurBVH("fin de fichier inattendue")
        jeton = jetons[position]
        position += 1
        return jeton

    def attendre(mot: str) -> None:
        jeton = suivant()
        if jeton != mot:
            raise ErreurBVH(f"« {mot} » attendu, trouvé « {jeton} »")

    articulations: list[Articulation] = []

    def lire_articulation(nom: str, parent: int | None) -> None:
        attendre("{")
        index = len(articulations)
        articulations.append(Articulation(nom, parent))
        while True:
            jeton = suivant()
            if jeton == "OFFSET":
                articulations[index].offset = (float(suivant()), float(suivant()), float(suivant()))
            elif jeton == "CHANNELS":
                articulations[index].canaux = [suivant() for _ in range(int(suivant()))]
            elif jeton == "JOINT":
                lire_articulation(_nom_propre(suivant()), index)
            elif jeton == "End":
                attendre("Site")
                lire_articulation(f"{nom}_End", index)
            elif jeton == "}":
                return
            else:
                raise ErreurBVH(f"mot inattendu dans la hiérarchie : « {jeton} »")

    try:
        attendre("HIERARCHY")
        attendre("ROOT")
        lire_articulation(_nom_propre(suivant()), None)
        attendre("MOTION")
        attendre("Frames:")
        nombre = int(suivant())
        attendre("Frame")
        attendre("Time:")
        duree_image = float(suivant())
    except ValueError as err:
        raise ErreurBVH(f"nombre illisible : {err}") from err
    largeur = sum(len(a.canaux) for a in articulations)
    try:
        valeurs = [float(v) for v in jetons[position:position + nombre * largeur]]
    except ValueError as err:
        raise ErreurBVH(f"donnée de mouvement illisible : {err}") from err
    if nombre < 1 or len(valeurs) < nombre * largeur:
        raise ErreurBVH(f"{nombre} images annoncées, données insuffisantes")
    if duree_image <= 0:
        raise ErreurBVH("durée d'image nulle ou négative")
    images = [valeurs[i * largeur:(i + 1) * largeur] for i in range(nombre)]
    return BVH(articulations, images, duree_image)


def _rotation(axe: str, degres: float) -> tuple[tuple[float, ...], ...]:
    a = math.radians(degres)
    c, s = math.cos(a), math.sin(a)
    if axe == "X":
        return ((1.0, 0.0, 0.0), (0.0, c, -s), (0.0, s, c))
    if axe == "Y":
        return ((c, 0.0, s), (0.0, 1.0, 0.0), (-s, 0.0, c))
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def _produit(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def _appliquer(m, v):
    return tuple(sum(m[i][k] * v[k] for k in range(3)) for i in range(3))


def positions(bvh: BVH, image: list[float]) -> list[tuple[float, float, float]]:
    """Positions monde de chaque articulation pour une image (cinématique directe).

    Les rotations se composent dans l'ordre où les canaux sont déclarés.
    """
    rotations, points = [], []
    curseur = 0
    for art in bvh.articulations:
        translation = [0.0, 0.0, 0.0]
        rotation = IDENTITE
        for canal in art.canaux:
            valeur = image[curseur]
            curseur += 1
            if canal.endswith("position"):
                translation["XYZ".index(canal[0].upper())] = valeur
            elif canal.endswith("rotation"):
                rotation = _produit(rotation, _rotation(canal[0].upper(), valeur))
            else:
                raise ErreurBVH(f"canal inconnu : {canal}")
        local = tuple(o + t for o, t in zip(art.offset, translation))
        if art.parent is None:
            points.append(local)
            rotations.append(rotation)
        else:
            rotation_parent = rotations[art.parent]
            decalage = _appliquer(rotation_parent, local)
            points.append(tuple(p + d for p, d in zip(points[art.parent], decalage)))
            rotations.append(_produit(rotation_parent, rotation))
    return points


def correspondance(noms: list[str]) -> dict[str, int]:
    exacts = {nom: i for i, nom in enumerate(noms)}
    minuscules = {nom.lower(): i for i, nom in enumerate(noms)}
    resultat, manquantes = {}, []
    for art in ARTICULATIONS:
        candidats = CORRESPONDANCES[art]
        trouve = next((exacts[c] for c in candidats if c in exacts), None)
        if trouve is None:
            trouve = next((minuscules[c.lower()] for c in candidats if c.lower() in minuscules), None)
        if trouve is None:
            manquantes.append(art)
        else:
            resultat[art] = trouve
    if manquantes:
        raise ErreurBVH("articulations introuvables : " + "; ".join(
            f"{a} (cherché : {', '.join(CORRESPONDANCES[a])})" for a in manquantes))
    return resultat


def _pose(bvh: BVH, t: float, corr: dict[str, int]) -> list[tuple[float, float, float]]:
    f = t / bvh.duree_image
    i = min(int(math.floor(f)), len(bvh.images) - 1)
    j = min(i + 1, len(bvh.images) - 1)
    a = f - i if j != i else 0.0
    pi = positions(bvh, bvh.images[i])
    pj = positions(bvh, bvh.images[j]) if j != i else pi
    return [tuple(pi[corr[n]][k] * (1 - a) + pj[corr[n]][k] * a for k in range(3)) for n in ARTICULATIONS]


def _horizontal(p: tuple[float, float, float]) -> tuple[float, float]:
    return (p[0], p[2])


def _axe(poses: list[list[tuple[float, float, float]]], plan: str, hauteur: float) -> tuple[tuple[float, float], str]:
    """Vecteur horizontal unitaire de projection, et plan retenu."""
    k = ARTICULATIONS.index
    premiere, derniere = poses[0], poses[-1]
    gauche, droite = _horizontal(premiere[k("epaule_g")]), _horizontal(premiere[k("epaule_d")])
    s = (droite[0] - gauche[0], droite[1] - gauche[1])
    norme = math.hypot(*s) or 1.0
    s = (s[0] / norme, s[1] / norme)
    depart, arrivee = _horizontal(premiere[k("hanche")]), _horizontal(derniere[k("hanche")])
    trajet = (arrivee[0] - depart[0], arrivee[1] - depart[1])
    if plan == "auto":
        plan = "sagittal" if math.hypot(*trajet) > 0.5 * hauteur else "frontal"
    if plan == "frontal":
        # Face à la caméra, la droite du personnage est à gauche de l'image.
        return (-s[0], -s[1]), plan
    u = (-s[1], s[0])
    if trajet[0] * u[0] + trajet[1] * u[1] < 0:
        u = (-u[0], -u[1])
    return u, plan


def convertir(bvh: BVH, *, nom: str, source: str, fps: float = 30.0, debut: float = 0.0,
              fin: float | None = None, plan: str = "auto", sur_place: bool = False) -> dict:
    if plan not in ("auto", "frontal", "sagittal"):
        raise ErreurBVH(f"plan inconnu : {plan}")
    corr = correspondance([a.nom for a in bvh.articulations])
    duree_totale = (len(bvh.images) - 1) * bvh.duree_image
    fin = duree_totale if fin is None else min(fin, duree_totale)
    if not 0 <= debut < fin:
        raise ErreurBVH(f"fenêtre [{debut:g}, {fin:g}] s vide ou hors du clip ({duree_totale:.2f} s)")
    pas = 1.0 / fps
    temps = []
    while debut + len(temps) * pas <= fin + 1e-9:
        temps.append(debut + len(temps) * pas)
    poses = [_pose(bvh, t, corr) for t in temps]

    premiere = poses[0]
    hauteur = max(p[1] for p in premiere) - min(p[1] for p in premiere)
    if hauteur <= 0:
        raise ErreurBVH("hauteur nulle à la première image")
    u, plan = _axe(poses, plan, hauteur)
    hanche = ARTICULATIONS.index("hanche")

    def abscisse(p: tuple[float, float, float]) -> float:
        return p[0] * u[0] + p[2] * u[1]

    origine_x, origine_y = abscisse(premiere[hanche]), premiere[hanche][1]
    images = []
    for pose in poses:
        recul = abscisse(pose[hanche]) - origine_x if sur_place else 0.0
        images.append([[round((abscisse(p) - origine_x - recul) / hauteur, 4) + 0.0,
                        round((p[1] - origine_y) / hauteur, 4) + 0.0] for p in pose])
    return {"nom": nom, "fps": fps, "articulations": list(ARTICULATIONS), "images": images,
            "plan": plan, "source": source, "licence": LICENCE_CMU}


def mettre_a_jour_catalogue(dossier: Path, clip: dict, fichier: str) -> None:
    chemin = dossier / "catalogue.json"
    catalogue = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {"clips": []}
    entree = {"nom": clip["nom"], "fichier": fichier, "source": clip["source"], "plan": clip["plan"],
              "fps": clip["fps"], "images": len(clip["images"]),
              "duree": round((len(clip["images"]) - 1) / clip["fps"], 3)}
    catalogue["clips"] = sorted([c for c in catalogue["clips"] if c["nom"] != clip["nom"]] + [entree],
                                key=lambda c: c["nom"])
    chemin.write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ecrire_bundle(dossier: Path) -> Path:
    """Regroupe tous les clips du dossier dans clips.js (global InkClips, ou module CommonJS)."""
    clips = {}
    for chemin in sorted(dossier.glob("*.json")):
        if chemin.name == "catalogue.json":
            continue
        clip = json.loads(chemin.read_text(encoding="utf-8"))
        clips[clip["nom"]] = clip
    corps = json.dumps(clips, ensure_ascii=False, separators=(",", ":"))
    sortie = dossier / "clips.js"
    sortie.write_text(
        "/* Généré par 08-video/scripts/bvh2clip.py : ne pas éditer. Clips dérivés de la base CMU\n"
        "   (voir ../THIRD_PARTY_NOTICES.md). */\n"
        "(function (racine, clips) {\n"
        '  if (typeof module === "object" && module && module.exports) { module.exports = clips; }\n'
        "  else { racine.InkClips = clips; }\n"
        f'}})(typeof globalThis !== "undefined" ? globalThis : this, {corps});\n',
        encoding="utf-8")
    return sortie


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convertit un BVH en clip 2D pour ink-theater.")
    p.add_argument("bvh", help="fichier BVH")
    p.add_argument("--nom", required=True, help="nom du clip (minuscules et tirets : marche, coup-de-pied)")
    p.add_argument("--source", required=True, help='origine citée dans les notices, ex. "CMU 02_01"')
    p.add_argument("--plan", choices=("auto", "frontal", "sagittal"), default="auto")
    p.add_argument("--sur-place", action="store_true", help="annule le déplacement horizontal de la hanche")
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--debut", type=float, default=0.0, help="début de la fenêtre, en s")
    p.add_argument("--fin", type=float, help="fin de la fenêtre, en s (défaut : fin du fichier)")
    p.add_argument("--sortie", default=str(SORTIE_DEFAUT))
    args = p.parse_args(argv)
    if not NOM_RE.fullmatch(args.nom):
        print(f"ERREUR : nom « {args.nom} » invalide (minuscules, chiffres et tirets)", file=sys.stderr)
        return 2
    if args.fps <= 0:
        print("ERREUR : --fps doit être positif", file=sys.stderr)
        return 2
    try:
        bvh = lire_bvh(Path(args.bvh).read_text(encoding="utf-8", errors="replace"))
        clip = convertir(bvh, nom=args.nom, source=args.source, fps=args.fps, debut=args.debut,
                         fin=args.fin, plan=args.plan, sur_place=args.sur_place)
    except (ErreurBVH, OSError) as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1
    dossier = Path(args.sortie)
    dossier.mkdir(parents=True, exist_ok=True)
    fichier = f"{args.nom}.json"
    (dossier / fichier).write_text(json.dumps(clip, ensure_ascii=False, separators=(",", ":")) + "\n",
                                   encoding="utf-8")
    mettre_a_jour_catalogue(dossier, clip, fichier)
    ecrire_bundle(dossier)
    print(f"{fichier} : {len(clip['images'])} images à {clip['fps']:g} i/s, plan {clip['plan']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
