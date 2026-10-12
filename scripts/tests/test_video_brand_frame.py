"""Tests de 08-video/scripts/brand-frame.py (frame.md et brand.css d'un projet HyperFrames)."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "08-video" / "scripts" / "brand-frame.py"


def _charger():
    spec = importlib.util.spec_from_file_location("brand_frame", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bf = _charger()


def _racine(tmp_path: Path, *, tokens: dict | None = None, remplir: bool = True) -> Path:
    root = tmp_path / "repo"
    for rel in ("docs/placeholders.json", "_templates/brand/tokens.json",
                "scripts/build-tokens.toml", "08-video/lib/brand.css"):
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text((REPO / rel).read_text(encoding="utf-8"), encoding="utf-8")
    if remplir:
        contenu = tokens if tokens is not None else bf.tokens_exemple(root)
        (root / "01-brand").mkdir()
        (root / "01-brand/tokens.json").write_text(json.dumps(contenu, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
    return root


def _lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def _retirer(tokens: dict, chemin: str) -> None:
    """Supprime le token « a.b » de l'arbre, comme le ferait un fork qui le retire."""
    *parents, dernier = chemin.split(".")
    noeud = tokens
    for parent in parents:
        noeud = noeud[parent]
    del noeud[dernier]


def _couleurs_frame(frame: str) -> dict[str, str]:
    """Les entrées hex du bloc `colors:` du frontmatter."""
    section = frame.split("\ncolors:\n", 1)[1].split("\n\ntypography:", 1)[0]
    return dict(re.findall(r'^  ([a-z-]+): "(#[0-9A-Fa-f]{6})"$', section, re.M))


def _hex_du_css(css: str) -> dict[str, str]:
    """Les variables `--brand-*` de brand.css dont la valeur est un hex, sans le préfixe."""
    return dict(re.findall(r"^\s*--brand-([a-z-]+):\s*(#[0-9A-Fa-f]{6});", css, re.M))


