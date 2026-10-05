#!/usr/bin/env python3
# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), scripts/qa.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Playwright QA for HTML slide decks: the quality gate every deck passes before delivery.

Usage:
    python3 06-graphic-design/presentations/scripts/qa.py 06-graphic-design/presentations/decks/<deck>.html [options]
    python3 06-graphic-design/presentations/scripts/qa.py _examples/deck-catalogue/catalogue.html --no-engine-check

What it checks
--------------
0. Engine parity, read from the file before any browser starts: the deck embeds
   every feature of the slides engine shipped in `06-graphic-design/presentations/templates/base.html`
   (fullscreen, overview, auto-numbered folios, PDF export hooks...). The list
   lives in ENGINE_MARKERS. Skip it with --no-engine-check for a file that is
   not a full deck, such as the layout catalogue.

Then, slide by slide, with every geometry brought back to the native frame
(1920x1080 by default, see --frame):

1. Overflow: no element leaves the frame.
2. Chrome safe zone: content keeps a gap of at least 16 px above the bottom
   chrome row (`.chrome-row.bottom`).
3. Type floors, on every visible text. Two registers:
     - content text: 18 px (--min-font), the projection floor of the deck
       doctrine (CLAUDE.md, "Minimum on-screen type size");
     - label register: 12 px (--min-font-chrome). A text belongs to it when it
       sits inside `.chrome`, when it carries or sits inside a label class
       (LABEL_SELECTORS: eyebrow, meta-label, signature, nav-num, tag-meta,
       tag-folio, tag-signature), or when its computed font-family is a
       monospace stack (first family named "mono", Menlo, Consolas, Monaco,
       Courier, or a stack whose generic fallback is `monospace`).
   Content text under 24 px is a `tight-body` warning (headings h1-h4 excepted).
   A label-register text under the content floor that runs past 12 words is a
   `long-label` warning: a sentence shrunk to caption size.
4. Font: the computed family is a brand family. Brand families come, in order,
   from --font (repeatable); from a DTCG tokens file (`font.<name>.$value`):
   --tokens, else the first `brand/tokens.json` or `01-brand/tokens.json`
   found walking up from the deck's folder, then from this script's folder,
   each walk stopping at the repository root; else from the deck's own CSS
   variables `--font-display`, `--font-body`, `--font-mono` (the normal path in
   slides-agent, whose brand lives in 06-graphic-design/presentations/tokens.css, inlined in every deck).
   A brand family passes everywhere. An undeclared monospace passes in the
   chrome, on label classes, on `code`, `pre`, `kbd` and on the exact class
   `mono`; elsewhere it is a warning. Any other family is an error. With no
   known brand family the check is skipped, with a warning.
5. Contrast, WCAG 2.x AA (4.5:1, or 3:1 from 24 px or from 18.66 px bold), on
   every visible text, chrome included. The text colour is composited with the
   element's effective opacity (opacities of the element and of its ancestors
   up to the first opaque background). On a gradient or image background the
   ratio cannot be computed: warning. Gradient text (`background-clip: text`)
   is listed apart, to be checked by eye.
6. Folios: present and increasing (`.nav-num` in the starter, `.tag-folio` in
   the catalogue; --folio for another selector, --no-folio to skip).
7. PDF weight (--with-pdf): renders the deck to PDF through its print hooks
   and fails when the average weight per slide falls under --min-kb-per-slide
   (default 40 KB): the symptom of print CSS collapsing pages.

Before measuring, transition and animation delays are zeroed and transitions
made instant, so each slide is audited in its settled state (a staggered
element still at opacity 0 would otherwise escape the audit).

