#!/usr/bin/env python3
"""Briques de calcul partagées par les scripts de QA visuelle.

Les scripts de QA du template (carrousels, visuels composés : qa-visuel.py ;
landing pages : 05-web-content/scripts/qa-landing.py ; la QA des decks,
vendorisée depuis slides-agent, porte ses propres calculs) collectent dans le
navigateur des valeurs CSS déjà calculées (`getComputedStyle`), sous forme de
chaînes, puis délèguent ici tout le raisonnement : lecture des couleurs,
luminance relative, contraste WCAG 2.x, aplatissement d'une pile de fonds
semi-transparents, opacité effective d'un texte, seuil de contraste exigé selon le corps, conformité de la
police, et comparaison d'une couleur mesurée à la palette de `01-brand/tokens.json`
(conversion sRGB vers Lab D65, distance ΔE76, portée des couleurs).

Il porte aussi ce que les scripts de QA partagent sans le calculer : la lecture
d'une taille de viewport, la lecture de `tokens.json`, et la source JavaScript du
collecteur de textes visibles, insérée telle quelle dans le `page.evaluate` de
chaque script. Ces pièces vivent ici pour qu'aucune ne soit recopiée d'un script
à l'autre.

Aucune valeur de marque n'est écrite dans ce module : les familles de police et
la palette se lisent dans `01-brand/tokens.json` (format DTCG : `color.*.$value`,
`font.*.$value`), ou se passent en argument.

Ce module est en pur Python : pas de Playwright, pas de navigateur, pas de
dépendance hors bibliothèque standard. Il est donc testable seul et réutilisable
par n'importe quel contrôle visuel du dépôt.

Tests : `python3 -m pytest scripts/tests/test_qa_common.py -q`
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, NamedTuple

# Seuils WCAG 2.x, niveau AA.
CONTRASTE_CORPS = 4.5
CONTRASTE_LARGE = 3.0
TAILLE_LARGE_PX = 24.0        # 18 pt
TAILLE_LARGE_GRAS_PX = 18.66  # 14 pt en gras

# Familles monospace courantes dont le nom ne contient pas « mono ».
MONO_CONNUES = {"menlo", "consolas", "monaco", "courier", "courier new"}

# Familles génériques CSS : jamais une police de marque, toujours un repli.
FAMILLES_GENERIQUES = {"serif", "sans-serif", "monospace", "cursive", "fantasy",
                       "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace",
                       "ui-rounded", "emoji", "math", "fangsong"}

_NOMBRE = re.compile(r"[-+]?[0-9]*\.?[0-9]+%?")
_FONCTION = re.compile(r"^rgba?\((.*)\)$")


Couleur = tuple[int, int, int]
CouleurAlpha = tuple[int, int, int, float]


def _canal(jeton: str) -> float:
    """Lit un canal RVB, en absolu (0-255) ou en pourcentage."""
    if jeton.endswith("%"):
        return float(jeton[:-1]) / 100.0 * 255.0
    return float(jeton)


def _alpha(jeton: str) -> float:
    valeur = float(jeton[:-1]) / 100.0 if jeton.endswith("%") else float(jeton)
    return min(1.0, max(0.0, valeur))


def _arrondi(valeur: float) -> int:
    """Arrondi au plus proche, moitié vers le haut, borné à l'octet."""
    return min(255, max(0, int(valeur + 0.5)))


def lire_couleur(css: str | None) -> CouleurAlpha | None:
    """Convertit une couleur CSS en `(r, v, b, alpha)`, ou None si illisible.

    Accepte les formes que renvoie `getComputedStyle` (`rgb(...)`, `rgba(...)`,
    syntaxe à espaces) ainsi que les notations hexadécimales à 3, 4, 6 ou 8
    chiffres, et le mot-clé `transparent`.
    """
    if not css:
        return None
    texte = css.strip().lower()

    if texte == "transparent":
        return (0, 0, 0, 0.0)

    if texte.startswith("#"):
        chiffres = texte[1:]
        if not re.fullmatch(r"[0-9a-f]+", chiffres):
            return None
        if len(chiffres) in (3, 4):
            chiffres = "".join(c * 2 for c in chiffres)
        if len(chiffres) not in (6, 8):
            return None
        r, v, b = (int(chiffres[i:i + 2], 16) for i in (0, 2, 4))
        a = int(chiffres[6:8], 16) / 255.0 if len(chiffres) == 8 else 1.0
        return (r, v, b, a)

    fonction = _FONCTION.match(texte)
    if not fonction:
        return None
    jetons = _NOMBRE.findall(fonction.group(1))
    if len(jetons) < 3:
        return None
    r, v, b = (_arrondi(_canal(j)) for j in jetons[:3])
    a = _alpha(jetons[3]) if len(jetons) > 3 else 1.0
    return (r, v, b, a)


