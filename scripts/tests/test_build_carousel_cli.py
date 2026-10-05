"""Tests de la ligne de commande de 06-graphic-design/scripts/build-carousel.py.

Le script écrit des fichiers dans le dépôt. Ces tests vérifient qu'il ne le fait
que sur demande explicite : ni à vide, ni sur un argument non reconnu, ni en
dry-run. Ils lancent une copie du script posée dans un dépôt fictif (voir
`carrousel_fictif.py`). L'export PDF, qui exige Playwright, n'est pas lancé :
la construction se teste avec `--sans-pdf`.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

_aide = importlib.util.spec_from_file_location(
    "carrousel_fictif", Path(__file__).with_name("carrousel_fictif.py"))
fictif = importlib.util.module_from_spec(_aide)
_aide.loader.exec_module(fictif)


@pytest.fixture
def depot(tmp_path):
    return fictif.creer_depot(tmp_path / "depot")


def lancer(depot: Path, *args: str) -> subprocess.CompletedProcess:
    script = depot / "06-graphic-design" / "scripts" / "build-carousel.py"
    return subprocess.run([sys.executable, str(script), *args],
                          capture_output=True, text=True, cwd=str(depot))


def test_sans_argument_sort_en_2_sans_rien_ecrire(depot):
    avant = fictif.empreinte(depot)
    result = lancer(depot)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "usage:" in result.stdout
    assert fictif.empreinte(depot) == avant


def test_dry_run_all_liste_sans_ecrire(depot):
    avant = fictif.empreinte(depot)
    result = lancer(depot, "--all", "--dry-run")
    assert result.returncode == 0, result.stderr
    lignes = [l for l in result.stdout.splitlines() if "[dry-run]" in l]
    assert len(lignes) == len(fictif.SPECS), result.stdout
    for ligne in lignes:
        assert "carrousel-" in ligne
    assert fictif.empreinte(depot) == avant


def test_slug_inconnu_sort_en_2_sans_rien_ecrire(depot):
    avant = fictif.empreinte(depot)
    result = lancer(depot, "slug-qui-n-existe-pas")
    assert result.returncode == 2
    assert "slug inconnu" in result.stderr
    assert "demo-portrait" in result.stderr
    assert fictif.empreinte(depot) == avant


def test_help_sort_en_0_sans_rien_ecrire(depot):
    avant = fictif.empreinte(depot)
    result = lancer(depot, "--help")
    assert result.returncode == 0
    assert "--dry-run" in result.stdout
    assert fictif.empreinte(depot) == avant


def test_all_et_slug_ensemble_sont_refuses(depot):
    avant = fictif.empreinte(depot)
    result = lancer(depot, "--all", "demo-these")
    assert result.returncode == 2
    assert "s'excluent" in result.stderr
    assert fictif.empreinte(depot) == avant


def test_spec_designee_par_son_chemin(depot):
    spec = fictif.dossier_spec(depot, fictif.SPEC_THESE) / "carrousel.json"
    result = lancer(depot, str(spec), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "demo-these" in result.stdout


def test_sans_pdf_ecrit_le_html_seul(depot):
    result = lancer(depot, "demo-these", "--sans-pdf")
    assert result.returncode == 0, result.stderr
    dossier = fictif.dossier_spec(depot, fictif.SPEC_THESE)
    html = (dossier / "index.html").read_text(encoding="utf-8")
    assert html.count('<section class="slide') == len(fictif.SPEC_THESE["slides"])
    assert not (dossier / "exports").exists()


def test_tokens_absents_sortent_en_2(depot):
    (depot / "01-brand" / "tokens.json").unlink()
    result = lancer(depot, "demo-these", "--sans-pdf")
    assert result.returncode == 2
    assert "tokens.json" in result.stderr
    assert not (fictif.dossier_spec(depot, fictif.SPEC_THESE) / "index.html").exists()


def test_aucune_spec_avec_all_sort_en_2(tmp_path):
    racine = fictif.creer_depot(tmp_path / "vide")
    for spec in fictif.SPECS:
        (fictif.dossier_spec(racine, spec) / "carrousel.json").unlink()
    result = lancer(racine, "--all", "--dry-run")
    assert result.returncode == 2
    assert "aucune spec" in result.stderr
