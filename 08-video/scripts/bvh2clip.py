#!/usr/bin/env python3
"""Convertit une capture de mouvement BVH en clip 2D pour le moteur ink-theater.

Lit la hiérarchie et les canaux d'un fichier BVH, calcule la position de chaque
articulation par cinématique directe, garde les 13 articulations d'une
silhouette (tête, cou, épaules, coudes, mains, hanche, genoux, pieds), les
projette sur un plan vertical et les normalise : hanche de la première image en
(0, 0), hauteur tête-pieds de la première image égale à 1, y vers le haut.

Hauteur de référence : de la tête (extrémité du crâne) au pied le plus bas de
la première image, même si une main est levée plus haut que la tête.

Plans et sens de l'image (convention fixe, qui ne dépend ni de l'orientation du
personnage dans le monde ni de son déplacement net) :
  - « frontal » : le personnage fait face à la caméra (gestes, danse) ; sa
    droite est à gauche de l'image.
  - « sagittal » : le personnage est de profil et regarde toujours vers la
    droite de l'image (marche, course, saut) ; l'avant du personnage, déduit de
    la ligne des épaules à la première image, va vers les x croissants. Une
    marche arrière fait donc diminuer x.
  - « auto » : sagittal si la hanche se déplace de plus d'une demi-hauteur,
    frontal sinon.

Usage :
    python3 08-video/scripts/bvh2clip.py 02_01.bvh --nom marche --source "CMU 02_01" --sur-place --fin 4
    python3 08-video/scripts/bvh2clip.py 111_37.bvh --nom salut --source "CMU 111_37" --plan frontal
    python3 08-video/scripts/bvh2clip.py capture.bvh --nom geste --source "ma capture" --licence "CC0 1.0"

Écrit <sortie>/<nom>.json, met à jour <sortie>/catalogue.json et régénère
<sortie>/clips.js (global InkClips pour les compositions HyperFrames).
Sortie par défaut : 08-video/lib/ink-theater/clips/. La licence écrite dans le
clip est celle de la base CMU, sauf si --licence en donne une autre.

Codes de sortie : 0 écrit, 1 BVH illisible, fenêtre vide ou écriture impossible,
2 usage.
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
# catalogue.json et clips.js vivent dans le même dossier que les clips : ces noms écraseraient l'un ou l'autre.
NOMS_RESERVES = frozenset({"catalogue", "clips"})
IDENTITE = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
CANAUX = frozenset(f"{axe}{nature}" for axe in "XYZ" for nature in ("position", "rotation"))


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
                canaux = [suivant() for _ in range(int(suivant()))]
                inconnus = [c for c in canaux if c not in CANAUX]
                if inconnus:
                    raise ErreurBVH(f"canal inconnu : {inconnus[0]} (attendu : Xposition, Yrotation, etc.)")
                articulations[index].canaux = canaux
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
    if axe == "Z":
        return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))
    raise ErreurBVH(f"axe de rotation inconnu : {axe}")


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
    """Vecteur horizontal unitaire de l'axe x de l'image dans le plan (x, z) du monde, et plan retenu.

    Le sens vient de la ligne des épaules de la première image : s est la
    droite du personnage (épaule droite moins épaule gauche), son avant est
    (s[1], -s[0]) (Y vers le haut, repère main droite).
    """
    k = ARTICULATIONS.index
    premiere, derniere = poses[0], poses[-1]
    gauche, droite = _horizontal(premiere[k("epaule_g")]), _horizontal(premiere[k("epaule_d")])
    s = (droite[0] - gauche[0], droite[1] - gauche[1])
    norme = math.hypot(*s)
    if norme <= 1e-6 * hauteur:
        raise ErreurBVH("épaules confondues dans le plan horizontal à la première image : "
                        "orientation du personnage indéterminée")
    s = (s[0] / norme, s[1] / norme)
    if plan == "auto":
        depart, arrivee = _horizontal(premiere[k("hanche")]), _horizontal(derniere[k("hanche")])
        plan = "sagittal" if math.hypot(arrivee[0] - depart[0], arrivee[1] - depart[1]) > 0.5 * hauteur else "frontal"
    if plan == "frontal":
        # Face à la caméra, la droite du personnage est à gauche de l'image.
        return (-s[0], -s[1]), plan
    # De profil, le personnage regarde vers la droite de l'image : x croît vers son avant.
    return (s[1], -s[0]), plan


def convertir(bvh: BVH, *, nom: str, source: str, fps: float = 30.0, debut: float = 0.0,
              fin: float | None = None, plan: str = "auto", sur_place: bool = False,
              licence: str = LICENCE_CMU) -> dict:
    if plan not in ("auto", "frontal", "sagittal"):
        raise ErreurBVH(f"plan inconnu : {plan}")
    if not (math.isfinite(fps) and fps > 0):
        raise ErreurBVH(f"fps invalide : {fps}")
    if len(bvh.images) < 2:
        raise ErreurBVH("un clip demande au moins deux images : ce BVH n'en contient qu'une")
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
    pieds = min(premiere[ARTICULATIONS.index(n)][1] for n in ("pied_g", "pied_d"))
    hauteur = premiere[ARTICULATIONS.index("tete")][1] - pieds
    if hauteur <= 0:      # squelette couché ou à l'envers : on retombe sur l'étendue verticale
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
            "plan": plan, "source": source, "licence": licence}


def _lire_json(chemin: Path):
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError as err:       # JSONDecodeError et UnicodeDecodeError en sont dérivées
        raise ErreurBVH(f"{chemin.name} illisible : {err}") from err


def _lire_catalogue(dossier: Path) -> dict:
    chemin = dossier / "catalogue.json"
    if not chemin.exists():
        return {"clips": []}
    catalogue = _lire_json(chemin)
    if not (isinstance(catalogue, dict) and isinstance(catalogue.get("clips"), list)
            and all(isinstance(c, dict) and "nom" in c for c in catalogue["clips"])):
        raise ErreurBVH('catalogue.json illisible : {"clips": [{"nom": …}, …]} attendu')
    return catalogue


def mettre_a_jour_catalogue(dossier: Path, clip: dict, fichier: str) -> None:
    catalogue = _lire_catalogue(dossier)
    entree = {"nom": clip["nom"], "fichier": fichier, "source": clip["source"], "plan": clip["plan"],
              "fps": clip["fps"], "images": len(clip["images"]),
              "duree": round((len(clip["images"]) - 1) / clip["fps"], 3)}
    catalogue["clips"] = sorted([c for c in catalogue["clips"] if c["nom"] != clip["nom"]] + [entree],
                                key=lambda c: c["nom"])
    (dossier / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=2) + "\n",
                                            encoding="utf-8")


def ecrire_bundle(dossier: Path) -> Path:
    """Regroupe tous les clips du dossier dans clips.js (global InkClips, ou module CommonJS).

    Les JSON valides qui ne sont pas un clip (catalogue, package.json, listes…) sont ignorés ;
    un JSON illisible arrête la génération (ErreurBVH) au lieu de faire disparaître un clip en silence.
    """
    clips = {}
    for chemin in sorted(dossier.glob("*.json")):
        if chemin.name == "catalogue.json":
            continue
        clip = _lire_json(chemin)
        if isinstance(clip, dict) and isinstance(clip.get("nom"), str) and isinstance(clip.get("images"), list):
            clips[clip["nom"]] = clip
    corps = json.dumps(clips, ensure_ascii=False, separators=(",", ":"))
    sortie = dossier / "clips.js"
    sortie.write_text(
        "/* Généré par 08-video/scripts/bvh2clip.py : ne pas éditer. Source et licence de chaque clip :\n"
        "   champs « source » et « licence » du clip, détail dans ../THIRD_PARTY_NOTICES.md. */\n"
        "(function (racine, clips) {\n"
        '  if (typeof module === "object" && module && module.exports) { module.exports = clips; }\n'
        "  else { racine.InkClips = clips; }\n"
        f'}})(typeof globalThis !== "undefined" ? globalThis : this, {corps});\n',
        encoding="utf-8")
    return sortie


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Convertit un BVH en clip 2D pour ink-theater.")
    p.add_argument("bvh", help="fichier BVH")
    p.add_argument("--nom", required=True,
                   help="nom du clip (minuscules et tirets : marche, coup-de-pied ; « catalogue » et « clips » réservés)")
    p.add_argument("--source", required=True, help='origine citée dans les notices, ex. "CMU 02_01"')
    p.add_argument("--plan", choices=("auto", "frontal", "sagittal"), default="auto")
    p.add_argument("--sur-place", action="store_true", help="annule le déplacement horizontal de la hanche")
    p.add_argument("--fps", type=float, default=30.0)
    p.add_argument("--debut", type=float, default=0.0, help="début de la fenêtre, en s")
    p.add_argument("--fin", type=float, help="fin de la fenêtre, en s (défaut : fin du fichier)")
    p.add_argument("--licence", default=LICENCE_CMU,
                   help="licence écrite dans le clip (défaut : licence de la base CMU)")
    p.add_argument("--sortie", default=str(SORTIE_DEFAUT))
    args = p.parse_args(argv)
    if not NOM_RE.fullmatch(args.nom):
        print(f"ERREUR : nom « {args.nom} » invalide (minuscules, chiffres et tirets)", file=sys.stderr)
        return 2
    if args.nom in NOMS_RESERVES:
        print(f"ERREUR : nom « {args.nom} » réservé (fichiers catalogue.json et clips.js du dossier) : "
              "en choisir un autre", file=sys.stderr)
        return 2
    if not (math.isfinite(args.fps) and args.fps > 0):
        print("ERREUR : --fps doit être un nombre positif et fini", file=sys.stderr)
        return 2
    dossier = Path(args.sortie)
    fichier = f"{args.nom}.json"
    try:
        bvh = lire_bvh(Path(args.bvh).read_text(encoding="utf-8-sig", errors="replace"))
        clip = convertir(bvh, nom=args.nom, source=args.source, fps=args.fps, debut=args.debut,
                         fin=args.fin, plan=args.plan, sur_place=args.sur_place, licence=args.licence)
        dossier.mkdir(parents=True, exist_ok=True)
        _lire_catalogue(dossier)      # un catalogue illisible arrête tout avant la moindre écriture
        (dossier / fichier).write_text(json.dumps(clip, ensure_ascii=False, separators=(",", ":")) + "\n",
                                       encoding="utf-8")
        mettre_a_jour_catalogue(dossier, clip, fichier)
        ecrire_bundle(dossier)
    except (ErreurBVH, OSError, ValueError) as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1
    print(f"{fichier} : {len(clip['images'])} images à {clip['fps']:g} i/s, plan {clip['plan']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
