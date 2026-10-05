"""Tests de 06-graphic-design/scripts/qa_common.py (briques de QA visuelle partagées).

Pur Python : aucune dépendance à Playwright ni à un navigateur. Les scripts de QA
visuelle (decks, carrousels, visuels composés) collectent les valeurs CSS
calculées dans le navigateur et délèguent tout le calcul à ce module.

Les couleurs et polices de ces tests sont celles d'une marque fictive
(« Acme », les exemples de docs/placeholders.json) : jamais celles d'un client.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "06-graphic-design" / "scripts" / "qa_common.py"

# Marque fictive : primaire bleu nuit, accent ambre, sombre ardoise, clair neige.
PRIMAIRE = (30, 64, 175)    # #1E40AF
ACCENT = (245, 158, 11)     # #F59E0B
SOMBRE = (15, 23, 42)       # #0F172A
CLAIR = (248, 250, 252)     # #F8FAFC

TOKENS_FICTIFS = {
    "color": {
        "primary": {"$value": "#1E40AF"},
        "accent": {"$value": "#F59E0B"},
        "dark": {"$value": "#0F172A"},
        "light": {"$value": "#F8FAFC"},
        "derived": {
            "$description": "nuances dérivées, à portée limitée",
            "primary-deep": {
                "$value": "#16307F",
                "$extensions": {"cockpit": {"scope": ["06-graphic-design/presentations"]}},
            },
        },
    },
    "font": {
        "$type": "fontFamily",
        "primary": {"$value": ["Inter", "system-ui", "sans-serif"]},
        "mono": {"$value": ["ui-monospace", "Menlo", "monospace"]},
        "accent": {"$value": "'Fictive Serif', Georgia, serif"},
    },
}


def _charger():
    """Charge qa_common.py par chemin : son dossier n'est pas un paquet importable."""
    spec = importlib.util.spec_from_file_location("qa_common", MODULE)
    module = importlib.util.module_from_spec(spec)
    sys.modules["qa_common"] = module
    spec.loader.exec_module(module)
    return module


qa_common = _charger()


# --- Lecture des couleurs CSS ------------------------------------------------

@pytest.mark.parametrize(
    "css, attendu",
    [
        ("rgb(30, 64, 175)", (30, 64, 175, 1.0)),
        ("rgba(30, 64, 175, 0.5)", (30, 64, 175, 0.5)),
        ("rgb(30 64 175 / 50%)", (30, 64, 175, 0.5)),
        ("#1E40AF", (30, 64, 175, 1.0)),
        ("#1e40af", (30, 64, 175, 1.0)),
        ("#FFF", (255, 255, 255, 1.0)),
        ("transparent", (0, 0, 0, 0.0)),
        ("rgba(0, 0, 0, 0)", (0, 0, 0, 0.0)),
    ],
)
def test_lire_couleur(css, attendu):
    assert qa_common.lire_couleur(css) == pytest.approx(attendu)


@pytest.mark.parametrize("css", ["", None, "currentColor", "var(--primaire)", "pas une couleur"])
def test_lire_couleur_inconnue(css):
    assert qa_common.lire_couleur(css) is None


# --- Luminance et contraste (WCAG 2.x) --------------------------------------

def test_luminance_bornes():
    assert qa_common.luminance((255, 255, 255)) == pytest.approx(1.0, abs=1e-6)
    assert qa_common.luminance((0, 0, 0)) == pytest.approx(0.0, abs=1e-6)


