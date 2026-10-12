"""Résultat de recherche d'une source d'archives, et sa fiche."""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass


@dataclass
class Resultat:
    source: str
    id: str
    titre: str
    auteur: str
    page: str
    url_fichier: str
    licence: str            # identifiant canonique (licences.normaliser)
    licence_brute: str      # mention d'origine, gardée pour les crédits
    duree: float | None = None
    requete: str = ""
    emplacement: str = ""

    @property
    def nom_fichier(self) -> str:
        """Nom de base sûr pour le disque : <source>-<id>."""
        return f"{self.source}-{re.sub(r'[^A-Za-z0-9._-]+', '_', self.id)[:80]}"

    def fiche(self) -> dict:
        return asdict(self)
