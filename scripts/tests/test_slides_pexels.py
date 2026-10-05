# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), tests/test_pexels.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Offline tests for 06-graphic-design/presentations/scripts/pexels.py — no network, no API key needed.

Run with:  python3 -m pytest scripts/tests/ -q
"""
import json
import pathlib
import sys

import pytest
pytest.importorskip("requests")
Image = pytest.importorskip("PIL.Image")

ROOT = pathlib.Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"
sys.path.insert(0, str(ROOT / "scripts"))
import pexels  # noqa: E402

TOKENS_CSS = """
:root {
  --brand-primary: #1E40AF;
  --brand-primary-soft: rgba(30, 64, 175, 0.12);
  --brand-neutral-light: #F8FAFC;
  --brand-neutral-dark: #0F172A; /* TODO: confirm */
  --rule: #abc;
}
"""

BRAND = {
    "brand-neutral-dark": "#0F172A",
    "brand-neutral-light": "#F8FAFC",
    "brand-primary": "#1E40AF",
}


class FakeResponse:
    def __init__(self, status, payload=None, headers=None, content=b""):
        self.status_code = status
        self._payload = payload or {}
        self.headers = headers or {}
        self.content = content
        self.text = json.dumps(self._payload)

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise pexels.requests.HTTPError(str(self.status_code))


# --- core -------------------------------------------------------------------

def test_read_tokens_keeps_only_hex_values(tmp_path):
    css = tmp_path / "tokens.css"
    css.write_text(TOKENS_CSS)
    tokens = pexels.read_tokens(css)
    assert tokens["brand-primary"] == "#1E40AF"
    assert tokens["brand-neutral-dark"] == "#0F172A"
    assert tokens["rule"] == "#abc"
    assert "brand-primary-soft" not in tokens


def test_read_tokens_missing_file_is_empty(tmp_path):
    assert pexels.read_tokens(tmp_path / "nope.css") == {}


def test_hex_to_rgb_handles_short_and_long():
    assert pexels.hex_to_rgb("#abc") == (170, 187, 204)
    assert pexels.hex_to_rgb("#1E40AF") == (30, 64, 175)


def test_resolve_color():
    tokens = {"brand-primary": "#1E40AF"}
    assert pexels.resolve_color("brand-primary", tokens) == "#1E40AF"
    assert pexels.resolve_color("--brand-primary", tokens) == "#1E40AF"
    assert pexels.resolve_color("#ffffff", tokens) == "#ffffff"
    assert pexels.resolve_color("blue", tokens) == "blue"


def test_slugify():
    assert pexels.slugify("Concrete Stairwell, morning light!") == "concrete-stairwell-morning-light"
    assert pexels.slugify("???") == "photo"


def test_load_env_reads_dotenv_and_env_wins(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("# comment\nPEXELS_API_KEY='from-file'\nOTHER=1\n")
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    assert pexels.load_env(tmp_path)["PEXELS_API_KEY"] == "from-file"
    monkeypatch.setenv("PEXELS_API_KEY", "from-env")
    assert pexels.load_env(tmp_path)["PEXELS_API_KEY"] == "from-env"


def test_missing_key_exits_with_onboarding_message():
    with pytest.raises(SystemExit) as exc:
        pexels.require_key({})
    message = str(exc.value)
    assert "PEXELS_API_KEY" in message
    assert "pexels.com/api" in message


@pytest.mark.parametrize("status, fragment", [
    (401, "API key"),
    (403, "API key"),
    (429, "quota"),
    (404, "not found"),
    (500, "500"),
])
def test_api_errors_are_explicit(monkeypatch, status, fragment):
    monkeypatch.setattr(pexels.requests, "get", lambda *a, **k: FakeResponse(status))
    with pytest.raises(pexels.PexelsError, match=fragment):
        pexels.api_get("/search", "key")


def test_api_get_sends_key_and_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, headers=None, params=None, timeout=None):
        seen.update(url=url, headers=headers, params=params)
        return FakeResponse(200, {"photos": []})

    monkeypatch.setattr(pexels.requests, "get", fake_get)
    pexels.api_get("/search", "secret", {"query": "stairs"})
    assert seen["url"] == "https://api.pexels.com/v1/search"
    assert seen["headers"]["Authorization"] == "secret"
    assert "slides-agent" in seen["headers"]["User-Agent"]
    assert seen["params"] == {"query": "stairs"}


def test_quota_line_reads_headers():
    response = FakeResponse(200, headers={"X-Ratelimit-Remaining": "19950", "X-Ratelimit-Limit": "20000"})
    assert "19950 / 20000" in pexels.quota_line(response)
    assert "unknown" in pexels.quota_line(FakeResponse(200))


# --- search -----------------------------------------------------------------

def test_simplify_keeps_credit_fields():
    photo = {
        "id": 7, "width": 4000, "height": 2667, "url": "https://www.pexels.com/photo/7/",
        "photographer": "Ana Lima", "photographer_url": "https://www.pexels.com/@ana",
        "photographer_id": 1, "avg_color": "#445566", "alt": None, "liked": False,
        "src": {"original": "https://images.pexels.com/7.jpeg", "medium": "https://images.pexels.com/7m.jpeg"},
    }
    simple = pexels.simplify(photo)
    assert simple["photographer"] == "Ana Lima"
    assert simple["alt"] == ""
    assert "liked" not in simple and "photographer_id" not in simple
    assert simple["src"]["medium"].endswith("7m.jpeg")


def test_build_sheet_grid_size():
    thumbs = [(f"#{i}", Image.new("RGB", (350, 233), (200, 0, 0))) for i in range(1, 6)]
    thumbs.append(("#6", None))
    sheet = pexels.build_sheet(thumbs, cols=4)
    assert sheet.size == (
        4 * pexels.TILE_W + 5 * pexels.GAP,
        2 * (pexels.TILE_H + pexels.LABEL_H) + 3 * pexels.GAP,
    )


# --- get --------------------------------------------------------------------

def _black_white():
    img = Image.new("RGB", (100, 10))
    img.paste((0, 0, 0), (0, 0, 50, 10))
    img.paste((255, 255, 255), (50, 0, 100, 10))
    return img


def test_mono_maps_luminance_onto_brand_neutrals():
    mono = pexels.apply_treatment(_black_white(), "mono", BRAND)
    assert mono.getpixel((10, 5)) == (0x0F, 0x17, 0x2A)
    assert mono.getpixel((90, 5)) == (0xF8, 0xFA, 0xFC)


def test_duotone_maps_highlights_onto_brand_primary():
    duo = pexels.apply_treatment(_black_white(), "duotone", BRAND)
    assert duo.getpixel((10, 5)) == (0x0F, 0x17, 0x2A)
    assert duo.getpixel((90, 5)) == (0x1E, 0x40, 0xAF)


def test_treatment_requires_brand_tokens():
    with pytest.raises(pexels.PexelsError, match="--brand-primary"):
        pexels.apply_treatment(Image.new("RGB", (4, 4)), "duotone", {"brand-neutral-dark": "#000000"})


def test_find_query_reads_search_cache(tmp_path):
    folder = tmp_path / "stairs"
    folder.mkdir()
    (folder / "results.json").write_text(json.dumps({"query": "concrete stairs", "photos": [{"id": 42}]}))
    assert pexels.find_query(42, tmp_path) == "concrete stairs"
    assert pexels.find_query(7, tmp_path) is None


# --- credits ----------------------------------------------------------------

DECK = """
<style>.x { background: url(../assets/photos/pexels-head-000.jpg); }</style>
<section class="slide active" data-eyebrow="a">
  <div class="slide-bg"><img src="../assets/photos/pexels-city-2024-111-mono.jpg" alt=""></div>