def test_contraste_noir_sur_blanc():
    assert qa_common.contraste((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0, abs=0.01)


def test_contraste_symetrique():
    assert qa_common.contraste(PRIMAIRE, SOMBRE) == pytest.approx(qa_common.contraste(SOMBRE, PRIMAIRE))


def test_contraste_identique_vaut_un():
    assert qa_common.contraste(SOMBRE, SOMBRE) == pytest.approx(1.0)


def test_contraste_sombre_sur_clair_passe_le_seuil_corps():
    # Couple de lecture de la marque fictive : doit passer 4,5:1.
    assert qa_common.contraste(SOMBRE, CLAIR) > 4.5


def test_contraste_accent_sur_clair_echoue_en_corps():
    # L'accent ambre sur fond clair est un couple décoratif, pas un couple de lecture.
    assert qa_common.contraste(ACCENT, CLAIR) < 4.5


# --- Aplatissement d'une pile de fonds --------------------------------------

def test_aplatir_couleur_opaque_ignore_le_fond():
    assert qa_common.aplatir((10, 20, 30, 1.0), (255, 255, 255)) == (10, 20, 30)


def test_aplatir_demi_transparent():
    assert qa_common.aplatir((0, 0, 0, 0.5), (255, 255, 255)) == (128, 128, 128)


def test_aplatir_totalement_transparent_rend_le_fond():
    assert qa_common.aplatir((0, 0, 0, 0.0), CLAIR) == CLAIR


def test_resoudre_fond_prend_le_premier_opaque():
    pile = ["rgba(0, 0, 0, 0)", "rgba(255, 255, 255, 0.5)", "rgb(15, 23, 42)"]
    assert qa_common.resoudre_fond(pile) == (135, 139, 149)


def test_resoudre_fond_vide_suppose_le_blanc():
    assert qa_common.resoudre_fond([]) == (255, 255, 255)


def test_resoudre_fond_sans_opaque_suppose_le_blanc():
    assert qa_common.resoudre_fond(["rgba(0, 0, 0, 0)"]) == (255, 255, 255)


# --- Seuil de contraste exigé ------------------------------------------------

@pytest.mark.parametrize(
    "taille, gras, attendu",
    [
        (18.0, False, 4.5),
        (23.9, False, 4.5),
        (24.0, False, 3.0),
        (40.0, False, 3.0),
        (19.0, True, 3.0),   # gras ≥ 18,66px : texte large au sens WCAG
        (18.0, True, 4.5),
    ],
)
def test_seuil_contraste(taille, gras, attendu):
    assert qa_common.seuil_contraste(taille, gras=gras) == attendu


# --- Fond uni ou non ---------------------------------------------------------

@pytest.mark.parametrize(
    "css, attendu",
    [
        ("none", True),
        ("", True),
        (None, True),
        ("linear-gradient(90deg, rgb(30, 64, 175), rgb(245, 158, 11))", False),
        ('url("file:///photo.jpg")', False),
    ],
)
def test_fond_uni(css, attendu):
    assert qa_common.fond_uni(css) is attendu


# --- Police ------------------------------------------------------------------

@pytest.mark.parametrize(
    "css, attendu",
    [
        ('Inter, "Helvetica Neue", sans-serif', "Inter"),
        ('"Inter", sans-serif', "Inter"),
        ("  ui-monospace , monospace ", "ui-monospace"),
        ("", ""),
    ],
)
def test_premiere_famille(css, attendu):
    assert qa_common.premiere_famille(css) == attendu


def test_police_conforme_famille_de_marque():
    assert qa_common.police_conforme("Inter, sans-serif", "Inter") is True


def test_police_conforme_insensible_a_la_casse():
    assert qa_common.police_conforme('"inter", sans-serif', ["Inter"]) is True


def test_police_conforme_parmi_plusieurs_familles():
    assert qa_common.police_conforme("'Fictive Serif', serif", ["Inter", "Fictive Serif"]) is True


def test_police_non_conforme_helvetica():
    assert qa_common.police_conforme('"Helvetica Neue", Arial, sans-serif', ["Inter"]) is False


def test_police_mono_refusee_hors_code():
    assert qa_common.police_conforme("ui-monospace, monospace", ["Inter"]) is False


def test_police_mono_acceptee_pour_du_code():
    assert qa_common.police_conforme("ui-monospace, monospace", ["Inter"], mono_autorise=True) is True


def test_police_mono_acceptee_par_menlo():
    assert qa_common.police_conforme("Menlo, monospace", ["Inter"], mono_autorise=True) is True


def test_police_vide_jamais_conforme():
    assert qa_common.police_conforme("", ["Inter"]) is False


# --- Syntaxe à espaces de CSS Color 4 ---------------------------------------
# Le collecteur JS ne calcule pas l'opacité lui-même : c'est `lire_couleur` qui
# tranche, y compris sur la syntaxe `rgb(r g b / a)` que Chromium peut rendre.

@pytest.mark.parametrize(
    "css, alpha_attendu",
    [
        ("rgb(15 23 42 / 100%)", 1.0),
        ("rgb(15 23 42 / 1)", 1.0),
        ("rgb(15 23 42 / 0.35)", 0.35),
        ("rgb(15 23 42 / 0%)", 0.0),
        ("rgba(15 23 42 / 65%)", 0.65),
    ],
)
def test_alpha_syntaxe_a_espaces(css, alpha_attendu):
    assert qa_common.lire_couleur(css)[3] == pytest.approx(alpha_attendu)


def test_resoudre_fond_syntaxe_a_espaces():
    pile = ["rgb(255 255 255 / 50%)", "rgb(15 23 42 / 100%)"]
    assert qa_common.resoudre_fond(pile) == (135, 139, 149)


def test_alpha_hors_bornes_est_borne():
    assert qa_common.lire_couleur("rgba(0, 0, 0, 1.5)")[3] == 1.0
    assert qa_common.lire_couleur("rgba(0, 0, 0, -0.2)")[3] == 0.0


# --- tokens.json : familles de police ----------------------------------------

def test_familles_de_marque_premiere_famille_de_chaque_token():
    """Liste ou chaîne CSS ; les familles génériques ne sont jamais retenues."""
    assert qa_common.familles_de_marque(TOKENS_FICTIFS) == ["Inter", "Fictive Serif"]


def test_familles_de_marque_sans_token_de_police():
    assert qa_common.familles_de_marque({"color": {}}) == []


def test_lire_tokens_absent_leve(tmp_path):
    with pytest.raises(ValueError, match="introuvable"):
        qa_common.lire_tokens(tmp_path / "tokens.json")


def test_lire_tokens_illisible_leve(tmp_path):
    chemin = tmp_path / "tokens.json"
    chemin.write_text("{ pas du json", encoding="utf-8")
    with pytest.raises(ValueError, match="illisible"):
        qa_common.lire_tokens(chemin)


def test_lire_tokens_valide(tmp_path):
    chemin = tmp_path / "tokens.json"
    chemin.write_text(json.dumps(TOKENS_FICTIFS), encoding="utf-8")
    assert qa_common.lire_tokens(chemin)["color"]["primary"]["$value"] == "#1E40AF"


# --- tokens.json : palette, Lab et portée ------------------------------------

def test_charger_palette_releve_toutes_les_couleurs():
    palette = {t.nom: t for t in qa_common.charger_palette(TOKENS_FICTIFS)}
    assert set(palette) == {"primary", "accent", "dark", "light", "derived.primary-deep"}
    assert palette["primary"].hexa == "#1E40AF"
    assert palette["primary"].scope == ()


def test_portee_lue_quel_que_soit_l_espace_de_noms():
    palette = {t.nom: t for t in qa_common.charger_palette(TOKENS_FICTIFS)}
    derivee = palette["derived.primary-deep"]
    assert derivee.scope == ("06-graphic-design/presentations",)
    assert derivee.admis_dans("06-graphic-design/presentations/decks/deck.html")
    assert not derivee.admis_dans("06-graphic-design/outputs/visuel.png")
    assert not derivee.admis_dans("06-graphic-design/presentations-bis/deck.html")


def test_couleur_sans_portee_admise_partout():
    palette = {t.nom: t for t in qa_common.charger_palette(TOKENS_FICTIFS)}
    assert palette["accent"].admis_dans("n'importe/ou.png")


def test_palette_vide_leve():
    with pytest.raises(ValueError, match="aucune couleur"):
        qa_common.charger_palette({"color": {"primary": {"$value": "pas un hex"}}})


@pytest.mark.parametrize(
    "brut, attendu",
    [("#abc", "#AABBCC"), ("#1e40af", "#1E40AF"), ("#1E40AF80", "#1E40AF")],
)
def test_developper_hex(brut, attendu):
    assert qa_common.developper_hex(brut) == attendu


def test_developper_hex_refuse_l_illisible():
    with pytest.raises(ValueError):
        qa_common.developper_hex("#12")


def test_delta_e_nul_sur_la_meme_couleur():
    assert qa_common.delta_e76("#1E40AF", "#1e40af") == pytest.approx(0.0)


def test_delta_e_faible_sur_une_nuance_de_rendu():
    assert qa_common.delta_e76("#1E40AF", "#2042B0") < 4.0


def test_delta_e_fort_entre_deux_tokens():
    assert qa_common.delta_e76("#1E40AF", "#F59E0B") > 50.0