def luminance(couleur: Couleur) -> float:
    """Luminance relative WCAG 2.x d'une couleur opaque."""
    canaux = []
    for brut in couleur:
        c = brut / 255.0
        canaux.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, v, b = canaux
    return 0.2126 * r + 0.7152 * v + 0.0722 * b


def contraste(premier_plan: Couleur, fond: Couleur) -> float:
    """Rapport de contraste WCAG 2.x entre deux couleurs opaques (1.0 à 21.0)."""
    a, b = luminance(premier_plan), luminance(fond)
    clair, sombre = max(a, b), min(a, b)
    return (clair + 0.05) / (sombre + 0.05)


def aplatir(dessus: CouleurAlpha, dessous: Couleur) -> Couleur:
    """Compose une couleur semi-transparente sur un fond opaque (source-over)."""
    r, v, b, a = dessus
    return tuple(_arrondi(a * haut + (1 - a) * bas) for haut, bas in zip((r, v, b), dessous))


def resoudre_fond(pile: list[str], defaut: Couleur = (255, 255, 255)) -> Couleur:
    """Résout la couleur de fond réelle d'un texte.

    `pile` liste les `background-color` calculés des ancêtres, du plus proche du
    texte au plus lointain. Les couches translucides sont composées sur la
    première couche opaque rencontrée ; sans couche opaque, `defaut` sert de base
    (le blanc du document).
    """
    couches = []
    base = defaut
    for css in pile:
        couleur = lire_couleur(css)
        if couleur is None or couleur[3] == 0.0:
            continue
        if couleur[3] >= 1.0:
            base = couleur[:3]
            break
        couches.append(couleur)

    for couche in reversed(couches):
        base = aplatir(couche, base)
    return base


def seuil_contraste(taille_px: float, gras: bool = False) -> float:
    """Contraste minimal exigé pour un texte de cette taille (WCAG 2.x AA)."""
    if taille_px >= TAILLE_LARGE_PX or (gras and taille_px >= TAILLE_LARGE_GRAS_PX):
        return CONTRASTE_LARGE
    return CONTRASTE_CORPS


def fond_uni(background_image: str | None) -> bool:
    """Vrai si le fond est une couleur unie, faux s'il porte un dégradé ou une image.

    Sur un fond non uni, le contraste n'est pas calculable par une formule à deux
    couleurs : l'appelant le signale en avertissement plutôt que de trancher.
    """
    if not background_image:
        return True
    return background_image.strip().lower() in ("none", "initial", "unset")


def premiere_famille(font_family: str | None) -> str:
    """Première famille déclarée dans un `font-family` calculé, sans guillemets."""
    if not font_family:
        return ""
    return font_family.split(",")[0].strip().strip("\"'").strip()


def est_monospace(famille: str) -> bool:
    nom = famille.strip().lower()
    return "mono" in nom or nom in MONO_CONNUES


def police_conforme(
    font_family: str | None,
    attendues: str | Iterable[str],
    mono_autorise: bool = False,
) -> bool:
    """Vrai si la police calculée est une famille de la marque (ou une monospace pour du code).

    `attendues` est une famille ou une liste de familles : celles de
    `01-brand/tokens.json` (voir `familles_de_marque`), ou celles passées en
    argument au script de QA. La comparaison ignore la casse.
    """
    famille = premiere_famille(font_family)
    if not famille:
        return False
    if isinstance(attendues, str):
        attendues = [attendues]
    if famille.lower() in {a.strip().lower() for a in attendues if a}:
        return True
    return mono_autorise and est_monospace(famille)


def resoudre_fond_et_uniformite(niveaux: list[dict]) -> tuple[Couleur, bool]:
    """Résout la couleur de fond d'un texte et dit si ce fond est uni.

    `niveaux` liste, du texte vers la racine, le `background-color` (clé `c`) et
    le `background-image` (clé `i`) calculés de chaque ancêtre. On s'arrête au
    premier fond opaque ; une image ou un dégradé rencontré avant lui rend le
    fond non uni, donc le contraste non calculable par une formule à deux
    couleurs : l'appelant le signale plutôt que de trancher.
    """
    couleurs: list[str] = []
    for niveau in niveaux:
        if not fond_uni(niveau.get("i")):
            return resoudre_fond(couleurs), False
        couleur = lire_couleur(niveau.get("c"))
        couleurs.append(niveau.get("c"))
        if couleur is not None and couleur[3] >= 1.0:
            break
    return resoudre_fond(couleurs), True