Exempt layers: anything inside BLEED selectors (`.slide-bg`, `[data-bleed]`,
`.aurora`, `.dust-grid`, the catalogue's `.legend` cartouche...) is skipped by
every check. Add more with --bleed. Put `data-bleed` on an image container,
never on a text block, or QA stops protecting that text.

Finding ids (`type`, stable, also used in the JSON output):
    overflow     element outside the native frame                      error
    chrome-gap   content closer than 16 px to the bottom chrome row     error
    type-floor   text under its register's floor                        error
    tight-body   content text under 24 px                               warning
    long-label   label-register sentence under the content floor        warning
    font         family outside the brand (undeclared mono: warning)    error / warning
    contrast     WCAG ratio too low (non-uniform background: warning)   error / warning
    folio        folio missing or not increasing                        error
    truncated    the collector hit its per-slide limit (partial report) warning
    lang         --lang asked but the deck exposes no window.__setLang  warning
    pdf-weight   --with-pdf: PDF missing or implausibly light           error
Missing engine markers are reported in the `engine` block (exit code 1).

Levels: `error` fails QA; `warning` is listed and does not fail; `summary`
stands for findings hidden by the per-slide cap (--max-per-slide, 8 per slide
and per type by default) and is never counted. The JSON output also carries
`errors_total`, `warnings_total` and `by_type`, computed before the cap.

Exit codes: 0 "All slides clean" (warnings allowed), 1 errors, 2 usage error,
missing or unreadable deck, or missing Playwright.

Requires: pip install playwright && playwright install chromium
Tests:    python3 -m pytest scripts/tests -q
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SCRIPT = Path(__file__).resolve()

# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------
SAFE_GAP_PX = 16          # min gap between the lowest content and the bottom chrome row
MIN_FONT_PX = 18.0        # content floor (projection, read from across a room)
MIN_FONT_CHROME_PX = 12.0 # label register floor (chrome, mono labels, eyebrows)
COMFORT_PX = 24.0         # content under this size is a `tight-body` warning
LABEL_MAX_WORDS = 12      # longer than this, a small label reads as a shrunk sentence
MAX_PER_SLIDE = 8         # findings listed per slide and per type (0 = no cap)
MAX_TEXTS = 400           # text elements collected per slide (the rest is reported)
MAX_OVERFLOWS = 20        # overflows collected per slide (the rest is reported)
MIN_KB_PER_SLIDE = 40     # --with-pdf: average PDF weight per slide
DEFAULT_WAIT_MS = 800
TMP_DIR = "/tmp/slides-qa"

SLIDE_SELECTORS = (".slide", ".plate")   # starter / decks, then the catalogue
FOLIO_DEFAULT = ".nav-num, .tag-folio"   # starter / decks, then the catalogue
TOKENS_CANDIDATES = ("brand/tokens.json", "01-brand/tokens.json")
FONT_VARIABLES = ("--font-display", "--font-body", "--font-mono")
HEADINGS = {"H1", "H2", "H3", "H4"}
TECHNICAL_TAGS = {"CODE", "PRE", "KBD"}

# Layers that are full-bleed or overflowing on purpose, and annotations that are
# not deck content. Each is skipped with its descendants by every check.
BLEED = [
    "[data-bleed]", ".bleed", ".slide-bg",              # photos that run to the frame edge
    ".aurora", ".dust-grid",                            # atmospheric layers
    ".legend",                                          # the catalogue's self-caption cartouche
    ".gridlines", ".grid-overlay", ".plate-bg", ".edge-gradient", ".paper",
]

# Label register: these classes (and their descendants) take the chrome floor.
LABEL_SELECTORS = [
    ".chrome",
    ".eyebrow", ".meta-label", ".signature", ".nav-num",   # starter (06-graphic-design/presentations/templates/base.html)
    ".tag-meta", ".tag-folio", ".tag-signature",           # catalogue
]

# ---------------------------------------------------------------------------
# Engine parity: the features of the slides engine in 06-graphic-design/presentations/templates/base.html.
# id -> (feature, textual markers; any one of them proves the feature).
# A deck missing a marker has lost a feature of the engine. Keep this list in
# step with 06-graphic-design/presentations/templates/base.html and with the table of 06-graphic-design/presentations/docs/engine-parity.md:
# scripts/tests/test_slides_qa.py fails if the starter misses one.
# ---------------------------------------------------------------------------
ENGINE_MARKERS: dict[str, tuple[str, tuple[str, ...]]] = {
    "stage-frame": (
        "native 1920x1080 frame scaled to the viewport", ("stage-frame",)),
    "body.presenting": (
        "fullscreen presentation mode (F key or button, nav-rail hidden)", ("body.presenting",)),
    "nav-peek": (
        "nav-rail reappears near the bottom edge in presentation mode", ("nav-peek",)),
    "requestFullscreen": (
        "Fullscreen API wiring", ("requestFullscreen",)),
    "overview": (
        "overview panel (O key)", ("overview",)),
    "auto-folios": (
        "in-slide folios auto-numbered from DOM order",
        ("querySelector('.nav-num')", 'querySelector(".nav-num")', "SLIDE_COUNT")),
    "printing-pdf": (
        "print mode of the PDF export (P key or button)", ("printing-pdf",)),
    "window.print": (
        "PDF export trigger", ("window.print",)),
    "__enablePrintMode": (
        "headless print-mode hook used by export_pdf.py and qa.py --with-pdf", ("__enablePrintMode",)),
    "__rasterizeGradients": (
        "gradient-text rasterisation hook for the PDF export", ("__rasterizeGradients",)),
    "GRADIENT_TEXT_SELECTORS": (
        "list of gradient-text selectors rasterised before printing", ("GRADIENT_TEXT_SELECTORS",)),
    "brand-pattern": ("brand-pattern hooks (.motif / .texture / .corner / .filet-orn)", ("--brand-pattern",)),
}


def check_engine_parity(deck: Path) -> list[str]:
    """Return the ids of the engine markers missing from the deck (empty = full engine)."""
    html = Path(deck).read_text(encoding="utf-8", errors="replace")
    return [key for key, (_, markers) in ENGINE_MARKERS.items()
            if not any(m in html for m in markers)]


# ---------------------------------------------------------------------------
# Colour and contrast (WCAG 2.x), pure Python
# ---------------------------------------------------------------------------
CONTRAST_BODY = 4.5
CONTRAST_LARGE = 3.0
LARGE_PX = 24.0          # 18 pt
LARGE_BOLD_PX = 18.66    # 14 pt bold

_NUMBER = re.compile(r"[-+]?[0-9]*\.?[0-9]+%?")
_FUNCTION = re.compile(r"^rgba?\((.*)\)$")

Color = tuple  # (r, g, b) ints 0-255
ColorAlpha = tuple  # (r, g, b, alpha 0-1)


def _channel(token: str) -> float:
    if token.endswith("%"):
        return float(token[:-1]) / 100.0 * 255.0
    return float(token)


def _alpha(token: str) -> float:
    value = float(token[:-1]) / 100.0 if token.endswith("%") else float(token)
    return min(1.0, max(0.0, value))


def _round(value: float) -> int:
    """Round half up, clamped to a byte."""
    return min(255, max(0, int(value + 0.5)))


def parse_color(css: str | None) -> ColorAlpha | None:
    """Read a CSS colour as (r, g, b, alpha), or None when unreadable.

    Accepts what `getComputedStyle` returns (`rgb()`, `rgba()`, space syntax with
    `/ alpha`), hex notations of 3, 4, 6 or 8 digits, and `transparent`.
    """
    if not css:
        return None
    text = css.strip().lower()
    if text == "transparent":
        return (0, 0, 0, 0.0)
    if text.startswith("#"):
        digits = text[1:]
        if not re.fullmatch(r"[0-9a-f]+", digits):
            return None
        if len(digits) in (3, 4):
            digits = "".join(c * 2 for c in digits)
        if len(digits) not in (6, 8):
            return None
        r, g, b = (int(digits[i:i + 2], 16) for i in (0, 2, 4))
        a = int(digits[6:8], 16) / 255.0 if len(digits) == 8 else 1.0
        return (r, g, b, a)
    match = _FUNCTION.match(text)
    if not match:
        return None
    tokens = _NUMBER.findall(match.group(1))
    if len(tokens) < 3:
        return None
    r, g, b = (_round(_channel(t)) for t in tokens[:3])
    a = _alpha(tokens[3]) if len(tokens) > 3 else 1.0
    return (r, g, b, a)


def luminance(color: Color) -> float:
    """WCAG 2.x relative luminance of an opaque colour."""
    channels = []
    for raw in color[:3]:
        c = raw / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: Color, background: Color) -> float:
    """WCAG 2.x contrast ratio between two opaque colours (1.0 to 21.0)."""
    a, b = luminance(foreground), luminance(background)
    light, dark = max(a, b), min(a, b)
    return (light + 0.05) / (dark + 0.05)


