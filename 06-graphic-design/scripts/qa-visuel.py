#!/usr/bin/env python3
"""QA visuelle d'un carrousel, d'un visuel composé ou d'une image générée.

Ce script mesure ce qu'un œil ne mesure pas : la part réelle de chaque couleur
dans l'image livrée, la police et le corps calculés de chaque texte, le contraste
texte/fond, et la zone de protection du logo. Il ne juge ni le goût ni le message.

Ce qu'il contrôle :

  a. couleurs. L'image rendue est quantifiée en 16 couleurs, chacune comparée à
     la palette de `01-brand/tokens.json` avec une tolérance de rendu ΔE76 ≤ 4
     (--delta-e). Une couleur hors palette qui dépasse 5 % des pixels (--part-max)
     est une erreur ; les traces en dessous du seuil, presque toujours de
     l'anti-crénelage, sont résumées en un avertissement. Les couleurs à portée
     limitée de tokens.json (`$extensions.<espace>.scope` : nuances dérivées,
     palette d'illustration) ne sont admises que si le chemin du livrable est
     dans leur portée.
  b. textes, pour une page HTML : police calculée (une famille de `font.*` dans
     tokens.json, ou une monospace), plancher typographique (28 px au format
     portrait d'un carrousel, 18 px sinon, --min-font), contraste WCAG 2.x (4,5:1,
     ou 3:1 au-delà de 24 px ou en gras). Le chrome du visuel, pied de slide,
     folio et mention de source, porte des repères et garde son propre plancher,
     22 px (--min-font-chrome) : il se déclare par `data-brand-chrome`, et les
     classes `.brand-chrome`, `.foot`, `.folio`, `.source`, `.credit` le
     reconnaissent (--chrome pour en ajouter).
  c. logo, pour une page HTML : tout élément portant `data-brand-logo` ou les
     classes `brand-logo` / `brand-mark` (plus les sélecteurs passés par --logo).
     Sa zone de protection vaut `logo.clear-space-ratio` × l'unité de protection
     (`logo.clear-space-unit` × hauteur du logo, 0,5 par défaut), lus dans
     tokens.json ; elle ne doit être pénétrée par rien, et rien ne doit être
     peint derrière le logo hors le fond de la composition (--logo-sur-aplat si
     la charte l'admet). Sa hauteur ne descend pas sous `logo.min-height-screen`.

Usage :
    python3 06-graphic-design/scripts/qa-visuel.py <fichier.html|png> [options]

Options : --viewport WxH (défaut 1080x1350), --tokens CHEMIN, --police FAMILLE
(répétable), --min-font N, --min-font-chrome N, --chrome SELECTEUR (répétable),
--allow-photo ZONE (répétable : sélecteur CSS ou rectangle `x,y,largeur,hauteur`
en pixels de l'image rendue), --logo SELECTEUR (répétable), --logo-sur-aplat,
--emplacement CHEMIN (chemin du livrable dans le dépôt, quand on analyse une
capture temporaire : il détermine les couleurs à portée limitée admises),
--delta-e N, --part-max N, --format text|json, --capture CHEMIN (garder l'image
rendue), --attente MS.

Codes de sortie : 0 propre, 1 au moins une erreur, 2 usage incorrect ou fichier
illisible. Les avertissements ne font pas échouer la QA.

Les decks projetés ont leur propre script,
`06-graphic-design/presentations/scripts/qa.py` (vendorisé depuis slides-agent,
voir docs/vendored-slides.md), qui contrôle en plus les débordements, le chrome,
les folios et la parité du moteur. Ce script-ci délègue ses calculs à
`06-graphic-design/scripts/qa_common.py` : couleurs, palette, contraste, police,
lecture du viewport et collecteur JavaScript des textes.

Prérequis : Pillow, et Playwright pour les pages HTML
(pip install pillow playwright && playwright install chromium).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path
from types import ModuleType

from PIL import Image, ImageDraw

RACINE = Path(__file__).resolve().parents[2]


def charger_module(nom: str, chemin: Path) -> ModuleType:
    """Charge un module par chemin : ces dossiers ne sont pas des paquets importables."""
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa_common = charger_module("qa_common", Path(__file__).resolve().parent / "qa_common.py")


COULEURS_QUANTIFIEES = 16   # niveaux de quantification de l'image (doctrine du contrôle)
DELTA_E_RENDU = 4.0         # tolérance de rendu entre une couleur mesurée et son token
PART_MAX_HORS_PALETTE = 5.0  # part de pixels au-delà de laquelle une couleur hors palette est une erreur
PLANCHER_PORTRAIT_PX = 28   # plancher typographique d'un carrousel, lu sur un téléphone
PLANCHER_PAYSAGE_PX = 18    # plancher typographique d'un visuel projeté ou lu à l'écran
PLANCHER_CHROME_PX = 22     # plancher du chrome : pied, folio, mention de source
VIEWPORT_DEFAUT = "1080x1350"
SELECTEURS_LOGO = ["[data-brand-logo]", ".brand-logo", ".brand-mark"]
# Registre du chrome d'un visuel : pied de slide, folio, mention de source et de
# crédit. Il porte des repères, pas le message, et garde donc son propre plancher
# typographique. Convention pour les nouveaux gabarits : poser `data-brand-chrome`
# sur l'élément ; les classes suivantes couvrent les gabarits courants.
SELECTEURS_CHROME = ["[data-brand-chrome]", ".brand-chrome", ".foot", ".folio", ".source", ".credit"]
MAX_TEXTES = 600            # textes remontés par page (le reste est signalé)
MAX_INTRUS = 6              # éléments listés par logo et par famille

# La zone de protection se compte en « unités de protection » : une fraction de
# la hauteur du logo (souvent la hauteur d'une lettre du logotype), multipliée
# par `logo.clear-space-ratio`. Les deux valeurs viennent de tokens.json ; à
# défaut, l'unité vaut la moitié de la hauteur du logo et le multiple vaut 1.
UNITE_PROTECTION_DEFAUT = 0.5
# Au-delà de cette fois la zone de protection, un conteneur qui peint n'est plus
# un aplat posé derrière le logo : c'est le sol de la composition.
TOLERANCE_SOL = 1.5

RECTANGLE_RE = re.compile(r"^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*$")
# Une valeur qui n'est faite que de chiffres, de virgules, de signes et d'espaces
# visait un rectangle : la refuser plutôt que la prendre pour un sélecteur CSS.
CHIFFRES_RE = re.compile(r"^[\d\s,.+-]+$")
EXTENSIONS_HTML = {".html", ".htm"}


class ErreurUsage(Exception):
    """Usage incorrect ou fichier illisible : sortie 2."""


# --------------------------------------------------------------------------
# tokens.json : palette, police, règles du logo
# --------------------------------------------------------------------------

def chemin_relatif(cible: Path, emplacement: str | None) -> str:
    """Chemin du livrable dans le dépôt : c'est lui qui ouvre les couleurs à portée limitée."""
    if emplacement:
        return emplacement.strip().lstrip("./")
    try:
        return cible.resolve().relative_to(RACINE).as_posix()
    except ValueError:
        return cible.resolve().as_posix()


