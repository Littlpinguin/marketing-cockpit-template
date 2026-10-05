#!/usr/bin/env python3
"""Générateur de carrousels LinkedIn brand-strict : une spec JSON, un HTML, un PDF.

Le moteur ne contient aucune valeur de marque :
  - les couleurs se lisent dans `01-brand/tokens.json` (aucun hex en dur ici) ;
  - la police est la première famille de `font.primary` (à défaut `font.display`,
    à défaut le premier token `font.*`), servie en local par
    `01-brand/assets/fonts/fonts.css` (voir `06-graphic-design/lib/README.md`) ;
  - le logo, la forme de titre, les médaillons, l'emblème et le sceau sont des
    assets de `01-brand/assets/`, désignés par la spec ;
  - le texte de chaque slide vient de la spec.

Format 1080×1350 (4:5 portrait, optimum du fil LinkedIn mobile). Échelle typo et
d'espacement STRICTE (voir la skill `carousel`) : aucun texte de contenu sous
28 px, pied de slide à 22 px, les planchers que contrôle `qa-visuel.py`. Anti-patterns appliqués : pas de
folio (LinkedIn numérote les pages), pied = le domaine seul, pas de point final
sur les titres, tiret insécable dans les mots composés.

SPEC — un fichier `carrousel.json` par carrousel, rangé dans son dossier de
sortie `06-graphic-design/outputs/carrousel-<slug>-<date>/` :

    {
      "slug": "exemple", "date": "2026-01-15", "lang": "fr",
      "marque": {
        "pied": "exemple.com",                       // texte du pied de slide
        "logo": "01-brand/assets/logos/logo.svg",     // optionnel
        "forme_titre": "01-brand/assets/patterns/forme-titre.svg",  // optionnel
        "medaillons": ["01-brand/assets/illustrations/m1.svg"],     // optionnel
        "embleme": "01-brand/assets/illustrations/embleme.svg",     // optionnel
        "sceau": "01-brand/assets/logos/sceau.png",                 // optionnel
        "couleurs": {"primaire": "color.primary"}    // optionnel : rôle → token
      },
      "slides": [ {"type": "cover", "title": ["Une ligne", ["g", "en dégradé"]]}, ... ]
    }

Chemins relatifs à la racine du dépôt. Rôles de couleur et token lu par défaut :
primaire `color.primary`, accent `color.accent`, sombre `color.dark`, clair
`color.light` (obligatoires) ; tertiaire `color.tertiary` (arrêt médian du
dégradé, à défaut dégradé à deux couleurs), blanc `color.white` (à défaut le
clair), primaire-clair `color.primary-light` (titre primaire posé sur la forme
sombre, à défaut le primaire). `marque.couleurs` remappe un rôle vers un autre
chemin de token quand `tokens.json` les nomme autrement.

L'eyebrow (surtitre en capitales espacées) reste optionnel sur chaque slide : la
doctrine de `06-graphic-design/compositions-carrousel.md` le déconseille, mieux vaut
replier l'information dans le titre.

Lignes de titre : une chaîne (ligne pleine), `["g", "texte"]` (ligne en dégradé,
bloc autonome rastérisé à l'export), `["primaire", "texte"]` (couleur primaire),
`["html", "..."]` (HTML brut). Jamais de dégradé au milieu d'une phrase.

Types de slides : cover, stat, statement, points, manifesto, cta, portrait_cover,
photobook, finale_stats, finale_portrait, window (famille « portrait / photo ») ;
t_cover, t_statement, t_stat, t_points, t_manifesto, t_cta (famille « thèse » :
grille cassée, alignée à gauche, sans forme de titre). Les paramètres de chaque
type se lisent dans sa fonction de rendu ci-dessous.

Usage : le script écrit dans `06-graphic-design/outputs/`, il ne se lance donc
jamais à vide. Lancé sans argument, il affiche son aide et sort en 2.

  build-carousel.py --help
  build-carousel.py <slug|carrousel.json> [...]   construit ces carrousels et rien d'autre
  build-carousel.py --all                         reconstruit tous les carrousels
  build-carousel.py --all --dry-run               liste ce qui serait construit, sans écrire
  build-carousel.py <slug> --sans-pdf             écrit le HTML seul (QA avant export)

GRID=1 dans l'environnement superpose une grille de repère (mise au point).
"""
from __future__ import annotations

import argparse
import html as _html
import json
import os
import pathlib
import re
import subprocess
import sys
from urllib.parse import quote

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "06-graphic-design" / "scripts"
SORTIES = ROOT / "06-graphic-design" / "outputs"
TOKENS = ROOT / "01-brand" / "tokens.json"
FONTS_CSS = ROOT / "01-brand" / "assets" / "fonts" / "fonts.css"
NOM_SPEC = "carrousel.json"


class ErreurSpec(Exception):
    """Spec ou tokens inutilisables : sortie 2, sans rien écrire."""


def _grid():
    """Overlay de grille de repère (mise au point), activé par GRID=1. Lignes
    horizontales tous les 50px + numéros + axe vertical central (x=540).

    Les deux couleurs de cet overlay sont volontairement hors palette : ce sont
    des repères d'atelier, jamais rendus dans un carrousel livré (GRID absent de
    l'environnement au build). Les voir dans une page signale un rendu de mise
    au point, pas une sortie de charte."""
    if not os.environ.get("GRID"):
        return ""
    lines = "".join(
        f'<line x1="0" y1="{y}" x2="1080" y2="{y}" stroke="#e0245e" '
        f'stroke-width="{2 if y % 100 == 0 else 1}" opacity=".5"/>'
        f'<text x="6" y="{y - 3}" fill="#e0245e" font-size="15">{y}</text>'
        for y in range(0, 1350, 50))
    return (f'<svg style="position:absolute;inset:0;z-index:99;pointer-events:none" '
            f'width="1080" height="1350">{lines}'
            f'<line x1="540" y1="0" x2="540" y2="1350" stroke="#1d9bf0" '
            f'stroke-width="2" opacity=".6"/></svg>')


# --------------------------------------------------------------------------
# COULEURS ET POLICE : lues dans 01-brand/tokens.json, jamais recopiées ici
# --------------------------------------------------------------------------
# Ce fichier est un .py : une couleur écrite en dur ici repartirait dans chaque
# index.html à chaque rebuild sans qu'aucun contrôle de fichier texte ne la voie.
# Les couleurs viennent donc de la source unique, rôle par rôle.

ROLES_DEFAUT = {
    "primaire": "color.primary",
    "accent": "color.accent",
    "sombre": "color.dark",
    "clair": "color.light",
    "tertiaire": "color.tertiary",
    "blanc": "color.white",
    "primaire-clair": "color.primary-light",
}
ROLES_OBLIGATOIRES = ("primaire", "accent", "sombre", "clair")
# Rôle optionnel absent : on retombe sur un rôle obligatoire. None = pas de repli
# (le tertiaire absent donne un dégradé à deux couleurs).
REPLIS = {"tertiaire": None, "blanc": "clair", "primaire-clair": "primaire"}
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _lire_tokens(chemin: pathlib.Path = TOKENS) -> dict:
    if not chemin.exists():
        raise ErreurSpec(f"{chemin.relative_to(ROOT) if chemin.is_relative_to(ROOT) else chemin} "
                         f"introuvable : les couleurs du carrousel s'y lisent")
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as err:
        raise ErreurSpec(f"{chemin} n'est pas un JSON valide : {err}") from err


def _token(arbre: dict, chemin: str):
    noeud = arbre
    for segment in chemin.split("."):
        if not isinstance(noeud, dict) or segment not in noeud:
            return None
        noeud = noeud[segment]
    return noeud.get("$value") if isinstance(noeud, dict) else None


