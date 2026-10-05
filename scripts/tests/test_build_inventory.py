"""Tests de scripts/build-inventory.py (index anti-répétition des livrables).

Le corpus est fictif et suit la disposition des dossiers du template, telle que
la déclare scripts/build-inventory.toml (la configuration livrée).
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "build-inventory.py"
CONFIG = REPO / "scripts" / "build-inventory.toml"
INVENTAIRE = "_templates/inventory.md"


def _load_module():
    """Charge build-inventory.py par chemin : son nom contient un tiret."""
    spec = importlib.util.spec_from_file_location("build_inventory", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # les dataclasses ont besoin du module enregistré
    spec.loader.exec_module(module)
    module.charger_config(CONFIG)
    return module


build_inventory = _load_module()


# --------------------------------------------------------------------------
# Fabrique de racine jetable
# --------------------------------------------------------------------------

POST_PUBLIE = """---
date: 2026-01-05
langue: FR
likes: 12
commentaires: 2
url: https://example.com/posts/1
---

Un post publié dont le corps commence ici et raconte une scène.
"""

POST_VALIDE = """---
date: 2025-12-01
langue: FR
likes: 0
url: ""
---

Les premiers mots de ce post servent de sujet faute de titre explicite.
"""

POST_REJETE = """---
date: 2025-11-03
statut: rejeté
motif: parallélisme négatif dans l'accroche
---

Un post arrêté au brand check.
"""

EDITION = """---
date: 2026-02-02
campaign_name: NL_EXEMPLE
subject: "Nouveau guide. Nouvelle équipe"
category: newsletter
sent: 75
open_rate: 41%
---

Corps de l'édition.
"""

PROMO_AVEC_PIPE = """---
date: 2026-03-03
subject: "Atelier | dernier appel"
category: promo
sent: 56
---

Corps de la promo.
"""

ARTICLE = """---
date: 2026-07-07
---

# Mesurer la valeur d'un projet de données

Premier paragraphe de l'article.
"""

FRONTMATTER_DEUX_POINTS = """---
date: 2026-05-02
subject: "Hi {$name}: the 9:30 session is open"
---

Corps.
"""

FRONTMATTER_LISTES = """---
date: 2026-05-03
tags: [guide, rapport]
piliers:
  - data
  - communaute
---

Corps.
"""

FRONTMATTER_NON_TERMINE = """---
date: 2026-05-04
subject: "Un frontmatter mal fermé"

Le corps commence sans que le bloc ait été refermé.
"""

SANS_DATE = """---
langue: FR
---

Un fichier sans date exploitable.
"""

PLAN_COMM = """---
date: 2026-08-01
---

