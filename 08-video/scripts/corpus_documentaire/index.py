"""Index CLIP d'un corpus et recherche par description textuelle.

L'encodeur réel (open_clip) n'est importé qu'à la demande ; tout le reste est
en bibliothèque standard. Les vecteurs sont normalisés puis stockés à la suite
en float32 (index.f32), leurs métadonnées dans index.json.
"""
from __future__ import annotations

import json
import math
from array import array
from pathlib import Path

from . import images_cles

INSTALLATION = "pip install -r 08-video/requirements-corpus.txt"


class ErreurFiche(ValueError):
    """Fiche de clip illisible (JSON invalide ou qui n'est pas un objet) : donnée du corpus à corriger."""


class DependanceManquante(Exception):
    """open_clip, torch ou pillow absent, ou modèle CLIP impossible à charger."""


class EncodeurClip:
    def __init__(self, modele: str = "ViT-B-32", poids: str = "laion2b_s34b_b79k"):
        try:
            import open_clip
            import torch
            from PIL import Image
        except (ImportError, OSError) as err:       # OSError : bibliothèque native de torch absente ou cassée
            raise DependanceManquante(
                f"open_clip, torch et pillow sont requis pour index et search : {INSTALLATION}") from err
        self.nom = f"{modele}/{poids}"
        self._torch, self._image = torch, Image
        try:
            self._modele, _, self._pretraitement = open_clip.create_model_and_transforms(modele, pretrained=poids)
            self._modele.eval()
            self._jetons = open_clip.get_tokenizer(modele)
        except Exception as err:                    # nom de modèle inconnu, poids non téléchargeables, réseau
            raise DependanceManquante(
                f"modèle CLIP {modele} ({poids}) indisponible : {type(err).__name__} : {str(err)[:200]}") from err

    def _charger(self, chemin: Path):
        with self._image.open(chemin) as image:
            return self._pretraitement(image.convert("RGB"))

    def images(self, chemins: list[Path]) -> list[list[float]]:
        vecteurs: list[list[float]] = []
        with self._torch.no_grad():
            for debut in range(0, len(chemins), 32):
                lot = self._torch.stack([self._charger(c) for c in chemins[debut:debut + 32]])
                v = self._modele.encode_image(lot)
                vecteurs += (v / v.norm(dim=-1, keepdim=True)).tolist()
        return vecteurs

    def texte(self, texte: str) -> list[float]:
        with self._torch.no_grad():
            v = self._modele.encode_text(self._jetons([texte]))
            return (v / v.norm(dim=-1, keepdim=True))[0].tolist()


def _normaliser(v: list[float]) -> list[float]:
    norme = math.sqrt(sum(x * x for x in v)) or 1.0
    return [x / norme for x in v]


def _ecrire(chemin: Path, contenu: bytes) -> None:
    """Écriture atomique : un index à moitié écrit ne doit jamais remplacer un index sain."""
    temporaire = chemin.with_name(chemin.name + ".tmp")
    temporaire.write_bytes(contenu)
    temporaire.replace(chemin)


def construire_index(dossier: Path, encodeur, *, extraire=images_cles.extraire, intervalle: float = 3.0,
                     avertir=None) -> int:
    """Index des images clés de clips/*.mp4 ; rend le nombre d'images.

    `avertir(message)` reçoit une ligne par clip dont aucune image clé n'a pu être
    extraite (fichier illisible) : ce clip n'est pas dans l'index, ce qui ne doit
    jamais passer inaperçu.
    """
    clips = sorted((dossier / "clips").glob("*.mp4"))
    if not clips:
        raise ValueError("aucun clip dans clips/ : constituer d'abord le corpus (corpus.py build)")
    images = dossier / "images"
    images.mkdir(exist_ok=True)
    entrees = []
    for clip in clips:
        trouvees = extraire(clip, images, intervalle)
        if not trouvees and avertir:
            avertir(f"{clip.name} : aucune image clé extraite (fichier illisible ?), clip absent de l'index")
        for t, chemin in trouvees:
            entrees.append({"clip": clip.name, "t": t, "image": chemin.name})
    if not entrees:
        raise ValueError(f"aucune image clé extraite de {len(clips)} clip(s) : fichiers illisibles ? "
                         "relancer corpus.py build, ou vérifier ffmpeg")
    vecteurs = encodeur.images([images / e["image"] for e in entrees])
    if len(vecteurs) != len(entrees):
        raise ValueError(f"encodeur {encodeur.nom} : {len(vecteurs)} vecteur(s) pour {len(entrees)} image(s)")
    dimension = len(vecteurs[0])
    if dimension == 0 or any(len(v) != dimension for v in vecteurs):
        raise ValueError(f"encodeur {encodeur.nom} : vecteurs de dimensions différentes ou vides")
    tableau = array("f")
    for vecteur in vecteurs:
        tableau.extend(_normaliser(vecteur))
    _ecrire(dossier / "index.f32", tableau.tobytes())
    _ecrire(dossier / "index.json", (json.dumps({"encodeur": encodeur.nom, "dimension": dimension,
                                                 "images": entrees}, ensure_ascii=False, indent=1) + "\n"
                                     ).encode("utf-8"))
    return len(entrees)