def lire_tokens(chemin_tokens: Path) -> dict:
    try:
        return qa_common.lire_tokens(chemin_tokens)
    except ValueError as err:
        raise ErreurUsage(str(err)) from err


def palette_admise(tokens: dict, rel: str) -> list:
    """Couleurs de marque, plus celles dont la portée couvre le chemin du livrable."""
    try:
        palette = qa_common.charger_palette(tokens)
    except ValueError as err:
        raise ErreurUsage(str(err)) from err
    return [token for token in palette if token.admis_dans(rel)]


def _nombre(valeur, defaut: float) -> float:
    if valeur is None:
        return defaut
    brut = re.sub(r"[^0-9.]", "", str(valeur))
    try:
        return float(brut) if brut else defaut
    except ValueError:
        return defaut


def lire_logo(tokens: dict) -> tuple[float, float, float]:
    """Rend (multiple de l'unité de protection, unité en fraction de la hauteur, hauteur mini à l'écran)."""
    logo = tokens.get("logo") or {}
    valeur = lambda cle: (logo.get(cle) or {}).get("$value") if isinstance(logo.get(cle), dict) else None
    ratio = _nombre(valeur("clear-space-ratio"), 1.0)
    unite = _nombre(valeur("clear-space-unit"), UNITE_PROTECTION_DEFAUT)
    mini = _nombre(valeur("min-height-screen"), 0.0)
    return ratio, unite, mini


# --------------------------------------------------------------------------
# Contrôle (a) : couleurs
# --------------------------------------------------------------------------

def lire_zones(valeurs: list[str]) -> tuple[list[tuple[int, int, int, int]], list[str]]:
    """Sépare les zones déclarées en rectangles de pixels et en sélecteurs CSS.

    Une valeur qui ressemble à un rectangle sans en avoir la forme exacte est
    refusée ici, avec le format attendu : la laisser filer dans la branche des
    sélecteurs CSS produirait un message hors sujet, voire un contrôle muet.
    """
    rectangles, selecteurs = [], []
    for valeur in valeurs:
        forme = RECTANGLE_RE.match(valeur)
        if forme:
            x, y, largeur, hauteur = (int(n) for n in forme.groups())
            if largeur <= 0 or hauteur <= 0:
                raise ErreurUsage(
                    f"zone photo « {valeur} » : largeur et hauteur doivent être strictement "
                    f"positives (attendu x,y,largeur,hauteur en pixels)"
                )
            rectangles.append((x, y, largeur, hauteur))
        elif CHIFFRES_RE.match(valeur):
            raise ErreurUsage(
                f"zone photo « {valeur} » illisible : attendu quatre entiers positifs "
                f"x,y,largeur,hauteur en pixels de l'image rendue, ou un sélecteur CSS"
            )
        else:
            selecteurs.append(valeur)
    return rectangles, selecteurs