def test_frame_porte_la_palette_et_les_polices(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    res = _lancer(str(projet), "--racine", str(root))
    assert res.returncode == 0, res.stderr
    frame = (projet / "frame.md").read_text(encoding="utf-8")
    assert frame.startswith("---\n") and "\n---\n" in frame[4:]
    assert 'primary: "#1E40AF"' in frame and 'accent: "#F59E0B"' in frame
    assert 'fontFamily: "Inter"' in frame and 'fontFamily: "JetBrains Mono"' in frame
    assert 'safe-bottom: "420px"' in frame and "1080×1920" in frame
    assert "{{" not in frame and "—" not in frame
    assert "01-brand/style-guide.md" in frame and "08-video/motion.md" in frame


def test_frontmatter_est_du_yaml_valide(tmp_path):
    yaml = pytest.importorskip("yaml")
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    texte = (projet / "frame.md").read_text(encoding="utf-8")
    entete = yaml.safe_load(texte.split("---\n")[1])
    assert set(entete) >= {"version", "name", "colors", "typography", "spacing", "components"}
    assert entete["typography"]["display"]["px"] == 120
    assert entete["typography"]["label"]["upper"] is True
    assert entete["colors"]["dark"] == "#0F172A"


def test_brand_css_est_la_cible_generee(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    css = (projet / "brand.css").read_text(encoding="utf-8")
    assert "--brand-primary: #1E40AF;" in css and "brand-tokens:start" in css


def test_check_detecte_une_retouche(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    assert _lancer(str(projet), "--racine", str(root), "--check").returncode == 0
    frame = projet / "frame.md"
    frame.write_text(frame.read_text(encoding="utf-8").replace("#1E40AF", "#FF0000"), encoding="utf-8")
    res = _lancer(str(projet), "--racine", str(root), "--check")
    assert res.returncode == 1 and "frame.md" in res.stdout


def test_check_garde_la_toile_du_projet(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root), "--aspect", "1920x1080").returncode == 0
    frame = (projet / "frame.md").read_text(encoding="utf-8")
    assert "1920×1080" in frame and 'safe-left: "96px"' in frame
    assert _lancer(str(projet), "--racine", str(root), "--check").returncode == 0


def test_placeholders_non_resolus_refuses(tmp_path):
    brut = json.loads((REPO / "_templates/brand/tokens.json").read_text(encoding="utf-8"))
    root = _racine(tmp_path, tokens=brut)
    res = _lancer(str(tmp_path / "projet"), "--racine", str(root))
    assert res.returncode == 1 and "placeholders non résolus" in res.stderr


@pytest.mark.parametrize("chemin", ["typography.stat", "font.mono"])
def test_token_manquant_nomme_sans_trace(tmp_path, chemin):
    root0 = _racine(tmp_path / "a")
    tokens = json.loads((root0 / "01-brand/tokens.json").read_text(encoding="utf-8"))
    _retirer(tokens, chemin)
    root = _racine(tmp_path / "b", tokens=tokens)
    res = _lancer(str(tmp_path / "projet"), "--racine", str(root))
    assert res.returncode == 1
    assert chemin in res.stderr and "Traceback" not in res.stderr


def test_exemple_sans_tokens(tmp_path):
    root = _racine(tmp_path, remplir=False)
    projet = tmp_path / "projet"
    res = _lancer(str(projet), "--racine", str(root), "--exemple")
    assert res.returncode == 0, res.stderr
    frame = (projet / "frame.md").read_text(encoding="utf-8")
    assert "Acme Inc. · Frame" in frame
    assert ".." not in frame      # un nom qui finit par un point ne double pas le point de la phrase


def test_toile_inconnue_code_2(tmp_path):
    root = _racine(tmp_path)
    assert _lancer(str(tmp_path / "p"), "--racine", str(root), "--aspect", "800x600").returncode == 2


# --------------------------------------------------------------------------
# Les couleurs de frame.md viennent de la cible build-tokens, jamais recalculées
# --------------------------------------------------------------------------

PALETTES = [
    pytest.param({}, id="exemple"),
    # Accent sombre : il doit être éclairci pour tenir 4,5:1 sur le sombre de la marque.
    pytest.param({"primary": "#7C3AED", "accent": "#1E3A8A"}, id="accent-sombre"),
]


@pytest.mark.parametrize("surcharge", PALETTES)
def test_couleurs_du_frame_sont_celles_de_brand_css(tmp_path, surcharge):
    tokens = bf.tokens_exemple(REPO)
    for nom, hexa in surcharge.items():
        tokens["color"][nom]["$value"] = hexa
    root = _racine(tmp_path, tokens=tokens)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    frame = (projet / "frame.md").read_text(encoding="utf-8")
    couleurs = _couleurs_frame(frame)
    dans_css = _hex_du_css((projet / "brand.css").read_text(encoding="utf-8"))
    assert {"primary-deep", "text-on-dark", "accent-on-dark", "on-accent"} <= set(dans_css)
    for nom, valeur in dans_css.items():
        assert couleurs.get(nom, "").upper() == valeur.upper(), nom
    assert {"primary", "accent", "dark", "light", "white"} <= set(couleurs)
    assert "primary-soft" not in couleurs and "accent-soft" not in couleurs    # rgba : hors frame.md
    assert 'textColor: "{colors.on-accent}"' in frame
    if surcharge:
        assert couleurs["accent-on-dark"].upper() != couleurs["accent"].upper()


# --------------------------------------------------------------------------
# Familles de polices : jamais un mot-clé générique CSS comme police de marque
# --------------------------------------------------------------------------

def test_famille_saute_les_mots_cles_generiques():
    tokens = bf.tokens_exemple(REPO)
    tokens["font"]["mono"]["$value"] = ["ui-monospace", "Menlo", "monospace"]    # pas de police secondaire
    frame = bf.construire_frame(tokens, entreprise="Marque", aspect="1080x1920")
    assert 'label: { fontFamily: "Menlo"' in frame


def test_famille_toute_generique_garde_le_premier_mot_cle():
    tokens = bf.tokens_exemple(REPO)
    tokens["font"]["display"]["$value"] = ["system-ui", "sans-serif"]
    frame = bf.construire_frame(tokens, entreprise="Marque", aspect="1080x1920")
    assert 'display: { fontFamily: "system-ui"' in frame


# --------------------------------------------------------------------------
# Rayons : un token absent est une erreur, pas un 0px silencieux
# --------------------------------------------------------------------------

@pytest.mark.parametrize("nom", ["cta", "badge", "card"])
def test_rayon_absent_leve_une_erreur(nom):
    tokens = bf.tokens_exemple(REPO)
    _retirer(tokens, f"radius.{nom}")
    with pytest.raises(bf.TokenError, match=f"radius.{nom}"):
        bf.construire_frame(tokens, entreprise="Marque", aspect="1080x1920")


# --------------------------------------------------------------------------
# --check : chaque fichier dérive indépendamment
# --------------------------------------------------------------------------

def test_check_detecte_une_retouche_de_brand_css_seule(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    css = projet / "brand.css"
    css.write_text(css.read_text(encoding="utf-8").replace("#1E40AF", "#FF0000"), encoding="utf-8")
    res = _lancer(str(projet), "--racine", str(root), "--check")
    assert res.returncode == 1
    assert "brand.css" in res.stdout and "frame.md" not in res.stdout


# --------------------------------------------------------------------------
# Erreurs d'environnement : message net, code 1, jamais de trace
# --------------------------------------------------------------------------

@pytest.mark.parametrize("options", [[], ["--check"]])
def test_frame_md_illisible_donne_une_erreur_nette(tmp_path, options):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    projet.mkdir()
    (projet / "frame.md").write_bytes(b"\xff\xfe pas de l'utf-8")
    res = _lancer(str(projet), "--racine", str(root), *options)
    assert res.returncode == 1
    assert res.stderr.startswith("ERREUR") and "frame.md" in res.stderr and "Traceback" not in res.stderr


def test_dossier_qui_est_un_fichier_donne_une_erreur_nette(tmp_path):
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    projet.write_text("pas un dossier", encoding="utf-8")
    res = _lancer(str(projet), "--racine", str(root))
    assert res.returncode == 1
    assert res.stderr.startswith("ERREUR") and "Traceback" not in res.stderr


@pytest.mark.parametrize("manquant", ["scripts/build-tokens.toml", "08-video/lib/brand.css"])
def test_racine_sans_les_fichiers_de_cible_ne_retombe_pas_sur_le_depot(tmp_path, manquant):
    root = _racine(tmp_path)
    (root / manquant).unlink()
    res = _lancer(str(tmp_path / "projet"), "--racine", str(root))
    assert res.returncode == 1
    assert Path(manquant).name in res.stderr and "Traceback" not in res.stderr


# --------------------------------------------------------------------------
# Nom de l'entreprise : .setup-completed
# --------------------------------------------------------------------------

def test_nom_de_l_entreprise_vient_de_setup_completed(tmp_path):
    root = _racine(tmp_path)
    (root / ".setup-completed").write_text(json.dumps({"company": "Maison Test"}), encoding="utf-8")
    projet = tmp_path / "projet"
    assert _lancer(str(projet), "--racine", str(root)).returncode == 0
    assert "Maison Test · Frame" in (projet / "frame.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("contenu", ["pas du json", "[1, 2]", '"texte"'])
def test_setup_completed_invalide_avertit_et_garde_marque(tmp_path, contenu):
    root = _racine(tmp_path)
    (root / ".setup-completed").write_text(contenu, encoding="utf-8")
    projet = tmp_path / "projet"
    res = _lancer(str(projet), "--racine", str(root))
    assert res.returncode == 0, res.stderr
    assert "Marque · Frame" in (projet / "frame.md").read_text(encoding="utf-8")
    assert ".setup-completed" in res.stderr and "Traceback" not in res.stderr
    assert len(res.stderr.strip().splitlines()) == 1


def test_toile_4_5_marge_de_titre_de_5_pour_cent(tmp_path):
    assert bf.MARGES["1080x1350"] == (68, 68, 54, 54)
    root = _racine(tmp_path)
    projet = tmp_path / "projet"
    res = _lancer(str(projet), "--racine", str(root), "--aspect", "1080x1350")
    assert res.returncode == 0, res.stderr
    frame = (projet / "frame.md").read_text(encoding="utf-8")
    assert "1080×1350" in frame
    for cle, valeur in (("safe-top", 68), ("safe-bottom", 68), ("safe-left", 54), ("safe-right", 54)):
        assert f'{cle}: "{valeur}px"' in frame, cle
    assert _lancer(str(projet), "--racine", str(root), "--check").returncode == 0
