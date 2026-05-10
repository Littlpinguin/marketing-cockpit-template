#!/usr/bin/env python3
"""
Playwright QA — verify no slide overflows the 1920×1080 frame
and no content invades the bottom chrome safe zone.

Usage:
    python scripts/qa.py presentations/your-deck.html [--viewport 1920x1080]

Requires:
    pip install playwright
    playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import os
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


SAFE_GAP_PX = 16  # min gap between bottom-most content and chrome bottom row
TMP_DIR = Path("/tmp/slides-qa")


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
    parser.add_argument("--viewport", default="1920x1080", help="viewport size (default: 1920x1080)")
    parser.add_argument("--screenshots", action="store_true", help="save per-slide PNGs to /tmp/slides-qa/")
    args = parser.parse_args()

    deck_path = Path(args.deck)
    viewport = parse_viewport(args.viewport)
    url = url_for(deck_path)

    if args.screenshots:
        TMP_DIR.mkdir(parents=True, exist_ok=True)

    print(f"qa  · deck     {deck_path}")
    print(f"qa  · viewport {viewport['width']}x{viewport['height']}")
    print(f"qa  · url      {url}")

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
        print(f"qa  · {total} slides detected\n")

        all_issues: dict[int, list[dict]] = {}

        for i in range(1, total + 1):
            page.evaluate(
                """(idx) => {
                    document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
                    document.querySelectorAll('.slide')[idx].classList.add('active');
                }""",
                i - 1,
            )
            page.wait_for_timeout(700)

            if args.screenshots:
                page.locator("#stage-frame").screenshot(path=str(TMP_DIR / f"slide-{i:02d}.png"))

            issues = page.evaluate(
                """(idx) => {
                    const slide = document.querySelectorAll('.slide')[idx];
                    const fb = document.getElementById('stage-frame').getBoundingClientRect();
                    const scale = fb.width / 1920;
                    const out = { overflow: [], chrome_gap: null };
                    slide.querySelectorAll('*').forEach(el => {
                        if (el.classList.contains('aurora') || el.classList.contains('dust-grid') || el.closest('.chrome')) return;
                        const r = el.getBoundingClientRect();
                        const oR = r.right - fb.right, oB = r.bottom - fb.bottom;
                        const oL = fb.left - r.left, oT = fb.top - r.top;
                        if ((oR > 2 || oB > 2 || oL > 2 || oT > 2) && r.width > 8 && r.height > 8) {
                            out.overflow.push({
                                cls: ((el.className || '') + '').slice(0, 40),
                                oR: Math.round(oR / scale), oB: Math.round(oB / scale),
                                oL: Math.round(oL / scale), oT: Math.round(oT / scale)
                            });
                        }
                    });
                    const chromeBottom = slide.querySelector('.chrome-row.bottom');
                    if (chromeBottom) {
                        const cb = chromeBottom.getBoundingClientRect();
                        const chromeTop = (cb.top - fb.top) / scale;
                        let lowest = 0;
                        slide.querySelectorAll('*').forEach(el => {
                            if (el.classList.contains('aurora') || el.classList.contains('dust-grid') || el.closest('.chrome')) return;
                            const r = el.getBoundingClientRect();
                            const y = (r.bottom - fb.top) / scale;
                            if (y > lowest && r.width > 8) lowest = y;
                        });
                        out.chrome_gap = { lowest: Math.round(lowest), chromeTop: Math.round(chromeTop), gap: Math.round(chromeTop - lowest) };
                    }
                    out.overflow.sort((a, b) => Math.max(b.oR, b.oB, b.oL, b.oT) - Math.max(a.oR, a.oB, a.oL, a.oT));
                    out.overflow = out.overflow.slice(0, 3);
                    return out;
                }""",
                i - 1,
            )

            slide_issues = []
            if issues["overflow"]:
                slide_issues.extend(issues["overflow"])
            if issues["chrome_gap"] and issues["chrome_gap"]["gap"] < SAFE_GAP_PX:
                slide_issues.append({
                    "type": "chrome_gap",
                    "gap": issues["chrome_gap"]["gap"],
                    "lowest": issues["chrome_gap"]["lowest"],
                })

            if slide_issues:
                all_issues[i] = slide_issues
                print(f"  slide {i:02d} · ISSUES")
                for issue in slide_issues:
                    if "cls" in issue:
                        print(f"    overflow .{issue['cls']:<40} oR={issue['oR']} oB={issue['oB']} oL={issue['oL']} oT={issue['oT']}")
                    else:
                        print(f"    chrome gap {issue['gap']}px (need ≥ {SAFE_GAP_PX}) — lowest content y={issue['lowest']}")
            else:
                print(f"  slide {i:02d} · ok")

        browser.close()

        print()
        if all_issues:
            print(f"FAIL · {len(all_issues)} of {total} slides have issues")
            return 1
        print(f"All slides clean · {total} / {total}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
