"""Tests de 06-graphic-design/scripts/promote-asset.py (champs de droits de la fiche).

Chaque test travaille sur une racine jetable : un faux `01-brand/assets/` et un
catalogue `index.md` fictif. Le dépôt n'est jamais touché.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "06-graphic-design" / "scripts" / "promote-asset.py"
ASSETS_DEPOT = REPO / "01-brand" / "assets"

# Catalogue fictif : une section par catégorie, dont une section groupée.
INDEX_FICTIF = """---
title: Catalogue des assets (fictif)
categories: [logos, icons, illustrations, patterns, photos, banners, archive, docs, sources]
---

# Catalogue des assets

## logos/

## icons/

## illustrations/

## patterns/

## photos/

## banners/

## docs/ · sources/

## archive/
"""


def _load_module():
    """Charge promote-asset.py par chemin : son nom contient un tiret."""
    spec = importlib.util.spec_from_file_location("promote_asset", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


promote_asset = _load_module()


def make_root(tmp_path: Path) -> Path:
    """Racine jetable : catalogue fictif, dossiers d'assets vides."""
    root = tmp_path / "repo"
    index = root / "01-brand" / "assets" / "index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(INDEX_FICTIF, encoding="utf-8")
    return root


def make_source(tmp_path: Path, nom: str = "sortie.svg") -> Path:
    """Un faux asset source : un SVG minimal, mesurable sans PIL."""
    src = tmp_path / "staging" / nom
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 60"></svg>',
                   encoding="utf-8")
    return src


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        capture_output=True, text=True,
    )


DROITS = ("--source", "généré (modèle d'image)",
          "--droits", "création interne, usage libre",
          "--auteur", "équipe marketing")


def promeut(root: Path, src: Path, dest: str, *extra: str) -> subprocess.CompletedProcess:
    return run(root, str(src), "--dest", dest, "--role", "test", *DROITS, *extra)


def lire_index(root: Path) -> str:
    return (root / "01-brand" / "assets" / "index.md").read_text(encoding="utf-8")


# --- Champs obligatoires -----------------------------------------------------

