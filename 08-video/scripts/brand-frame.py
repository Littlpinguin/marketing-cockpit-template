#!/usr/bin/env python3
"""Charte d'un projet HyperFrames, tirée de la marque : frame.md et brand.css.

HyperFrames lit `frame.md` à la racine d'un projet (avant design.md) et traite
son frontmatter comme la vérité de marque : couleurs, polices, graisses et
rayons y sont cités tels quels. Ce script l'écrit depuis 01-brand/tokens.json
et écrit à côté `brand.css`, le fichier de variables CSS de la cible
08-video/lib/brand.css de scripts/build-tokens.toml. Ne jamais éditer ces deux
fichiers à la main dans un projet : relancer le script.

Usage :
    python3 08-video/scripts/brand-frame.py 08-video/projets/<slug>/hyperframes
    python3 08-video/scripts/brand-frame.py <dossier> --aspect 1920x1080
    python3 08-video/scripts/brand-frame.py <dossier> --check
    python3 08-video/scripts/brand-frame.py <dossier> --exemple

--check n'écrit rien et sort 1 si frame.md ou brand.css ne correspond plus à la
marque. Sans --aspect, la toile d'un frame.md existant est conservée (défaut
1080x1920). --exemple part de la palette neutre de docs/placeholders.json, pour
essayer le module avant /brand-discover.

Codes de sortie : 0 écrit ou conforme, 1 tokens invalides ou dérive, 2 usage.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

RACINE = Path(__file__).resolve().parents[2]
CIBLE_CSS = "08-video/lib/brand.css"
TOKENS_REL = "01-brand/tokens.json"
GABARIT_TOKENS = "_templates/brand/tokens.json"
PLACEHOLDERS = "docs/placeholders.json"

# Zones de sécurité par toile, en px : haut, bas, gauche, droite.
# 9:16 : valeurs de 08-video/formats.md. 1:1 et 16:9 : marge de titre de 5 %.
MARGES = {
    "1080x1920": (200, 420, 60, 160),
    "1080x1080": (54, 54, 54, 54),
    "1920x1080": (54, 54, 96, 96),
}

# Rôles typographiques : (rôle, token de typographie, taille de départ en px
# pour une toile de 1080 px de petit côté, token de famille). Graisse et
# interlignage viennent des tokens ; les tailles de départ sont propres à la
# vidéo (lecture sur téléphone) et se discutent dans 08-video/motion.md.
ROLES = (
    ("display", "typography.h1", 120, "font.display"),
    ("headline", "typography.h2", 84, "font.display"),
    ("title", "typography.h3", 60, "font.display"),
    ("body", "typography.body", 44, "font.display"),
    ("stat", "typography.stat", 160, "font.display"),
    ("label", None, 30, "font.mono"),
)
COULEURS = ("primary", "accent", "dark", "light", "white")
UNIT_RE = re.compile(r'^unit: "la frame : (\d+)×(\d+)"$', re.M)

CORPS = """
## Overview

Charte vidéo de {entreprise}. Le frontmatter est normatif : couleurs, polices, graisses et rayons se citent tels quels, sans arrondi ni invention. La composition est libre.

## Sources

- Palette, polices, rayons : `01-brand/tokens.json`, rendus ici et dans `brand.css` (copié à côté de ce fichier).
- Règles visuelles et tropes bannis : `01-brand/style-guide.md`.
- Anti-générique : `01-brand/design-anti-generique.md`.
- Mouvement, rythme, profil de goût : `08-video/motion.md`.

## The Frame

Toile {largeur}×{hauteur}. Zones de sécurité : {haut} px en haut, {bas} px en bas, {gauche} px à gauche, {droite} px à droite. Aucun texte, sous-titre ni élément essentiel dans ces marges.

## Composition Rules

- Couleurs, polices et rayons passent par les variables de `brand.css` (`var(--brand-primary)`, `var(--font-display)`…), jamais en dur.
- Deux niveaux de texte simultanés au plus.
- Une idée par scène ; jamais trois scènes du même type d'affilée.

## Do's and Don'ts

