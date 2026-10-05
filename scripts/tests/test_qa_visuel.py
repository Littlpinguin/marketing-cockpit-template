"""Tests de 06-graphic-design/scripts/qa-visuel.py.

Deux familles : les contrôles de couleur, qui ne demandent qu'une image PIL
fabriquée dans un dossier temporaire, et les contrôles de page, qui pilotent un
vrai Chromium et sont ignorés proprement si Playwright ou le navigateur manquent.

Aucune image n'est écrite dans le dépôt : tout vit dans `tmp_path`. La palette,
les polices et les règles du logo sont celles d'une marque fictive (« Acme », les
exemples de docs/placeholders.json), écrites dans un tokens.json temporaire :
jamais celles d'un client, jamais le `01-brand/tokens.json` du dépôt.
"""
from __future__ import annotations

import json
import random
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "06-graphic-design" / "scripts" / "qa-visuel.py"


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


CHROMIUM = pytest.mark.skipif(
    not _chromium_disponible(), reason="Playwright ou Chromium indisponible sur cette machine"
)

# Marque fictive. La nuance dérivée n'est admise que sous presentations/.
TOKENS_FICTIFS = {
    "color": {
        "primary": {"$value": "#1E40AF"},
        "accent": {"$value": "#F59E0B"},
        "dark": {"$value": "#0F172A"},
        "light": {"$value": "#F8FAFC"},
        "derived": {
            "primary-deep": {
                "$value": "#16307F",
                "$extensions": {"cockpit": {"scope": ["06-graphic-design/presentations"]}},
            },
        },
    },
    "font": {
        "primary": {"$value": ["Inter", "system-ui", "sans-serif"]},
        "mono": {"$value": ["ui-monospace", "Menlo", "monospace"]},
    },
    "logo": {
        "clear-space-ratio": {"$value": 1},
        "min-height-screen": {"$value": "24px"},
    },
}
TOKENS: Path | None = None


@pytest.fixture(autouse=True, scope="module")
def _tokens_fictifs(tmp_path_factory):
    global TOKENS
    TOKENS = tmp_path_factory.mktemp("marque") / "tokens.json"
    TOKENS.write_text(json.dumps(TOKENS_FICTIFS, ensure_ascii=False), encoding="utf-8")
    yield


def ecrire_tokens(dossier: Path, **logo) -> Path:
    """Variante des tokens fictifs, avec d'autres règles de logo."""
    tokens = json.loads(json.dumps(TOKENS_FICTIFS))
    for cle, valeur in logo.items():
        tokens["logo"][cle.replace("_", "-")] = {"$value": valeur}
    chemin = dossier / "tokens-variante.json"
    chemin.write_text(json.dumps(tokens, ensure_ascii=False), encoding="utf-8")
    return chemin


# --------------------------------------------------------------------------
# Utilitaires
# --------------------------------------------------------------------------

def lancer(cible: Path, *options: str) -> subprocess.CompletedProcess:
    defaut = () if "--tokens" in options else ("--tokens", str(TOKENS))
    return subprocess.run(
        [sys.executable, str(QA), str(cible), *defaut, *options],
        capture_output=True, text=True, cwd=str(REPO), timeout=180,
    )


def rapport(cible: Path, *options: str) -> tuple[subprocess.CompletedProcess, dict]:
    resultat = lancer(cible, "--format", "json", *options)
    assert resultat.stdout, f"aucune sortie JSON : {resultat.stderr}"
    return resultat, json.loads(resultat.stdout)


def types(donnees: dict, niveau: str = "erreur") -> list[str]:
    return [c["type"] for c in donnees["constats"] if c["niveau"] == niveau]


def ecrire_png(chemin: Path, bandes: list[tuple[str, float]], taille=(200, 200)) -> Path:
    """Écrit un PNG fait de bandes horizontales : (couleur, part de la hauteur)."""
    image = Image.new("RGB", taille, bandes[0][0])
    dessin = ImageDraw.Draw(image)
    haut = 0.0
    for couleur, part in bandes:
        bas = haut + part * taille[1]
        dessin.rectangle([0, int(haut), taille[0] - 1, int(bas) - 1], fill=couleur)
        haut = bas
    image.save(chemin)
    return chemin


