#!/usr/bin/env python3
"""QA Playwright des decks HTML : le script de QA des présentations.

Contrôle d'abord, sans navigateur, la **parité du moteur** : le deck embarque-t-il
toutes les features du moteur de slides (docs/engine-parity.md) ? Puis, slide par
slide, ramené au cadre natif de la slide (1920x1080 par défaut, voir --frame) :
  1. débordement hors du cadre (overflow)
  2. zone de sécurité du chrome bas (gap ≥ 16 px)
  3. plancher typographique sur tout texte visible : 18 px pour le contenu
     (--min-font), 12 px pour le texte du chrome (--min-font-chrome), qui porte
     le registre des repères ; avertissement sous 24 px pour le corps
  4. police calculée : une famille de la marque. Les familles admises se lisent,
     dans l'ordre, dans --police, dans les tokens `font.*` de
     `01-brand/tokens.json`, ou à défaut dans les variables `--font-display` et
     `--font-body` du deck lui-même. Une monospace est admise sans réserve dans
     le chrome, sur `code`, `pre`, `kbd` et sur la classe exacte `mono` ;
     ailleurs elle sort en avertissement, parce que le registre mono reste un
     choix de direction artistique à confirmer. Toute autre famille est une
     erreur.
  5. contraste texte/fond WCAG 2.x (4,5:1, ou 3:1 au-delà de 24 px ou en gras),
     sur tout texte visible, chrome compris
  6. folio présent et croissant (`.nav-num` du moteur, `.tag-folio` du
     catalogue, --folio pour un autre sélecteur, --sans-folio pour un format
     qui n'en porte pas, comme un carrousel)

Les géométries sont mesurées à l'écran puis divisées par le facteur du
`transform: scale()` qui amène le cadre natif à la fenêtre. Les tailles de police
calculées ne sont pas affectées par ce transform : elles sont lues telles quelles.

Usage (depuis 06-graphic-design/presentations/) :
    python scripts/qa.py decks/<deck>.html [options]

Options : --viewport WxH, --frame WxH, --lang CODE, --min-font N,
--min-font-chrome N, --police FAMILLE (répétable), --tokens CHEMIN,
--folio SELECTEUR, --sans-folio, --no-engine-check, --format text|json,
--screenshots [DOSSIER], --bleed SELECTEUR (répétable), --attente MS. Un rapport
partiel se signale : au-delà de 400 textes ou de 20 débordements par slide, un
avertissement `[troncature]` dit combien d'éléments n'ont pas été audités, et
les constats écartés par le plafond de lisibilité (8 par slide et par famille)
sont résumés par une ligne de niveau `resume`, qui ne compte ni dans les erreurs
ni dans les avertissements. Le JSON porte en plus `errors_total` et
`warnings_total`, les volumes avant plafonnement.

Succès : « All slides clean », code 0. Erreurs : code 1. Les avertissements ne
font pas échouer la QA, ils sont listés. Usage incorrect ou deck illisible : 2.

Le calcul (couleurs, luminance, contraste, police), la lecture du viewport et de
tokens.json, et le collecteur JavaScript des textes visibles vivent dans le module
partagé `06-graphic-design/scripts/qa_common.py`, réutilisé par
`06-graphic-design/scripts/qa-visuel.py` (carrousels et visuels composés).

Prérequis : pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.stderr.write(
        "Playwright n'est pas installé. Lancer :\n"
        "  pip install playwright && playwright install chromium\n"
    )
    sys.exit(2)

_ICI = Path(__file__).resolve()
RACINE = _ICI.parents[3]
_COMMUN = _ICI.parents[2] / "scripts" / "qa_common.py"
_spec = importlib.util.spec_from_file_location("qa_common", _COMMUN)
qa_common = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qa_common)


SAFE_GAP_PX = 16         # écart minimal entre le bas du contenu et le chrome bas
MIN_FONT_PX = 18         # plancher typographique du contenu (lisibilité en projection)
MIN_FONT_CHROME_PX = 12  # plancher du texte du chrome (registre des repères)
CORPS_CONFORT_PX = 24    # sous ce corps, un texte de contenu passe en avertissement
MAX_PAR_SLIDE = 8        # constats listés par slide et par famille
MAX_TEXTES = 400         # éléments de texte remontés par slide (le reste est signalé)
MAX_OVERFLOWS = 20       # débordements remontés par slide (le reste est signalé)
FOLIO_DEFAUT = ".nav-num, .tag-folio"   # moteur (base.html) et catalogue
TMP_DIR = "/tmp/slides-qa"

# Couches décoratives volontairement pleine page ou débordantes, et annotations
# hors deck : la QA les ignore, elles et leurs descendants, sinon elles remontent
# en faux positifs. Convention pour les nouveaux decks : poser `data-bleed` sur
# le calque, ou passer son sélecteur par --bleed.
BLEED = [
    "[data-bleed]", ".bleed",
    ".aurora", ".dust-grid", ".legend",
    ".gridlines", ".grid-overlay", ".plate-bg", ".edge-gradient", ".paper",
]

TITRES = {"H1", "H2", "H3", "H4"}

# ---------------------------------------------------------------------------
# PARITÉ DU MOTEUR — marqueurs canoniques du moteur de slides.
# Miroir exécutable de docs/engine-parity.md : chaque deck, le starter
# (templates/base.html) et le catalogue (_examples/deck-catalogue/catalogue.html)
# embarquent le moteur complet. Un marqueur absent = une feature manquante
# (plein écran, nav-peek, folios auto, export PDF, hooks de pattern...).
# Tenir cette liste en phase avec docs/engine-parity.md.
# ---------------------------------------------------------------------------
ENGINE_MARKERS = {
    "body.presenting": "mode présentation plein écran (touche F, nav masquée)",
    "nav-peek": "réapparition de la nav près du bas de l'écran en mode présentation",
    "requestFullscreen": "câblage de la Fullscreen API (touche F / bouton)",
    "SLIDE_COUNT": "folios auto-numérotés pilotés par le nombre de slides",
    "printing-pdf": "mode d'impression de l'export PDF (touche P / bouton)",
    "window.print": "déclencheur de l'export PDF",
    "--brand-pattern": "hooks de pattern de marque (.motif / .texture / .corner)",
    "overview": "panneau de vue d'ensemble (touche O)",
}


def verifier_parite_moteur(deck: Path) -> list[str]:
    """Rend la liste des marqueurs du moteur absents du deck (vide = moteur complet)."""
    html = deck.read_text(encoding="utf-8", errors="replace")
    return [m for m in ENGINE_MARKERS if m not in html]


# Collecteur exécuté dans la page : il ne juge rien, il relève des valeurs CSS
# calculées et les rend au Python, qui tranche.
COLLECTEUR = """
(args) => {
  const [idx, selecteur, bleed, cadreNatif, maxTextes, maxOver, selFolio] = args;
  const slide = document.querySelectorAll(selecteur)[idx];
  const cadreEl = document.getElementById('stage-frame') || slide;
  const fb = cadreEl.getBoundingClientRect();

  // Le cadre natif (1920x1080 par défaut) est amené à l'écran par un
  // `transform: scale()`. getBoundingClientRect rend des pixels écran : les
  // diviser par ce facteur les ramène en pixels natifs. En revanche la taille de
  // police calculée n'est PAS affectée par le transform : ne jamais la diviser.
  const scale = (fb.width / cadreNatif) || 1;

  const ignore = el => bleed.some(s => { try { return el.closest(s); } catch (e) { return false; } });
  const cls = el => (el.getAttribute('class') || '').slice(0, 40);

  // 1. débordements
  const over = [];
  slide.querySelectorAll('*').forEach(el => {
    if (ignore(el) || el.closest('.chrome')) return;
    const r = el.getBoundingClientRect();
    if (r.width < 8 * scale || r.height < 8 * scale) return;
    const o = { R: (r.right - fb.right) / scale, B: (r.bottom - fb.bottom) / scale,
                L: (fb.left - r.left) / scale, T: (fb.top - r.top) / scale };
    if (o.R > 2 || o.B > 2 || o.L > 2 || o.T > 2)
      over.push({ cls: cls(el), R: Math.round(o.R), B: Math.round(o.B),
                  L: Math.round(o.L), T: Math.round(o.T) });
  });
  over.sort((a, b) => Math.max(b.R, b.B, b.L, b.T) - Math.max(a.R, a.B, a.L, a.T));

  // 2. zone de sécurité du chrome bas
  let gap = null, plusBas = '';
  const chromeBas = slide.querySelector('.chrome-row.bottom');
  if (chromeBas) {
    const chromeT = (chromeBas.getBoundingClientRect().top - fb.top) / scale;
    let bas = 0;
    slide.querySelectorAll('*').forEach(el => {
      if (ignore(el) || el.closest('.chrome')) return;
      const r = el.getBoundingClientRect();
      if (r.width < 8 * scale || r.height < 4 * scale) return;
      const y = (r.bottom - fb.top) / scale;
      if (y > bas) { bas = y; plusBas = cls(el); }
    });
    gap = Math.round(chromeT - bas);
  }

  // 3 à 5. texte visible : corps, police, couleurs
  // Le relevé est celui du module partagé (`qa_common.JS_TEXTES`), inséré ici :
  // il ne juge rien, il remonte les valeurs CSS brutes, y compris les
  // `background-image` des ancêtres, et Python tranche. Le registre du chrome
  // est propre aux decks : il est ajouté par le rappel `extra`.
  const textes = __COLLECTE_TEXTES__(slide, fb, {
    ignorer: ignore,
    max: maxTextes,
    extra: el => ({ chrome: !!el.closest('.chrome') }),
  });

  // 6. folio
  const folio = selFolio ? slide.querySelector(selFolio) : null;
  const folio_txt = folio ? (folio.textContent || '').trim() : null;

  return { over: over.slice(0, maxOver), over_total: over.length,
           gap, plus_bas: plusBas,
           textes: textes.liste, textes_total: textes.total,
           folio: folio_txt, scale: Math.round(scale * 1000) / 1000 };
}
""".replace("__COLLECTE_TEXTES__", qa_common.JS_TEXTES)

# Familles déclarées par le deck lui-même, lues sur :root. Repli quand ni
# --police ni tokens.json ne disent quelle police attendre.
VARIABLES_POLICE = """
() => {
  const cs = getComputedStyle(document.documentElement);
  return ['--font-display', '--font-body'].map(v => cs.getPropertyValue(v).trim()).filter(Boolean);
}
"""


def url_du_deck(chemin: Path) -> str:
    absolu = chemin.resolve()
    if not absolu.exists():
        sys.stderr.write(f"fichier introuvable : {absolu}\n")
        sys.exit(2)
    return absolu.as_uri()


def lire_viewport(valeur: str) -> dict:
    """Lecture partagée, avec la sortie en 2 propre à un usage incorrect du script."""
    try:
        return qa_common.lire_viewport(valeur)
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(2)


def premier_entier(texte: str | None) -> int | None:
    if not texte:
        return None
    chiffres = "".join(c if c.isdigit() else " " for c in texte).split()
    return int(chiffres[0]) if chiffres else None


def familles_depuis_tokens(chemin: Path) -> list[str]:
    """Familles `font.*` de tokens.json, ou liste vide si le fichier manque."""
    if not chemin.exists():
        return []
    try:
        return qa_common.familles_de_marque(qa_common.lire_tokens(chemin))
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(2)


def familles_depuis_variables(valeurs: list[str]) -> list[str]:
    """Première famille de chaque variable `--font-*` du deck, hors familles génériques."""
    familles = []
    for valeur in valeurs:
        famille = qa_common.premiere_famille(valeur)
        if famille and famille.lower() not in qa_common.FAMILLES_GENERIQUES and famille not in familles:
            familles.append(famille)
    return familles


def mono_autorise(texte: dict) -> bool:
    """La monospace n'est admise sans réserve que sur le registre technique.

    Trois registres la légitiment : les balises `code`, `pre`, `kbd` ; la classe
    exacte `mono` en tant que token de classe, donc `.monogram` et `.monochrome`
    ne passent pas ; et le chrome, dont le registre mono est déclaré par le
    système de slides lui-même (`--font-mono`, méta-label, folio, signature).
    Partout ailleurs, une monospace sort en avertissement.
    """
    return (
        texte["chrome"]
        or texte["tag"] in ("CODE", "PRE", "KBD")
        or "mono" in texte["cls"].split()
    )


def auditer_textes(brut: dict, min_font: int, min_font_chrome: int,
                   familles: list[str]) -> tuple[list[dict], list[str]]:
    """Rend les constats de typographie, police et contraste, plus les textes en gradient.

    `familles` vide : la police n'est pas contrôlée (le rapport le dit une fois).
    """
    constats: list[dict] = []
    gradients: list[str] = []

    for texte in brut["textes"]:
        cible = f".{texte['cls']}" if texte["cls"] else texte["tag"].lower()
        taille, gras = texte["fs"], texte["poids"] >= 700
        plancher = min_font_chrome if texte["chrome"] else min_font

        if taille < plancher:
            registre = " du chrome" if texte["chrome"] else ""
            constats.append({
                "niveau": "erreur", "type": "plancher-typo",
                "message": f"corps {taille}px sous le plancher{registre} {plancher}px sur {cible}",
            })
        elif not texte["chrome"] and taille < CORPS_CONFORT_PX and texte["tag"] not in TITRES:
            constats.append({
                "niveau": "avertissement", "type": "corps-serre",
                "message": f"corps {taille}px sous le confort {CORPS_CONFORT_PX}px sur {cible}",
            })

        if familles and not qa_common.police_conforme(texte["police"], familles,
                                                      mono_autorise=mono_autorise(texte)):
            famille = qa_common.premiere_famille(texte["police"])
            if qa_common.est_monospace(famille):
                # Le registre mono est déclaré par le système de slides (`--font-mono`)
                # et la doctrine le légitime pour les repères du chrome. Hors chrome,
                # hors `code`, `pre` et `kbd`, il reste un choix de direction
                # artistique à confirmer, pas une sortie de charte : avertissement,
                # jamais erreur.
                constats.append({
                    "niveau": "avertissement", "type": "police",
                    "message": f"registre mono « {famille} » hors chrome et hors code sur {cible}",
                })
            else:
                constats.append({
                    "niveau": "erreur", "type": "police",
                    "message": f"police « {famille} » au lieu de {' / '.join(familles)} sur {cible}",
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

    return constats, gradients


def auditer_troncatures(brut: dict) -> list[dict]:
    """Signale ce que le collecteur a laissé de côté : un rapport partiel se dit."""
    constats = []
    reste_textes = brut["textes_total"] - len(brut["textes"])
    if reste_textes > 0:
        constats.append({
            "niveau": "avertissement", "type": "troncature",
            "message": (
                f"{reste_textes} éléments de texte non audités sur cette slide "
                f"({brut['textes_total']} relevés, {len(brut['textes'])} remontés)"
            ),
        })
    reste_over = brut["over_total"] - len(brut["over"])
    if reste_over > 0:
        constats.append({
            "niveau": "avertissement", "type": "troncature",
            "message": (
                f"{reste_over} débordements non listés sur cette slide "
                f"({brut['over_total']} relevés, {len(brut['over'])} remontés)"
            ),
        })
    return constats


def auditer_slide(brut: dict, min_font: int, min_font_chrome: int,
                  familles: list[str]) -> tuple[list[dict], list[str]]:
    constats = [
        {
            "niveau": "erreur", "type": "overflow",
            "message": f"débordement .{o['cls']} R={o['R']} B={o['B']} L={o['L']} T={o['T']}",
        }
        for o in brut["over"]
    ]

    if brut["gap"] is not None and brut["gap"] < SAFE_GAP_PX:
        constats.append({
            "niveau": "erreur", "type": "chrome-gap",
            "message": (
                f"zone de sécurité du chrome : {brut['gap']}px au lieu de ≥ {SAFE_GAP_PX}px, "
                f"élément le plus bas .{brut['plus_bas']}"
            ),
        })

    textes, gradients = auditer_textes(brut, min_font, min_font_chrome, familles)
    return constats + textes + auditer_troncatures(brut), gradients


def auditer_folios(folios: list[str | None]) -> list[dict]:
    constats = []
    numeros = []
    for index, brut in enumerate(folios, start=1):
        numero = premier_entier(brut)
        if numero is None:
            constats.append({
                "slide": index, "niveau": "erreur", "type": "folio",
                "message": "folio absent ou illisible",
            })
        numeros.append(numero)

    precedent = None
    for index, numero in enumerate(numeros, start=1):
        if numero is None:
            continue
        if precedent is not None and numero <= precedent:
            constats.append({
                "slide": index, "niveau": "erreur", "type": "folio",
                "message": f"folio {numero} non croissant (slide précédente : {precedent})",
            })
        precedent = numero
    return constats


def compter(constats: list[dict], niveau: str) -> int:
    """Compte les constats d'un niveau donné, en ignorant les lignes de résumé."""
    return sum(1 for c in constats if c["niveau"] == niveau)


