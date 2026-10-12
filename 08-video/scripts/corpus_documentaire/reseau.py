"""Accès réseau du corpus : JSON et téléchargements, avec politesse envers les API.

Les messages d'erreur ne citent que l'URL de base, jamais ses paramètres (une
clé d'API peut y figurer). Seuls les schémas http et https sont suivis : une
réponse d'API ne doit jamais pouvoir faire lire un fichier local (file://).
"""
from __future__ import annotations

import http.client
import json
import shutil
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "marketing-cockpit-template-corpus/1.0 (+https://github.com/Littlpinguin/marketing-cockpit-template)"
PAUSE = 0.5
SCHEMAS = ("http", "https")


class ErreurReseau(Exception):
    """Requête en échec (HTTP, délai, réponse illisible)."""


def _url(url: str, params: dict | None) -> str:
    return url + ("?" + urllib.parse.urlencode(params, doseq=True) if params else "")


def _base(url: str) -> str:
    """L'URL sans paramètres ni fragment : seule forme qui figure dans un message."""
    return url.split("?")[0].split("#")[0]


def _verifier_schema(url: str) -> None:
    try:
        schema = urllib.parse.urlsplit(url).scheme.lower()
    except ValueError:
        schema = ""
    if schema not in SCHEMAS:
        raise ErreurReseau(f"{_base(url)} : adresse refusée (http et https seulement)")


def _longueur_annoncee(reponse) -> int | None:
    """Content-Length si le serveur en donne une utilisable, sinon None (transfert en morceaux, en-tête absent)."""
    entetes = getattr(reponse, "headers", None)
    try:
        longueur = int(entetes.get("Content-Length")) if entetes is not None else None
    except (TypeError, ValueError):
        return None
    return longueur if longueur is not None and longueur >= 0 else None


def obtenir_json(url: str, params: dict | None = None, entetes: dict | None = None, delai: int = 30) -> Any:
    _verifier_schema(url)
    try:
        requete = urllib.request.Request(_url(url, params), headers={"User-Agent": USER_AGENT, **(entetes or {})})
        with urllib.request.urlopen(requete, timeout=delai) as reponse:
            donnees = json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        time.sleep(PAUSE)       # après un refus (429 surtout), ne pas relancer la requête suivante aussitôt
        raise ErreurReseau(f"HTTP {err.code} sur {_base(url)}") from None
    except (OSError, http.client.HTTPException, ValueError) as err:     # URLError, délai, coupure, JSON, UTF-8
        raise ErreurReseau(f"{_base(url)} : {type(err).__name__}") from None
    time.sleep(PAUSE)
    return donnees


def telecharger(url: str, destination: Path, delai: int = 120) -> Path:
    _verifier_schema(url)
    partiel = destination.with_name(destination.name + ".part")
    try:
        requete = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(requete, timeout=delai) as reponse, partiel.open("wb") as sortie:
            annonce = _longueur_annoncee(reponse)
            shutil.copyfileobj(reponse, sortie)
        recu = partiel.stat().st_size
        # Une coupure en route n'est pas toujours une exception : on compare à ce que le serveur annonçait.
        if recu == 0:
            probleme = "fichier vide"
        elif annonce is not None and recu != annonce:
            probleme = f"téléchargement incomplet ({recu} octets reçus sur {annonce})"
        else:
            probleme = ""
        if probleme:
            partiel.unlink(missing_ok=True)
            raise ErreurReseau(f"{_base(url)} : {probleme}")
        partiel.replace(destination)
    except urllib.error.HTTPError as err:
        partiel.unlink(missing_ok=True)
        time.sleep(PAUSE)
        raise ErreurReseau(f"HTTP {err.code} sur {_base(url)}") from None
    except (OSError, http.client.HTTPException, ValueError) as err:
        partiel.unlink(missing_ok=True)
        raise ErreurReseau(f"{_base(url)} : {type(err).__name__}") from None
    time.sleep(PAUSE)
    return destination