PAGE = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
  body {{ margin: 0; width: 1080px; height: 1350px; background: #F8FAFC;
          font-family: Inter, sans-serif; color: #0F172A; }}
  .corps {{ position: absolute; left: 80px; top: 200px; font-size: 40px; }}
  {styles}
</style></head><body>{corps}</body></html>"""


def ecrire_page(dossier: Path, corps: str, styles: str = "", nom: str = "page.html") -> Path:
    chemin = dossier / nom
    chemin.write_text(PAGE.format(corps=corps, styles=styles), encoding="utf-8")
    return chemin


# --------------------------------------------------------------------------
# Couleurs (sans navigateur)
# --------------------------------------------------------------------------

def test_image_aux_couleurs_de_la_palette(tmp_path):
    image = ecrire_png(tmp_path / "propre.png", [
        ("#F8FAFC", 0.5), ("#1E40AF", 0.2), ("#F59E0B", 0.2), ("#0F172A", 0.1),
    ])
    resultat, donnees = rapport(image)
    assert resultat.returncode == 0, resultat.stdout
    assert donnees["couleurs"]["hors_palette"] == []


def test_couleur_hors_palette_au_dessus_du_seuil(tmp_path):
    image = ecrire_png(tmp_path / "rouge.png", [("#F8FAFC", 0.8), ("#FF0000", 0.2)])
    resultat, donnees = rapport(image)
    assert resultat.returncode == 1
    assert "couleur" in types(donnees)
    hors = donnees["couleurs"]["hors_palette"]
    assert hors and hors[0]["hex"] == "#FF0000"
    assert 19.0 <= hors[0]["part"] <= 21.0


def test_couleur_hors_palette_sous_le_seuil_en_avertissement(tmp_path):
    image = ecrire_png(tmp_path / "trace.png", [("#F8FAFC", 0.98), ("#FF0000", 0.02)])
    resultat, donnees = rapport(image)
    assert resultat.returncode == 0
    assert "couleur" not in types(donnees)
    assert "couleur" in types(donnees, "avertissement")


def test_tolerance_de_rendu_sur_une_nuance_voisine(tmp_path):
    """Un primaire décalé d'un cheveu par le rendu reste dans la palette (ΔE76 ≤ 4)."""
    image = ecrire_png(tmp_path / "voisin.png", [("#F8FAFC", 0.5), ("#2042B0", 0.5)])
    resultat, donnees = rapport(image)
    assert resultat.returncode == 0, donnees["couleurs"]["hors_palette"]


def test_zone_photo_declaree_exclue_du_calcul(tmp_path):
    image = ecrire_png(tmp_path / "photo.png", [("#F8FAFC", 0.8), ("#FF0000", 0.2)])
    resultat, donnees = rapport(image, "--allow-photo", "0,160,200,40")
    assert resultat.returncode == 0, donnees["couleurs"]["hors_palette"]
    assert donnees["couleurs"]["pixels_exclus"] > 0


def test_couleur_a_portee_limitee_hors_de_son_dossier(tmp_path):
    """`color.derived.primary-deep` n'est admise que sous 06-graphic-design/presentations."""
    image = ecrire_png(tmp_path / "derive.png", [("#F8FAFC", 0.5), ("#16307F", 0.5)])
    resultat, donnees = rapport(image)
    assert resultat.returncode == 1
    assert donnees["couleurs"]["hors_palette"][0]["hex"] == "#16307F"

    resultat, donnees = rapport(
        image, "--emplacement", "06-graphic-design/presentations/decks/visuel.png"
    )
    assert resultat.returncode == 0, donnees["couleurs"]["hors_palette"]


def test_zone_photo_exclue_avant_la_quantification(tmp_path):
    """Les pixels exclus ne consomment pas de niveaux et ne déplacent pas les centroïdes.

    La photo porte des bleus nuit voisins du sombre : quantifiés avec le reste,
    ils entraînent le centroïde du sombre hors palette et font échouer des
    pixels qui valent pourtant exactement le token.
    """
    image = Image.new("RGB", (200, 200), "#F8FAFC")
    dessin = ImageDraw.Draw(image)
    for rang, couleur in enumerate(("#F8FAFC", "#1E40AF", "#F59E0B", "#0F172A")):
        dessin.rectangle([0, rang * 12, 199, rang * 12 + 11], fill=couleur)
    alea = random.Random(3)
    for y in range(50, 200):
        for x in range(0, 200):
            if x < 120:
                canaux = (24 + alea.randrange(-6, 7), 34 + alea.randrange(-6, 7),
                          80 + alea.randrange(-30, 31))
            else:
                canaux = (230 + alea.randrange(-12, 13), 220 + alea.randrange(-12, 13),
                          190 + alea.randrange(-12, 13))
            image.putpixel((x, y), tuple(max(0, min(255, c)) for c in canaux))
    chemin = tmp_path / "photo-bruitee.png"
    image.save(chemin)

    resultat, donnees = rapport(chemin, "--allow-photo", "0,50,200,150")
    assert resultat.returncode == 0, donnees["couleurs"]["hors_palette"]
    assert donnees["couleurs"]["hors_palette"] == []
    assert donnees["couleurs"]["pixels_exclus"] == 200 * 150
    mesurees = {entree["hex"] for entree in donnees["couleurs"]["dominantes"]}
    assert {"#F8FAFC", "#1E40AF", "#F59E0B", "#0F172A"} <= mesurees


def test_image_indexee_sans_transparence(tmp_path):
    """Un PNG en palette sans transparence ne déclenche pas l'avertissement d'alpha."""
    ecrire_png(tmp_path / "plate.png", [("#F8FAFC", 0.5), ("#1E40AF", 0.5)])
    indexee = Image.open(tmp_path / "plate.png").convert("P", palette=Image.Palette.ADAPTIVE)
    chemin = tmp_path / "indexee.png"
    indexee.save(chemin)
    _, donnees = rapport(chemin)
    assert "transparence" not in types(donnees, "avertissement")


def test_fichier_absent_sort_en_deux(tmp_path):
    resultat = lancer(tmp_path / "fantome.png")
    assert resultat.returncode == 2
    assert "introuvable" in resultat.stderr


@pytest.mark.parametrize("zone", ["0,0,0,0", "0,0,10", "5000,5000,10,10"])
def test_zone_photo_invalide_sort_en_deux(tmp_path, zone):
    image = ecrire_png(tmp_path / "propre.png", [("#F8FAFC", 1.0)])
    resultat = lancer(image, "--allow-photo", zone)
    assert resultat.returncode == 2, resultat.stdout
    assert "zone" in resultat.stderr.lower()


@pytest.mark.parametrize("option", [("--delta-e", "-1"), ("--part-max", "-5")])
def test_seuils_negatifs_sortent_en_deux(tmp_path, option):
    image = ecrire_png(tmp_path / "propre.png", [("#F8FAFC", 1.0)])
    resultat = lancer(image, *option)
    assert resultat.returncode == 2
    assert resultat.stderr.strip()


# --------------------------------------------------------------------------
# Page rendue (Chromium)
# --------------------------------------------------------------------------

@CHROMIUM
def test_plancher_typographique_du_carrousel(tmp_path):
    page = ecrire_page(tmp_path, '<p class="corps" style="font-size:12px">Trop petit</p>')
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "plancher-typo" in types(donnees)
    assert donnees["summary"]["min_font"] == 28


@CHROMIUM
def test_plancher_abaisse_par_option(tmp_path):
    page = ecrire_page(tmp_path, '<p class="corps" style="font-size:12px">Trop petit</p>')
    resultat, donnees = rapport(page, "--min-font", "10")
    assert "plancher-typo" not in types(donnees)


@CHROMIUM
def test_plancher_du_chrome_du_carrousel(tmp_path):
    """Le pied de slide, le folio et la mention de source ont leur propre plancher."""
    page = ecrire_page(tmp_path, """
      <p class="foot" style="position:absolute;left:80px;top:1200px;font-size:22px">Pied</p>
      <p data-brand-chrome style="position:absolute;left:80px;top:1250px;font-size:22px">Source</p>""")
    resultat, donnees = rapport(page)
    assert resultat.returncode == 0, donnees["constats"]
    assert donnees["summary"]["min_font_chrome"] == 22


@CHROMIUM
def test_le_corps_du_message_garde_le_plancher_du_contenu(tmp_path):
    page = ecrire_page(
        tmp_path, '<p style="position:absolute;left:80px;top:400px;font-size:22px">Corps</p>'
    )
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "plancher-typo" in types(donnees)


@CHROMIUM
def test_chrome_sous_son_propre_plancher(tmp_path):
    page = ecrire_page(
        tmp_path,
        '<p class="foot" style="position:absolute;left:80px;top:1200px;font-size:12px">Pied</p>',
    )
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "plancher-typo" in types(donnees)


@CHROMIUM
def test_zone_de_protection_suit_le_ratio_des_tokens(tmp_path):
    """Le multiple de `logo.clear-space-ratio` pilote la détection, pas seulement le message."""
    large = ecrire_tokens(tmp_path, clear_space_ratio=3)

    page = ecrire_page(tmp_path, """
      <div data-brand-logo style="position:absolute;left:200px;top:200px;
           width:200px;height:60px;background:#0F172A"></div>
      <p style="position:absolute;left:450px;top:210px;font-size:40px">À 50 px</p>""")

    _, serre = rapport(page)
    assert "zone-protection" not in types(serre)

    _, large_zone = rapport(page, "--tokens", str(large))
    assert "zone-protection" in types(large_zone)


@CHROMIUM
def test_police_hors_charte(tmp_path):
    page = ecrire_page(
        tmp_path, '<p class="corps" style="font-family:Helvetica">Hors charte</p>'
    )
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "police" in types(donnees)


@CHROMIUM
def test_monospace_admise(tmp_path):
    page = ecrire_page(tmp_path, '<p class="corps" style="font-family:Menlo">Code</p>')
    _, donnees = rapport(page)
    assert "police" not in types(donnees)


@CHROMIUM
def test_contraste_insuffisant(tmp_path):
    page = ecrire_page(tmp_path, '<p class="corps" style="color:#E2E8F0">Trop pâle</p>')
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "contraste" in types(donnees)


@CHROMIUM
def test_logo_isole_ne_leve_rien(tmp_path):
    page = ecrire_page(tmp_path, """
      <div data-brand-logo style="position:absolute;left:80px;top:80px;
           width:200px;height:60px;background:#0F172A"></div>
      <p class="corps" style="top:600px">Un message</p>""")
    _, donnees = rapport(page)
    assert "zone-protection" not in types(donnees)
    assert "fond-logo" not in types(donnees)


@CHROMIUM
def test_element_dans_la_zone_de_protection_du_logo(tmp_path):
    """La zone de protection vaut la hauteur du N, soit la moitié du logo."""
    page = ecrire_page(tmp_path, """
      <div data-brand-logo style="position:absolute;left:200px;top:200px;
           width:200px;height:60px;background:#0F172A"></div>
      <p style="position:absolute;left:420px;top:220px;font-size:40px">Trop près</p>""")
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "zone-protection" in types(donnees)


@CHROMIUM
def test_forme_peinte_derriere_le_logo(tmp_path):
    page = ecrire_page(tmp_path, """
      <div style="position:absolute;left:180px;top:180px;width:300px;height:160px;
           background:#F59E0B;border-radius:50%"></div>
      <div data-brand-logo style="position:absolute;left:240px;top:220px;
           width:180px;height:60px"></div>""")
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "fond-logo" in types(donnees)


@CHROMIUM
def test_fond_de_page_degrade_n_est_pas_un_fond_de_logo(tmp_path):
    """Le sol de la composition n'est pas un aplat posé derrière le logo."""
    page = ecrire_page(
        tmp_path,
        """<div data-brand-logo style="position:absolute;left:80px;top:80px;
             width:200px;height:60px"></div>""",
        styles="body { background: radial-gradient(circle at 20% 10%,"
               " rgba(30,64,175,.06), transparent 70%), #F8FAFC; }",
    )
    _, donnees = rapport(page)
    assert "fond-logo" not in types(donnees)


@CHROMIUM
def test_pastille_locale_derriere_le_logo(tmp_path):
    """Un conteneur à la taille du logo, lui, est bien un aplat posé derrière."""
    page = ecrire_page(tmp_path, """
      <div style="position:absolute;left:200px;top:200px;width:240px;height:90px;
           background:#0F172A;border-radius:45px">
        <div data-brand-logo style="position:absolute;left:20px;top:15px;
             width:200px;height:60px"></div>
      </div>""")
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "fond-logo" in types(donnees)


@CHROMIUM
def test_calque_vectoriel_plein_cadre_sans_trace_sous_le_logo(tmp_path):
    """Un `<svg>` pleine page est un conteneur : l'encre est dans ses tracés."""
    page = ecrire_page(tmp_path, """
      <svg style="position:absolute;left:0;top:0;width:1080px;height:1350px">
        <circle cx="540" cy="1000" r="120" fill="#1E40AF"></circle>
      </svg>
      <div data-brand-logo style="position:absolute;left:80px;top:80px;
           width:200px;height:60px"></div>""")
    _, donnees = rapport(page)
    assert "fond-logo" not in types(donnees)


@CHROMIUM
def test_trace_vectoriel_sous_le_logo(tmp_path):
    page = ecrire_page(tmp_path, """
      <svg style="position:absolute;left:0;top:0;width:1080px;height:1350px">
        <circle cx="180" cy="110" r="120" fill="#1E40AF"></circle>
      </svg>
      <div data-brand-logo style="position:absolute;left:80px;top:80px;
           width:200px;height:60px"></div>""")
    resultat, donnees = rapport(page)
    assert resultat.returncode == 1
    assert "fond-logo" in types(donnees)


@CHROMIUM
def test_selecteur_de_logo_supplementaire(tmp_path):
    """Un gabarit qui nomme son logo autrement : `--logo` le rattache au contrôle."""
    page = ecrire_page(tmp_path, """
      <div class="logo-maison" style="position:absolute;left:200px;top:200px;
           width:200px;height:60px;background:#0F172A"></div>
      <p style="position:absolute;left:420px;top:220px;font-size:40px">Trop près</p>""")
    _, sans = rapport(page)
    assert "zone-protection" not in types(sans)
    _, avec = rapport(page, "--logo", ".logo-maison")
    assert "zone-protection" in types(avec)


@CHROMIUM
def test_zone_photo_par_selecteur(tmp_path):
    page = ecrire_page(tmp_path, """
      <div class="photo" style="position:absolute;left:0;top:0;
           width:1080px;height:400px;background:#FF0000"></div>""")
    resultat, _ = rapport(page)
    assert resultat.returncode == 1
    resultat, donnees = rapport(page, "--allow-photo", ".photo")
    assert resultat.returncode == 0, donnees["couleurs"]["hors_palette"]


# --------------------------------------------------------------------------
# Réglages propres à chaque marque : aucun n'est écrit en dur dans le script
# --------------------------------------------------------------------------

def test_tokens_absents_sortent_en_deux(tmp_path):
    image = ecrire_png(tmp_path / "propre.png", [("#F8FAFC", 1.0)])
    resultat = lancer(image, "--tokens", str(tmp_path / "absent.json"))
    assert resultat.returncode == 2
    assert "introuvable" in resultat.stderr


@CHROMIUM
def test_aplat_derriere_le_logo_admis_par_la_charte(tmp_path):
    """`--logo-sur-aplat` : une marque qui admet une pastille sous son logo."""
    page = ecrire_page(tmp_path, """
      <div style="position:absolute;left:200px;top:200px;width:240px;height:90px;
           background:#0F172A;border-radius:45px">
        <div data-brand-logo style="position:absolute;left:20px;top:15px;
             width:200px;height:60px"></div>
      </div>""")
    resultat, donnees = rapport(page, "--logo-sur-aplat")
    assert "fond-logo" not in types(donnees)
    assert "fond-logo" in types(donnees, "avertissement")
    assert resultat.returncode == 0, donnees["constats"]


@CHROMIUM
def test_unite_de_protection_lue_dans_les_tokens(tmp_path):
    """`logo.clear-space-unit` : l'unité de protection en fraction de la hauteur du logo."""
    page = ecrire_page(tmp_path, """
      <div data-brand-logo style="position:absolute;left:200px;top:200px;
           width:200px;height:60px;background:#0F172A"></div>
      <p style="position:absolute;left:450px;top:210px;font-size:40px">À 50 px</p>""")
    _, defaut = rapport(page)
    assert "zone-protection" not in types(defaut)

    unite_large = ecrire_tokens(tmp_path, clear_space_unit=1)
    _, large = rapport(page, "--tokens", str(unite_large))
    assert "zone-protection" in types(large)


@CHROMIUM
def test_police_passee_en_option_remplace_les_tokens(tmp_path):
    page = ecrire_page(
        tmp_path, '<p class="corps" style="font-family:\'Fictive Serif\'">Autre famille</p>'
    )
    _, sans = rapport(page)
    assert "police" in types(sans)
    _, avec = rapport(page, "--police", "Fictive Serif", "--police", "Inter")
    assert "police" not in types(avec)
    assert avec["summary"]["familles"] == ["Fictive Serif", "Inter"]
