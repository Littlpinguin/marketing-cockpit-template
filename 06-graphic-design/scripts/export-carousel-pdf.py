#!/usr/bin/env python3
"""Exporte un carrousel HTML standalone vers un PDF multipage via Playwright.

Le HTML contient une section `.slide` par page + `@page { size: 1080px 1350px;
margin: 0 }` (c'est ce que produit `build-carousel.py`, et ce qu'attend la skill
`carousel` pour un carrousel écrit à la main).

Texte en dégradé : Chromium rend `background-clip:text` comme un rectangle plein
à l'impression PDF. Contournement : chaque élément `.grad / .hl / .num` (ou les
sélecteurs passés par --selecteurs) est **rastérisé par screenshot Playwright**
(pixel près, dégradé et police réels) puis remplacé par un `<img>` aux dimensions
identiques avant `page.pdf()`. La mise en page est préservée.

Usage:
    python3 06-graphic-design/scripts/export-carousel-pdf.py <html> <out.pdf>

Prérequis : pip install playwright && playwright install chromium
"""
import argparse
import base64
import pathlib
import sys

GRADIENT_SELECTORS = ".grad, .hl, .num"

RASTERIZE_JS = """
(el, p) => {
  const cs = getComputedStyle(el);
  const img = document.createElement('img');
  img.src = p.dataUrl;
  // Le PNG capturé inclut une marge verticale (padT/padB) pour ne PAS couper les
  // jambages (g, y, p) ni les accents. Marges négatives = mise en page inchangée,
  // mais les pixels du jambage débordent (overflow visible) et s'affichent.
  img.style.width = p.w + 'px';
  img.style.height = p.h + 'px';
  img.style.marginTop = (-p.padT) + 'px';
  img.style.marginBottom = (-p.padB) + 'px';
  img.style.display = cs.display.startsWith('inline') ? 'inline-block' : 'block';
  img.style.verticalAlign = 'baseline';
  img.setAttribute('data-rasterized', '1');
  el.replaceWith(img);
}
"""


# Pendant la capture d'un texte en dégradé : neutraliser TOUT ce qui est peint
# derrière le bloc (fond de la slide + grain ::before), puis capturer avec
# `omit_background` → seuls les glyphes du dégradé restent opaques, le reste du
# PNG est transparent. Réinséré sur la slide intacte, le grain de la slide
# transparaît autour des lettres : pas de rectangle parasite. (Conserver le grain
# dans le screenshot le doublait → boîte plus sombre.) La forme de titre sombre
# reste peinte : le dégradé capturé sur la forme se réaligne exactement sur elle.
CLEAN_CSS = (".rzclean .glow{display:none!important}"
             ".rzclean{background:transparent!important}"
             ".rzclean::before{display:none!important}")


def rasterize_gradients(page, selecteurs: str = GRADIENT_SELECTORS):
    """Remplace chaque texte en dégradé par son screenshot (rendu PDF correct).

    Capture une zone ÉLARGIE vers le bas pour inclure les jambages (g, y, p) et
    accents : sinon Chromium clippe la bounding-box au line-height et tronque le
    bas des lettres descendantes. Réinsertion en marges négatives → mise en page
    strictement inchangée, jambages visibles."""
    page.add_style_tag(content=CLEAN_CSS)
    handles = page.query_selector_all(selecteurs)
    count = 0
    for el in handles:
        box = el.bounding_box()
        if not box or box["width"] < 1 or box["height"] < 1:
            continue
        # Padding-bas TEMPORAIRE : agrandit la box de l'élément vers le bas pour
        # que le jambage ne soit plus collé au bord et ne soit pas clippé par le
        # screenshot (element.screenshot capture la border-box, indépendamment
        # du scroll, contrairement à page.screenshot(clip)).
        pad_b = max(10, round(box["height"] * 0.32))
        el.evaluate(
            "(e, pb) => { e.dataset._pb = e.style.paddingBottom || '';"
            " e.style.paddingBottom = pb + 'px';"
            " const s = e.closest('.slide'); if (s) s.classList.add('rzclean'); }",
            pad_b)
        box2 = el.bounding_box()           # box agrandie (inclut le padding-bas)
        png = el.screenshot(type="png", omit_background=True)
        el.evaluate(
            "e => { e.style.paddingBottom = e.dataset._pb || '';"
            " const s = e.closest('.slide'); if (s) s.classList.remove('rzclean'); }")
        data_url = "data:image/png;base64," + base64.b64encode(png).decode()
        el.evaluate(RASTERIZE_JS, {"dataUrl": data_url, "w": box2["width"],
                                   "h": box2["height"], "padT": 0, "padB": pad_b})
        count += 1
    return count


def main():
    ap = argparse.ArgumentParser(description="Exporte un carrousel HTML en PDF multipage.")
    ap.add_argument("html", type=pathlib.Path)
    ap.add_argument("pdf", type=pathlib.Path)
    ap.add_argument("--width", default="1080px")
    ap.add_argument("--height", default="1350px")
    ap.add_argument("--selecteurs", default=GRADIENT_SELECTORS,
                    help=f"éléments en dégradé à rastériser (défaut : « {GRADIENT_SELECTORS} »)")
    ap.add_argument("--wait-ms", type=int, default=1500,
                    help="délai après networkidle pour le rendu des polices locales.")
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Playwright n'est pas installé. Lancer :\n"
                 "  pip install playwright && playwright install chromium")

    html_path = args.html.resolve()
    if not html_path.exists():
        sys.exit(f"ERREUR : {html_path} introuvable.")
    args.pdf.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(
            viewport={"width": int(args.width.rstrip("px")),
                      "height": int(args.height.rstrip("px"))},
            device_scale_factor=3,
        )
        page = ctx.new_page()
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(args.wait_ms)

        n = rasterize_gradients(page, args.selecteurs)
        page.wait_for_timeout(300)

        page.pdf(
            path=str(args.pdf),
            width=args.width,
            height=args.height,
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    print(f"OK → {args.pdf}  ({n} éléments en dégradé rastérisés)")


if __name__ == "__main__":
    main()
