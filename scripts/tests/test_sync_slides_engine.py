"""Tests de scripts/sync-slides-engine.py (vendorisation du moteur de slides).

Le mécanisme se teste sur une mini-arborescence fictive de slides-agent, générée
depuis la table du script lui-même (COPIES, ADAPTATIONS) : chaque fichier mappé
existe et contient le texte d'origine de ses adaptations. Le câblage du dépôt se
teste à part : le registre docs/vendored-slides.md documente toute la table, et
chaque fichier vendorisé porte son en-tête.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sync-slides-engine.py"


def _charger():
    spec = importlib.util.spec_from_file_location("sync_slides_engine", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module    # requis par @dataclass (annotations différées)
    spec.loader.exec_module(module)
    return module


sync = _charger()

# Chemins de slides-agent cités dans les fichiers fictifs, et ce qui doit les
# remplacer (ou les laisser intacts) une fois vendorisés.
CHEMINS = (
    "scripts/qa.py presentations/<deck>.html `pytest tests -q` tests/test_qa.py "
    "brand/tokens.css docs/engine-parity.md templates/components/ reference/LAYOUTS.md "
    "reference/catalogue-layouts.html catalogue-layouts.html reference/photos/ "
    "assets/photos/ ../assets/photos/x.jpg 01-brand/tokens.json brand/tokens.json "
    "http://localhost:5173/presentations/ generate-image\n"
)
JPG = bytes(range(256)) * 4    # pas de l'UTF-8 : doit passer octet pour octet


def contenu_fictif(source: str, adaptations: tuple[str, ...]) -> str:
    anciens = "".join(sync.ADAPTATIONS[a].avant + "\n" for a in adaptations)
    suffixe = Path(source).suffix
    if suffixe == ".html":
        return f"<!DOCTYPE html>\n<p>{CHEMINS}</p>\n{anciens}"
    if suffixe == ".md":
        return f"# Doc\n\n{CHEMINS}{anciens}"
    if suffixe == ".sh":
        return f"#!/usr/bin/env bash\n# {CHEMINS}{anciens}"
    if source.startswith("tests/"):
        return f'"""{CHEMINS}"""\nimport pytest\n{anciens}'
    return f'#!/usr/bin/env python3\n"""{CHEMINS}"""\n{anciens}'


def source_fictive(tmp_path: Path) -> Path:
    source = tmp_path / "slides-agent"
    for copie in sync.COPIES:
        if "*" in copie.source:
            dossier = source / copie.source.rpartition("/")[0]
            dossier.mkdir(parents=True, exist_ok=True)
            if copie.source.endswith(".jpg"):
                (dossier / "pexels-a-1.jpg").write_bytes(JPG)
                (dossier / "pexels-b-2.jpg").write_bytes(JPG[::-1])
            else:
                (dossier / "pexels-a-1.json").write_text('{"photographer": "Fictif"}\n')
            continue
        chemin = source / copie.source
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu_fictif(copie.source, copie.adaptations), encoding="utf-8")
        if chemin.suffix == ".sh":
            chemin.chmod(0o755)
    return source


@pytest.fixture()
def arbres(tmp_path):
    source = source_fictive(tmp_path)
    cible = tmp_path / "template"
    (cible / "docs").mkdir(parents=True)
    (cible / sync.REGISTRE).write_text(
        f"# Registre\n\nAvant.\n\n{sync.MARQUEUR_DEBUT}\n{sync.MARQUEUR_FIN}\n\nAprès.\n",
        encoding="utf-8")
    return source, cible


def lancer(source: Path, cible: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    options = ["--root", str(cible)] + (["--source", str(source)] if source else [])
    return subprocess.run([sys.executable, str(SCRIPT), *options, *args],
                          capture_output=True, text=True, env=env)


def lire(cible: Path, rel: str) -> str:
    return (cible / rel).read_text(encoding="utf-8")


# --------------------------------------------------------------------------
# Synchronisation
# --------------------------------------------------------------------------

def test_sync_ecrit_chaque_fichier_puis_check_passe(arbres):
    source, cible = arbres
    resultat = lancer(source, cible)
    assert resultat.returncode == 0, resultat.stderr
    attendus, _ = sync.attendus(source)
    for attendu in attendus:
        assert (cible / attendu.cible).is_file(), attendu.cible
    assert lancer(source, cible, "--check").returncode == 0
    second = lancer(source, cible)
    assert "Rien à faire" in second.stdout


def test_chemins_reecrits_et_chemins_deja_justes_intacts(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    texte = lire(cible, "06-graphic-design/presentations/templates/base.html")
    for attendu in (
        "06-graphic-design/presentations/scripts/qa.py",
        "06-graphic-design/presentations/decks/<deck>.html",
        "`pytest scripts/tests -q`",
        "scripts/tests/test_slides_qa.py",
        "06-graphic-design/presentations/tokens.css",
        "06-graphic-design/presentations/docs/engine-parity.md",
        "06-graphic-design/presentations/templates/components/",
        "_examples/deck-catalogue/LAYOUTS.md",
        "_examples/deck-catalogue/catalogue.html catalogue.html",
        "_examples/deck-catalogue/photos/",
        "06-graphic-design/presentations/assets/photos/ ../assets/photos/x.jpg",
        "01-brand/tokens.json brand/tokens.json",
        "http://localhost:5173/06-graphic-design/presentations/decks/",
        "image-generation",
    ):
        assert attendu in texte, attendu


def test_reecriture_en_une_seule_passe():
    assert sync.reecrire("presentations/x.html") == "06-graphic-design/presentations/decks/x.html"
    assert sync.reecrire("reference/catalogue-layouts.html") == "_examples/deck-catalogue/catalogue.html"
    assert sync.reecrire("01-brand/tokens.json ../assets/photos/a.jpg") == \
        "01-brand/tokens.json ../assets/photos/a.jpg"


def test_adaptations_appliquees(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    for copie in sync.COPIES:
        for ident in copie.adaptations:
            adaptation = sync.ADAPTATIONS[ident]
            texte = lire(cible, copie.cible)
            assert adaptation.apres in texte, ident
            assert adaptation.avant not in texte, ident


def test_adaptation_qui_ne_s_applique_plus_arrete_tout(arbres):
    source, cible = arbres
    serve = source / "scripts/serve.sh"
    serve.write_text(serve.read_text(encoding="utf-8").replace("/..", "/../.."), encoding="utf-8")
    resultat = lancer(source, cible)
    assert resultat.returncode == 1
    assert "serve-racine" in resultat.stderr
    assert not (cible / "06-graphic-design").exists()    # rien n'a été copié à moitié


def test_en_tete_place_selon_le_type_de_fichier(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    html = lire(cible, "06-graphic-design/presentations/templates/base.html").splitlines()
    assert html[0] == "<!DOCTYPE html>" and html[1] == "<!--"
    assert sync.BANDEAU_TETE in html[2]
    assert sync.NOTE_STARTER in lire(cible, "06-graphic-design/presentations/templates/base.html")
    py = lire(cible, "06-graphic-design/presentations/scripts/qa.py").splitlines()
    assert py[0].startswith("#!") and sync.BANDEAU_TETE in py[1]
    test = lire(cible, "scripts/tests/test_slides_qa.py").splitlines()
    assert sync.BANDEAU_TETE in test[0]
    md = lire(cible, "_examples/deck-catalogue/LAYOUTS.md")
    assert md.startswith("<!--\n  " + sync.BANDEAU_TETE)
    # un commentaire HTML ne doit contenir aucun double tiret
    assert all("--" not in ligne for ligne in sync.lignes_bandeau("x", sync.NOTE_STARTER))


def test_copie_brute_octet_pour_octet(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    photos = cible / "_examples/deck-catalogue/photos"
    assert (photos / "pexels-a-1.jpg").read_bytes() == JPG
    assert (photos / "pexels-a-1.json").read_text() == '{"photographer": "Fictif"}\n'


def test_bit_executable_repris_de_la_source(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    assert os.access(cible / "06-graphic-design/presentations/scripts/serve.sh", os.X_OK)
    assert not os.access(cible / "06-graphic-design/presentations/scripts/qa.py", os.X_OK)


def test_check_detecte_une_edition_manuelle_et_sync_la_defait(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    deck = cible / "06-graphic-design/presentations/templates/components.md"
    original = deck.read_text(encoding="utf-8")
    deck.write_text(original + "retouche\n", encoding="utf-8")
    resultat = lancer(source, cible, "--check")
    assert resultat.returncode == 1
    assert "components.md" in resultat.stdout
    assert deck.read_text(encoding="utf-8").endswith("retouche\n")    # --check n'écrit rien
    assert lancer(source, cible).returncode == 0
    assert deck.read_text(encoding="utf-8") == original


def test_photo_retiree_en_amont_est_supprimee(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    photos = cible / "_examples/deck-catalogue/photos"
    (source / "reference/photos/pexels-b-2.jpg").unlink()
    (photos / "README.md").write_text("propre au template\n")
    resultat = lancer(source, cible, "--check")
    assert resultat.returncode == 1
    assert "pexels-b-2.jpg (n'existe plus dans slides-agent)" in resultat.stdout
    assert lancer(source, cible).returncode == 0
    assert not (photos / "pexels-b-2.jpg").exists()
    assert (photos / "README.md").exists()


def test_fichier_amont_non_mappe_signale(arbres):
    source, cible = arbres
    (source / "scripts/nouveau.py").write_text("x = 1\n")
    (source / "CLAUDE.md").write_text("# écarté volontairement\n")
    sortie = lancer(source, cible).stdout
    assert "scripts/nouveau.py" in sortie
    assert "CLAUDE.md" not in sortie


def test_fichier_mappe_absent_en_amont(arbres):
    source, cible = arbres
    (source / "scripts/shots.py").unlink()
    resultat = lancer(source, cible)
    assert resultat.returncode == 1
    assert "scripts/shots.py" in resultat.stderr


# --------------------------------------------------------------------------
# Source et registre
# --------------------------------------------------------------------------

def test_source_introuvable_sort_en_deux(tmp_path):
    resultat = lancer(tmp_path / "absent", tmp_path)
    assert resultat.returncode == 2
    assert "slides-agent" in resultat.stderr


def test_source_par_variable_d_environnement_puis_dossier_voisin(arbres, tmp_path):
    source, cible = arbres
    env = {**os.environ, sync.ENV_SOURCE: str(source)}
    assert lancer(None, cible, "--check", env=env).returncode == 1    # trouvée, rien copié
    env.pop(sync.ENV_SOURCE)
    # cible et source sont voisines dans tmp_path : ../slides-agent par défaut
    assert lancer(None, cible, env=env).returncode == 0


def test_registre_hors_git_et_texte_autour_conserve(arbres):
    source, cible = arbres
    assert lancer(source, cible).returncode == 0
    registre = lire(cible, sync.REGISTRE)
    assert registre.startswith("# Registre\n\nAvant.\n\n")
    assert registre.endswith("\n\nAprès.\n")
    assert "commit `inconnu`" in registre
    assert "copies brutes" in registre


def test_registre_sans_marqueurs_refuse(arbres):
    source, cible = arbres
    (cible / sync.REGISTRE).write_text("# Registre sans bloc\n", encoding="utf-8")
    resultat = lancer(source, cible)
    assert resultat.returncode == 1
    assert "slides-engine-sync" in resultat.stderr


def _git(dossier: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(dossier), *args], capture_output=True, text=True,
                          check=True).stdout.strip()


def test_commit_source_consigne_et_copie_sale_signalee(arbres):
    source, cible = arbres
    try:
        _git(source, "init", "-q")
        _git(source, "add", ".")
        _git(source, "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
             "commit", "-q", "-m", "fictif")
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("git indisponible")
    commit = _git(source, "rev-parse", "HEAD")
    assert lancer(source, cible).returncode == 0
    assert f"commit `{commit}`" in lire(cible, sync.REGISTRE)

    (source / "templates/components.md").write_text("modifié\n", encoding="utf-8")
    resultat = lancer(source, cible)
    assert "non commitées" in resultat.stdout
    assert "non commitées" in lire(cible, sync.REGISTRE)


# --------------------------------------------------------------------------
# Câblage du dépôt
# --------------------------------------------------------------------------

def test_le_registre_documente_toute_la_table():
    registre = (REPO / sync.REGISTRE).read_text(encoding="utf-8")
    for copie in sync.COPIES:
        assert f"`{copie.source}`" in registre, copie.source
        assert f"`{copie.cible}`" in registre, copie.cible
    for ident in sync.ADAPTATIONS:
        assert f"`{ident}`" in registre, ident
    for regle in sync.REECRITURES:
        assert f"`{regle.id}`" in registre, regle.id
    for ecarte in sync.ECARTES:
        assert f"`{ecarte}`" in registre, ecarte
    assert sync.MARQUEUR_DEBUT in registre and sync.MARQUEUR_FIN in registre


def test_les_fichiers_vendorises_du_depot_portent_leur_en_tete():
    """Un fichier vendorisé manquant ou privé de son en-tête trahit une copie à la main."""
    for copie in sync.COPIES:
        if "*" in copie.source:
            dossier = REPO / copie.cible
            assert any(dossier.glob(copie.source.rpartition("/")[2])), copie.cible
            continue
        texte = (REPO / copie.cible).read_text(encoding="utf-8")
        assert sync.BANDEAU_TETE in texte[:400], copie.cible


def _source_locale() -> Path | None:
    try:
        return sync.trouver_source(None, REPO)
    except FileNotFoundError:
        return None


@pytest.mark.skipif(_source_locale() is None,
                    reason="pas de checkout de slides-agent ($SLIDES_AGENT_DIR ou ../slides-agent)")
def test_la_copie_vendorisee_correspond_a_la_source_locale():
    resultat = subprocess.run([sys.executable, str(SCRIPT), "--check"],
                              capture_output=True, text=True)
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