def couleurs(spec: dict | None = None, tokens: dict | None = None) -> dict[str, str]:
    """Couleurs du carrousel par rôle, lues dans tokens.json. Clés : rôles locaux.

    Le rôle `tertiaire` est absent du résultat quand tokens.json ne le porte pas.
    """
    tokens = tokens if tokens is not None else _lire_tokens()
    roles = dict(ROLES_DEFAUT)
    roles.update(((spec or {}).get("marque") or {}).get("couleurs") or {})
    lues: dict[str, str] = {}
    for role, chemin in roles.items():
        valeur = _token(tokens, chemin)
        if isinstance(valeur, str) and HEX.match(valeur.strip()):
            lues[role] = valeur.strip()
    manquants = [r for r in ROLES_OBLIGATOIRES if r not in lues]
    if manquants:
        raise ErreurSpec(
            "couleurs introuvables dans tokens.json pour les rôles "
            + ", ".join(f"{r} ({roles[r]})" for r in manquants)
            + " : renseigner ces tokens ou remapper les rôles dans marque.couleurs")
    for role, repli in REPLIS.items():
        if role not in lues and repli:
            lues[role] = lues[repli]
    return lues


def police(tokens: dict | None = None) -> str:
    """Famille de la marque : `font.primary`, à défaut `font.display`, à défaut le premier `font.*`."""
    tokens = tokens if tokens is not None else _lire_tokens()
    fonts = tokens.get("font") or {}
    ordre = ["primary", "display"] + [k for k in fonts if not k.startswith("$")]
    for cle in ordre:
        noeud = fonts.get(cle)
        valeur = noeud.get("$value") if isinstance(noeud, dict) else None
        if isinstance(valeur, list) and valeur and isinstance(valeur[0], str):
            return valeur[0].strip().strip("\"'")
        if isinstance(valeur, str) and valeur.strip():
            return valeur.split(",")[0].strip().strip("\"'")
    raise ErreurSpec("aucune famille de police dans tokens.json (font.primary ou font.display)")


def _rgb(hexa: str) -> tuple[int, int, int]:
    return tuple(int(hexa[i:i + 2], 16) for i in (1, 3, 5))


def degrade_css(c: dict[str, str]) -> str:
    """Dégradé de marque : primaire → (tertiaire) → accent."""
    if "tertiaire" in c:
        return f"linear-gradient(90deg,{c['primaire']} 0%,{c['tertiaire']} 48%,{c['accent']} 100%)"
    return f"linear-gradient(90deg,{c['primaire']} 0%,{c['accent']} 100%)"


def arrets_svg(c: dict[str, str]) -> str:
    """Les mêmes arrêts, en `<stop>` SVG."""
    arrets = [("0", c["primaire"])]
    if "tertiaire" in c:
        arrets.append((".5", c["tertiaire"]))
    arrets.append(("1", c["accent"]))
    return "".join(f'<stop offset="{o}" stop-color="{v}"/>' for o, v in arrets)


# Jeton de couleur dans la feuille de style : « %primaire% » rend le hex,
# « %primaire:.15% » rend le rgba correspondant. Les jetons %GRAIN%, %POLICE%,
# %GRAD% et %FONTS_IMPORT% sont en capitales : ce motif ne lit que des noms en
# minuscules.
_JETON = re.compile(r"%([a-z-]+)(?::([0-9.]+))?%")


def teinter(css: str, c: dict[str, str] | None = None) -> str:
    """Remplace les jetons de couleur d'une feuille de style par leurs valeurs."""
    c = c if c is not None else _CTX.get("couleurs") or couleurs()

    def valeur(trouve):
        nom, alpha = trouve.group(1), trouve.group(2)
        hexa = c.get(nom) or c[{"tertiaire": "primaire"}.get(nom, nom)]
        if alpha is None:
            return hexa
        r, v, b = _rgb(hexa)
        return f"rgba({r},{v},{b},{alpha})"
    return _JETON.sub(valeur, css)


# Contexte du carrousel en cours de rendu, posé par document() : dossier de
# sortie (pour rel()), couleurs, police, marque. Le HTML produit ne cite jamais
# de chemin absolu : il reste ouvrable après un clone ailleurs ou un déplacement
# du dossier avec ses assets. Aucune slide ne se rend hors de ce contexte.
_CTX: dict = {}


def chemin_repo(p) -> pathlib.Path:
    """Chemin d'un asset désigné par la spec, relatif à la racine du dépôt."""
    p = pathlib.Path(p)
    return p if p.is_absolute() else ROOT / p


def rel(chemin) -> str:
    """URL d'un asset, relative au dossier de sortie du carrousel.

    Encode ce qui casserait une URL (espaces, parenthèses, lettres accentuées).
    """
    if "out_dir" not in _CTX:
        raise RuntimeError(
            "rel() hors rendu : appeler document(spec, out_dir) ou build(spec), "
            "le chemin d'un asset se calcule depuis le dossier de sortie")
    return quote(os.path.relpath(str(chemin_repo(chemin)), str(_CTX["out_dir"])))


def _marque(cle: str, defaut=None):
    return (_CTX.get("marque") or {}).get(cle, defaut)


# Grain papier : tuile PNG 140px pré-cuite (alpha faible), répétée en background.
# PAS de filtre SVG / blur / mix-blend à l'impression → PDF vectoriel léger
# (les filtres forcent Chromium à aplatir chaque page en bitmap lossless).
_TILE = (pathlib.Path(__file__).parent / ".grain-tile.b64").read_text().strip()
GRAIN = "data:image/png;base64," + _TILE

