"""Tests de scripts/relativize-paths.py.

Le script réécrit des fichiers du dépôt : ces tests travaillent tous dans un
dossier temporaire, avec l'option --root, et vérifient qu'en dry-run rien n'est
jamais écrit.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "relativize-paths.py"


def _module():
    spec = importlib.util.spec_from_file_location("relativize_paths", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rp = _module()


def lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )


# --------------------------- réécriture de base ---------------------------

def test_src_html_devient_relatif(tmp_path):
    racine = tmp_path
    (racine / "01-brand" / "assets").mkdir(parents=True)
    (racine / "01-brand" / "assets" / "logo.svg").write_text("x")
    page = racine / "06-graphic-design" / "productions" / "page.html"
    page.parent.mkdir(parents=True)
    page.write_text(
        f'<img src="file://{racine}/01-brand/assets/logo.svg" alt="">',
        encoding="utf-8")

    n = rp.relativiser_fichier(page, racine, ecrire=True)

    assert n == 1
    assert page.read_text(encoding="utf-8") == (
        '<img src="../../01-brand/assets/logo.svg" alt="">')


def test_url_css_sans_guillemets(tmp_path):
    racine = tmp_path
    (racine / "lib").mkdir()
    (racine / "lib" / "grain.png").write_text("x")
    feuille = racine / "theme" / "style.css"
    feuille.parent.mkdir()
    feuille.write_text(
        f"body{{background:url(file://{racine}/lib/grain.png) repeat}}",
        encoding="utf-8")

    assert rp.relativiser_fichier(feuille, racine, ecrire=True) == 1
    assert feuille.read_text(encoding="utf-8") == (
        "body{background:url(../lib/grain.png) repeat}")


def test_href_et_srcset_multiples(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    for nom in ("un.png", "deux.png", "style.css"):
        (racine / "a" / nom).write_text("x")
    page = racine / "page.html"
    page.write_text(
        f'<link rel="stylesheet" href="file://{racine}/a/style.css">'
        f'<img srcset="file://{racine}/a/un.png 1x, file://{racine}/a/deux.png 2x">',
        encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 3
    contenu = page.read_text(encoding="utf-8")
    assert 'href="a/style.css"' in contenu
    assert 'srcset="a/un.png 1x, a/deux.png 2x"' in contenu


def test_remontee_depuis_un_sous_dossier_profond(tmp_path):
    racine = tmp_path
    (racine / "01-brand").mkdir()
    (racine / "01-brand" / "x.svg").write_text("x")
    page = racine / "a" / "b" / "c" / "page.html"
    page.parent.mkdir(parents=True)
    page.write_text(f'<img src="file://{racine}/01-brand/x.svg">', encoding="utf-8")

    rp.relativiser_fichier(page, racine, ecrire=True)
    assert 'src="../../../01-brand/x.svg"' in page.read_text(encoding="utf-8")


# ------------------------------- encodage --------------------------------

def test_chemin_encode_est_decode_puis_reencode(tmp_path):
    racine = tmp_path
    (racine / "fonts").mkdir()
    (racine / "fonts" / "Ma Police.ttf").write_text("x")
    feuille = racine / "deep" / "style.css"
    feuille.parent.mkdir()
    feuille.write_text(
        f"@font-face{{src:url('file://{racine}/fonts/Ma%20Police.ttf')}}",
        encoding="utf-8")

    assert rp.relativiser_fichier(feuille, racine, ecrire=True) == 1
    assert "url('../fonts/Ma%20Police.ttf')" in feuille.read_text(encoding="utf-8")


def test_fragment_et_query_traversent_intacts(tmp_path):
    """Un `#` ou un `?` de l'URL vise le fichier, pas son nom : jamais encodé."""
    racine = tmp_path
    (racine / "assets").mkdir()
    (racine / "assets" / "sprite.svg").write_text("x")
    (racine / "assets" / "grille.svg").write_text("x")
    page = racine / "page.html"
    page.write_text(
        f'<use href="file://{racine}/assets/sprite.svg#icone-logo"/>'
        f'<img src="file://{racine}/assets/grille.svg?v=3">',
        encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 2

    ecrit = page.read_text(encoding="utf-8")
    assert 'href="assets/sprite.svg#icone-logo"' in ecrit
    assert 'src="assets/grille.svg?v=3"' in ecrit
    assert "%23" not in ecrit and "%3F" not in ecrit


def test_diese_encode_dans_le_nom_de_fichier_reste_encode(tmp_path):
    """Un `%23` vient d'un vrai `#` dans le nom : il se ré-encode, lui."""
    racine = tmp_path
    (racine / "assets").mkdir()
    (racine / "assets" / "teinte #3.svg").write_text("x")
    page = racine / "page.html"
    page.write_text(
        f'<img src="file://{racine}/assets/teinte%20%233.svg">', encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 1
    assert 'src="assets/teinte%20%233.svg"' in page.read_text(encoding="utf-8")


# ------------------------------ non-touches ------------------------------

# ------------------------- chemins absolus nus --------------------------

def test_href_absolu_nu_devient_relatif(tmp_path):
    """Le cas d'une maquette qui charge sa feuille sans file:// devant."""
    racine = tmp_path
    (racine / "06-graphic-design" / "lib").mkdir(parents=True)
    (racine / "06-graphic-design" / "lib" / "compose.css").write_text("x")
    page = racine / "06-graphic-design" / "outputs" / "maquette" / "apercu.html"
    page.parent.mkdir(parents=True)
    page.write_text(
        f'<link rel="stylesheet" href="{racine}/06-graphic-design/lib/compose.css">',
        encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 1
    assert page.read_text(encoding="utf-8") == (
        '<link rel="stylesheet" href="../../lib/compose.css">')


def test_src_et_url_css_absolus_nus(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    (racine / "a" / "logo.svg").write_text("x")
    (racine / "a" / "grain.png").write_text("x")
    page = racine / "page.html"
    page.write_text(
        f'<img src="{racine}/a/logo.svg">'
        f'<style>body{{background:url({racine}/a/grain.png)}}</style>',
        encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 2
    contenu = page.read_text(encoding="utf-8")
    assert 'src="a/logo.svg"' in contenu
    assert "url(a/grain.png)" in contenu


def test_srcset_absolu_nu_sur_tous_les_candidats(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    for nom in ("un.png", "deux.png"):
        (racine / "a" / nom).write_text("x")
    page = racine / "page.html"
    page.write_text(
        f'<img srcset="{racine}/a/un.png 1x, {racine}/a/deux.png 2x">',
        encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 2
    assert 'srcset="a/un.png 1x, a/deux.png 2x"' in page.read_text(encoding="utf-8")


def test_chemin_absolu_hors_contexte_durl_est_laisse_intact(tmp_path):
    """Un chemin cité dans un commentaire ou dans de la prose n'est pas une URL."""
    racine = tmp_path
    (racine / "a").mkdir()
    (racine / "a" / "logo.svg").write_text("x")
    page = racine / "page.html"
    avant = (f'<!-- source : {racine}/a/logo.svg -->'
             f'<p>Le fichier vit dans {racine}/a/logo.svg</p>')
    page.write_text(avant, encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 0
    assert page.read_text(encoding="utf-8") == avant


def test_src_nu_vers_une_autre_racine_est_laisse_intact(tmp_path):
    racine = tmp_path / "projet"
    racine.mkdir()
    voisin = tmp_path / "projet-site"
    voisin.mkdir()
    page = racine / "page.html"
    avant = f'<img src="{voisin}/assets/bg.svg">'
    page.write_text(avant, encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 0
    assert page.read_text(encoding="utf-8") == avant


def test_autre_racine_absolue_est_laissee_intacte(tmp_path):
    racine = tmp_path / "projet"
    racine.mkdir()
    voisin = tmp_path / "projet-site"
    voisin.mkdir()
    page = racine / "page.html"
    avant = f'<img src="file://{voisin}/assets/bg.svg">'
    page.write_text(avant, encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 0
    assert page.read_text(encoding="utf-8") == avant


def test_fichier_sans_occurrence_nest_pas_reecrit(tmp_path):
    racine = tmp_path
    page = racine / "page.html"
    page.write_text("<p>rien</p>", encoding="utf-8")
    avant = page.stat().st_mtime_ns

    assert rp.relativiser_fichier(page, racine, ecrire=True) == 0
    assert page.stat().st_mtime_ns == avant


# -------------------------------- dry-run --------------------------------

def test_dry_run_necrit_rien(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    (racine / "a" / "x.svg").write_text("x")
    page = racine / "page.html"
    avant = f'<img src="file://{racine}/a/x.svg">'
    page.write_text(avant, encoding="utf-8")

    assert rp.relativiser_fichier(page, racine, ecrire=False) == 1
    assert page.read_text(encoding="utf-8") == avant


def test_cli_dry_run_liste_le_fichier_et_le_compte(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    (racine / "a" / "x.svg").write_text("x")
    page = racine / "page.html"
    avant = f'<img src="file://{racine}/a/x.svg">'
    page.write_text(avant, encoding="utf-8")

    r = lancer("--dry-run", "--root", str(racine), str(page))

    assert r.returncode == 0, r.stderr
    assert "page.html" in r.stdout
    assert "1" in r.stdout
    assert "a/x.svg" in r.stdout          # exemple de remplacement
    assert page.read_text(encoding="utf-8") == avant


def test_cli_reecrit_pour_de_vrai(tmp_path):
    racine = tmp_path
    (racine / "a").mkdir()
    (racine / "a" / "x.svg").write_text("x")
    page = racine / "page.html"
    page.write_text(f'<img src="file://{racine}/a/x.svg">', encoding="utf-8")

    r = lancer("--root", str(racine), str(page))

    assert r.returncode == 0, r.stderr
    assert 'src="a/x.svg"' in page.read_text(encoding="utf-8")


# ------------------------------- erreurs ---------------------------------

def test_fichier_absent_sort_en_erreur(tmp_path):
    r = lancer("--root", str(tmp_path), str(tmp_path / "absent.html"))
    assert r.returncode != 0
    assert "absent.html" in r.stderr


def test_extension_refusee(tmp_path):
    fichier = tmp_path / "note.md"
    fichier.write_text("x", encoding="utf-8")
    r = lancer("--root", str(tmp_path), str(fichier))
    assert r.returncode != 0
    assert "note.md" in r.stderr


def test_sans_argument_sort_en_erreur():
    r = lancer()
    assert r.returncode != 0


def test_help_sort_en_zero():
    r = lancer("--help")
    assert r.returncode == 0
    assert "--dry-run" in r.stdout