</section>
<section class="slide"><p>no photo</p><!-- <img src="../assets/photos/pexels-ghost-999.jpg"> --></section>
<section class="slide dark"><img src="../assets/photos/pexels-forest-222.jpg" alt=""></section>
<section class="slide">
  <img src="../assets/photos/pexels-city-2024-111-mono.jpg" alt="">
  <img src="../assets/photos/pexels-hand-333.jpeg" alt="">
</section>
"""


def test_photos_by_slide_orders_dedupes_and_ignores_comments():
    assert pexels.photos_by_slide(DECK) == [
        ("pexels-city-2024-111", [1, 4]),
        ("pexels-forest-222", [3]),
        ("pexels-hand-333", [4]),
    ]


def _write_sidecars(folder):
    for base, name in [("pexels-city-2024-111", "Ana <Lima>"), ("pexels-forest-222", "Tom Berg")]:
        (folder / f"{base}.json").write_text(json.dumps({
            "photographer": name,
            "photographer_url": "https://www.pexels.com/@someone",
            "pexels_url": f"https://www.pexels.com/photo/{base}/",
        }))


def test_render_credits_english(tmp_path):
    _write_sidecars(tmp_path)
    html_out, warnings = pexels.render_credits(pexels.photos_by_slide(DECK), photos_dir=tmp_path)
    assert 'data-heading="Photo credits"' in html_out
    assert 'class="photo-credits"' in html_out
    assert "slides 01, 04" in html_out
    assert "slide 03" in html_out
    assert "Ana &lt;Lima&gt;" in html_out
    assert 'href="https://www.pexels.com"' in html_out
    assert "pc-list--two" not in html_out
    assert "—" not in html_out
    assert len(warnings) == 1 and "pexels-hand-333" in warnings[0]


def test_render_credits_french_and_two_columns(tmp_path):
    entries = []
    for n in range(1, 8):
        base = f"pexels-shot-{n}"
        (tmp_path / f"{base}.json").write_text(json.dumps({"photographer": f"P{n}"}))
        entries.append((base, [n]))
    html_out, warnings = pexels.render_credits(entries, photos_dir=tmp_path, lang="fr")
    assert "Crédits photo" in html_out
    assert "pc-list--two" in html_out
    assert warnings == []


def test_credits_command_prints_slide(tmp_path, monkeypatch, capsys):
    deck = tmp_path / "deck.html"
    deck.write_text(DECK)
    _write_sidecars(tmp_path)
    monkeypatch.setattr(pexels, "PHOTOS_DIR", tmp_path)
    pexels.main(["credits", str(deck)])
    captured = capsys.readouterr()
    assert "<section class=\"slide\"" in captured.out
    assert "pexels-hand-333" in captured.err


def test_credits_command_without_photos_fails_clearly(tmp_path):
    deck = tmp_path / "deck.html"
    deck.write_text('<section class="slide"><h1>Hi</h1></section>')
    with pytest.raises(SystemExit) as exc:
        pexels.main(["credits", str(deck)])
    assert "no Pexels photo" in str(exc.value)
