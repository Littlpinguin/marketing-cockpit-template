#!/usr/bin/env python3
"""
Génère les fichiers CSS de marque depuis 01-brand/tokens.json.

tokens.json est la SEULE source de vérité de la palette, de la typographie et
des constantes graphiques de la marque. Ce script recopie ces valeurs dans les
fichiers qui les consomment ; aucune couleur ne doit être saisie ailleurs à la
main.

Les cibles ne sont pas codées ici : elles sont déclarées dans
scripts/build-tokens.toml, pour que chaque fork liste ses propres consommateurs
sans toucher au code. Deux modes de cible :

  - block : seul le contenu entre « /* brand-tokens:start */ » et
            « /* brand-tokens:end */ » est régénéré ; hors marqueurs, le
            fichier est conservé à l'octet près ;
  - file  : le fichier entier est réécrit.

Chaque variable d'une cible pointe un token par son chemin (« color.primary »),
avec deux modificateurs facultatifs : `alpha` (une couleur rendue en rgba) et
`angle` (un gradient rendu sous un autre angle). Une liste `auto` de groupes
(« color », « gradient », « font », « radius ») exporte d'office chaque token
de ces groupes sous le nom « --<groupe>-<chemin> ».

Usage:
  python3 scripts/build-tokens.py             # écrit les cibles
  python3 scripts/build-tokens.py --dry-run   # affiche sans écrire
  python3 scripts/build-tokens.py --check     # sort 1 si une cible a dérivé

Le script refuse un tokens.json dont un placeholder {{…}} n'est pas résolu
(wizard pas encore passé), une couleur qui n'est pas un #RRGGBB, une référence
introuvable ou un arrêt de gradient mal formé. Il est idempotent : deux
exécutions successives ne changent rien.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterator

try:
    import tomllib
except ModuleNotFoundError:    # tomllib est entré dans la bibliothèque standard en 3.11
    print(f"ERREUR : Python 3.11 ou plus récent est requis (module « tomllib » absent) ; "
          f"version courante : {sys.version.split()[0]}.", file=sys.stderr)
    raise SystemExit(2)

MARKER_START = "/* brand-tokens:start */"
MARKER_END = "/* brand-tokens:end */"

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
REF_RE = re.compile(r"^\{([A-Za-z0-9_.-]+)\}$")
PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}")

TOKENS_REL_DEFAUT = "01-brand/tokens.json"
CONFIG_DEFAUT = Path(__file__).resolve().parent / "build-tokens.toml"
EXTENSION = "cockpit"    # espace de noms des métadonnées sous $extensions

ENTETE_GENERE = "Généré depuis {source} (python3 scripts/build-tokens.py). Ne pas éditer."

# Mots-clés CSS de famille générique : jamais entre quotes.
FAMILLES_GENERIQUES = {
    "serif", "sans-serif", "monospace", "cursive", "fantasy",
    "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded",
}

GROUPES_AUTO = {"color", "gradient", "font", "radius"}


class TokenError(Exception):
    """Erreur de contenu ou de structure dans tokens.json, la config ou une cible."""


# --------------------------------------------------------------------------
# Lecture et validation de tokens.json
# --------------------------------------------------------------------------

def load_tokens(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise TokenError(
            f"{path} introuvable : lancer /brand-discover, qui le crée depuis "
            "_templates/brand/tokens.json"
        )
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise TokenError(f"{path} n'est pas un JSON valide : {err}") from err


def iter_tokens(node: dict[str, Any], inherited_type: str | None = None,
                path: tuple[str, ...] = ()) -> Iterator[tuple[str, str | None, Any]]:
    """Parcourt l'arbre DTCG et rend (chemin, type effectif, valeur) par token."""
    node_type = node.get("$type", inherited_type)
    if "$value" in node:
        yield ".".join(path), node_type, node["$value"]
        return
    for key, child in node.items():
        if key.startswith("$"):
            continue
        if not isinstance(child, dict):
            chemin = ".".join(path + (key,))
            raise TokenError(
                f"token mal typé « {chemin} » : un groupe ou un token (objet avec "
                f"« $value ») était attendu, trouvé {type(child).__name__} "
                f"({child!r}). Un token s'écrit "
                '{ "$value": ..., "$description": ... }.'
            )
        yield from iter_tokens(child, node_type, path + (key,))


def _placeholders_dans(valeur: Any) -> list[str]:
    if isinstance(valeur, str):
        return PLACEHOLDER_RE.findall(valeur)
    if isinstance(valeur, list):
        return [nom for element in valeur for nom in _placeholders_dans(element)]
    if isinstance(valeur, dict):
        return [nom for element in valeur.values() for nom in _placeholders_dans(element)]
    return []