CSS = """%FONTS_IMPORT%
:root{
  --primaire:%primaire%; --accent:%accent%; --tertiaire:%tertiaire%;
  --sombre:%sombre%; --clair:%clair%;
  --grad:%GRAD%;
  --sp-3xs:8px; --sp-2xs:16px; --sp-xs:24px; --sp-sm:32px; --sp-md:48px;
  --sp-lg:64px; --sp-xl:80px; --sp-2xl:100px;
}
*{margin:0;padding:0;box-sizing:border-box}
@page{size:1080px 1350px;margin:0}
html,body{font-family:%POLICE%,sans-serif;-webkit-font-smoothing:antialiased}
/* Toutes les slides : fond clair grainé. Ambiance colorée CUITE dans le fond
   (peinture directe → pas de couche rasterisée → pas de bande grise au bord,
   contrairement à un halo en élément séparé). Le grain par-dessus dithering
   tout résidu de banding. */
.slide{width:1080px;height:1350px;position:relative;overflow:hidden;
  page-break-after:always;display:flex;flex-direction:column;
  padding:128px 104px 150px;color:var(--sombre);
  background:
    radial-gradient(56% 40% at 84% 7%, %accent:.05%, transparent 72%),
    radial-gradient(62% 46% at 10% 95%, %primaire:.055%, transparent 72%),
    var(--clair)}
.slide:last-child{page-break-after:auto}
.slide::before{content:"";position:absolute;inset:0;z-index:0;
  background-image:url("%GRAIN%");background-repeat:repeat;
  background-size:140px 140px;opacity:.85;pointer-events:none}
.center{justify-content:center}
/* Forme sombre conteneur de titre héros (asset de marque, plein cadre en haut).
   Sans asset dans la spec : un bloc CSS arrondi de la couleur sombre. */
.blob{position:absolute;left:50%;top:-26px;transform:translateX(-50%);
  width:1244px;height:auto;z-index:0}
.blob.css{height:600px;background:var(--sombre);border-radius:0 0 50% 50%/0 0 26% 26%}
.blob.css.xl{height:700px}
.heroblob{position:relative;z-index:1;padding-top:64px;padding-bottom:48px}
.heroblob .title,.heroblob .sub{color:var(--clair)}
.eyebrow{font-size:28px;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:var(--primaire);margin-bottom:var(--sp-sm)}
.heroblob .eyebrow{color:var(--accent)}
.h-xxl{font-size:172px;line-height:.92;letter-spacing:-.025em;font-weight:800}
.h-xl{font-size:116px;line-height:.96;letter-spacing:-.022em;font-weight:800}
.h-l{font-size:92px;line-height:1.0;letter-spacing:-.018em;font-weight:800}
.h-m{font-size:66px;line-height:1.04;letter-spacing:-.012em;font-weight:700}
.lede{font-size:42px;line-height:1.34;font-weight:500;margin-top:var(--sp-lg)}
.heroblob .lede{font-weight:600}
.body-l{font-size:34px;line-height:1.44;font-weight:400}
/* Dégradé de marque en texte — rastérisé en PDF (export-carousel-pdf.py). Blocs only. */
.grad,.hl{background:var(--grad);-webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;color:transparent;
  -webkit-box-decoration-break:clone;box-decoration-break:clone}
.num{font-size:312px;line-height:.9;font-weight:800;letter-spacing:-.03em;
  background:var(--grad);-webkit-background-clip:text;background-clip:text;
  -webkit-text-fill-color:transparent;color:transparent}
.title{display:flex;flex-direction:column}
.title .grad{width:max-content;max-width:100%}
.title .primaire{color:var(--primaire)}
.heroblob .title .primaire{color:%primaire-clair%}
.spacer{flex:1}
.steptitle{text-align:center;font-size:88px;line-height:1.05;font-weight:800;
  letter-spacing:-.018em;align-self:center;max-width:900px}
.stepbody{font-size:43px;line-height:1.36;font-weight:500;text-align:center;
  align-self:center;max-width:944px;margin-top:var(--sp-md);opacity:.85}
/* Médaillon thématique — coin haut alterné G/D, sous la zone de texte centrée */
.illo{position:absolute;width:264px;height:auto;opacity:.95;z-index:0}
.illo.tr{right:76px;top:104px}.illo.tl{left:76px;top:104px}
/* Emblème de marque en filigrane — comble le vide bas (cover sans portrait) */
.coveraccent{position:absolute;right:-70px;bottom:-60px;width:430px;height:auto;
  opacity:.16;z-index:0;pointer-events:none}
.cover-lede{font-size:41px;line-height:1.34;font-weight:500;
  margin-top:104px;max-width:820px;position:relative;z-index:1}
/* Cover portrait : ligne d'identité + visage héros détouré ancré en bas */
.cover-role{font-size:42px;line-height:1.2;font-weight:600;color:var(--primaire);
  margin-top:96px;max-width:820px;position:relative;z-index:1}
.cover-portrait{width:660px;height:auto;align-self:center;margin-bottom:-26px;
  position:relative;z-index:1}
.pcov .heroblob{text-align:center;padding-top:24px}
.pcov .title{align-items:center}
.pcov .cover-role{align-self:center;text-align:center;max-width:none;margin-top:104px}
/* Portrait posé sur le bord bas, tête remontée : à l'abri de la barre du lecteur
   PDF mobile qui mange le bas de la slide */
.pcov .cover-portrait{position:absolute;bottom:0;left:50%;
  transform:translateX(calc(-50% + 24px));width:782px;height:auto;margin:0}
/* Grande scène illustrée — hero d'un point de contenu */
.scene{width:582px;height:auto;align-self:center;
  margin-bottom:var(--sp-md);position:relative;z-index:1}
.scene.big{width:828px}
.scene-pts{width:372px;height:auto;align-self:center;
  margin-top:var(--sp-md);position:relative;z-index:1}
/* Points de progression bas-centre */
.dots{position:absolute;left:0;right:0;bottom:74px;display:flex;
  justify-content:center;align-items:center;gap:18px;z-index:2}
.dots i{width:20px;height:20px;border-radius:50%;display:block}
.dots i.on{width:64px;border-radius:12px;background:var(--primaire)}
.dots i.t{background:var(--tertiaire)}.dots i.a{background:var(--accent)}
.dots i.off{background:%sombre:.22%}
.foot{position:absolute;left:104px;bottom:64px;font-size:22px;font-weight:600;
  letter-spacing:.01em;color:var(--sombre);opacity:.5;z-index:2}
.brand-logo{position:absolute;right:104px;bottom:54px;width:120px;height:auto;z-index:2}
.logo-haut{position:absolute;left:0;right:0;top:64px;display:flex;
  justify-content:center;z-index:3}
.logo-haut img{width:128px;height:auto}
/* Sceau de marque en filigrane (finale) */
.stamp{position:absolute;right:64px;bottom:96px;width:240px;height:auto;
  opacity:.28;z-index:0}
.arrow{font-size:66px;font-weight:800;color:var(--accent);
  position:relative;z-index:1;margin-top:var(--sp-md)}
/* Points à filet */
.pts{display:flex;flex-direction:column;gap:var(--sp-md);margin-top:var(--sp-xl);
  position:relative;z-index:1}
.pt{font-size:46px;line-height:1.22;font-weight:600;padding-left:var(--sp-md);
  border-left:7px solid var(--primaire)}
.pt:nth-child(even){border-color:var(--accent)}
.mlines{display:flex;flex-direction:column;gap:var(--sp-2xs);
  position:relative;z-index:1;align-items:center;text-align:center}
.mlines .h-l{font-size:74px;line-height:1.08}
.mlines .h-l:nth-child(2){color:var(--primaire)}
.mlines .h-l:nth-child(3){color:var(--accent)}
/* Portrait détouré (PNG transparent) — pas de boîte, pas de chevauchement */
.pcover{align-items:center;text-align:center;justify-content:flex-start;
  padding-top:150px}
.pcover .eyebrow{margin-bottom:var(--sp-xs)}
.pcover .name{font-size:100px;font-weight:800;letter-spacing:-.02em;
  position:relative;z-index:1}
.pcover .role{font-size:34px;font-weight:600;color:var(--primaire);
  margin-top:var(--sp-2xs);position:relative;z-index:1}
.pcover .portrait{width:680px;height:auto;margin-top:var(--sp-md);
  align-self:center;position:relative;z-index:1}
/* Photobook : triptyque encadré façon livre photo */
.pbtitle{font-size:80px;font-weight:800;letter-spacing:-.018em;
  text-align:center;align-self:center;position:relative;z-index:1}
.pbrow{display:flex;gap:40px;justify-content:center;align-items:flex-start;
  margin-top:var(--sp-2xl);position:relative;z-index:1}
/* Pas de box-shadow : Chromium la rend en rectangle gris à l'export PDF.
   Filet fin à la place pour détacher la carte du fond. */
.pbcard{background:%blanc%;padding:22px 22px 0;border-radius:14px;
  border:1px solid %sombre:.12%;display:flex;flex-direction:column;
  align-items:center}
.pbcard:nth-child(1){transform:rotate(-3deg)}
.pbcard:nth-child(3){transform:rotate(3deg)}
.pbcard img{width:260px;height:340px;object-fit:cover;border-radius:6px;display:block}
.pbcard .cap{font-size:28px;font-weight:600;padding:22px 0;letter-spacing:.01em}
/* Bloc sous la forme de titre (finales) */
.belowblob{margin-top:176px;position:relative;z-index:1}
.stats{display:flex;flex-direction:column;gap:var(--sp-md)}
.stat-row{display:grid;grid-template-columns:210px 1fr;align-items:baseline;
  gap:var(--sp-sm);padding-bottom:var(--sp-sm);
  border-bottom:2px solid %sombre:.10%}
.stat-row:last-child{border-bottom:0}
.stat-row b{font-size:72px;font-weight:800;letter-spacing:-.02em;
  width:max-content;color:var(--primaire)}
.stat-row span{font-size:33px;font-weight:500;opacity:.82}
.welcome-char{position:absolute;right:36px;bottom:-20px;width:548px;height:auto;
  z-index:1}
/* Bouton CTA en SVG vecteur (dégradé net en PDF, cf. _cta_pill) */
.cta-pill-svg{display:block;margin-top:var(--sp-lg);position:relative;z-index:1}
/* Cover compacte : titre entièrement DANS la forme (dégradé sur sombre, lisible) */
.heroblob.tight{padding-top:0;padding-bottom:44px}
.heroblob.tight .eyebrow{margin-bottom:var(--sp-2xs)}
.h-cover{font-size:96px;line-height:1.06;letter-spacing:-.02em;font-weight:800}
/* Forme agrandie : son bord bas descend nettement sous le titre (jambages dégagés) */
.blob.xl{width:1340px;top:-16px}
.cover-lede.low{margin-top:248px}
/* Illustration de remplissage en bas de cover (comble le vide) */
.cover-art{align-self:center;height:500px;width:auto;margin-bottom:-30px;
  position:relative;z-index:1}
.heroblob.ctr{text-align:center}
.heroblob.ctr .title{align-items:center}
.h-slogan{font-size:60px;line-height:1.08;letter-spacing:-.01em;font-weight:800}
/* CTA : texte + bouton alignés à gauche, descendus */
.cta-col{position:absolute;left:76px;top:715px;width:520px;text-align:left;z-index:2}
.cta-data{font-size:35px;line-height:1.36;font-weight:600;color:var(--sombre)}
.cta-art{position:absolute;right:-18px;bottom:0;height:770px;width:auto;z-index:1}
/* ===== Famille THÈSE — grille cassée, aligné à gauche, SANS forme de titre ===== */
.t-slide{padding:118px 104px 150px;align-items:flex-start;text-align:left;justify-content:center}
.t-eyebrow{font-size:28px;font-weight:700;letter-spacing:.2em;text-transform:uppercase;
  color:var(--primaire);position:relative;z-index:1}
.t-rule{height:12px;width:260px;background:var(--grad);border-radius:7px;
  margin:var(--sp-md) 0 var(--sp-lg);position:relative;z-index:1}
.t-title{font-size:132px;line-height:.95;letter-spacing:-.024em;font-weight:800;
  text-align:left;display:flex;flex-direction:column;position:relative;z-index:1}
.t-title .grad{width:max-content;max-width:100%}
.t-title .primaire{color:var(--primaire)}
.t-h2{font-size:96px;line-height:1.0;letter-spacing:-.02em;font-weight:800;
  text-align:left;display:flex;flex-direction:column;position:relative;z-index:1}
.t-h2 .grad{width:max-content;max-width:100%}.t-h2 .primaire{color:var(--primaire)}
.t-lede{font-size:43px;line-height:1.34;font-weight:500;max-width:860px;
  margin-top:var(--sp-lg);position:relative;z-index:1}
/* numéro éditorial géant en filigrane (coin haut-droit) */
.t-folio{position:absolute;right:96px;top:92px;font-size:300px;line-height:.8;
  font-weight:800;color:%sombre:.06%;z-index:0;letter-spacing:-.04em}
/* SPLIT data : numéro géant à gauche (rastérisé via .num), texte à droite + filet */
.t-split{display:grid;grid-template-columns:430px 1fr;align-items:center;
  gap:var(--sp-md);padding:118px 90px 150px}
.t-split .num{font-size:156px;line-height:.84;text-align:left;align-self:center}
.t-right{border-left:6px solid var(--sombre);padding-left:var(--sp-md);
  position:relative;z-index:1}
.t-right .t-eyebrow{margin-bottom:var(--sp-sm);display:block;letter-spacing:.12em}
.t-cap{font-size:37px;line-height:1.3;font-weight:600}
.t-points{display:flex;flex-direction:column;gap:var(--sp-md);margin-top:var(--sp-lg);
  max-width:760px;position:relative;z-index:1}
.t-pt{font-size:46px;line-height:1.22;font-weight:600;padding-left:var(--sp-md);
  border-left:7px solid var(--primaire)}
.t-pt:nth-child(even){border-color:var(--accent)}
.t-scene-br{position:absolute;right:60px;bottom:120px;width:430px;height:auto;z-index:0;opacity:.96}
.t-mlines{display:flex;flex-direction:column;gap:8px;position:relative;z-index:1}
.t-mlines div{font-size:82px;line-height:1.04;font-weight:800;letter-spacing:-.02em}
.t-mlines div:nth-child(2){color:var(--primaire)}.t-mlines div:nth-child(3){color:var(--accent)}
.t-cta-rows{display:flex;flex-direction:column;gap:var(--sp-2xs);margin-top:var(--sp-lg);
  position:relative;z-index:1}
.t-cta-rows .body-l{font-size:40px;opacity:.9}
/* Slide PAUSE — fond sombre (rythme) : gros chiffre en dégradé qui éclate sur le
   sombre, ponctue la séquence claire. */
.t-dark{background:var(--sombre);color:var(--clair)}
.t-dark .t-eyebrow{color:var(--accent)}
.t-dark .t-cap,.t-dark .t-lede{color:var(--clair)}
.t-dark .t-right{border-left-color:%clair:.55%}
.t-dark .foot{color:%clair:.6%}
.t-dark .dots i.off{background:%clair:.32%}
.t-dark .t-mlines div{color:var(--clair)}
.t-dark .t-mlines div:nth-child(2){color:var(--primaire)}
.t-dark .t-mlines div:nth-child(3){color:var(--accent)}
/* ===== WINDOW — photo réelle cadrée comme une fenêtre de marque =====
   Liseré en DÉGRADÉ (fond plein → rendu OK en PDF, contrairement au dégradé
   texte) > passe-partout sombre > photo arrondie. Itinéraire pointillé optionnel
   qui relie les slides (envie de swiper). Fenêtre alternée gauche/droite. */
.win-slide{padding:0}
.win-eyebrow{position:absolute;left:104px;top:62px;z-index:5;display:flex;
  align-items:center;gap:15px;font-size:28px;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:var(--primaire)}
/* Icône d'eyebrow (ex. logo d'un canal tiers, jamais recoloré) */
.icone{height:34px;width:auto;display:block;flex:none}
.eyebrow.icone-eb{display:flex;align-items:center;gap:16px}
.eyebrow.icone-eb .icone{height:38px}
/* Fenêtre = SVG inline (cadre dégradé + passe-partout + photo + étiquette).
   La rotation est appliquée EN VECTEUR à l'intérieur du SVG (g transform),
   donc le cadre fin reste net en biais à l'export PDF (un élément DOM tourné
   en CSS est rasterisé en escalier par Chromium). */
.winsvg{position:absolute;z-index:2;overflow:visible}
.route{position:absolute;inset:0;width:1080px;height:1350px;z-index:1;pointer-events:none}
/* Mini-fenêtre photo sur la cover */
.cover-window{position:absolute;right:74px;bottom:172px;width:286px;height:360px;
  object-fit:cover;border-radius:24px;border:10px solid var(--sombre);
  outline:7px solid var(--accent);transform:rotate(5deg);z-index:1}
/* Objet illustré sur la cover (illustration détourée) */
.cover-objet{position:absolute;right:64px;bottom:150px;width:412px;height:auto;
  z-index:1;transform:rotate(-3deg)}
.cover-icone{position:absolute;left:104px;bottom:336px;display:flex;align-items:center;
  gap:16px;font-size:28px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;
  color:var(--primaire);z-index:3}
.cover-icone .icone{height:38px}
"""