def limiter(constats: list[dict]) -> list[dict]:
    """Garde au plus MAX_PAR_SLIDE constats par famille, pour un rapport lisible.

    Ce qui dépasse est résumé par une ligne de niveau `resume`, qui porte le
    nombre d'éléments écartés. Ce niveau n'est ni une erreur ni un avertissement :
    une ligne de résumé ne doit jamais gonfler les compteurs du rapport, sans quoi
    un deck paraît plus fautif qu'il ne l'est.
    """
    gardes, comptes, ecartes = [], {}, {}
    for constat in constats:
        famille = constat["type"]
        comptes[famille] = comptes.get(famille, 0) + 1
        if comptes[famille] <= MAX_PAR_SLIDE:
            gardes.append(constat)
        else:
            ecartes[famille] = ecartes.get(famille, 0) + 1

    for famille, nombre in ecartes.items():
        gardes.append({
            "niveau": "resume", "type": famille,
            "message": f"… {nombre} autres constats « {famille} » non listés sur cette slide",
        })
    return gardes


def collecter(page, selecteur: str, total: int, bleed: list[str], cadre_natif: int,
              attente: int, dossier_shots: Path | None, sel_folio: str | None) -> list[dict]:
    bruts = []
    for index in range(total):
        page.evaluate(
            """([sel, i]) => {
                const s = document.querySelectorAll(sel);
                s.forEach(e => e.classList.remove('active'));
                s[i].classList.add('active');
            }""",
            [selecteur, index],
        )
        page.wait_for_timeout(attente)
        if dossier_shots:
            cadre = page.locator("#stage-frame")
            cible = cadre if cadre.count() else page.locator(selecteur).nth(index)
            cible.screenshot(path=str(dossier_shots / f"slide-{index + 1:02d}.png"))
        bruts.append(page.evaluate(
            COLLECTEUR,
            [index, selecteur, bleed, cadre_natif, MAX_TEXTES, MAX_OVERFLOWS, sel_folio],
        ))
    return bruts


