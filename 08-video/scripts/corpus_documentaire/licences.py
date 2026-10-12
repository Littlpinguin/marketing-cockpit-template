"""Licences des archives : normalisation, filtre, libellés pour les crédits."""
from __future__ import annotations

import re

ADMISES_DEFAUT = frozenset({"domaine-public", "cc0", "cc-by", "pexels", "pixabay"})
CONNUES = ADMISES_DEFAUT | {"cc-by-sa", "cc-by-nc", "cc-by-nd", "cc-by-nc-sa", "cc-by-nc-nd", "inconnue"}
LIBELLES = {
    "domaine-public": "domaine public",
    "cc0": "CC0",
    "cc-by": "CC BY",
    "cc-by-sa": "CC BY-SA",
    "cc-by-nc": "CC BY-NC",
    "cc-by-nd": "CC BY-ND",
    "cc-by-nc-sa": "CC BY-NC-SA",
    "cc-by-nc-nd": "CC BY-NC-ND",
    "pexels": "licence Pexels",
    "pixabay": "licence Pixabay",
    "inconnue": "licence inconnue",
}


def normaliser(brute: str | list | None) -> str:
    """Identifiant canonique d'une mention de licence (texte libre, URL, ou liste de valeurs d'une API)."""
    if isinstance(brute, (list, tuple)):         # plusieurs valeurs : retenues seulement si elles s'accordent
        valeurs = {normaliser(v) for v in brute if v}
        return valeurs.pop() if len(valeurs) == 1 else "inconnue"
    if not brute or not isinstance(brute, str):
        return "inconnue"
    texte = brute.strip().lower()
    if texte in ("pexels", "pixabay"):
        return texte
    if "publicdomain/zero" in texte or re.search(r"\bcc0\b", texte) or "cc-zero" in texte:
        return "cc0"
    if ("publicdomain/mark" in texte or "public domain" in texte or texte.startswith("pd-")
            or texte in ("pd", "public-domain", "domaine public", "domaine-public")):
        return "domaine-public"
    url = re.search(r"licenses/(by(?:-nc)?(?:-sa|-nd)?)/", texte)
    if url:
        return "cc-" + url.group(1)
    mention = re.search(r"\bcc[\s-]*(by(?:[\s-]*nc)?(?:[\s-]*(?:sa|nd))?)\b", texte)
    if mention:
        return "cc-" + re.sub(r"[\s-]+", "-", mention.group(1))
    return "inconnue"


def admise(licence: str, admises: frozenset[str] | set[str]) -> bool:
    return licence in admises


def attribution_exigee(licence: str) -> bool:
    return licence.startswith("cc-by")