def esc(t) -> str:
    # Tiret insécable (U+2011) : un mot composé ne doit JAMAIS se couper au
    # retour à la ligne. Visuellement identique à "-".
    return _html.escape(str(t), quote=False).replace("-", "‑")


def _lede_html(lede) -> str:
    """Sous-titre. `str` = bloc unique (wrap aux espaces). `list` = retours à la
    ligne EXPLICITES (on contrôle où ça coupe, jamais en plein milieu d'un mot)."""
    if isinstance(lede, (list, tuple)):
        return "<br>".join(esc(x) for x in lede)
    return esc(lede)


MARQUEURS_TITRE = {"g", "primaire", "html"}


def T(items, cls) -> str:
    """Titre multi-lignes. Chaque item : str (ligne pleine), ["g", txt] ligne en
    dégradé (BLOC autonome → rastérisation sans casser la mise en page),
    ["primaire", txt] ligne en couleur primaire, ["html", "..."] ligne HTML brute.
    Jamais de dégradé inline au milieu d'une phrase."""
    if isinstance(items, str):
        items = [items]
    out = []
    for it in items:
        if isinstance(it, (list, tuple)) and len(it) == 2 and it[0] in MARQUEURS_TITRE:
            marqueur, texte = it
            if marqueur == "g":
                out.append(f'<div class="{cls} grad">{esc(texte)}</div>')
            elif marqueur == "primaire":
                out.append(f'<div class="{cls} primaire">{esc(texte)}</div>')
            else:
                out.append(f'<div class="{cls}">{texte}</div>')
        else:
            out.append(f'<div class="{cls}">{esc(it)}</div>')
    return "".join(out)