# Plan de communication du salon d'automne
"""

CARROUSEL = "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head><body><div>slide</div></body></html>"

DECK_TITRE = (
    "<!DOCTYPE html><html><head><title>Exemple · Offre conseil</title></head>"
    "<body><h1>Offre</h1></body></html>"
)

DECK_COMMENTE = (
    "<!--\n  Mode d'emploi du gabarit :\n  2. Mettre à jour <title>\n  3. Remplacer les plaques\n-->"
    "<html><head><title>Exemple · Revue du parcours client</title></head><body></body></html>"
)

DECK_H1 = (
    "<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head>"
    "<body><h1 class=\"reveal\">Le semestre raconté à l'équipe</h1></body></html>"
)

FICHIERS = {
    "03-social-media/linkedin/examples/2026-01-05-un-post-publie.md": POST_PUBLIE,
    "03-social-media/linkedin/examples/2025-12-01-un-post-sans-metrique.md": POST_VALIDE,
    "03-social-media/linkedin/examples/2025-11-03-un-post-rejete.md": POST_REJETE,
    "03-social-media/linkedin/examples/notes.txt": "hors périmètre",
    "03-social-media/discord/examples/2026-04-10-annonce.md": POST_PUBLIE.replace("2026-01-05", "2026-04-10"),
    "04-email/newsletter/editions/2026-02-02-nouveau-guide.md": EDITION,
    "04-email/promos/2026-03-03-atelier-dernier-appel.md": PROMO_AVEC_PIPE,
    "04-email/sales-outreach/2026-04-01-hi-name.md": EDITION.replace("2026-02-02", "2026-04-01"),
    "04-email/sales-outreach/playbook.md": SANS_DATE,
    "04-email/promos/notes-sans-date.md": SANS_DATE,
    "06-graphic-design/presentations/decks/offre-commentee-2026-05-06-v1.html": DECK_COMMENTE,
    "06-graphic-design/presentations/decks/offre-conseil-2026-05-05-v1.html": DECK_TITRE,
    "06-graphic-design/presentations/decks/revue/semestre-2026-06-06-v1.html": DECK_H1,
    "06-graphic-design/outputs/carrousel-mon-sujet-2026-04-04/index.html": CARROUSEL,
    "07-events/salon-automne-2026/comm-plan.md": PLAN_COMM,
    "07-events/templates/comm-plan.md": PLAN_COMM,
    "09-seo/articles/2026-07-07-valeur-donnees.md": ARTICLE,
    "09-seo/articles/2026-07-07-alpha-meme-date.md": ARTICLE,
}

BINAIRES = [
    "06-graphic-design/outputs/carrousel-mon-sujet-2026-04-04/exports/carrousel.pdf",
    "06-graphic-design/presentations/decks/offre-conseil.pdf",
]


def make_root(tmp_path: Path) -> Path:
    """Construit une racine jetable : l'inventaire vide du template plus un corpus fictif."""
    root = tmp_path / "repo"
    cible = root / INVENTAIRE
    cible.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REPO / INVENTAIRE, cible)
    for rel, contenu in FICHIERS.items():
        chemin = root / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(contenu, encoding="utf-8")
    mal_encode = root / "04-email/promos/2026-05-08-mal-encode.md"
    mal_encode.write_bytes(
        b"---\ndate: 2026-05-08\n---\n\nCaf\xe9 encod\xe9 en latin-1, pas en UTF-8\n"
    )
    for rel in BINAIRES:
        chemin = root / rel
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_bytes(b"%PDF-1.4 factice")
    return root


def run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--config", str(CONFIG), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def lignes_tableau(root: Path) -> list[str]:
    texte = (root / INVENTAIRE).read_text(encoding="utf-8")
    return [
        ligne
        for ligne in texte.splitlines()
        if ligne.startswith("| ") and not ligne.startswith("| Date ") and "---" not in ligne
    ]


def cellules(ligne: str) -> list[str]:
    return [c.strip() for c in re.split(r"(?<!\\)\|", ligne.strip())[1:-1]]


# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

def test_configuration_livree_declare_les_sources_du_template():
    dossiers = {source.dossier for source in build_inventory.SOURCES}
    assert "03-social-media/linkedin/examples" in dossiers
    assert "06-graphic-design/presentations/decks" in dossiers
    for source in build_inventory.SOURCES:
        assert (REPO / Path(source.dossier).parts[0]).is_dir(), source.dossier


def test_configuration_absente_sort_en_deux(tmp_path):
    root = make_root(tmp_path)
    resultat = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--config", str(tmp_path / "absent.toml")],
        capture_output=True, text=True, check=False,
    )
    assert resultat.returncode == 2
    assert "configuration introuvable" in resultat.stderr


def test_configuration_sans_source_refusee(tmp_path):
    vide = tmp_path / "vide.toml"
    vide.write_text('inventory = "_templates/inventory.md"\n', encoding="utf-8")
    with pytest.raises(build_inventory.InventaireError, match="aucune source"):
        build_inventory.charger_config(vide)
    build_inventory.charger_config(CONFIG)    # remet la configuration livrée


# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------

def test_frontmatter_lit_les_paires_cle_valeur():
    champs = build_inventory.lire_frontmatter(EDITION)
    assert champs["date"] == "2026-02-02"
    assert champs["campaign_name"] == "NL_EXEMPLE"
    assert champs["sent"] == "75"


def test_frontmatter_retire_les_guillemets():
    champs = build_inventory.lire_frontmatter(EDITION)
    assert champs["subject"] == "Nouveau guide. Nouvelle équipe"


def test_frontmatter_ignore_le_corps():
    champs = build_inventory.lire_frontmatter(ARTICLE)
    assert "Mesurer" not in " ".join(champs.values())
    assert set(champs) == {"date"}


def test_frontmatter_absent_rend_un_dictionnaire_vide():
    assert build_inventory.lire_frontmatter("# Titre\n\nDu texte.\n") == {}


