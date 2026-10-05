#!/usr/bin/env python3
# VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), scripts/pexels.py,
# by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
# then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
# onboarding and the pexels-photos skill refer to slides-agent.
# Register: docs/vendored-slides.md
"""Search, download, brand-treat and credit Pexels photos for slides.

This is the engine behind the `pexels-photos` skill. Pexels
(https://www.pexels.com) offers free, high-quality photography through a free
API. The script keeps decks standalone: photos are always downloaded into
06-graphic-design/presentations/assets/photos/ (never hotlinked), each with a JSON sidecar recording the
photographer and the source, so the deck's credits slide can be generated
automatically.

Usage:
    python3 06-graphic-design/presentations/scripts/pexels.py check
    python3 06-graphic-design/presentations/scripts/pexels.py search "<query>" [--orientation landscape|portrait|square]
                                               [--color <hex|brand token|colour name>]
                                               [--per-page 12] [--page 1] [--locale en-US]
    python3 06-graphic-design/presentations/scripts/pexels.py get <id> --slug <slug> [--width 2400] [--treatment mono|duotone] [--dir <folder>]
    python3 06-graphic-design/presentations/scripts/pexels.py credits 06-graphic-design/presentations/decks/<deck>.html [--lang en|fr]

Credentials are read from a `.env` file at the repo root (git-ignored):
    PEXELS_API_KEY=...        # free key, see 06-graphic-design/presentations/docs/pexels-setup.md

Real environment variables, when set, take precedence over `.env`.

Output:
    .cache/pexels/<query>/results.json + sheet.jpg    (search, git-ignored)
    06-graphic-design/presentations/assets/photos/pexels-<slug>-<id>.jpg + .json      (get: photo + credit sidecar)
    06-graphic-design/presentations/assets/photos/pexels-<slug>-<id>-<treatment>.jpg  (get --treatment)
"""
import argparse
import concurrent.futures
import datetime
import html
import io
import json
import os
import pathlib
import re
import sys

try:
    import requests
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    sys.exit(
        "ERROR: the `requests` and `Pillow` packages are required.\n"
        "Install them with:  python3 -m pip install requests pillow"
    )

ROOT = pathlib.Path(__file__).resolve().parents[3]
CACHE_DIR = ROOT / ".cache" / "pexels"
PHOTOS_DIR = ROOT / "06-graphic-design" / "presentations" / "assets" / "photos"
TOKENS_PATH = ROOT / "06-graphic-design" / "presentations" / "tokens.css"
API_BASE = "https://api.pexels.com/v1"
USER_AGENT = "slides-agent (+https://github.com/Littlpinguin/slides-agent)"

# treatment -> (token mapped onto shadows, token mapped onto highlights)
TREATMENTS = {
    "mono": ("brand-neutral-dark", "brand-neutral-light"),
    "duotone": ("brand-neutral-dark", "brand-primary"),
}

LICENSE_NOTE = (
    "Pexels License: free to use and modify, attribution appreciated "
    "(credited on the deck's photo-credits slide). https://www.pexels.com/license/"
)

MISSING_KEY = (
    "ERROR: PEXELS_API_KEY is not set.\n"
    "Pexels photos are optional and free. To enable them (about 3 minutes):\n"
    "  1. Open https://www.pexels.com/api/ and click \"Get Started\"\n"
    "     (choose \"I want to download\" and create a free account if asked)\n"
    "  2. Fill the short API form and copy the key Pexels shows you\n"
    "  3. cp .env.example .env   (if .env does not exist yet)\n"
    "  4. In .env, set:  PEXELS_API_KEY=<your key>   (no quotes, no spaces)\n"
    "  5. python3 06-graphic-design/presentations/scripts/pexels.py check\n"
    "Step-by-step guide: 06-graphic-design/presentations/docs/pexels-setup.md\n"
    "Without a key, illustrate slides with 06-graphic-design/presentations/assets/photos/, the image-generation\n"
    "skill, or typography alone."
)

# Contact sheet geometry (px).
TILE_W, TILE_H, LABEL_H, GAP, COLS = 360, 240, 36, 12, 4


