"""Tests unitaires du plafonnement des constats de `qa.py`, sans navigateur.

`limiter()` est la seule pièce de `qa.py` qui décide ce que le rapport montre et
ce qu'il tait. Elle se teste sans Chromium, contrairement au reste du script :
d'où ce fichier séparé de `test_qa_slides.py`, qui lui pilote un vrai navigateur.

Seul Playwright est requis, parce que `qa.py` sort en 2 à l'import s'il manque.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "06-graphic-design" / "presentations" / "scripts" / "qa.py"


def _charger_qa():
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return None
    spec = importlib.util.spec_from_file_location("qa_slides", QA)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa = _charger_qa()

pytestmark = pytest.mark.skipif(qa is None, reason="Playwright indisponible sur cette machine")


def constat(type_: str, niveau: str = "erreur", n: int = 0) -> dict:
    return {"niveau": niveau, "type": type_, "message": f"constat {type_} {n}"}


def test_sous_le_plafond_rien_n_est_touche():
    entree = [constat("contraste", n=i) for i in range(5)]
    assert qa.limiter(entree) == entree


def test_au_plafond_exact_aucune_ligne_de_resume():
    entree = [constat("contraste", n=i) for i in range(qa.MAX_PAR_SLIDE)]
    sortie = qa.limiter(entree)
    assert len(sortie) == qa.MAX_PAR_SLIDE
    assert not [c for c in sortie if c["niveau"] == "resume"]


def test_le_resume_porte_le_nombre_d_ecartes():
    entree = [constat("contraste", n=i) for i in range(qa.MAX_PAR_SLIDE + 5)]
    sortie = qa.limiter(entree)
    resumes = [c for c in sortie if c["niveau"] == "resume"]
    assert len(resumes) == 1
    assert "5 autres constats" in resumes[0]["message"]
    assert resumes[0]["type"] == "contraste"


def test_le_resume_ne_compte_ni_en_erreur_ni_en_avertissement():
    """C'est tout l'enjeu : une ligne de résumé ne doit pas gonfler les compteurs."""
    entree = [constat("contraste", n=i) for i in range(qa.MAX_PAR_SLIDE + 3)]
    sortie = qa.limiter(entree)
    assert qa.compter(sortie, "erreur") == qa.MAX_PAR_SLIDE
    assert qa.compter(sortie, "avertissement") == 0
    assert qa.compter(entree, "erreur") == qa.MAX_PAR_SLIDE + 3


def test_chaque_famille_a_son_propre_plafond():
    entree = (
        [constat("contraste", n=i) for i in range(qa.MAX_PAR_SLIDE + 2)]
        + [constat("police", niveau="avertissement", n=i) for i in range(qa.MAX_PAR_SLIDE + 4)]
        + [constat("folio", n=0)]
    )
    sortie = qa.limiter(entree)
    resumes = {c["type"]: c["message"] for c in sortie if c["niveau"] == "resume"}
    assert set(resumes) == {"contraste", "police"}
    assert "2 autres constats" in resumes["contraste"]
    assert "4 autres constats" in resumes["police"]
    assert qa.compter(sortie, "erreur") == qa.MAX_PAR_SLIDE + 1
    assert qa.compter(sortie, "avertissement") == qa.MAX_PAR_SLIDE


def test_le_resume_garde_le_niveau_resume_quel_que_soit_le_niveau_ecarte():
    entree = [constat("corps-serre", niveau="avertissement", n=i)
              for i in range(qa.MAX_PAR_SLIDE + 1)]
    sortie = qa.limiter(entree)
    assert [c["niveau"] for c in sortie if c["type"] == "corps-serre"][-1] == "resume"