def _img(chemin, cls: str, alt: str = "", style: str = "") -> str:
    style = f' style="{style}"' if style else ""
    return f'<img class="{cls}" src="{rel(chemin)}" alt="{_html.escape(alt)}"{style}>'


def blob(xl: bool = False) -> str:
    """Forme sombre conteneur de titre héros : l'asset de la spec, sinon un bloc CSS."""
    cls = "blob xl" if xl else "blob"
    forme = _marque("forme_titre")
    if forme:
        return _img(forme, cls)
    return f'<div class="{cls} css"></div>'


def _logo_haut() -> str:
    logo = _marque("logo")
    return f'<div class="logo-haut">{_img(logo, "", "")}</div>' if logo else ""


def _illo(s) -> str:
    """Médaillon thématique en coin haut, alterné G/D le long du parcours.
    `s["illo"]` = numéro du médaillon (1…n dans `marque.medaillons`) choisi pour
    le SENS de la slide ; sinon cycle. `s["side"]` ('l'/'r') force le coin.
    Pas de médaillon si illo=0 ou si la marque n'en déclare pas."""
    medaillons = _marque("medaillons") or []
    n = s.get("illo")
    if n == 0 or not medaillons:
        return ""
    pos = s.get("_pos", 0)
    idx = (n - 1) if n else pos
    side = s.get("side")
    if side:
        corner = "tr" if side == "r" else "tl"
    else:
        corner = "tr" if pos % 2 == 0 else "tl"
    return _img(medaillons[idx % len(medaillons)], f"illo {corner}")


def _dots(pos, total) -> str:
    """Points de progression bas-centre : pilule primaire active + tertiaire/accent."""
    out = []
    for k in range(total):
        if k == pos:
            out.append('<i class="on"></i>')
        else:
            out.append(f'<i class="{("t", "a")[k % 2]}"></i>')
    return f'<div class="dots">{"".join(out)}</div>'


def _foot(logo: bool = True) -> str:
    pied = _marque("pied")
    texte = f'<span class="foot">{esc(pied)}</span>' if pied else ""
    image = _img(_marque("logo"), "brand-logo") if (logo and _marque("logo")) else ""
    return texte + image


def _icone(s) -> str:
    return _img(s["icone"], "icone") if s.get("icone") else ""


def _cta_pill(kicker) -> str:
    """Bouton CTA pilule en SVG VECTEUR (dégradé de marque + texte vecteur).
    Rendu PDF net (un div à fond dégradé se rasterise → bords crénelés).
    Largeur estimée d'après le texte."""
    c = _CTX["couleurs"]
    k = esc(kicker)
    pad, gap, arr = 46, 20, 34
    tw = len(kicker) * 21
    PW, PH = int(pad + tw + gap + arr + pad), 86
    by = PH / 2 + 13
    famille = _html.escape(_CTX["police"])
    return (f'<svg class="cta-pill-svg" width="{PW}" height="{PH}" '
            f'viewBox="0 0 {PW} {PH}" fill="none"><defs>'
            f'<linearGradient id="ctapill" x1="0" y1="0" x2="{PW}" y2="0" '
            f'gradientUnits="userSpaceOnUse">{arrets_svg(c)}</linearGradient></defs>'
            f'<rect x="0" y="0" width="{PW}" height="{PH}" rx="{PH / 2}" fill="url(#ctapill)"/>'
            f'<text x="{pad}" y="{by:.0f}" font-family="{famille}" font-size="38" '
            f'font-weight="800" fill="{c["sombre"]}">{k}</text>'
            f'<text x="{PW - pad}" y="{by:.0f}" font-family="{famille}" font-size="38" '
            f'font-weight="800" fill="{c["sombre"]}" text-anchor="end">&#8594;</text></svg>')


def _route(i, route, start=False) -> str:
    """Itinéraire pointillé en dégradé, trait vectoriel (rendu PDF propre). Relie
    `route[0]` (hauteur d'entrée à gauche) à `route[1]` (sortie à droite) en un
    swoop. Pour un fil continu d'une slide à l'autre, la sortie d'une slide vaut
    l'entrée de la suivante. `start` : la ligne émerge du niveau de la carte au
    lieu de déborder du bord gauche."""
    if not route:
        return ""
    pid = f"rg{i}"
    grad = (f'<linearGradient id="{pid}" x1="0" y1="0" x2="1080" y2="1350" '
            f'gradientUnits="userSpaceOnUse">{arrets_svg(_CTX["couleurs"])}</linearGradient>')
    y0, y1 = route
    x0 = 120 if start else -40
    d = f"M {x0} {y0} C 380 {y0} 760 {y1} 1130 {y1}"
    return (f'<svg class="route" viewBox="0 0 1080 1350" fill="none">'
            f'<defs>{grad}</defs>'
            f'<path d="{d}" stroke="url(#{pid})" stroke-width="6" '
            f'stroke-dasharray="2 20" stroke-linecap="round" opacity=".9"/></svg>')


