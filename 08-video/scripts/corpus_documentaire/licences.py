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


# Tirets Unicode (U+2010 à U+2015, signe moins U+2212) : « CC BY‑NC » s'écrit souvent avec un tiret
# insécable ou demi-cadratin. Repliés sur « - » avant toute analyse, sinon la restriction passerait inaperçue.
_TIRETS = str.maketrans({c: "-" for c in "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"})
# « no derivs », « NoDerivatives », « non-derivative », « NonDerivs »…
_SANS_DERIVE = r"non?[\s-]?deriv"

# Mentions Creative Commons : abréviations collées à « CC BY », adresses de licence, noms en toutes lettres.
_CC_MENTION = re.compile(r"\bcc[\s-]*by((?:[\s-]+(?:nc|sa|nd))*)(?![a-z])")      # « cc by sand » n'est pas « sa nd »
_CC_ADRESSE = re.compile(r"licenses/by((?:-nc)?(?:-sa|-nd)?)/")
_CC_EN_TOUTES_LETTRES = re.compile(
    r"\bcc[\s-]*attribution|creative\s*commons[\s,:-]*attribution"
    rf"|attribution[\s-]*(?:non[\s-]?commercial|{_SANS_DERIVE}|share[\s-]?alike)")
# Restrictions écrites en toutes lettres : elles comptent même quand la mention s'arrête à « CC BY ».
_RESTRICTIONS = {
    "nc": re.compile(r"non[\s-]?commercial"),
    "nd": re.compile(_SANS_DERIVE),
    "sa": re.compile(r"share[\s-]?alike"),
}
# Un texte libre qui parle d'autre chose que du domaine public ne vaut pas domaine public.
_AUTRES_TERMES = re.compile(
    r"all rights reserved|tous droits|copyright|©|\bgfdl\b|\bgpl\b|\blgpl\b|\bmit\b|\bbsd\b|apache"
    rf"|attribution|creative\s*commons|\bcc\b|\bfal\b|free art|licen[cs]e|non[\s-]?commercial|{_SANS_DERIVE}"
    r"|share[\s-]?alike")


def _creative_commons(texte: str) -> str | None:
    """Identifiant cc-by… d'un texte qui nomme une licence Creative Commons, « inconnue » si elle est ambiguë."""
    identifications = {frozenset(m.group(1).split("-")[1:]) for m in _CC_ADRESSE.finditer(texte)}
    identifications |= {frozenset(re.findall(r"nc|sa|nd", m.group(1))) for m in _CC_MENTION.finditer(texte)}
    en_toutes_lettres = bool(_CC_EN_TOUTES_LETTRES.search(texte))
    if not identifications and not en_toutes_lettres:
        return None
    if len(identifications) > 1:                    # « CC BY 4.0 / CC BY-NC 3.0 » : on ne choisit pas la plus large
        return "inconnue"
    restrictions = set().union(*identifications) if identifications else set()
    restrictions |= {code for code, motif in _RESTRICTIONS.items() if motif.search(texte)}
    if {"sa", "nd"} <= restrictions:                # contradictoire
        return "inconnue"
    return "cc-by" + "".join(f"-{code}" for code in ("nc", "sa", "nd") if code in restrictions)


def normaliser(brute: str | list | None) -> str:
    """Identifiant canonique d'une mention de licence (texte libre, URL, ou liste de valeurs d'une API).

    Dans le doute, « inconnue » : une licence plus large que la vraie ferait entrer dans un film
    un plan dont l'usage commercial ou la modification est interdit.
    """
    if isinstance(brute, (list, tuple)):         # plusieurs valeurs : retenues seulement si elles s'accordent
        valeurs = {normaliser(v) for v in brute if v}
        return valeurs.pop() if len(valeurs) == 1 else "inconnue"
    if not brute or not isinstance(brute, str):
        return "inconnue"
    texte = brute.translate(_TIRETS).strip().lower()
    if texte in ("pexels", "pixabay"):
        return texte
    if "publicdomain/zero" in texte or re.search(r"\bcc0\b", texte) or "cc-zero" in texte:
        return "cc0"
    creative_commons = _creative_commons(texte)       # avant le domaine public : « CC BY-NC (œuvre dérivée du domaine public) »
    if creative_commons:
        return creative_commons
    if "publicdomain/mark" in texte:
        return "domaine-public"
    if texte in ("pd", "public-domain", "domaine public", "domaine-public"):
        return "domaine-public"
    if "public domain" in texte or "domaine public" in texte or texte.startswith("pd-"):
        reste = texte.replace("public domain", " ").replace("domaine public", " ")
        return "inconnue" if _AUTRES_TERMES.search(reste) else "domaine-public"
    return "inconnue"


def admise(licence: str, admises: frozenset[str] | set[str]) -> bool:
    return licence in admises


def attribution_exigee(licence: str) -> bool:
    return licence.startswith("cc-by")
