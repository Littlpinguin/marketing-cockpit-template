# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), tests/test_qa.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Tests for 06-graphic-design/presentations/scripts/qa.py.

Two layers:
- pure-Python tests (colours, contrast, fonts, tokens, registers, folios, cap,
  engine parity): no browser, always run;
- deck tests that drive a real headless Chromium on small fictional decks:
  skipped cleanly when Playwright or Chromium is missing.

Fixtures use an invented brand (navy #1E40AF, amber #F59E0B, slate #0F172A,
snow #F8FAFC) and generic font names. Run: python3 -m pytest scripts/tests -q
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"
QA = ROOT / "scripts" / "qa.py"


def _load_qa():
    spec = importlib.util.spec_from_file_location("slides_qa", QA)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa = _load_qa()

NAVY = (30, 64, 175)      # #1E40AF
AMBER = (245, 158, 11)    # #F59E0B
SLATE = (15, 23, 42)      # #0F172A
SNOW = (248, 250, 252)    # #F8FAFC

FICTIONAL_TOKENS = {
    "color": {"primary": {"$value": "#1E40AF"}, "accent": {"$value": "#F59E0B"}},
    "font": {
        "$type": "fontFamily",
        "primary": {"$value": ["Inter", "system-ui", "sans-serif"]},
        "mono": {"$value": ["ui-monospace", "Menlo", "monospace"]},
        "accent": {"$value": "'Fictive Serif', Georgia, serif"},
    },
}


# ===========================================================================
# Pure Python
# ===========================================================================

# --- colours ----------------------------------------------------------------

@pytest.mark.parametrize(
    "css, expected",
    [
        ("rgb(30, 64, 175)", (30, 64, 175, 1.0)),
        ("rgba(30, 64, 175, 0.5)", (30, 64, 175, 0.5)),
        ("rgb(30 64 175 / 50%)", (30, 64, 175, 0.5)),
        ("#1E40AF", (30, 64, 175, 1.0)),
        ("#1e40af", (30, 64, 175, 1.0)),
        ("#FFF", (255, 255, 255, 1.0)),
        ("transparent", (0, 0, 0, 0.0)),
        ("rgba(0, 0, 0, 0)", (0, 0, 0, 0.0)),
        ("rgb(15 23 42 / 0.35)", (15, 23, 42, 0.35)),
        ("rgba(15 23 42 / 65%)", (15, 23, 42, 0.65)),
    ],
)
def test_parse_color(css, expected):
    assert qa.parse_color(css) == pytest.approx(expected)


@pytest.mark.parametrize("css", ["", None, "currentColor", "var(--primary)", "not a colour", "#12"])
def test_parse_color_unknown(css):
    assert qa.parse_color(css) is None


def test_alpha_is_clamped():
    assert qa.parse_color("rgba(0, 0, 0, 1.5)")[3] == 1.0
    assert qa.parse_color("rgba(0, 0, 0, -0.2)")[3] == 0.0


# --- luminance and contrast (WCAG 2.x) ---------------------------------------

def test_luminance_bounds():
    assert qa.luminance((255, 255, 255)) == pytest.approx(1.0, abs=1e-6)
    assert qa.luminance((0, 0, 0)) == pytest.approx(0.0, abs=1e-6)


def test_black_on_white_is_21():
    assert qa.contrast_ratio((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0, abs=0.01)


def test_contrast_is_symmetric_and_identity_is_one():
    assert qa.contrast_ratio(NAVY, SLATE) == pytest.approx(qa.contrast_ratio(SLATE, NAVY))
    assert qa.contrast_ratio(SLATE, SLATE) == pytest.approx(1.0)


def test_reading_pair_passes_and_decorative_pair_fails():
    assert qa.contrast_ratio(SLATE, SNOW) > 4.5
    assert qa.contrast_ratio(AMBER, SNOW) < 4.5


@pytest.mark.parametrize(
    "size, bold, expected",
    [(18.0, False, 4.5), (23.9, False, 4.5), (24.0, False, 3.0), (40.0, False, 3.0),
     (19.0, True, 3.0), (18.0, True, 4.5)],
)
def test_contrast_threshold(size, bold, expected):
    assert qa.contrast_threshold(size, bold=bold) == expected


# --- background stack ---------------------------------------------------------

def test_composite():
    assert qa.composite((10, 20, 30, 1.0), (255, 255, 255)) == (10, 20, 30)
    assert qa.composite((0, 0, 0, 0.5), (255, 255, 255)) == (128, 128, 128)
    assert qa.composite((0, 0, 0, 0.0), SNOW) == SNOW


def test_resolve_background_stops_at_first_opaque():
    stack = ["rgba(0, 0, 0, 0)", "rgba(255, 255, 255, 0.5)", "rgb(15, 23, 42)"]
    assert qa.resolve_background(stack) == (135, 139, 149)
    assert qa.resolve_background(["rgb(255 255 255 / 50%)", "rgb(15 23 42 / 100%)"]) == (135, 139, 149)


def test_resolve_background_defaults_to_white():
    assert qa.resolve_background([]) == (255, 255, 255)
    assert qa.resolve_background(["rgba(0, 0, 0, 0)"]) == (255, 255, 255)


@pytest.mark.parametrize(
    "css, expected",
    [("none", True), ("", True), (None, True),
     ("linear-gradient(90deg, rgb(30, 64, 175), rgb(245, 158, 11))", False),
     ('url("file:///photo.jpg")', False)],
)
def test_is_plain_background(css, expected):
    assert qa.is_plain_background(css) is expected


def test_gradient_before_opaque_layer_is_not_uniform():
    levels = [{"c": "rgba(0, 0, 0, 0)", "i": "linear-gradient(red, blue)"}, {"c": "rgb(255, 255, 255)", "i": "none"}]
    assert qa.resolve_background_and_uniformity(levels)[1] is False


def test_effective_opacity_stops_at_the_opaque_background():
    levels = [
        {"c": "rgba(0, 0, 0, 0)", "i": "none", "o": 0.5},
        {"c": "rgba(0, 0, 0, 0)", "i": "none", "o": 0.8},
        {"c": "rgb(248, 250, 252)", "i": "none", "o": 0.1},   # opaque: excluded
        {"c": "rgba(0, 0, 0, 0)", "i": "none", "o": 0.1},     # beyond: ignored
    ]
    assert qa.effective_opacity(levels) == pytest.approx(0.4)


# --- fonts -------------------------------------------------------------------

@pytest.mark.parametrize(
    "css, expected",
    [('Inter, "Helvetica Neue", sans-serif', "Inter"), ('"Inter", sans-serif', "Inter"),
     ("  ui-monospace , monospace ", "ui-monospace"), ("", "")],
)
def test_first_family(css, expected):
    assert qa.first_family(css) == expected


def test_font_matches():
    assert qa.font_matches("Inter, sans-serif", "Inter")
    assert qa.font_matches('"inter", sans-serif', ["Inter"])
    assert qa.font_matches("'Fictive Serif', serif", ["Inter", "Fictive Serif"])
    assert not qa.font_matches('"Helvetica Neue", Arial, sans-serif', ["Inter"])
    assert not qa.font_matches("", ["Inter"])


def test_monospace_needs_permission():
    assert not qa.font_matches("ui-monospace, monospace", ["Inter"])
    assert qa.font_matches("ui-monospace, monospace", ["Inter"], mono_allowed=True)
    assert qa.font_matches("Menlo, monospace", ["Inter"], mono_allowed=True)


@pytest.mark.parametrize(
    "css, expected",
    [("'JetBrains Mono', ui-monospace, monospace", True),
     ("Menlo, monospace", True),
     ("'Fira Code', monospace", True),          # mono through its generic fallback
     ("ui-monospace", True),
     ("Inter, system-ui, sans-serif", False),
     ("'Fictive Serif', Georgia, serif", False),
     ("", False)],
)
def test_is_monospace_stack(css, expected):
    assert qa.is_monospace_stack(css) is expected


# --- tokens ------------------------------------------------------------------

def test_brand_families_first_family_of_each_token():
    assert qa.brand_families(FICTIONAL_TOKENS) == ["Inter", "Fictive Serif"]
    assert qa.brand_families({"color": {}}) == []


def test_read_tokens_errors(tmp_path):
    with pytest.raises(ValueError, match="not found"):
        qa.read_tokens(tmp_path / "tokens.json")
    broken = tmp_path / "tokens.json"
    broken.write_text("{ not json", encoding="utf-8")
    with pytest.raises(ValueError, match="unreadable"):
        qa.read_tokens(broken)


def test_families_from_variables_skips_generics_and_duplicates():
    values = ["'Inter', system-ui, sans-serif", "Inter, sans-serif", "monospace",
              "'JetBrains Mono', ui-monospace, monospace"]
    assert qa.families_from_variables(values) == ["Inter", "JetBrains Mono"]


def _repo(tmp_path: Path, name: str) -> Path:
    root = tmp_path / name
    (root / ".git").mkdir(parents=True)
    return root


def test_find_tokens_prefers_brand_over_01_brand(tmp_path):
    root = _repo(tmp_path, "repo")
    for folder in ("brand", "01-brand"):
        (root / folder).mkdir()
        (root / folder / "tokens.json").write_text("{}", encoding="utf-8")
    deck = root / "presentations" / "deck.html"
    deck.parent.mkdir()
    deck.write_text("", encoding="utf-8")
    assert qa.find_tokens_file(deck, script=tmp_path / "elsewhere" / "qa.py") == root / "brand" / "tokens.json"


def test_find_tokens_falls_back_on_the_script_repo(tmp_path):
    deck_repo = _repo(tmp_path, "decks")
    deck = deck_repo / "deck.html"
    deck.write_text("", encoding="utf-8")
    tool_repo = _repo(tmp_path, "tool")
    (tool_repo / "01-brand").mkdir()
    (tool_repo / "01-brand" / "tokens.json").write_text("{}", encoding="utf-8")
    script = tool_repo / "a" / "b" / "scripts" / "qa.py"
    assert qa.find_tokens_file(deck, script=script) == tool_repo / "01-brand" / "tokens.json"


def test_find_tokens_stops_at_the_repo_root(tmp_path):
    (tmp_path / "brand").mkdir()
    (tmp_path / "brand" / "tokens.json").write_text("{}", encoding="utf-8")  # above the repo
    root = _repo(tmp_path, "repo")
    deck = root / "deck.html"
    deck.write_text("", encoding="utf-8")
    assert qa.find_tokens_file(deck, script=root / "scripts" / "qa.py") is None


def test_parse_size():
    assert qa.parse_size("1920x1080") == {"width": 1920, "height": 1080}
    for bad in ("1920", "axb", "0x1080"):
        with pytest.raises(ValueError):
            qa.parse_size(bad)


# --- registers and floors (raw values as the collector returns them) ---------

def _text(**over):
    base = {"cls": "body", "tag": "P", "ctx": "", "text": "a line", "words": 2, "fs": 28.0,
            "weight": 400, "font": "Inter, sans-serif", "color": "rgb(15, 23, 42)",
            "bgs": [{"c": "rgb(248, 250, 252)", "i": "none", "o": 1.0}],
            "gradient": False, "chrome": False, "label": False}
    base.update(over)
    return base


def _audit(*texts, min_font=18, min_font_chrome=12, brand=("Inter",)):
    findings, _ = qa.audit_texts({"texts": list(texts)}, min_font, min_font_chrome, list(brand))
    return findings


def _types(findings, level=None):
    return [f["type"] for f in findings if level is None or f["level"] == level]


@pytest.mark.parametrize(
    "over, register",
    [({"chrome": True, "label": True}, "chrome"),
     ({"label": True}, "label"),
     ({"font": "'JetBrains Mono', monospace"}, "mono"),
     ({}, "content")],
)
def test_text_register(over, register):
    assert qa.text_register(_text(**over)) == register


def test_content_floor_is_18():
    assert "type-floor" in _types(_audit(_text(fs=16.0)), "error")
    assert "type-floor" not in _types(_audit(_text(fs=18.0)))


def test_label_register_uses_the_chrome_floor():
    for over in ({"chrome": True, "label": True}, {"label": True},
                 {"font": "'JetBrains Mono', ui-monospace, monospace"}):
        assert "type-floor" not in _types(_audit(_text(fs=12.0, **over))), over
        found = _audit(_text(fs=11.0, **over))
        assert "type-floor" in _types(found, "error"), over
        assert "chrome floor" in found[0]["message"]


def test_tight_body_only_on_content():
    assert "tight-body" in _types(_audit(_text(fs=20.0)), "warning")
    assert "tight-body" not in _types(_audit(_text(fs=20.0, tag="H2")))
    assert "tight-body" not in _types(_audit(_text(fs=13.0, label=True)))


def test_long_label_is_a_warning():
    sentence = _text(fs=13.0, font="'JetBrains Mono', monospace", words=20, text="a long sentence")
    found = _audit(sentence)
    assert "long-label" in _types(found, "warning")
    assert not _types(found, "error")
    assert "long-label" not in _types(_audit(_text(fs=13.0, label=True, words=4)))


def test_undeclared_mono_warns_outside_labels_and_code():
    mono = "'JetBrains Mono', ui-monospace, monospace"
    assert _types(_audit(_text(font=mono)), "warning") == ["font"]
    assert "font" not in _types(_audit(_text(font=mono, label=True, fs=13.0)))
    assert "font" not in _types(_audit(_text(font=mono, tag="CODE")))
    assert "font" not in _types(_audit(_text(font=mono, cls="tick mono")))
    assert "font" in _types(_audit(_text(font=mono, cls="monogram")))
    assert "font" not in _types(_audit(_text(font=mono), brand=("Inter", "JetBrains Mono")))


def test_off_brand_font_is_an_error_and_no_brand_means_no_check():
    helvetica = _text(font='"Helvetica Neue", sans-serif')
    assert "font" in _types(_audit(helvetica), "error")
    assert "font" not in _types(_audit(helvetica, brand=()))


def test_opacity_lowers_contrast():
    faded = _text(bgs=[{"c": "rgba(0, 0, 0, 0)", "i": "none", "o": 0.3},
                       {"c": "rgb(248, 250, 252)", "i": "none", "o": 1.0}])
    found = _audit(faded)
    assert "contrast" in _types(found, "error")
    assert "opacity 0.30" in [f for f in found if f["type"] == "contrast"][0]["message"]
    assert "contrast" not in _types(_audit(_text()))


def test_gradient_text_is_listed_not_judged():
    found, gradients = qa.audit_texts(
        {"texts": [_text(gradient=True, color="rgba(0, 0, 0, 0)", cls="gradient-text", text="Go")]},
        18, 12, ["Inter"])
    assert gradients == ['.gradient-text "Go"']
    assert "contrast" not in _types(found)


def test_classless_target_is_named_by_its_ancestor():
    assert qa._target("", "STRONG", "nav-num") == ".nav-num strong"
    assert qa._target("eyebrow reveal", "SPAN", "x") == ".eyebrow.reveal"
    assert qa._target("", "P", "") == "p"


# --- folios ------------------------------------------------------------------

def test_folios():
    assert qa.audit_folios(["01 / 03", "02 / 03", "03 / 03"]) == []
    missing = qa.audit_folios(["01 / 02", None])
    assert missing[0][0] == 2 and "missing" in missing[0][1]["message"]
    backwards = qa.audit_folios(["01", "02", "01"])
    assert backwards[0][0] == 3 and "not increasing" in backwards[0][1]["message"]


# --- cap ---------------------------------------------------------------------

def _f(type_, level="error", n=0):
    return {"level": level, "type": type_, "message": f"{type_} {n}"}


def test_cap_under_the_limit_changes_nothing():
    findings = [_f("contrast", n=i) for i in range(5)]
    assert qa.cap(findings) == findings
    exact = [_f("contrast", n=i) for i in range(qa.MAX_PER_SLIDE)]
    assert not [f for f in qa.cap(exact) if f["level"] == "summary"]


def test_cap_summary_carries_the_hidden_count_and_never_counts():
    findings = [_f("contrast", n=i) for i in range(qa.MAX_PER_SLIDE + 5)]
    capped = qa.cap(findings)
    summaries = [f for f in capped if f["level"] == "summary"]
    assert len(summaries) == 1 and summaries[0]["hidden"] == 5
    assert "5 more" in summaries[0]["message"]
    assert qa.count(capped, "error") == qa.MAX_PER_SLIDE
    assert qa.count(capped, "warning") == 0


def test_cap_is_per_type_and_zero_disables_it():
    findings = ([_f("contrast", n=i) for i in range(qa.MAX_PER_SLIDE + 2)]
                + [_f("font", "warning", i) for i in range(qa.MAX_PER_SLIDE + 4)] + [_f("folio")])
    summaries = {f["type"]: f["hidden"] for f in qa.cap(findings) if f["level"] == "summary"}
    assert summaries == {"contrast": 2, "font": 4}
    assert qa.cap(findings, 0) == findings


def test_tally_ignores_summaries():
    findings = [_f("contrast"), _f("contrast", "warning"), {"level": "summary", "type": "contrast", "message": ""}]
    assert qa.tally(findings) == {"contrast": {"errors": 1, "warnings": 1}}


# --- engine parity -------------------------------------------------------------

def test_starter_embeds_every_engine_marker():
    """ENGINE_MARKERS must describe 06-graphic-design/presentations/templates/base.html: keep them in step."""
    assert qa.check_engine_parity(ROOT / "templates" / "base.html") == []


def test_engine_markers_accept_alternatives(tmp_path):
    deck = tmp_path / "deck.html"
    all_but_folios = " ".join(markers[0] for key, (_, markers) in qa.ENGINE_MARKERS.items()
                              if key != "auto-folios")
    deck.write_text(f"<!-- {all_but_folios} -->", encoding="utf-8")
    assert qa.check_engine_parity(deck) == ["auto-folios"]
    deck.write_text(f"<!-- {all_but_folios} SLIDE_COUNT -->", encoding="utf-8")
    assert qa.check_engine_parity(deck) == []


# ===========================================================================
# Deck tests: real headless Chromium
# ===========================================================================

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


browser = pytest.mark.skipif(not _chromium_available(),
                             reason="Playwright or Chromium is not installed on this machine")

# The skeleton mimics the engine: a native 1920x1080 frame fitted to the window
# by `transform: scale()`, so geometry is checked in native pixels while font
# sizes are read as computed.
SKELETON = """<!doctype html><html lang="en"><head><meta charset="utf-8"><style>
  body {{ margin: 0; font-family: Inter, sans-serif; overflow: hidden; }}
  #stage-frame {{ position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px;
                  background: #F8FAFC; }}
  .{kind} {{ display: none; position: absolute; inset: 0; background: #F8FAFC; }}
  .{kind}.active {{ display: block; }}
  .chrome-row.bottom {{ position: absolute; left: 40px; right: 40px; bottom: 0; height: 40px; }}
  .tag-folio {{ font-size: 14px; color: #0F172A; }}
  .body {{ position: absolute; left: 80px; top: 200px; font-size: 28px; color: #0F172A; }}
  {styles}
</style></head><body><div id="stage-frame">{slides}</div>
<script>
  const frame = document.getElementById('stage-frame');
  const fit = () => {{
    const f = Math.min(innerWidth / 1920, innerHeight / 1080);
    frame.style.transform = 'translate(-50%, -50%) scale(' + f + ')';
  }};
  addEventListener('resize', fit); fit();
</script></body></html>"""

SLIDE = """<section class="{kind} {active}">
  <div class="chrome"><div class="chrome-row bottom">
    <span class="tag-folio"><strong>{folio:02d}</strong> / {total}</span>
  </div></div>
  <p class="body">A readable line of content</p>
  {extra}
</section>"""

# The minimal deck does not embed the engine (parity is tested apart) and names
# its font explicitly, so no tokens file is involved.
DEFAULTS = ("--no-engine-check", "--font", "Inter", "--wait", "200")


def write_deck(folder: Path, name: str, extras: list[str], styles: str = "", kind: str = "slide") -> Path:
    slides = "".join(
        SLIDE.format(kind=kind, active="active" if i == 0 else "", folio=i + 1,
                     total=len(extras), extra=extra)
        for i, extra in enumerate(extras)
    )
    path = folder / name
    path.write_text(SKELETON.format(kind=kind, slides=slides, styles=styles), encoding="utf-8")
    return path


def run(deck: Path, *options: str, defaults=DEFAULTS) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(QA), str(deck), *defaults, *options],
                          capture_output=True, text=True, cwd=str(ROOT), timeout=180)


