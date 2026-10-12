"""Pixabay, vidéos (clé gratuite PIXABAY_API_KEY, licence Pixabay)."""
from __future__ import annotations

from .. import reseau
from ..modeles import Resultat
from .base import Source, flottant


class Pixabay(Source):
    nom = "pixabay"
    cle_env = "PIXABAY_API_KEY"
    URL = "https://pixabay.com/api/videos/"

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        donnees = reseau.obtenir_json(self.URL, {"key": self.cle, "q": requete,
                                                 "per_page": max(3, min(n, 200)), "safesearch": "true"})
        resultats = []
        for hit in donnees.get("hits", [])[:n]:
            videos = hit.get("videos") or {}
            fichier = next((videos[t] for t in ("large", "medium", "small")
                            if (videos.get(t) or {}).get("url")), None)
            if not fichier:
                continue
            resultats.append(Resultat(
                source=self.nom, id=str(hit["id"]), titre=hit.get("tags", ""), auteur=hit.get("user", ""),
                page=hit.get("pageURL", ""), url_fichier=fichier["url"], licence="pixabay",
                licence_brute="Pixabay Content License", duree=flottant(hit.get("duration")),
                requete=requete))
        return resultats
