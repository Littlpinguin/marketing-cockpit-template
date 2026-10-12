"""NASA Image and Video Library (sans clé ; contenus NASA généralement libres de droits)."""
from __future__ import annotations

from .. import reseau
from ..modeles import Resultat
from .base import Source

PREFERENCES = ("~medium.mp4", "~mobile.mp4", "~small.mp4", "~orig.mp4")


def _mp4(urls: list[str]) -> str | None:
    for suffixe in PREFERENCES:
        for url in urls:
            if isinstance(url, str) and url.endswith(suffixe):
                return url.replace("http://", "https://", 1).replace(" ", "%20")
    return None


class Nasa(Source):
    nom = "nasa"
    URL = "https://images-api.nasa.gov/search"

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        donnees = reseau.obtenir_json(self.URL, {"q": requete, "media_type": "video",
                                                 "page_size": max(1, min(n, 100))})
        resultats = []
        for item in ((donnees.get("collection") or {}).get("items") or [])[:n]:
            data = (item.get("data") or [{}])[0]
            ident, manifeste = data.get("nasa_id"), item.get("href")
            if not ident or not manifeste:
                continue
            try:
                url = _mp4(reseau.obtenir_json(manifeste))
            except reseau.ErreurReseau:
                continue        # un manifeste en panne ne fait pas perdre les autres résultats de la requête
            if not url:
                continue
            resultats.append(Resultat(
                source=self.nom, id=ident, titre=data.get("title", ""), auteur=data.get("center") or "NASA",
                page=f"https://images.nasa.gov/details/{ident}", url_fichier=url, licence="domaine-public",
                licence_brute="NASA media usage guidelines (public domain unless noted)", requete=requete))
        return resultats
