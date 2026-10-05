# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), tests/test_engine.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Behaviour of the slides engine shipped in 06-graphic-design/presentations/templates/base.html.

The features listed in 06-graphic-design/presentations/docs/engine-parity.md that react to input are driven
here in headless Chromium: folios numbered from SLIDE_COUNT, the overview
grouped by data-family (and its flat fallback), the keyboard and backdrop rules
of the open overview, the exporting state of the PDF button, the aurora hidden
in print, and the descender compensation of gradient text.

Skipped cleanly when Playwright or Chromium is missing.
Run: python3 -m pytest scripts/tests -q
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"
STARTER = ROOT / "templates" / "base.html"


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
def open_deck():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        errors: list[str] = []

        def _open(path: Path = STARTER):
            page = browser.new_page(viewport={"width": 1600, "height": 900})
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.goto(path.as_uri(), wait_until="load")
            page.wait_for_timeout(200)
            return page

        yield _open
        browser.close()
        assert not errors, errors


def _variant(tmp_path: Path, name: str, transform) -> Path:
    deck = tmp_path / name
    deck.write_text(transform(STARTER.read_text(encoding="utf-8")), encoding="utf-8")
    return deck


ACTIVE = "[...document.querySelectorAll('.slide')].findIndex(s => s.classList.contains('active'))"
IS_OPEN = "document.getElementById('overview').classList.contains('open')"


def test_folios_come_from_slide_count(open_deck):
    markup = STARTER.read_text(encoding="utf-8")
    assert re.search(r'<span class="nav-num">\s*</span>', markup), "folio spans ship empty"
    page = open_deck()
    total = page.evaluate("document.querySelectorAll('.slide').length")
    folios = page.evaluate("[...document.querySelectorAll('.nav-num')].map(e => e.textContent)")
    assert folios == [f"{i:02d} / {total:02d}" for i in range(1, total + 1)]


def test_overview_groups_thumbnails_by_family(open_deck):
    page = open_deck()
    page.keyboard.press("ArrowRight")
    page.keyboard.press("o")
    assert page.evaluate(IS_OPEN)
    heads = page.evaluate("[...document.querySelectorAll('.overview-fam')].map(e => e.textContent)")
    assert heads == ["Opening and navigation", "Offer and closing"]
    thumbs = page.evaluate("""[...document.querySelectorAll('.overview-thumb')].map(t => ({
        tag: t.tagName, index: t.dataset.index, current: t.classList.contains('current'),
        dark: t.classList.contains('dark') }))""")
    assert all(t["tag"] == "BUTTON" for t in thumbs)
    assert [t["index"] for t in thumbs if t["current"]] == ["1"]
    assert [t["index"] for t in thumbs if t["dark"]] == ["1"]


def test_open_overview_only_listens_to_o_and_escape(open_deck):
    page = open_deck()
    page.keyboard.press("o")
    page.keyboard.press("ArrowRight")
    page.keyboard.press("End")
    assert page.evaluate(ACTIVE) == 0, "navigation keys must not move the deck under the panel"
    assert page.evaluate(IS_OPEN)
    page.keyboard.press("Escape")
    assert not page.evaluate(IS_OPEN)
    page.keyboard.press("o")
    page.keyboard.press("o")
    assert not page.evaluate(IS_OPEN)


def test_backdrop_click_closes_and_thumbnail_click_navigates(open_deck):
    page = open_deck()
    page.keyboard.press("o")
    page.mouse.click(4, 4)  # the panel itself, outside every thumbnail
    assert not page.evaluate(IS_OPEN)
    page.keyboard.press("o")
    page.click(".overview-thumb[data-index='2']")
    assert page.evaluate(ACTIVE) == 2
    assert not page.evaluate(IS_OPEN)


def test_deck_without_families_gets_one_flat_grid(open_deck, tmp_path):
    deck = _variant(tmp_path, "flat.html", lambda html: re.sub(r' data-family="[^"]*"', "", html))
    page = open_deck(deck)
    page.keyboard.press("o")
    assert page.evaluate("document.querySelectorAll('.overview-fam').length") == 0
    assert page.evaluate("document.querySelectorAll('.overview-grid').length") == 1
    assert page.evaluate("document.querySelectorAll('.overview-thumb').length") == 3


def test_unknown_family_lands_in_a_last_group(open_deck, tmp_path):
    deck = _variant(tmp_path, "other.html",
                    lambda html: html.replace('data-family="conclusion"', 'data-family="toString"', 1))
    page = open_deck(deck)
    heads = page.evaluate("[...document.querySelectorAll('.overview-fam')].map(e => e.textContent)")
    assert heads == ["Opening and navigation", "Other slides"]


def test_pdf_button_closes_the_overview_and_shows_its_state(open_deck):
    page = open_deck()
    page.evaluate("window.print = () => {}")
    page.keyboard.press("o")
    # The open panel covers the nav rail, so the export can only be reached
    # programmatically then (a script, a bookmarklet): it closes the panel first
    page.evaluate("document.getElementById('pdf-btn').click()")
    assert not page.evaluate(IS_OPEN)
    assert page.evaluate("document.getElementById('pdf-btn').classList.contains('exporting')")
    assert "printing-pdf" in page.evaluate("document.body.className")
    page.evaluate("window.dispatchEvent(new Event('afterprint'))")
    assert not page.evaluate("document.getElementById('pdf-btn').classList.contains('exporting')")
    assert "printing-pdf" not in page.evaluate("document.body.className")


def test_aurora_sits_under_the_content_and_is_hidden_in_print(open_deck):
    page = open_deck()
    assert page.evaluate("document.querySelectorAll('.aurora').length") >= 1
    assert page.evaluate("getComputedStyle(document.querySelector('.aurora')).zIndex") == "-1"
    page.evaluate("window.__enablePrintMode()")
    page.emulate_media(media="print")
    assert page.evaluate("getComputedStyle(document.querySelector('.aurora')).display") == "none"


def test_gradient_text_keeps_its_descender_compensation(open_deck):
    page = open_deck()
    boxes = page.evaluate("""[...document.querySelectorAll('.gradient-text')].map(e => {
        const cs = getComputedStyle(e);
        return { size: parseFloat(cs.fontSize), top: parseFloat(cs.paddingTop),
                 left: parseFloat(cs.paddingLeft), mtop: parseFloat(cs.marginTop) };
    })""")
    assert boxes
    for box in boxes:
        assert box["top"] == pytest.approx(0.22 * box["size"], rel=0.02), box
        assert box["left"] == pytest.approx(0.08 * box["size"], rel=0.02), box
        assert box["mtop"] == pytest.approx(-box["top"], rel=0.02), box