def test_refus_si_source_manquante(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    res = run(root, str(src), "--dest", "logos/clients/logo_client_test.svg",
              "--droits", "à confirmer", "--auteur", "équipe marketing")
    assert res.returncode != 0
    assert "--source" in res.stderr
    assert src.exists(), "la source ne doit pas avoir été déplacée"


def test_refus_liste_tous_les_champs_manquants(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    res = run(root, str(src), "--dest", "logos/clients/logo_client_test.svg")
    assert res.returncode != 0
    for option in ("--source", "--droits", "--auteur"):
        assert option in res.stderr, f"{option} absent du message : {res.stderr}"


def test_droits_a_confirmer_est_une_valeur_acceptee(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    res = run(root, str(src), "--dest", "logos/clients/logo_client_test.svg",
              "--role", "test", "--source", "fourni par le client",
              "--droits", "à confirmer", "--auteur", "inconnu")
    assert res.returncode == 0, res.stderr
    assert "- droits: à confirmer" in lire_index(root)


# --- Contenu de la fiche -----------------------------------------------------

def test_fiche_porte_les_trois_champs_de_droits(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    texte = lire_index(root)
    assert "- source: généré (modèle d'image)" in texte
    assert "- droits: création interne, usage libre" in texte
    assert "- auteur: équipe marketing" in texte


def test_genere_par_ia_vaut_non_par_defaut(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    assert "- généré-par-ia: non" in lire_index(root)


def test_genere_par_ia_oui(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg", "--ia", "oui").returncode == 0
    assert "- généré-par-ia: oui" in lire_index(root)


def test_ia_refuse_une_valeur_hors_oui_non(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg", "--ia", "peut-être").returncode != 0


def test_aucun_tiret_long_dans_la_fiche(tmp_path):
    """La fiche par défaut ne doit contenir ni cadratin ni demi-cadratin."""
    root, src = make_root(tmp_path), make_source(tmp_path)
    avant = lire_index(root)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    ajout = lire_index(root).replace(avant, "")
    assert "—" not in ajout and "–" not in ajout, ajout
    assert "- variantes: aucune" in ajout
    assert "- palette: aucune" in ajout


def test_fiche_inseree_dans_la_bonne_section(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    texte = lire_index(root)
    debut_logos = texte.index("## logos/")
    section_suivante = texte.index("## icons/")
    position = texte.index("### logo_client_test")
    assert debut_logos < position < section_suivante


def test_fichier_range_a_la_destination(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    assert (root / "01-brand" / "assets" / "logos" / "clients" / "logo_client_test.svg").exists()
    assert not src.exists(), "sans --copy, la source est déplacée"


def test_copie_conserve_la_source(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg", "--copy").returncode == 0
    assert src.exists()


def test_refus_ecrasement(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    autre = make_source(tmp_path, "autre.svg")
    res = promeut(root, autre, "logos/clients/logo_client_test.svg")
    assert res.returncode != 0
    assert "existante" in res.stderr


def test_refus_nom_non_conforme(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    res = promeut(root, src, "logos/clients/Logo Client Test.svg")
    assert res.returncode != 0
    assert "conforme" in res.stderr


def test_refus_categorie_inconnue(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    res = promeut(root, src, "affiches/logo_client_test.svg")
    assert res.returncode != 0
    assert "affiches" in res.stderr


def test_refus_source_introuvable(tmp_path):
    root = make_root(tmp_path)
    res = promeut(root, tmp_path / "fantome.svg", "logos/clients/logo_client_test.svg")
    assert res.returncode != 0
    assert "source introuvable" in res.stderr


def test_categories_docs_et_sources_acceptees(tmp_path):
    """Le frontmatter du catalogue déclare docs et sources : le script doit les accepter."""
    root = make_root(tmp_path)
    for categorie in ("docs", "sources"):
        src = make_source(tmp_path, f"{categorie}.svg")
        res = promeut(root, src, f"{categorie}/{categorie}_test-droits.svg")
        assert res.returncode == 0, res.stderr
        assert (root / "01-brand" / "assets" / categorie / f"{categorie}_test-droits.svg").exists()


# --- Fiche de génération (sidecar) -------------------------------------------

def make_png(tmp_path: Path, nom: str = "sortie.png") -> Path:
    """Un vrai PNG de staging, pour les cas de provenance."""
    from PIL import Image

    src = tmp_path / "staging" / nom
    src.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (8, 8), (30, 64, 175)).save(src, format="PNG")
    return src


def pose_sidecar(src: Path, prompt: str = "Une scène de marque fictive, fond clair") -> Path:
    fiche = Path(str(src) + ".gen.json")
    fiche.write_text(json.dumps({
        "model": "gemini-3-pro-image-preview",
        "prompt": prompt,
        "prompt_file": None,
        "input_images": [],
        "temperature": 0.4,
        "aspect_ratio": "1:1",
        "image_size": "2K",
        "timestamp": "2026-09-13T10:00:00+02:00",
        "script": "generation-exemple.py",
        "script_version": "1.0",
        "sha256": "0" * 64,
    }, ensure_ascii=False), encoding="utf-8")
    return fiche


DEST_PNG = "illustrations/scenes/illustrations_scene_test-provenance.png"


def test_sidecar_met_genere_par_ia_a_oui(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG).returncode == 0
    assert "- généré-par-ia: oui" in lire_index(root)


def test_sidecar_ajoute_modele_et_prompt_a_la_fiche(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG).returncode == 0
    texte = lire_index(root)
    assert "- modèle: gemini-3-pro-image-preview" in texte
    assert "- prompt: Une scène de marque fictive, fond clair" in texte


def test_prompt_de_la_fiche_tient_sur_une_ligne_et_est_coupe(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src, "Ligne une — longue\n" + "z" * 300)
    avant = lire_index(root)
    assert promeut(root, src, DEST_PNG).returncode == 0
    ajout = lire_index(root).replace(avant, "")
    ligne = [l for l in ajout.splitlines() if l.startswith("- prompt:")][0]
    assert "—" not in ligne and "–" not in ligne
    assert len(ligne) <= len("- prompt: ") + 121


def test_le_sidecar_suit_l_asset_promu(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG).returncode == 0
    promu = root / "01-brand" / "assets" / DEST_PNG
    fiche = Path(str(promu) + ".gen.json")
    assert fiche.exists()
    assert json.loads(fiche.read_text(encoding="utf-8"))["model"] == "gemini-3-pro-image-preview"


def test_ia_non_explicite_prime_sur_le_sidecar(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG, "--ia", "non").returncode == 0
    assert "- généré-par-ia: non" in lire_index(root)


def test_source_deduite_du_sidecar_quand_elle_manque(tmp_path):
    """Avec une fiche de génération, `--source` n'est plus obligatoire."""
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    res = run(root, str(src), "--dest", DEST_PNG, "--role", "test",
              "--droits", "création interne", "--auteur", "équipe marketing (modèle d'image)")
    assert res.returncode == 0, res.stderr
    texte = lire_index(root)
    assert "- source: généré par gemini-3-pro-image-preview" in texte


def test_droits_et_auteur_restent_obligatoires_avec_un_sidecar(tmp_path):
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    res = run(root, str(src), "--dest", DEST_PNG, "--role", "test")
    assert res.returncode != 0
    assert "--droits" in res.stderr and "--auteur" in res.stderr
    assert "--source" not in res.stderr


def test_png_promu_porte_le_tag_de_generation(tmp_path):
    """Le tag se pose sur la source de staging, la copie est octet à octet."""
    from PIL import Image

    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG).returncode == 0
    promu = root / "01-brand" / "assets" / DEST_PNG
    with Image.open(promu) as im:
        assert im.text["ai:generated_by"] == "gemini-3-pro-image-preview"


def test_asset_promu_jamais_reecrit_apres_la_copie(tmp_path):
    """Les octets de la destination sont ceux de la source au moment du transfert."""
    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)
    assert promeut(root, src, DEST_PNG, "--copy").returncode == 0
    promu = root / "01-brand" / "assets" / DEST_PNG
    assert promu.read_bytes() == src.read_bytes()


def test_sans_sidecar_rien_ne_change(tmp_path):
    root, src = make_root(tmp_path), make_source(tmp_path)
    assert promeut(root, src, "logos/clients/logo_client_test.svg").returncode == 0
    texte = lire_index(root)
    assert "- généré-par-ia: non" in texte
    assert "- modèle:" not in texte and "- prompt:" not in texte


def test_sidecar_vide_compte_comme_present(tmp_path):
    """Une fiche présente mais vide reste une fiche : l'asset vient d'une génération."""
    root, src = make_root(tmp_path), make_png(tmp_path)
    Path(str(src) + ".gen.json").write_text("{}", encoding="utf-8")
    assert promeut(root, src, DEST_PNG).returncode == 0
    texte = lire_index(root)
    assert "- généré-par-ia: oui" in texte
    assert "- modèle: à confirmer" in texte


def test_sha256_du_sidecar_recalcule_sur_l_asset_promu(tmp_path):
    """La fiche qui suit l'asset doit décrire l'asset, pas le fichier de staging."""
    import hashlib

    root, src = make_root(tmp_path), make_png(tmp_path)
    pose_sidecar(src)  # sha256 volontairement faux ("0" * 64)
    res = promeut(root, src, DEST_PNG)
    assert res.returncode == 0
    promu = root / "01-brand" / "assets" / DEST_PNG
    fiche = json.loads(Path(str(promu) + ".gen.json").read_text(encoding="utf-8"))
    assert fiche["sha256"] == hashlib.sha256(promu.read_bytes()).hexdigest()
    assert "sha256" in res.stdout


def test_sha256_conforme_ne_declenche_pas_d_avertissement(tmp_path):
    import hashlib

    root, src = make_root(tmp_path), make_png(tmp_path)
    fiche = pose_sidecar(src)
    donnees = json.loads(fiche.read_text(encoding="utf-8"))
    donnees["sha256"] = hashlib.sha256(src.read_bytes()).hexdigest()
    fiche.write_text(json.dumps(donnees, ensure_ascii=False), encoding="utf-8")
    res = promeut(root, src, DEST_PNG, "--ia", "non")  # pas de tag, octets intacts
    assert res.returncode == 0
    assert "sha256" not in res.stdout


# --- Aide en ligne -----------------------------------------------------------

def test_help_mentionne_les_nouveaux_champs():
    res = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                         capture_output=True, text=True)
    assert res.returncode == 0
    for option in ("--source", "--droits", "--auteur", "--ia"):
        assert option in res.stdout, f"{option} absent de --help"
    assert res.stdout.count("(obligatoire)") == 3, "les trois champs de droits doivent se dire obligatoires"


def test_le_depot_est_intact(tmp_path):
    """Garde-fou : aucun test ne doit avoir écrit dans le 01-brand/assets/ du dépôt."""
    def inventaire():
        return sorted(str(p) for p in ASSETS_DEPOT.rglob("*")) if ASSETS_DEPOT.exists() else []
    avant = inventaire()
    root, src = make_root(tmp_path), make_source(tmp_path)
    promeut(root, src, "logos/clients/logo_client_test.svg")
    assert inventaire() == avant


def test_catalogue_absent_refuse_et_explique(tmp_path):
    root = tmp_path / "vide"
    (root / "01-brand" / "assets").mkdir(parents=True)
    src = make_source(tmp_path)
    res = promeut(root, src, "logos/clients/logo_client_test.svg")
    assert res.returncode != 0
    assert "catalogue introuvable" in res.stderr
    assert src.exists()
