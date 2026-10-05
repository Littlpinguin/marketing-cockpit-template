"""Couleurs du générateur de carrousels : aucune valeur hors de tokens.json.

`06-graphic-design/scripts/build-carousel.py` est un fichier Python : une couleur
écrite en dur dans ce script repartirait dans les `index.html` des carrousels à
chaque reconstruction, sans qu'aucun contrôle de fichier texte ne la voie. Ces
tests referment ce trou : le rendu ne cite que des couleurs de `tokens.json`.

Ils travaillent sur un dépôt fictif (voir `carrousel_fictif.py`) et ne
construisent rien : ils appellent la fonction de rendu, qui n'écrit pas.
"""
from __future__ import annotations

import importlib.util
import json
import re
from pathlib import Path

import pytest

_aide = importlib.util.spec_from_file_location(
    "carrousel_fictif", Path(__file__).with_name("carrousel_fictif.py"))
fictif = importlib.util.module_from_spec(_aide)
_aide.loader.exec_module(fictif)

HEX = re.compile(r"#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})\b")


@pytest.fixture(scope="module")
def depot(tmp_path_factory):
    return fictif.creer_depot(tmp_path_factory.mktemp("depot"))


@pytest.fixture(scope="module")
def bc(depot):
    return fictif.charger(depot)


def normaliser(hexa: str) -> str:
    """« #fff » et « #FFFFFF » désignent la même couleur : une seule écriture."""
    chiffres = hexa.lstrip("#")
    if len(chiffres) == 3:
        chiffres = "".join(c * 2 for c in chiffres)
    return "#" + chiffres.upper()


PALETTE = {normaliser(n["$value"]) for n in fictif.TOKENS_FICTIFS["color"].values()}


@pytest.mark.parametrize("spec", fictif.SPECS, ids=[s["slug"] for s in fictif.SPECS])
def test_le_rendu_ne_cite_aucune_couleur_hors_tokens(bc, depot, spec):
    html = bc.document(json.loads(json.dumps(spec)), fictif.dossier_spec(depot, spec))
    hors_palette = sorted({normaliser(m.group(0)) for m in HEX.finditer(html)} - PALETTE)
    assert hors_palette == [], (
        f"couleurs absentes de tokens.json dans le rendu « {spec['slug']} » : "
        f"{', '.join(hors_palette)}")


def test_les_roles_viennent_de_tokens_json(bc):
    c = bc.couleurs()
    couleurs = fictif.TOKENS_FICTIFS["color"]
    assert c["primaire"] == couleurs["primary"]["$value"]
    assert c["accent"] == couleurs["accent"]["$value"]
    assert c["tertiaire"] == couleurs["tertiary"]["$value"]
    assert c["sombre"] == couleurs["dark"]["$value"]
    assert c["clair"] == couleurs["light"]["$value"]
    assert c["blanc"] == couleurs["white"]["$value"]
    assert c["primaire-clair"] == couleurs["primary-light"]["$value"]


def test_un_role_se_remappe_depuis_la_spec(bc):
    spec = {"marque": {"couleurs": {"primaire": "color.accent"}}}
    assert bc.couleurs(spec)["primaire"] == fictif.TOKENS_FICTIFS["color"]["accent"]["$value"]


def test_role_obligatoire_absent_refuse(bc):
    tokens = json.loads(json.dumps(fictif.TOKENS_FICTIFS))
    del tokens["color"]["dark"]
    with pytest.raises(bc.ErreurSpec, match="sombre"):
        bc.couleurs(tokens=tokens)


def test_roles_optionnels_retombent_sur_les_obligatoires(bc):
    tokens = json.loads(json.dumps(fictif.TOKENS_FICTIFS))
    for cle in ("tertiary", "white", "primary-light"):
        del tokens["color"][cle]
    c = bc.couleurs(tokens=tokens)
    assert "tertiaire" not in c
    assert c["blanc"] == c["clair"]
    assert c["primaire-clair"] == c["primaire"]
    # Sans tertiaire, le dégradé n'a que deux arrêts.
    assert bc.degrade_css(c).count("%") == 2
    assert bc.arrets_svg(c).count("<stop") == 2


def test_aucun_hex_en_dur_dans_la_feuille_de_style_du_script(bc):
    """La feuille de style ne porte que des jetons : les valeurs arrivent au rendu."""
    assert HEX.search(bc.CSS) is None
    c = bc.couleurs()
    teinte = bc.teinter(bc.CSS, c)
    assert "%primaire%" not in teinte and "%sombre:" not in teinte
    assert normaliser(c["primaire"]) in {normaliser(m.group(0)) for m in HEX.finditer(teinte)}


def test_la_police_vient_de_tokens_json(bc, depot):
    assert bc.police() == "Inter"
    spec = json.loads(json.dumps(fictif.SPEC_PORTRAIT))
    html = bc.document(spec, fictif.dossier_spec(depot, spec))
    assert "font-family:'Inter',sans-serif" in html
    assert 'font-family="Inter"' in html   # textes vecteur du bouton CTA et des fenêtres


def test_sans_police_dans_les_tokens_refuse(bc):
    with pytest.raises(bc.ErreurSpec, match="police"):
        bc.police({"font": {}})