def rapport_texte(deck: Path, viewport: dict, cadre: str, selecteur: str, par_slide: list[dict],
                  gradients: list[str], erreurs: int, avertissements: int,
                  erreurs_totales: int, avertissements_totaux: int, familles: list[str],
                  source_familles: str) -> None:
    print(f"qa  · deck     {deck}")
    print(f"qa  · viewport {viewport['width']}x{viewport['height']} · cadre natif {cadre}")
    print(f"qa  · police   {' / '.join(familles) or 'non contrôlée'}"
          + (f" ({source_familles})" if familles else ""))
    print(f"qa  · {len(par_slide)} slides détectées (sélecteur {selecteur})\n")

    for entree in par_slide:
        constats = entree["constats"]
        if not constats:
            print(f"  slide {entree['slide']:02d} · ok")
            continue
        nb_err = compter(constats, "erreur")
        nb_avt = compter(constats, "avertissement")
        print(f"  slide {entree['slide']:02d} · {nb_err} erreur(s), {nb_avt} avertissement(s)")
        for constat in constats:
            marque = {"erreur": "!", "avertissement": "~"}.get(constat["niveau"], "+")
            print(f"    {marque} [{constat['type']}] {constat['message']}")

    if gradients:
        print("\n  texte en background-clip: text (contraste non jugé, à relire à l'œil) :")
        for entree in gradients:
            print(f"    · {entree}")

    print()
    if erreurs:
        print(f"FAIL · {erreurs} erreur(s), {avertissements} avertissement(s)")
    else:
        print(f"All slides clean · {len(par_slide)} / {len(par_slide)}"
              + (f" · {avertissements} avertissement(s)" if avertissements else ""))
    if (erreurs_totales, avertissements_totaux) != (erreurs, avertissements):
        print(f"     · avant plafonnement à {MAX_PAR_SLIDE} par slide et par famille : "
              f"{erreurs_totales} erreur(s), {avertissements_totaux} avertissement(s)")


