"""Interface commune des sources d'archives."""
from __future__ import annotations

import math

from ..modeles import Resultat


def flottant(valeur) -> float | None:
    """Nombre fini ou None : une durée « nan », « inf » ou illisible n'est pas une durée."""
    try:
        nombre = float(valeur)
    except (TypeError, ValueError):
        return None
    return nombre if math.isfinite(nombre) else None


class Source:
    nom = ""
    cle_env: str | None = None      # variable d'environnement de la clé, si la source en exige une

    def __init__(self, cle: str | None = None):
        self.cle = cle

    def disponible(self) -> tuple[bool, str]:
        if self.cle_env and not self.cle:
            return False, f"{self.cle_env} absent de l'environnement et de .env (clé gratuite)"
        return True, ""

    def rechercher(self, requete: str, n: int) -> list[Resultat]:
        raise NotImplementedError
