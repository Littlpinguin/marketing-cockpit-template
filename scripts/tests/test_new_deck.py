"""Tests de 06-graphic-design/scripts/new-deck.py, le pont entre le moteur de
slides vendorisé et la marque du projet.

Le starter (templates/base.html, vendorisé depuis slides-agent) garde son
`:root` neutre ; un deck prend celui de presentations/tokens.css, généré depuis
01-brand/tokens.json. Deux familles de tests :
  - la composition, sur des fichiers fictifs ;
  - le câblage réel : le starter composé avec le tokens.css du dépôt, puis avec
    la marque fictive d'un tokens.json jetable, passe la QA des decks (Chromium,
    sauté proprement si Playwright ou le navigateur manquent).
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
SCRIPT = REPO / "06-graphic-design" / "scripts" / "new-deck.py"
MOTEUR = REPO / "06-graphic-design" / "presentations"
QA = MOTEUR / "scripts" / "qa.py"
BUILD_TOKENS = REPO / "scripts" / "build-tokens.py"


def _charger():
    spec = importlib.util.spec_from_file_location("new_deck", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new_deck = _charger()

STARTER = """<!DOCTYPE html>
<!--
  VENDORED from slides-agent (https://example.invalid), templates/base.html,
  Register: docs/vendored-slides.md
-->
<html><head><title>{{DECK_TITLE}}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>
/* commentaire qui cite :root { sans en être un } */
:root {
  --brand-primary: #1E40AF;
  --brand-pattern: url("data:image/svg+xml,%3Csvg%3E{}%3C/svg%3E");
  --font-display: 'Inter', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}
.slide { color: var(--brand-primary); }
</style></head><body><section class="slide"></section></body></html>
"""

TOKENS_CSS = """/* en-tête : le premier :root ci-dessous */
:root {
  /* brand-tokens:start */
  --brand-primary: #2F6F5E;
  /* brand-tokens:end */
  --brand-pattern: none;
  --font-display: 'Fictive Serif', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
}
:root { --carousel-fs-body: 50px; }
"""


def racine_fictive(tmp_path: Path, starter: str = STARTER, tokens: str = TOKENS_CSS) -> Path:
    root = tmp_path / "repo"
    (root / new_deck.STARTER).parent.mkdir(parents=True)
    (root / new_deck.STARTER).write_text(starter, encoding="utf-8")
    (root / new_deck.TOKENS).write_text(tokens, encoding="utf-8")
    return root


def lancer(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root), *args],
                          capture_output=True, text=True)


# --------------------------------------------------------------------------
# Composition
# --------------------------------------------------------------------------

def test_bloc_root_ignore_commentaires_et_chaines():
    debut, fin = new_deck.bloc_root(STARTER, STARTER.find("<style"))
    bloc = STARTER[debut:fin]
    assert bloc.startswith(":root {") and bloc.endswith("}")
    assert "--font-mono" in bloc and ".slide" not in bloc


def test_composer_remplace_le_root_par_celui_de_la_marque():
    deck = new_deck.composer(STARTER, TOKENS_CSS, "Revue & bilan")
    assert "--brand-primary: #2F6F5E;" in deck
    assert "#1E40AF" not in deck
    assert "/* brand-tokens:start */" in deck           # le bloc reste reconnaissable
    assert "--carousel-fs-body" not in deck             # seul le premier :root est repris
    assert ".slide { color: var(--brand-primary); }" in deck
    assert "<title>Revue &amp; bilan</title>" in deck
    assert new_deck.BANDEAU_TETE not in deck            # le deck appartient au projet
    assert deck.startswith("<!DOCTYPE html>\n<html>")


def test_bloc_root_absent_refuse():
    with pytest.raises(new_deck.DeckError):
        new_deck.composer(STARTER.replace(":root {", ".x {"), TOKENS_CSS)


def test_police_non_chargee_signalee():
    deck = new_deck.composer(STARTER, TOKENS_CSS)
    assert new_deck.familles_manquantes(deck) == ["Fictive Serif"]
    assert new_deck.familles_manquantes(new_deck.composer(STARTER, STARTER[STARTER.find(":root"):])) == []


def test_cli_ecrit_le_deck_et_refuse_d_ecraser(tmp_path):
    root = racine_fictive(tmp_path)
    resultat = lancer(root, "revue-t3", "--titre", "Revue T3")
    assert resultat.returncode == 0, resultat.stderr
    assert "Fictive Serif" in resultat.stdout           # avertissement sur les polices
    deck = root / new_deck.DECKS / "revue-t3.html"
    assert "<title>Revue T3</title>" in deck.read_text(encoding="utf-8")
    assert lancer(root, "revue-t3").returncode == 1
    assert lancer(root, "revue-t3", "--force").returncode == 0


def test_cli_slug_invalide(tmp_path):
    assert lancer(racine_fictive(tmp_path), "Revue T3").returncode == 2


def test_le_root_du_starter_reel_est_remplacable():
    """Le starter vendorisé et le tokens.css du dépôt se composent sans perte de variable."""
    starter = (REPO / new_deck.STARTER).read_text(encoding="utf-8")
    tokens = (REPO / new_deck.TOKENS).read_text(encoding="utf-8")
    deck = new_deck.composer(starter, tokens)
    declarees = lambda texte: set(re.findall(r"(--[\w-]+)\s*:", texte))   # noqa: E731
    d, f = new_deck.bloc_root(starter, starter.find("<style"))
    attendues = declarees(starter[d:f])
    d, f = new_deck.bloc_root(deck, deck.find("<style"))
    assert sorted(attendues - declarees(deck[d:f])) == []


# --------------------------------------------------------------------------
# Câblage réel : le deck composé passe la QA
# --------------------------------------------------------------------------

def _chromium_disponible() -> bool:
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


navigateur = pytest.mark.skipif(not _chromium_disponible(),
                                reason="Playwright ou Chromium indisponible sur cette machine")


def _qa(deck: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(QA), str(deck), "--wait", "300", *options],
                          capture_output=True, text=True, timeout=300)


@navigateur
def test_starter_aux_couleurs_du_tokens_css_du_depot_passe_la_qa(tmp_path):
    starter = (REPO / new_deck.STARTER).read_text(encoding="utf-8")
    tokens = (REPO / new_deck.TOKENS).read_text(encoding="utf-8")
    deck = tmp_path / "deck.html"
    deck.write_text(new_deck.composer(starter, tokens), encoding="utf-8")
    familles = re.findall(r"--font-(?:display|mono):\s*'([^']+)'", tokens)
    options = [opt for famille in familles for opt in ("--font", famille)]
    resultat = _qa(deck, *options)
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr


# Marque fictive volontairement exigeante : une primaire claire, que le registre
# des étiquettes doit assombrir pour tenir 4,5:1 sur fond clair.
MARQUE_FICTIVE = {
    "BRAND_COLOR_PRIMARY": "#38BDF8", "BRAND_COLOR_ACCENT": "#FACC15",
    "BRAND_COLOR_DARK": "#111827", "BRAND_COLOR_LIGHT": "#FFFFFF",
    "BRAND_FONT_PRIMARY": "Fictive Sans", "BRAND_FONT_SECONDARY": "Fictive Mono",
}


@navigateur
def test_deck_d_une_marque_fictive_passe_la_qa(tmp_path):
    root = tmp_path / "repo"
    (root / "01-brand").mkdir(parents=True)
    gabarit = (REPO / "_templates/brand/tokens.json").read_text(encoding="utf-8")
    rempli = re.sub(r"\{\{([A-Z0-9_]+)\}\}", lambda m: MARQUE_FICTIVE.get(m.group(1), m.group(0)),
                    gabarit)
    (root / "01-brand/tokens.json").write_text(rempli, encoding="utf-8")
    (root / "01-brand/style-guide.md").write_text(
        (REPO / "_templates/brand/style-guide.md").read_text(encoding="utf-8"), encoding="utf-8")
    # Toutes les cibles « block » de build-tokens.toml doivent exister dans la racine jetable.
    for rel in (new_deck.STARTER, new_deck.TOKENS, "05-web-content/templates/assets/tokens.css"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text((REPO / rel).read_text(encoding="utf-8"), encoding="utf-8")

    genere = subprocess.run([sys.executable, str(BUILD_TOKENS), "--root", str(root),
                             "--config", str(REPO / "scripts/build-tokens.toml")],
                            capture_output=True, text=True)
    assert genere.returncode == 0, genere.stderr
    tokens = (root / new_deck.TOKENS).read_text(encoding="utf-8")
    assert "--label-accent: #38BDF8;" not in tokens     # la primaire claire a été assombrie

    assert lancer(root, "marque-fictive").returncode == 0
    deck = root / new_deck.DECKS / "marque-fictive.html"
    resultat = _qa(deck, "--tokens", str(root / "01-brand/tokens.json"), "--format", "json")
    rapport = json.loads(resultat.stdout)
    assert rapport["summary"]["fonts"] == ["Fictive Sans", "Fictive Mono"]
    assert resultat.returncode == 0, resultat.stdout