def masque(image: Image.Image, zones: list[tuple[int, int, int, int]]) -> tuple[Image.Image | None, int]:
    """Masque les zones déclarées (photos) et rend le masque plus le nombre de pixels exclus."""
    if not zones:
        return None, 0
    largeur_image, hauteur_image = image.size
    masque_image = Image.new("L", image.size, 255)
    dessin = ImageDraw.Draw(masque_image)
    for x, y, largeur, hauteur in zones:
        if x >= largeur_image or y >= hauteur_image:
            raise ErreurUsage(
                f"zone photo {x},{y},{largeur},{hauteur} hors de l'image "
                f"({largeur_image}x{hauteur_image} pixels)"
            )
        dessin.rectangle([x, y, x + largeur - 1, y + hauteur - 1], fill=0)
    exclus = largeur_image * hauteur_image - sum(masque_image.histogram()[255:])
    return masque_image, exclus


def couleur_de_remplissage(plate: Image.Image, zone_masquee: Image.Image) -> tuple[int, int, int]:
    """Couleur la plus fréquente parmi les pixels conservés, par échantillonnage régulier.

    Elle sert à recouvrir les zones exclues avant la quantification : remplies
    d'une couleur déjà présente ailleurs, elles ne consomment aucun des 16
    niveaux et ne déplacent aucun centroïde.
    """
    largeur, hauteur = plate.size
    pas = max(1, round((largeur * hauteur / 20000) ** 0.5))
    comptes: dict[tuple[int, int, int], int] = {}
    for y in range(0, hauteur, pas):
        for x in range(0, largeur, pas):
            if zone_masquee.getpixel((x, y)) == 0:
                continue
            couleur = plate.getpixel((x, y))
            comptes[couleur] = comptes.get(couleur, 0) + 1
    if not comptes:
        raise ErreurUsage("toute l'image est exclue par les zones déclarées : rien à contrôler")
    return max(comptes.items(), key=lambda entree: entree[1])[0]


def a_de_la_transparence(image: Image.Image) -> bool:
    """Vrai si l'image porte des pixels réellement transparents.

    Un PNG indexé ou un mode à canal alpha ne sont pas transparents par nature :
    on regarde le canal, pas le mode, sinon toute image en palette déclencherait
    une composition sur du blanc qui ne change rien.
    """
    if image.mode in ("RGBA", "LA"):
        return min(image.getchannel("A").getextrema()) < 255
    if image.mode == "P":
        return "transparency" in image.info
    return False


def en_hex(rouge: int, vert: int, bleu: int) -> str:
    return f"#{rouge:02X}{vert:02X}{bleu:02X}"


def analyser_couleurs(image: Image.Image, palette: list, zones: list, delta_max: float,
                      part_max: float) -> tuple[list[dict], dict]:
    """Compare les couleurs dominantes de l'image à la palette admise."""
    plate = image.convert("RGB")
    zone_masquee, exclus = masque(plate, zones)

    if zone_masquee is not None:
        # Recouvrir AVANT de quantifier : sinon les pixels exclus, photo ou
        # illustration, se partagent les 16 niveaux avec le reste et entraînent
        # les centroïdes des aplats voisins hors palette.
        plate = plate.copy()
        dessin = ImageDraw.Draw(plate)
        remplissage = couleur_de_remplissage(plate, zone_masquee)
        for x, y, largeur, hauteur in zones:
            dessin.rectangle([x, y, x + largeur - 1, y + hauteur - 1], fill=remplissage)

    quantifiee = plate.quantize(colors=COULEURS_QUANTIFIEES, method=Image.Quantize.MEDIANCUT)
    carte = quantifiee.getpalette()
    comptes = quantifiee.histogram(zone_masquee) if zone_masquee else quantifiee.histogram()
    total = sum(comptes)
    if total == 0:
        raise ErreurUsage("toute l'image est exclue par les zones déclarées : rien à contrôler")
    if not palette:
        raise ErreurUsage("aucune couleur de tokens.json n'est admise à cet emplacement")

    dominantes, hors_palette = [], []
    for index, compte in enumerate(comptes):
        if not compte:
            continue
        hexa = en_hex(*carte[index * 3:index * 3 + 3])
        proche = min(palette, key=lambda token: qa_common.delta_e76(hexa, token.hexa))
        ecart = qa_common.delta_e76(hexa, proche.hexa)
        entree = {
            "hex": hexa,
            "part": round(compte / total * 100, 2),
            "proche": f"color.{proche.nom}",
            "hex_proche": proche.hexa,
            "delta_e": round(ecart, 2),
        }
        dominantes.append(entree)
        if ecart > delta_max:
            hors_palette.append(entree)

    dominantes.sort(key=lambda e: e["part"], reverse=True)
    hors_palette.sort(key=lambda e: e["part"], reverse=True)

    constats = []
    traces = []
    for entree in hors_palette:
        if entree["part"] > part_max:
            constats.append({
                "niveau": "erreur", "type": "couleur",
                "message": (
                    f"{entree['hex']} occupe {entree['part']:.1f} % des pixels, hors palette "
                    f"(plus proche : {entree['proche']} {entree['hex_proche']}, "
                    f"ΔE76 {entree['delta_e']:.1f})"
                ),
            })
        else:
            traces.append(entree)

    if traces:
        cumul = sum(entree["part"] for entree in traces)
        noms = ", ".join(f"{e['hex']} {e['part']:.1f} %" for e in traces[:6])
        constats.append({
            "niveau": "avertissement", "type": "couleur",
            "message": (
                f"{len(traces)} nuance(s) hors palette sous le seuil de {part_max:g} %, "
                f"{cumul:.1f} % cumulés, le plus souvent de l'anti-crénelage : {noms}"
            ),
        })

    detail = {
        "pixels": total,
        "pixels_exclus": exclus,
        "delta_e_max": delta_max,
        "part_max": part_max,
        "palette": [f"color.{token.nom}" for token in palette],
        "dominantes": dominantes,
        "hors_palette": hors_palette,
    }
    return constats, detail


