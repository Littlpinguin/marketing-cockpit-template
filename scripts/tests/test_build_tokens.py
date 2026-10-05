"""Tests de scripts/build-tokens.py (source unique de la palette et de la typographie).

Deux familles de tests :
  - le mécanisme, sur des tokens et des cibles fictifs écrits dans une racine
    jetable avec leur propre fichier de cibles ;
  - le câblage du template : le gabarit _templates/brand/tokens.json, une fois
    ses placeholders remplacés par les exemples de docs/placeholders.json, doit
    produire les cibles déclarées dans scripts/build-tokens.toml.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "build-tokens.py"
CONFIG_LIVREE = REPO / "scripts" / "build-tokens.toml"
GABARIT_TOKENS = REPO / "_templates" / "brand" / "tokens.json"
GABARIT_STYLE_GUIDE = REPO / "_templates" / "brand" / "style-guide.md"
TOKENS_CSS_DECKS = "06-graphic-design/presentations/tokens.css"
TOKENS = "01-brand/tokens.json"


def _load_module():
    """Charge build-tokens.py par chemin : son nom contient un tiret."""
    spec = importlib.util.spec_from_file_location("build_tokens", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


build_tokens = _load_module()


# --------------------------------------------------------------------------
# Fixtures fictives
# --------------------------------------------------------------------------

TOKENS_FICTIFS = {
    "color": {
        "$type": "color",
        "primary": {"$value": "#1E40AF"},
        "accent": {"$value": "#F59E0B"},
        "dark": {"$value": "#0F172A"},
        "light": {"$value": "#F8FAFC"},
        "alias": {"$value": "{color.primary}"},
    },
    "gradient": {
        "$type": "gradient",
        "signature": {
            "$value": [
                {"color": "{color.primary}", "position": 0},
                {"color": "{color.accent}", "position": 1},
            ],
            "$extensions": {"cockpit": {"angle": "90deg"}},
        },
    },
    "font": {
        "$type": "fontFamily",
        "display": {"$value": ["Inter", "system-ui", "sans-serif"]},
    },
    "radius": {"$type": "dimension", "card": {"$value": "16px"}},
    "typography": {
        "$type": "typography",
        "h1": {"$value": {"fontFamily": "{font.display}", "fontSize": "56px"}},
    },
}

FEUILLE = (
    "/* En-tête conservé */\n"
    "@font-face { font-family: 'Inter'; src: url(inter.woff2); }\n"
    ":root {\n"
    "  /* brand-tokens:start */\n"
    "  /* brand-tokens:end */\n"
    "  --local: 4px;\n"
    "}\n"
    "body { color: var(--ink); }\n"
)

CONFIG_FICTIVE = """
tokens = "01-brand/tokens.json"

[[targets]]
path = "lib/compose.css"
mode = "block"
indent = "  "

[targets.vars]
"--ink" = "color.dark"
"--paper" = "color.light"
"--accent-soft" = { token = "color.accent", alpha = 0.12 }
"--grad" = "gradient.signature"
"--grad-v" = { token = "gradient.signature", angle = "180deg" }
"--font" = "font.display"
"--radius" = "radius.card"