def run_json(deck: Path, *options: str, defaults=DEFAULTS) -> tuple[subprocess.CompletedProcess, dict]:
    result = run(deck, "--format", "json", *options, defaults=defaults)
    return result, json.loads(result.stdout)


def all_findings(report: dict) -> list[dict]:
    return report["deck_findings"] + [f for s in report["slides"] for f in s["findings"]]


def findings_of(deck: Path, *options: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
    result, report = run_json(deck, *options)
    return result, all_findings(report)


def of_type(findings: list[dict], type_: str, level: str | None = None) -> list[dict]:
    return [f for f in findings if f["type"] == type_ and (level is None or f["level"] == level)]


@browser
def test_clean_deck(tmp_path):
    result = run(write_deck(tmp_path, "clean.html", ["", ""]))
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All slides clean" in result.stdout


@browser
def test_catalogue_selector_is_detected(tmp_path):
    deck = write_deck(tmp_path, "plates.html", ["", ""], kind="plate")
    result, report = run_json(deck)
    assert report["summary"]["selector"] == ".plate"
    assert report["summary"]["slides"] == 2
    assert result.returncode == 0, result.stdout


@browser
def test_content_type_floor(tmp_path):
    deck = write_deck(tmp_path, "small.html", ['<p class="note">A note far too small</p>'],
                      styles=".note { position: absolute; left: 80px; top: 400px; font-size: 12px; color: #0F172A; }")
    result, found = findings_of(deck)
    assert result.returncode == 1
    assert any("12px below the content floor 18px" in f["message"] for f in of_type(found, "type-floor"))


@browser
def test_floor_raised_by_option(tmp_path):
    deck = write_deck(tmp_path, "twenty.html", ['<p class="note">A twenty pixel note</p>'],
                      styles=".note { position: absolute; left: 80px; top: 400px; font-size: 20px; color: #0F172A; }")
    _, default = findings_of(deck)
    assert not of_type(default, "type-floor")
    _, raised = findings_of(deck, "--min-font", "24")
    assert of_type(raised, "type-floor")


@browser
def test_mono_label_takes_the_chrome_floor(tmp_path):
    styles = (".cap { position: absolute; left: 80px; top: 400px; color: #0F172A;"
              " font-family: 'JetBrains Mono', ui-monospace, monospace; }"
              ".c12 { font-size: 12px; } .c11 { top: 500px; font-size: 11px; }")
    deck = write_deck(tmp_path, "mono.html", ['<p class="cap c12">fig. 1 · source</p>'], styles=styles)
    result, found = findings_of(deck)
    assert not of_type(found, "type-floor"), result.stdout
    deck = write_deck(tmp_path, "mono11.html", ['<p class="cap c11">fig. 1 · source</p>'], styles=styles)
    _, found = findings_of(deck)
    assert any("chrome floor" in f["message"] for f in of_type(found, "type-floor", "error"))


@browser
def test_eyebrow_class_takes_the_chrome_floor(tmp_path):
    deck = write_deck(tmp_path, "eyebrow.html", ['<span class="eyebrow">chapter one</span>'],
                      styles=".eyebrow { position: absolute; left: 80px; top: 120px; font-size: 13px; color: #0F172A; }")
    result, found = findings_of(deck)
    assert not of_type(found, "type-floor")
    assert result.returncode == 0, result.stdout


@browser
def test_insufficient_contrast(tmp_path):
    deck = write_deck(tmp_path, "contrast.html", ['<p class="pale">Pale text on snow</p>'],
                      styles=".pale { position: absolute; left: 80px; top: 400px; font-size: 28px; color: #F59E0B; }")
    result, found = findings_of(deck)
    assert result.returncode == 1
    assert any("below 3.0:1" in f["message"] for f in of_type(found, "contrast"))


@browser
def test_opacity_is_folded_into_contrast(tmp_path):
    deck = write_deck(tmp_path, "faded.html", ['<p class="faded">Faded text</p>'],
                      styles=".faded { position: absolute; left: 80px; top: 400px; font-size: 28px;"
                             " color: #0F172A; opacity: 0.25; }")
    result, found = findings_of(deck)
    assert result.returncode == 1
    assert any("opacity 0.25" in f["message"] for f in of_type(found, "contrast", "error"))


@browser
def test_non_uniform_background_is_a_warning(tmp_path):
    deck = write_deck(
        tmp_path, "gradient.html", ['<div class="band"><p class="over">On a gradient</p></div>'],
        styles=(".band { position: absolute; left: 80px; top: 400px; width: 900px; height: 120px;"
                " background: linear-gradient(90deg, #1E40AF 0%, #F59E0B 100%); }"
                ".over { font-size: 28px; color: #0F172A; margin: 0; }"))
    result, found = findings_of(deck)
    assert any("non-uniform background" in f["message"] for f in of_type(found, "contrast", "warning"))
    assert result.returncode == 0


@browser
def test_gradient_text_is_listed_apart(tmp_path):
    deck = write_deck(
        tmp_path, "gradient-text.html", ['<h2 class="gradient-text">Gradient <span>title</span></h2>'],
        styles=(".gradient-text { position: absolute; left: 80px; top: 400px; font-size: 60px;"
                " background: linear-gradient(90deg, #1E40AF, #F59E0B);"
                " -webkit-background-clip: text; background-clip: text; color: transparent; }"))
    _, report = run_json(deck)
    assert any("gradient-text" in line for line in report["gradient_text"])
    assert any(".gradient-text span" in line for line in report["gradient_text"])   # inherits the clip
    assert not of_type(all_findings(report), "contrast")


@browser
def test_off_brand_font(tmp_path):
    deck = write_deck(tmp_path, "font.html", ['<p class="foreign">Helvetica text</p>'],
                      styles=(".foreign { position: absolute; left: 80px; top: 400px; font-size: 28px;"
                              ' color: #0F172A; font-family: "Helvetica Neue", sans-serif; }'))
    result, found = findings_of(deck)
    assert result.returncode == 1
    assert any("Helvetica Neue" in f["message"] for f in of_type(found, "font", "error"))


@browser
def test_monospace_on_code_and_in_chrome_passes(tmp_path):
    deck = write_deck(tmp_path, "code.html", ['<code class="snippet">python3 qa.py deck.html</code>'],
                      styles=(".snippet { position: absolute; left: 80px; top: 400px; font-size: 28px;"
                              " color: #0F172A; font-family: ui-monospace, monospace; }"
                              ".tag-folio { font-family: 'JetBrains Mono', ui-monospace, monospace; }"))
    result, found = findings_of(deck)
    assert not of_type(found, "font"), result.stdout
    assert result.returncode == 0


@browser
def test_undeclared_monospace_outside_labels_is_a_warning(tmp_path):
    deck = write_deck(tmp_path, "kicker.html", ['<p class="kicker">A monospace kicker</p>'],
                      styles=(".kicker { position: absolute; left: 80px; top: 400px; font-size: 28px;"
                              " color: #0F172A; font-family: 'JetBrains Mono', ui-monospace, monospace; }"))
    result, found = findings_of(deck)
    fonts = of_type(found, "font")
    assert fonts and all(f["level"] == "warning" for f in fonts)
    assert result.returncode == 0


@browser
def test_mono_class_must_be_an_exact_token(tmp_path):
    styles = (".m { position: absolute; left: 80px; top: 400px; font-size: 28px;"
              " color: #0F172A; font-family: ui-monospace, monospace; }")
    _, found = findings_of(write_deck(tmp_path, "monogram.html", ['<p class="m monogram">AB</p>'], styles=styles))
    assert of_type(found, "font")
    _, found = findings_of(write_deck(tmp_path, "mono.html", ['<p class="m mono">42</p>'], styles=styles))
    assert not of_type(found, "font")


@browser
def test_chrome_floor_has_its_own_threshold(tmp_path):
    deck = write_deck(tmp_path, "chrome10.html", [""], styles=".tag-folio { font-size: 10px; }")
    result, found = findings_of(deck)
    floors = of_type(found, "type-floor")
    assert floors and "chrome floor (chrome register) 12px" in floors[0]["message"]
    assert result.returncode == 1
    _, found = findings_of(write_deck(tmp_path, "chrome12.html", [""], styles=".tag-folio { font-size: 12px; }"))
    assert not of_type(found, "type-floor")
    _, found = findings_of(write_deck(tmp_path, "chrome-opt.html", [""], styles=".tag-folio { font-size: 12px; }"),
                           "--min-font-chrome", "14")
    assert of_type(found, "type-floor")


@browser
def test_geometry_is_native_at_a_small_viewport(tmp_path):
    """20 native px above the chrome pass, and a 3 native px overflow is caught, at 1024x600."""
    gap = write_deck(tmp_path, "gap.html", ['<div class="foot"></div>'],
                     styles=".foot { position: absolute; left: 80px; top: 1000px; width: 400px; height: 20px; background: #1E40AF; }")
    result, found = findings_of(gap, "--viewport", "1024x600")
    assert not of_type(found, "chrome-gap"), result.stdout
    over = write_deck(tmp_path, "over.html", ['<div class="thin"></div>'],
                      styles=".thin { position: absolute; left: 1800px; top: 300px; width: 123px; height: 100px; background: #1E40AF; }")
    _, found = findings_of(over, "--viewport", "1024x600")
    overflows = of_type(found, "overflow")
    assert overflows and "R=3" in overflows[0]["message"]


@browser
def test_scale_does_not_touch_font_size(tmp_path):
    deck = write_deck(tmp_path, "type-native.html", ['<p class="note">A note far too small</p>'],
                      styles=".note { position: absolute; left: 80px; top: 400px; font-size: 12px; color: #0F172A; }")
    # A window wider than the fitted frame: if the scale factor leaked into the
    # font size, 12px would read as 18px and pass.
    _, found = findings_of(deck, "--viewport", "1600x600")
    floors = of_type(found, "type-floor")
    assert floors and "type 12px" in floors[0]["message"]


@browser
def test_overflow_detected_and_bleed_ignored(tmp_path):
    styles = ".wide { position: absolute; left: 1800px; top: 300px; width: 400px; height: 200px; background: #1E40AF; }"
    result, found = findings_of(write_deck(tmp_path, "overflow.html", ['<div class="wide"></div>'], styles=styles))
    assert result.returncode == 1
    assert any(".wide" in f["message"] for f in of_type(found, "overflow"))
    _, found = findings_of(write_deck(tmp_path, "bleed.html", ['<div class="wide" data-bleed></div>'], styles=styles))
    assert not of_type(found, "overflow")


@browser
def test_slide_bg_and_aurora_are_exempt(tmp_path):
    extra = ('<div class="slide-bg"><img class="photo" alt=""></div>'
             '<div class="aurora"><i class="orb"></i></div>')
    styles = (".photo { position: absolute; left: -40px; top: -40px; width: 2000px; height: 1160px; background: #1E40AF; }"
              ".orb { position: absolute; left: 1700px; top: 900px; width: 600px; height: 600px; background: #F59E0B; }")
    result, found = findings_of(write_deck(tmp_path, "bg.html", [extra], styles=styles))
    assert not of_type(found, "overflow") and not of_type(found, "chrome-gap"), result.stdout


@browser
def test_chrome_safe_zone(tmp_path):
    deck = write_deck(tmp_path, "chrome.html", ['<div class="foot"></div>'],
                      styles=".foot { position: absolute; left: 80px; top: 1030px; width: 400px; height: 20px; background: #1E40AF; }")
    result, found = findings_of(deck)
    assert result.returncode == 1
    assert any(".foot" in f["message"] for f in of_type(found, "chrome-gap"))


@browser
def test_settled_state_is_audited(tmp_path):
    """An element still waiting for its transition delay is audited in its final state.

    Slides switch on visibility, as in the engine, so activating slide 2 starts
    a real transition: without the settle step its text would still be at
    opacity 0 when measured, hence invisible and silently skipped.
    """
    deck = write_deck(tmp_path, "stagger.html", ["", '<p class="late">Late small text</p>'],
                      styles=(".slide { display: block; visibility: hidden; }"
                              ".slide.active { visibility: visible; }"
                              ".late { position: absolute; left: 80px; top: 400px; font-size: 12px;"
                              " color: #0F172A; opacity: 0; transition: opacity 1s 5s; }"
                              ".slide.active .late { opacity: 1; }"))
    _, report = run_json(deck)
    assert of_type(report["slides"][1]["findings"], "type-floor")


@browser
def test_folios(tmp_path):
    missing = write_deck(tmp_path, "no-folio.html", [""])
    missing.write_text(missing.read_text(encoding="utf-8").replace("tag-folio", "tag-mute"), encoding="utf-8")
    result, found = findings_of(missing)
    assert result.returncode == 1
    assert any("missing" in f["message"] for f in of_type(found, "folio"))
    result, found = findings_of(missing, "--no-folio")
    assert not of_type(found, "folio") and result.returncode == 0

    backwards = write_deck(tmp_path, "folios.html", ["", "", ""])
    backwards.write_text(backwards.read_text(encoding="utf-8").replace("<strong>03</strong>", "<strong>01</strong>"),
                         encoding="utf-8")
    _, found = findings_of(backwards)
    assert any("not increasing" in f["message"] for f in of_type(found, "folio"))

    nav_num = write_deck(tmp_path, "nav-num.html", ["", ""])
    nav_num.write_text(nav_num.read_text(encoding="utf-8").replace("tag-folio", "nav-num"), encoding="utf-8")
    _, found = findings_of(nav_num)
    assert not of_type(found, "folio")


@browser
def test_usage_errors_exit_2(tmp_path):
    empty = tmp_path / "empty.html"
    empty.write_text("<!doctype html><html><body><p>nothing</p></body></html>", encoding="utf-8")
    assert run(empty).returncode == 2
    assert run(tmp_path / "missing.html").returncode == 2


@browser
def test_truncation_is_reported(tmp_path):
    blocks = "".join(f'<div class="d{i} out"></div>' for i in range(25))
    deck = write_deck(tmp_path, "truncated.html", [blocks],
                      styles=".out { position: absolute; left: 1850px; top: 100px; width: 200px; height: 20px; background: #1E40AF; }")
    _, found = findings_of(deck)
    truncated = of_type(found, "truncated")
    assert truncated and "5 overflows not listed" in truncated[0]["message"]
    assert truncated[0]["level"] == "warning"


@browser
def test_language_switch(tmp_path):
    deck = write_deck(
        tmp_path, "bilingual.html",
        ['<p class="fine">short</p>'
         '<script>window.__setLang = l => { document.querySelector(".fine").textContent ='
         ' l === "fr" ? "version française" : "short"; };</script>'],
        styles=".fine { position: absolute; left: 80px; top: 400px; font-size: 14px; color: #0F172A; }")
    _, found = findings_of(deck, "--lang", "fr")
    assert not of_type(found, "lang")
    assert any("type 14px" in f["message"] for f in of_type(found, "type-floor"))

    single = write_deck(tmp_path, "single.html", [""])
    result, found = findings_of(single, "--lang", "fr")
    lang = of_type(found, "lang")
    assert lang and "__setLang is missing" in lang[0]["message"] and lang[0]["level"] == "warning"
    assert result.returncode == 0


@browser
def test_cap_does_not_inflate_the_summary(tmp_path):
    blocks = "".join(f'<p class="p{i} tiny">note</p>' for i in range(12))
    deck = write_deck(tmp_path, "cap.html", [blocks],
                      styles=".tiny { position: relative; font-size: 10px; color: #0F172A; }")
    _, report = run_json(deck)
    listed = all_findings(report)
    assert [f for f in listed if f["level"] == "summary"]
    assert report["summary"]["errors"] == sum(1 for f in listed if f["level"] == "error")
    assert report["summary"]["errors_total"] > report["summary"]["errors"]
    assert report["summary"]["by_type"]["type-floor"]["errors"] == report["summary"]["errors_total"]
    _, uncapped = run_json(deck, "--max-per-slide", "0")
    assert uncapped["summary"]["errors"] == uncapped["summary"]["errors_total"]


# --- engine parity, checked before any browser --------------------------------

ENGINE_COMMENT = "<!-- " + " ".join(m[0] for _, m in qa.ENGINE_MARKERS.values()) + " -->"
WITH_ENGINE_CHECK = ("--font", "Inter", "--wait", "200")


@browser
def test_missing_engine_fails(tmp_path):
    deck = write_deck(tmp_path, "no-engine.html", [""])
    result = run(deck, defaults=WITH_ENGINE_CHECK)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "engine parity" in result.stdout and "body.presenting" in result.stdout
    result, report = run_json(deck, defaults=WITH_ENGINE_CHECK)
    assert result.returncode == 1
    assert {"nav-peek", "auto-folios", "__enablePrintMode"} <= {m["marker"] for m in report["engine"]["missing"]}


@browser
def test_full_engine_passes(tmp_path):
    deck = write_deck(tmp_path, "engine.html", [ENGINE_COMMENT])
    result = run(deck, defaults=WITH_ENGINE_CHECK)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "All slides clean" in result.stdout


# --- where brand fonts come from ------------------------------------------------

NO_FONT = ("--no-engine-check", "--wait", "200")


@browser
def test_fonts_from_an_explicit_tokens_file(tmp_path):
    tokens = tmp_path / "tokens.json"
    tokens.write_text(json.dumps({"font": {"primary": {"$value": ["Fictive Sans", "sans-serif"]}}}), encoding="utf-8")
    result, report = run_json(write_deck(tmp_path, "tokens.html", [""]), "--tokens", str(tokens), defaults=NO_FONT)
    assert report["summary"]["fonts"] == ["Fictive Sans"]
    assert any("Inter" in f["message"] for f in of_type(all_findings(report), "font", "error"))
    assert result.returncode == 1


@browser
def test_fonts_from_a_discovered_brand_tokens_file(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "brand").mkdir()
    (repo / "brand" / "tokens.json").write_text(
        json.dumps({"font": {"body": {"$value": "'Inter', sans-serif"}}}), encoding="utf-8")
    (repo / "presentations").mkdir()
    result, report = run_json(write_deck(repo / "presentations", "deck.html", [""]), defaults=NO_FONT)
    assert report["summary"]["fonts"] == ["Inter"]
    assert "brand/tokens.json" in report["summary"]["fonts_source"]
    assert result.returncode == 0, result.stdout


@browser
def test_fonts_from_the_deck_variables_with_a_missing_tokens_file(tmp_path):
    deck = write_deck(tmp_path, "variables.html", ['<p class="cap">fig. 1</p>'],
                      styles=(":root { --font-display: 'Inter', system-ui, sans-serif;"
                              " --font-mono: 'Fictive Mono', ui-monospace, monospace; }"
                              ".cap { position: absolute; left: 80px; top: 400px; font-size: 28px;"
                              " color: #0F172A; font-family: var(--font-mono); }"))
    result, report = run_json(deck, "--tokens", str(tmp_path / "absent.json"), defaults=NO_FONT)
    assert report["summary"]["fonts"] == ["Inter", "Fictive Mono"]
    assert "variables" in report["summary"]["fonts_source"]
    found = all_findings(report)
    assert any("tokens file not found" in f["message"] for f in of_type(found, "font", "warning"))
    assert not [f for f in of_type(found, "font") if "Fictive Mono" in f["message"]]   # declared mono passes
    assert result.returncode == 0, result.stdout


@browser
def test_no_known_family_is_reported(tmp_path):
    result, report = run_json(write_deck(tmp_path, "unknown.html", [""]), defaults=NO_FONT)
    assert any(f["level"] == "warning" for f in of_type(all_findings(report), "font"))
    assert report["summary"]["fonts"] == []
    assert result.returncode == 0


# --- PDF weight -----------------------------------------------------------------

@browser
def test_pdf_weight(tmp_path):
    deck = write_deck(tmp_path, "pdf.html", ["", ""])
    result, report = run_json(deck, "--with-pdf", "--min-kb-per-slide", "0")
    assert report["pdf"]["ok"] is True and report["pdf"]["size_kb"] > 0
    assert result.returncode == 0, result.stdout
    result, report = run_json(deck, "--with-pdf", "--min-kb-per-slide", "100000")
    assert report["pdf"]["ok"] is False
    assert of_type(report["deck_findings"], "pdf-weight", "error")
    assert result.returncode == 1