def opacite_effective(niveaux: list[dict]) -> float:
    """Produit des opacités (clé `o`) du texte jusqu'à son fond opaque, celui-ci exclu.

    Mêmes `niveaux` que `resoudre_fond_et_uniformite`, du texte vers la racine,
    chacun avec son `opacity` calculé en clé `o`. Un texte posé à 60 % d'opacité
    sur son fond se compose avec ce fond avant le calcul du contraste. Le niveau
    qui porte le fond opaque est exclu : s'il s'estompe, il s'estompe avec le
    texte et leur contraste relatif bouge à peine. La marche s'arrête aussi au
    premier fond non uni (dégradé, image), où le contraste n'est pas calculable.
    """
    opacite = 1.0
    for niveau in niveaux:
        if not fond_uni(niveau.get("i")):
            break
        couleur = lire_couleur(niveau.get("c"))
        if couleur is not None and couleur[3] >= 1.0:
            break
        valeur = niveau.get("o")
        if isinstance(valeur, (int, float)) and 0.0 <= valeur <= 1.0:
            opacite *= valeur
    return opacite


def lire_viewport(valeur: str) -> dict:
    """Lit une taille `LARGEURxHAUTEUR` et rend le dictionnaire attendu par Playwright.

    Lève `ValueError` sur une valeur illisible : c'est l'appelant, script de QA,
    qui décide du message et du code de sortie.
    """
    try:
        largeur, hauteur = valeur.lower().split("x")
        taille = {"width": int(largeur), "height": int(hauteur)}
    except Exception:
        raise ValueError(f"viewport invalide : {valeur} (attendu LARGEURxHAUTEUR, ex. 1920x1080)")
    if taille["width"] <= 0 or taille["height"] <= 0:
        raise ValueError(f"viewport invalide : {valeur} (dimensions strictement positives)")
    return taille


# --------------------------------------------------------------------------
# tokens.json : lecture, familles de police, palette
# --------------------------------------------------------------------------

def lire_tokens(chemin: Path) -> dict[str, Any]:
    """Lit `01-brand/tokens.json`. Lève `ValueError` si absent ou illisible."""
    chemin = Path(chemin)
    if not chemin.exists():
        raise ValueError(f"{chemin} introuvable : la palette et la police ne peuvent pas être vérifiées")
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise ValueError(f"{chemin} illisible : {err}") from err
    if not isinstance(donnees, dict):
        raise ValueError(f"{chemin} : un objet JSON est attendu à la racine")
    return donnees


def familles_de_marque(tokens: dict[str, Any]) -> list[str]:
    """Première famille de chaque token de police (`font.<nom>.$value`).

    Une valeur peut être une liste (`["Ma Police", "system-ui", "sans-serif"]`) ou
    une chaîne CSS (`"'Ma Police', sans-serif"`). Les familles génériques CSS ne
    sont jamais retenues comme police de marque.
    """
    familles: list[str] = []
    for cle, noeud in (tokens.get("font") or {}).items():
        if cle.startswith("$") or not isinstance(noeud, dict):
            continue
        valeur = noeud.get("$value")
        if isinstance(valeur, list):
            premiere = valeur[0] if valeur and isinstance(valeur[0], str) else ""
        elif isinstance(valeur, str):
            premiere = valeur.split(",")[0]
        else:
            continue
        premiere = premiere.strip().strip("\"'").strip()
        if premiere and premiere.lower() not in FAMILLES_GENERIQUES and premiere not in familles:
            familles.append(premiere)
    return familles


# Blanc de référence D65, observateur 2 degrés.
BLANC_D65 = (95.047, 100.000, 108.883)