def validate_tokens(tokens: dict[str, Any]) -> None:
    """Refuse placeholders résiduels, hex mal formés et gradients non résolubles."""
    residus = sorted({
        nom
        for _, _, valeur in iter_tokens(tokens)
        for nom in _placeholders_dans(valeur)
    })
    if residus:
        raise TokenError(
            "placeholders non résolus dans tokens.json : "
            + ", ".join(f"{{{{{nom}}}}}" for nom in residus)
            + ". Les remplir (/brand-discover) avant de générer les cibles."
        )
    for chemin, type_token, valeur in iter_tokens(tokens):
        if type_token == "color":
            resolve_color(tokens, valeur, chemin)
        elif type_token == "gradient":
            if not isinstance(valeur, list) or not valeur:
                raise TokenError(f"gradient vide ou mal formé pour « {chemin} »")
            for index, stop in enumerate(valeur):
                if not isinstance(stop, dict) or "color" not in stop or "position" not in stop:
                    raise TokenError(
                        f"arrêt {index} du gradient « {chemin} » : "
                        "clés « color » et « position » attendues"
                    )
                resolve_color(tokens, stop["color"], f"{chemin}[{index}]")
                position = stop["position"]
                if (isinstance(position, bool) or not isinstance(position, (int, float))
                        or not 0 <= position <= 1):
                    raise TokenError(
                        f"arrêt {index} du gradient « {chemin} » : "
                        f"position {position!r} hors de [0, 1]"
                    )
        elif type_token == "fontFamily":
            if (not isinstance(valeur, list) or not valeur
                    or not all(isinstance(f, str) and f.strip() for f in valeur)):
                raise TokenError(
                    f"famille de police mal formée pour « {chemin} » : "
                    "une liste non vide de noms était attendue"
                )


def lookup_node(tokens: dict[str, Any], chemin: str) -> dict[str, Any]:
    node: Any = tokens
    for segment in chemin.split("."):
        if not isinstance(node, dict) or segment not in node:
            raise TokenError(f"token « {chemin} » absent de tokens.json")
        node = node[segment]
    if not isinstance(node, dict) or "$value" not in node:
        raise TokenError(f"« {chemin} » n'est pas un token (pas de $value)")
    return node


def lookup(tokens: dict[str, Any], chemin: str) -> Any:
    return lookup_node(tokens, chemin)["$value"]


def type_of(tokens: dict[str, Any], chemin: str) -> str | None:
    """Type effectif d'un token : le sien, sinon celui hérité de ses groupes."""
    node: Any = tokens
    type_courant = tokens.get("$type")
    for segment in chemin.split("."):
        node = node[segment]
        type_courant = node.get("$type", type_courant)
    return type_courant


def resolve_color(tokens: dict[str, Any], valeur: Any, contexte: str,
                  _vus: frozenset[str] = frozenset()) -> str:
    """Résout un hex littéral ou une référence « {color.primary} »."""
    if isinstance(valeur, str):
        ref = REF_RE.match(valeur)
        if ref:
            cible = ref.group(1)
            if cible in _vus:
                raise TokenError(f"référence circulaire dans « {contexte} » : {cible}")
            return resolve_color(tokens, lookup(tokens, cible), contexte, _vus | {cible})
    if not isinstance(valeur, str) or not HEX_RE.match(valeur):
        raise TokenError(
            f"couleur invalide pour « {contexte} » : {valeur!r} (format attendu #RRGGBB)"
        )
    return valeur.upper()


# --------------------------------------------------------------------------
# Rendu des valeurs
# --------------------------------------------------------------------------

def color(tokens: dict[str, Any], chemin: str) -> str:
    return resolve_color(tokens, lookup(tokens, chemin), chemin)


def rgba(tokens: dict[str, Any], chemin: str, alpha: float) -> str:
    hexa = color(tokens, chemin)
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {alpha:.2f})"


def gradient_css(tokens: dict[str, Any], chemin: str, angle: str | None = None) -> str:
    noeud = lookup_node(tokens, chemin)
    if angle is None:
        angle = noeud.get("$extensions", {}).get(EXTENSION, {}).get("angle", "90deg")
    morceaux = [
        f"{resolve_color(tokens, stop['color'], chemin)} {stop['position'] * 100:g}%"
        for stop in noeud["$value"]
    ]
    return f"linear-gradient({angle}, {', '.join(morceaux)})"


def font_css(tokens: dict[str, Any], chemin: str) -> str:
    familles = lookup(tokens, chemin)
    return ", ".join(f if f in FAMILLES_GENERIQUES else f"'{f}'" for f in familles)