def composite(top: ColorAlpha, bottom: Color) -> Color:
    """Composite a translucent colour over an opaque one (source-over)."""
    r, g, b, a = top
    return tuple(_round(a * hi + (1 - a) * lo) for hi, lo in zip((r, g, b), bottom))


def resolve_background(stack: list[str], default: Color = (255, 255, 255)) -> Color:
    """Actual background colour behind a text.

    `stack` lists computed `background-color` values from the text outwards.
    Translucent layers are composited over the first opaque one; without an
    opaque layer, `default` (the document white) is the base.
    """
    layers = []
    base = default
    for css in stack:
        color = parse_color(css)
        if color is None or color[3] == 0.0:
            continue
        if color[3] >= 1.0:
            base = color[:3]
            break
        layers.append(color)
    for layer in reversed(layers):
        base = composite(layer, base)
    return base


def contrast_threshold(size_px: float, bold: bool = False) -> float:
    """Minimum WCAG 2.x AA ratio for a text of this size."""
    if size_px >= LARGE_PX or (bold and size_px >= LARGE_BOLD_PX):
        return CONTRAST_LARGE
    return CONTRAST_BODY


def is_plain_background(background_image: str | None) -> bool:
    """True when the layer has no gradient or image (contrast is then computable)."""
    if not background_image:
        return True
    return background_image.strip().lower() in ("none", "initial", "unset")


def _is_opaque_level(level: dict) -> bool:
    color = parse_color(level.get("c"))
    return color is not None and color[3] >= 1.0


def resolve_background_and_uniformity(levels: list[dict]) -> tuple[Color, bool]:
    """Resolve the background behind a text and tell whether it is a plain colour.

    `levels` lists, from the text outwards, each ancestor's computed
    `background-color` (key `c`) and `background-image` (key `i`). The walk stops
    at the first opaque colour; an image or gradient met before it makes the
    background non-uniform, so the caller warns instead of judging.
    """
    colors: list[str] = []
    for level in levels:
        if not is_plain_background(level.get("i")):
            return resolve_background(colors), False
        colors.append(level.get("c"))
        if _is_opaque_level(level):
            break
    return resolve_background(colors), True


def effective_opacity(levels: list[dict]) -> float:
    """Product of the opacities (key `o`) from the text up to its opaque background.

    The level that carries the opaque background is excluded: if it fades, it
    fades together with the text and their relative contrast barely moves.
    """
    opacity = 1.0
    for level in levels:
        if not is_plain_background(level.get("i")) or _is_opaque_level(level):
            break
        value = level.get("o")
        if isinstance(value, (int, float)) and 0.0 <= value <= 1.0:
            opacity *= value
    return opacity


# ---------------------------------------------------------------------------
# Fonts and brand tokens, pure Python
# ---------------------------------------------------------------------------
GENERIC_FAMILIES = {"serif", "sans-serif", "monospace", "cursive", "fantasy",
                    "system-ui", "ui-serif", "ui-sans-serif", "ui-monospace",
                    "ui-rounded", "emoji", "math", "fangsong"}
KNOWN_MONOSPACE = {"menlo", "consolas", "monaco", "courier", "courier new"}


def families(font_family: str | None) -> list[str]:
    """Families of a computed `font-family`, unquoted, in order."""
    if not font_family:
        return []
    return [f.strip().strip("\"'").strip() for f in font_family.split(",") if f.strip()]


def first_family(font_family: str | None) -> str:
    found = families(font_family)
    return found[0] if found else ""


def is_monospace(family: str) -> bool:
    name = family.strip().lower()
    return "mono" in name or name in KNOWN_MONOSPACE


def is_monospace_stack(font_family: str | None) -> bool:
    """True when a computed `font-family` renders as monospace.

    Either its first family is a monospace (named "mono", Menlo, Consolas...),
    or its last generic fallback is `monospace` / `ui-monospace`.
    """
    stack = families(font_family)
    if not stack:
        return False
    if is_monospace(stack[0]):
        return True
    generics = [f.lower() for f in stack if f.lower() in GENERIC_FAMILIES]
    return bool(generics) and generics[-1] in ("monospace", "ui-monospace")


def font_matches(font_family: str | None, expected: str | Iterable[str],
                 mono_allowed: bool = False) -> bool:
    """True when the computed first family is a brand family (case-insensitive),
    or a monospace where `mono_allowed` is set."""
    family = first_family(font_family)
    if not family:
        return False
    if isinstance(expected, str):
        expected = [expected]
    if family.lower() in {e.strip().lower() for e in expected if e}:
        return True
    return mono_allowed and is_monospace(family)


def read_tokens(path: Path) -> dict[str, Any]:
    """Read a DTCG tokens file. Raise ValueError when missing or unreadable."""
    path = Path(path)
    if not path.exists():
        raise ValueError(f"{path} not found")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise ValueError(f"{path} is unreadable: {err}") from err
    if not isinstance(data, dict):
        raise ValueError(f"{path}: a JSON object is expected at the root")
    return data


def brand_families(tokens: dict[str, Any]) -> list[str]:
    """First family of each font token (`font.<name>.$value`), generics excluded.

    A value may be a list (`["Brand Sans", "system-ui", "sans-serif"]`) or a CSS
    string (`"'Brand Sans', sans-serif"`).
    """
    found: list[str] = []
    for key, node in (tokens.get("font") or {}).items():
        if key.startswith("$") or not isinstance(node, dict):
            continue
        value = node.get("$value")
        if isinstance(value, list):
            head = value[0] if value and isinstance(value[0], str) else ""
        elif isinstance(value, str):
            head = value.split(",")[0]
        else:
            continue
        head = head.strip().strip("\"'").strip()
        if head and head.lower() not in GENERIC_FAMILIES and head not in found:
            found.append(head)
    return found


def families_from_variables(values: Iterable[str]) -> list[str]:
    """First family of each `--font-*` variable value, generics excluded, deduplicated."""
    found: list[str] = []
    for value in values:
        family = first_family(value)
        if family and family.lower() not in GENERIC_FAMILIES and family not in found:
            found.append(family)
    return found