def window(s, i):
    """Slide « fenêtre » : photo réelle cadrée comme une fenêtre de marque.
    SVG inline avec rotation VECTEUR interne (`g transform=rotate`) : cadre en
    dégradé + passe-partout sombre + photo (`<image>` embarqué) + étiquette
    lieu/coordonnées, le tout net en biais à l'export PDF.
    Paramètres : img, place, coords, side l/r/c, land (photo paysage),
    etiquette (eyebrow), icone, route [y_entree, y_sortie], route_start."""
    c = _CTX["couleurs"]
    side = s.get("side", "l")
    land = s.get("land")
    IMG_W, IMG_H = (872, 620) if land else (648, 810)
    W, H = IMG_W + 50, IMG_H + 50              # +9 cadre +16 passe-partout, ×2
    MX, MT, MB = 80, 70, 170                   # marges canvas (rotation + étiquette)
    CW, CH = W + 2 * MX, MT + H + MB
    bx, by = MX, MT
    cx, cy = bx + W / 2, by + H / 2
    ix, iy = bx + 25, by + 25
    angle = {"l": -2, "r": 2, "c": -1.5}.get(side, -2)
    if side == "c":
        pos = f"left:{540 - (MX + W / 2):.0f}px;top:{344 - MT}px"
    elif side == "r":
        pos = f"right:{96 - MX}px;top:{268 - MT}px"
    else:
        pos = f"left:{96 - MX}px;top:{268 - MT}px"
    place, coords = s.get("place", ""), s.get("coords", "")
    pw = len(place) * 23.5
    block = 20 + 14 + pw                       # repère + écart + lieu
    tw = max(block, len(coords) * 15.8) + 60
    th = 104
    tag_top = by + H - 26 - th
    y1 = tag_top + 52                          # ligne de base du lieu
    y2 = y1 + 34                               # ligne de base des coordonnées
    blk_x = cx - block / 2
    gid, cid = f"wf{i}", f"wc{i}"
    famille = _html.escape(_CTX["police"])
    grad = (f'<linearGradient id="{gid}" x1="{bx}" y1="{by}" x2="{bx + W}" y2="{by + H}" '
            f'gradientUnits="userSpaceOnUse">{arrets_svg(c)}</linearGradient>')
    clip = (f'<clipPath id="{cid}"><rect x="{ix}" y="{iy}" width="{IMG_W}" '
            f'height="{IMG_H}" rx="26"/></clipPath>')
    tag = ""
    if place or coords:
        tag = (f'<rect x="{cx - tw / 2:.1f}" y="{tag_top}" width="{tw:.1f}" height="{th}" '
               f'rx="22" fill="{c["clair"]}" stroke="{c["sombre"]}" stroke-opacity=".16"/>'
               f'<circle cx="{blk_x + 10:.1f}" cy="{y1 - 12}" r="10" fill="{c["accent"]}"/>'
               f'<text x="{blk_x + 34:.1f}" y="{y1}" font-family="{famille}" font-size="42" '
               f'font-weight="800" fill="{c["sombre"]}">{esc(place)}</text>'
               f'<text x="{cx:.1f}" y="{y2}" font-family="{famille}" font-size="28" '
               f'font-weight="600" fill="{c["sombre"]}" fill-opacity=".55" letter-spacing="3" '
               f'text-anchor="middle">{esc(coords)}</text>')
    svg = (f'<svg class="winsvg" style="{pos}" width="{CW}" height="{CH}" '
           f'viewBox="0 0 {CW} {CH}" fill="none">'
           f'<defs>{grad}{clip}</defs>'
           f'<g transform="rotate({angle} {cx} {cy})">'
           f'<rect x="{bx}" y="{by}" width="{W}" height="{H}" rx="46" fill="url(#{gid})"/>'
           f'<rect x="{bx + 9}" y="{by + 9}" width="{W - 18}" height="{H - 18}" rx="38" '
           f'fill="{c["sombre"]}"/>'
           f'<image href="{rel(s["img"])}" x="{ix}" y="{iy}" width="{IMG_W}" '
           f'height="{IMG_H}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>'
           # Trait sombre VECTEUR posé sur le bord de la photo : masque le
           # crénelage du bord raster de l'<image> tournée → bord intérieur net.
           f'<rect x="{ix}" y="{iy}" width="{IMG_W}" height="{IMG_H}" rx="26" '
           f'fill="none" stroke="{c["sombre"]}" stroke-width="8"/>'
           f'{tag}</g></svg>')
    etiquette = ""
    if s.get("etiquette") or s.get("icone"):
        etiquette = (f'<div class="win-eyebrow">{_icone(s)}'
                     f'<span>{esc(s.get("etiquette", ""))}</span></div>')
    return f'''<section class="slide win-slide">
{_route(i, s.get("route"), start=s.get("route_start", False))}
{etiquette}
{svg}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def cover(s, i):
    """Cover de la famille portrait / photo : titre dans la forme sombre.
    Paramètres : eyebrow, icone, title, title_cls (h-xxl/h-xl/h-l/h-cover),
    tight, forme_xl, forme_pt, lede, lede_mt, art, portrait + role (variante
    portrait), objet (illustration bas-droite), teaser (mini-fenêtre photo),
    icone_bas (eyebrow posé en bas à gauche, à côté de l'objet)."""
    icone_bas = s.get("icone_bas")
    if s.get("eyebrow") and s.get("icone") and not icone_bas:
        eb = f'<div class="eyebrow icone-eb">{_icone(s)}<span>{esc(s["eyebrow"])}</span></div>'
    elif s.get("eyebrow") and not icone_bas:
        eb = f'<div class="eyebrow">{esc(s["eyebrow"])}</div>'
    else:
        eb = ""
    cls = "slide"
    if s.get("portrait"):
        cls = "slide pcov"
        role = f'<div class="cover-role">{esc(s["role"])}</div>' if s.get("role") else ""
        anchor = _img(s["portrait"], "cover-portrait")
        foot = _foot(logo=False)
        body = role + anchor
    else:
        lede_cls = "cover-lede low" if s.get("tight") else "cover-lede"
        lede_style = f' style="margin-top:{s["lede_mt"]}px"' if s.get("lede_mt") else ""
        lede = (f'<div class="{lede_cls}"{lede_style}>{_lede_html(s["lede"])}</div>'
                if s.get("lede") else "")
        if s.get("teaser") or s.get("objet"):
            fill = ""
        elif s.get("art"):
            fill = _img(s["art"], "cover-art")
        elif _marque("embleme"):
            fill = _img(_marque("embleme"), "coveraccent")
        else:
            fill = ""
        anchor = f'<div class="spacer"></div>{fill}'
        foot = _foot()
        body = lede + anchor
    hb = "heroblob tight" if s.get("tight") else "heroblob"
    tcls = s.get("title_cls", "h-xl")
    hero = blob(xl=bool(s.get("forme_xl")))
    extra = ""
    if s.get("objet"):
        extra += _img(s["objet"], "cover-objet")
    elif s.get("teaser"):
        extra += _img(s["teaser"], "cover-window")
    if icone_bas and s.get("eyebrow"):
        extra += f'<div class="cover-icone">{_icone(s)}<span>{esc(s["eyebrow"])}</span></div>'
    hb_style = f' style="padding-top:{s["forme_pt"]}px"' if s.get("forme_pt") else ""
    return f'''<section class="{cls}">
{_logo_haut()}{hero}
<div class="{hb}"{hb_style}>{eb}<div class="title">{T(s["title"], tcls)}</div></div>
{body}{foot}{extra}{_grid()}</section>'''


def stat(s, i):
    """Chiffre héros centré. Paramètres : eyebrow, number, caption, num_size, illo, side."""
    # Chiffre centré via text-align (bloc pleine largeur) : robuste à la
    # rastérisation — l'img de remplacement perd `align-self`, pas le text-align.
    num_style = "text-align:center;white-space:nowrap"
    if s.get("num_size"):
        num_style += f";font-size:{s['num_size']}"
    return f'''<section class="slide center">
{_illo(s)}
<div class="eyebrow" style="text-align:center;align-self:center">{esc(s.get("eyebrow", ""))}</div>
<div class="num" style="{num_style}">{esc(s["number"])}</div>
<div class="stepbody" style="margin-top:var(--sp-md)">{_lede_html(s["caption"])}</div>
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def statement(s, i):
    """Affirmation centrée. Paramètres : title, lede, scene, scene_big, illo, side, route."""
    body = f'<div class="stepbody">{_lede_html(s["lede"])}</div>' if s.get("lede") else ""
    if s.get("scene"):
        art = _img(s["scene"], "scene big" if s.get("scene_big") else "scene")
    else:
        art = _illo(s)
    return f'''<section class="slide center">
{_route(i, s.get("route"))}{art}
<div class="steptitle">{T(s["title"], "title")}</div>{body}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def points(s, i):
    """Liste à filets. Paramètres : eyebrow, title, points, scene."""
    items = "".join(f'<div class="pt">{esc(p)}</div>' for p in s["points"])
    scene = _img(s["scene"], "scene-pts") if s.get("scene") else ""
    titre = T(s["title"], "") if isinstance(s["title"], list) else esc(s["title"])
    return f'''<section class="slide">