# --------------------------------------------------------------------------
# Contrôle (b) : textes
# --------------------------------------------------------------------------

def police_admise(font_family: str | None, familles: list[str]) -> bool:
    """Une famille de marque, ou une monospace, admise pour le registre technique."""
    if qa_common.police_conforme(font_family, familles):
        return True
    return qa_common.est_monospace(qa_common.premiere_famille(font_family))


def auditer_textes(textes: list[dict], total: int, min_font: int, min_font_chrome: int,
                   familles: list[str]) -> tuple[list[dict], list[str]]:
    constats: list[dict] = []
    gradients: list[str] = []

    for texte in textes:
        cible = f".{texte['cls']}" if texte["cls"] else texte["tag"].lower()
        taille, gras = texte["fs"], texte["poids"] >= 700

        chrome = bool(texte.get("chrome"))
        plancher_texte = min_font_chrome if chrome else min_font
        if taille < plancher_texte:
            registre = " du chrome" if chrome else ""
            constats.append({
                "niveau": "erreur", "type": "plancher-typo",
                "message": f"corps {taille}px sous le plancher{registre} {plancher_texte}px sur {cible}",
            })

        if familles and not police_admise(texte["police"], familles):
            famille = qa_common.premiere_famille(texte["police"])
            constats.append({
                "niveau": "erreur", "type": "police",
                "message": (
                    f"police « {famille} » sur {cible}, hors des familles de marque "
                    f"({', '.join(familles)}) et hors registre monospace"
                ),
            })

        if texte["gradient"]:
            gradients.append(f"{cible} « {texte['texte']} »")
            continue

        fond, uni = qa_common.resoudre_fond_et_uniformite(texte["fonds"])
        if not uni:
            constats.append({
                "niveau": "avertissement", "type": "contraste",
                "message": f"fond non uni, contraste non calculé sur {cible}",
            })
            continue

        couleur = qa_common.lire_couleur(texte["couleur"])
        if couleur is None:
            continue
        rapport = qa_common.contraste(qa_common.aplatir(couleur, fond), fond)
        seuil = qa_common.seuil_contraste(taille, gras=gras)
        if rapport < seuil:
            constats.append({
                "niveau": "erreur", "type": "contraste",
                "message": f"contraste {rapport:.2f}:1 sous {seuil}:1 sur {cible} ({taille}px)",
            })

    reste = total - len(textes)
    if reste > 0:
        constats.append({
            "niveau": "avertissement", "type": "troncature",
            "message": f"{reste} éléments de texte non audités ({total} relevés, {len(textes)} remontés)",
        })
    return constats, gradients


# --------------------------------------------------------------------------
# Contrôle (c) : logo
# --------------------------------------------------------------------------

def decrire(elements: list[dict], limite: int = MAX_INTRUS) -> str:
    """Nomme au plus `limite` éléments par leur classe, à défaut par leur balise."""
    montres = []
    for element in elements[:limite]:
        nom = f".{element['cls']}" if element["cls"] else element["tag"].lower()
        montres.append(f"{nom} ({element['quoi']})")
    reste = len(elements) - len(montres)
    return ", ".join(montres) + (f", et {reste} autre(s)" if reste > 0 else "")


def fonds_peints(logo: dict, zone: tuple[float, float]) -> list[dict]:
    """Aplats posés derrière le logo par ses propres conteneurs.

    On remonte les ancêtres. Le premier qui peint quelque chose et déborde
    largement la zone de protection est le sol de la composition : le fond de
    page, le fond de slide, la couleur du support. Il est admis, et on s'arrête
    là. Un conteneur à la taille du logo, lui, n'existe que pour lui : c'est un
    cartouche, une pastille ou un halo.
    """
    peints = []
    for fond in logo["fonds"]:
        image = not qa_common.fond_uni(fond.get("i"))
        couleur = qa_common.lire_couleur(fond.get("c"))
        aplat = couleur is not None and couleur[3] > 0.02
        if not (image or aplat):
            continue
        if fond["w"] > zone[0] * TOLERANCE_SOL or fond["h"] > zone[1] * TOLERANCE_SOL:
            break
        peints.append({
            "cls": fond["cls"], "tag": fond["tag"],
            "quoi": "fond dégradé ou imagé" if image else "aplat",
        })
    return peints


