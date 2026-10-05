#!/usr/bin/env python3
"""Assemble a static landing page from the section library.

The library lives in 05-web-content/templates/: shared assets in `assets/`
(tokens.css generated from 01-brand/tokens.json, base.css, and the engines
reveal.js, scroll.js, offer.js, tracking.js) and one fragment per proven
section pattern in `sections/<name>.html`. A spec says which sections a page
carries, in which order, with which slot values; this script renders them and
writes one self-contained HTML file (CSS and JS inline by default).

Usage:
    python3 05-web-content/scripts/assemble-landing.py SPEC [-o OUTPUT]
    python3 05-web-content/scripts/assemble-landing.py SPEC --check
    python3 05-web-content/scripts/assemble-landing.py --list
    python3 05-web-content/scripts/assemble-landing.py --describe hero

Spec formats: JSON (`.json`), YAML (`.yaml` / `.yml`, needs PyYAML) or
Markdown with a YAML front matter (`.md`, between two `---` lines; the body is
free notes). Keys (only `title` and `sections` are required):

    output: 05-web-content/landing-pages/<slug>/index.html   # from repo root
    title: "Page title"               lang: fr        page: <slug>
    description: "…"                  robots: "noindex, nofollow"
    canonical: https://…              og: {title, description, image, url}
    favicon: assets/favicon.svg       fonts: ["Inter:wght@400;600;800"]
    tokens: 05-web-content/templates/assets/tokens.css
    assets: inline | link             ground: dots | plain
    theatre: {progress: true}         skip_link: "Aller au contenu"
    tracking: {mode: datalayer | gtm | gtag | off, ga4: G-…, gtm: GTM-…, utm: true}
    offer: {state: open | waitlist | closed, closes_at: ISO date, after_close: waitlist}
    samples: false                    # true: sample copy is intended, no warning
    annotate: false                   # true: catalogue notes before each section
    intro: {title, text}              # catalogue intro (annotate only)
    sections:
      - use: hero                     # fragment name (sections/hero.html)
        id: hero                      # instance id, unique on the page (default: use)
        gated: false                  # true: hidden until the choice gate opens it
        slots: {title: "…", primary: true, items: [{…}, …]}
      - use: _placeholder             # provisional section, for a bespoke one to come
        id: demonstrateur
      - file: sections/05-demonstrateur.html   # bespoke fragment, path from the spec
        id: demonstrateur                       # (inserted as is between its markers)

Fragments: see 05-web-content/templates/sections/README.md. Slots use a
Mustache subset in lowercase: {{name}} (escaped), {{{name}}} (raw HTML),
{{#name}}…{{/name}} (list, object or truthy value), {{^name}}…{{/name}}
(falsy), {{.}} (current item), {{@index}} (1-based), {{@index0}}, {{@first}},
{{@last}}, {{@count}}. Upper-case markers such as {{FORM_ENDPOINT}} are the
repository's install-time placeholders: they are never touched.

A slot the spec does not fill takes the fragment's sample value and is
reported (fictional copy must never ship); `samples: true` silences that for
a demo, `--strict` turns every warning into a failure.

Safety: the output is one file. The script never writes or deletes anything
in a `pilotage/` folder and refuses an output path inside one (it may read a
spec or a builder's fragment from there). It
refuses to overwrite a page edited by hand since its last assembly (the
`generator` meta carries a hash of what it wrote) unless --force.

Exit codes: 0 written (or up to date with --check), 1 warnings under --strict
or a --check mismatch, 2 usage, spec or fragment error, refused write.
Tests: python3 -m pytest scripts/tests/test_assemble_landing.py -q
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

RACINE = Path(__file__).resolve().parents[2]
TEMPLATES = RACINE / "05-web-content" / "templates"
LIBRARY_DEFAUT = TEMPLATES / "sections"
ASSETS_DEFAUT = TEMPLATES / "assets"
TOKENS_DEFAUT = ASSETS_DEFAUT / "tokens.css"

ENGINES = ("reveal", "scroll", "offer", "forms", "tracking")     # load order
ENGINES_TOUJOURS = ("reveal", "tracking")
REGIONS = ("header", "main", "footer", "after")
TYPES_SLOT = {"text", "html", "url", "bool", "list", "number", "object"}
GENERATEUR = "assemble-landing.py"
RE_GENERATEUR = re.compile(r'<meta name="generator" content="assemble-landing\.py · sha256:([0-9a-f]{64})">')
HASH_NUL = "0" * 64


class ErreurAssemblage(Exception):
    """Spec, fragment or write error: exit 2."""


# --------------------------------------------------------------------------
# Mustache subset
# --------------------------------------------------------------------------

RE_TAG = re.compile(
    r"\{\{\{\s*(?P<raw>[a-z_@.][a-z0-9_.@-]*)\s*\}\}\}"
    r"|\{\{(?P<sigil>[#^/]?)\s*(?P<name>[a-z_@.][a-z0-9_.@-]*)\s*\}\}"
)


@dataclass
class Noeud:
    genre: str                       # "var" | "section"
    nom: str
    echappe: bool = True
    inverse: bool = False
    enfants: list = field(default_factory=list)


def analyser(gabarit: str, origine: str = "") -> list:
    """Parse a template into a tree of strings and nodes."""
    racine: list = []
    pile: list[tuple[str, list]] = [("", racine)]
    pos = 0
    for m in RE_TAG.finditer(gabarit):
        pile[-1][1].append(gabarit[pos:m.start()])
        pos = m.end()
        if m.group("raw"):
            pile[-1][1].append(Noeud("var", m.group("raw"), echappe=False))
            continue
        sigil, nom = m.group("sigil"), m.group("name")
        if sigil in ("#", "^"):
            noeud = Noeud("section", nom, inverse=(sigil == "^"))
            pile[-1][1].append(noeud)
            pile.append((nom, noeud.enfants))
        elif sigil == "/":
            if len(pile) == 1 or pile[-1][0] != nom:
                ouvert = pile[-1][0] or "aucune"
                raise ErreurAssemblage(f"{origine} : {{{{/{nom}}}}} ferme {ouvert}")
            pile.pop()
        else:
            pile[-1][1].append(Noeud("var", nom))
    pile[-1][1].append(gabarit[pos:])
    if len(pile) > 1:
        raise ErreurAssemblage(f"{origine} : section {{{{#{pile[-1][0]}}}}} jamais fermée")
    return racine


def noms_racine(arbre: list) -> set[str]:
    """Top-level names a template reads (outside any section)."""
    noms: set[str] = set()
    for n in arbre:
        if isinstance(n, Noeud):
            if not n.nom.startswith("@") and n.nom != ".":
                noms.add(n.nom.split(".")[0])
    return noms


def _cherche(pile: list, nom: str) -> Any:
    if nom == ".":
        return pile[-1]
    tete, *reste = nom.split(".")
    for cadre in reversed(pile):
        if isinstance(cadre, dict) and tete in cadre:
            valeur = cadre[tete]
            for cle in reste:
                if cle == "length" and isinstance(valeur, list):
                    valeur = len(valeur)
                elif isinstance(valeur, dict):
                    valeur = valeur.get(cle)
                else:
                    return None
            return valeur
    return None


def _vrai(valeur: Any) -> bool:
    if valeur is None or valeur is False:
        return False
    if isinstance(valeur, (str, list, dict)) and not valeur:
        return False
    return True


def _texte(valeur: Any) -> str:
    if valeur is None:
        return ""
    if isinstance(valeur, bool):
        return "true" if valeur else "false"
    if isinstance(valeur, float) and valeur.is_integer():
        return str(int(valeur))
    return str(valeur)


def rendre(arbre: list, pile: list) -> str:
    sortie: list[str] = []
    for n in arbre:
        if isinstance(n, str):
            sortie.append(n)
            continue
        valeur = _cherche(pile, n.nom)
        if n.genre == "var":
            texte = _texte(valeur)
            sortie.append(html.escape(texte, quote=True) if n.echappe else texte)
            continue
        if n.inverse:
            if not _vrai(valeur):
                sortie.append(rendre(n.enfants, pile))
            continue
        if not _vrai(valeur):
            continue
        if isinstance(valeur, list):
            total = len(valeur)
            for i, item in enumerate(valeur):
                boucle = {"@index": i + 1, "@index0": i, "@first": i == 0,
                          "@last": i == total - 1, "@count": total}
                sortie.append(rendre(n.enfants, pile + [boucle, item]))
        else:
            sortie.append(rendre(n.enfants, pile + [valeur]))
    return "".join(sortie)


def rendre_texte(gabarit: str, contexte: dict, origine: str = "") -> str:
    return rendre(analyser(gabarit, origine), [contexte])


# --------------------------------------------------------------------------
# Fragments
# --------------------------------------------------------------------------

RE_META = re.compile(r'<script type="application/json" data-section-meta>\s*(.*?)\s*</script>\s*', re.S)
RE_STYLE = re.compile(r'<style data-section-style(?:="[^"]*")?>\s*(.*?)\s*</style>\s*', re.S)
RE_SCRIPT = re.compile(r'<script data-section-script(?:="[^"]*")?>\s*(.*?)\s*</script>\s*', re.S)
RE_RESTE = re.compile(r"\{\{\{?\s*[#^/]?\s*[a-z_@.][a-z0-9_.@-]*\s*\}?\}\}")


@dataclass
class Fragment:
    nom: str
    chemin: Path
    meta: dict
    style: str
    balisage: str
    script: str
    arbre: list

    @property
    def region(self) -> str:
        return self.meta.get("region", "main")

    @property
    def slots(self) -> dict:
        return self.meta.get("slots", {})


def charger_fragment(chemin: Path) -> Fragment:
    if not chemin.is_file():
        raise ErreurAssemblage(f"fragment introuvable : {chemin}")
    source = chemin.read_text(encoding="utf-8")
    nom = chemin.stem
    m = RE_META.search(source)
    if not m:
        raise ErreurAssemblage(f"{chemin.name} : bloc <script type=\"application/json\" data-section-meta> absent")
    try:
        meta = json.loads(m.group(1))
    except json.JSONDecodeError as err:
        raise ErreurAssemblage(f"{chemin.name} : métadonnées JSON invalides ({err})") from err
    if meta.get("id") != nom:
        raise ErreurAssemblage(f"{chemin.name} : meta.id vaut {meta.get('id')!r}, attendu {nom!r}")
    if meta.get("region", "main") not in REGIONS:
        raise ErreurAssemblage(f"{chemin.name} : région {meta.get('region')!r} inconnue ({', '.join(REGIONS)})")
    for moteur in meta.get("engines", []):
        if moteur not in ENGINES:
            raise ErreurAssemblage(f"{chemin.name} : moteur {moteur!r} inconnu ({', '.join(ENGINES)})")
    reste = source[:m.start()] + source[m.end():]
    styles = [s.group(1) for s in RE_STYLE.finditer(reste)]
    reste = RE_STYLE.sub("", reste)
    scripts = [s.group(1) for s in RE_SCRIPT.finditer(reste)]
    balisage = RE_SCRIPT.sub("", reste).strip()
    slots = meta.setdefault("slots", {})
    for nom_slot, spec in slots.items():
        if not isinstance(spec, dict) or "doc" not in spec or "example" not in spec:
            raise ErreurAssemblage(f"{chemin.name} : le slot {nom_slot!r} doit porter « doc » et « example »")
        if spec.get("type", "text") not in TYPES_SLOT:
            raise ErreurAssemblage(f"{chemin.name} : slot {nom_slot!r} de type {spec.get('type')!r} inconnu")
    arbre = analyser(balisage, chemin.name)
    inconnus = sorted(noms_racine(arbre) - set(slots) - {"id"})
    if inconnus:
        raise ErreurAssemblage(f"{chemin.name} : slot(s) lu(s) mais non déclaré(s) : {', '.join(inconnus)}")
    if balisage.count("<!-- section:{{id}} -->") != 1 or balisage.count("<!-- /section:{{id}} -->") != 1:
        raise ErreurAssemblage(f"{chemin.name} : une seule paire de marqueurs <!-- section:{{{{id}}}} --> attendue")
    return Fragment(nom, chemin, meta, "\n".join(styles), balisage, "\n".join(scripts), arbre)


def bibliotheque(dossier: Path) -> dict[str, Fragment]:
    return {p.stem: charger_fragment(p) for p in sorted(dossier.glob("*.html"))
            if not p.name.startswith("_") and p.name != "catalogue.html"}


# --------------------------------------------------------------------------
# Spec
# --------------------------------------------------------------------------

def lire_spec(chemin: Path) -> dict:
    if not chemin.is_file():
        raise ErreurAssemblage(f"spec introuvable : {chemin}")
    texte = chemin.read_text(encoding="utf-8")
    suffixe = chemin.suffix.lower()
    if suffixe == ".json":
        try:
            spec = json.loads(texte)
        except json.JSONDecodeError as err:
            raise ErreurAssemblage(f"{chemin.name} : JSON invalide ({err})") from err
    elif suffixe in (".yaml", ".yml", ".md"):
        if suffixe == ".md":
            m = re.match(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", texte, re.S)
            if not m:
                raise ErreurAssemblage(f"{chemin.name} : front matter YAML (entre deux lignes ---) absent")
            texte = m.group(1)
        try:
            import yaml  # type: ignore
        except ImportError as err:
            raise ErreurAssemblage("spec YAML : PyYAML est requis (pip install pyyaml), "
                                   "ou écrire la spec en JSON") from err
        try:
            spec = yaml.safe_load(texte)
        except yaml.YAMLError as err:
            raise ErreurAssemblage(f"{chemin.name} : YAML invalide ({err})") from err
    else:
        raise ErreurAssemblage(f"{chemin.name} : format de spec inconnu (.json, .yaml, .yml, .md)")
    if not isinstance(spec, dict):
        raise ErreurAssemblage(f"{chemin.name} : la spec doit être un objet")
    if not spec.get("title"):
        raise ErreurAssemblage(f"{chemin.name} : « title » manquant")
    if not isinstance(spec.get("sections"), list) or not spec["sections"]:
        raise ErreurAssemblage(f"{chemin.name} : « sections » doit être une liste non vide")
    return spec


def chemin_depuis_racine(valeur: str | Path) -> Path:
    p = Path(valeur)
    return p if p.is_absolute() else (RACINE / p)


def dans_pilotage(chemin: Path) -> bool:
    return "pilotage" in chemin.resolve().parts or "pilotage" in Path(os.path.abspath(chemin)).parts


# --------------------------------------------------------------------------
# Assembly
# --------------------------------------------------------------------------

@dataclass
class Resultat:
    html: str
    avertissements: list[str]


def _verifier_type(nom: str, spec: dict, valeur: Any, origine: str, avert: list[str]) -> None:
    attendu = spec.get("type", "text")
    if valeur is None:
        return
    ok = {
        "bool": lambda v: isinstance(v, bool),
        "list": lambda v: isinstance(v, list),
        "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
        "object": lambda v: isinstance(v, dict),
    }.get(attendu, lambda v: isinstance(v, (str, int, float)) or v is None)
    if not ok(valeur):
        avert.append(f"{origine} : slot « {nom} » de type {attendu} attendu, reçu {type(valeur).__name__}")


def valeurs_slots(fragment: Fragment, instance: dict, origine: str, samples: bool,
                  avert: list[str]) -> dict:
    fournis = instance.get("slots") or {}
    if not isinstance(fournis, dict):
        raise ErreurAssemblage(f"{origine} : « slots » doit être un objet")
    contexte: dict = {}
    for nom, spec in fragment.slots.items():
        if nom in fournis:
            _verifier_type(nom, spec, fournis[nom], origine, avert)
            contexte[nom] = fournis[nom]
        else:
            contexte[nom] = spec["example"]
            if not samples:
                avert.append(f"{origine} : slot « {nom} » non rempli, texte d'exemple utilisé")
    for nom in sorted(set(fournis) - set(fragment.slots) - {"id"}):
        avert.append(f"{origine} : slot « {nom} » inconnu du fragment {fragment.nom} (ignoré)")
    contexte["id"] = instance.get("id") or fragment.nom
    return contexte


def note_catalogue(fragment: Fragment, instance_id: str) -> str:
    meta = fragment.meta
    e = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731
    lignes = [
        ("Objection traitée", meta.get("objection")),
        ("Quand l'utiliser", meta.get("when")),
        ("Quand l'éviter", meta.get("avoid")),
        ("Mouvement réduit", meta.get("reduced_motion")),
    ]
    blocs = "".join(f"<div><dt>{t}</dt><dd>{e(v)}</dd></div>" for t, v in lignes if v)
    slots = " ".join(f"<code>{e(n)}</code>" for n in fragment.slots)
    moteurs = " ".join(f"<code>{e(m)}</code>" for m in fragment.meta.get("engines", []))
    techniques = f"<div><dt>Slots</dt><dd class=\"lib-note__codes\">{slots}</dd></div>"
    if moteurs:
        techniques += f"<div><dt>Moteurs</dt><dd class=\"lib-note__codes\">{moteurs}</dd></div>"
    return (
        f'<aside class="lib-note" aria-label="Fiche de la section {e(meta.get("name"))}">\n'
        f'  <div class="wrap lib-note__inner">\n'
        f'    <p class="lib-note__head"><code class="lib-note__id">{e(fragment.nom)}</code>'
        f'<span class="lib-note__name">{e(meta.get("name"))}</span>'
        f'<span class="lib-note__anchor">#{e(instance_id)}</span></p>\n'
        f'    <dl class="lib-note__grid">{blocs}{techniques}</dl>\n'
        f'  </div>\n'
        f'</aside>'
    )


def intro_catalogue(spec: dict, plan: list[tuple[Fragment, dict, str]]) -> str:
    intro = spec.get("intro") or {}
    e = lambda s: html.escape(str(s or ""), quote=True)  # noqa: E731
    liens = "".join(
        f'<li><a href="#{e(cid)}"><code>{e(f.nom)}</code> {e(f.meta.get("name"))}</a></li>'
        for f, _, cid in plan if f.region == "main")
    return (
        '<div class="lib-intro">\n'
        '  <div class="wrap lib-intro__inner">\n'
        f'    <p class="lib-intro__title">{e(intro.get("title", "Bibliothèque de sections"))}</p>\n'
        f'    <p class="lib-intro__text">{e(intro.get("text", ""))}</p>\n'
        f'    <nav class="lib-intro__toc" aria-label="Sections du catalogue"><ol role="list">{liens}</ol></nav>\n'
        '  </div>\n'
        '</div>'
    )


def _google_fonts(familles: list[str]) -> str:
    if not familles:
        return ""
    params = "&".join("family=" + f.strip().replace(" ", "+") for f in familles)
    return ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{params}&display=swap">')


def _suivi_head(suivi: dict) -> str:
    mode = suivi.get("mode", "datalayer")
    if mode == "off":
        return ""
    morceaux = ["<script>window.dataLayer = window.dataLayer || [];</script>"]
    if mode == "gtm" and suivi.get("gtm"):
        gtm = html.escape(suivi["gtm"], quote=True)
        morceaux.append(
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),"
            "event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;"
            f"j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);}})"
            f"(window,document,'script','dataLayer','{gtm}');</script>")
    if mode == "gtag" and suivi.get("ga4"):
        ga4 = html.escape(suivi["ga4"], quote=True)
        morceaux.append(f'<script async src="https://www.googletagmanager.com/gtag/js?id={ga4}"></script>')
        morceaux.append("<script>function gtag(){dataLayer.push(arguments);}gtag('js', new Date());"
                        f"gtag('config', '{ga4}');</script>")
    return "\n".join(morceaux)


def fragment_de_fichier(instance: dict, i: int, spec_dir: Path | None, avert: list[str]) -> tuple[Fragment, str]:
    """A bespoke section written by a builder (pilotage/sections/<nn>-<id>.html), inserted as is.

    The file is read, never written. It carries its own <section>, <style> and
    <script> (charter § 8); the assembler only puts it between its markers.
    """
    if instance.get("use"):
        raise ErreurAssemblage(f"sections[{i}] : « use » et « file » sont exclusifs")
    cid = instance.get("id")
    if not cid or not re.fullmatch(r"[a-z][a-z0-9-]*", cid):
        raise ErreurAssemblage(f"sections[{i}] : « file » demande un « id » valide (minuscules, chiffres, tirets)")
    chemin = Path(instance["file"])
    if not chemin.is_absolute():
        chemin = (spec_dir or RACINE) / chemin
    if not chemin.is_file():
        raise ErreurAssemblage(f"sections[{i}] : fichier introuvable : {chemin}")
    contenu = chemin.read_text(encoding="utf-8").strip()
    debut, fin = f"<!-- section:{cid} -->", f"<!-- /section:{cid} -->"
    if debut not in contenu:
        contenu = f"{debut}\n{contenu}\n{fin}"
    if contenu.count(debut) != 1 or contenu.count(fin) != 1:
        raise ErreurAssemblage(f"sections[{i}] : {chemin.name} doit porter une seule paire de marqueurs {cid}")
    if f'id="{cid}"' not in contenu:
        avert.append(f"{cid} : {chemin.name} ne porte pas id=\"{cid}\" sur sa section")
    meta = {"id": cid, "name": f"Section sur mesure ({chemin.name})", "slots": {}}
    return Fragment(f"file:{chemin.name}", chemin, meta, "", contenu, "", [contenu]), cid


def assembler(spec: dict, *, spec_dir: Path | None = None, library: Path | None = None,
              assets: Path | None = None, sortie: Path | None = None) -> Resultat:
    avert: list[str] = []
    library = library or chemin_depuis_racine(spec.get("library", LIBRARY_DEFAUT))
    assets = assets or ASSETS_DEFAUT
    samples_page = bool(spec.get("samples", False))
    annotate = bool(spec.get("annotate", False))

    # ---- plan: fragments, slot values, instance ids ----
    cache: dict[str, Fragment] = {}
    plan: list[tuple[Fragment, dict, str]] = []
    vus: set[str] = set()
    for i, instance in enumerate(spec["sections"]):
        if isinstance(instance, str):
            instance = {"use": instance}
        if isinstance(instance, dict) and instance.get("file"):
            fragment, cid = fragment_de_fichier(instance, i, spec_dir, avert)
            if cid in vus:
                raise ErreurAssemblage(f"sections[{i}] : id {cid!r} en double sur la page")
            vus.add(cid)
            plan.append((fragment, {**instance, "_contexte": {"id": cid}}, cid))
            continue
        if not isinstance(instance, dict) or not instance.get("use"):
            raise ErreurAssemblage(f"sections[{i}] : « use » (nom du fragment) ou « file » manquant")
        nom = instance["use"]
        if nom not in cache:
            cache[nom] = charger_fragment(library / f"{nom}.html")
        fragment = cache[nom]
        cid = instance.get("id") or nom
        if not re.fullmatch(r"[a-z][a-z0-9-]*", cid):
            raise ErreurAssemblage(f"sections[{i}] : id {cid!r} invalide (minuscules, chiffres, tirets)")
        if cid in vus:
            raise ErreurAssemblage(f"sections[{i}] : id {cid!r} en double sur la page")
        vus.add(cid)
        samples = samples_page or bool(instance.get("samples", False))
        contexte = valeurs_slots(fragment, {**instance, "id": cid}, f"{cid} ({nom})", samples, avert)
        plan.append((fragment, {**instance, "_contexte": contexte}, cid))

    # ---- body ----
    regions: dict[str, list[str]] = {r: [] for r in REGIONS}
    gate_ouvert = False
    notes_hors_main: list[str] = []
    for fragment, instance, cid in plan:
        rendu = rendre(fragment.arbre, [instance["_contexte"]]).strip()
        for reste in RE_RESTE.findall(rendu):
            avert.append(f"{cid} : balise de slot non résolue {reste}")
        if fragment.region != "main":
            regions[fragment.region].append(rendu)
            if annotate:
                notes_hors_main.append(note_catalogue(fragment, cid))
            continue
        bloc = rendu
        if annotate:
            bloc = note_catalogue(fragment, cid) + "\n" + bloc
        gated = bool(instance.get("gated", False))
        if gated and not gate_ouvert:
            regions["main"].append('<div class="gated" data-gated hidden>')
            gate_ouvert = True
        elif not gated and gate_ouvert:
            regions["main"].append("</div>")
            gate_ouvert = False
        regions["main"].append(bloc)
    if gate_ouvert:
        regions["main"].append("</div>")
    if annotate:
        regions["main"].insert(0, intro_catalogue(spec, plan))
        regions["main"].extend(notes_hors_main)
    if any(i.get("gated") for _, i, _ in plan) and not any(f.nom == "choice-gate" for f, _, _ in plan):
        avert.append("des sections sont « gated » mais la page n'a pas de porte de choix (choice-gate) : "
                     "elles resteront cachées")

    # ---- assets ----
    moteurs = set(ENGINES_TOUJOURS) | set(spec.get("engines", []))
    for fragment, _, _ in plan:
        moteurs |= set(fragment.meta.get("engines", []))
    if spec.get("offer"):
        moteurs.add("offer")
    if (spec.get("theatre") or {}).get("progress"):
        moteurs.add("scroll")
    tokens = chemin_depuis_racine(spec["tokens"]) if spec.get("tokens") else assets / "tokens.css"
    if not tokens.is_file():
        raise ErreurAssemblage(f"fichier de tokens introuvable : {tokens}")
    css_fichiers = [tokens, assets / "base.css"]
    if annotate:
        css_fichiers.append(assets / "catalogue.css")
    js_fichiers = [assets / f"{m}.js" for m in ENGINES if m in moteurs]
    for f in css_fichiers + js_fichiers:
        if not f.is_file():
            raise ErreurAssemblage(f"asset introuvable : {f}")

    styles_sections, scripts_sections, deja = [], [], set()
    for fragment, _, _ in plan:
        if fragment.nom in deja:
            continue
        deja.add(fragment.nom)
        if fragment.style:
            styles_sections.append(f"/* ---- section : {fragment.nom} ---- */\n{fragment.style}")
        if fragment.script:
            scripts_sections.append(f"/* ---- section : {fragment.nom} ---- */\n{fragment.script}")

    mode_assets = spec.get("assets", "inline")
    if mode_assets not in ("inline", "link"):
        raise ErreurAssemblage("« assets » vaut inline ou link")
    if mode_assets == "inline":
        css_assets = "\n".join(f"/* ---- {f.name} ---- */\n{f.read_text(encoding='utf-8').strip()}"
                               for f in css_fichiers)
        head_css = f"<style>\n{css_assets}\n{chr(10).join(styles_sections)}\n</style>"
        js_assets = "\n".join(f"<script>\n/* ---- {f.name} ---- */\n{f.read_text(encoding='utf-8').strip()}\n</script>"
                              for f in js_fichiers)
    else:
        base = (sortie.parent if sortie else RACINE)
        rel = lambda f: html.escape(Path(os.path.relpath(f, base)).as_posix(), quote=True)  # noqa: E731
        head_css = "\n".join(f'<link rel="stylesheet" href="{rel(f)}">' for f in css_fichiers)
        head_css += f"\n<style>\n{chr(10).join(styles_sections)}\n</style>"
        js_assets = "\n".join(f'<script src="{rel(f)}"></script>' for f in js_fichiers)
    js_sections = f"<script>\n{chr(10).join(scripts_sections)}\n</script>" if scripts_sections else ""

    # ---- configuration ----
    page = spec.get("page") or (sortie.parent.name if sortie else "landing")
    suivi = dict(spec.get("tracking") or {})
    suivi.setdefault("mode", "datalayer")
    if suivi["mode"] not in ("datalayer", "gtm", "gtag", "off"):
        raise ErreurAssemblage("tracking.mode vaut datalayer, gtm, gtag ou off")
    config = {"page": page, "tracking": {"mode": suivi["mode"], "utm": suivi.get("utm", True), "page": page}}
    if spec.get("offer"):
        config["offer"] = spec["offer"]
    config_js = json.dumps(config, ensure_ascii=False).replace("</", "<\\/")

    e = lambda s: html.escape(str(s), quote=True)  # noqa: E731
    head = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{e(spec['title'])}</title>",
    ]
    if spec.get("description"):
        head.append(f'<meta name="description" content="{e(spec["description"])}">')
    head.append(f'<meta name="robots" content="{e(spec.get("robots", "noindex, nofollow"))}">')
    if spec.get("canonical"):
        head.append(f'<link rel="canonical" href="{e(spec["canonical"])}">')
    for cle, valeur in (spec.get("og") or {}).items():
        head.append(f'<meta property="og:{e(cle)}" content="{e(valeur)}">')
    if spec.get("favicon"):
        head.append(f'<link rel="icon" href="{e(spec["favicon"])}">')
    head.append(f'<meta name="generator" content="{GENERATEUR} · sha256:{HASH_NUL}">')
    polices = _google_fonts(spec.get("fonts") or [])
    if polices:
        head.append(polices)
    suivi_head = _suivi_head(suivi)
    if suivi_head:
        head.append(suivi_head)
    head.append(f"<script>window.LANDING_CONFIG = {config_js};</script>")
    head.append(head_css)

    corps = []
    sol = spec.get("ground", "dots")
    attributs = f' data-page-slug="{e(page)}"' + (' data-ground="plain"' if sol == "plain" else "")
    corps.append(f'<a class="skip-link" href="#contenu">{e(spec.get("skip_link", "Aller au contenu"))}</a>')
    if (spec.get("theatre") or {}).get("progress"):
        corps.append('<div class="reading-progress" aria-hidden="true"></div>')
    corps.extend(regions["header"])
    corps.append('<main id="contenu">')
    corps.extend(regions["main"])
    corps.append("</main>")
    corps.extend(regions["footer"])
    corps.extend(regions["after"])
    if any(f.nom == "choice-gate" for f, _, _ in plan):
        corps.append('<noscript><style>[data-gated][hidden]{display:block !important}</style></noscript>')
    corps.append(js_assets)
    if js_sections:
        corps.append(js_sections)

    document = (
        "<!DOCTYPE html>\n"
        f'<html lang="{e(spec.get("lang", "fr"))}">\n'
        "<head>\n" + "\n".join(head) + "\n</head>\n"
        f"<body{attributs}>\n" + "\n".join(corps) + "\n</body>\n</html>\n"
    )
    empreinte = hashlib.sha256(document.encode("utf-8")).hexdigest()
    document = document.replace(f"sha256:{HASH_NUL}", f"sha256:{empreinte}", 1)
    return Resultat(document, avert)


def empreinte_valide(texte: str) -> bool | None:
    """True: unchanged since assembly; False: edited by hand; None: not an assembled page."""
    m = RE_GENERATEUR.search(texte)
    if not m:
        return None
    neutre = texte.replace(f"sha256:{m.group(1)}", f"sha256:{HASH_NUL}", 1)
    return hashlib.sha256(neutre.encode("utf-8")).hexdigest() == m.group(1)


# --------------------------------------------------------------------------
# Command line
# --------------------------------------------------------------------------

def decrire(fragment: Fragment) -> str:
    meta = fragment.meta
    lignes = [f"{fragment.nom} · {meta.get('name', '')}",
              f"  région : {fragment.region}" + (f" · moteurs : {', '.join(meta['engines'])}" if meta.get("engines") else "")]
    for cle, titre in (("objection", "objection"), ("when", "quand"), ("avoid", "pas quand"),
                       ("reduced_motion", "mouvement réduit")):
        if meta.get(cle):
            lignes.append(f"  {titre} : {meta[cle]}")
    lignes.append("  slots :")
    for nom, spec in fragment.slots.items():
        lignes.append(f"    {nom} ({spec.get('type', 'text')}) : {spec['doc']}")
        for champ, doc in (spec.get("fields") or {}).items():
            lignes.append(f"      .{champ} : {doc}")
    return "\n".join(lignes)


def construire_parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Assemble une landing statique depuis la bibliothèque de sections "
                                            "(05-web-content/templates/sections/).")
    p.add_argument("spec", nargs="?", help="spec de la page (.json, .yaml, .yml, .md à front matter)")
    p.add_argument("-o", "--output", help="fichier de sortie (prime sur « output » de la spec)")
    p.add_argument("--library", help="dossier des fragments (défaut : 05-web-content/templates/sections)")
    p.add_argument("--check", action="store_true", help="ne rien écrire ; sortir 1 si la sortie diffère")
    p.add_argument("--strict", action="store_true", help="tout avertissement fait échouer (sortie 1, rien d'écrit)")
    p.add_argument("--force", action="store_true", help="écraser une page modifiée à la main depuis son assemblage")
    p.add_argument("--list", action="store_true", help="lister les fragments de la bibliothèque")
    p.add_argument("--describe", metavar="FRAGMENT", help="décrire un fragment et ses slots")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)
    try:
        library = Path(args.library).resolve() if args.library else LIBRARY_DEFAUT
        if args.list or args.describe:
            frags = bibliotheque(library)
            if args.describe:
                chemin = library / f"{args.describe}.html"
                if args.describe not in frags and not chemin.is_file():
                    raise ErreurAssemblage(f"fragment inconnu : {args.describe}")
                print(decrire(frags.get(args.describe) or charger_fragment(chemin)))
            else:
                for nom, f in frags.items():
                    print(f"{nom:18} {f.region:7} {f.meta.get('name', '')}")
            return 0
        if not args.spec:
            raise ErreurAssemblage("spec manquante (ou --list / --describe)")
        chemin_spec = Path(args.spec).resolve()
        spec = lire_spec(chemin_spec)
        if args.library:
            spec["library"] = str(library)
        cible = args.output or spec.get("output")
        if not cible:
            raise ErreurAssemblage("aucune sortie : « output » dans la spec ou -o")
        sortie = Path(cible) if Path(cible).is_absolute() else (Path.cwd() / cible if args.output else RACINE / cible)
        if dans_pilotage(sortie):
            raise ErreurAssemblage(f"sortie refusée : {sortie} est dans un dossier pilotage/ (fabrication, "
                                   "jamais écrite par l'assembleur)")
        resultat = assembler(spec, spec_dir=chemin_spec.parent, library=library, sortie=sortie)
    except ErreurAssemblage as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2

    for a in resultat.avertissements:
        print(f"avertissement : {a}", file=sys.stderr)

    actuel = sortie.read_text(encoding="utf-8") if sortie.is_file() else None
    if args.check:
        if actuel == resultat.html:
            print(f"OK : {sortie} est à jour.")
            return 0
        print(f"DIVERGENCE : {sortie} ne correspond plus à la spec et aux fragments. Relancer sans --check.")
        return 1
    if args.strict and resultat.avertissements:
        print(f"ÉCHEC (--strict) : {len(resultat.avertissements)} avertissement(s), rien n'est écrit.",
              file=sys.stderr)
        return 1
    if actuel is not None and not args.force:
        etat = empreinte_valide(actuel)
        if etat is None:
            print(f"ERREUR : {sortie} existe et n'a pas été produit par {GENERATEUR} : --force pour l'écraser.",
                  file=sys.stderr)
            return 2
        if etat is False:
            print(f"ERREUR : {sortie} a été modifié à la main depuis son assemblage : --force pour l'écraser "
                  "(les retouches seront perdues).", file=sys.stderr)
            return 2
    if actuel == resultat.html:
        print(f"Rien à faire : {sortie} est à jour.")
        return 0
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(resultat.html, encoding="utf-8")
    taille = len(resultat.html.encode("utf-8")) / 1024
    print(f"écrit : {sortie} ({taille:.0f} Ko, {len(resultat.avertissements)} avertissement(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