def test_frontmatter_garde_les_deux_points_de_la_valeur():
    champs = build_inventory.lire_frontmatter(FRONTMATTER_DEUX_POINTS)
    assert champs["subject"] == "Hi {$name}: the 9:30 session is open"


def test_frontmatter_traite_les_listes_comme_des_valeurs_brutes():
    """Une liste en crochets reste une chaîne ; une liste en tirets rend une valeur vide."""
    champs = build_inventory.lire_frontmatter(FRONTMATTER_LISTES)
    assert champs["tags"] == "[guide, rapport]"
    assert champs["piliers"] == ""
    assert "data" not in champs and "- data" not in champs
    assert set(champs) == {"date", "tags", "piliers"}


def test_frontmatter_non_termine_garde_les_champs_lus():
    """Le `---` de fermeture manque : les champs déjà lus sont conservés."""
    champs = build_inventory.lire_frontmatter(FRONTMATTER_NON_TERMINE)
    assert champs["date"] == "2026-05-04"
    assert champs["subject"] == "Un frontmatter mal fermé"


# --------------------------------------------------------------------------
# Extraction d'un livrable
# --------------------------------------------------------------------------

def test_livrable_email_prend_le_sujet_du_frontmatter(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("04-email/newsletter/editions/2026-02-02-nouveau-guide.md")
    )
    assert livrable.date == "2026-02-02"
    assert livrable.canal == "newsletter"
    assert livrable.type == "email"
    assert livrable.sujet == "Nouveau guide. Nouvelle équipe"
    assert livrable.statut == "publié"


def test_livrable_post_sans_metrique_est_valide(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("03-social-media/linkedin/examples/2025-12-01-un-post-sans-metrique.md")
    )
    assert livrable.statut == "validé"
    assert livrable.sujet.startswith("Les premiers mots de ce post")


def test_livrable_post_publie_detecte_par_ses_metriques(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("03-social-media/linkedin/examples/2026-01-05-un-post-publie.md")
    )
    assert livrable.statut == "publié"
    assert livrable.canal == "linkedin"
    assert livrable.type == "post"


