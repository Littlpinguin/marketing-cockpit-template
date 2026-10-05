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
TOKENS_CSS_LANDINGS = "05-web-content/templates/assets/tokens.css"
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
    for cible in (TOKENS_CSS_DECKS, TOKENS_CSS_LANDINGS):
        dst = root / cible
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text((REPO / cible).read_text(encoding="utf-8"), encoding="utf-8")
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
    landings = (root / TOKENS_CSS_LANDINGS).read_text(encoding="utf-8")
    assert build_tokens.PLACEHOLDER_RE.search(landings) is None
    assert "--brand-accent: #F59E0B;" in landings and "--font-display: 'Inter'" in landings
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


# --------------------------------------------------------------------------
# Couleurs dérivées (mix, contraste) : le fichier de marque du moteur de slides
# --------------------------------------------------------------------------

def test_mix_reproduit_les_derivees_de_slides_agent():
    """color-mix(in srgb, ...) rendu en hex : les valeurs publiées par slides-agent."""
    assert build_tokens.mix_hex("#1E40AF", "#000000", 0.12) == "#1A389A"
    assert build_tokens.mix_hex("#F59E0B", "#000000", 0.12) == "#D88B0A"
    assert build_tokens.mix_hex("#F8FAFC", "#FFFFFF", 0.35) == "#FAFCFD"
    assert build_tokens.mix_hex("#0F172A", "#FFFFFF", 0.14) == "#313748"
    assert build_tokens.mix_hex("#1E40AF", "#FFFFFF", 0.5) == "#8EA0D7"


def test_contraste_wcag():
    assert round(build_tokens.contraste("#000000", "#FFFFFF"), 2) == 21.0
    assert round(build_tokens.contraste("#1E40AF", "#E9EBED"), 1) == 7.3


def _spec(**options):
    return {"token": "color.primary", **options}


def test_min_contrast_garde_une_couleur_deja_conforme():
    spec = _spec(mix="#000000", min_contrast=4.5,
                 against={"token": "color.light", "mix": "#000000", "amount": 0.06})
    assert build_tokens.render_value(TOKENS_FICTIFS, spec, "t") == "#1E40AF"


def test_min_contrast_assombrit_une_primaire_claire_jusqu_au_seuil():
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["primary"]["$value"] = "#38BDF8"
    spec = _spec(mix="#000000", min_contrast=4.5, against=["color.light", "#FFFFFF"])
    rendu = build_tokens.render_value(tokens, spec, "t")
    assert rendu != "#38BDF8"
    assert build_tokens.contraste(rendu, "#F8FAFC") >= 4.5
    # le pas précédent n'y suffisait pas : le mélange s'arrête au seuil, pas au noir
    assert rendu != "#000000"


def test_min_contrast_inatteignable_refuse():
    # assombrir la primaire ne l'éloignera jamais d'un fond noir
    spec = _spec(mix="#000000", min_contrast=4.5, against="#000000")
    with pytest.raises(build_tokens.TokenError, match="inatteignable"):
        build_tokens.render_value(TOKENS_FICTIFS, spec, "t")


@pytest.mark.parametrize("spec, motif", [
    (_spec(amount=0.12), "demandent « mix »"),
    (_spec(mix="#000000", against="color.light"), "against"),
    (_spec(mix="#000000", alpha=0.1), "exclusifs"),
    (_spec(mix="#000000", amount=1.5), "hors de"),
    (_spec(mix="#000000", min_contrast=40, against="color.light"), "min_contrast"),
    (_spec(mix="color.inexistante"), "color.inexistante"),
    ({"token": "gradient.signature", "mix": "#000000"}, "qu'à une couleur"),
])
def test_options_de_derivee_mal_formees_refusees(spec, motif):
    with pytest.raises(build_tokens.TokenError, match=motif):
        build_tokens.render_value(TOKENS_FICTIFS, spec, "t")


def test_mix_vers_un_token(tmp_path):
    spec = _spec(mix="color.dark", amount=0.5)
    assert build_tokens.render_value(TOKENS_FICTIFS, spec, "t") == \
        build_tokens.mix_hex("#1E40AF", "#0F172A", 0.5)


# Le template livre tokens.css avec la palette d'exemple de docs/placeholders.json.
# Dans un fork configuré, le wizard a remplacé ces valeurs : ces deux tests ne
# concernent que le template lui-même.
template_non_configure = pytest.mark.skipif(
    (REPO / TOKENS).exists(),
    reason="fork configuré : 01-brand/tokens.json a remplacé la palette d'exemple",
)


