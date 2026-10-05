# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), tests/test_print.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Print pipeline of the starter engine (06-graphic-design/presentations/templates/base.html).

Drives headless Chromium through the hooks that 06-graphic-design/presentations/scripts/export_pdf.py and
`qa.py --with-pdf` call (window.__enablePrintMode, window.__rasterizeGradients)
and checks what the PDF depends on:

- a rasterised gradient text keeps its layout, carries a non-empty image placed
  over its own glyphs, and loses its gradient background (otherwise the PDF
  paints the whole gradient box behind the image);
- every slide carries its own background in print, since the print CSS makes
  the stage frame transparent (otherwise light slides print white);
- restoring after the print gives back the exact screen DOM.

Skipped cleanly when Playwright or Chromium is missing.
Run: python3 -m pytest scripts/tests -q
"""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"
STARTER = ROOT / "templates" / "base.html"
TRANSPARENT = "rgba(0, 0, 0, 0)"


def _chromium_available() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(not _chromium_available(),
                                reason="Playwright or Chromium is not installed on this machine")


@pytest.fixture
def page():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        # The export viewport: the stage is scaled down to leave room for the nav rail
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto(STARTER.as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        yield page
        browser.close()


RECTS = "[...document.querySelectorAll('.gradient-text')].map(e => e.getBoundingClientRect().toJSON())"

# For each rasterised element: its print-time background, and the extent of the
# ink in its overlay image against the extent of its visible characters, both in
# the element's own CSS pixels.
OVERLAYS = """async () => {
  const out = [];
  for (const el of document.querySelectorAll('.gradient-text')) {
    const img = el.querySelector(':scope > img[data-raster-overlay]');
    const item = { rasterized: el.dataset.rasterized === '1', overlay: !!img,
                   background: getComputedStyle(el).backgroundImage, text: el.textContent };
    if (img) {
      await img.decode();
      const c = document.createElement('canvas');
      c.width = img.naturalWidth; c.height = img.naturalHeight;
      const ctx = c.getContext('2d');
      ctx.drawImage(img, 0, 0);
      const px = ctx.getImageData(0, 0, c.width, c.height).data;
      let min = Infinity, max = -Infinity, ink = 0;
      for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) {
        if (px[(y * c.width + x) * 4 + 3] > 40) { ink++; min = Math.min(min, x); max = Math.max(max, x); }
      }
      const k = el.getBoundingClientRect().width / el.offsetWidth;
      const perPx = img.naturalWidth / img.getBoundingClientRect().width * k;
      const box = img.getBoundingClientRect(), own = el.getBoundingClientRect();
      const r = document.createRange();
      let left = Infinity, right = -Infinity;
      const walk = n => n.childNodes.forEach(ch => {
        if (ch.nodeType === 1) return walk(ch);
        if (ch.nodeType !== 3) return;
        for (let i = 0; i < ch.textContent.length; i++) {
          if (/\\s/.test(ch.textContent[i])) continue;
          r.setStart(ch, i); r.setEnd(ch, i + 1);
          const b = r.getBoundingClientRect();
          if (b.width) { left = Math.min(left, b.left); right = Math.max(right, b.right); }
        }
      });
      walk(el);
      Object.assign(item, {
        ink,
        inkLeft: min / perPx + (box.left - own.left) / k, inkRight: (max + 1) / perPx + (box.left - own.left) / k,
        textLeft: (left - own.left) / k, textRight: (right - own.left) / k,
        fontSize: parseFloat(getComputedStyle(el).fontSize),
      });
    }
    out.push(item);
  }
  return out;
}"""


def test_rasterised_gradient_text_has_no_background_box_and_keeps_its_place(page):
    before = page.evaluate(RECTS)
    assert before, "the starter should carry gradient text"
    page.evaluate("window.__enablePrintMode(); window.__rasterizeGradients()")
    assert page.evaluate(RECTS) == before, "rasterising must not move the layout"
    page.emulate_media(media="print")
    for item in page.evaluate(OVERLAYS):
        assert item["rasterized"] and item["overlay"], item["text"]
        # The gradient + background-clip: text would print as a solid box behind the image
        assert item["background"] == "none", item["text"]
        assert item["ink"] > 0, f"blank overlay for {item['text']!r}"
        # The glyphs are drawn where the text is: not pushed by collapsed spaces,
        # not widened by a nested span drawn at the parent's size
        tolerance = 0.12 * item["fontSize"]
        assert item["inkLeft"] >= item["textLeft"] - tolerance, item
        assert item["inkRight"] <= item["textRight"] + tolerance, item
        assert item["inkRight"] - item["inkLeft"] >= 0.75 * (item["textRight"] - item["textLeft"]), item


def test_every_slide_prints_its_own_background(page):
    page.evaluate("window.__enablePrintMode()")
    page.emulate_media(media="print")
    state = page.evaluate("""() => {
      const probe = document.createElement('div');
      probe.style.background = 'var(--brand-neutral-light)';
      document.body.appendChild(probe);
      const light = getComputedStyle(probe).backgroundColor;
      probe.remove();
      return {
        frame: getComputedStyle(document.getElementById('stage-frame')).backgroundColor,
        light,
        slides: [...document.querySelectorAll('.slide')].map(s => ({
          classes: s.className, background: getComputedStyle(s).backgroundColor })),
      };
    }""")
    # The print CSS hands the background over to the slides
    assert state["frame"] == TRANSPARENT
    for slide in state["slides"]:
        assert slide["background"] != TRANSPARENT, slide
        if not any(v in slide["classes"].split() for v in ("dark", "soft", "tint", "cream")):
            assert slide["background"] == state["light"], slide


def test_restore_gives_back_the_screen_dom(page):
    before = page.evaluate("document.getElementById('stage-frame').outerHTML")
    page.evaluate("window.__enablePrintMode(); window.__rasterizeGradients()")
    assert page.evaluate("document.querySelectorAll('img[data-raster-overlay]').length") > 0
    page.evaluate("window.__restoreRaster()")
    assert page.evaluate("document.getElementById('stage-frame').outerHTML") == before
    assert "printing-pdf" not in page.evaluate("document.body.className")
