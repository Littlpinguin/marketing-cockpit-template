"""Pexels, vidéos (clé gratuite PEXELS_API_KEY, licence Pexels)."""
from __future__ import annotations

from urllib.parse import urlparse

from .. import reseau
from ..modeles import Resultat
from .base import Source, flottant


def _meilleur_fichier(fichiers: list[dict]) -> dict | None:
    mp4 = [f for f in fichiers if f.get("file_type") == "video/mp4" and f.get("link")]
    raisonnables = [f for f in mp4 if (f.get("width") or 0) <= 1920 and (f.get("height") or 0) <= 1920]
    return max(raisonnables or mp4, key=lambda f: (f.get("width") or 0) * (f.get("height") or 0), default=None)


def _titre(page: str) -> str:
    morceaux = [m for m in urlparse(page).path.split("/") if m]
    if not morceaux:
        return ""
    mots = morceaux[-1].split("-")
    if mots and mots[-1].isdigit():
        mots = mots[:-1]
    return " ".join(mots)


class Pexels(Source):
    nom = "pexels"
    cle_env = "PEXELS_API_KEY"
    URL = "https://api.pexels.com/videos/search"

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        donnees = reseau.obtenir_json(self.URL, {"query": requete, "per_page": max(1, min(n, 80))},
                                      {"Authorization": self.cle})
        resultats = []
        for video in donnees.get("videos", [])[:n]:
            fichier = _meilleur_fichier(video.get("video_files", []))
            if not fichier:
                continue
            resultats.append(Resultat(
                source=self.nom, id=str(video["id"]), titre=_titre(video.get("url", "")),
                auteur=(video.get("user") or {}).get("name", ""), page=video.get("url", ""),
                url_fichier=fichier["link"], licence="pexels", licence_brute="Pexels License",
                duree=flottant(video.get("duration")), requete=requete))
        return resultats