- Le logo n'apparaît qu'en plan de fin, ou discret en zone sûre.
- Aucune couleur hors de cette palette, aucun dégradé autre que celui de la marque.
- Aucun preset visuel d'HyperFrames (`frame-presets`) : cette charte les remplace.
- Les tropes bannis de `01-brand/style-guide.md` s'appliquent à chaque plan.
"""


def _charger(chemin: Path, nom: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BT = _charger(RACINE / "scripts" / "build-tokens.py", "build_tokens")
TokenError = BT.TokenError


def _exemples(racine: Path) -> dict[str, str]:
    groupes = json.loads((racine / PLACEHOLDERS).read_text(encoding="utf-8"))["groups"]
    return {e["name"]: e["example"] for g in groupes.values() for e in g if "example" in e}


def tokens_exemple(racine: Path) -> dict[str, Any]:
    """Le gabarit de tokens rempli avec les exemples de docs/placeholders.json."""
    exemples = _exemples(racine)
    gabarit = (racine / GABARIT_TOKENS).read_text(encoding="utf-8")
    rempli = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: exemples.get(m.group(1), m.group(0)), gabarit)
    return json.loads(rempli)


def nom_entreprise(racine: Path, exemple: bool) -> str:
    if exemple:
        return _exemples(racine).get("COMPANY_NAME", "Marque")
    setup = racine / ".setup-completed"
    if setup.exists():
        try:
            nom = json.loads(setup.read_text(encoding="utf-8")).get("company")
        except json.JSONDecodeError:
            nom = None
        if isinstance(nom, str) and nom.strip():
            return nom.strip()
    return "Marque"


def _q(texte: str) -> str:
    """Chaîne YAML entre guillemets (une chaîne JSON est une chaîne YAML valide)."""
    return json.dumps(texte, ensure_ascii=False)


def _yaml(valeur: Any) -> str:
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if isinstance(valeur, (int, float)):
        return str(valeur)
    return _q(str(valeur))


def _poids(tokens: dict[str, Any], valeur: Any, contexte: str) -> int:
    if isinstance(valeur, str):
        ref = BT.REF_RE.match(valeur)
        if ref:
            return _poids(tokens, BT.lookup(tokens, ref.group(1)), contexte)
    if isinstance(valeur, bool) or not isinstance(valeur, (int, float)):
        raise TokenError(f"« {contexte} » : graisse invalide {valeur!r}")
    return int(valeur)


def _famille(tokens: dict[str, Any], chemin: str) -> str:
    familles = BT.lookup(tokens, chemin)
    if not isinstance(familles, list) or not familles:
        raise TokenError(f"« {chemin} » : liste de familles attendue")
    return str(familles[0])


def _rayon(tokens: dict[str, Any], nom: str) -> str:
    try:
        valeur = BT.lookup(tokens, f"radius.{nom}")
    except TokenError:
        return "0px"
    return f"{valeur}px" if isinstance(valeur, (int, float)) else str(valeur)


def couleurs(tokens: dict[str, Any]) -> dict[str, str]:
    resultat = {nom: BT.color(tokens, f"color.{nom}") for nom in COULEURS}
    resultat["primary-deep"] = BT.mix_hex(resultat["primary"], "#000000", 0.12)
    resultat["primary-soft"] = BT.mix_hex(resultat["primary"], "#FFFFFF", 0.85)
    return resultat


def typographie(tokens: dict[str, Any], echelle: float) -> list[tuple[str, dict[str, Any]]]:
    roles = []
    for role, chemin, taille, famille in ROLES:
        style: dict[str, Any] = {"fontFamily": _famille(tokens, famille), "px": round(taille * echelle)}
        if chemin:
            valeur = BT.lookup(tokens, chemin)
            if not isinstance(valeur, dict):
                raise TokenError(f"« {chemin} » : objet de typographie attendu")
            if "fontWeight" in valeur:
                style["weight"] = _poids(tokens, valeur["fontWeight"], chemin)
            if "lineHeight" in valeur:
                style["lineHeight"] = valeur["lineHeight"]
        else:
            style.update({"weight": 600, "tracking": "0.12em", "upper": True})
        roles.append((role, style))
    return roles


def construire_frame(tokens: dict[str, Any], *, entreprise: str, aspect: str) -> str:
    BT.validate_tokens(tokens)
    largeur, hauteur = (int(x) for x in aspect.split("x"))
    echelle = min(largeur, hauteur) / 1080
    haut, bas, gauche, droite = MARGES[aspect]
    lignes = [
        "---",
        "version: alpha",
        f"name: {_q(f'{entreprise} · Frame')}",
        "description: " + _q(f"Charte vidéo de {entreprise}, générée depuis 01-brand/tokens.json "
                             "par 08-video/scripts/brand-frame.py. Ne pas éditer à la main : relancer le script."),
        f"unit: {_q(f'la frame : {largeur}×{hauteur}')}",
        "principle: " + _q("atomes de marque intangibles · composition libre · chiffres tirés du script"),
        "",
        "colors:",
        *(f"  {nom}: {_q(valeur)}" for nom, valeur in couleurs(tokens).items()),
        "",
        "typography:",
        *(f"  {role}: {{ " + ", ".join(f"{cle}: {_yaml(v)}" for cle, v in style.items()) + " }"
          for role, style in typographie(tokens, echelle)),
        "",
        "spacing:",
        f"  safe-top: {_q(f'{haut}px')}",
        f"  safe-bottom: {_q(f'{bas}px')}",
        f"  safe-left: {_q(f'{gauche}px')}",
        f"  safe-right: {_q(f'{droite}px')}",
        f"  gap: {_q(f'{round(32 * echelle)}px')}",
        "",
        "components:",
        "  cta:",
        '    backgroundColor: "{colors.accent}"',
        '    textColor: "{colors.dark}"',
        f"    rounded: {_q(_rayon(tokens, 'cta'))}",
        "  badge:",
        f"    rounded: {_q(_rayon(tokens, 'badge'))}",
        "  card:",
        '    backgroundColor: "{colors.white}"',
        f"    rounded: {_q(_rayon(tokens, 'card'))}",
        "  gradient:",
        f"    background: {_q(BT.gradient_css(tokens, 'gradient.signature'))}",
        "  logo:",
        f"    placement: {_q('plan de fin uniquement, ou discret en zone sûre')}",
        "---",
    ]
    corps = CORPS.format(entreprise=entreprise, largeur=largeur, hauteur=hauteur,
                         haut=haut, bas=bas, gauche=gauche, droite=droite)
    return "\n".join(lignes) + "\n" + corps


def brand_css(racine: Path, tokens: dict[str, Any]) -> str:
    """Contenu attendu de la cible 08-video/lib/brand.css pour ces tokens."""
    chemin_config = racine / "scripts" / "build-tokens.toml"
    if not chemin_config.exists():
        chemin_config = RACINE / "scripts" / "build-tokens.toml"
    config = BT.load_config(chemin_config)
    cibles = [c for c in config["targets"] if c["path"] == CIBLE_CSS]
    if not cibles:
        raise TokenError(f"cible {CIBLE_CSS} absente de scripts/build-tokens.toml")
    config = dict(config, targets=cibles)
    base = racine if (racine / CIBLE_CSS).exists() else RACINE
    return BT.expected_contents(base, tokens, config, config.get("tokens", TOKENS_REL))[CIBLE_CSS]


def aspect_existant(dossier: Path) -> str | None:
    frame = dossier / "frame.md"
    if not frame.exists():
        return None
    trouve = UNIT_RE.search(frame.read_text(encoding="utf-8"))
    return f"{trouve.group(1)}x{trouve.group(2)}" if trouve else None


def ecrire(dossier: Path, frame: str, css: str, *, check: bool) -> list[str]:
    """Rend les noms des fichiers qui diffèrent ; les écrit sauf en --check."""
    cibles = {dossier / "frame.md": frame, dossier / "brand.css": css}
    differents = [p for p, contenu in cibles.items()
                  if not p.exists() or p.read_text(encoding="utf-8") != contenu]
    if not check:
        dossier.mkdir(parents=True, exist_ok=True)
        for chemin in differents:
            chemin.write_text(cibles[chemin], encoding="utf-8")
    return [p.name for p in differents]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Écrit frame.md et brand.css d'un projet HyperFrames depuis la marque.")
    p.add_argument("dossier", help="racine du projet HyperFrames (08-video/projets/<slug>/hyperframes)")
    p.add_argument("--aspect", help=f"toile : {', '.join(MARGES)} (défaut : celle du frame.md existant, sinon 1080x1920)")
    p.add_argument("--check", action="store_true", help="ne rien écrire ; sortir 1 si un fichier a dérivé")
    p.add_argument("--exemple", action="store_true", help="palette neutre de docs/placeholders.json")
    p.add_argument("--racine", default=str(RACINE), help="racine du dépôt (défaut : ce dépôt)")
    args = p.parse_args(argv)

    dossier = Path(args.dossier)
    aspect = args.aspect or aspect_existant(dossier) or "1080x1920"
    if aspect not in MARGES:
        print(f"ERREUR : toile « {aspect} » non prise en charge (admises : {', '.join(MARGES)})", file=sys.stderr)
        return 2
    racine = Path(args.racine)
    try:
        tokens = tokens_exemple(racine) if args.exemple else BT.load_tokens(racine / TOKENS_REL)
        frame = construire_frame(tokens, entreprise=nom_entreprise(racine, args.exemple), aspect=aspect)
        css = brand_css(racine, tokens)
    except TokenError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1

    fichiers = ecrire(dossier, frame, css, check=args.check)
    if args.check:
        if fichiers:
            print(f"DIVERGENCE dans {dossier} : {', '.join(fichiers)} ne correspond plus à la marque. "
                  "Relancer sans --check.")
            return 1
        print(f"OK : frame.md et brand.css de {dossier} sont conformes à la marque.")
        return 0
    print(f"écrit dans {dossier} : {', '.join(fichiers)}" if fichiers else f"{dossier} : déjà conforme.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
