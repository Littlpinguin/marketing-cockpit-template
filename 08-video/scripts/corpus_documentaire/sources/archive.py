"""Internet Archive, films du domaine public et Creative Commons (sans clé)."""
from __future__ import annotations

from urllib.parse import quote

from .. import reseau
from ..licences import normaliser
from ..modeles import Resultat
from .base import Source, flottant

TAILLE_MAX = 300_000_000


def _texte(valeur) -> str:
    if isinstance(valeur, list):
        return ", ".join(str(v) for v in valeur)
    return str(valeur or "")


def _duree(valeur) -> float | None:
    if isinstance(valeur, str) and ":" in valeur:
        secondes = 0.0
        try:
            for morceau in valeur.split(":"):
                secondes = secondes * 60 + float(morceau)
        except ValueError:
            return None
        return secondes
    return flottant(valeur)


def _taille(fichier: dict) -> int | None:
    try:
        return int(fichier.get("size") or 0)
    except (TypeError, ValueError):
        return None


def _mp4(fichiers: list[dict]) -> dict | None:
    mp4 = [f for f in fichiers if str(f.get("name", "")).lower().endswith(".mp4")
           and _taille(f) is not None and _taille(f) <= TAILLE_MAX]
    return max(mp4, key=_taille, default=None)


class Archive(Source):
    nom = "archive"
    RECHERCHE = "https://archive.org/advancedsearch.php"
    METADONNEES = "https://archive.org/metadata/"

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        q = (f"({requete}) AND mediatype:(movies) AND "
             "licenseurl:(*publicdomain* OR *creativecommons.org/licenses/by/*)")
        donnees = reseau.obtenir_json(self.RECHERCHE, {"q": q, "fl[]": ["identifier", "title", "creator", "licenseurl"],
                                                       "rows": n, "output": "json"})
        resultats = []
        for doc in (donnees.get("response") or {}).get("docs", [])[:n]:
            ident = doc.get("identifier")
            if not ident:
                continue
            try:
                meta = reseau.obtenir_json(self.METADONNEES + quote(ident))
            except reseau.ErreurReseau:
                continue        # une fiche en panne ne fait pas perdre les autres résultats de la requête
            fichier = _mp4(meta.get("files", []))
            if not fichier:
                continue
            brute = doc.get("licenseurl") or (meta.get("metadata") or {}).get("licenseurl", "")
            resultats.append(Resultat(
                source=self.nom, id=ident, titre=_texte(doc.get("title")), auteur=_texte(doc.get("creator")),
                page=f"https://archive.org/details/{ident}",
                url_fichier=f"https://archive.org/download/{ident}/{quote(fichier['name'])}",
                licence=normaliser(brute), licence_brute=_texte(brute), duree=_duree(fichier.get("length")),
                requete=requete))
        return resultats