def _lire_index(dossier: Path) -> tuple[dict, array]:
    """index.json et index.f32, vérifiés l'un contre l'autre ; ValueError si l'un est abîmé."""
    abime = "index abîmé ({}) : reconstruire l'index (corpus.py index)"
    try:
        meta = json.loads((dossier / "index.json").read_text(encoding="utf-8"))
        encodeur, dimension, entrees = meta["encodeur"], meta["dimension"], meta["images"]
        valide = (isinstance(encodeur, str) and isinstance(dimension, int) and dimension > 0
                  and isinstance(entrees, list)
                  and all(isinstance(e, dict) and {"clip", "t", "image"} <= e.keys() for e in entrees))
    except (ValueError, KeyError, TypeError) as err:       # JSON ou UTF-8 invalide, clé absente, mauvais type
        raise ValueError(abime.format(f"index.json : {type(err).__name__}")) from None
    if not valide:
        raise ValueError(abime.format("index.json : structure inattendue"))
    tableau = array("f")
    try:
        tableau.frombytes((dossier / "index.f32").read_bytes())
    except ValueError:                                     # longueur qui n'est pas un multiple de 4 octets
        raise ValueError(abime.format("index.f32 tronqué")) from None
    if len(tableau) != dimension * len(entrees):
        raise ValueError(abime.format("index.f32 ne correspond pas à index.json"))
    return meta, tableau


def _lire_fiche(chemin: Path) -> dict | None:
    """La fiche d'un clip, None s'il n'en a pas ; ErreurFiche si elle existe mais est inutilisable."""
    if not chemin.exists():
        return None
    try:
        fiche = json.loads(chemin.read_text(encoding="utf-8"))
    except ValueError as err:
        raise ErreurFiche(f"fiche {chemin.name} illisible : {err}") from None
    if not isinstance(fiche, dict):
        raise ErreurFiche(f"fiche {chemin.name} illisible : un objet JSON est attendu")
    return fiche


def rechercher(dossier: Path, texte: str, encodeur, top: int = 5) -> list[dict]:
    if top < 1:
        raise ValueError("top doit valoir au moins 1")
    meta, tableau = _lire_index(dossier)
    if meta["encodeur"] != encodeur.nom:
        raise ValueError(f"index construit avec {meta['encodeur']}, recherche avec {encodeur.nom} : "
                         "reconstruire l'index (corpus.py index)")
    requete = _normaliser(encodeur.texte(texte))
    dimension = meta["dimension"]
    if len(requete) != dimension:
        raise ValueError(f"la requête a {len(requete)} dimension(s), l'index {dimension} : "
                         "reconstruire l'index (corpus.py index)")
    meilleurs: dict[str, dict] = {}
    for i, entree in enumerate(meta["images"]):
        vecteur = tableau[i * dimension:(i + 1) * dimension]
        score = sum(a * b for a, b in zip(requete, vecteur))
        if entree["clip"] not in meilleurs or score > meilleurs[entree["clip"]]["score"]:
            meilleurs[entree["clip"]] = {"clip": entree["clip"], "t": entree["t"],
                                         "score": round(score, 4), "image": entree["image"]}
    resultats = sorted(meilleurs.values(), key=lambda r: -r["score"])[:top]
    for resultat in resultats:
        resultat["fiche"] = _lire_fiche(dossier / "clips" / (Path(resultat["clip"]).stem + ".json"))
    return resultats