[[targets]]
path = "out/tokens.css"
mode = "file"
auto = ["color", "gradient"]
"""

CIBLES = ["lib/compose.css", "out/tokens.css"]


def make_root(tmp_path: Path, tokens: dict | None = None) -> Path:
    root = tmp_path / "repo"
    (root / "01-brand").mkdir(parents=True)
    (root / "lib").mkdir()
    (root / TOKENS).write_text(json.dumps(tokens or TOKENS_FICTIFS, indent=2), encoding="utf-8")
    (root / "lib/compose.css").write_text(FEUILLE, encoding="utf-8")
    (root / "build-tokens.toml").write_text(CONFIG_FICTIVE, encoding="utf-8")
    return root


def run(root: Path, *args: str, config: Path | None = None) -> subprocess.CompletedProcess:
    config = config or (root / "build-tokens.toml")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--config", str(config), *args],
        capture_output=True,
        text=True,
    )


def contenus(root: Path) -> dict[str, bytes | None]:
    return {rel: (root / rel).read_bytes() if (root / rel).exists() else None for rel in CIBLES}


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def test_hex_invalide_refuse():
    """Une couleur mal formée arrête le build au lieu de se propager dans le CSS."""
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["primary"]["$value"] = "1E40AF"
    with pytest.raises(build_tokens.TokenError, match="color.primary"):
        build_tokens.validate_tokens(tokens)


def test_token_mal_type_refuse(tmp_path):
    """Une valeur posée en chaîne au lieu d'un objet est refusée, pas ignorée."""
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["primary"] = "#1E40AF"
    with pytest.raises(build_tokens.TokenError, match="mal typé"):
        build_tokens.validate_tokens(tokens)

    result = run(make_root(tmp_path, tokens))
    assert result.returncode == 1
    assert "color.primary" in result.stdout + result.stderr


def test_placeholder_residuel_refuse_avec_un_message_clair(tmp_path):
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["primary"]["$value"] = "{{BRAND_COLOR_PRIMARY}}"
    tokens["font"]["display"]["$value"] = ["{{BRAND_FONT_PRIMARY}}", "sans-serif"]
    result = run(make_root(tmp_path, tokens))
    assert result.returncode == 1
    assert "{{BRAND_COLOR_PRIMARY}}" in result.stderr
    assert "{{BRAND_FONT_PRIMARY}}" in result.stderr
    assert "/brand-discover" in result.stderr


def test_reference_introuvable_refusee():
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["alias"]["$value"] = "{color.inexistante}"
    with pytest.raises(build_tokens.TokenError, match="color.inexistante"):
        build_tokens.validate_tokens(tokens)


def test_arret_de_gradient_hors_bornes_refuse():
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["gradient"]["signature"]["$value"][1]["position"] = 1.5
    with pytest.raises(build_tokens.TokenError, match="hors de"):
        build_tokens.validate_tokens(tokens)


def test_tokens_fictifs_valides():
    build_tokens.validate_tokens(TOKENS_FICTIFS)


def test_tokens_absents_renvoient_au_wizard(tmp_path):
    root = make_root(tmp_path)
    (root / TOKENS).unlink()
    result = run(root)
    assert result.returncode == 1
    assert "/brand-discover" in result.stderr


# --------------------------------------------------------------------------
# Rendu
# --------------------------------------------------------------------------

def test_rendu_des_variables(tmp_path):
    root = make_root(tmp_path)
    assert run(root).returncode == 0
    css = (root / "lib/compose.css").read_text(encoding="utf-8")
    assert "  --ink: #0F172A;" in css
    assert "  --accent-soft: rgba(245, 158, 11, 0.12);" in css
    assert "  --grad: linear-gradient(90deg, #1E40AF 0%, #F59E0B 100%);" in css
    assert "  --grad-v: linear-gradient(180deg, #1E40AF 0%, #F59E0B 100%);" in css
    assert "  --font: 'Inter', system-ui, sans-serif;" in css
    assert "  --radius: 16px;" in css


def test_mode_fichier_et_variables_automatiques(tmp_path):
    root = make_root(tmp_path)
    assert run(root).returncode == 0
    css = (root / "out/tokens.css").read_text(encoding="utf-8")
    assert css.startswith("/* Généré depuis 01-brand/tokens.json")
    assert ":root {" in css
    assert "  --color-primary: #1E40AF;" in css
    assert "  --color-alias: #1E40AF;" in css    # la référence est résolue
    assert "  --gradient-signature: linear-gradient(90deg, #1E40AF 0%, #F59E0B 100%);" in css


def test_type_non_rendable_refuse(tmp_path):
    root = make_root(tmp_path)
    config = root / "build-tokens.toml"
    config.write_text(CONFIG_FICTIVE.replace('"--radius" = "radius.card"',
                                             '"--radius" = "typography.h1"'), encoding="utf-8")
    result = run(root)
    assert result.returncode == 1
    assert "typography.h1" in result.stderr