def auditer_logos(logos: list[dict], ratio: float, unite: float, mini: float,
                  aplat_admis: bool = False) -> list[dict]:
    constats: list[dict] = []
    for index, logo in enumerate(logos, start=1):
        cible = f".{logo['cls']}" if logo["cls"] else f"logo {index}"
        marge = round(logo["hauteur"] * unite * ratio, 1)

        if mini and logo["hauteur"] < mini:
            constats.append({
                "niveau": "erreur", "type": "logo-taille",
                "message": (
                    f"logo {cible} haut de {logo['hauteur']:.0f}px, sous la hauteur minimale "
                    f"à l'écran de {mini:.0f}px"
                ),
            })

        if logo["intrus"]:
            constats.append({
                "niveau": "erreur", "type": "zone-protection",
                "message": (
                    f"zone de protection du logo {cible} pénétrée sur {marge:g}px "
                    f"(unité {unite:g} × hauteur du logo, × {ratio:g}) par : {decrire(logo['intrus'])}"
                ),
            })

        zone = (logo["largeur"] + 2 * marge, logo["hauteur"] + 2 * marge)
        peints = list(logo["derriere"]) + fonds_peints(logo, zone)

        if peints:
            constats.append({
                "niveau": "avertissement" if aplat_admis else "erreur", "type": "fond-logo",
                "message": (
                    f"le logo {cible} devrait reposer sur un fond nu : {decrire(peints)} "
                    f"chevauche sa surface"
                ),
            })
    return constats


# --------------------------------------------------------------------------
# Rendu de la page
# --------------------------------------------------------------------------

COLLECTEUR = """
(args) => {
  const [selLogos, selZones, selChrome, maxTextes, facteurMarge] = args;
  const collecterTextes = __COLLECTE_TEXTES__;
  const cls = el => (el.getAttribute('class') || '').slice(0, 40);
  const visible = el => el.checkVisibility
    ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })
    : (() => { const cs = getComputedStyle(el);
               return cs.display !== 'none' && cs.visibility !== 'hidden'
                      && parseFloat(cs.opacity) > 0; })();
  const boite = el => {
    const r = el.getBoundingClientRect();
    return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height,
             left: r.left, top: r.top, right: r.right, bottom: r.bottom };
  };

  // Ce qui fait encre : un texte propre, une image, un tracé vectoriel, un aplat,
  // un filet. Le reste est un conteneur transparent : il ne peint rien et
  // n'empiète sur rien. Un `<svg>` ou un `<g>` plein cadre est justement un
  // conteneur, souvent transparent de part en part : son encre est dans ses
  // tracés, qui sont des éléments à part entière et seront jugés pour eux-mêmes.
  const CONTENEURS_VECTORIELS = ['SVG', 'G', 'DEFS', 'SYMBOL', 'CLIPPATH', 'MASK', 'PATTERN'];
  const FORMES_VECTORIELLES = ['PATH', 'CIRCLE', 'ELLIPSE', 'RECT', 'LINE', 'POLYGON',
                               'POLYLINE', 'USE', 'IMAGE', 'TEXT', 'TSPAN'];
  const peint = valeur => !!valeur && valeur !== 'none' && valeur !== 'rgba(0, 0, 0, 0)'
                          && valeur !== 'transparent';
  const encre = el => {
    const cs = getComputedStyle(el);
    const tag = el.tagName.toUpperCase();
    if (Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim()))
      return 'texte';
    if (CONTENEURS_VECTORIELS.includes(tag)) return null;
    if (FORMES_VECTORIELLES.includes(tag)) {
      if (peint(cs.fill)) return 'tracé';
      if (peint(cs.stroke) && (parseFloat(cs.strokeWidth) || 0) > 0) return 'tracé';
      return null;
    }
    if (['IMG', 'CANVAS', 'VIDEO', 'PICTURE'].includes(tag)) return 'image';
    if (cs.backgroundImage && cs.backgroundImage !== 'none') return 'fond imagé';
    const m = (cs.backgroundColor || '').match(/rgba?\\(([^)]+)\\)/);
    if (m) {
      const parts = m[1].split(',').map(s => parseFloat(s));
      const alpha = parts.length > 3 ? parts[3] : 1;
      if (alpha > 0.02) return 'aplat';
    }
    const filets = ['borderTopWidth', 'borderRightWidth', 'borderBottomWidth', 'borderLeftWidth']
      .map(k => parseFloat(cs[k]) || 0);
    if (Math.max.apply(null, filets) > 0 && cs.borderTopStyle !== 'none') return 'filet';
    return null;
  };

  const textes = collecterTextes(document.body, null, {
    max: maxTextes,
    extra: el => ({ chrome: !!el.closest(selChrome) }),
  });

  const logos = Array.from(document.querySelectorAll(selLogos)).map(logo => {
    const r = boite(logo);
    // Zone de protection : unité (fraction de la hauteur du logo) multipliée
    // par `clear-space-ratio`, que Python a fondus dans facteurMarge.
    const marge = r.h * facteurMarge;
    const intrus = [], derriere = [];
    document.querySelectorAll('*').forEach(el => {
      if (el === logo || logo.contains(el) || el.contains(logo)) return;
      if (!visible(el)) return;
      const e = boite(el);
      if (e.w < 1 || e.h < 1) return;
      if (e.right <= r.left - marge || e.left >= r.right + marge
          || e.bottom <= r.top - marge || e.top >= r.bottom + marge) return;
      const quoi = encre(el);
      if (!quoi) return;
      const sousLeLogo = !(e.right <= r.left || e.left >= r.right
                           || e.bottom <= r.top || e.top >= r.bottom);
      (sousLeLogo ? derriere : intrus).push({ cls: cls(el), tag: el.tagName, quoi: quoi });
    });

    const fonds = [];
    let n = logo.parentElement;
    for (let profondeur = 0; n && profondeur < 40; n = n.parentElement, profondeur++) {
      const cs = getComputedStyle(n);
      const b = boite(n);
      fonds.push({ cls: cls(n), tag: n.tagName, c: cs.backgroundColor, i: cs.backgroundImage,
                   w: b.w, h: b.h });
      if (n === document.documentElement) break;
    }

    return { cls: cls(logo), hauteur: r.h, largeur: r.w, intrus: intrus,
             derriere: derriere, fonds: fonds };
  });

  const zones = selZones.map(sel => {
    const boites = [];
    document.querySelectorAll(sel).forEach(el => {
      const e = boite(el);
      if (e.w >= 1 && e.h >= 1) boites.push([Math.round(e.x), Math.round(e.y),
                                             Math.round(e.w), Math.round(e.h)]);
    });
    return { selecteur: sel, boites: boites };
  });

  return { textes: textes.liste, textes_total: textes.total, logos: logos, zones: zones };
}
""".replace("__COLLECTE_TEXTES__", qa_common.JS_TEXTES)