<div class="eyebrow">{esc(s.get("eyebrow", ""))}</div>
<div class="h-l">{titre}</div>
<div class="pts">{items}</div>{scene}<div class="spacer"></div>
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def manifesto(s, i):
    """Manifeste centré en lignes empilées. Paramètres : lines, lede, illo, side."""
    lines = "".join(f'<div class="h-l">{esc(l)}</div>' for l in s["lines"])
    sub = f'<div class="stepbody">{_lede_html(s["lede"])}</div>' if s.get("lede") else ""
    return f'''<section class="slide center">
{_illo(s)}
<div class="mlines">{lines}</div>{sub}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def cta(s, i):
    """Finale CTA : forme + titre, message, URL en bouton pilule, sceau en
    filigrane ou illustration latérale. Pas de pied (la pilule porte l'URL).
    Paramètres : title, title_cls, center_title, rows, kicker, art."""
    rows = "".join(f'<div class="cta-data">{esc(r)}</div>' for r in s.get("rows", []))
    pill = _cta_pill(s["kicker"]) if s.get("kicker") else ""
    art = _img(s["art"], "cta-art") if s.get("art") else ""
    sceau = _marque("sceau")
    stamp = ("" if (s.get("art") or not sceau) else
             _img(sceau, "stamp",
                  style="left:auto;right:56px;top:560px;bottom:auto;width:264px;opacity:.55"))
    tcls = s.get("title_cls", "h-l")
    hbcls = "heroblob ctr" if s.get("center_title") else "heroblob"
    return f'''<section class="slide">
{_logo_haut()}{blob()}
<div class="{hbcls}"><div class="title">{T(s["title"], tcls)}</div></div>
{stamp}{art}
<div class="spacer"></div>
<div class="cta-col">{rows}{pill}</div></section>'''


def portrait_cover(s, i):
    """Cover portrait centrée. Paramètres : eyebrow, name, role, img."""
    return f'''<section class="slide pcover">
<div class="eyebrow" style="text-align:center">{esc(s.get("eyebrow", ""))}</div>
<div class="name">{esc(s["name"])}</div>
<div class="role">{esc(s["role"])}</div>
{_img(s["img"], "portrait")}
{_foot()}</section>'''


def photobook(s, i):
    """Triptyque photo façon livre. Paramètres : title, lede, photos [[chemin, légende] × 3]."""
    cards = "".join(
        f'<div class="pbcard">{_img(img, "")}<div class="cap">{esc(cap)}</div></div>'
        for img, cap in s["photos"])
    sub = (f'<div class="stepbody" style="margin-top:var(--sp-sm);max-width:920px">'
           f'{_lede_html(s["lede"])}</div>') if s.get("lede") else ""
    rowmt = "var(--sp-lg)" if sub else "var(--sp-2xl)"
    return f'''<section class="slide center">
<div class="pbtitle">{T(s["title"], "title")}</div>{sub}
<div class="pbrow" style="margin-top:{rowmt}">{cards}</div>
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def finale_stats(s, i):
    """Finale chiffrée : forme + titre, lignes chiffre/libellé, message, personnage.
    Paramètres : title, stats [[chiffre, libellé], ...], lede, img."""
    rows = "".join(
        f'<div class="stat-row"><b>{esc(b)}</b><span>{esc(t)}</span></div>'
        for b, t in s["stats"])
    char = _img(s["img"], "welcome-char") if s.get("img") else ""
    sceau = _marque("sceau")
    stamp = _img(sceau, "stamp") if sceau else ""
    return f'''<section class="slide">
{_logo_haut()}{blob()}
<div class="heroblob"><div class="title">{T(s["title"], "h-xl")}</div></div>
{stamp}
<div class="belowblob">
<div class="stats">{rows}</div>
<div class="lede" style="max-width:640px;margin-top:var(--sp-lg)">{esc(s.get("lede", ""))}</div>
</div>{char}{_foot(logo=False)}</section>'''


def finale_portrait(s, i):
    """Finale chaleureuse d'un carrousel portrait : forme + titre, message de
    clôture, ligne d'accueil, URL en bouton CTA, visage détouré bas-droite.
    Paramètres : title, lede, welcome, cta, img."""
    welcome = (f'<div class="body-l" style="margin-top:var(--sp-md);opacity:.9">'
               f'{esc(s["welcome"])}</div>' if s.get("welcome") else "")
    pill = _cta_pill(s["cta"]) if s.get("cta") else ""
    char = _img(s["img"], "welcome-char") if s.get("img") else ""
    sceau = _marque("sceau")
    stamp = (_img(sceau, "stamp",
                  style="left:auto;right:50px;top:560px;bottom:auto;width:280px;opacity:.6")
             if sceau else "")
    return f'''<section class="slide">
{blob()}
<div class="heroblob"><div class="title">{T(s["title"], "h-xl")}</div></div>
{stamp}
<div class="belowblob" style="max-width:600px">
<div class="lede">{_lede_html(s["lede"])}</div>
{welcome}{pill}
</div>{char}</section>'''


# ===== Famille THÈSE — grille cassée, alignée à gauche, sans forme de titre =====
def _t_art(s):
    """Illustration en coin bas-droite (asymétrie éditoriale). `art` = chemin,
    `art_w` = largeur px. Issue d'une passe catalogue (assets/index.md) après brief."""
    if not s.get("art"):
        return ""
    return _img(s["art"], "t-scene-br", style=f"width:{s.get('art_w', 380)}px")


def t_cover(s, i):
    """Paramètres : eyebrow, folio (filigrane), title, lede."""
    eb = f'<div class="t-eyebrow">{esc(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    folio = f'<div class="t-folio">{esc(s["folio"])}</div>' if s.get("folio") else ""
    lede = f'<div class="t-lede">{_lede_html(s["lede"])}</div>' if s.get("lede") else ""
    return f'''<section class="slide t-slide">{folio}
{_logo_haut()}
{eb}<div class="t-rule"></div><div class="t-title">{T(s["title"], "")}</div>{lede}
{_foot(logo=False)}</section>'''


def t_statement(s, i):
    """Paramètres : eyebrow, title, lede, art, art_w."""
    eb = f'<div class="t-eyebrow">{esc(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    lede = f'<div class="t-lede">{_lede_html(s["lede"])}</div>' if s.get("lede") else ""
    return f'''<section class="slide t-slide">{eb}
<div class="t-h2">{T(s["title"], "")}</div>{lede}{_t_art(s)}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def t_stat(s, i):
    """Slide « pause » : fond sombre par défaut (rythme), `clair: true` pour la
    garder claire. Paramètres : number, eyebrow, caption, clair."""
    cls = "slide t-split" if s.get("clair") else "slide t-split t-dark"
    return f'''<section class="{cls}">
<div class="num">{esc(s["number"])}</div>
<div class="t-right"><div class="t-eyebrow">{esc(s.get("eyebrow", ""))}</div>
<div class="t-cap">{_lede_html(s["caption"])}</div></div>
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def t_points(s, i):
    """Paramètres : eyebrow, title, points, scene."""
    eb = f'<div class="t-eyebrow">{esc(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    pts = "".join(f'<div class="t-pt">{esc(p)}</div>' for p in s["points"])
    scene = _img(s["scene"], "t-scene-br") if s.get("scene") else ""
    return f'''<section class="slide t-slide">{eb}
<div class="t-h2">{T(s["title"], "")}</div>
<div class="t-points">{pts}</div>{scene}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def t_manifesto(s, i):
    """Paramètres : lines, lede, dark, art, art_w."""
    lines = "".join(f'<div>{esc(l)}</div>' for l in s["lines"])
    lede = f'<div class="t-lede">{_lede_html(s["lede"])}</div>' if s.get("lede") else ""
    cls = "slide t-slide t-dark" if s.get("dark") else "slide t-slide"
    return f'''<section class="{cls}">
<div class="t-rule"></div><div class="t-mlines">{lines}</div>{lede}{_t_art(s)}
{_dots(s["_pos"], s["_tot"])}{_foot()}</section>'''


def t_cta(s, i):
    """Paramètres : eyebrow, title, rows, kicker, art, art_w."""
    eb = f'<div class="t-eyebrow">{esc(s["eyebrow"])}</div>' if s.get("eyebrow") else ""
    rows = "".join(f'<div class="body-l">{esc(r)}</div>' for r in s.get("rows", []))
    pill = _cta_pill(s["kicker"]) if s.get("kicker") else ""
    return f'''<section class="slide t-slide">{eb}