def test_alpha_sur_un_gradient_refuse(tmp_path):
    root = make_root(tmp_path)
    config = root / "build-tokens.toml"
    config.write_text(CONFIG_FICTIVE.replace('{ token = "color.accent", alpha = 0.12 }',
                                             '{ token = "gradient.signature", alpha = 0.12 }'),
                      encoding="utf-8")
    result = run(root)
    assert result.returncode == 1
    assert "alpha" in result.stderr


# --------------------------------------------------------------------------
# Écriture, idempotence, contrôle
# --------------------------------------------------------------------------

def test_idempotence(tmp_path):
    root = make_root(tmp_path)
    assert run(root).returncode == 0
    premier = contenus(root)
    assert run(root).returncode == 0
    assert contenus(root) == premier


def test_check_detecte_une_divergence(tmp_path):
    root = make_root(tmp_path)
    assert run(root).returncode == 0
    assert run(root, "--check").returncode == 0

    cible = root / "lib/compose.css"
    cible.write_text(cible.read_text(encoding="utf-8").replace("#0F172A", "#FF0000"),
                     encoding="utf-8")
    result = run(root, "--check")
    assert result.returncode == 1
    assert "compose.css" in result.stdout + result.stderr


def test_check_avant_generation_echoue(tmp_path):
    assert run(make_root(tmp_path), "--check").returncode == 1


def test_dry_run_n_ecrit_rien(tmp_path):
    root = make_root(tmp_path)
    avant = contenus(root)
    result = run(root, "--dry-run")
    assert result.returncode == 0
    assert contenus(root) == avant


def test_marqueurs_respectes_et_reste_du_fichier_intact(tmp_path):
    """Hors marqueurs, la feuille est conservée à l'octet près."""
    root = make_root(tmp_path)
    avant = FEUILLE
    debut = avant.index(build_tokens.MARKER_START)
    fin = avant.index(build_tokens.MARKER_END) + len(build_tokens.MARKER_END)
    tete, queue = avant[:debut], avant[fin:]

    assert run(root).returncode == 0
    apres = (root / "lib/compose.css").read_text(encoding="utf-8")
    assert apres.startswith(tete)
    assert apres.endswith(queue)
    assert "#0F172A" in apres
    assert "@font-face" in apres


def test_cible_sans_marqueur_echoue(tmp_path):
    root = make_root(tmp_path)
    cible = root / "lib/compose.css"
    cible.write_text(FEUILLE.replace(build_tokens.MARKER_END, ""), encoding="utf-8")
    result = run(root)
    assert result.returncode == 1
    assert "compose.css" in result.stdout + result.stderr


def test_marqueurs_en_double_refuses(tmp_path):
    root = make_root(tmp_path)
    cible = root / "lib/compose.css"
    cible.write_text(FEUILLE + "/* brand-tokens:start */\n/* brand-tokens:end */\n", encoding="utf-8")
    result = run(root)
    assert result.returncode == 1
    assert "double" in result.stderr


def test_check_et_dry_run_sont_exclusifs(tmp_path):
    result = run(make_root(tmp_path), "--check", "--dry-run")
    assert result.returncode == 2


# --------------------------------------------------------------------------
# Câblage du template
# --------------------------------------------------------------------------

def _exemples_placeholders() -> dict[str, str]:
    groupes = json.loads((REPO / "docs/placeholders.json").read_text(encoding="utf-8"))["groups"]
    return {e["name"]: e["example"] for g in groupes.values() for e in g if "example" in e}


def racine_du_template_apres_wizard(tmp_path: Path) -> Path:
    """Simule /brand-discover : gabarit rempli avec les exemples de placeholders.json."""
    exemples = _exemples_placeholders()
    gabarit = GABARIT_TOKENS.read_text(encoding="utf-8")
    rempli = re.sub(r"\{\{([A-Z0-9_]+)\}\}",
                    lambda m: exemples.get(m.group(1), m.group(0)), gabarit)
    root = tmp_path / "repo"
    (root / "01-brand").mkdir(parents=True)
    (root / TOKENS).write_text(rempli, encoding="utf-8")
    (root / "01-brand/style-guide.md").write_text(
        GABARIT_STYLE_GUIDE.read_text(encoding="utf-8"), encoding="utf-8")
    dst = root / TOKENS_CSS_DECKS
    dst.parent.mkdir(parents=True)
    dst.write_text((REPO / TOKENS_CSS_DECKS).read_text(encoding="utf-8"), encoding="utf-8")
    return root