def _up_to_repo_root(start: Path):
    """Yield `start` and its parents, stopping at the first folder holding `.git`."""
    folder = start
    while True:
        yield folder
        if (folder / ".git").exists() or folder.parent == folder:
            return
        folder = folder.parent


def find_tokens_file(deck: Path, script: Path = SCRIPT) -> Path | None:
    """First `brand/tokens.json` or `01-brand/tokens.json` near the deck, then near the script."""
    seen: set[Path] = set()
    for start in (Path(deck).resolve().parent, Path(script).resolve().parent):
        for folder in _up_to_repo_root(start):
            if folder in seen:
                continue
            seen.add(folder)
            for relative in TOKENS_CANDIDATES:
                candidate = folder / relative
                if candidate.is_file():
                    return candidate
    return None


def parse_size(value: str) -> dict:
    """Read `WIDTHxHEIGHT` into the dict Playwright expects. Raise ValueError when invalid."""
    try:
        width, height = value.lower().split("x")
        size = {"width": int(width), "height": int(height)}
    except Exception:
        raise ValueError(f"invalid size: {value} (expected WIDTHxHEIGHT, e.g. 1920x1080)")
    if size["width"] <= 0 or size["height"] <= 0:
        raise ValueError(f"invalid size: {value} (dimensions must be positive)")
    return size


# ---------------------------------------------------------------------------
# Audit: raw values collected in the page -> findings. Pure Python.
# ---------------------------------------------------------------------------
def finding(level: str, type_: str, message: str, target: str | None = None) -> dict:
    out = {"level": level, "type": type_, "message": message}
    if target:
        out["target"] = target
    return out


def _target(cls: str, tag: str, ctx: str = "") -> str:
    """CSS-like name of an element: `.a.b`, or `.ancestor tag` when it has no class."""
    if cls:
        return "." + ".".join(cls.split())
    tag = (tag or "?").lower()
    return f".{ctx} {tag}" if ctx else tag


def text_register(text: dict) -> str:
    """`chrome`, `label` (label class), `mono` (monospace stack) or `content`."""
    if text.get("chrome"):
        return "chrome"
    if text.get("label"):
        return "label"
    if is_monospace_stack(text.get("font")):
        return "mono"
    return "content"


def mono_allowed(text: dict) -> bool:
    """Where an undeclared monospace passes silently: chrome, label classes,
    `code` / `pre` / `kbd`, and the exact class token `mono` (not `.monogram`)."""
    return (
        bool(text.get("chrome"))
        or bool(text.get("label"))
        or text.get("tag") in TECHNICAL_TAGS
        or "mono" in (text.get("cls") or "").split()
    )


def audit_texts(raw: dict, min_font: float, min_font_chrome: float,
                brand: list[str]) -> tuple[list[dict], list[str]]:
    """Type floors, font and contrast findings, plus the gradient texts to check by eye.

    `brand` empty: the font is not checked (the deck-level report says so once).
    """
    findings: list[dict] = []
    gradients: list[str] = []

    for text in raw["texts"]:
        target = _target(text.get("cls", ""), text.get("tag", ""), text.get("ctx", ""))
        size, bold = text["fs"], text.get("weight", 400) >= 700
        register = text_register(text)
        floor = min_font if register == "content" else min_font_chrome

        if size < floor:
            where = "content floor" if register == "content" else f"chrome floor ({register} register)"
            findings.append(finding(
                "error", "type-floor",
                f"type {size:g}px below the {where} {floor:g}px on {target}", target))
        elif register == "content" and size < COMFORT_PX and text.get("tag") not in HEADINGS:
            findings.append(finding(
                "warning", "tight-body",
                f"type {size:g}px below the comfort size {COMFORT_PX:g}px on {target}", target))

        if (register != "content" and size < min_font
                and text.get("words", 0) > LABEL_MAX_WORDS):
            findings.append(finding(
                "warning", "long-label",
                f"{text['words']}-word text at {size:g}px in the {register} register on {target}: "
                f"labels stay short, set sentences at {min_font:g}px or more", target))

        if brand and not font_matches(text.get("font"), brand, mono_allowed=mono_allowed(text)):
            family = first_family(text.get("font"))
            if is_monospace_stack(text.get("font")):
                # An undeclared monospace outside the label register is an art
                # direction choice to confirm, not a brand breach: warning.
                findings.append(finding(
                    "warning", "font",
                    f'undeclared monospace "{family}" outside the chrome, labels and code on {target}',
                    target))
            else:
                findings.append(finding(
                    "error", "font",
                    f'font "{family}" instead of {" / ".join(brand)} on {target}', target))

        if text.get("gradient"):
            gradients.append(f'{target} "{text.get("text", "")}"')
            continue

        levels = text.get("bgs") or []
        background, uniform = resolve_background_and_uniformity(levels)
        if not uniform:
            findings.append(finding(
                "warning", "contrast",
                f"non-uniform background, contrast not computed on {target}", target))
            continue

        color = parse_color(text.get("color"))
        if color is None:
            continue
        opacity = effective_opacity(levels)
        rendered = composite((color[0], color[1], color[2], color[3] * opacity), background)
        ratio = contrast_ratio(rendered, background)
        threshold = contrast_threshold(size, bold=bold)
        if ratio < threshold:
            faded = f", opacity {opacity:.2f}" if opacity < 0.995 else ""
            findings.append(finding(
                "error", "contrast",
                f"contrast {ratio:.2f}:1 below {threshold}:1 on {target} ({size:g}px{faded})",
                target))

    return findings, gradients


def audit_truncation(raw: dict) -> list[dict]:
    """A partial report says so."""
    out = []
    rest = raw["texts_total"] - len(raw["texts"])
    if rest > 0:
        out.append(finding(
            "warning", "truncated",
            f"{rest} text elements not audited on this slide "
            f"({raw['texts_total']} found, {len(raw['texts'])} collected)"))
    rest = raw["over_total"] - len(raw["over"])
    if rest > 0:
        out.append(finding(
            "warning", "truncated",
            f"{rest} overflows not listed on this slide "
            f"({raw['over_total']} found, {len(raw['over'])} collected)"))
    return out


