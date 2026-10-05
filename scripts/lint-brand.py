#!/usr/bin/env python3
"""
Linter de marque déterministe.

Contrôle mécaniquement ce que la doctrine de `01-brand/` énonce en toutes
lettres : vocabulaire interdit, tirets longs, ponctuation des titres, hashtags,
placeholders résiduels, couleurs hors palette, polices hors marque, et patrons
de parallélisme négatif. Aucun jugement de goût : chaque constat renvoie à une
règle écrite quelque part.

Le code ne connaît aucune marque. La palette et les polices admises viennent de
`01-brand/tokens.json` (créé par /brand-discover), jamais d'une valeur recopiée
ici. Les listes de mots, les tirets visés, les dossiers et les règles actives
vivent dans `scripts/lint-brand.toml`. Tant que tokens.json manque ou porte
encore des placeholders, les deux règles graphiques (off-palette, font-family)
sont suspendues et un avertissement « palette » le dit ; les règles de texte
s'appliquent normalement.

Usage :
  python3 scripts/lint-brand.py                        # tout le dépôt
  python3 scripts/lint-brand.py 03-social-media 04-email
  python3 scripts/lint-brand.py --only dashes,hashtags
  python3 scripts/lint-brand.py --skip off-palette
  python3 scripts/lint-brand.py --format json
  python3 scripts/lint-brand.py --warnings-as-errors

Code de sortie : 1 si au moins une erreur (ou un avertissement avec
--warnings-as-errors), 2 si l'invocation est fautive, 0 sinon.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from bisect import bisect_right
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterator, NamedTuple

try:
    import tomllib
except ModuleNotFoundError:    # tomllib est entré dans la bibliothèque standard en 3.11
    print(f"ERREUR : Python 3.11 ou plus récent est requis (module « tomllib » absent) ; "
          f"version courante : {sys.version.split()[0]}.", file=sys.stderr)
    raise SystemExit(2)

RACINE_DEFAUT = Path(__file__).resolve().parents[1]
CONFIG_DEFAUT = Path(__file__).resolve().parent / "lint-brand.toml"
TOKENS_REL = "01-brand/tokens.json"
EXTENSION = "cockpit"    # espace de noms des métadonnées sous $extensions
PLACEHOLDER_RE = re.compile(r"\{\{\s*[A-Z][A-Z0-9_]*\s*\}\}")
# Règles qui lisent tokens.json : suspendues tant que la palette est indisponible.
REGLES_GRAPHIQUES = ("off-palette", "font-family")

ERREUR = "error"
AVERTISSEMENT = "warning"
LIBELLE_NIVEAU = {ERREUR: "erreur", AVERTISSEMENT: "avertissement"}
RANG_NIVEAU = {ERREUR: 2, AVERTISSEMENT: 1}


class LintError(Exception):
    """Configuration, palette ou invocation inutilisable."""


class Constat(NamedTuple):
    fichier: str          # chemin relatif à la racine
    ligne: int
    regle: str
    niveau: str           # ERREUR ou AVERTISSEMENT
    message: str
    extrait: str = ""     # texte exactement mis en cause, quand il existe
    colonne: int = 0      # 1 pour le premier caractère, 0 quand la règle ne situe rien


# --------------------------------------------------------------------------
# Couleur : sRGB vers Lab (D65) et ΔE76, en pur Python
# --------------------------------------------------------------------------

# Blanc de référence D65, observateur 2 degrés.
BLANC_D65 = (95.047, 100.000, 108.883)


@lru_cache(maxsize=8192)
def developper_hex(valeur: str) -> str:
    """Rend un #RRGGBB majuscule depuis #RGB, #RRGGBB ou #RRGGBBAA."""
    brut = valeur.lstrip("#")
    if len(brut) == 3:
        brut = "".join(c * 2 for c in brut)
    elif len(brut) == 8:
        brut = brut[:6]
    if len(brut) != 6:
        raise LintError(f"hex non développable : {valeur!r}")
    return "#" + brut.upper()


def _canal_lineaire(canal: float) -> float:
    return canal / 12.92 if canal <= 0.04045 else ((canal + 0.055) / 1.055) ** 2.4


def _pivot_lab(t: float) -> float:
    return t ** (1 / 3) if t > 216 / 24389 else (841 / 108) * t + 4 / 29