def test_gabarit_tokens_est_un_json_dtcg_valide_une_fois_rempli(tmp_path):
    root = racine_du_template_apres_wizard(tmp_path)
    tokens = json.loads((root / TOKENS).read_text(encoding="utf-8"))
    build_tokens.validate_tokens(tokens)


def test_gabarit_tokens_ne_porte_que_des_placeholders_connus():
    """Tout placeholder du gabarit est déclaré dans docs/placeholders.json."""
    connus = {
        e["name"]
        for g in json.loads((REPO / "docs/placeholders.json").read_text(encoding="utf-8"))["groups"].values()
        for e in g
    }
    noms = set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", GABARIT_TOKENS.read_text(encoding="utf-8")))
    assert noms and noms <= connus


def test_gabarit_brut_refuse_tant_que_le_wizard_n_est_pas_passe():
    tokens = json.loads(GABARIT_TOKENS.read_text(encoding="utf-8"))
    with pytest.raises(build_tokens.TokenError, match="placeholders non résolus"):
        build_tokens.validate_tokens(tokens)


def test_cibles_livrees_generees_sans_placeholder(tmp_path):
    root = racine_du_template_apres_wizard(tmp_path)
    result = run(root, config=CONFIG_LIVREE)
    assert result.returncode == 0, result.stderr
    assert run(root, "--check", config=CONFIG_LIVREE).returncode == 0
    css = (root / TOKENS_CSS_DECKS).read_text(encoding="utf-8")
    assert build_tokens.PLACEHOLDER_RE.search(css) is None
    assert "--brand-primary: #1E40AF;" in css
    guide = (root / "01-brand/style-guide.md").read_text(encoding="utf-8")
    debut = guide.index(build_tokens.MARKER_START)
    assert build_tokens.PLACEHOLDER_RE.search(guide[debut:]) is None
    assert "--color-primary: #1E40AF;" in guide


# Une déclaration CSS de variable : « --nom: ».
DECLARATION_RE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
# Une lecture : « var(--nom) », le groupe 2 vaut « , » si un repli suit.
LECTURE_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(,)?")
BLOC_ROOT_RE = re.compile(r":root\s*\{(.*?)\}", re.S)


def test_tokens_css_declare_les_variables_attendues_par_les_gabarits_de_deck(tmp_path):
    """Les gabarits de deck doivent retrouver toutes leurs variables.

    La liste est relue dans les gabarits à chaque exécution : une variable
    ajoutée à un gabarit fait échouer le test tant que tokens.css ne la
    déclare pas. Sont attendues toute variable déclarée dans le `:root` du
    gabarit et toute variable lue en `var(--nom)` sans valeur de repli.
    """
    gabarits = sorted((REPO / "06-graphic-design/presentations/templates").glob("*.html"))
    assert gabarits
    attendues: set[str] = set()
    for gabarit in gabarits:
        source = gabarit.read_text(encoding="utf-8")
        bloc = BLOC_ROOT_RE.search(source)
        assert bloc, f"aucun bloc :root trouvé dans {gabarit.name}"
        attendues |= set(DECLARATION_RE.findall(bloc.group(1)))
        attendues |= {nom for nom, repli in LECTURE_RE.findall(source) if not repli}

    root = racine_du_template_apres_wizard(tmp_path)
    assert run(root, config=CONFIG_LIVREE).returncode == 0
    declarees = set(DECLARATION_RE.findall((root / TOKENS_CSS_DECKS).read_text(encoding="utf-8")))
    assert sorted(attendues - declarees) == []
