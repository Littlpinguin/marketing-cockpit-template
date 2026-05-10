#!/usr/bin/env python3
"""
Render an HTML deck to a clean 1920×1080 PDF (one slide per page)
using headless Chromium via Playwright.

Triggers the deck's print mode and gradient-text rasterisation
hooks before printing — these compensate for Chromium's PDF
pipeline quirks (gradient-on-text artefacts, animation final state).

Usage: python scripts/export_pdf.py input.html output.pdf
"""
from __future__ import annotations

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


def main() -> int:
    if len(sys.argv) != 3:
        sys.stderr.write("usage: export_pdf.py <input.html> <output.pdf>\n")
        return 2

    html_in = Path(sys.argv[1]).resolve()
    pdf_out = Path(sys.argv[2]).resolve()

    if not html_in.exists():
        sys.stderr.write(f"file not found: {html_in}\n")
        return 2

    pdf_out.parent.mkdir(parents=True, exist_ok=True)

    print(f"export · in  {html_in}")
    print(f"export · out {pdf_out}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(html_in.as_uri(), wait_until="networkidle")
        # Wait for fonts to settle
        page.wait_for_timeout(1500)
        page.evaluate("document.fonts && document.fonts.ready")

        # Trigger print-mode hooks if the deck exposes them
        page.evaluate("if (window.__enablePrintMode) window.__enablePrintMode()")
        page.evaluate("if (window.__rasterizeGradients) window.__rasterizeGradients()")
        page.wait_for_timeout(800)
        page.emulate_media(media="print")

        page.pdf(
            path=str(pdf_out),
            width="1920px",
            height="1080px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            prefer_css_page_size=True,
        )
        browser.close()

    print(f"export · done · {pdf_out.stat().st_size / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