<div class="t-h2">{T(s["title"], "")}</div>
<div class="t-cta-rows">{rows}</div>{pill}{_t_art(s)}
{_foot(logo=False)}</section>'''


RENDER = {"cover": cover, "stat": stat, "statement": statement, "points": points,
          "manifesto": manifesto, "cta": cta,
          "portrait_cover": portrait_cover, "photobook": photobook,
          "finale_stats": finale_stats, "finale_portrait": finale_portrait,
          "t_cover": t_cover, "t_statement": t_statement, "t_stat": t_stat,
          "t_points": t_points, "t_manifesto": t_manifesto, "t_cta": t_cta,
          "window": window}

# Slides qui portent les points de progression (le contenu, pas les seuils).
CONTENT_TYPES = {"statement", "stat", "points", "manifesto", "photobook",
                 "window",
                 "t_statement", "t_stat", "t_points", "t_manifesto"}


def document(spec, out_dir) -> str:
    """HTML complet d'un carrousel, sans rien écrire sur le disque.

    Tous les assets sont référencés en chemin relatif à `out_dir` : le HTML
    produit ne contient aucun `file://` ni aucun chemin absolu.
    """
    tokens = _lire_tokens()
    sls = spec["slides"]
    inconnus = sorted({sl.get("type", "?") for sl in sls} - set(RENDER))
    if inconnus:
        raise ErreurSpec(f"type(s) de slide inconnu(s) dans « {spec.get('slug')} » : "
                         f"{', '.join(inconnus)} (connus : {', '.join(sorted(RENDER))})")
    content = [k for k, sl in enumerate(sls) if sl["type"] in CONTENT_TYPES]
    tot = len(content)
    for pos, k in enumerate(content):
        sls[k]["_pos"], sls[k]["_tot"] = pos, tot
    c = couleurs(spec, tokens)
    _CTX.clear()
    _CTX.update(out_dir=pathlib.Path(out_dir), couleurs=c, police=police(tokens),
                marque=spec.get("marque") or {})
    try:
        slides = "".join(RENDER[sl["type"]](sl, i) for i, sl in enumerate(sls))
        famille = _CTX["police"].replace("'", "\\'")
        fonts_import = f"@import url('{rel(FONTS_CSS)}');" if FONTS_CSS.exists() else ""
        css = teinter(CSS.replace("%GRAIN%", GRAIN)
                         .replace("%POLICE%", f"'{famille}'")
                         .replace("%GRAD%", degrade_css(c))
                         .replace("%FONTS_IMPORT%", fonts_import), c)
    finally:
        _CTX.clear()
    lang = _html.escape(str(spec.get("lang", "fr")))
    return f'''<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8">
<style>{css}</style></head><body>{slides}</body></html>'''


# ----------------------------- SPECS -----------------------------

def charger_spec(chemin: pathlib.Path) -> dict:
    """Lit une spec de carrousel et vérifie ses clés obligatoires."""
    try:
        spec = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise ErreurSpec(f"spec illisible : {chemin} ({err})") from err
    manquantes = [cle for cle in ("slug", "date", "slides") if not spec.get(cle)]
    if manquantes:
        raise ErreurSpec(f"spec {chemin} : clé(s) obligatoire(s) absente(s) : {', '.join(manquantes)}")
    spec["_fichier"] = str(chemin)
    return spec


def charger_specs() -> list[dict]:
    """Toutes les specs `outputs/carrousel-*/carrousel.json`, triées par dossier."""
    return [charger_spec(p) for p in sorted(SORTIES.glob(f"carrousel-*/{NOM_SPEC}"))]


def dossier_de(spec) -> pathlib.Path:
    """Dossier de sortie d'un carrousel, sans rien écrire : celui de sa spec."""
    if spec.get("_fichier"):
        return pathlib.Path(spec["_fichier"]).parent
    return SORTIES / f'carrousel-{spec["slug"]}-{spec["date"]}'


def build(spec, pdf: bool = True):
    out_dir = dossier_de(spec)
    doc = document(spec, out_dir)
    if not FONTS_CSS.exists():
        sys.stderr.write(
            f"⚠ {FONTS_CSS.relative_to(ROOT)} absent : la police de marque n'est pas "
            f"embarquée, Chrome headless rendra une police de repli. "
            f"Voir 06-graphic-design/lib/README.md.\n")
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "index.html"
    html_path.write_text(doc, encoding="utf-8")
    if not pdf:
        return html_path
    pdf_path = out_dir / "exports" / f'{spec["slug"]}.pdf'
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(SCRIPTS / "export-carousel-pdf.py"),
                    str(html_path), str(pdf_path)], check=True)
    return pdf_path


# ----------------------------- LIGNE DE COMMANDE -----------------------------
# Le script écrit des fichiers dans le dépôt : il ne construit que ce qu'on lui
# nomme. Un argument non reconnu ne doit jamais dégénérer en « tout reconstruire ».

def construire(specs, dry_run: bool = False, pdf: bool = True) -> int:
    for spec in specs:
        if dry_run:
            print(f"  [dry-run] {spec['slug']} → {dossier_de(spec)}")
            continue
        print(f"  carrousel → {build(spec, pdf=pdf)}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="build-carousel.py",
        description="Construit un ou plusieurs carrousels LinkedIn (HTML puis PDF) depuis "
                    f"leur spec {NOM_SPEC}.",
        epilog=f"Les specs vivent dans 06-graphic-design/outputs/carrousel-<slug>-<date>/{NOM_SPEC} ; "
               "le HTML et le PDF sont écrits à côté.",
    )
    parser.add_argument(
        "cible", nargs="*",
        help=f"carrousel à construire : son slug, ou le chemin de sa spec {NOM_SPEC}. Répétable.")
    parser.add_argument(
        "--all", action="store_true",
        help="reconstruire tous les carrousels. Obligatoire pour une reconstruction "
             "complète : elle ne se déclenche jamais toute seule.")
    parser.add_argument(
        "--dry-run", action="store_true",
        help="lister ce qui serait construit, sans écrire aucun fichier.")
    parser.add_argument(
        "--sans-pdf", action="store_true",
        help="écrire le HTML seul, sans export PDF (QA avant export, machine sans Playwright).")
    args = parser.parse_args(argv)

    if args.all and args.cible:
        parser.error("« --all » et une liste de carrousels s'excluent ; choisir l'un ou l'autre")
    if not args.all and not args.cible:
        parser.print_help()
        return 2

    try:
        if args.all:
            specs = charger_specs()
            if not specs:
                sys.stderr.write(f"aucune spec {NOM_SPEC} sous {SORTIES.relative_to(ROOT)}/carrousel-*/\n")
                return 2
        else:
            par_slug = {}
            specs = []
            inconnus = []
            for cible in args.cible:
                if cible.endswith(".json"):
                    chemin = pathlib.Path(cible)
                    if not chemin.exists():
                        inconnus.append(cible)
                        continue
                    specs.append(charger_spec(chemin))
                    continue
                if not par_slug:
                    par_slug = {s["slug"]: s for s in charger_specs()}
                if cible in par_slug:
                    specs.append(par_slug[cible])
                else:
                    inconnus.append(cible)
            if inconnus:
                disponibles = ", ".join(sorted(par_slug)) or "aucun"
                sys.stderr.write(f"slug inconnu : {', '.join(inconnus)}\n"
                                 f"slugs disponibles : {disponibles}\n")
                return 2
        return construire(specs, args.dry_run, pdf=not args.sans_pdf)
    except ErreurSpec as err:
        sys.stderr.write(f"{err}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