def render_value(tokens: dict[str, Any], spec: Any, contexte: str) -> str:
    """Rend la valeur CSS d'une variable depuis sa spécification de cible.

    La spécification est soit un chemin de token (« color.primary »), soit une
    table { token = "...", alpha = 0.12 } ou { token = "...", angle = "180deg" }.
    """
    if isinstance(spec, str):
        chemin, options = spec, {}
    elif isinstance(spec, dict) and isinstance(spec.get("token"), str):
        chemin = spec["token"]
        options = {k: v for k, v in spec.items() if k != "token"}
        inconnues = sorted(set(options) - {"alpha", "angle"})
        if inconnues:
            raise TokenError(f"{contexte} : option(s) inconnue(s) {', '.join(inconnues)}")
    else:
        raise TokenError(
            f"{contexte} : un chemin de token ou une table {{ token = ... }} était attendu"
        )

    lookup_node(tokens, chemin)    # lève si le chemin ne désigne pas un token
    type_token = type_of(tokens, chemin)
    if "alpha" in options:
        if type_token != "color":
            raise TokenError(f"{contexte} : « alpha » ne s'applique qu'à une couleur")
        alpha = options["alpha"]
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not 0 <= alpha <= 1:
            raise TokenError(f"{contexte} : alpha {alpha!r} hors de [0, 1]")
        return rgba(tokens, chemin, float(alpha))
    if "angle" in options and type_token != "gradient":
        raise TokenError(f"{contexte} : « angle » ne s'applique qu'à un gradient")

    if type_token == "color":
        return color(tokens, chemin)
    if type_token == "gradient":
        return gradient_css(tokens, chemin, options.get("angle"))
    if type_token == "fontFamily":
        return font_css(tokens, chemin)
    if type_token in ("dimension", "number", "fontWeight", "duration"):
        return str(lookup(tokens, chemin))
    raise TokenError(
        f"{contexte} : le token « {chemin} » (type {type_token!r}) ne se rend pas "
        "en une variable CSS"
    )


def auto_vars(tokens: dict[str, Any], groupes: list[str]) -> list[tuple[str, str]]:
    """Variables « --<groupe>-<chemin> » de chaque token des groupes demandés."""
    variables: list[tuple[str, str]] = []
    for groupe in groupes:
        if groupe not in tokens:
            raise TokenError(f"groupe « {groupe} » absent de tokens.json")
        for chemin, _, _ in iter_tokens(tokens[groupe], tokens[groupe].get("$type"), (groupe,)):
            nom = "--" + chemin.replace(".", "-")
            variables.append((nom, render_value(tokens, chemin, f"auto {nom}")))
    return variables


# --------------------------------------------------------------------------
# Configuration des cibles
# --------------------------------------------------------------------------

def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise TokenError(f"configuration introuvable : {path}")
    try:
        config = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise TokenError(f"{path} n'est pas un TOML valide : {err}") from err
    cibles = config.get("targets")
    if not isinstance(cibles, list) or not cibles:
        raise TokenError(f"{path} : aucune cible déclarée ([[targets]])")
    for index, cible in enumerate(cibles):
        if not isinstance(cible.get("path"), str) or not cible["path"]:
            raise TokenError(f"{path} : la cible {index} n'a pas de « path »")
        if cible.get("mode", "block") not in ("block", "file"):
            raise TokenError(f"{path} : cible {cible['path']} : mode « block » ou « file » attendu")
        inconnus = sorted(set(cible.get("auto", [])) - GROUPES_AUTO)
        if inconnus:
            raise TokenError(
                f"{path} : cible {cible['path']} : groupe(s) auto inconnu(s) "
                f"{', '.join(inconnus)} (admis : {', '.join(sorted(GROUPES_AUTO))})"
            )
        if not cible.get("vars") and not cible.get("auto"):
            raise TokenError(f"{path} : cible {cible['path']} sans « vars » ni « auto »")
    return config


def target_lines(tokens: dict[str, Any], cible: dict[str, Any], source: str) -> list[str]:
    """Lignes générées pour une cible, sans indentation ni marqueurs."""
    declarations: list[tuple[str, str]] = []
    for nom, spec in cible.get("vars", {}).items():
        if not nom.startswith("--"):
            raise TokenError(f"cible {cible['path']} : « {nom} » n'est pas une variable CSS (--nom)")
        declarations.append((nom, render_value(tokens, spec, f"cible {cible['path']}, {nom}")))
    declarations += auto_vars(tokens, list(cible.get("auto", [])))

    noms = [nom for nom, _ in declarations]
    doublons = sorted({nom for nom in noms if noms.count(nom) > 1})
    if doublons:
        raise TokenError(f"cible {cible['path']} : variable(s) en double {', '.join(doublons)}")

    entete = f"/* {ENTETE_GENERE.format(source=source)} */"
    if cible.get("comment"):
        entete = f"/* {cible['comment']} {ENTETE_GENERE.format(source=source)} */"
    selecteur = cible.get("selector")
    if cible.get("mode", "block") == "file" and not selecteur:
        selecteur = ":root"
    if selecteur:
        return [entete, f"{selecteur} {{"] + [f"  {n}: {v};" for n, v in declarations] + ["}"]
    return [entete] + [f"{n}: {v};" for n, v in declarations]


