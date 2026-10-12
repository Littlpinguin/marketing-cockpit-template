"""Registre des sources d'archives."""
from __future__ import annotations

from .archive import Archive
from .base import Source
from .nasa import Nasa
from .pexels import Pexels
from .pixabay import Pixabay
from .wikimedia import Wikimedia

SOURCES: dict[str, type[Source]] = {
    "pexels": Pexels, "pixabay": Pixabay, "archive": Archive, "wikimedia": Wikimedia, "nasa": Nasa,
}


def construire(noms: list[str], env: dict[str, str]) -> list[Source]:
    """Instancie les sources demandées, avec leur clé lue dans `env` quand elles en exigent une."""
    instances = []
    for nom in noms:
        classe = SOURCES[nom]
        instances.append(classe(env.get(classe.cle_env) if classe.cle_env else None))
    return instances
