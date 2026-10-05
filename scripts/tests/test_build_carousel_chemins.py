"""Chemins d'assets du générateur de carrousels.

Le HTML d'un carrousel ne doit citer aucune URL absolue : ni `file://`, ni chemin
de poste. Chaque asset est référencé relativement au dossier de sortie, de sorte
qu'un carrousel reste ouvrable après un clone du dépôt ailleurs.

Ces tests travaillent sur un dépôt fictif (voir `carrousel_fictif.py`) et ne
construisent rien : ils appellent la fonction de rendu, qui n'écrit pas. Un
contrôle d'empreinte vérifie qu'aucun fichier n'a bougé.
"""
from __future__ import annotations

import importlib.util
import json
import re
import urllib.parse
from pathlib import Path

import pytest

_aide = importlib.util.spec_from_file_location(
    "carrousel_fictif", Path(__file__).with_name("carrousel_fictif.py"))
fictif = importlib.util.module_from_spec(_aide)
_aide.loader.exec_module(fictif)


@pytest.fixture(scope="module")
def depot(tmp_path_factory):
    return fictif.creer_depot(tmp_path_factory.mktemp("depot"))


@pytest.fixture(scope="module")
def bc(depot):
    return fictif.charger(depot)


def copie(spec: dict) -> dict:
    return json.loads(json.dumps(spec))


def liens(html: str) -> set[str]:
    """URL locales portées par src, href ou url() dans le document."""
    trouves = set(re.findall(r'(?:src|href)="([^"]+)"', html))
    trouves |= set(re.findall(r"url\(['\"]?([^'\")]+)", html))
    return {u for u in trouves if not u.startswith(("http", "data:", "#", "/"))}


@pytest.mark.parametrize("spec", fictif.SPECS, ids=[s["slug"] for s in fictif.SPECS])
def test_le_document_ne_cite_aucune_url_absolue(bc, depot, spec):
    avant = fictif.empreinte(depot)
    html = bc.document(copie(spec), fictif.dossier_spec(depot, spec))
    assert "file://" not in html
    assert str(depot) not in html
    assert fictif.empreinte(depot) == avant


@pytest.mark.parametrize("spec", fictif.SPECS, ids=[s["slug"] for s in fictif.SPECS])
def test_chaque_asset_resout_depuis_le_dossier_de_sortie(bc, depot, spec):
    out_dir = fictif.dossier_spec(depot, spec)
    html = bc.document(copie(spec), out_dir)
    manquants = [u for u in liens(html) if not (out_dir / urllib.parse.unquote(u)).exists()]
    assert manquants == []


def test_les_noms_a_espaces_et_accents_sont_encodes(bc, depot):
    spec = copie(fictif.SPEC_PORTRAIT)
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert "atelier%20%28v2%29.svg" in html
    assert "vue%20fen%C3%AAtre.svg" in html


def test_la_police_est_servie_en_local(bc, depot):
    spec = copie(fictif.SPEC_PORTRAIT)
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert "fonts.googleapis.com" not in html
    assert re.search(r"@import url\('(\.\./)+01-brand/assets/fonts/fonts\.css'\);", html)


def test_sans_fonts_css_aucun_import(tmp_path):
    racine = fictif.creer_depot(tmp_path / "sans-police", polices=False)
    module = fictif.charger(racine)
    spec = copie(fictif.SPEC_THESE)
    html = module.document(spec, fictif.dossier_spec(racine, spec))
    assert "@import" not in html


def test_un_dossier_de_sortie_different_donne_un_autre_chemin(bc, depot, tmp_path):
    """Le chemin est calculé au rendu, jamais figé au chargement du module."""
    sortie = tmp_path / "carrousel-essai"
    html = bc.document(copie(fictif.SPEC_PORTRAIT), sortie)
    assert "file://" not in html
    forme = [u for u in liens(html) if "forme-titre" in u]
    assert forme, "la forme de titre n'est plus référencée"
    cible = (sortie / urllib.parse.unquote(forme[0])).resolve()
    assert cible == (depot / fictif.ASSETS["forme_titre"]).resolve()


def test_sans_forme_de_titre_un_bloc_css_la_remplace(bc, depot):
    spec = copie(fictif.SPEC_PORTRAIT)
    del spec["marque"]["forme_titre"]
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert 'class="blob css"' in html


def test_sans_logo_ni_pied_rien_n_est_invente(bc, depot):
    spec = copie(fictif.SPEC_THESE)
    spec["marque"] = {}
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert 'class="brand-logo"' not in html
    assert 'class="foot"' not in html


def test_le_logo_porte_la_classe_controlee_par_la_qa(bc, depot):
    """`qa-visuel.py` contrôle `.brand-logo` : le générateur doit l'employer."""
    spec = copie(fictif.SPEC_PORTRAIT)
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert 'class="brand-logo"' in html


def test_type_de_slide_inconnu_refuse(bc, depot):
    spec = copie(fictif.SPEC_THESE)
    spec["slides"].append({"type": "inexistant"})
    with pytest.raises(bc.ErreurSpec, match="inexistant"):
        bc.document(spec, fictif.dossier_spec(depot, spec))


def test_rel_refuse_de_travailler_hors_rendu(bc):
    with pytest.raises(RuntimeError):
        bc.rel("01-brand/assets/logos/logo_acme_principal.svg")