def test_livrable_discord(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(root, Path("03-social-media/discord/examples/2026-04-10-annonce.md"))
    assert (livrable.canal, livrable.type) == ("discord", "post")


def test_livrable_rejete_est_archive(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("03-social-media/linkedin/examples/2025-11-03-un-post-rejete.md")
    )
    assert livrable.statut == "archivé"


def test_livrable_article_prend_son_titre_h1(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(root, Path("09-seo/articles/2026-07-07-valeur-donnees.md"))
    assert livrable.sujet == "Mesurer la valeur d'un projet de données"
    assert livrable.canal == "blog"
    assert livrable.type == "article"


def test_livrable_deck_prend_son_titre_html(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("06-graphic-design/presentations/decks/offre-conseil-2026-05-05-v1.html")
    )
    assert livrable.sujet == "Exemple · Offre conseil"
    assert livrable.date == "2026-05-05"
    assert livrable.canal == "slides"
    assert livrable.type == "deck"


def test_livrable_deck_sans_titre_retombe_sur_le_h1(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("06-graphic-design/presentations/decks/revue/semestre-2026-06-06-v1.html")
    )
    assert livrable.sujet == "Le semestre raconté à l'équipe"


def test_livrable_carrousel_retombe_sur_le_nom_de_dossier(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("06-graphic-design/outputs/carrousel-mon-sujet-2026-04-04/index.html"),
    )
    assert livrable.date == "2026-04-04"
    assert livrable.sujet == "mon sujet"
    assert (livrable.canal, livrable.type) == ("linkedin", "carrousel")


def test_livrable_plan_de_com_evenementiel(tmp_path):
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(root, Path("07-events/salon-automne-2026/comm-plan.md"))
    assert (livrable.canal, livrable.type) == ("event", "plan-comm")
    assert livrable.sujet == "Plan de communication du salon d'automne"


def test_un_gabarit_n_est_jamais_un_livrable(tmp_path):
    root = make_root(tmp_path)
    assert build_inventory.source_de(Path("07-events/templates/comm-plan.md")) is None
    chemins = {l.chemin for l in build_inventory.collecter(root)}
    assert "07-events/templates/comm-plan.md" not in chemins


def test_livrable_sans_date_est_ignore(tmp_path):
    root = make_root(tmp_path)
    assert build_inventory.extraire(root, Path("04-email/promos/notes-sans-date.md")) is None


def test_fichier_de_service_est_hors_perimetre(tmp_path):
    root = make_root(tmp_path)
    assert build_inventory.source_de(Path("04-email/sales-outreach/playbook.md")) is None
    assert build_inventory.extraire(root, Path("04-email/sales-outreach/playbook.md")) is None


def test_livrable_deck_ignore_le_commentaire_den_tete(tmp_path):
    """Le gabarit de deck cite « <title> » dans son mode d'emploi en commentaire."""
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(
        root, Path("06-graphic-design/presentations/decks/offre-commentee-2026-05-06-v1.html")
    )
    assert livrable.sujet == "Exemple · Revue du parcours client"


# --------------------------------------------------------------------------
# Collecte, tri, rendu
# --------------------------------------------------------------------------

def test_collecte_ignore_les_extensions_hors_perimetre(tmp_path):
    root = make_root(tmp_path)
    chemins = {livrable.chemin for livrable in build_inventory.collecter(root)}
    assert not any(c.endswith((".pdf", ".txt")) for c in chemins)
    assert "04-email/promos/2026-03-03-atelier-dernier-appel.md" in chemins


def test_collecte_trie_du_plus_recent_au_plus_ancien(tmp_path):
    root = make_root(tmp_path)
    dates = [livrable.date for livrable in build_inventory.collecter(root)]
    assert dates == sorted(dates, reverse=True)
    assert dates[0] == "2026-08-01"


def test_fichier_mal_encode_est_lu_sans_lever(tmp_path):
    """Les octets illisibles sont remplacés, le livrable reste indexable."""
    root = make_root(tmp_path)
    livrable = build_inventory.extraire(root, Path("04-email/promos/2026-05-08-mal-encode.md"))
    assert livrable is not None
    assert livrable.date == "2026-05-08"
    assert livrable.sujet.startswith("Caf")


def test_tri_departage_par_chemin_a_date_egale(tmp_path):
    root = make_root(tmp_path)
    memes = [l.chemin for l in build_inventory.collecter(root) if l.date == "2026-07-07"]
    assert len(memes) == 2
    assert memes == sorted(memes)


def test_sujet_remplace_les_tirets_longs():
    assert build_inventory.nettoyer("78% — Présentation interne") == "78% · Présentation interne"
    assert "–" not in build_inventory.nettoyer("Un titre – coupé")


def test_rendu_echappe_les_barres_verticales(tmp_path):
    root = make_root(tmp_path)
    run(root)
    ligne = next(l for l in lignes_tableau(root) if "Atelier" in l)
    assert r"Atelier \| dernier appel" in ligne
    assert len(cellules(ligne)) == 6


# --------------------------------------------------------------------------
# Modes de la ligne de commande
# --------------------------------------------------------------------------

def test_reconstruction_remplit_le_tableau(tmp_path):
    root = make_root(tmp_path)
    resultat = run(root)
    assert resultat.returncode == 0, resultat.stderr
    lignes = lignes_tableau(root)
    assert len(lignes) == len(build_inventory.collecter(root))
    texte = (root / INVENTAIRE).read_text(encoding="utf-8")
    assert "Dernière mise à jour" in texte
    assert "(mode : reconstruction)" in texte


def test_reconstruction_est_idempotente(tmp_path):
    root = make_root(tmp_path)
    run(root)
    premier = (root / INVENTAIRE).read_text(encoding="utf-8")
    run(root)
    assert (root / INVENTAIRE).read_text(encoding="utf-8") == premier


def test_reconstruction_conserve_la_note_d_usage(tmp_path):
    root = make_root(tmp_path)
    run(root)
    texte = (root / INVENTAIRE).read_text(encoding="utf-8")
    assert "## Note d'usage" in texte
    assert texte.startswith((REPO / INVENTAIRE).read_text(encoding="utf-8").splitlines()[0])


def test_check_sort_zero_juste_apres_generation(tmp_path):
    root = make_root(tmp_path)
    run(root)
    assert run(root, "--check").returncode == 0


def test_check_signale_les_fichiers_sans_date_sans_echouer(tmp_path):
    root = make_root(tmp_path)
    run(root)
    resultat = run(root, "--check")
    assert resultat.returncode == 0
    assert "avertissement" in resultat.stderr
    assert "notes-sans-date.md" in resultat.stderr
    assert "avertissement" not in resultat.stdout


def test_check_sort_un_si_le_tableau_a_derive(tmp_path):
    root = make_root(tmp_path)
    run(root)
    cible = root / INVENTAIRE
    texte = cible.read_text(encoding="utf-8")
    cible.write_text(texte.replace("| blog | article ", "| web | landing ", 1), encoding="utf-8")
    assert run(root, "--check").returncode == 1


def test_check_n_ecrit_rien(tmp_path):
    root = make_root(tmp_path)
    run(root)
    avant = (root / INVENTAIRE).read_text(encoding="utf-8")
    (root / "03-social-media/linkedin/examples/2026-08-08-nouveau.md").write_text(
        POST_PUBLIE.replace("2026-01-05", "2026-08-08"), encoding="utf-8"
    )
    assert run(root, "--check").returncode == 1
    assert (root / INVENTAIRE).read_text(encoding="utf-8") == avant


def test_add_insere_une_ligne_absente(tmp_path):
    root = make_root(tmp_path)
    run(root)
    avant = len(lignes_tableau(root))
    nouveau = "03-social-media/linkedin/examples/2026-08-08-nouveau-post.md"
    (root / nouveau).write_text(POST_PUBLIE.replace("2026-01-05", "2026-08-08"), encoding="utf-8")
    resultat = run(root, "--add", nouveau)
    assert resultat.returncode == 0, resultat.stderr
    lignes = lignes_tableau(root)
    assert len(lignes) == avant + 1
    assert nouveau in lignes[0]
    assert "(mode : incrément)" in (root / INVENTAIRE).read_text(encoding="utf-8")


def test_add_est_idempotent(tmp_path):
    root = make_root(tmp_path)
    run(root)
    chemin = "04-email/promos/2026-03-03-atelier-dernier-appel.md"
    run(root, "--add", chemin)
    premier = (root / INVENTAIRE).read_text(encoding="utf-8")
    run(root, "--add", chemin)
    assert (root / INVENTAIRE).read_text(encoding="utf-8") == premier
    assert sum(chemin in ligne for ligne in lignes_tableau(root)) == 1


def test_add_met_a_jour_la_ligne_existante(tmp_path):
    root = make_root(tmp_path)
    run(root)
    chemin = "03-social-media/linkedin/examples/2025-12-01-un-post-sans-metrique.md"
    ligne = next(l for l in lignes_tableau(root) if chemin in l)
    assert cellules(ligne)[5] == "validé"
    (root / chemin).write_text(POST_PUBLIE.replace("2026-01-05", "2025-12-01"), encoding="utf-8")
    run(root, "--add", chemin)
    lignes = [l for l in lignes_tableau(root) if chemin in l]
    assert len(lignes) == 1
    assert cellules(lignes[0])[5] == "publié"


def test_add_conserve_les_autres_lignes(tmp_path):
    root = make_root(tmp_path)
    run(root)
    attendu = len(lignes_tableau(root))
    run(root, "--add", "09-seo/articles/2026-07-07-valeur-donnees.md")
    assert len(lignes_tableau(root)) == attendu


def test_add_refuse_un_chemin_hors_perimetre(tmp_path):
    root = make_root(tmp_path)
    run(root)
    resultat = run(root, "--add", "_templates/inventory.md")
    assert resultat.returncode != 0
    assert "périmètre" in (resultat.stderr + resultat.stdout)


def test_add_refuse_un_fichier_absent(tmp_path):
    root = make_root(tmp_path)
    run(root)
    resultat = run(root, "--add", "03-social-media/linkedin/examples/inexistant.md")
    assert resultat.returncode != 0


# --------------------------------------------------------------------------
# Inventaire versionné du dépôt
# --------------------------------------------------------------------------

def test_inventaire_versionne_se_lit_et_reste_vide_dans_le_template():
    """Le gabarit d'inventaire se parse, et le template ne livre aucune ligne."""
    texte = (REPO / INVENTAIRE).read_text(encoding="utf-8")
    assert build_inventory.lire_tableau(texte) == []
    assert "{{COMPANY_NAME}}" in texte.splitlines()[0]
