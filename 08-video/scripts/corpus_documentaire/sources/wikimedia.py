"""Wikimedia Commons, fichiers vidéo (sans clé ; webm et ogv convertis en mp4 au téléchargement)."""
from __future__ import annotations

import html
import re

from .. import reseau
from ..licences import normaliser
from ..modeles import Resultat
from .base import Source, flottant


def _sans_html(texte: str) -> str:
    """Texte brut d'un champ HTML de Commons : balises retirées d'abord, puis entités décodées."""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", texte or ""))).strip()


class Wikimedia(Source):
    nom = "wikimedia"
    URL = "https://commons.wikimedia.org/w/api.php"

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        donnees = reseau.obtenir_json(self.URL, {
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"{requete} filetype:video", "gsrnamespace": 6, "gsrlimit": n,
            "prop": "imageinfo", "iiprop": "url|extmetadata|size|mediatype",
            "iiextmetadatafilter": "LicenseShortName|Artist|ObjectName|LicenseUrl"})
        pages = sorted(((donnees.get("query") or {}).get("pages") or {}).values(), key=lambda p: p.get("index", 0))
        resultats = []
        for page in pages[:n]:
            info = (page.get("imageinfo") or [{}])[0]
            if not info.get("url"):
                continue
            meta = info.get("extmetadata") or {}
            brute = (meta.get("LicenseShortName") or {}).get("value") or (meta.get("LicenseUrl") or {}).get("value", "")
            titre = _sans_html((meta.get("ObjectName") or {}).get("value", "")) or page.get("title", "")
            resultats.append(Resultat(
                source=self.nom, id=str(page.get("pageid")), titre=titre,
                auteur=_sans_html((meta.get("Artist") or {}).get("value", "")),
                page=info.get("descriptionurl", ""), url_fichier=info["url"], licence=normaliser(brute),
                licence_brute=brute, duree=flottant(info.get("duration")), requete=requete))
        return resultats
