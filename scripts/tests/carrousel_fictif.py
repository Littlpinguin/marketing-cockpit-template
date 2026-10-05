"""Dépôt fictif pour les tests de 06-graphic-design/scripts/build-carousel.py.

Le générateur lit ses couleurs dans `01-brand/tokens.json`, ses assets dans
`01-brand/assets/` et ses specs dans `06-graphic-design/outputs/` : tout est
relatif à la racine du dépôt où vit le script. Les tests recopient donc le script
dans une racine jetable, peuplée d'une marque fictive (« Acme », les exemples de
docs/placeholders.json), et chargent cette copie. Le vrai dépôt n'est jamais lu
ni écrit.

Ce module n'est pas un fichier de test (pas de préfixe `test_`) : les modules de
test le chargent par chemin.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "06-graphic-design" / "scripts"

TOKENS_FICTIFS = {
    "color": {
        "primary": {"$value": "#1E40AF"},
        "accent": {"$value": "#F59E0B"},
        "tertiary": {"$value": "#10B981"},
        "dark": {"$value": "#0F172A"},
        "light": {"$value": "#F8FAFC"},
        "white": {"$value": "#FFFFFF"},
        "primary-light": {"$value": "#93C5FD"},
    },
    "font": {
        "primary": {"$value": ["Inter", "system-ui", "sans-serif"]},
    },
}

SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 60"><rect width="100" height="60" fill="#0F172A"/></svg>'

ASSETS = {
    "logo": "01-brand/assets/logos/logo_acme_principal.svg",
    "forme_titre": "01-brand/assets/patterns/patterns_forme-titre_sombre.svg",
    "medaillon_1": "01-brand/assets/illustrations/illustrations_medaillon_un.svg",
    "medaillon_2": "01-brand/assets/illustrations/illustrations_medaillon_deux.svg",
    "embleme": "01-brand/assets/illustrations/illustrations_embleme_etoile.svg",
    "sceau": "01-brand/assets/logos/logos_sceau_rond.svg",
    "scene": "01-brand/assets/illustrations/scenes/illustrations_scene_atelier (v2).svg",
    "portrait": "01-brand/assets/photos/photos_portrait_exemple.svg",
    "photo": "06-graphic-design/outputs/photos/vue fenêtre.svg",
}

MARQUE = {
    "pied": "acme.example",
    "logo": ASSETS["logo"],
    "forme_titre": ASSETS["forme_titre"],
    "medaillons": [ASSETS["medaillon_1"], ASSETS["medaillon_2"]],
    "embleme": ASSETS["embleme"],
    "sceau": ASSETS["sceau"],
}

SPEC_PORTRAIT = {
    "slug": "demo-portrait", "date": "2026-01-15", "lang": "fr",
    "marque": MARQUE,
    "slides": [
        {"type": "cover", "eyebrow": "Un exemple", "title": ["Une cover", ["g", "en dégradé"]],
         "lede": ["Une promesse courte", "sur deux lignes"]},
        {"type": "statement", "title": ["Une affirmation", ["primaire", "nette"]], "illo": 1,
         "side": "r", "lede": "Un sous-titre", "route": [470, 1050]},
        {"type": "stat", "eyebrow": "Source fictive", "number": "42%", "caption": "Un chiffre héros"},
        {"type": "points", "eyebrow": "Trois points", "title": "Une liste",
         "points": ["Premier point", "Deuxième point", "Troisième point"], "scene": ASSETS["scene"]},
        {"type": "manifesto", "lines": ["Une ligne", "Une autre", "Une dernière"], "illo": 2},
        {"type": "photobook", "title": [["g", "Un triptyque"]],
         "photos": [[ASSETS["photo"], "Un"], [ASSETS["photo"], "Deux"], [ASSETS["photo"], "Trois"]]},
        {"type": "window", "side": "l", "img": ASSETS["photo"], "place": "Un lieu",
         "coords": "0.00°N · 0.00°E", "etiquette": "Une étiquette", "route": [1050, 350],
         "route_start": True},
        {"type": "portrait_cover", "eyebrow": "Portrait", "name": "Prénom Fictif",
         "role": "Un rôle", "img": ASSETS["portrait"]},
        {"type": "finale_stats", "title": ["Une finale"], "stats": [["12", "un libellé"]],
         "lede": "Un message", "img": ASSETS["portrait"]},
        {"type": "finale_portrait", "title": ["Merci"], "lede": "Un message de clôture",
         "welcome": "Une ligne d'accueil", "cta": "acme.example", "img": ASSETS["portrait"]},
        {"type": "cta", "title": ["Passer à l'action"], "rows": ["Une ligne de données"],
         "kicker": "acme.example"},
    ],
}

SPEC_THESE = {
    "slug": "demo-these", "date": "2026-02-01",
    "marque": {"pied": "acme.example", "logo": ASSETS["logo"]},
    "slides": [
        {"type": "t_cover", "eyebrow": "Une thèse", "folio": "01", "title": ["Une thèse", ["g", "chiffrée"]],
         "lede": "Un sous-titre"},
        {"type": "t_statement", "title": ["Un constat"], "lede": "Une explication", "art": ASSETS["scene"]},
        {"type": "t_stat", "number": "3×", "eyebrow": "Source fictive", "caption": "Une légende"},
        {"type": "t_points", "title": ["Des points"], "points": ["Un", "Deux"]},
        {"type": "t_manifesto", "lines": ["Une", "Deux", "Trois"], "dark": True},
        {"type": "t_cta", "title": ["Agir"], "rows": ["Une ligne"], "kicker": "acme.example"},
    ],
}

SPECS = [SPEC_PORTRAIT, SPEC_THESE]


def dossier_spec(racine: Path, spec: dict) -> Path:
    return racine / "06-graphic-design" / "outputs" / f'carrousel-{spec["slug"]}-{spec["date"]}'


def creer_depot(racine: Path, tokens: dict | None = None, polices: bool = True) -> Path:
    """Peuple une racine jetable : script, tokens, assets, police locale, specs."""
    scripts = racine / "06-graphic-design" / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    for nom in ("build-carousel.py", ".grain-tile.b64", "export-carousel-pdf.py"):
        shutil.copy2(SCRIPTS / nom, scripts / nom)

    marque = racine / "01-brand"
    marque.mkdir(parents=True, exist_ok=True)
    (marque / "tokens.json").write_text(
        json.dumps(tokens if tokens is not None else TOKENS_FICTIFS, ensure_ascii=False),
        encoding="utf-8")
    for chemin in ASSETS.values():
        cible = racine / chemin
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(SVG, encoding="utf-8")
    if polices:
        fonts = marque / "assets" / "fonts"
        fonts.mkdir(parents=True, exist_ok=True)
        (fonts / "fonts.css").write_text(
            "@font-face{font-family:'Inter';font-display:block;src:url('inter.woff2') format('woff2');}\n",
            encoding="utf-8")

    for spec in SPECS:
        dossier = dossier_spec(racine, spec)
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / "carrousel.json").write_text(json.dumps(spec, ensure_ascii=False, indent=2),
                                                encoding="utf-8")
    return racine


def charger(racine: Path):
    """Charge la copie du script posée dans la racine jetable."""
    chemin = racine / "06-graphic-design" / "scripts" / "build-carousel.py"
    spec = importlib.util.spec_from_file_location(f"build_carousel_{uuid.uuid4().hex}", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def empreinte(racine: Path) -> dict[str, float]:
    """Date de modification de chaque fichier de la racine jetable."""
    return {str(p): p.stat().st_mtime for p in sorted(racine.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}