def construire_parseur() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QA Playwright d'un deck HTML : parité du moteur, overflow, chrome, "
                    "typo, police, contraste, folio.",
    )
    parser.add_argument("deck", help="chemin du fichier HTML du deck")
    parser.add_argument("--viewport", default="1920x1080",
                        help="taille de la fenêtre du navigateur (défaut : 1920x1080)")
    parser.add_argument("--frame", default="1920x1080",
                        help="taille du cadre natif de la slide, avant le transform scale() "
                             "qui l'amène à la fenêtre (défaut : 1920x1080). Les géométries "
                             "mesurées sont ramenées à ce cadre ; les tailles de police, elles, "
                             "ne sont pas affectées par le transform et sont lues telles quelles")
    parser.add_argument("--min-font", type=int, default=MIN_FONT_PX,
                        help=f"plancher typographique du contenu, en px (défaut : {MIN_FONT_PX})")
    parser.add_argument("--min-font-chrome", type=int, default=MIN_FONT_CHROME_PX,
                        help=f"plancher typographique du texte du chrome, en px "
                             f"(défaut : {MIN_FONT_CHROME_PX}). Le chrome porte le registre des "
                             f"repères, plus petit que le contenu, mais il reste soumis au "
                             f"contrôle de contraste comme tout texte visible")
    parser.add_argument("--police", action="append", default=[], metavar="FAMILLE",
                        help="famille de police admise (répétable). Défaut : les familles "
                             "`font.*` de 01-brand/tokens.json, à défaut les variables "
                             "--font-display et --font-body du deck")
    parser.add_argument("--tokens", default=str(RACINE / "01-brand" / "tokens.json"),
                        help="fichier de tokens où lire les familles de police "
                             "(défaut : 01-brand/tokens.json)")
    parser.add_argument("--folio", default=FOLIO_DEFAUT, metavar="SELECTEUR",
                        help=f"sélecteur du folio de chaque slide (défaut : « {FOLIO_DEFAUT} »)")
    parser.add_argument("--sans-folio", action="store_true",
                        help="ne pas contrôler les folios (format qui n'en porte pas, comme un "
                             "carrousel dont la plateforme numérote les pages)")
    parser.add_argument("--no-engine-check", action="store_true",
                        help="sauter le contrôle de parité du moteur (decks hérités seulement, "
                             "voir docs/engine-parity.md ; jamais un régime permanent)")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="forme de la sortie (défaut : text)")
    parser.add_argument("--screenshots", metavar="DOSSIER", nargs="?", const=TMP_DIR,
                        help=f"enregistrer une capture par slide (défaut : {TMP_DIR})")
    parser.add_argument("--bleed", action="append", default=[], metavar="SELECTEUR",
                        help="sélecteur supplémentaire à ignorer (débordement volontaire), répétable")
    parser.add_argument("--lang", metavar="CODE",
                        help="auditer le deck dans cette langue : après chargement, le script "
                             "appelle `window.__setLang(<code>)`, la fonction de bascule exposée "
                             "par les decks bilingues, puis attend --attente. Un deck qui "
                             "n'expose pas cette fonction est audité dans la langue affichée au "
                             "chargement, avec un avertissement [lang]. Un deck bilingue se "
                             "contrôle dans chaque langue, la plus longue étant la plus exposée "
                             "au débordement")
    parser.add_argument("--attente", type=int, default=800,
                        help="attente en ms après activation d'une slide (défaut : 800, "
                             "à monter jusqu'à 2000 si le deck a des stagger longs, et "
                             "jusqu'à 4000 si ses slides portent un autofit JS : celui-ci "
                             "essaie une taille par frame et ne converge pas en 2000 ms, "
                             "ce qui fait mesurer des corps intermédiaires plus petits que "
                             "le rendu final)")
    return parser


