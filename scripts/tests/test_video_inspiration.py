"""Tests de la bibliothèque d'inspiration (08-video/scripts/inspiration.py).

Aucun accès au réseau extérieur et aucune donnée réelle : les cinq entrées
ci-dessous sont fictives, écrites par le test. Le cache et la source par défaut
sont redirigés vers un dossier temporaire par une fixture automatique, de sorte
qu'un test qui oublierait `--source` ou `--cache` n'atteint ni le dépôt ni
Internet. Seul le test de la couche HTTP parle à un serveur local (boucle
locale), et se saute si la machine ne peut pas en ouvrir un.
"""
from __future__ import annotations

import importlib.util
import json
import re
import socket
import subprocess
import sys
import threading
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CLI = REPO / "08-video" / "scripts" / "inspiration.py"


def _charger():
    spec = importlib.util.spec_from_file_location("inspiration_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


inspiration = _charger()
SOURCE_REELLE = inspiration.SOURCE_DEFAUT
CACHE_REEL = inspiration.CACHE_DEFAUT

# Prompt de plus de 240 caractères, pour vérifier la borne de l'extrait.
PROMPT_LONG = ("Rotating crystal under a slow camera orbit, facets catching a cold light while the "
               "background fades to black. ") * 4


def entrees_fictives() -> list[dict]:
    return [
        {"slug": "fictif-aurore", "title": "Particle aurora", "author": "auteur-fictif-a",
         "author_url": "https://example.org/auteur-fictif-a", "post_url": "https://example.org/posts/aurore",
         "category": "motion", "tech_tags": ["canvas", "particles"],
         "prompt": "A slow aurora of glowing particles drifting across a dark horizon, the camera barely moves.",
         "prompt_partial": False, "poster_url": "https://example.org/posters/aurore.webp",
         "skillry_url": None, "added": "2026-09-01", "has_remake": False},
        {"slug": "fictif-cristal", "title": None, "author": "auteur-fictif-b",
         "author_url": "https://example.org/auteur-fictif-b", "post_url": "https://example.org/posts/cristal",
         "category": "3d", "tech_tags": ["threejs", "shader"], "prompt": PROMPT_LONG,
         "prompt_partial": True, "poster_url": "https://example.org/posters/cristal.webp",
         "skillry_url": "https://example.org/remakes/cristal", "added": "2026-09-20", "has_remake": True},
        {"slug": "fictif-cartes", "title": "Café des données", "author": "auteur-fictif-c",
         "author_url": "https://example.org/auteur-fictif-c", "post_url": "https://example.org/posts/cartes",
         "category": "explainer", "tech_tags": ["svg", "gsap"],
         "prompt": "An animated explainer: data cards slide in, a bar chart grows, small étoile markers pop. Step by step.",
         "prompt_partial": False, "poster_url": "https://example.org/posters/cartes.webp",
         "skillry_url": None, "added": "2026-09-20", "has_remake": False},
        {"slug": "fictif-jeu", "title": "Playable orbit toy", "author": "auteur-fictif-d",
         "author_url": "https://example.org/auteur-fictif-d", "post_url": "https://example.org/posts/jeu",
         "category": "interactive", "tech_tags": ["canvas", "physics"],
         "prompt": "Interactive toy: drag a planet and watch the particles react. Particles orbit, particles bounce, particles fade.",
         "prompt_partial": False, "poster_url": "https://example.org/posters/jeu.webp",
         "skillry_url": None, "added": "2026-08-15", "has_remake": False},
        {"slug": "fictif-logo", "title": "Logo reveal", "author": "auteur-fictif-e",
         "author_url": "https://example.org/auteur-fictif-e", "post_url": "https://example.org/posts/logo",
         "category": "motion", "tech_tags": ["svg", "gsap", "audio"],
         "prompt": "Logo reveal with a slow camera push and a soft whoosh, a few particles settle at the end.",
         "prompt_partial": False, "poster_url": "https://example.org/posters/logo.webp",
         "skillry_url": "https://example.org/remakes/logo", "added": "2026-10-01", "has_remake": True},
    ]


LARGE = "slow camera particles data orbit logo crystal"      # touche les cinq entrées


@pytest.fixture(autouse=True)
def isole(monkeypatch, tmp_path_factory):
    """Aucun test n'atteint le vrai cache du dépôt ni Internet, même s'il oublie --source ou --cache."""
    monkeypatch.setattr(inspiration, "SOURCE_DEFAUT", "http://127.0.0.1:9/videos.json")
    monkeypatch.setattr(inspiration, "CACHE_DEFAUT", tmp_path_factory.mktemp("cache-defaut") / "cache.json")


@pytest.fixture
def source(tmp_path) -> Path:
    chemin = tmp_path / "videos.json"
    chemin.write_text(json.dumps(entrees_fictives(), ensure_ascii=False), encoding="utf-8")
    return chemin


@pytest.fixture
def cache(tmp_path) -> Path:
    return tmp_path / "cache" / "opus-5-5-videos.json"


def lancer(capsys, *args, source=None, cache=None, format=None):
    """(code, stdout, stderr) d'un appel en processus."""
    argv = [str(a) for a in args]
    if source is not None:
        argv += ["--source", str(source)]
    if cache is not None:
        argv += ["--cache", str(cache)]
    if format:
        argv += ["--format", format]
    capsys.readouterr()
    code = inspiration.main(argv)
    sortie = capsys.readouterr()
    return code, sortie.out, sortie.err


def slugs(sortie: str) -> list[str]:
    return re.findall(r"^\s+slug : (\S+)$", sortie, re.M)


def vieillir_le_cache(cache: Path, jours: int) -> None:
    enveloppe = json.loads(cache.read_text(encoding="utf-8"))
    enveloppe["recupere"] = (datetime.now(timezone.utc) - timedelta(days=jours)).isoformat()
    cache.write_text(json.dumps(enveloppe), encoding="utf-8")


# ------------------------------------------------------------------ constantes et hygiène du dépôt

def test_source_et_cache_par_defaut():
    assert SOURCE_REELLE == ("https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/data/videos.json")
    assert CACHE_REEL == REPO / ".cache" / "inspiration" / "opus-5-5-videos.json"
    assert inspiration.VALIDITE_JOURS == 7
    ignores = (REPO / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".cache/" in [ligne.strip() for ligne in ignores], "le cache doit rester hors du dépôt"


def test_aucune_donnee_reelle_dans_le_depot():
    """Les données des créateurs vivent dans .cache/ (ignoré), jamais dans l'index Git."""
    try:
        suivis = subprocess.run(["git", "ls-files", "--", ".cache"], cwd=REPO, capture_output=True, text=True).stdout
    except OSError:
        pytest.skip("git absent")
    assert suivis.strip() == ""


# ------------------------------------------------------------------ chercher : classement

def test_classement_par_nombre_de_mots_puis_date_decroissante(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "slow camera particles", source=source, cache=cache)
    assert code == 0
    # E et A trouvent 3 mots : la plus récente d'abord ; B en trouve 2 ; D 1 (même répété trois fois) ; C aucun.
    assert slugs(out) == ["fictif-logo", "fictif-aurore", "fictif-cristal", "fictif-jeu"]


def test_un_mot_repete_ne_compte_qu_une_fois(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "slow camera particles", source=source, cache=cache, format="json")
    scores = {r["slug"]: r["score"] for r in json.loads(out)}
    assert scores == {"fictif-logo": 3, "fictif-aurore": 3, "fictif-cristal": 2, "fictif-jeu": 1}


def test_a_score_et_date_egaux_le_slug_departage(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "data crystal", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-cartes", "fictif-cristal"]       # 2026-09-20 chacune


def test_sans_accents_et_sans_casse(capsys, source, cache):
    for requete in ("etoile", "ÉTOILE", "Étoile"):
        code, out, _ = lancer(capsys, "chercher", requete, source=source, cache=cache)
        assert code == 0 and slugs(out) == ["fictif-cartes"], requete
    for requete in ("cafe", "CAFÉ"):
        code, out, _ = lancer(capsys, "chercher", requete, source=source, cache=cache)
        assert slugs(out) == ["fictif-cartes"], requete            # titre « Café des données »
    code, out, _ = lancer(capsys, "chercher", "donnees", source=source, cache=cache)
    assert slugs(out) == ["fictif-cartes"]                         # le mot n'est que dans le titre


def test_les_tags_techniques_sont_cherches(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "audio", source=source, cache=cache)
    assert slugs(out) == ["fictif-logo"]                           # « audio » n'est que dans tech_tags
    code, out, _ = lancer(capsys, "chercher", "threejs", source=source, cache=cache)
    assert slugs(out) == ["fictif-cristal"]


def test_mot_long_cherche_par_prefixe_mot_court_exact(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "particle", source=source, cache=cache)
    assert code == 0 and set(slugs(out)) == {"fictif-aurore", "fictif-jeu", "fictif-logo"}     # « particles » trouvé
    code, out, _ = lancer(capsys, "chercher", "sl", source=source, cache=cache)
    assert code == 1 and slugs(out) == []                          # « sl » n'est pas le début de « slow »


def test_le_debut_d_un_mot_compte_pas_son_milieu(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "rotat", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-cristal"]            # début de « Rotating »
    code, out, _ = lancer(capsys, "chercher", "icle", source=source, cache=cache)
    assert code == 1                                                 # milieu de « particles » : pas une correspondance


def test_mots_vides_ignores_quand_il_reste_des_mots(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "the logo of", source=source, cache=cache, format="json")
    assert [r["slug"] for r in json.loads(out)] == ["fictif-logo"]
    assert json.loads(out)[0]["score"] == 1


def test_aucun_resultat_code_1(capsys, source, cache):
    code, out, err = lancer(capsys, "chercher", "submarine", source=source, cache=cache)
    assert code == 1 and slugs(out) == [] and "Traceback" not in err


def test_requete_vide_code_2(capsys, source, cache):
    for args in (("chercher",), ("chercher", ""), ("chercher", "   "), ("chercher", "?!")):
        code, out, err = lancer(capsys, *args, source=source, cache=cache)
        assert code == 2, args
        assert "ERREUR" in err and "Traceback" not in err


# ------------------------------------------------------------------ chercher : filtres

def test_filtre_categorie(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", LARGE, "--categorie", "3d", source=source, cache=cache)
    assert slugs(out) == ["fictif-cristal"]
    code, out, _ = lancer(capsys, "chercher", LARGE, "--categorie", "motion", source=source, cache=cache)
    assert set(slugs(out)) == {"fictif-aurore", "fictif-logo"}


def test_filtre_categorie_inconnue_est_une_erreur_d_usage(capsys, source, cache):
    code, _, err = lancer(capsys, "chercher", LARGE, "--categorie", "bidon", source=source, cache=cache)
    assert code == 2 and "Traceback" not in err


def test_filtre_tech(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", LARGE, "--tech", "gsap", source=source, cache=cache)
    assert set(slugs(out)) == {"fictif-cartes", "fictif-logo"}
    code, out, _ = lancer(capsys, "chercher", LARGE, "--tech", "GSAP", source=source, cache=cache)
    assert set(slugs(out)) == {"fictif-cartes", "fictif-logo"}      # casse indifférente
    code, out, _ = lancer(capsys, "chercher", LARGE, "--tech", "gs", source=source, cache=cache)
    assert code == 1                                                # tag exact, pas un préfixe


def test_filtre_avec_remake(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", LARGE, "--avec-remake", source=source, cache=cache)
    assert set(slugs(out)) == {"fictif-cristal", "fictif-logo"}


def test_filtres_combines(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", LARGE, "--tech", "svg", "--avec-remake", "--categorie", "motion",
                          source=source, cache=cache)
    assert slugs(out) == ["fictif-logo"]


def test_top(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", LARGE, "--top", "2", source=source, cache=cache)
    assert len(slugs(out)) == 2
    code, out, _ = lancer(capsys, "chercher", LARGE, source=source, cache=cache)
    assert len(slugs(out)) == 5                                     # défaut assez large pour les cinq


@pytest.mark.parametrize("valeur", ["0", "-3", "abc"])
def test_top_invalide_code_2(capsys, source, cache, valeur):
    code, _, err = lancer(capsys, "chercher", LARGE, "--top", valeur, source=source, cache=cache)
    assert code == 2 and "Traceback" not in err


# ------------------------------------------------------------------ chercher : sortie

def bloc(sortie: str, slug: str) -> str:
    """Le bloc de texte d'un résultat, du numéro à son slug."""
    for morceau in re.split(r"(?m)^(?=\d+\. )", sortie):
        if f"slug : {slug}" in morceau:
            return morceau
    raise AssertionError(f"{slug} absent de la sortie")


def test_sortie_texte_complete(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "crystal", source=source, cache=cache)
    assert code == 0
    b = bloc(out, "fictif-cristal")
    assert b.startswith("1. Rotating crystal under a slow camera orbit"), "sans titre : le début du prompt"
    for attendu in ("3d", "threejs, shader", "auteur-fictif-b", "(prompt partiel)",
                    "https://example.org/posts/cristal", "https://example.org/remakes/cristal"):
        assert attendu in b, attendu
    extrait = re.search(r"^\s+prompt : (.*?)(?: \(prompt partiel\))?$", b, re.M).group(1)
    assert 0 < len(extrait) <= 240
    assert PROMPT_LONG not in out, "le prompt complet n'est pas affiché par chercher"


def test_sortie_texte_avec_titre_sans_marque_partielle(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "aurora", source=source, cache=cache)
    b = bloc(out, "fictif-aurore")
    assert b.startswith("1. Particle aurora")
    assert "(prompt partiel)" not in b
    assert "canvas, particles" in b and "motion" in b
    assert "A slow aurora of glowing particles" in b                  # extrait court : entier
    assert "skillry" not in b.lower(), "pas de lien skillry quand l'entrée n'en a pas"
    assert "https://example.org/posts/aurore" in b


def test_extrait_tronque_a_240_caracteres_exactement(capsys, source, tmp_path, cache):
    entrees = entrees_fictives()
    entrees[0]["prompt"] = "mot " * 200
    fichier = tmp_path / "long.json"
    fichier.write_text(json.dumps(entrees), encoding="utf-8")
    code, out, _ = lancer(capsys, "chercher", "mot", source=fichier, cache=cache)
    extrait = re.search(r"^\s+prompt : (.*)$", bloc(out, "fictif-aurore"), re.M).group(1)
    assert len(extrait) == 240 and extrait.endswith("…")


def test_sortie_json_de_chercher(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "slow camera particles", source=source, cache=cache, format="json")
    assert code == 0
    donnees = json.loads(out)
    assert [r["slug"] for r in donnees] == ["fictif-logo", "fictif-aurore", "fictif-cristal", "fictif-jeu"]
    premier = donnees[0]
    for cle in ("score", "slug", "title", "category", "tech_tags", "author", "author_url", "post_url", "skillry_url",
                "added", "has_remake", "prompt_partial", "extrait"):
        assert cle in premier, cle
    cristal = next(r for r in donnees if r["slug"] == "fictif-cristal")
    assert cristal["prompt_partial"] is True and len(cristal["extrait"]) <= 240
    assert cristal["title"] is None
    assert "prompt" not in cristal, "chercher ne diffuse pas les prompts entiers"


def test_json_sans_resultat_est_une_liste_vide_et_code_1(capsys, source, cache):
    code, out, _ = lancer(capsys, "chercher", "submarine", source=source, cache=cache, format="json")
    assert code == 1 and json.loads(out) == []


# ------------------------------------------------------------------ montrer, categories

def test_montrer_entree_complete(capsys, source, cache):
    code, out, _ = lancer(capsys, "montrer", "fictif-cristal", source=source, cache=cache)
    assert code == 0
    for attendu in ("fictif-cristal", "3d", "threejs, shader", "auteur-fictif-b", "https://example.org/auteur-fictif-b",
                    "https://example.org/posts/cristal", "https://example.org/remakes/cristal",
                    "https://example.org/posters/cristal.webp", "2026-09-20", "(prompt partiel)"):
        assert attendu in out, attendu
    assert PROMPT_LONG.strip() in out, "montrer affiche le prompt en entier"


def test_montrer_sans_marque_partielle_ni_skillry_quand_l_entree_n_en_a_pas(capsys, source, cache):
    code, out, _ = lancer(capsys, "montrer", "fictif-aurore", source=source, cache=cache)
    assert code == 0 and "(prompt partiel)" not in out and "skillry" not in out.lower()
    assert "A slow aurora of glowing particles" in out and "https://example.org/posters/aurore.webp" in out


def test_montrer_json(capsys, source, cache):
    code, out, _ = lancer(capsys, "montrer", "fictif-aurore", source=source, cache=cache, format="json")
    assert code == 0
    assert json.loads(out) == entrees_fictives()[0]


def test_montrer_slug_inconnu_code_1(capsys, source, cache):
    code, out, err = lancer(capsys, "montrer", "n-existe-pas", source=source, cache=cache)
    assert code == 1 and "n-existe-pas" in err and "Traceback" not in err


def test_categories(capsys, source, cache):
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 0
    assert re.search(r"^\s*motion : 2$", out, re.M)
    for categorie in ("3d", "explainer", "interactive"):
        assert re.search(rf"^\s*{categorie} : 1$", out, re.M), categorie
    for tech, nombre in (("canvas", 2), ("svg", 2), ("gsap", 2), ("particles", 1), ("audio", 1), ("threejs", 1)):
        assert re.search(rf"^\s*{tech} : {nombre}$", out, re.M), tech
    assert "5" in out.splitlines()[0]


def test_categories_json(capsys, source, cache):
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    donnees = json.loads(out)
    assert donnees["total"] == 5
    assert donnees["categories"] == {"motion": 2, "3d": 1, "explainer": 1, "interactive": 1}
    assert donnees["techs"]["canvas"] == 2 and donnees["techs"]["audio"] == 1


# ------------------------------------------------------------------ cache

def test_la_premiere_lecture_ecrit_le_cache_sans_residu(capsys, source, cache):
    code, _, err = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 0 and err == ""
    enveloppe = json.loads(cache.read_text(encoding="utf-8"))
    assert enveloppe["source"] == str(source.resolve())
    assert len(enveloppe["videos"]) == 5
    assert datetime.fromisoformat(enveloppe["recupere"]).tzinfo is not None
    assert [p.name for p in cache.parent.iterdir()] == [cache.name], "pas de fichier temporaire laissé"


def test_cache_frais_reutilise_sans_lire_la_source(capsys, source, cache):
    code, premiere, _ = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    source.unlink()                                                # la source n'existe plus
    code, seconde, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 0 and err == "" and seconde == premiere


def test_cache_frais_ne_relit_pas_la_source_meme_modifiee(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    entrees = entrees_fictives()[:1]
    source.write_text(json.dumps(entrees), encoding="utf-8")
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert json.loads(out)["total"] == 5


def test_rafraichir_force_la_relecture(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    source.write_text(json.dumps(entrees_fictives()[:2]), encoding="utf-8")
    code, out, err = lancer(capsys, "categories", "--rafraichir", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 2 and err == ""
    assert len(json.loads(cache.read_text(encoding="utf-8"))["videos"]) == 2


def test_rafraichir_en_echec_se_replie_sur_le_cache_avec_avertissement(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    source.unlink()
    code, out, err = lancer(capsys, "categories", "--rafraichir", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 5
    assert "avertissement" in err.lower()


def test_une_autre_source_n_utilise_pas_le_cache_d_une_premiere(capsys, source, cache, tmp_path):
    lancer(capsys, "categories", source=source, cache=cache)
    autre = tmp_path / "autre.json"
    autres = entrees_fictives()[:2]
    autres[0]["slug"] = "autre-un"
    autre.write_text(json.dumps(autres), encoding="utf-8")
    code, out, _ = lancer(capsys, "chercher", LARGE, source=autre, cache=cache)
    assert "autre-un" in slugs(out) and "fictif-logo" not in slugs(out)


def test_cache_perime_et_source_injoignable_avertit_et_sert_le_cache(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    vieillir_le_cache(cache, 30)
    source.unlink()
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-logo"]
    assert "avertissement" in err.lower() and "périmé" in err and "Traceback" not in err


def test_cache_de_6_jours_est_frais_cache_de_8_jours_est_perime(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    vieillir_le_cache(cache, 6)
    source.unlink()
    code, _, err = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 0 and err == ""
    vieillir_le_cache(cache, 8)
    code, _, err = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 0 and "avertissement" in err.lower()


def test_cache_perime_et_source_disponible_est_remplace(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    vieillir_le_cache(cache, 30)
    source.write_text(json.dumps(entrees_fictives()[:3]), encoding="utf-8")
    code, out, err = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert code == 0 and err == "" and json.loads(out)["total"] == 3
    age = datetime.now(timezone.utc) - datetime.fromisoformat(json.loads(cache.read_text(encoding="utf-8"))["recupere"])
    assert age < timedelta(minutes=5)


def test_ni_cache_ni_source_code_2(capsys, source, cache):
    source.unlink()
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 2 and out == ""
    assert err.startswith("ERREUR") and "Traceback" not in err
    assert not cache.exists()


def test_cache_illisible_est_ignore_puis_remplace(capsys, source, cache):
    cache.parent.mkdir(parents=True)
    cache.write_text("{pas du json", encoding="utf-8")
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-logo"] and "Traceback" not in err
    assert json.loads(cache.read_text(encoding="utf-8"))["videos"]


def test_cache_de_forme_inattendue_est_ignore(capsys, source, cache):
    cache.parent.mkdir(parents=True)
    for contenu in ('[1, 2]', '{"videos": "non"}', '{"source": 3, "recupere": 4, "videos": []}', '"texte"'):
        cache.write_text(contenu, encoding="utf-8")
        code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
        assert code == 0 and slugs(out) == ["fictif-logo"], contenu
        assert "Traceback" not in err


def test_horodatage_du_cache_illisible_compte_comme_perime(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    enveloppe = json.loads(cache.read_text(encoding="utf-8"))
    enveloppe["recupere"] = "hier soir"
    cache.write_text(json.dumps(enveloppe), encoding="utf-8")
    source.write_text(json.dumps(entrees_fictives()[:1]), encoding="utf-8")
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 1             # la source a été relue


def test_cache_non_ecrivable_n_empeche_pas_la_recherche(capsys, source, tmp_path):
    bloquant = tmp_path / "fichier-ordinaire"
    bloquant.write_text("x", encoding="utf-8")
    cache_impossible = bloquant / "sous-dossier" / "cache.json"     # le parent est un fichier
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache_impossible)
    assert code == 0 and slugs(out) == ["fictif-logo"]
    assert "avertissement" in err.lower() and "Traceback" not in err


def test_defauts_branches_sur_les_constantes_du_module(capsys, source, monkeypatch):
    monkeypatch.setattr(inspiration, "SOURCE_DEFAUT", str(source))
    code, out, _ = lancer(capsys, "categories", format="json")
    assert code == 0 and json.loads(out)["total"] == 5
    assert inspiration.CACHE_DEFAUT.is_file()


# ------------------------------------------------------------------ source invalide ou hostile

def test_json_invalide_code_2_sans_trace(capsys, source, cache):
    source.write_text("{pas du json", encoding="utf-8")
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 2 and out == ""
    assert err.startswith("ERREUR") and "Traceback" not in err and "JSON" in err
    assert not cache.exists(), "une source illisible n'écrit rien dans le cache"


def test_json_invalide_se_replie_sur_le_cache_sans_l_ecraser(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    vieillir_le_cache(cache, 30)
    avant = cache.read_bytes()
    source.write_text("<html>erreur 502</html>", encoding="utf-8")
    code, out, err = lancer(capsys, "chercher", "logo", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-logo"]
    assert "avertissement" in err.lower() and cache.read_bytes() == avant


@pytest.mark.parametrize("contenu", ['{"videos": []}', '[]', '["a", 1, null]', '"texte"', '42', '[{"title": "sans slug"}]'])
def test_forme_inattendue_ou_vide_code_2(capsys, source, cache, contenu):
    source.write_text(contenu, encoding="utf-8")
    code, out, err = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 2 and err.startswith("ERREUR") and "Traceback" not in err
    assert not cache.exists()


def test_une_source_vide_n_ecrase_pas_un_bon_cache(capsys, source, cache):
    lancer(capsys, "categories", source=source, cache=cache)
    avant = cache.read_bytes()
    source.write_text("[]", encoding="utf-8")
    code, out, err = lancer(capsys, "categories", "--rafraichir", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 5 and "avertissement" in err.lower()
    assert cache.read_bytes() == avant


def test_entrees_douteuses_ignorees_sans_planter(capsys, source, cache):
    brutes = entrees_fictives() + ["texte", 42, None, {"title": "sans slug"}, {"slug": ""}, {"slug": 7}]
    brutes.append({"slug": "fictif-nul", "title": None, "tech_tags": None, "prompt": None, "category": None,
                   "author": None, "added": None, "has_remake": None, "prompt_partial": None})
    source.write_text(json.dumps(brutes), encoding="utf-8")
    code, out, err = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 6 and "Traceback" not in err
    code, out, err = lancer(capsys, "montrer", "fictif-nul", source=source, cache=cache)
    assert code == 0 and "Traceback" not in err
    code, out, err = lancer(capsys, "chercher", LARGE, source=source, cache=cache)
    assert code == 0 and "fictif-nul" not in slugs(out)


def test_caracteres_de_controle_retires_de_l_affichage(capsys, source, cache):
    entrees = entrees_fictives()
    entrees[0]["prompt"] = "A slow \x1b[31maurora\x1b[0m\x07 with\ta tab\nand a line \u202ereversed"
    entrees[0]["title"] = "Particle\x1b]0;pirate\x07 aurora"
    entrees[0]["tech_tags"] = ["can\x1bvas"]
    source.write_text(json.dumps(entrees), encoding="utf-8")
    for commande in (("chercher", "aurora"), ("montrer", "fictif-aurore")):
        code, out, err = lancer(capsys, *commande, source=source, cache=cache)
        assert code == 0
        assert not re.search("[\x00-\x08\x0b-\x1f\x7f-\x9f\u202a-\u202e]", out), commande
    code, out, _ = lancer(capsys, "montrer", "fictif-aurore", source=source, cache=cache)
    assert "with\ta tab\nand a line" in out, "tabulations et retours à la ligne conservés dans montrer"
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert "canvas" in json.loads(out)["techs"]


def test_techs_non_textuels_ignores(capsys, source, cache):
    entrees = entrees_fictives()
    entrees[0]["tech_tags"] = ["canvas", 3, None, ["x"], "particles"]
    source.write_text(json.dumps(entrees), encoding="utf-8")
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["techs"]["canvas"] == 2


def test_decodage_tolerant_et_bom(capsys, source, cache):
    brut = json.dumps(entrees_fictives(), ensure_ascii=False).encode("utf-8")
    brut = brut.replace(b"glowing", b"glo\xffwing")                  # octet invalide dans un prompt
    source.write_bytes(b"\xef\xbb\xbf" + brut)                       # et un BOM
    code, out, err = lancer(capsys, "chercher", "aurora", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-aurore"] and "Traceback" not in err


def test_reponse_trop_volumineuse_refusee(capsys, source, cache, monkeypatch):
    monkeypatch.setattr(inspiration, "TAILLE_MAX", 200)
    code, out, err = lancer(capsys, "categories", source=source, cache=cache)
    assert code == 2 and "volumineu" in err and "Traceback" not in err
    assert not cache.exists()


@pytest.mark.parametrize("adresse", ["file:///etc/hosts", "ftp://127.0.0.1/videos.json", "gopher://x/y"])
def test_schemas_autres_que_http_refuses(capsys, cache, adresse):
    code, out, err = lancer(capsys, "categories", source=adresse, cache=cache)
    assert code == 2 and "http" in err and "Traceback" not in err


def test_aucun_prompt_ecrit_ailleurs_que_dans_le_cache(capsys, source, cache, tmp_path):
    fichiers_avant = {p for p in tmp_path.rglob("*") if p.is_file()}
    lancer(capsys, "chercher", "crystal", source=source, cache=cache)
    nouveaux = {p for p in tmp_path.rglob("*") if p.is_file()} - fichiers_avant
    assert nouveaux == {cache}


# ------------------------------------------------------------------ couche HTTP (serveur local)

@pytest.fixture
def serveur(monkeypatch):
    corps = json.dumps(entrees_fictives(), ensure_ascii=False).encode("utf-8")
    agents: list[str] = []

    class Gestionnaire(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            agents.append(self.headers.get("User-Agent", ""))
            if self.path == "/videos.json":
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(corps)))
                self.end_headers()
                self.wfile.write(corps)
            elif self.path == "/ftp":
                self.send_response(302)
                self.send_header("Location", "ftp://127.0.0.1:9/videos.json")
                self.end_headers()
            elif self.path == "/ailleurs":
                self.send_response(302)
                self.send_header("Location", "/videos.json")
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header("Content-Length", "0")
                self.end_headers()

    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), Gestionnaire)
    except OSError:
        pytest.skip("impossible d'ouvrir un serveur local")
    monkeypatch.setenv("no_proxy", "127.0.0.1")
    monkeypatch.setenv("NO_PROXY", "127.0.0.1")
    fil = threading.Thread(target=httpd.serve_forever, daemon=True)
    fil.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", agents
    httpd.shutdown()
    httpd.server_close()


def test_lecture_http_avec_user_agent(capsys, cache, serveur):
    base, agents = serveur
    code, out, err = lancer(capsys, "chercher", "logo", source=f"{base}/videos.json", cache=cache)
    assert code == 0 and slugs(out) == ["fictif-logo"] and err == ""
    assert agents and agents[0].startswith("marketing-cockpit-template"), agents
    assert json.loads(cache.read_text(encoding="utf-8"))["source"] == f"{base}/videos.json"


def test_redirection_http_suivie(capsys, cache, serveur):
    base, _ = serveur
    code, out, _ = lancer(capsys, "categories", source=f"{base}/ailleurs", cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 5


def test_redirection_vers_ftp_refusee(capsys, cache, serveur):
    base, _ = serveur
    code, out, err = lancer(capsys, "categories", source=f"{base}/ftp", cache=cache)
    assert code == 2 and "ERREUR" in err and "redirection refusée" in err and "Traceback" not in err


def test_http_404_et_serveur_absent(capsys, cache, serveur):
    base, _ = serveur
    code, _, err = lancer(capsys, "categories", source=f"{base}/absent.json", cache=cache)
    assert code == 2 and "404" in err and "Traceback" not in err
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port_ferme = s.getsockname()[1]
    code, _, err = lancer(capsys, "categories", source=f"http://127.0.0.1:{port_ferme}/x.json", cache=cache)
    assert code == 2 and "ERREUR" in err and "Traceback" not in err


def test_http_en_echec_se_replie_sur_le_cache_de_la_meme_adresse(capsys, cache, serveur):
    base, _ = serveur
    lancer(capsys, "categories", source=f"{base}/videos.json", cache=cache)
    # Une autre adresse en échec : le cache d'une adresse différente n'est pas un repli valable.
    code, _, err = lancer(capsys, "chercher", "logo", source=f"{base}/absent.json", cache=cache)
    assert code == 2 and "404" in err
    # La même adresse en échec : repli sur le cache périmé, avec avertissement qui nomme la cause.
    enveloppe = json.loads(cache.read_text(encoding="utf-8"))
    enveloppe["source"] = f"{base}/absent.json"
    cache.write_text(json.dumps(enveloppe), encoding="utf-8")
    vieillir_le_cache(cache, 30)
    code, out, err = lancer(capsys, "chercher", "logo", source=f"{base}/absent.json", cache=cache)
    assert code == 0 and slugs(out) == ["fictif-logo"]
    assert "404" in err and "avertissement" in err.lower()


# ------------------------------------------------------------------ ligne de commande réelle

def test_script_en_sous_processus(source, cache):
    commun = [sys.executable, "-I", str(CLI)]
    ok = subprocess.run([*commun, "chercher", "logo", "--source", str(source), "--cache", str(cache)],
                        capture_output=True, text=True)
    assert ok.returncode == 0 and "fictif-logo" in ok.stdout and ok.stderr == ""
    rien = subprocess.run([*commun, "chercher", "submarine", "--source", str(source), "--cache", str(cache)],
                          capture_output=True, text=True)
    assert rien.returncode == 1
    usage = subprocess.run([*commun, "chercher"], capture_output=True, text=True)     # requête vide : avant tout accès
    assert usage.returncode == 2 and "Traceback" not in usage.stderr
    aucune = subprocess.run([*commun], capture_output=True, text=True)
    assert aucune.returncode == 2 and "Traceback" not in aucune.stderr
    hors_ligne = subprocess.run([*commun, "categories", "--source", str(source.parent / "absent.json"),
                                 "--cache", str(cache.parent / "autre.json")], capture_output=True, text=True)
    assert hors_ligne.returncode == 2 and "Traceback" not in hors_ligne.stderr and "ERREUR" in hors_ligne.stderr


# ------------------------------------------------------------------ revue finale : robustesse

@pytest.mark.parametrize("adresse", ["http://127.0.0.1:abc/videos.json", "https://example.org:99999/videos.json"])
def test_port_malforme_erreur_propre_code_2(capsys, cache, adresse):
    code, out, err = lancer(capsys, "categories", source=adresse, cache=cache)
    assert code == 2 and err.startswith("ERREUR") and "port" in err
    assert not cache.exists()


def test_surrogate_isole_ni_trace_ni_fichier_temporaire(capsys, source, cache):
    brut = json.dumps(entrees_fictives())             # ensure_ascii : les \uXXXX restent échappés dans la source
    assert "Particle aurora" in brut
    source.write_text(brut.replace("Particle aurora", "Particle \\ud83d aurora"), encoding="utf-8")
    code, out, err = lancer(capsys, "chercher", "aurora", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-aurore"] and "Traceback" not in err
    assert cache.exists() and not list(cache.parent.glob("*.tmp"))
    code, out, err = lancer(capsys, "montrer", "fictif-aurore", source=source, cache=cache)
    assert code == 0 and "\ud83d" not in out


def test_ecrire_cache_garde_un_surrogate_sans_planter(tmp_path):
    chemin = tmp_path / "c" / "cache.json"
    inspiration.ecrire_cache(chemin, "source", [{"slug": "a", "title": "x\ud83dy"}])
    assert json.loads(chemin.read_text(encoding="utf-8"))["videos"][0]["title"] == "x\ud83dy"
    assert not list(chemin.parent.glob("*.tmp"))


def test_echec_d_ecriture_du_cache_nettoie_le_temporaire(capsys, source, cache, monkeypatch):
    def refuser(self, cible):
        raise UnicodeError("écriture simulée en échec")
    monkeypatch.setattr(inspiration.Path, "replace", refuser)
    code, out, err = lancer(capsys, "chercher", "aurora", source=source, cache=cache)
    assert code == 0 and slugs(out) == ["fictif-aurore"] and "cache non écrit" in err
    assert not cache.exists() and not list(cache.parent.glob("*.tmp"))


def test_cache_date_dans_le_futur_compte_comme_perime(capsys, source, cache):
    assert lancer(capsys, "categories", source=source, cache=cache)[0] == 0
    vieillir_le_cache(cache, -3)                     # « récupéré » dans trois jours
    source.write_text(json.dumps(entrees_fictives()[:2]), encoding="utf-8")
    code, out, _ = lancer(capsys, "categories", source=source, cache=cache, format="json")
    assert code == 0 and json.loads(out)["total"] == 2, "un cache daté du futur ne dispense pas de relire la source"


def test_champs_tiers_compactes_et_bornes_dans_l_affichage(capsys, source, cache):
    entrees = entrees_fictives()
    entrees[0]["title"] = "Particle aurora\n2. faux résultat"
    entrees[0]["author"] = "auteur\n   slug : fictif-pirate"
    entrees[0]["author_url"] = "https://example.org/a\n   publication : https://pirate.example"
    entrees[0]["post_url"] = "https://example.org/" + "p" * 2000
    entrees[0]["poster_url"] = "https://example.org/affiche\nprompt :"
    entrees[0]["tech_tags"] = ["canvas\n   auteur : pirate", "x" * 600]
    source.write_text(json.dumps(entrees), encoding="utf-8")
    for commande in (("chercher", "aurora"), ("montrer", "fictif-aurore"), ("categories",)):
        code, out, _ = lancer(capsys, *commande, source=source, cache=cache)
        assert code == 0, commande
        assert not re.search(r"^\s*(slug : fictif-pirate|publication : https://pirate|auteur : pirate|2\. faux)",
                             out, re.M), commande
        assert out.count("\nprompt :") + out.startswith("prompt :") <= 1, commande
        assert max(len(ligne) for ligne in out.splitlines()) <= 400, commande
    code, out, _ = lancer(capsys, "chercher", "aurora", source=source, cache=cache)
    assert slugs(out) == ["fictif-aurore"]