@lru_cache(maxsize=8192)
def hex_vers_lab(valeur: str) -> tuple[float, float, float]:
    """Convertit un hex sRGB en L*a*b* (D65), par la formule standard."""
    hexa = developper_hex(valeur)
    r, g, b = (_canal_lineaire(int(hexa[i:i + 2], 16) / 255) for i in (1, 3, 5))
    x = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) * 100
    y = (0.2126729 * r + 0.7151522 * g + 0.0721750 * b) * 100
    z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) * 100
    fx, fy, fz = (_pivot_lab(c / w) for c, w in zip((x, y, z), BLANC_D65))
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def delta_e76(premier: str, second: str) -> float:
    """Distance CIE76 entre deux hex : la tolérance de la doctrine s'y exprime."""
    l1, a1, b1 = hex_vers_lab(premier)
    l2, a2, b2 = hex_vers_lab(second)
    return ((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5


# --------------------------------------------------------------------------
# Palette : lecture de tokens.json et portée des tokens
# --------------------------------------------------------------------------

class TokenCouleur(NamedTuple):
    nom: str
    hexa: str
    scope: tuple[str, ...]    # vide = palette de marque, admise partout
    delta_max: float

    def admis_dans(self, rel: str) -> bool:
        if not self.scope:
            return True
        return any(rel == d or rel.startswith(d.rstrip("/") + "/") for d in self.scope)


class Palette(NamedTuple):
    couleurs: list[TokenCouleur]
    polices: frozenset[str]   # familles déclarées dans le groupe « font », en minuscules


class PaletteIndisponible(Exception):
    """tokens.json absent ou pas encore rempli : état normal avant le wizard."""


# Familles CSS génériques : jamais une police de marque.
FAMILLES_GENERIQUES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
    "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded",
}


def charger_palette(chemin: Path, delta_defaut: float) -> Palette:
    """Relève les couleurs (avec leur portée) et les polices de tokens.json.

    Lève PaletteIndisponible si le fichier manque ou porte encore des
    placeholders ; LintError s'il existe mais qu'il est inexploitable.
    """
    if not chemin.exists():
        raise PaletteIndisponible(f"{chemin.name} introuvable")
    texte = chemin.read_text(encoding="utf-8")
    try:
        tokens = json.loads(texte)
    except json.JSONDecodeError as err:
        raise LintError(f"{chemin} n'est pas un JSON valide : {err}") from err

    couleurs: list[TokenCouleur] = []
    polices: set[str] = set()
    residus: list[str] = []

    def descendre(noeud: dict[str, Any], chemin_token: tuple[str, ...]) -> None:
        groupe = chemin_token[0]
        if "$value" in noeud:
            valeur = noeud["$value"]
            if PLACEHOLDER_RE.search(json.dumps(valeur, ensure_ascii=False)):
                residus.append(".".join(chemin_token))
                return
            if groupe == "color" and isinstance(valeur, str) and valeur.startswith("#"):
                meta = noeud.get("$extensions", {}).get(EXTENSION, {})
                couleurs.append(TokenCouleur(
                    nom=".".join(chemin_token[1:]),
                    hexa=developper_hex(valeur),
                    scope=tuple(meta.get("scope", ())),
                    delta_max=float(meta.get("deltaE_max", delta_defaut)),
                ))
            elif groupe == "font" and isinstance(valeur, list):
                polices.update(
                    f.strip().lower() for f in valeur
                    if isinstance(f, str) and f.strip().lower() not in FAMILLES_GENERIQUES
                )
            return
        for cle, enfant in noeud.items():
            if cle.startswith("$") or not isinstance(enfant, dict):
                continue
            descendre(enfant, chemin_token + (cle,))

    for groupe in ("color", "font"):
        if isinstance(tokens.get(groupe), dict):
            descendre(tokens[groupe], (groupe,))
    if residus:
        raise PaletteIndisponible(
            f"{chemin.name} porte encore des placeholders ({', '.join(sorted(residus))})"
        )
    if not couleurs:
        raise LintError(f"aucune couleur trouvée dans {chemin}")
    return Palette(couleurs, frozenset(polices))


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def _motif_mot(mot: str) -> str:
    """Mot entier, espaces souples, apostrophe droite (le texte est normalisé)."""
    return r"\b" + re.escape(mot).replace(r"\ ", r"\s+") + r"\b"


def _motif_verbe(verbe: str) -> str:
    """Verbe et ses flexions simples : s, es, ed, ing."""
    if verbe.endswith("e"):
        return r"\b" + re.escape(verbe[:-1]) + r"(?:e|es|ed|ing)\b"
    return r"\b" + re.escape(verbe) + r"(?:s|es|ed|ing)?\b"


def _compiler_groupe(bloc: dict[str, Any]) -> re.Pattern[str] | None:
    morceaux = [_motif_mot(m) for m in bloc.get("words", ())]
    morceaux += [_motif_verbe(v) for v in bloc.get("verbs", ())]
    morceaux += [_motif_mot(p) for p in bloc.get("phrases", ())]
    if not morceaux:
        return None
    # Les alternatives longues d'abord : « ressources humaines » avant « ressources ».
    morceaux.sort(key=len, reverse=True)
    return re.compile("|".join(morceaux), re.IGNORECASE)


def charger_config(chemin: Path, racine: Path) -> dict[str, Any]:
    """Lit le TOML, compile les motifs, et attache la palette et la racine."""
    if not chemin.exists():
        raise LintError(f"configuration introuvable : {chemin}")
    try:
        config = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise LintError(f"{chemin} n'est pas un TOML valide : {err}") from err

    mots = config.get("forbidden-words", {})
    compile_: dict[str, Any] = {
        "charter": _compiler_groupe(mots.get("charter", {})),
        "tolerated": _compiler_groupe(mots.get("tolerated", {})),
        "ai": _compiler_groupe(mots.get("ai", {})),
        "negative": [],
    }
    for patron in config.get("negative-parallelism", {}).get("patterns", []):
        try:
            compile_["negative"].append((patron["label"], re.compile(patron["regex"])))
        except (KeyError, re.error) as err:
            raise LintError(f"patron de parallélisme négatif invalide : {err}") from err

    config["_compile"] = compile_
    config["_racine"] = racine
    tokens_rel = config.get("general", {}).get("tokens", TOKENS_REL)
    config["_tokens_rel"] = tokens_rel
    try:
        palette = charger_palette(
            racine / tokens_rel,
            float(config.get("off-palette", {}).get("delta_e_max", 2.0)),
        )
        config["_palette"] = palette.couleurs
        config["_polices"] = palette.polices
        config["_palette_absente"] = None
    except PaletteIndisponible as raison:
        config["_palette"] = None
        config["_polices"] = frozenset()
        config["_palette_absente"] = str(raison)
    return config


def regle_active(config: dict[str, Any], nom: str) -> bool:
    """Une règle est active sauf si sa section porte `enabled = false`."""
    section = config.get(nom, {})
    return not isinstance(section, dict) or section.get("enabled", True) is not False


def exclusions_production(config: dict[str, Any]) -> list[str]:
    """Chemins soustraits aux règles graphiques : code tiers, gabarits, archives."""
    return config.get("general", {}).get("exclude_paths_production", [])


def sous_chemin(rel: str, prefixes: list[str]) -> bool:
    """Vrai si le chemin relatif est l'un des préfixes ou vit dessous."""
    for prefixe in prefixes:
        net = prefixe.rstrip("/")
        if rel == net or rel.startswith(net + "/"):
            return True
    return False


# --------------------------------------------------------------------------
# Découpage du texte : ce qui ne se lit pas comme de la prose
# --------------------------------------------------------------------------

SEPARATEUR_TABLEAU_RE = re.compile(r"^\s*\|?[\s:|-]*-[\s:|-]*\|[\s:|-]*$")


@lru_cache(maxsize=16)
def lignes(texte: str) -> tuple[str, ...]:
    return tuple(texte.splitlines())


@lru_cache(maxsize=16)
def _debuts_de_ligne(texte: str) -> tuple[int, ...]:
    """Position de départ de chaque ligne, pour convertir un offset en numéro.

    Le tableau est construit une fois par fichier : compter les sauts de ligne
    à chaque correspondance rendrait le parcours quadratique.
    """
    debuts = [0]
    position = texte.find("\n")
    while position >= 0:
        debuts.append(position + 1)
        position = texte.find("\n", position + 1)
    return tuple(debuts)


def numero_ligne(texte: str, position: int) -> int:
    return bisect_right(_debuts_de_ligne(texte), position)


def extrait_ligne(texte: str, numero: int) -> str:
    toutes = lignes(texte)
    return toutes[numero - 1] if 0 < numero <= len(toutes) else ""


@lru_cache(maxsize=16)
def fence_non_refermee(texte: str) -> int | None:
    """Ligne de la clôture ``` restée ouverte à la fin du fichier, s'il y en a une."""
    ouverture: int | None = None
    for numero, ligne in enumerate(lignes(texte), start=1):
        if ligne.lstrip().startswith("```"):
            ouverture = None if ouverture is not None else numero
    return ouverture


@lru_cache(maxsize=16)
def lignes_de_code(texte: str) -> frozenset[int]:
    """Numéros de ligne pris dans une clôture ``` (les délimiteurs compris).

    Une clôture jamais refermée n'en est pas une : comme pour un frontmatter
    laissé ouvert, rien n'est ignoré, sans quoi une accolade oubliée éteindrait
    le linter sur toute la fin du fichier.
    """
    if fence_non_refermee(texte) is not None:
        return frozenset()
    dedans = False
    numeros: set[int] = set()
    for numero, ligne in enumerate(lignes(texte), start=1):
        if ligne.lstrip().startswith("```"):
            numeros.add(numero)
            dedans = not dedans
            continue
        if dedans:
            numeros.add(numero)
    return frozenset(numeros)


@lru_cache(maxsize=16)
def lignes_frontmatter(texte: str) -> frozenset[int]:
    """Numéros de ligne du frontmatter YAML, délimiteurs compris."""
    toutes = lignes(texte)
    if not toutes or toutes[0].strip() != "---":
        return frozenset()
    for numero, ligne in enumerate(toutes[1:], start=2):
        if ligne.strip() == "---":
            return frozenset(range(1, numero + 1))
    return frozenset()


def ligne_ignoree(texte: str, numero: int, ligne: str) -> bool:
    return (
        numero in lignes_de_code(texte)
        or numero in lignes_frontmatter(texte)
        or bool(SEPARATEUR_TABLEAU_RE.match(ligne))
    )


# --------------------------------------------------------------------------
# Règle 1 : forbidden-words
# --------------------------------------------------------------------------

# Le contenu de <style> et de <script> est du code, jamais du texte lu par un
# humain : les deux sont blanchis en entier, comme les clôtures de code.
CODE_EMBARQUE_RE = re.compile(r"<(style|script)\b[^>]*>.*?</\1\s*>", re.IGNORECASE | re.DOTALL)
# Une balise ne contient jamais de « < », et ne franchit pas une ligne vide :
# sans ces deux bornes, un « < » orphelin blanchirait le texte jusqu'au « > »
# suivant, à l'autre bout du fichier et sans rien dire.
BALISE_COMPLETE_RE = re.compile(r"<[a-zA-Z!/][^<>]*>")
LIGNE_VIDE_RE = re.compile(r"\n[ \t]*\n")
# Attributs qui portent du texte lu par un humain : eux restent contrôlés.
ATTRIBUT_PROSE_RE = re.compile(
    r"""\b(?:alt|title|aria-label|placeholder|content)\s*=\s*(["'])((?:(?!\1).)*)\1""",
    re.IGNORECASE | re.DOTALL,
)


def _blanchir(fragment: str, gardes: set[int] = frozenset()) -> str:
    """Remplace chaque caractère par une espace, sauf les sauts de ligne et les gardes.

    Un pour un : les décalages et les numéros de ligne restent exacts.
    """
    return "".join(c if (c == "\n" or i in gardes) else " " for i, c in enumerate(fragment))


@lru_cache(maxsize=16)
def sans_code_de_balisage(texte: str) -> str:
    """Blanchit CSS et balisage pour ne soumettre que la prose au vocabulaire.

    Une feuille de style n'est pas de la prose : « vertical-align » et
    « background: transparent » y sont des mots-clés du langage. Un script non
    plus. Une balise non plus : « align » de `<td align="center">` est de la
    mise en page. Même raison que les clôtures de code, déjà ignorées. Le texte
    entre les balises est gardé, ainsi que les attributs qu'un lecteur voit
    vraiment (alt, title, aria-label, placeholder, content).
    """
    def blanchir_balise(trouve: re.Match[str]) -> str:
        brut = trouve.group(0)
        if LIGNE_VIDE_RE.search(brut):    # un paragraphe, pas une balise
            return brut
        gardes = {
            position
            for attribut in ATTRIBUT_PROSE_RE.finditer(brut)
            for position in range(attribut.start(2), attribut.end(2))
        }
        return _blanchir(brut, gardes)

    sans_code = CODE_EMBARQUE_RE.sub(lambda m: _blanchir(m.group(0)), texte)
    return BALISE_COMPLETE_RE.sub(blanchir_balise, sans_code)


def _colle_a_un_trait(texte: str, debut: int, fin: int) -> bool:
    """Vrai si la correspondance est soudée à un trait d'union.

    « vertical-align » et « align-items » sont des identifiants composés, pas
    le verbe « align ». Les composés réellement interdits (« game-changer »,
    « cutting-edge ») sont configurés en entier, trait compris, et gardent donc
    leurs deux bords libres.
    """
    return (debut > 0 and texte[debut - 1] == "-") or (fin < len(texte) and texte[fin] == "-")


def regle_forbidden_words(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("forbidden-words", {})
    if sous_chemin(chemin, reglages.get("exclude_paths", [])):
        return []

    if Path(chemin).suffix.lower() in reglages.get("skip_extensions", []):
        return []
    texte = sans_code_de_balisage(texte)

    # Trois régimes, du plus sévère au plus souple :
    #   contenu publié  : la charte et l'anti-style-IA sont des erreurs ;
    #   ailleurs        : la charte reste une erreur, l'anti-style-IA avertit ;
    #   doctrine        : les deux avertissent, car ces fichiers citent les mots
    #                     qu'ils interdisent et un blocage y serait faux.
    en_contenu = sous_chemin(chemin, reglages.get("content_dirs", []))
    en_doctrine = sous_chemin(chemin, reglages.get("doctrine_dirs", []))
    niveau_charte = AVERTISSEMENT if en_doctrine else ERREUR
    niveau_ia = ERREUR if en_contenu and not en_doctrine else AVERTISSEMENT
    groupes = [
        (config["_compile"]["charter"], niveau_charte, "charte éditoriale"),
        (config["_compile"]["ai"], niveau_ia, "anti-style-IA"),
        (config["_compile"]["tolerated"], AVERTISSEMENT, "toléré selon le contexte"),
    ]

    bruts: list[tuple[int, int, int, str, str, str]] = []
    for motif, niveau, source in groupes:
        if motif is None:
            continue
        for trouve in motif.finditer(texte):
            if _colle_a_un_trait(texte, trouve.start(), trouve.end()):
                continue
            numero = numero_ligne(texte, trouve.start())
            if ligne_ignoree(texte, numero, extrait_ligne(texte, numero)):
                continue
            bruts.append((trouve.start(), trouve.end(), numero, trouve.group(0), niveau, source))

    return [
        Constat(chemin, numero, "forbidden-words", niveau,
                f"« {mot} » est interdit ({source})", mot)
        for _, _, numero, mot, niveau, source in _sans_chevauchement(bruts)
    ]


def _sans_chevauchement(
    bruts: list[tuple[int, int, int, str, str, str]],
) -> list[tuple[int, int, int, str, str, str]]:
    """Garde la correspondance la plus longue, puis la plus sévère.

    « ressources humaines » est une erreur de charte : le mot « ressources »,
    toléré à lui seul, ne doit pas la doubler d'un avertissement.
    """
    ordonnes = sorted(bruts, key=lambda b: (b[0], -(b[1] - b[0]), -RANG_NIVEAU[b[4]]))
    gardes: list[tuple[int, int, int, str, str, str]] = []
    for candidat in ordonnes:
        debut, fin = candidat[0], candidat[1]
        if any(g[0] <= debut and fin <= g[1] for g in gardes):
            continue
        gardes.append(candidat)
    return sorted(gardes, key=lambda b: b[0])


# --------------------------------------------------------------------------
# Règle 2 : dashes
# --------------------------------------------------------------------------

def regle_dashes(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("dashes", {})
    caracteres = reglages.get("characters", ["—"])
    niveau = reglages.get("level", ERREUR)
    noms = {"—": "tiret quadratin", "–": "tiret demi-cadratin"}

    constats: list[Constat] = []
    for numero, ligne in enumerate(lignes(texte), start=1):
        if ligne_ignoree(texte, numero, ligne):
            continue
        for caractere in caracteres:
            colonne = ligne.find(caractere)
            while colonne >= 0:
                constats.append(Constat(
                    chemin, numero, "dashes", niveau,
                    f"{noms.get(caractere, 'tiret long')} « {caractere} » : "
                    "reformuler avec une virgule, deux points, une parenthèse ou un point",
                    caractere, colonne + 1,
                ))
                colonne = ligne.find(caractere, colonne + 1)
    return constats


# --------------------------------------------------------------------------
# Règle 3 : title-period
# --------------------------------------------------------------------------

TITRE_MD_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
TITRE_HTML_RE = re.compile(r"<h([1-3])\b[^>]*>(.*?)</h\1\s*>", re.IGNORECASE | re.DOTALL)
BALISE_RE = re.compile(r"<[^>]+>")


def _termine_par_un_point(texte_titre: str) -> bool:
    net = texte_titre.strip().rstrip("*_`\"'» ")
    return net.endswith(".") and not net.endswith("..")


def regle_title_period(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    niveau = config.get("title-period", {}).get("level", ERREUR)
    constats: list[Constat] = []

    for numero, ligne in enumerate(lignes(texte), start=1):
        if numero in lignes_de_code(texte) or numero in lignes_frontmatter(texte):
            continue
        trouve = TITRE_MD_RE.match(ligne)
        if trouve and _termine_par_un_point(trouve.group(2)):
            constats.append(Constat(
                chemin, numero, "title-period", niveau,
                f"titre terminé par un point : « {trouve.group(2).strip()} »",
                trouve.group(2).strip(),
            ))

    for trouve in TITRE_HTML_RE.finditer(texte):
        contenu = BALISE_RE.sub("", trouve.group(2))
        if _termine_par_un_point(contenu):
            numero = numero_ligne(texte, trouve.start())
            if numero in lignes_de_code(texte) or numero in lignes_frontmatter(texte):
                continue
            constats.append(Constat(
                chemin, numero, "title-period", niveau,
                f"titre <h{trouve.group(1)}> terminé par un point : « {contenu.strip()} »",
                contenu.strip(),
            ))
    return constats


# --------------------------------------------------------------------------
# Règle 4 : hashtags
# --------------------------------------------------------------------------

HASHTAG_RE = re.compile(r"(?<![\w&#])#([A-Za-z][A-Za-z0-9_]*)")
HEX_MOT_RE = re.compile(r"^(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


def regle_hashtags(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("hashtags", {})
    if Path(chemin).suffix.lower() not in reglages.get("extensions", [".md"]):
        return []
    if not sous_chemin(chemin, reglages.get("include_paths", [])):
        return []
    niveau = reglages.get("level", ERREUR)

    constats: list[Constat] = []
    for numero, ligne in enumerate(lignes(texte), start=1):
        if ligne_ignoree(texte, numero, ligne) or TITRE_MD_RE.match(ligne):
            continue
        for trouve in HASHTAG_RE.finditer(ligne):
            mot = trouve.group(1)
            if HEX_MOT_RE.match(mot):    # une couleur, pas un hashtag
                continue
            constats.append(Constat(
                chemin, numero, "hashtags", niveau,
                f"hashtag « #{mot} » : la doctrine sociale de la marque n'en emploie aucun",
                f"#{mot}",
            ))
    return constats


# --------------------------------------------------------------------------
# Règle 5 : placeholders (délègue à scripts/lint-placeholders.py)
# --------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _module_placeholders():
    """Charge lint-placeholders.py : son nom contient un tiret."""
    chemin = Path(__file__).resolve().parent / "lint-placeholders.py"
    spec = importlib.util.spec_from_file_location("lint_placeholders", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def regle_placeholders(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("placeholders", {})
    if sous_chemin(chemin, reglages.get("exclude_paths", [])):
        return []
    module = _module_placeholders()
    # Mêmes exclusions que lint-placeholders.py, sans les recopier : galeries de
    # gabarits (« templates/ »), corpus d'exemples, docs, et gabarits à copier.
    if any(part in module.IGNORE_DIRS for part in Path(chemin).parts):
        return []
    if chemin.endswith(module.IGNORE_FILE_SUFFIXES):
        return []
    niveau = reglages.get("level", ERREUR)
    absolu = config["_racine"] / chemin
    return [
        Constat(chemin, ligne, "placeholders", niveau,
                f"placeholder non résolu {{{{{nom}}}}}", f"{{{{{nom}}}}}")
        for ligne, nom in module.scan_file(absolu, set(module.PLACEHOLDERS_TOLERES))
    ]


# --------------------------------------------------------------------------
# Règle 6 : off-palette
# --------------------------------------------------------------------------

HEX_RE = re.compile(r"#([0-9a-fA-F]{3,8})(?![0-9a-fA-F])")
DEBUT_DATA_URI_RE = re.compile(r"data:[a-zA-Z][\w.+-]*/")
FINS_DATA_URI = set(" \t\r\n\"'()")


def plages_data_uri(texte: str) -> list[tuple[int, int]]:
    """Étendue de chaque data: URI : ses hex décrivent une image, pas la charte.

    Une URI citée court jusqu'à sa quote fermante, ce qui couvre le SVG en
    clair ; une URI nue s'arrête au premier blanc ou séparateur.
    """
    plages: list[tuple[int, int]] = []
    for debut_uri in DEBUT_DATA_URI_RE.finditer(texte):
        debut = debut_uri.start()
        quote = texte[debut - 1] if debut else ""
        if quote in ('"', "'"):
            fin = texte.find(quote, debut)
            # Une quote fermante absente, ou repoussée à la ligne suivante, ne doit pas
            # éteindre la règle jusqu'à la fin du fichier : la plage s'arrête au saut.
            fin_de_ligne = texte.find("\n", debut)
            if fin < 0 or (0 <= fin_de_ligne < fin):
                fin = len(texte) if fin_de_ligne < 0 else fin_de_ligne
        else:
            fin = debut_uri.end()
            while fin < len(texte) and texte[fin] not in FINS_DATA_URI:
                fin += 1
        plages.append((debut, fin))
    return plages


DEBUT_BLOC_GENERE = "/* brand-tokens:start */"
FIN_BLOC_GENERE = "/* brand-tokens:end */"


def plages_generees(texte: str) -> list[tuple[int, int]]:
    """Étendue de chaque bloc écrit par scripts/build-tokens.py depuis tokens.json.

    Ses nuances dérivées (-deep, -soft, accents des étiquettes) sont calculées
    depuis la palette : les mesurer contre elle n'a pas de sens, et leur
    conformité se vérifie par `build-tokens.py --check`. Un bloc ouvert sans
    marqueur de fin n'exempte rien.
    """
    plages: list[tuple[int, int]] = []
    debut = texte.find(DEBUT_BLOC_GENERE)
    while debut != -1:
        fin = texte.find(FIN_BLOC_GENERE, debut)
        if fin == -1:
            break
        plages.append((debut, fin + len(FIN_BLOC_GENERE)))
        debut = texte.find(DEBUT_BLOC_GENERE, fin)
    return plages


def _est_gris(hexa: str) -> bool:
    return hexa[1:3] == hexa[3:5] == hexa[5:7]


def regle_off_palette(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("off-palette", {})
    if config["_palette"] is None:    # pas de tokens.json exploitable : voir « palette »
        return []
    if Path(chemin).suffix.lower() not in reglages.get("extensions", []):
        return []
    if sous_chemin(chemin, exclusions_production(config)):
        return []

    plages_data = plages_data_uri(texte) + plages_generees(texte)
    palette = config["_palette"]
    admis = [t for t in palette if t.admis_dans(chemin)]

    fautifs: dict[str, tuple[int, str]] = {}    # hex développé -> (ligne, message)
    conformes: set[str] = set()                 # déjà reconnus, ne pas remesurer
    for trouve in HEX_RE.finditer(texte):
        if len(trouve.group(1)) not in (3, 6, 8):
            continue
        if any(debut <= trouve.start() < fin for debut, fin in plages_data):
            continue
        hexa = developper_hex(trouve.group(0))
        if _est_gris(hexa):    # noir, blanc et gris purs restent neutres
            continue
        if hexa in fautifs or hexa in conformes:
            continue
        # Le token le plus proche est cherché dans TOUTE la palette, portée comprise :
        # sa portée est jugée ensuite. Chercher d'abord parmi les seuls tokens admis
        # laisserait passer une couleur restreinte que la tolérance rapproche d'une
        # couleur de marque (une ombre d'illustration à ΔE 1.5 de l'accent, par
        # exemple, passerait alors pour l'accent partout).
        voisins = [t for t in palette if delta_e76(hexa, t.hexa) <= t.delta_max]
        numero = numero_ligne(texte, trouve.start())
        if voisins:
            proche = min(voisins, key=lambda t: delta_e76(hexa, t.hexa))
            if proche.admis_dans(chemin):
                conformes.add(hexa)
                continue
            ecart = delta_e76(hexa, proche.hexa)
            designation = (
                f"est le token « color.{proche.nom} »" if ecart == 0
                else f"est à ΔE {ecart:.2f} du token « color.{proche.nom} » {proche.hexa}"
            )
            message = (
                f"{hexa} {designation}, dont la portée se limite à "
                f"{', '.join(proche.scope)} : hors de là il est hors palette"
            )
        elif admis:
            proche = min(admis, key=lambda t: delta_e76(hexa, t.hexa))
            message = (
                f"{hexa} est hors palette (le plus proche : « color.{proche.nom} » "
                f"{proche.hexa}, ΔE76 {delta_e76(hexa, proche.hexa):.1f})"
            )
        else:
            # Aucune couleur de marque n'est admise ici : la palette n'a rien à opposer.
            message = f"{hexa} est hors palette (aucun token admis dans ce dossier)"
        fautifs[hexa] = (numero, message)

    if not fautifs:
        return []
    niveau = ERREUR if len(fautifs) > int(reglages.get("max_distinct", 3)) else AVERTISSEMENT
    return [
        Constat(chemin, ligne, "off-palette", niveau, message, hexa)
        for hexa, (ligne, message) in sorted(fautifs.items(), key=lambda item: item[1][0])
    ]


# --------------------------------------------------------------------------
# Règle 7 : font-family
# --------------------------------------------------------------------------

FONT_FAMILY_RE = re.compile(r"font-family\s*:\s*([^;}{\n]+)", re.IGNORECASE)
GENERIQUES = {"sans-serif", "serif", "system-ui", "ui-sans-serif", "ui-serif", "cursive", "fantasy"}


def regle_font_family(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("font-family", {})
    if config["_palette"] is None:    # pas de tokens.json exploitable : voir « palette »
        return []
    if Path(chemin).suffix.lower() not in reglages.get("extensions", []):
        return []
    if sous_chemin(chemin, exclusions_production(config)):
        return []

    # Les polices de marque viennent de tokens.json ; la configuration n'ajoute
    # que des mots-clés neutres ou une famille tolérée partout.
    admises = set(config["_polices"]) | {f.lower() for f in reglages.get("allowed", [])}
    noms_marque = ", ".join(sorted(config["_polices"])) or "aucune police déclarée"
    monospace = {f.lower() for f in reglages.get("monospace", [])}
    tolerees_mail = {f.lower() for f in reglages.get("mail_allowed", [])}
    en_sursis = {f.lower() for f in reglages.get("mail_warn", [])}
    en_mail = sous_chemin(chemin, reglages.get("mail_dirs", []))
    en_sursis_ici = sous_chemin(chemin, reglages.get("mail_warn_dirs", []))

    constats: list[Constat] = []
    for trouve in FONT_FAMILY_RE.finditer(texte):
        declaration = re.sub(r"!\s*important\s*$", "", trouve.group(1).strip(), flags=re.IGNORECASE)
        premiere = declaration.split(",")[0].strip().strip("'\"").strip()
        if not premiere or premiere.lower().startswith("var("):
            continue
        cle = premiere.lower()
        if cle in admises or cle in monospace or cle in GENERIQUES:
            continue
        numero = numero_ligne(texte, trouve.start())
        if numero in lignes_de_code(texte):
            continue
        if en_mail and cle in tolerees_mail:
            constats.append(Constat(
                chemin, numero, "font-family", AVERTISSEMENT,
                f"première famille « {premiere} » : tolérée en messagerie, "
                f"à garder au strict nécessaire (police de marque : {noms_marque})",
                premiere,
            ))
        elif en_sursis_ici and cle in en_sursis:
            constats.append(Constat(
                chemin, numero, "font-family", AVERTISSEMENT,
                f"première famille « {premiere} » : police en sursis, tolérée dans ce "
                "dossier le temps de sa migration vers la police de marque "
                f"({noms_marque}), et erreur partout ailleurs",
                premiere,
            ))
        else:
            constats.append(Constat(
                chemin, numero, "font-family", ERREUR,
                f"première famille « {premiere} » hors marque : "
                f"{noms_marque} (01-brand/tokens.json) ou une monospace pour le code",
                premiere,
            ))
    return constats


# --------------------------------------------------------------------------
# Règle 8 : negative-parallelism
# --------------------------------------------------------------------------

def regle_negative_parallelism(chemin: str, texte: str, config: dict[str, Any]) -> list[Constat]:
    reglages = config.get("negative-parallelism", {})
    if sous_chemin(chemin, reglages.get("exclude_paths", [])):
        return []
    niveau = reglages.get("level", AVERTISSEMENT)

    vus: set[tuple[int, str]] = set()
    constats: list[Constat] = []
    for label, motif in config["_compile"]["negative"]:
        for trouve in motif.finditer(texte):
            numero = numero_ligne(texte, trouve.start())
            if ligne_ignoree(texte, numero, extrait_ligne(texte, numero)):
                continue
            if (numero, label) in vus:
                continue
            vus.add((numero, label))
            constats.append(Constat(
                chemin, numero, "negative-parallelism", niveau,
                f"parallélisme négatif, patron « {label} » : "
                "supprimer la négation et n'affirmer que la proposition positive",
                " ".join(trouve.group(0).split())[:80],
            ))
    return constats


# --------------------------------------------------------------------------
# Parcours et exécution
# --------------------------------------------------------------------------

REGLES: dict[str, Callable[[str, str, dict[str, Any]], list[Constat]]] = {
    "forbidden-words": regle_forbidden_words,
    "dashes": regle_dashes,
    "title-period": regle_title_period,
    "hashtags": regle_hashtags,
    "placeholders": regle_placeholders,
    "off-palette": regle_off_palette,
    "font-family": regle_font_family,
    "negative-parallelism": regle_negative_parallelism,
}


def iter_fichiers(cibles: list[Path], racine: Path, config: dict[str, Any]) -> Iterator[tuple[Path, str]]:
    """Rend les fichiers à analyser, avec leur chemin relatif à la racine."""
    general = config.get("general", {})
    extensions = {e.lower() for e in general.get("extensions", [])}
    dossiers_exclus = set(general.get("exclude_dirs", []))
    chemins_exclus = general.get("exclude_paths", [])
    vus: set[Path] = set()

    def relatif(fichier: Path) -> str | None:
        try:
            return fichier.resolve().relative_to(racine.resolve()).as_posix()
        except ValueError:
            return fichier.as_posix()

    def retenir(fichier: Path) -> Iterator[tuple[Path, str]]:
        if fichier.suffix.lower() not in extensions:
            return
        # Un lien symbolique pointe vers un fichier déjà parcouru ailleurs : le
        # suivre ferait compter deux fois le même texte.
        if fichier.is_symlink() or fichier in vus:
            return
        rel = relatif(fichier)
        if rel is None or sous_chemin(rel, chemins_exclus):
            return
        vus.add(fichier)
        yield fichier, rel

    for cible in cibles:
        # `exists()` remonte l'erreur du système de fichiers telle quelle : un
        # chemin trop long (ENAMETOOLONG) ou porteur d'un octet nul lève une
        # OSError, pas un `False`. Sans garde, la trace Python sortait à la
        # place du message du linter.
        try:
            presente = cible.exists()
        except (OSError, ValueError) as err:
            raise LintError(f"chemin illisible : {cible} ({err})") from err
        if not presente:
            raise LintError(f"chemin inexistant : {cible}")
        if cible.is_file():
            yield from retenir(cible)
            continue
        for fichier in sorted(cible.rglob("*")):
            if not fichier.is_file():
                continue
            if any(part in dossiers_exclus for part in fichier.parts):
                continue
            yield from retenir(fichier)


# L'apostrophe courbe est ramenée à l'apostrophe droite : même longueur, donc
# les positions et les numéros de ligne restent exacts, et un seul motif suffit.
def normaliser(texte: str) -> str:
    return texte.replace("’", "'").replace(" ", " ")


def analyser(cibles: list[Path], racine: Path, config: dict[str, Any],
             regles: list[str]) -> tuple[list[Constat], int]:
    constats: list[Constat] = []
    nombre = 0
    graphiques_vus = False
    for fichier, rel in iter_fichiers(cibles, racine, config):
        nombre += 1
        try:
            texte = normaliser(fichier.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError) as err:
            constats.append(Constat(
                rel, 0, "io", AVERTISSEMENT,
                f"fichier illisible, aucune règle ne s'y applique : {err}",
            ))
            continue
        # Diagnostic de fichier, comme « io » : il ne dépend d'aucune règle et
        # ne se sélectionne donc ni par --only ni par --skip.
        ouverte = fence_non_refermee(texte)
        if ouverte is not None:
            constats.append(Constat(
                rel, ouverte, "fence", AVERTISSEMENT,
                "clôture ``` non refermée : plus rien n'est mis à l'abri du linter "
                "au-delà de cette ligne, refermer la clôture",
                "```",
            ))
        for nom in regles:
            constats.extend(REGLES[nom](rel, texte, config))
        if fichier.suffix.lower() in _extensions_graphiques(config, regles):
            graphiques_vus = True
    # Diagnostic de dépôt, comme « io » et « fence » : sans tokens.json exploitable,
    # les règles graphiques se taisent, et le silence ne doit pas passer pour un
    # fichier conforme. Un seul constat, et seulement si un fichier était concerné.
    if graphiques_vus and config["_palette"] is None:
        constats.append(Constat(
            config["_tokens_rel"], 0, "palette", AVERTISSEMENT,
            f"palette indisponible ({config['_palette_absente']}) : "
            f"{', '.join(r for r in REGLES_GRAPHIQUES if r in regles)} non appliquée(s). "
            "Lancer /brand-discover, qui crée 01-brand/tokens.json",
        ))
    constats.sort(key=lambda c: (c.fichier, c.ligne, c.colonne, c.regle, c.message))
    return constats, nombre


def _extensions_graphiques(config: dict[str, Any], regles: list[str]) -> set[str]:
    """Extensions que lisent les règles graphiques actives."""
    return {
        extension.lower()
        for regle in REGLES_GRAPHIQUES if regle in regles
        for extension in config.get(regle, {}).get("extensions", [])
    }


def resume(constats: list[Constat], fichiers: int) -> dict[str, Any]:
    par_regle: dict[str, int] = {}
    for constat in constats:
        par_regle[constat.regle] = par_regle.get(constat.regle, 0) + 1
    return {
        "files": fichiers,
        "findings": len(constats),
        "errors": sum(1 for c in constats if c.niveau == ERREUR),
        "warnings": sum(1 for c in constats if c.niveau == AVERTISSEMENT),
        "by_rule": dict(sorted(par_regle.items())),
    }


def accord(nombre: int, singulier: str) -> str:
    return f"{nombre} {singulier}{'s' if nombre > 1 else ''}"


def rendre_texte(constats: list[Constat], bilan: dict[str, Any]) -> str:
    lignes = [
        f"{c.fichier}:{c.ligne}{f':{c.colonne}' if c.colonne else ''}: "
        f"[{c.regle}] {LIBELLE_NIVEAU[c.niveau]}: {c.message}"
        for c in constats
    ]
    if lignes:
        lignes.append("")
    lignes.append(
        f"{accord(bilan['findings'], 'constat')} : {accord(bilan['errors'], 'erreur')}, "
        f"{accord(bilan['warnings'], 'avertissement')} sur "
        f"{accord(bilan['files'], 'fichier')} analysé{'s' if bilan['files'] > 1 else ''}"
    )
    for regle, total in bilan["by_rule"].items():
        detail = [c for c in constats if c.regle == regle]
        erreurs = sum(1 for c in detail if c.niveau == ERREUR)
        lignes.append(f"  {regle} : {total} ({erreurs} en erreur)")
    return "\n".join(lignes)


def rendre_json(constats: list[Constat], bilan: dict[str, Any]) -> str:
    return json.dumps({
        "summary": bilan,
        "findings": [
            {"file": c.fichier, "line": c.ligne, "column": c.colonne, "rule": c.regle,
             "level": c.niveau, "message": c.message, "match": c.extrait}
            for c in constats
        ],
    }, indent=2, ensure_ascii=False)


def _liste_regles(valeur: str | None) -> list[str]:
    if not valeur:
        return []
    return [morceau.strip() for morceau in valeur.split(",") if morceau.strip()]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Linter de marque déterministe (doctrine 01-brand/, configuration scripts/lint-brand.toml).",
        epilog="Règles : " + ", ".join(REGLES),
    )
    parser.add_argument("paths", nargs="*", help="Fichiers ou dossiers à analyser (défaut : la racine).")
    parser.add_argument("--root", default=str(RACINE_DEFAUT),
                        help="Racine du dépôt (défaut : le dossier parent de scripts/).")
    parser.add_argument("--config", default=str(CONFIG_DEFAUT),
                        help="Fichier de configuration TOML (défaut : scripts/lint-brand.toml).")
    parser.add_argument("--only", help="Ne garder que ces règles (séparées par des virgules).")
    parser.add_argument("--skip", help="Écarter ces règles (séparées par des virgules).")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="Forme de la sortie (défaut : text).")
    parser.add_argument("--warnings-as-errors", action="store_true",
                        help="Sortir 1 dès le premier avertissement.")
    args = parser.parse_args(argv)

    only, skip = _liste_regles(args.only), _liste_regles(args.skip)
    inconnues = sorted(set(only + skip) - set(REGLES))
    if inconnues:
        print(f"ERREUR : règle inconnue : {', '.join(inconnues)}. "
              f"Règles disponibles : {', '.join(REGLES)}.", file=sys.stderr)
        return 2
    racine = Path(args.root).resolve()
    cibles = [Path(p) for p in args.paths] or [racine]
    try:
        config = charger_config(Path(args.config), racine)
    except LintError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2

    # --only l'emporte sur la configuration : une règle demandée nommément tourne,
    # même si la marque l'a désactivée (`enabled = false`) pour le parcours courant.
    if only:
        regles = [nom for nom in REGLES if nom in only and nom not in skip]
    else:
        regles = [nom for nom in REGLES if regle_active(config, nom) and nom not in skip]
    if not regles:
        print("ERREUR : aucune règle ne reste active.", file=sys.stderr)
        return 2

    try:
        constats, fichiers = analyser(cibles, racine, config, regles)
    except LintError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2

    bilan = resume(constats, fichiers)
    print(rendre_json(constats, bilan) if args.format == "json" else rendre_texte(constats, bilan))

    if bilan["errors"] or (args.warnings_as_errors and bilan["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