def sortir_parite(args, deck: Path, manquants: list[str]) -> int:
    """Échec de parité du moteur : le deck n'embarque pas le moteur complet."""
    if args.format == "json":
        print(json.dumps({
            "summary": {"deck": str(deck), "errors": len(manquants), "warnings": 0,
                        "errors_total": len(manquants), "warnings_total": 0, "slides": None},
            "engine": {"checked": True,
                       "missing": [{"marker": m, "feature": ENGINE_MARKERS[m]} for m in manquants]},
            "slides": [], "gradient_text": [],
        }, ensure_ascii=False, indent=2))
    else:
        print(f"qa  · deck     {deck}")
        print("\nFAIL · parité du moteur : le deck n'embarque pas le moteur de slides complet :")
        for marqueur in manquants:
            print(f"  marqueur absent « {marqueur} » → {ENGINE_MARKERS[marqueur]}")
        print("Porter la ou les features depuis templates/base.html ou "
              "_examples/deck-catalogue/catalogue.html (voir docs/engine-parity.md).")
    return 1


def main() -> int:
    args = construire_parseur().parse_args()

    bleed = BLEED + args.bleed
    deck = Path(args.deck)
    viewport = lire_viewport(args.viewport)
    cadre = lire_viewport(args.frame)
    url = url_du_deck(deck)

    # ---- Parité du moteur (docs/engine-parity.md), avant tout navigateur ----
    if not args.no_engine_check:
        manquants = verifier_parite_moteur(deck)
        if manquants:
            return sortir_parite(args, deck, manquants)

    if args.police:
        familles, source_familles = list(args.police), "--police"
    else:
        familles, source_familles = familles_depuis_tokens(Path(args.tokens)), "tokens.json"

    dossier_shots = Path(args.screenshots) if args.screenshots else None
    if dossier_shots:
        dossier_shots.mkdir(parents=True, exist_ok=True)
    lang_absente = False
    sel_folio = None if args.sans_folio else args.folio

    with sync_playwright() as playwright:
        navigateur = playwright.chromium.launch()
        contexte = navigateur.new_context(viewport=viewport, reduced_motion="reduce")
        page = contexte.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(args.attente)

        # Bascule de langue : les decks bilingues exposent `window.__setLang`.
        # Un deck qui ne l'expose pas est audité dans la langue affichée au
        # chargement, et le rapport le dit.
        if args.lang:
            if page.evaluate("typeof window.__setLang === 'function'"):
                page.evaluate("(l) => window.__setLang(l)", args.lang)
                page.wait_for_timeout(args.attente)
            else:
                lang_absente = True

        if not familles:
            familles = familles_depuis_variables(page.evaluate(VARIABLES_POLICE))
            source_familles = "variables --font-display / --font-body du deck"

        selecteur = next(
            (s for s in (".slide", ".plate") if page.evaluate(f"document.querySelectorAll('{s}').length")),
            None,
        )
        if not selecteur:
            sys.stderr.write("aucun élément .slide ni .plate trouvé dans ce deck\n")
            navigateur.close()
            return 2

        total = page.evaluate(f"document.querySelectorAll('{selecteur}').length")
        bruts = collecter(page, selecteur, total, bleed, cadre["width"], args.attente,
                          dossier_shots, sel_folio)
        navigateur.close()

    par_slide, gradients, avant_plafond = [], [], []
    for index, brut in enumerate(bruts, start=1):
        constats, gradients_slide = auditer_slide(brut, args.min_font, args.min_font_chrome, familles)
        avant_plafond.extend(constats)
        par_slide.append({"slide": index, "constats": limiter(constats)})
        gradients.extend(f"slide {index:02d} · {g}" for g in gradients_slide)

    if sel_folio:
        for constat in auditer_folios([b["folio"] for b in bruts]):
            avant_plafond.append(dict(constat, slide=None))
            par_slide[constat.pop("slide") - 1]["constats"].append(constat)

    constats_deck = []
    if lang_absente:
        constats_deck.append({
            "niveau": "avertissement", "type": "lang",
            "message": (
                f"fonction __setLang absente : le deck a été audité dans la langue "
                f"affichée au chargement, pas en « {args.lang} »"
            ),
        })
    if not familles:
        constats_deck.append({
            "niveau": "avertissement", "type": "police",
            "message": "aucune famille de marque connue (--police, tokens.json ou variables "
                       "--font-display / --font-body) : la police n'est pas contrôlée",
        })
    for constat in reversed(constats_deck):
        avant_plafond.append(constat)
        par_slide[0]["constats"].insert(0, constat)

    tous = [c for entree in par_slide for c in entree["constats"]]
    erreurs = compter(tous, "erreur")
    avertissements = compter(tous, "avertissement")
    erreurs_totales = compter(avant_plafond, "erreur")
    avertissements_totaux = compter(avant_plafond, "avertissement")

    if args.format == "json":
        print(json.dumps({
            "summary": {
                "deck": str(deck), "viewport": args.viewport, "frame": args.frame,
                "selector": selecteur,
                "slides": len(par_slide),
                "fonts": familles, "fonts_source": source_familles if familles else None,
                "errors": erreurs, "warnings": avertissements,
                "errors_total": erreurs_totales, "warnings_total": avertissements_totaux,
            },
            "engine": {"checked": not args.no_engine_check, "missing": []},
            "slides": par_slide,
            "gradient_text": gradients,
        }, ensure_ascii=False, indent=2))
    else:
        rapport_texte(deck, viewport, args.frame, selecteur, par_slide, gradients,
                      erreurs, avertissements, erreurs_totales, avertissements_totaux,
                      familles, source_familles)

    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