class PexelsError(Exception):
    """An API or input problem, reported to the user as a one-line message."""


# --------------------------------------------------------------------------
# Core helpers
# --------------------------------------------------------------------------

def load_env(root=ROOT):
    """Read KEY=VALUE pairs from .env at the repo root, then let the real
    environment variable override them."""
    env = {}
    envfile = root / ".env"
    if envfile.exists():
        for line in envfile.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    if os.environ.get("PEXELS_API_KEY"):
        env["PEXELS_API_KEY"] = os.environ["PEXELS_API_KEY"]
    return env


def require_key(env):
    key = env.get("PEXELS_API_KEY", "").strip()
    if not key:
        sys.exit(MISSING_KEY)
    return key


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60].strip("-") or "photo"


def read_tokens(path=TOKENS_PATH):
    """Return {token-name: '#hex'} for every hex-valued custom property."""
    if not path.exists():
        return {}
    pattern = r"--([\w-]+)\s*:\s*(#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3}))\b"
    return dict(re.findall(pattern, path.read_text()))


def hex_to_rgb(value):
    value = value.lstrip("#")
    if len(value) == 3:
        value = "".join(c * 2 for c in value)
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def resolve_color(value, tokens):
    """Accept a hex code, a brand token name (with or without the leading --)
    or a Pexels colour name (red, blue, ...), and return what the API expects."""
    if value.startswith("#"):
        return value
    name = value.lstrip("-")
    return tokens.get(name, value)


def api_get(path, key, params=None):
    try:
        response = requests.get(
            f"{API_BASE}{path}",
            headers={"Authorization": key, "User-Agent": USER_AGENT},
            params=params,
            timeout=30,
        )
    except requests.RequestException as exc:
        raise PexelsError(f"request to Pexels failed: {exc}")
    if response.status_code in (401, 403):
        raise PexelsError(
            f"Pexels rejected the API key (HTTP {response.status_code}). "
            "Check PEXELS_API_KEY in .env: paste the key exactly, without quotes "
            "or spaces. You can copy it again from https://www.pexels.com/api/ "
            "(see 06-graphic-design/presentations/docs/pexels-setup.md)."
        )
    if response.status_code == 429:
        raise PexelsError(
            "Pexels quota reached (200 requests/hour, 20,000/month). "
            + reset_hint(response)
        )
    if response.status_code == 404:
        raise PexelsError(f"not found on Pexels: {path}")
    if response.status_code != 200:
        raise PexelsError(f"Pexels API returned {response.status_code}: {response.text[:500]}")
    return response


def reset_hint(response):
    reset = response.headers.get("X-Ratelimit-Reset", "")
    if not reset.isdigit():
        return "Try again later."
    return f"Quota resets at {datetime.datetime.fromtimestamp(int(reset)):%Y-%m-%d %H:%M}."


def quota_line(response):
    remaining = response.headers.get("X-Ratelimit-Remaining")
    limit = response.headers.get("X-Ratelimit-Limit")
    if remaining is None or limit is None:
        return "quota: unknown"
    return f"quota: {remaining} / {limit} requests left this month"


def cmd_check(args, env):
    response = api_get("/curated", require_key(env), {"per_page": 1})
    print("OK · the Pexels API key works")
    print(quota_line(response))


# --------------------------------------------------------------------------
# search
# --------------------------------------------------------------------------

def simplify(photo):
    return {
        "id": photo["id"],
        "width": photo.get("width"),
        "height": photo.get("height"),
        "url": photo.get("url"),
        "photographer": photo.get("photographer"),
        "photographer_url": photo.get("photographer_url"),
        "alt": photo.get("alt") or "",
        "avg_color": photo.get("avg_color"),
        "src": photo.get("src") or {},
    }


def load_font(size):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1 has a single bitmap size
        return ImageFont.load_default()


def fetch_image(url):
    if not url:
        return None
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
        response.raise_for_status()
        img = Image.open(io.BytesIO(response.content))
        img.load()
        return img
    except (requests.RequestException, OSError):
        return None