def rendre(cible: Path, viewport: dict, attente: int, selecteurs_logo: list[str],
           selecteurs_chrome: list[str], selecteurs_zone: list[str], facteur_marge: float,
           capture: Path) -> tuple[Image.Image, dict]:
    """Rend la page dans Chromium, en tire une capture pleine page et le relevé du DOM."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as err:
        raise ErreurUsage(
            "Playwright n'est pas installé. Lancer :\n"
            "  pip install playwright && playwright install chromium"
        ) from err

    with sync_playwright() as playwright:
        navigateur = playwright.chromium.launch()
        contexte = navigateur.new_context(viewport=viewport, reduced_motion="reduce")
        page = contexte.new_page()
        page.goto(cible.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(attente)
        page.screenshot(path=str(capture), full_page=True)
        releve = page.evaluate(
            COLLECTEUR,
            [", ".join(selecteurs_logo), selecteurs_zone, ", ".join(selecteurs_chrome),
             MAX_TEXTES, facteur_marge],
        )
        navigateur.close()

    return Image.open(capture), releve


# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------

def compter(constats: list[dict], niveau: str) -> int:
    return sum(1 for constat in constats if constat["niveau"] == niveau)


def rapport_texte(resume: dict, constats: list[dict], couleurs: dict, gradients: list[str]) -> None:
    print(f"qa  · visuel   {resume['fichier']}")
    print(f"qa  · type     {resume['type']}"
          + (f" · viewport {resume['viewport']}" if resume["viewport"] else ""))
    if resume["min_font"]:
        print(f"qa  · plancher {resume['min_font']}px"
              f" · chrome {resume['min_font_chrome']}px"
              f" · textes {resume['textes']} · logos {resume['logos']}")
    exclus = f" · {couleurs['pixels_exclus']} exclus" if couleurs["pixels_exclus"] else ""
    print(f"qa  · pixels   {couleurs['pixels']}{exclus} · palette {len(couleurs['palette'])} couleurs"
          f" · ΔE76 ≤ {couleurs['delta_e_max']:g}\n")

    print("  couleurs dominantes :")
    for entree in couleurs["dominantes"][:8]:
        verdict = ("palette" if entree["delta_e"] <= couleurs["delta_e_max"]
                   else f"hors palette, ΔE {entree['delta_e']:.1f}")
        print(f"    · {entree['hex']} {entree['part']:>5.1f} %  {verdict}"
              f"  (proche {entree['proche']})")

    if constats:
        print("\n  constats :")
        for constat in constats:
            marque = {"erreur": "!", "avertissement": "~"}.get(constat["niveau"], "+")
            print(f"    {marque} [{constat['type']}] {constat['message']}")

    if gradients:
        print("\n  texte en background-clip: text (contraste non jugé, à relire à l'œil) :")
        for entree in gradients:
            print(f"    · {entree}")

    erreurs = compter(constats, "erreur")
    avertissements = compter(constats, "avertissement")
    print()
    if erreurs:
        print(f"FAIL · {erreurs} erreur(s), {avertissements} avertissement(s)")
    else:
        print("Visuel clean" + (f" · {avertissements} avertissement(s)" if avertissements else ""))


# --------------------------------------------------------------------------
# Programme
# --------------------------------------------------------------------------

def plancher(viewport: dict, demande: int | None) -> int:
    """Le plancher du carrousel au format portrait, celui d'un visuel large sinon."""
    if demande is not None:
        return demande
    return PLANCHER_PORTRAIT_PX if viewport["height"] > viewport["width"] else PLANCHER_PAYSAGE_PX