def audit_slide(raw: dict, min_font: float, min_font_chrome: float,
                brand: list[str]) -> tuple[list[dict], list[str]]:
    out = []
    for o in raw["over"]:
        target = _target(o.get("cls", ""), o.get("tag", ""), o.get("ctx", ""))
        out.append(finding(
            "error", "overflow",
            f"overflow {target} R={o['R']} B={o['B']} L={o['L']} T={o['T']}", target))

    if raw.get("gap") is not None and raw["gap"] < SAFE_GAP_PX:
        target = _target(raw.get("lowest_cls", ""), raw.get("lowest_tag", ""), raw.get("lowest_ctx", ""))
        out.append(finding(
            "error", "chrome-gap",
            f"chrome safe zone {raw['gap']}px instead of >= {SAFE_GAP_PX}px, "
            f"lowest element {target}", target))

    texts, gradients = audit_texts(raw, min_font, min_font_chrome, brand)
    return out + texts + audit_truncation(raw), gradients


def first_integer(text: str | None) -> int | None:
    if not text:
        return None
    digits = "".join(c if c.isdigit() else " " for c in text).split()
    return int(digits[0]) if digits else None


def audit_folios(folios: list[str | None]) -> list[tuple[int, dict]]:
    """(slide number, finding) for every missing or non-increasing folio."""
    out = []
    numbers = []
    for index, raw in enumerate(folios, start=1):
        number = first_integer(raw)
        if number is None:
            out.append((index, finding("error", "folio", "folio missing or unreadable")))
        numbers.append(number)
    previous = None
    for index, number in enumerate(numbers, start=1):
        if number is None:
            continue
        if previous is not None and number <= previous:
            out.append((index, finding(
                "error", "folio", f"folio {number} not increasing (previous slide: {previous})")))
        previous = number
    return out


def count(findings: list[dict], level: str) -> int:
    """Count findings of a level; summary lines never count."""
    return sum(1 for f in findings if f["level"] == level)


def cap(findings: list[dict], limit: int = MAX_PER_SLIDE) -> list[dict]:
    """Keep at most `limit` findings per type, for a readable report (0 = no cap).

    What is hidden is stood for by one `summary` line per type, carrying the
    number hidden. A summary is neither an error nor a warning: it must never
    inflate the totals, or a deck looks worse than it is.
    """
    if not limit or limit <= 0:
        return list(findings)
    kept, seen, hidden = [], {}, {}
    for f in findings:
        kind = f["type"]
        seen[kind] = seen.get(kind, 0) + 1
        if seen[kind] <= limit:
            kept.append(f)
        else:
            hidden[kind] = hidden.get(kind, 0) + 1
    for kind, number in hidden.items():
        kept.append({"level": "summary", "type": kind, "hidden": number,
                     "message": f'... {number} more "{kind}" findings not listed on this slide'})
    return kept


def tally(findings: Iterable[dict]) -> dict[str, dict[str, int]]:
    """{type: {"errors": n, "warnings": m}}, summary lines excluded."""
    out: dict[str, dict[str, int]] = {}
    for f in findings:
        if f["level"] not in ("error", "warning"):
            continue
        entry = out.setdefault(f["type"], {"errors": 0, "warnings": 0})
        entry["errors" if f["level"] == "error" else "warnings"] += 1
    return dict(sorted(out.items()))


# ---------------------------------------------------------------------------
# Browser side: the collector judges nothing, it reports computed CSS values
# and geometries brought back to the native frame. Python decides.
# ---------------------------------------------------------------------------
SETTLE_CSS = """
*, *::before, *::after {
  transition-delay: 0s !important;
  transition-duration: 0.01ms !important;
  animation-delay: 0s !important;
}
"""

COLLECTOR = """
(args) => {
  const [idx, selector, bleed, labelSel, nativeWidth, maxTexts, maxOver, folioSel] = args;
  const slide = document.querySelectorAll(selector)[idx];
  const frameEl = document.getElementById('stage-frame') || slide;
  const fb = frameEl.getBoundingClientRect();

  // The native frame is brought to the screen by `transform: scale()`.
  // getBoundingClientRect returns screen pixels: dividing by this factor gives
  // native pixels. Computed font sizes are NOT affected by the transform.
  const scale = (fb.width / nativeWidth) || 1;

  const ignored = el => bleed.some(s => { try { return !!el.closest(s); } catch (e) { return false; } });
  const cls = el => (el.getAttribute('class') || '').trim().replace(/\\s+/g, ' ').slice(0, 40);
  // First class of the nearest classed ancestor: names a classless element (`.nav-num strong`).
  const ctx = el => {
    for (let n = el.parentElement; n; n = n.parentElement) {
      const c = cls(n);
      if (c) return c.split(' ')[0];
      if (n === slide) break;
    }
    return '';
  };
  // Text painted by a `background-clip: text` on itself or an ancestor (gradient text).
  const clipped = el => {
    for (let n = el; n; n = n.parentElement) {
      const c = getComputedStyle(n);
      if (c.webkitBackgroundClip === 'text' || c.backgroundClip === 'text') return true;
      if (n === slide) break;
    }
    return false;
  };

  // 1. overflow
  const over = [];
  slide.querySelectorAll('*').forEach(el => {
    if (ignored(el) || el.closest('.chrome')) return;
    const r = el.getBoundingClientRect();
    if (r.width < 8 * scale || r.height < 8 * scale) return;
    const o = { R: (r.right - fb.right) / scale, B: (r.bottom - fb.bottom) / scale,
                L: (fb.left - r.left) / scale, T: (fb.top - r.top) / scale };
    if (o.R > 2 || o.B > 2 || o.L > 2 || o.T > 2)
      over.push({ cls: cls(el), tag: el.tagName, ctx: ctx(el), R: Math.round(o.R), B: Math.round(o.B),
                  L: Math.round(o.L), T: Math.round(o.T) });
  });
  over.sort((a, b) => Math.max(b.R, b.B, b.L, b.T) - Math.max(a.R, a.B, a.L, a.T));

  // 2. bottom chrome safe zone
  let gap = null, lowestCls = '', lowestTag = '', lowestCtx = '';
  const chromeBottom = slide.querySelector('.chrome-row.bottom');
  if (chromeBottom) {
    const chromeTop = (chromeBottom.getBoundingClientRect().top - fb.top) / scale;
    let lowest = 0;
    slide.querySelectorAll('*').forEach(el => {
      if (ignored(el) || el.closest('.chrome')) return;
      const r = el.getBoundingClientRect();
      if (r.width < 8 * scale || r.height < 4 * scale) return;
      const y = (r.bottom - fb.top) / scale;
      if (y > lowest) { lowest = y; lowestCls = cls(el); lowestTag = el.tagName; lowestCtx = ctx(el); }
    });
    gap = Math.round(chromeTop - lowest);
  }

  // 3-5. visible texts: size, font, colours, background stack, register flags
  const visible = el => el.checkVisibility
    ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })
    : (() => { const cs = getComputedStyle(el);
               return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0; })();
  const texts = [];
  let textsTotal = 0;
  slide.querySelectorAll('*').forEach(el => {
    if (ignored(el)) return;
    const own = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own || !visible(el)) return;
    const r = el.getBoundingClientRect();
    if (r.width < 1 || r.height < 1) return;
    if (r.right < fb.left || r.left > fb.right || r.bottom < fb.top || r.top > fb.bottom) return;
    textsTotal += 1;
    if (texts.length >= maxTexts) return;

    const cs = getComputedStyle(el);
    const bgs = [];
    for (let n = el, depth = 0; n && depth < 40; n = n.parentElement, depth++) {
      const ncs = getComputedStyle(n);
      bgs.push({ c: ncs.backgroundColor, i: ncs.backgroundImage, o: parseFloat(ncs.opacity) });
      if (n === document.documentElement) break;
    }
    const content = (el.textContent || '').trim().replace(/\\s+/g, ' ');
    texts.push({
      cls: cls(el), tag: el.tagName, ctx: ctx(el), text: content.slice(0, 40),
      words: content ? content.split(' ').length : 0,
      fs: Math.round(parseFloat(cs.fontSize) * 10) / 10,
      weight: parseInt(cs.fontWeight, 10) || 400,
      font: cs.fontFamily, color: cs.color, bgs: bgs,
      gradient: clipped(el),
      chrome: !!el.closest('.chrome'),
      label: !!(labelSel && el.closest(labelSel)),
    });
  });

  // 6. folio
  const folio = folioSel ? slide.querySelector(folioSel) : null;

  return { over: over.slice(0, maxOver), over_total: over.length,
           gap: gap, lowest_cls: lowestCls, lowest_tag: lowestTag, lowest_ctx: lowestCtx,
           texts: texts, texts_total: textsTotal,
           folio: folio ? (folio.textContent || '').trim() : null,
           scale: Math.round(scale * 1000) / 1000 };
}
"""