def build_sheet(thumbs, cols=COLS):
    """thumbs: list of (label, PIL image or None). Returns one image with
    numbered tiles, so a whole search can be judged in a single look."""
    rows = max(1, -(-len(thumbs) // cols))
    width = cols * TILE_W + (cols + 1) * GAP
    height = rows * (TILE_H + LABEL_H) + (rows + 1) * GAP
    sheet = Image.new("RGB", (width, height), (245, 245, 242))
    draw = ImageDraw.Draw(sheet)
    font = load_font(20)
    for i, (label, thumb) in enumerate(thumbs):
        x = GAP + (i % cols) * (TILE_W + GAP)
        y = GAP + (i // cols) * (TILE_H + LABEL_H + GAP)
        draw.rectangle([x, y, x + TILE_W - 1, y + TILE_H - 1], fill=(222, 222, 218))
        if thumb is not None:
            fitted = ImageOps.contain(thumb.convert("RGB"), (TILE_W, TILE_H))
            sheet.paste(fitted, (x + (TILE_W - fitted.width) // 2, y + (TILE_H - fitted.height) // 2))
        draw.text((x + 4, y + TILE_H + 8), label, fill=(20, 20, 20), font=font)
    return sheet


def cmd_search(args, env):
    key = require_key(env)
    params = {
        "query": args.query,
        "orientation": args.orientation,
        "per_page": max(1, min(80, args.per_page)),
        "page": max(1, args.page),
    }
    if args.color:
        params["color"] = resolve_color(args.color, read_tokens())
    if args.locale:
        params["locale"] = args.locale
    response = api_get("/search", key, params)
    photos = [simplify(p) for p in response.json().get("photos", [])]
    if not photos:
        raise PexelsError(
            f'no results for "{args.query}". Try broader, concrete English nouns '
            "(a place, a material, an object, a light), or drop --color."
        )

    outdir = CACHE_DIR / slugify(args.query)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "results.json").write_text(json.dumps(
        {"query": args.query, "params": params, "photos": photos},
        ensure_ascii=False, indent=2,
    ))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        thumbs = list(pool.map(fetch_image, [p["src"].get("medium", "") for p in photos]))
    labels = [f"#{i + 1}  {p['id']}" for i, p in enumerate(photos)]
    build_sheet(list(zip(labels, thumbs))).save(outdir / "sheet.jpg", quality=85)

    for i, p in enumerate(photos):
        size = f"{p['width']}x{p['height']}"
        print(f"#{i + 1:<3} {p['id']:<10} {size:<10} {p['photographer']} · {p['alt'][:70]}")
    print(f"\nsheet   -> {outdir / 'sheet.jpg'}")
    print(f"results -> {outdir / 'results.json'}")
    print(quota_line(response))


# --------------------------------------------------------------------------
# get
# --------------------------------------------------------------------------

def find_query(photo_id, cache_dir=CACHE_DIR):
    """Return the search query that surfaced this photo, if it is cached."""
    for results in sorted(cache_dir.glob("*/results.json")):
        try:
            data = json.loads(results.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if any(p.get("id") == photo_id for p in data.get("photos", [])):
            return data.get("query")
    return None


def apply_treatment(img, treatment, tokens):
    """Map the photo's luminance onto two brand colours (shadows -> highlights).
    Baked into the file, so screen and PDF render identically."""
    dark_token, light_token = TREATMENTS[treatment]
    missing = [f"--{t}" for t in (dark_token, light_token) if t not in tokens]
    if missing:
        raise PexelsError(f"06-graphic-design/presentations/tokens.css has no hex value for: {', '.join(missing)}")
    gray = ImageOps.autocontrast(ImageOps.grayscale(img), cutoff=1)
    return ImageOps.colorize(
        gray,
        black=hex_to_rgb(tokens[dark_token]),
        white=hex_to_rgb(tokens[light_token]),
    )


def cmd_get(args, env):
    key = require_key(env)
    photo = simplify(api_get(f"/photos/{args.id}", key).json())
    original = photo["src"].get("original")
    if not original:
        raise PexelsError(f"photo {args.id} has no downloadable source")
    try:
        response = requests.get(
            original,
            params={"auto": "compress", "cs": "tinysrgb", "w": args.width},
            headers={"User-Agent": USER_AGENT},
            timeout=120,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PexelsError(f"download failed: {exc}")

    outdir = pathlib.Path(args.dir) if args.dir else PHOTOS_DIR
    outdir.mkdir(parents=True, exist_ok=True)
    base = f"pexels-{slugify(args.slug)}-{args.id}"
    photo_path = outdir / f"{base}.jpg"
    img = Image.open(io.BytesIO(response.content))
    if img.format == "JPEG":
        photo_path.write_bytes(response.content)
    else:
        img.convert("RGB").save(photo_path, quality=88)
    written = [photo_path]

    if args.treatment:
        variant_path = outdir / f"{base}-{args.treatment}.jpg"
        apply_treatment(img, args.treatment, read_tokens()).save(variant_path, quality=88)
        written.append(variant_path)

    sidecar = outdir / f"{base}.json"
    files = [p.name for p in written]
    if sidecar.exists():
        try:
            previous = json.loads(sidecar.read_text()).get("files", [])
            files = sorted(set(previous) | set(files))
        except json.JSONDecodeError:
            pass
    sidecar.write_text(json.dumps({
        "source": "pexels",
        "id": photo["id"],
        "slug": slugify(args.slug),
        "pexels_url": photo["url"],
        "photographer": photo["photographer"],
        "photographer_url": photo["photographer_url"],
        "alt": photo["alt"],
        "avg_color": photo["avg_color"],
        "original_size": [photo["width"], photo["height"]],
        "download_width": args.width,
        "query": find_query(photo["id"]),
        "downloaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "files": files,
        "license": LICENSE_NOTE,
    }, ensure_ascii=False, indent=2))

    for path in written:
        print(f"OK -> {path}")
    print(f"     {sidecar}")
    print(f"credit: {photo['photographer']} · {photo['url']}")


# --------------------------------------------------------------------------
# credits
# --------------------------------------------------------------------------

SLIDE_RE = re.compile(r'<section\b[^>]*\bclass="[^"]*(?<![\w-])slide(?![\w-])[^"]*"', re.I)
PHOTO_RE = re.compile(r"(pexels-[a-z0-9-]*?-\d+)(?:-(?:mono|duotone))?\.jpe?g")

CREDITS_LABELS = {
    "en": {
        "heading": "Photo credits",
        "eyebrow": "photo credits",
        "title": 'Photographs from <a href="https://www.pexels.com">Pexels</a>',
        "slide": "slide",
        "slides": "slides",
        "link": "view on pexels",
        "signature": "photographs · pexels license",
        "unknown": "Unknown photographer",
    },
    "fr": {
        "heading": "Crédits photo",
        "eyebrow": "crédits photo",
        "title": 'Photographies issues de <a href="https://www.pexels.com">Pexels</a>',
        "slide": "slide",
        "slides": "slides",
        "link": "voir sur pexels",
        "signature": "photographies · licence pexels",
        "unknown": "Photographe inconnu",
    },
}

CREDITS_SLIDE = """<section class="slide" data-eyebrow="{eyebrow}" data-heading="{heading}">
  <div class="chrome">
    <div class="chrome-row top">
      <span class="meta-label">{eyebrow}</span>
      <span class="nav-num"></span>
    </div>
    <div class="chrome-row bottom">
      <span class="signature">{signature}</span>
      <svg class="brand-mark"><use href="#brand-logo"/></svg>
    </div>
  </div>
  <div class="photo-credits">
    <span class="eyebrow reveal">{eyebrow}</span>
    <h2 class="pc-title reveal">{title}</h2>
    <ol class="{list_class} reveal">
{items}
    </ol>
  </div>
</section>"""


def photos_by_slide(deck_html):
    """Return [(photo base name, [slide numbers])] in order of first use.
    Slides are the deck's <section class="slide"> elements, in DOM order."""
    text = re.sub(r"<!--.*?-->", "", deck_html, flags=re.S)
    starts = [m.start() for m in SLIDE_RE.finditer(text)]
    found = {}
    for n, start in enumerate(starts, 1):
        end = starts[n] if n < len(starts) else len(text)
        for base in PHOTO_RE.findall(text[start:end]):
            slides = found.setdefault(base, [])
            if n not in slides:
                slides.append(n)
    return list(found.items())


def render_credits(entries, photos_dir=PHOTOS_DIR, lang="en"):
    """Build the photo-credits slide. Returns (html, warnings)."""
    labels = CREDITS_LABELS[lang]
    items, warnings = [], []
    for base, slides in entries:
        sidecar = photos_dir / f"{base}.json"
        if not sidecar.exists():
            warnings.append(f"no sidecar for {base} (downloaded outside pexels.py?), credit it by hand")
            continue
        meta = json.loads(sidecar.read_text())
        where = labels["slide" if len(slides) == 1 else "slides"] + " " + ", ".join(f"{n:02d}" for n in slides)
        name = html.escape(meta.get("photographer") or labels["unknown"])
        profile = html.escape(meta.get("photographer_url") or "https://www.pexels.com", quote=True)
        page = html.escape(meta.get("pexels_url") or "https://www.pexels.com", quote=True)
        items.append(
            f'      <li><span class="pc-slide">{where}</span>'
            f'<a class="pc-name" href="{profile}"><bdi>{name}</bdi></a>'
            f'<a class="pc-link" href="{page}">{labels["link"]}</a></li>'
        )
    html_out = CREDITS_SLIDE.format(
        eyebrow=labels["eyebrow"],
        heading=labels["heading"],
        signature=labels["signature"],
        title=labels["title"],
        list_class="pc-list pc-list--two" if len(items) > 6 else "pc-list",
        items="\n".join(items),
    )
    return html_out, warnings


def cmd_credits(args, env):
    deck = pathlib.Path(args.deck)
    if not deck.exists():
        raise PexelsError(f"deck not found: {deck}")
    entries = photos_by_slide(deck.read_text())
    if not entries:
        raise PexelsError("no Pexels photo (pexels-*.jpg) referenced in this deck, so no credits slide is needed")
    html_out, warnings = render_credits(entries, photos_dir=PHOTOS_DIR, lang=args.lang)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    print(html_out)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="Search, download, brand-treat and credit Pexels photos for slides."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="verify the API key and show the remaining quota")

    search = sub.add_parser("search", help="search photos and build a numbered contact sheet")
    search.add_argument("query", help="concrete English nouns work best, e.g. 'harbour at dawn'")
    search.add_argument("--orientation", default="landscape", choices=["landscape", "portrait", "square"])
    search.add_argument("--color", help="hex (#1E40AF), brand token (brand-primary) or Pexels colour name (blue)")
    search.add_argument("--per-page", type=int, default=12, help="results per page, 1-80 (default 12)")
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--locale", help="e.g. fr-FR; English queries usually return better results")

    get = sub.add_parser("get", help="download one photo into 06-graphic-design/presentations/assets/photos/ with its credit sidecar")
    get.add_argument("id", type=int, help="Pexels photo id (second column of the search output)")
    get.add_argument("--slug", required=True, help="short kebab-case name, e.g. harbour-dawn")
    get.add_argument("--width", type=int, default=2400, help="download width in px (default 2400)")
    get.add_argument("--treatment", choices=sorted(TREATMENTS),
                     help="also write a brand-tinted variant (colours from 06-graphic-design/presentations/tokens.css)")
    get.add_argument("--dir", help="output folder (default 06-graphic-design/presentations/assets/photos/)")

    credits = sub.add_parser("credits", help="print the photo-credits slide for a deck")
    credits.add_argument("deck", help="path to the deck HTML file")
    credits.add_argument("--lang", default="en", choices=sorted(CREDITS_LABELS))
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    commands = {"check": cmd_check, "search": cmd_search, "get": cmd_get, "credits": cmd_credits}
    try:
        commands[args.command](args, load_env())
    except PexelsError as exc:
        sys.exit(f"ERROR: {exc}")


if __name__ == "__main__":
    main()