def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        description="QA visuelle d'un carrousel, d'un visuel composé ou d'une image générée : "
                    "couleurs contre la palette, police, corps, contraste, zone de protection du logo.",
    )
    parseur.add_argument("fichier", help="page HTML à rendre, ou image déjà produite (PNG, JPEG…)")
    parseur.add_argument("--viewport", default=VIEWPORT_DEFAUT,
                         help=f"taille de la fenêtre pour une page HTML (défaut : {VIEWPORT_DEFAUT}, "
                              f"le format d'un carrousel LinkedIn)")
    parseur.add_argument("--tokens", default=str(RACINE / "01-brand" / "tokens.json"),
                         help="palette, polices et règles du logo (défaut : 01-brand/tokens.json)")
    parseur.add_argument("--police", action="append", default=[], metavar="FAMILLE",
                         help="famille de police admise, à la place des familles `font.*` de "
                              "tokens.json. Répétable")
    parseur.add_argument("--min-font", type=int, default=None,
                         help=f"plancher typographique en px (défaut : {PLANCHER_PORTRAIT_PX} au "
                              f"format portrait d'un carrousel, {PLANCHER_PAYSAGE_PX} sinon)")
    parseur.add_argument("--min-font-chrome", type=int, default=PLANCHER_CHROME_PX,
                         help=f"plancher typographique du chrome en px (défaut : {PLANCHER_CHROME_PX}). "
                              f"Le chrome porte les repères du visuel, pied de slide, folio, mention "
                              f"de source : plus petits que le message, ils restent soumis au "
                              f"contrôle de police et de contraste comme tout texte visible")
    parseur.add_argument("--chrome", action="append", default=[], metavar="SELECTEUR",
                         help="sélecteur de chrome supplémentaire, en plus de `data-brand-chrome`, "
                              "`.brand-chrome`, `.foot`, `.folio`, `.source` et `.credit`. Répétable")
    parseur.add_argument("--allow-photo", action="append", default=[], metavar="ZONE",
                         help="zone exclue du contrôle des couleurs, parce qu'elle porte une photo : "
                              "sélecteur CSS (page HTML) ou rectangle `x,y,largeur,hauteur` en pixels "
                              "de l'image rendue. Répétable")
    parseur.add_argument("--logo", action="append", default=[], metavar="SELECTEUR",
                         help="sélecteur de logo supplémentaire, en plus de `data-brand-logo`, "
                              "`.brand-logo` et `.brand-mark`. Répétable")
    parseur.add_argument("--logo-sur-aplat", action="store_true",
                         help="la charte admet un aplat ou une pastille derrière le logo : le "
                              "constat `fond-logo` passe en avertissement")
    parseur.add_argument("--emplacement", metavar="CHEMIN",
                         help="chemin du livrable dans le dépôt, quand le fichier analysé est une "
                              "capture temporaire : il décide des couleurs à portée limitée admises")
    parseur.add_argument("--delta-e", type=float, default=DELTA_E_RENDU,
                         help=f"tolérance de rendu entre une couleur mesurée et son token "
                              f"(défaut : {DELTA_E_RENDU:g})")
    parseur.add_argument("--part-max", type=float, default=PART_MAX_HORS_PALETTE,
                         help=f"part de pixels au-delà de laquelle une couleur hors palette est une "
                              f"erreur (défaut : {PART_MAX_HORS_PALETTE:g} %%)")
    parseur.add_argument("--format", choices=("text", "json"), default="text",
                         help="forme de la sortie (défaut : text)")
    parseur.add_argument("--capture", metavar="CHEMIN",
                         help="conserver l'image rendue à ce chemin (hors du dépôt)")
    parseur.add_argument("--attente", type=int, default=500,
                         help="attente en ms après chargement de la page (défaut : 500)")
    return parseur