ACTIVATE = """
([selector, index]) => {
  const slides = document.querySelectorAll(selector);
  slides.forEach(s => s.classList.remove('active'));
  slides[index].classList.add('active');
}
"""

FONT_VARIABLES_JS = """
(names) => {
  const cs = getComputedStyle(document.documentElement);
  return names.map(v => cs.getPropertyValue(v).trim()).filter(Boolean);
}
"""


def collect(page, selector: str, total: int, bleed: list[str], native_width: int,
            wait_ms: int, shots_dir: Path | None, folio_sel: str | None) -> list[dict]:
    raws = []
    label_sel = ", ".join(LABEL_SELECTORS)
    for index in range(total):
        page.evaluate(ACTIVATE, [selector, index])
        page.wait_for_timeout(wait_ms)
        if shots_dir:
            frame = page.locator("#stage-frame")
            target = frame if frame.count() else page.locator(selector).nth(index)
            target.screenshot(path=str(shots_dir / f"slide-{index + 1:02d}.png"))
        raws.append(page.evaluate(
            COLLECTOR,
            [index, selector, bleed, label_sel, native_width, MAX_TEXTS, MAX_OVERFLOWS, folio_sel],
        ))
    return raws


def render_pdf(page, deck: Path, frame: dict, total: int, min_kb: float) -> dict:
    """Render the deck through its print hooks and judge the average weight per slide."""
    out_dir = Path(TMP_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{deck.stem}.pdf"
    try:
        page.evaluate("() => { if (window.__enablePrintMode) window.__enablePrintMode();"
                      " else document.body.classList.add('printing-pdf'); }")
        page.evaluate("() => { if (window.__rasterizeGradients) window.__rasterizeGradients(); }")
        page.wait_for_timeout(600)
        page.pdf(path=str(pdf_path), width=f"{frame['width']}px", height=f"{frame['height']}px",
                 print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    except Exception as exc:  # noqa: BLE001 - any failure is a QA finding
        return {"path": str(pdf_path), "error": str(exc), "ok": False}
    size_kb = pdf_path.stat().st_size / 1024
    average = size_kb / max(1, total)
    return {"path": str(pdf_path), "size_kb": round(size_kb, 1),
            "avg_kb_per_slide": round(average, 1), "threshold_kb": min_kb,
            "ok": average >= min_kb}


def pdf_finding(pdf: dict) -> dict | None:
    if pdf.get("ok"):
        return None
    if "error" in pdf:
        return finding("error", "pdf-weight", f"could not render the PDF: {pdf['error']}")
    return finding(
        "error", "pdf-weight",
        f"PDF averages {pdf['avg_kb_per_slide']:.0f} KB per slide, below {pdf['threshold_kb']:g} KB: "
        "pages probably collapsed; check the @media print rules, GRADIENT_TEXT_SELECTORS "
        "coverage and the __enablePrintMode / __rasterizeGradients hooks")


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
MARK = {"error": "!", "warning": "~"}


def _print_findings(findings: list[dict]) -> None:
    for f in findings:
        print(f"    {MARK.get(f['level'], '+')} [{f['type']}] {f['message']}")


def text_report(ctx: dict) -> None:
    summary = ctx["summary"]
    print(f"qa  · deck     {summary['deck']}")
    print(f"qa  · viewport {summary['viewport']} · native frame {summary['frame']}")
    fonts = " / ".join(summary["fonts"]) or "not checked"
    print(f"qa  · fonts    {fonts}" + (f" ({summary['fonts_source']})" if summary["fonts"] else ""))
    print(f"qa  · floors   content {summary['min_font']:g}px · chrome and labels "
          f"{summary['min_font_chrome']:g}px")
    print(f"qa  · {summary['slides']} slides detected (selector {summary['selector']})\n")

    deck_findings = ctx["deck_findings"]
    if deck_findings:
        print(f"  deck · {count(deck_findings, 'error')} error(s), "
              f"{count(deck_findings, 'warning')} warning(s)")
        _print_findings(deck_findings)

    for entry in ctx["slides"]:
        findings = entry["findings"]
        if not findings:
            print(f"  slide {entry['slide']:02d} · ok")
            continue
        print(f"  slide {entry['slide']:02d} · {count(findings, 'error')} error(s), "
              f"{count(findings, 'warning')} warning(s)")
        _print_findings(findings)

    if ctx["gradient_text"]:
        print("\n  gradient text (background-clip: text), contrast not judged, check by eye:")
        for line in ctx["gradient_text"]:
            print(f"    · {line}")

    pdf = ctx.get("pdf")
    if pdf:
        print()
        if "error" in pdf:
            print(f"pdf · FAIL · could not render the PDF: {pdf['error']}")
        else:
            print(f"pdf · {'ok' if pdf['ok'] else 'FAIL'} · {pdf['path']} · "
                  f"{pdf['size_kb']:.0f} KB total · {pdf['avg_kb_per_slide']:.0f} KB/slide "
                  f"(threshold >= {pdf['threshold_kb']:g} KB/slide)")

    print()
    errors, warnings = summary["errors"], summary["warnings"]
    if errors:
        print(f"FAIL · {errors} error(s), {warnings} warning(s)")
    else:
        print(f"All slides clean · {summary['slides']} / {summary['slides']}"
              + (f" · {warnings} warning(s)" if warnings else ""))
    if (summary["errors_total"], summary["warnings_total"]) != (errors, warnings):
        print(f"     · before the cap of {summary['max_per_slide']} per slide and type: "
              f"{summary['errors_total']} error(s), {summary['warnings_total']} warning(s)")
    if summary["by_type"] and (errors or warnings):
        parts = []
        for kind, n in summary["by_type"].items():
            bits = [f"{n['errors']} err" if n["errors"] else "", f"{n['warnings']} warn" if n["warnings"] else ""]
            parts.append(f"{kind} " + " ".join(b for b in bits if b))
        print("     · by type: " + " · ".join(parts))


def report_engine_failure(args, deck: Path, missing: list[str]) -> int:
    if args.format == "json":
        print(json.dumps({
            "summary": {"deck": str(deck), "slides": None, "errors": len(missing), "warnings": 0,
                        "errors_total": len(missing), "warnings_total": 0, "by_type": {}},
            "engine": {"checked": True,
                       "missing": [{"marker": m, "feature": ENGINE_MARKERS[m][0]} for m in missing]},
            "deck_findings": [], "slides": [], "gradient_text": [], "pdf": None,
        }, ensure_ascii=False, indent=2))
    else:
        print(f"qa  · deck     {deck}")
        print("\nFAIL · engine parity: the deck does not embed the full slides engine:")
        for marker in missing:
            print(f'  missing marker "{marker}" -> {ENGINE_MARKERS[marker][0]}')
        print("Port the missing feature(s) from 06-graphic-design/presentations/templates/base.html. "
              "For a file that is not a full deck (the layout catalogue), pass --no-engine-check.")
    return 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Playwright QA of an HTML deck: engine parity, overflow, chrome safe zone, "
                    "type floors, font, contrast, folios, optional PDF weight.",
    )
    parser.add_argument("deck", help="path to the deck HTML file")
    parser.add_argument("--viewport", default="1920x1080",
                        help="browser window size (default: 1920x1080)")
    parser.add_argument("--frame", default="1920x1080",
                        help="native slide frame, before the transform: scale() that fits it to the "
                             "window (default: 1920x1080). Geometries are brought back to this frame; "
                             "font sizes are not affected by the transform and are read as is")
    parser.add_argument("--min-font", type=float, default=MIN_FONT_PX,
                        help=f"content type floor in px (default: {MIN_FONT_PX:g})")
    parser.add_argument("--min-font-chrome", type=float, default=MIN_FONT_CHROME_PX,
                        help=f"floor in px for the label register: text inside .chrome, label classes "
                             f"(eyebrow, folio, signature...) and monospace text "
                             f"(default: {MIN_FONT_CHROME_PX:g}). Contrast still applies to it")
    parser.add_argument("--font", action="append", default=[], metavar="FAMILY",
                        help="allowed brand font family (repeatable). Default: the font tokens of "
                             "--tokens or of a discovered brand/tokens.json / 01-brand/tokens.json, "
                             "else the deck's --font-display / --font-body / --font-mono variables")
    parser.add_argument("--tokens", metavar="PATH",
                        help="DTCG tokens file to read font families from (default: the first "
                             "brand/tokens.json or 01-brand/tokens.json found walking up from the "
                             "deck, then from this script, up to the repository root)")
    parser.add_argument("--folio", default=FOLIO_DEFAULT, metavar="SELECTOR",
                        help=f'folio selector on each slide (default: "{FOLIO_DEFAULT}")')
    parser.add_argument("--no-folio", action="store_true",
                        help="skip the folio check (a format without folios)")
    parser.add_argument("--no-engine-check", action="store_true",
                        help="skip the engine parity check (for a file that is not a full deck, "
                             "such as _examples/deck-catalogue/catalogue.html)")
    parser.add_argument("--bleed", action="append", default=[], metavar="SELECTOR",
                        help="extra selector to skip (intentional full-bleed layer), repeatable")
    parser.add_argument("--lang", metavar="CODE",
                        help="audit the deck in this language: after loading, call "
                             "window.__setLang(CODE), the switch bilingual decks expose. A deck "
                             "without it is audited in its loaded language, with a [lang] warning. "
                             "Audit a bilingual deck in each language; the longer one overflows first")
    parser.add_argument("--wait", type=int, default=DEFAULT_WAIT_MS, metavar="MS",
                        help=f"wait after activating a slide, in ms (default: {DEFAULT_WAIT_MS}). "
                             "Raise to 2000-4000 for decks with a JS autofit that converges "
                             "over several frames")
    parser.add_argument("--max-per-slide", type=int, default=MAX_PER_SLIDE, metavar="N",
                        help=f"findings listed per slide and per type (default: {MAX_PER_SLIDE}, "
                             "0 = list everything). Totals are always computed before the cap")
    parser.add_argument("--format", choices=("text", "json"), default="text",
                        help="output format (default: text)")
    parser.add_argument("--screenshots", metavar="DIR", nargs="?", const=TMP_DIR,
                        help=f"save one PNG per slide (default folder: {TMP_DIR})")
    parser.add_argument("--with-pdf", action="store_true",
                        help=f"also render a PDF to {TMP_DIR}/<deck>.pdf through the deck's print "
                             "hooks and fail when its average weight per slide is below "
                             "--min-kb-per-slide (collapsed pages)")
    parser.add_argument("--min-kb-per-slide", type=float, default=MIN_KB_PER_SLIDE, metavar="KB",
                        help=f"threshold for --with-pdf (default: {MIN_KB_PER_SLIDE} KB per slide; "
                             "raise to 150-200 for image-heavy decks)")
    return parser


def _size_or_exit(value: str) -> dict:
    try:
        return parse_size(value)
    except ValueError as err:
        sys.stderr.write(f"{err}\n")
        sys.exit(2)


def _deck_url(path: Path) -> str:
    resolved = path.resolve()
    if not resolved.is_file():
        sys.stderr.write(f"file not found: {resolved}\n")
        sys.exit(2)
    return resolved.as_uri()


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    deck = Path(args.deck)
    viewport = _size_or_exit(args.viewport)
    frame = _size_or_exit(args.frame)
    url = _deck_url(deck)

    # ---- 0. engine parity, before any browser ----
    if not args.no_engine_check:
        missing = check_engine_parity(deck)
        if missing:
            return report_engine_failure(args, deck, missing)

    deck_findings: list[dict] = []
    brand: list[str] = []
    fonts_source = None
    if args.font:
        brand, fonts_source = list(args.font), "--font"
    else:
        tokens_path = Path(args.tokens) if args.tokens else find_tokens_file(deck)
        if tokens_path is not None and tokens_path.is_file():
            try:
                brand = brand_families(read_tokens(tokens_path))
            except ValueError as err:
                sys.stderr.write(f"{err}\n")
                return 2
            fonts_source = f"tokens: {_display_path(tokens_path)}"
        elif tokens_path is not None:
            deck_findings.append(finding(
                "warning", "font",
                f"tokens file not found: {tokens_path}; falling back to the deck's CSS variables"))

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.stderr.write("Playwright is not installed. Run:\n"
                         "  pip install playwright && playwright install chromium\n")
        return 2

    shots_dir = Path(args.screenshots) if args.screenshots else None
    if shots_dir:
        shots_dir.mkdir(parents=True, exist_ok=True)
    folio_sel = None if args.no_folio else args.folio
    bleed = BLEED + args.bleed
    lang_missing = False
    pdf = None

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            context = browser.new_context(viewport=viewport, reduced_motion="reduce")
            page = context.new_page()
            page.goto(url, wait_until="networkidle")
            page.add_style_tag(content=SETTLE_CSS)
            page.wait_for_timeout(args.wait)

            if args.lang:
                if page.evaluate("typeof window.__setLang === 'function'"):
                    page.evaluate("(code) => window.__setLang(code)", args.lang)
                    page.wait_for_timeout(args.wait)
                else:
                    lang_missing = True

            if not brand:
                brand = families_from_variables(page.evaluate(FONT_VARIABLES_JS, list(FONT_VARIABLES)))
                if brand:
                    fonts_source = "deck CSS variables " + " / ".join(FONT_VARIABLES)

            selector = next(
                (s for s in SLIDE_SELECTORS
                 if page.evaluate("(s) => document.querySelectorAll(s).length", s)),
                None,
            )
            if not selector:
                sys.stderr.write(f"no {' or '.join(SLIDE_SELECTORS)} element found in this deck\n")
                return 2
            total = page.evaluate("(s) => document.querySelectorAll(s).length", selector)
            raws = collect(page, selector, total, bleed, frame["width"], args.wait,
                           shots_dir, folio_sel)
            if args.with_pdf:
                pdf = render_pdf(page, deck, frame, total, args.min_kb_per_slide)
        finally:
            browser.close()

    # ---- audit ----
    if lang_missing:
        deck_findings.append(finding(
            "warning", "lang",
            f'window.__setLang is missing: the deck was audited in its loaded language, '
            f'not in "{args.lang}"'))
    if not brand:
        deck_findings.append(finding(
            "warning", "font",
            "no known brand family (--font, tokens file, or --font-display / --font-body / "
            "--font-mono variables): the font is not checked"))
    if pdf is not None:
        failed = pdf_finding(pdf)
        if failed:
            deck_findings.append(failed)

    slides, gradients, uncapped = [], [], list(deck_findings)
    per_slide: list[list[dict]] = []
    for index, raw in enumerate(raws, start=1):
        findings, slide_gradients = audit_slide(raw, args.min_font, args.min_font_chrome, brand)
        per_slide.append(findings)
        gradients.extend(f"slide {index:02d} · {g}" for g in slide_gradients)
    if folio_sel:
        for index, f in audit_folios([raw["folio"] for raw in raws]):
            per_slide[index - 1].append(f)
    for index, findings in enumerate(per_slide, start=1):
        uncapped.extend(findings)
        slides.append({"slide": index, "findings": cap(findings, args.max_per_slide)})

    listed = deck_findings + [f for entry in slides for f in entry["findings"]]
    summary = {
        "deck": str(deck), "viewport": args.viewport, "frame": args.frame,
        "selector": selector, "slides": len(slides),
        "fonts": brand, "fonts_source": fonts_source if brand else None,
        "min_font": args.min_font, "min_font_chrome": args.min_font_chrome,
        "max_per_slide": args.max_per_slide,
        "errors": count(listed, "error"), "warnings": count(listed, "warning"),
        "errors_total": count(uncapped, "error"), "warnings_total": count(uncapped, "warning"),
        "by_type": tally(uncapped),
    }
    ctx = {
        "summary": summary,
        "engine": {"checked": not args.no_engine_check, "missing": []},
        "deck_findings": deck_findings,
        "slides": slides,
        "gradient_text": gradients,
        "pdf": pdf,
    }
    if args.format == "json":
        print(json.dumps(ctx, ensure_ascii=False, indent=2))
    else:
        text_report(ctx)
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