@template_non_configure
def test_tokens_css_livre_est_la_sortie_de_la_palette_d_exemple(tmp_path):
    """Le bloc livré est exactement ce que build-tokens.py écrit pour les exemples."""
    root = racine_du_template_apres_wizard(tmp_path)
    assert run(root, config=CONFIG_LIVREE).returncode == 0
    assert (root / TOKENS_CSS_DECKS).read_text(encoding="utf-8") == \
        (REPO / TOKENS_CSS_DECKS).read_text(encoding="utf-8")


def _valeurs_root(texte: str) -> dict[str, str]:
    bloc = BLOC_ROOT_RE.search(texte).group(1)
    bloc = re.sub(r"/\*.*?\*/", "", bloc, flags=re.S)
    return {nom: valeur.strip() for nom, valeur in
            re.findall(r"(--[A-Za-z0-9_-]+)\s*:\s*([^;]+);", bloc)}


def _normaliser(valeur: str) -> str:
    valeur = re.sub(r"\s+", "", valeur).upper()
    if valeur.startswith("'") or valeur.startswith('"') or "," in valeur and "(" not in valeur:
        valeur = valeur.split(",")[0].strip("'\"")    # police : la première famille
    return valeur


@template_non_configure
def test_valeurs_par_defaut_identiques_au_starter_vendorise():
    """La palette d'exemple de tokens.css est celle du starter de slides-agent."""
    starter = _valeurs_root((REPO / "06-graphic-design/presentations/templates/base.html")
                            .read_text(encoding="utf-8"))
    tokens = _valeurs_root((REPO / TOKENS_CSS_DECKS).read_text(encoding="utf-8"))
    comparees = [nom for nom, valeur in starter.items()
                 if nom in tokens and "var(" not in valeur]
    assert len(comparees) >= 20
    ecarts = {nom: (starter[nom], tokens[nom]) for nom in comparees
              if _normaliser(starter[nom]) != _normaliser(tokens[nom])}
    assert ecarts == {}


# --------------------------------------------------------------------------
# Fichier de marque des landings (bibliothèque de sections)
# --------------------------------------------------------------------------

@template_non_configure
def test_tokens_css_des_landings_livre_est_la_sortie_de_la_palette_d_exemple(tmp_path):
    """Le bloc livré dans 05-web-content/templates/assets/tokens.css est celui que le script écrit."""
    root = racine_du_template_apres_wizard(tmp_path)
    assert run(root, config=CONFIG_LIVREE).returncode == 0
    assert (root / TOKENS_CSS_LANDINGS).read_text(encoding="utf-8") == \
        (REPO / TOKENS_CSS_LANDINGS).read_text(encoding="utf-8")


def _valeurs_landings(tokens: dict) -> dict[str, str]:
    config = build_tokens.load_config(CONFIG_LIVREE)
    cible = next(c for c in config["targets"] if c["path"] == TOKENS_CSS_LANDINGS)
    lignes = build_tokens.target_lines(tokens, cible, "test")
    return dict(re.findall(r"(--[A-Za-z0-9-]+): ([^;]+);", "\n".join(lignes)))


@pytest.mark.parametrize("accent, primaire", [
    ("#F59E0B", "#1E40AF"),    # palette d'exemple
    ("#E11D48", "#7C3AED"),    # accent de ton moyen : ni le sombre ni le blanc n'y tiennent 4,5:1
    ("#1E3A8A", "#FACC15"),    # accent sombre, primaire claire
])
def test_derivees_des_landings_tiennent_leurs_contrastes(accent, primaire):
    """Quelle que soit la palette, les couleurs de texte dérivées tiennent leur seuil (ou le build échoue)."""
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    tokens["color"]["accent"]["$value"] = accent
    tokens["color"]["primary"]["$value"] = primaire
    tokens["color"]["white"] = {"$value": "#FFFFFF"}
    tokens["radius"].update({"cta": {"$value": "999px"}, "badge": {"$value": "999px"},
                             "input": {"$value": "8px"}})
    tokens["font"]["mono"] = {"$value": ["JetBrains Mono", "monospace"]}
    v = _valeurs_landings(tokens)
    clair, blanc, sombre = "#F8FAFC", "#FFFFFF", "#0F172A"
    assert build_tokens.contraste(v["--brand-muted"], clair) >= 4.6
    assert build_tokens.contraste(v["--brand-muted"], blanc) >= 4.6
    assert build_tokens.contraste(v["--brand-muted-on-dark"], sombre) >= 4.6
    assert build_tokens.contraste(v["--brand-primary-text"], clair) >= 4.6
    assert build_tokens.contraste(v["--brand-accent-on-dark"], sombre) >= 4.6
    assert build_tokens.contraste(v["--brand-on-accent"], accent) >= 3
    assert build_tokens.contraste(v["--brand-field-border"], blanc) >= 3
    assert build_tokens.contraste(v["--brand-danger"], blanc) >= 4.6