def executer(args: argparse.Namespace) -> int:
    cible = Path(args.fichier)
    if not cible.exists():
        raise ErreurUsage(f"fichier introuvable : {cible}")
    if args.delta_e < 0:
        raise ErreurUsage(f"--delta-e doit être positif ou nul, reçu {args.delta_e:g}")
    if args.part_max < 0:
        raise ErreurUsage(f"--part-max est une part de pixels en pourcentage, "
                          f"donc positive ou nulle, reçu {args.part_max:g}")

    tokens = lire_tokens(Path(args.tokens))
    rel = chemin_relatif(cible, args.emplacement)
    palette = palette_admise(tokens, rel)
    rectangles, selecteurs_zone = lire_zones(args.allow_photo)
    est_html = cible.suffix.lower() in EXTENSIONS_HTML

    ratio, unite, hauteur_mini = lire_logo(tokens)
    familles = list(args.police) or qa_common.familles_de_marque(tokens)

    constats: list[dict] = []
    gradients: list[str] = []
    viewport = None
    min_font = min_font_chrome = None
    nb_textes = nb_logos = 0

    with tempfile.TemporaryDirectory(prefix="qa-visuel-") as temporaire:
        if est_html:
            try:
                viewport = qa_common.lire_viewport(args.viewport)
            except ValueError as err:
                raise ErreurUsage(str(err)) from err
            capture = Path(args.capture) if args.capture else Path(temporaire) / "rendu.png"
            capture.parent.mkdir(parents=True, exist_ok=True)
            image, releve = rendre(
                cible, viewport, args.attente, SELECTEURS_LOGO + args.logo,
                SELECTEURS_CHROME + args.chrome, selecteurs_zone,
                ratio * unite, capture,
            )
            min_font = plancher(viewport, args.min_font)
            min_font_chrome = args.min_font_chrome
            nb_textes, nb_logos = releve["textes_total"], len(releve["logos"])

            if not familles:
                constats.append({
                    "niveau": "avertissement", "type": "police",
                    "message": "aucune famille `font.*` dans tokens.json ni --police : "
                               "la police des textes n'est pas contrôlée",
                })
            textes, gradients = auditer_textes(
                releve["textes"], releve["textes_total"], min_font, min_font_chrome, familles,
            )
            constats.extend(textes)
            constats.extend(auditer_logos(releve["logos"], ratio, unite, hauteur_mini,
                                          aplat_admis=args.logo_sur_aplat))

            for zone in releve["zones"]:
                if not zone["boites"]:
                    constats.append({
                        "niveau": "avertissement", "type": "zone-photo",
                        "message": f"aucun élément visible pour la zone déclarée « {zone['selecteur']} »",
                    })
                rectangles.extend(tuple(boite) for boite in zone["boites"])
        else:
            for option, donnee in (("--min-font", args.min_font), ("--logo", args.logo),
                                   ("--police", args.police)):
                if donnee:
                    constats.append({
                        "niveau": "avertissement", "type": "usage",
                        "message": f"{option} ne s'applique qu'à une page HTML : sans DOM, seules "
                                   f"les couleurs sont contrôlées",
                    })
            if selecteurs_zone:
                raise ErreurUsage(
                    "une zone déclarée par sélecteur CSS n'a de sens que sur une page HTML : "
                    "sur une image, donner un rectangle `x,y,largeur,hauteur`"
                )
            try:
                image = Image.open(cible)
                image.load()
            except Exception as err:
                raise ErreurUsage(f"image illisible : {cible} ({err})") from err
            if a_de_la_transparence(image):
                fond = Image.new("RGB", image.size, (255, 255, 255))
                transparente = image.convert("RGBA")
                fond.paste(transparente, mask=transparente.split()[-1])
                image = fond
                constats.append({
                    "niveau": "avertissement", "type": "transparence",
                    "message": "image à transparence réelle : elle est composée sur du blanc avant analyse",
                })
            if args.capture:
                Path(args.capture).parent.mkdir(parents=True, exist_ok=True)
                image.save(args.capture)

        couleurs_constats, couleurs = analyser_couleurs(
            image, palette, rectangles, args.delta_e, args.part_max,
        )
    constats = couleurs_constats + constats

    resume = {
        "fichier": str(cible),
        "type": "page HTML rendue" if est_html else "image",
        "emplacement": rel,
        "viewport": args.viewport if est_html else None,
        "min_font": min_font,
        "min_font_chrome": min_font_chrome,
        "familles": familles,
        "textes": nb_textes,
        "logos": nb_logos,
        "errors": compter(constats, "erreur"),
        "warnings": compter(constats, "avertissement"),
    }

    if args.format == "json":
        print(json.dumps({
            "summary": resume, "couleurs": couleurs,
            "constats": constats, "gradient_text": gradients,
        }, ensure_ascii=False, indent=2))
    else:
        rapport_texte(resume, constats, couleurs, gradients)

    return 1 if resume["errors"] else 0


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)
    try:
        return executer(args)
    except ErreurUsage as err:
        sys.stderr.write(f"{err}\n")
        return 2
    except Exception as err:
        # Une panne du contrôle n'est pas un défaut du livrable : elle sort en 2,
        # en une ligne, pour qu'un appelant ne la prenne jamais pour une QA rouge.
        sys.stderr.write(f"contrôle interrompu : {type(err).__name__} : {err}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