# --------------------------------------------------------------------------
# Application aux fichiers
# --------------------------------------------------------------------------

def render_block(lignes: list[str], indent: str) -> str:
    corps = "".join(f"{indent}{ligne}\n" if ligne else "\n" for ligne in lignes)
    return f"{MARKER_START}\n{corps}{indent}{MARKER_END}"


def apply_block(texte: str, bloc: str, rel: str) -> str:
    debut = texte.find(MARKER_START)
    fin = texte.find(MARKER_END)
    if debut == -1 or fin == -1 or fin < debut:
        raise TokenError(
            f"marqueurs « {MARKER_START} » / « {MARKER_END} » introuvables dans {rel}"
        )
    if texte.count(MARKER_START) > 1 or texte.count(MARKER_END) > 1:
        raise TokenError(f"marqueurs en double dans {rel} : un seul bloc généré par fichier")
    return texte[:debut] + bloc + texte[fin + len(MARKER_END):]


def expected_contents(root: Path, tokens: dict[str, Any], config: dict[str, Any],
                      source: str) -> dict[str, str]:
    """Rend, pour chaque cible, le contenu complet attendu."""
    attendus: dict[str, str] = {}
    for cible in config["targets"]:
        rel = cible["path"]
        lignes = target_lines(tokens, cible, source)
        if cible.get("mode", "block") == "file":
            attendus[rel] = "\n".join(lignes) + "\n"
            continue
        chemin = root / rel
        if not chemin.exists():
            raise TokenError(f"cible introuvable : {rel}")
        attendus[rel] = apply_block(
            chemin.read_text(encoding="utf-8"),
            render_block(lignes, cible.get("indent", "")),
            rel,
        )
    return attendus


def build(root: Path, config_path: Path, *, check: bool = False, dry_run: bool = False) -> int:
    config = load_config(config_path)
    source = config.get("tokens", TOKENS_REL_DEFAUT)
    tokens = load_tokens(root / source)
    validate_tokens(tokens)
    attendus = expected_contents(root, tokens, config, source)

    divergences: list[str] = []
    ecrits: list[str] = []
    for rel, contenu in attendus.items():
        chemin = root / rel
        actuel = chemin.read_text(encoding="utf-8") if chemin.exists() else None
        if actuel == contenu:
            continue
        divergences.append(rel)
        if dry_run:
            print(f"--- {rel} ---")
            print(contenu)
        elif not check:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_text(contenu, encoding="utf-8")
            ecrits.append(rel)

    if check:
        if divergences:
            print(f"DIVERGENCE : ces cibles ne correspondent plus à {source} :")
            for rel in divergences:
                print(f"  - {rel}")
            print("Relancer : python3 scripts/build-tokens.py")
            return 1
        print(f"OK : les {len(attendus)} cibles sont conformes à {source}.")
        return 0

    if dry_run:
        if divergences:
            print(f"\n{len(divergences)} cible(s) seraient réécrites (aucune écriture en --dry-run).")
        else:
            print("Rien à réécrire : les cibles sont déjà conformes.")
        return 0

    if ecrits:
        for rel in ecrits:
            print(f"écrit : {rel}")
    else:
        print("Rien à faire : les cibles sont déjà conformes.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Génère les fichiers CSS de marque depuis 01-brand/tokens.json "
                    "(cibles déclarées dans scripts/build-tokens.toml)."
    )
    parser.add_argument("--check", action="store_true",
                        help="Ne rien écrire ; sortir 1 si une cible a dérivé.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Afficher le contenu qui serait écrit, sans écrire.")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                        help="Racine du dépôt (défaut : le dossier parent de scripts/).")
    parser.add_argument("--config", default=str(CONFIG_DEFAUT),
                        help="Fichier de cibles TOML (défaut : scripts/build-tokens.toml).")
    args = parser.parse_args(argv)

    if args.check and args.dry_run:
        print("ERREUR : --check et --dry-run sont exclusifs.", file=sys.stderr)
        return 2

    try:
        return build(Path(args.root), Path(args.config), check=args.check, dry_run=args.dry_run)
    except TokenError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
