#!/usr/bin/env python3
# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), scripts/shots.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""
Playwright capture — screenshot chosen slides of a deck with all entry
animations neutralised, for fast visual verification.

Each requested slide is activated (the `.slide.active` pattern the deck
uses for navigation), then its `.reveal` elements and `[data-stagger]`
children are forced to their final visible state — so the PNG shows the
slide as the audience sees it once motion has settled, not mid-fade.

Brand-agnostic: relies only on the structural conventions every deck
built from 06-graphic-design/presentations/templates/base.html shares (`.slide`, `.stage-frame`,
`.reveal`, `[data-stagger]`).

Usage:
    python 06-graphic-design/presentations/scripts/shots.py 06-graphic-design/presentations/decks/your-deck.html            # all slides
    python 06-graphic-design/presentations/scripts/shots.py 06-graphic-design/presentations/decks/your-deck.html 3 8 18     # slides 3, 8, 18

Output:
    /tmp/slide-NN.png  (one PNG per captured slide, NN = 1-based index)

Requires:
    pip install playwright
    playwright install chromium
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.stderr.write(
        "Playwright is not installed. Run:\n"
        "  pip install playwright && playwright install chromium\n"
    )
    sys.exit(2)


OUT_DIR = Path("/tmp")

# Force every animated element to its resting, fully-visible state. The deck
# animates entry by starting `.reveal` / `[data-stagger] > *` at opacity:0 and
# transitioning them in with staggered delays; we override that inline so the
# screenshot never catches a half-played transition.
NEUTRALISE_JS = """() => {
    const els = document.querySelectorAll('.reveal, [data-stagger] > *');
    els.forEach(el => {
        el.style.setProperty('opacity', '1', 'important');
        el.style.setProperty('transform', 'none', 'important');
        el.style.setProperty('transition', 'none', 'important');
        el.style.setProperty('animation', 'none', 'important');
    });
}"""

ACTIVATE_JS = """(idx) => {
    const slides = document.querySelectorAll('.slide');
    slides.forEach(s => s.classList.remove('active'));
    slides[idx].classList.add('active');
}"""


def url_for(path: Path) -> str:
    abs_path = path.resolve()
    if not abs_path.exists():
        sys.stderr.write(f"file not found: {abs_path}\n")
        sys.exit(2)
    return abs_path.as_uri()


def parse_viewport(s: str) -> dict:
    try:
        w, h = s.lower().split("x")
        return {"width": int(w), "height": int(h)}
    except Exception:
        sys.stderr.write(f"invalid viewport: {s} (expected WIDTHxHEIGHT, e.g. 1920x1080)\n")
        sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deck", help="path to the presentation HTML file")
    parser.add_argument(
        "slides",
        nargs="*",
        type=int,
        help="1-based slide numbers to capture (default: all slides)",
    )
    parser.add_argument("--viewport", default="1920x1080", help="viewport size (default: 1920x1080)")
    args = parser.parse_args()

    deck_path = Path(args.deck)
    viewport = parse_viewport(args.viewport)
    url = url_for(deck_path)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"shots · deck     {deck_path}")
    print(f"shots · viewport {viewport['width']}x{viewport['height']}")
    print(f"shots · url      {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport=viewport, reduced_motion="reduce")
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle")
        page.wait_for_timeout(800)

        total = page.evaluate("document.querySelectorAll('.slide').length")
        if not total:
            print("error · no .slide elements found")
            browser.close()
            return 2

        # Resolve which slides to capture: requested set, or all.
        if args.slides:
            wanted = []
            for n in args.slides:
                if n < 1 or n > total:
                    print(f"shots · skip slide {n} (out of range 1..{total})")
                    continue
                if n not in wanted:
                    wanted.append(n)
            if not wanted:
                print("error · no valid slides requested")
                browser.close()
                return 2
        else:
            wanted = list(range(1, total + 1))

        print(f"shots · {total} slides detected, capturing {len(wanted)}\n")

        # Locate the rendered frame; fall back to the page if absent.
        frame = page.locator("#stage-frame")
        has_frame = frame.count() > 0

        for n in wanted:
            page.evaluate(ACTIVATE_JS, n - 1)
            page.evaluate(NEUTRALISE_JS)
            page.wait_for_timeout(200)

            out_path = OUT_DIR / f"slide-{n:02d}.png"
            if has_frame:
                frame.screenshot(path=str(out_path))
            else:
                page.screenshot(path=str(out_path))
            print(f"  slide {n:02d} · {out_path}")

        browser.close()

    print(f"\nshots · done · {len(wanted)} PNG(s) in {OUT_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