@lru_cache(maxsize=8192)
def developper_hex(valeur: str) -> str:
    """Rend un #RRGGBB majuscule depuis #RGB, #RRGGBB ou #RRGGBBAA."""
    brut = valeur.strip().lstrip("#")
    if len(brut) == 3:
        brut = "".join(c * 2 for c in brut)
    elif len(brut) == 8:
        brut = brut[:6]
    if len(brut) != 6 or not re.fullmatch(r"[0-9A-Fa-f]{6}", brut):
        raise ValueError(f"hex non développable : {valeur!r}")
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
    """Distance CIE76 entre deux hex."""
    l1, a1, b1 = hex_vers_lab(premier)
    l2, a2, b2 = hex_vers_lab(second)
    return ((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5


class TokenCouleur(NamedTuple):
    nom: str                   # chemin du token sous `color`, ex. « primary » ou « derived.primary-deep »
    hexa: str                  # #RRGGBB majuscule
    scope: tuple[str, ...]     # vide = palette de marque, admise partout

    def admis_dans(self, rel: str) -> bool:
        """Vrai si la couleur est admise pour un livrable à ce chemin du dépôt."""
        if not self.scope:
            return True
        return any(rel == d or rel.startswith(d.rstrip("/") + "/") for d in self.scope)


def _portee(noeud: dict[str, Any]) -> tuple[str, ...]:
    """Portée d'un token : `$extensions.<espace>.scope`, quel que soit l'espace de noms.

    Une couleur sans portée appartient à la palette de marque et vaut partout ;
    une couleur à portée (nuance dérivée, palette d'illustration) n'est admise
    que dans les dossiers listés.
    """
    portee: list[str] = []
    for espace in (noeud.get("$extensions") or {}).values():
        if isinstance(espace, dict):
            valeur = espace.get("scope")
            if isinstance(valeur, str):
                portee.append(valeur)
            elif isinstance(valeur, list):
                portee.extend(str(v) for v in valeur)
    return tuple(portee)


def charger_palette(tokens: dict[str, Any]) -> list[TokenCouleur]:
    """Relève chaque token de couleur hexadécimal de `tokens.json`, avec sa portée.

    Lève `ValueError` si aucune couleur n'est trouvée : une QA de palette sans
    palette ne mesurerait rien.
    """
    couleurs: list[TokenCouleur] = []

    def descendre(noeud: dict[str, Any], chemin: tuple[str, ...]) -> None:
        if "$value" in noeud:
            valeur = noeud["$value"]
            if isinstance(valeur, str) and valeur.strip().startswith("#"):
                try:
                    hexa = developper_hex(valeur)
                except ValueError:
                    return
                couleurs.append(TokenCouleur(".".join(chemin), hexa, _portee(noeud)))
            return
        for cle, enfant in noeud.items():
            if cle.startswith("$") or not isinstance(enfant, dict):
                continue
            descendre(enfant, chemin + (cle,))

    descendre(tokens.get("color") or {}, ())
    if not couleurs:
        raise ValueError("aucune couleur hexadécimale trouvée sous « color » dans tokens.json")
    return couleurs


# Collecteur de textes visibles, exécuté dans la page par les scripts de QA.
# Il ne juge rien : il relève des valeurs CSS calculées, y compris la pile des
# fonds des ancêtres, et rend la main à Python, qui tranche. Chaque script
# l'insère dans son propre `page.evaluate` et lui passe ses filtres.
#
# Signature JS : (racine, cadre, options) -> { liste, total }
#   racine  : élément dont on parcourt les descendants
#   cadre   : DOMRect hors de laquelle un texte est ignoré, ou null
#   options : { ignorer(el), extra(el), max }
JS_TEXTES = """
((racine, cadre, options) => {
  const opts = options || {};
  const max = opts.max || 1000;
  const ignorer = opts.ignorer || (() => false);
  const extra = opts.extra || (() => ({}));
  const cls = el => (el.getAttribute('class') || '').slice(0, 40);
  const visible = el => el.checkVisibility
    ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })
    : (() => { const cs = getComputedStyle(el);
               return cs.display !== 'none' && cs.visibility !== 'hidden'
                      && parseFloat(cs.opacity) > 0; })();

  const liste = [];
  let total = 0;
  racine.querySelectorAll('*').forEach(el => {
    if (ignorer(el)) return;
    const propre = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    if (!propre || !visible(el)) return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (cadre && (r.right < cadre.left || r.left > cadre.right
                  || r.bottom < cadre.top || r.top > cadre.bottom)) return;

    total += 1;
    if (liste.length >= max) return;

    const cs = getComputedStyle(el);
    const fonds = [];
    let n = el;
    for (let profondeur = 0; n && profondeur < 40; n = n.parentElement, profondeur++) {
      const ncs = getComputedStyle(n);
      fonds.push({ c: ncs.backgroundColor, i: ncs.backgroundImage });
      if (n === document.documentElement) break;
    }

    liste.push(Object.assign({
      cls: cls(el),
      tag: el.tagName,
      texte: (el.textContent || '').trim().slice(0, 40),
      fs: Math.round(parseFloat(cs.fontSize) * 10) / 10,
      poids: parseInt(cs.fontWeight, 10) || 400,
      police: cs.fontFamily,
      couleur: cs.color,
      fonds: fonds,
      gradient: cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text',
    }, extra(el)));
  });

  return { liste: liste, total: total };
})
"""
