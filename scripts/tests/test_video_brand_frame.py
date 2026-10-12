"""Tests de 08-video/scripts/brand-frame.py (frame.md et brand.css d'un projet HyperFrames)."""
from __future__ import annotations

import importlib.util
import json
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


def test_token_manquant_nomme_sans_trace(tmp_path):
    root0 = _racine(tmp_path / "a")
    tokens = json.loads((root0 / "01-brand/tokens.json").read_text(encoding="utf-8"))
    del tokens["typography"]["stat"]
    root = _racine(tmp_path / "b", tokens=tokens)
    res = _lancer(str(tmp_path / "projet"), "--racine", str(root))
    assert res.returncode == 1
    assert "typography.stat" in res.stderr and "Traceback" not in res.stderr


def test_exemple_sans_tokens(tmp_path):
    root = _racine(tmp_path, remplir=False)
    projet = tmp_path / "projet"
    res = _lancer(str(projet), "--racine", str(root), "--exemple")
    assert res.returncode == 0, res.stderr
    assert "Acme Inc. · Frame" in (projet / "frame.md").read_text(encoding="utf-8")


def test_toile_inconnue_code_2(tmp_path):
    root = _racine(tmp_path)
    assert _lancer(str(tmp_path / "p"), "--racine", str(root), "--aspect", "800x600").returncode == 2
