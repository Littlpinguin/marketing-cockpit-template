"""Tests du corpus documentaire (08-video/scripts/corpus.py et paquet corpus_documentaire).

Aucun accès réseau : la couche reseau est remplacée par des réponses fictives.
Aucune dépendance lourde : l'index et la recherche (tâche 7) utilisent un
encodeur factice.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import urllib.error
from http.client import IncompleteRead
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "08-video" / "scripts"
CLI = SCRIPTS / "corpus.py"
sys.path.insert(0, str(SCRIPTS))

from corpus_documentaire import construire as cons  # noqa: E402
from corpus_documentaire import credits, licences, reseau, sources  # noqa: E402
from corpus_documentaire.modeles import Resultat  # noqa: E402
from corpus_documentaire.sources.base import Source  # noqa: E402

requiert_ffmpeg = pytest.mark.skipif(not shutil.which("ffmpeg"), reason="ffmpeg absent")


def _charger_cli():
    """corpus.py en module (pour tester les commandes sans sous-processus)."""
    spec = importlib.util.spec_from_file_location("corpus_cli", CLI)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


corpus_cli = _charger_cli()


# ------------------------------------------------------------------ licences

@pytest.mark.parametrize("brute, attendue", [
    ("Public Domain", "domaine-public"),
    ("PD-USGov-NASA", "domaine-public"),
    ("http://creativecommons.org/publicdomain/mark/1.0/", "domaine-public"),
    ("https://creativecommons.org/publicdomain/zero/1.0/", "cc0"),
    ("CC0", "cc0"),
    ("CC BY 3.0", "cc-by"),
    ("https://creativecommons.org/licenses/by/4.0/", "cc-by"),
    ("CC BY-SA 4.0", "cc-by-sa"),
    ("cc by-nc-sa 2.0", "cc-by-nc-sa"),
    ("http://creativecommons.org/licenses/by-nc/3.0/", "cc-by-nc"),
    ("pexels", "pexels"),
    ("", "inconnue"),
    (None, "inconnue"),
    ("All rights reserved", "inconnue"),
])
def test_normaliser_licence(brute, attendue):
    assert licences.normaliser(brute) == attendue


def test_licences_admises_et_attribution():
    assert licences.admise("cc-by", licences.ADMISES_DEFAUT)
    assert not licences.admise("cc-by-sa", licences.ADMISES_DEFAUT)
    assert not licences.admise("inconnue", licences.ADMISES_DEFAUT)
    assert licences.attribution_exigee("cc-by") and not licences.attribution_exigee("cc0")


# ------------------------------------------------------------------ thème

THEME = """
nom = "savoir-faire"
sources = ["archive", "nasa"]
par_requete = 2
duree_max = 60

[[emplacements]]
id = "ouverture"
description = "mains d'artisan qui travaillent le bois, gros plan"
requetes = ["woodworking hands", "carpenter workshop"]
"""


def test_charger_theme(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME, encoding="utf-8")
    theme = cons.charger_theme(chemin)
    assert theme.nom == "savoir-faire" and theme.sources == ["archive", "nasa"]
    assert theme.licences == licences.ADMISES_DEFAUT
    assert theme.emplacements[0].requetes == ["woodworking hands", "carpenter workshop"]


@pytest.mark.parametrize("remplacement, message", [
    (('["archive", "nasa"]', '["youtube"]'), "source inconnue"),
    (('duree_max = 60', 'duree_max = 60\nlicences = ["cc-by", "toutes"]'), "licence inconnue"),
    (('requetes = ["woodworking hands", "carpenter workshop"]', 'requetes = []'), "requetes"),
    (('nom = "savoir-faire"', 'nom = "Savoir Faire"'), "nom"),
])
def test_theme_invalide(tmp_path, remplacement, message):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME.replace(*remplacement), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        cons.charger_theme(chemin)


def test_theme_d_exemple_livre_est_valide():
    theme = cons.charger_theme(REPO / "08-video" / "corpus" / "themes" / "exemple-savoir-faire.toml")
    assert theme.emplacements and all(e.requetes for e in theme.emplacements)


# ------------------------------------------------------------------ sources (réponses fictives)

def _faux_reseau(monkeypatch, reponses: dict):
    appels = []

    def obtenir_json(url, params=None, entetes=None, delai=30):
        appels.append((url, params, entetes))
        for prefixe, reponse in reponses.items():
            if url.startswith(prefixe):
                return reponse(url, params) if callable(reponse) else reponse
        raise AssertionError(f"URL inattendue : {url}")

    monkeypatch.setattr(reseau, "obtenir_json", obtenir_json)
    return appels


def test_pexels(monkeypatch):
    appels = _faux_reseau(monkeypatch, {"https://api.pexels.com/videos/search": {"videos": [{
        "id": 42, "url": "https://www.pexels.com/video/hands-working-wood-42/", "duration": 12,
        "user": {"name": "Ana"},
        "video_files": [
            {"file_type": "video/mp4", "width": 3840, "height": 2160, "link": "https://p/4k.mp4"},
            {"file_type": "video/mp4", "width": 1920, "height": 1080, "link": "https://p/hd.mp4"},
            {"file_type": "video/mp4", "width": 640, "height": 360, "link": "https://p/sd.mp4"}]}]}})
    resultats = sources.SOURCES["pexels"]("cle-secrete").rechercher("hands wood", 3)
    assert len(resultats) == 1
    r = resultats[0]
    assert (r.source, r.id, r.url_fichier, r.licence, r.auteur, r.duree) == \
        ("pexels", "42", "https://p/hd.mp4", "pexels", "Ana", 12.0)
    assert r.titre == "hands working wood"
    assert appels[0][2] == {"Authorization": "cle-secrete"}


def test_pixabay(monkeypatch):
    _faux_reseau(monkeypatch, {"https://pixabay.com/api/videos/": {"hits": [{
        "id": 7, "pageURL": "https://pixabay.com/videos/id-7/", "tags": "forge, metal", "user": "Bo",
        "duration": 20, "videos": {"large": {"url": ""}, "medium": {"url": "https://x/m.mp4"}}}]}})
    r = sources.SOURCES["pixabay"]("cle").rechercher("forge", 3)[0]
    assert (r.url_fichier, r.licence, r.titre, r.duree) == ("https://x/m.mp4", "pixabay", "forge, metal", 20.0)


def test_archive(monkeypatch):
    _faux_reseau(monkeypatch, {
        "https://archive.org/advancedsearch.php": {"response": {"docs": [
            {"identifier": "film_1950", "title": "Le métier", "creator": ["Studio A"],
             "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"}]}},
        "https://archive.org/metadata/film_1950": {"files": [
            {"name": "film_1950.mp4", "size": "50000000", "length": "00:02:30"},
            {"name": "film_1950_512kb.mp4", "size": "9000000", "length": "150.0"},
            {"name": "film_1950.ogv", "size": "40000000"}]}})
    r = sources.SOURCES["archive"]().rechercher("craft", 2)[0]
    assert r.url_fichier == "https://archive.org/download/film_1950/film_1950.mp4"
    assert (r.licence, r.auteur, r.duree) == ("domaine-public", "Studio A", 150.0)


def test_wikimedia(monkeypatch):
    _faux_reseau(monkeypatch, {"https://commons.wikimedia.org/w/api.php": {"query": {"pages": {
        "9": {"pageid": 9, "index": 1, "title": "File:Forge.webm", "imageinfo": [{
            "url": "https://upload.wikimedia.org/forge.webm", "descriptionurl": "https://commons/forge",
            "duration": 33.5, "extmetadata": {
                "LicenseShortName": {"value": "CC BY-SA 4.0"},
                "Artist": {"value": '<a href="x">Jean <b>Forgeron</b></a>'},
                "ObjectName": {"value": "Forge"}}}]}}}}})
    r = sources.SOURCES["wikimedia"]().rechercher("forge", 2)[0]
    assert (r.licence, r.auteur, r.titre, r.duree) == ("cc-by-sa", "Jean Forgeron", "Forge", 33.5)
    assert r.url_fichier.endswith(".webm")


def test_nasa(monkeypatch):
    _faux_reseau(monkeypatch, {
        "https://images-api.nasa.gov/search": {"collection": {"items": [{
            "href": "https://images-assets.nasa.gov/video/ID1/collection.json",
            "data": [{"nasa_id": "ID1", "title": "Launch", "center": "KSC"}]}]}},
        "https://images-assets.nasa.gov/video/ID1/collection.json": [
            "http://images-assets.nasa.gov/video/ID1/ID1~orig.mp4",
            "http://images-assets.nasa.gov/video/ID1/ID1~medium.mp4",
            "http://images-assets.nasa.gov/video/ID1/ID1.srt"]})
    r = sources.SOURCES["nasa"]().rechercher("launch", 2)[0]
    assert r.url_fichier == "https://images-assets.nasa.gov/video/ID1/ID1~medium.mp4"
    assert (r.licence, r.auteur) == ("domaine-public", "KSC")


def test_source_sans_cle_indisponible():
    ok, raison = sources.SOURCES["pexels"](None).disponible()
    assert not ok and "PEXELS_API_KEY" in raison


def test_erreur_http_ne_revele_pas_la_cle(monkeypatch):
    def refuser(requete, timeout=0):
        raise urllib.error.HTTPError(requete.full_url, 429, "Too Many Requests", {}, None)

    monkeypatch.setattr(reseau.urllib.request, "urlopen", refuser)
    with pytest.raises(reseau.ErreurReseau) as erreur:
        reseau.obtenir_json("https://pixabay.com/api/videos/", {"key": "cle-tres-secrete", "q": "x"})
    assert "429" in str(erreur.value) and "cle-tres-secrete" not in str(erreur.value)


# ------------------------------------------------------------------ constitution

class SourceFactice(Source):
    nom = "factice"

    def __init__(self, resultats=None, erreur=None):
        super().__init__(None)
        self._resultats, self._erreur = resultats or [], erreur

    def rechercher(self, requete, n):
        if self._erreur:
            raise reseau.ErreurReseau(self._erreur)
        return [Resultat(**{**r.fiche(), "requete": requete}) for r in self._resultats]   # ignore n : tout est rendu


class SourceACle(SourceFactice):
    nom = "acle"
    cle_env = "ACLE_API_KEY"


def _resultat(ident, licence="cc0", duree=10.0):
    return Resultat(source="factice", id=ident, titre=f"Titre {ident}", auteur="Auteur",
                    page=f"https://exemple/{ident}", url_fichier=f"https://exemple/{ident}.mp4",
                    licence=licence, licence_brute=licence, duree=duree)


def _theme(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME.replace('["archive", "nasa"]', '["archive"]'), encoding="utf-8")
    return cons.charger_theme(chemin)


def _telecharger(url, destination):
    destination.write_bytes(b"video")
    return destination


def test_construire_filtre_et_reprend(tmp_path):
    theme = _theme(tmp_path)
    bonne = SourceFactice([_resultat("a"), _resultat("b", licence="cc-by-sa"), _resultat("c", duree=300)])
    dossier = tmp_path / "corpus"
    rapport = cons.construire(theme, dossier, [bonne, SourceFactice(erreur="HTTP 500 sur https://x"),
                                               SourceACle()], telecharger=_telecharger)
    assert rapport.telecharges == 1
    assert rapport.ecartes_licence == 2 and rapport.ecartes_duree == 2   # deux requêtes
    assert any("HTTP 500" in e for e in rapport.erreurs)
    assert any("ACLE_API_KEY" in s for s in rapport.sources_ignorees)
    fiche = json.loads((dossier / "clips" / "factice-a.json").read_text(encoding="utf-8"))
    assert fiche["emplacement"] == "ouverture" and fiche["fichier"] == "factice-a.mp4"
    assert fiche["attribution_exigee"] is False
    encore = cons.construire(theme, dossier, [bonne], telecharger=_telecharger)
    assert encore.telecharges == 0 and encore.deja_presents >= 1


def test_construire_convertit_le_webm(tmp_path):
    theme = _theme(tmp_path)
    webm = _resultat("w")
    webm.url_fichier = "https://exemple/w.webm"
    convertis = []

    def convertir(source, cible):
        convertis.append((source.name, cible.name))
        cible.write_bytes(b"mp4")
        source.unlink()
        return cible

    cons.construire(theme, tmp_path / "c", [SourceFactice([webm])], telecharger=_telecharger,
                    convertir=convertir)
    assert convertis == [("factice-w.webm", "factice-w.mp4")]
    assert (tmp_path / "c" / "clips" / "factice-w.mp4").exists()


# ------------------------------------------------------------------ crédits et CLI

def _corpus_pret(tmp_path) -> Path:
    dossier = tmp_path / "corpus" / "savoir-faire"
    (dossier / "clips").mkdir(parents=True)
    (dossier / "theme.toml").write_text(THEME, encoding="utf-8")
    for ident, licence in (("a", "cc-by"), ("b", "domaine-public")):
        r = _resultat(ident, licence=licence)
        (dossier / "clips" / f"factice-{ident}.mp4").write_bytes(b"x")
        (dossier / "clips" / f"factice-{ident}.json").write_text(json.dumps(
            {**r.fiche(), "fichier": f"factice-{ident}.mp4",
             "attribution_exigee": licences.attribution_exigee(licence)}), encoding="utf-8")
    return dossier


def test_credits(tmp_path):
    dossier = _corpus_pret(tmp_path)
    texte = credits.ecrire_credits(dossier).read_text(encoding="utf-8")
    assert "Titre a" in texte and "CC BY" in texte and "domaine public" in texte
    assert "Attribution obligatoire" in texte
    selection = dossier / "selections.json"
    selection.write_text(json.dumps({"ouverture": [{"clip": "factice-b.mp4", "t": 1.0, "score": 0.3}]}))
    texte = credits.ecrire_credits(dossier, selection).read_text(encoding="utf-8")
    assert "Titre b" in texte and "Titre a" not in texte


def _cli(*args, env=None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(CLI), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env={**os.environ, **(env or {})})


def test_cli_list_et_credits(tmp_path):
    _corpus_pret(tmp_path)
    racine = str(tmp_path / "corpus")
    res = _cli("list", "savoir-faire", "--racine", racine)
    assert res.returncode == 0, res.stderr
    assert "2 clip" in res.stdout and "cc-by" in res.stdout
    assert _cli("credits", "savoir-faire", "--racine", racine).returncode == 0
    assert _cli("list", "absent", "--racine", racine).returncode == 2


def test_cli_build_sans_source_active_echoue(tmp_path):
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["pexels"]'), encoding="utf-8")
    res = _cli("build", str(theme), "--racine", str(tmp_path / "corpus"), env={"PEXELS_API_KEY": ""})
    assert res.returncode == 1 and "PEXELS_API_KEY" in res.stdout + res.stderr


# ------------------------------------------------------------------ durcissement : thème

@pytest.mark.parametrize("remplacement, message", [
    (('nom = "savoir-faire"', 'nom = 12'), "nom"),
    (('par_requete = 2', 'par_requete = "beaucoup"'), "par_requete"),
    (('par_requete = 2', 'par_requete = 0'), "par_requete"),
    (('duree_max = 60', 'duree_max = "soixante"'), "duree_max"),
    (('duree_max = 60', 'duree_max = -5'), "duree_max"),
    (('sources = ["archive", "nasa"]', 'sources = "archive"'), "sources"),
    (('sources = ["archive", "nasa"]', 'sources = []'), "sources"),
    (('duree_max = 60', 'duree_max = 60\nlicences = "cc0"'), "licences"),
    (('duree_max = 60', 'duree_max = 60\nlicences = []'), "licences"),
    (('id = "ouverture"', 'id = 3'), "exige un « id »"),
    (('requetes = ["woodworking hands", "carpenter workshop"]', 'requetes = "bois"'), "requetes"),
])
def test_theme_invalide_sans_trace(tmp_path, remplacement, message):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME.replace(*remplacement), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        cons.charger_theme(chemin)


def test_theme_toml_invalide(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME.replace('nom = "savoir-faire"', 'nom = '), encoding="utf-8")
    with pytest.raises(ValueError):
        cons.charger_theme(chemin)


def test_theme_emplacements_mal_formes(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME.split("[[emplacements]]")[0] + 'emplacements = ["x"]\n', encoding="utf-8")
    with pytest.raises(ValueError, match="emplacement"):
        cons.charger_theme(chemin)


def test_theme_emplacement_en_double(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_text(THEME + THEME[THEME.index("[[emplacements]]"):], encoding="utf-8")
    with pytest.raises(ValueError, match="en double"):
        cons.charger_theme(chemin)


def test_theme_utf8_invalide(tmp_path):
    chemin = tmp_path / "t.toml"
    chemin.write_bytes(b'nom = "\xff\xfe"')
    with pytest.raises(ValueError):
        cons.charger_theme(chemin)


# ------------------------------------------------------------------ durcissement : réseau

class _Reponse(io.BytesIO):
    pass


def _urlopen_qui_leve(erreur):
    def urlopen(requete, timeout=0):
        raise erreur
    return urlopen


@pytest.mark.parametrize("erreur", [
    ConnectionResetError("coupure"),
    IncompleteRead(b"abc"),
    TimeoutError("délai"),
    urllib.error.URLError("hôte introuvable"),
])
def test_obtenir_json_traduit_les_erreurs_de_connexion(monkeypatch, erreur):
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_qui_leve(erreur))
    with pytest.raises(reseau.ErreurReseau) as err:
        reseau.obtenir_json("https://exemple.org/api", {"key": "cle-tres-secrete"})
    assert "cle-tres-secrete" not in str(err.value) and "exemple.org/api" in str(err.value)


@pytest.mark.parametrize("corps", [b"pas du json", b"\xff\xfe\x00"])
def test_obtenir_json_reponse_illisible(monkeypatch, corps):
    monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0: _Reponse(corps))
    with pytest.raises(reseau.ErreurReseau):
        reseau.obtenir_json("https://exemple.org/api")


def test_obtenir_json_ok(monkeypatch):
    monkeypatch.setattr(reseau, "PAUSE", 0)
    monkeypatch.setattr(reseau.urllib.request, "urlopen",
                        lambda requete, timeout=0: _Reponse(b'{"a": 1}'))
    assert reseau.obtenir_json("https://exemple.org/api") == {"a": 1}


def test_telecharger_ecrit_le_fichier_sans_reste(tmp_path, monkeypatch):
    monkeypatch.setattr(reseau, "PAUSE", 0)
    monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0: _Reponse(b"video"))
    cible = tmp_path / "clip.mp4"
    assert reseau.telecharger("https://exemple.org/clip.mp4", cible) == cible
    assert cible.read_bytes() == b"video"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["clip.mp4"]


@pytest.mark.parametrize("erreur", [
    urllib.error.HTTPError("https://exemple.org/f.mp4?jeton=secret", 403, "Forbidden", {}, None),
    ConnectionResetError("coupure"),
    IncompleteRead(b"abc"),
])
def test_telecharger_nettoie_et_ne_revele_pas_les_parametres(tmp_path, monkeypatch, erreur):
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_qui_leve(erreur))
    with pytest.raises(reseau.ErreurReseau) as err:
        reseau.telecharger("https://exemple.org/f.mp4?jeton=secret", tmp_path / "f.mp4")
    assert "secret" not in str(err.value)
    assert list(tmp_path.iterdir()) == []


def test_telecharger_interrompu_en_cours_de_route_ne_laisse_rien(tmp_path, monkeypatch):
    class Coupee(io.BytesIO):
        def read(self, taille=-1):
            raise ConnectionResetError("coupure")

    monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0: Coupee(b"x"))
    with pytest.raises(reseau.ErreurReseau):
        reseau.telecharger("https://exemple.org/f.mp4", tmp_path / "f.mp4")
    assert list(tmp_path.iterdir()) == []


def test_telecharger_refuse_un_fichier_vide(tmp_path, monkeypatch):
    monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0: _Reponse(b""))
    with pytest.raises(reseau.ErreurReseau, match="vide"):
        reseau.telecharger("https://exemple.org/f.mp4", tmp_path / "f.mp4")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("url", ["file:///etc/hosts", "ftp://exemple.org/f.mp4", "gopher://x/y", "pas une url"])
def test_reseau_refuse_les_schemas_autres_que_http(tmp_path, monkeypatch, url):
    def interdit(requete, timeout=0):
        raise AssertionError("urlopen ne doit pas être appelé")

    monkeypatch.setattr(reseau.urllib.request, "urlopen", interdit)
    with pytest.raises(reseau.ErreurReseau, match="http"):
        reseau.telecharger(url, tmp_path / "f.mp4")
    with pytest.raises(reseau.ErreurReseau, match="http"):
        reseau.obtenir_json(url)
    assert list(tmp_path.iterdir()) == []


# ------------------------------------------------------------------ durcissement : sources et constitution

def test_archive_tolere_des_metadonnees_mal_formees(monkeypatch):
    _faux_reseau(monkeypatch, {
        "https://archive.org/advancedsearch.php": {"response": {"docs": [
            {"identifier": "f1", "title": "Un", "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"}]}},
        "https://archive.org/metadata/f1": {"files": [
            {"name": "f1.mp4", "size": "inconnue", "length": "00:xx:30"},     # taille illisible : écarté
            {"name": "f1_petit.mp4", "size": "9000000", "length": "00:xx:30"}]}})
    r = sources.SOURCES["archive"]().rechercher("x", 2)[0]
    assert r.url_fichier.endswith("f1_petit.mp4") and r.duree is None


def test_valeurs_non_finies_ne_sont_pas_des_durees(monkeypatch):
    _faux_reseau(monkeypatch, {"https://pixabay.com/api/videos/": {"hits": [{
        "id": 1, "tags": "t", "user": "u", "duration": "nan", "videos": {"small": {"url": "https://x/s.mp4"}}}]}})
    assert sources.SOURCES["pixabay"]("cle").rechercher("x", 3)[0].duree is None


class SourceMalformee(SourceFactice):
    nom = "malformee"

    def rechercher(self, requete, n):
        return [{"pas": "un résultat"}["absent"]]


def test_une_reponse_inattendue_ne_bloque_pas_les_autres_sources(tmp_path):
    rapport = cons.construire(_theme(tmp_path), tmp_path / "c",
                              [SourceMalformee(), SourceFactice([_resultat("a")])], telecharger=_telecharger)
    assert rapport.telecharges == 1
    assert any("malformee" in e and "réponse inattendue" in e for e in rapport.erreurs)


def test_un_echec_de_telechargement_ne_bloque_pas_les_autres_clips(tmp_path):
    def telecharger(url, destination):
        if url.endswith("/a.mp4"):
            raise OSError("disque plein")
        return _telecharger(url, destination)

    rapport = cons.construire(_theme(tmp_path), tmp_path / "c",
                              [SourceFactice([_resultat("a"), _resultat("b")])], telecharger=telecharger)
    assert rapport.telecharges == 1
    assert any("factice-a" in e and "disque plein" in e for e in rapport.erreurs)
    assert not (tmp_path / "c" / "clips" / "factice-a.json").exists()
    assert (tmp_path / "c" / "clips" / "factice-b.json").exists()


def test_un_echec_de_conversion_ne_laisse_pas_de_fiche(tmp_path):
    webm = _resultat("w")
    webm.url_fichier = "https://exemple/w.webm"

    def convertir(source, cible):
        raise cons.ErreurConversion("ffmpeg introuvable")

    rapport = cons.construire(_theme(tmp_path), tmp_path / "c", [SourceFactice([webm])],
                              telecharger=_telecharger, convertir=convertir)
    assert rapport.telecharges == 0 and any("ffmpeg introuvable" in e for e in rapport.erreurs)
    assert not list((tmp_path / "c" / "clips").glob("*.json"))


def test_une_fiche_sans_clip_ou_un_clip_sans_fiche_est_retelecharge(tmp_path):
    theme = _theme(tmp_path)
    source = SourceFactice([_resultat("a")])
    cons.construire(theme, tmp_path / "c", [source], telecharger=_telecharger)
    (tmp_path / "c" / "clips" / "factice-a.mp4").unlink()
    rapport = cons.construire(theme, tmp_path / "c", [source], telecharger=_telecharger)
    assert rapport.telecharges == 1 and rapport.deja_presents == 1       # 2 requêtes : refait puis présent


@requiert_ffmpeg
def test_conversion_reelle_en_mp4(tmp_path):
    source = tmp_path / "essai.mov"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc2=s=160x120:r=10:d=1", "-c:v", "mpeg4", str(source)], check=True)
    cible = cons.convertir_en_mp4(source, tmp_path / "essai.mp4")
    assert cible.exists() and cible.stat().st_size > 0 and not source.exists()


@requiert_ffmpeg
def test_conversion_en_echec_ne_laisse_pas_de_cible(tmp_path):
    source = tmp_path / "casse.webm"
    source.write_bytes(b"ce n'est pas une video")
    with pytest.raises(cons.ErreurConversion):
        cons.convertir_en_mp4(source, tmp_path / "casse.mp4")
    assert source.exists() and not (tmp_path / "casse.mp4").exists()


def test_conversion_interrompue_ne_laisse_pas_de_mp4_tronque(tmp_path, monkeypatch):
    options_vues = {}

    def faux_ffmpeg(commande, **options):
        options_vues.update(options)
        Path(commande[-1]).write_bytes(b"mp4 tronque")        # ffmpeg a commencé à écrire, puis échoué
        return subprocess.CompletedProcess(commande, 1, "", "Error while encoding \u00e9")

    monkeypatch.setattr(cons.shutil, "which", lambda nom: "/usr/bin/ffmpeg")
    monkeypatch.setattr(cons.subprocess, "run", faux_ffmpeg)
    source = tmp_path / "essai.webm"
    source.write_bytes(b"x")
    with pytest.raises(cons.ErreurConversion, match="Error while encoding"):
        cons.convertir_en_mp4(source, tmp_path / "essai.mp4")
    assert source.exists() and not (tmp_path / "essai.mp4").exists()
    assert options_vues["encoding"] == "utf-8" and options_vues["errors"] == "replace"   # sortie d'outil jamais fatale


def test_conversion_sans_ffmpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(cons.shutil, "which", lambda nom: None)
    source = tmp_path / "essai.webm"
    source.write_bytes(b"x")
    with pytest.raises(cons.ErreurConversion, match="ffmpeg"):
        cons.convertir_en_mp4(source, tmp_path / "essai.mp4")
    assert source.exists()


# ------------------------------------------------------------------ durcissement : crédits

def test_credits_une_ligne_par_clip_meme_avec_des_retours_a_la_ligne(tmp_path):
    dossier = _corpus_pret(tmp_path)
    fiche = dossier / "clips" / "factice-a.json"
    donnees = json.loads(fiche.read_text(encoding="utf-8"))
    donnees["titre"] = "Premier\nsecond\n\n- faux point de liste"
    donnees["auteur"] = ""
    fiche.write_text(json.dumps(donnees), encoding="utf-8")
    lignes = credits.ecrire_credits(dossier).read_text(encoding="utf-8").splitlines()
    assert sum(1 for ligne in lignes if ligne.startswith("- ")) == 2
    assert any("Premier second - faux point de liste" in ligne and "auteur non renseigné" in ligne
               for ligne in lignes)


def test_credits_refuse_une_selection_dont_un_clip_n_a_pas_de_fiche(tmp_path):
    dossier = _corpus_pret(tmp_path)
    selection = dossier / "selections.json"
    selection.write_text(json.dumps({"ouverture": [{"clip": "factice-b.mp4"}, {"clip": "factice-zzz.mp4"}]}))
    with pytest.raises(ValueError, match="factice-zzz.mp4"):
        credits.ecrire_credits(dossier, selection)
    assert not (dossier / "credits.md").exists()


@pytest.mark.parametrize("contenu", ["[]", '{"ouverture": "factice-a.mp4"}', '{"ouverture": [{"t": 1}]}',
                                     "pas du json", '{"ouverture": [3]}'])
def test_credits_refuse_une_selection_mal_formee(tmp_path, contenu):
    dossier = _corpus_pret(tmp_path)
    selection = dossier / "selections.json"
    selection.write_text(contenu, encoding="utf-8")
    with pytest.raises(ValueError, match="selections.json"):
        credits.ecrire_credits(dossier, selection)


def test_credits_refuse_un_corpus_ou_une_selection_vide(tmp_path):
    dossier = _corpus_pret(tmp_path)
    selection = dossier / "selections.json"
    selection.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="aucun clip"):
        credits.ecrire_credits(dossier, selection)
    vide = tmp_path / "vide"
    (vide / "clips").mkdir(parents=True)
    with pytest.raises(ValueError, match="aucun clip"):
        credits.ecrire_credits(vide)
    assert not (vide / "credits.md").exists()


def test_fiche_illisible_est_nommee(tmp_path):
    dossier = _corpus_pret(tmp_path)
    (dossier / "clips" / "factice-b.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ValueError, match="factice-b.json"):
        credits.lire_fiches(dossier)
    (dossier / "clips" / "factice-b.json").write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(ValueError, match="factice-b.json"):
        credits.lire_fiches(dossier)


# ------------------------------------------------------------------ durcissement : CLI

def _sans_trace(res: subprocess.CompletedProcess) -> None:
    assert "Traceback" not in res.stderr + res.stdout, res.stderr


def test_cli_build_theme_invalide_ou_absent(tmp_path):
    racine = str(tmp_path / "corpus")
    casse = tmp_path / "casse.toml"
    casse.write_text("nom = ", encoding="utf-8")
    for theme in (casse, tmp_path / "absent.toml"):
        res = _cli("build", str(theme), "--racine", racine)
        assert res.returncode == 2 and res.stderr.startswith("ERREUR : "), res.stderr
        assert theme.name in res.stderr
        _sans_trace(res)
    assert not (tmp_path / "corpus").exists()


def test_cli_credits_et_list_sur_donnees_invalides(tmp_path):
    dossier = _corpus_pret(tmp_path)
    racine = str(tmp_path / "corpus")
    res = _cli("credits", "savoir-faire", "--racine", racine, "--selection", str(tmp_path / "absente.json"))
    assert res.returncode == 2 and res.stderr.startswith("ERREUR : ")
    _sans_trace(res)
    (dossier / "selections.json").write_text("[]", encoding="utf-8")
    res = _cli("credits", "savoir-faire", "--racine", racine, "--selection", str(dossier / "selections.json"))
    assert res.returncode == 1 and "selections.json" in res.stderr
    _sans_trace(res)
    (dossier / "clips" / "factice-a.json").write_text("{pas du json", encoding="utf-8")
    for commande in ("credits", "list"):
        res = _cli(commande, "savoir-faire", "--racine", racine)
        assert res.returncode == 1 and "factice-a.json" in res.stderr, commande
        _sans_trace(res)


def test_cli_racine_avant_ou_apres_la_sous_commande(tmp_path):
    _corpus_pret(tmp_path)
    racine = str(tmp_path / "corpus")
    assert _cli("--racine", racine, "list", "savoir-faire").returncode == 0
    assert _cli("list", "savoir-faire", "--racine", racine).returncode == 0
    assert _cli("list", "savoir-faire", f"--racine={racine}").returncode == 0
    res = _cli("list", "savoir-faire", "--racine")
    assert res.returncode == 2 and "Traceback" not in res.stderr


def test_cli_list_sans_index_le_dit(tmp_path):
    _corpus_pret(tmp_path)
    res = _cli("list", "savoir-faire", "--racine", str(tmp_path / "corpus"))
    assert "absent" in res.stdout


# Commandes en processus : sources et téléchargements remplacés.

def _urlopen_fictif(archive_ok: bool = True):
    """Pixabay refuse (HTTP 429, la clé est dans l'URL) ; l'Internet Archive répond."""
    def urlopen(requete, timeout=0):
        url = requete.full_url
        if url.startswith("https://pixabay.com/") or not archive_ok:
            raise urllib.error.HTTPError(url, 429, "Too Many Requests", {}, None)
        if url.startswith("https://archive.org/advancedsearch.php"):
            return _Reponse(json.dumps({"response": {"docs": [{
                "identifier": "film_1950", "title": "Le métier", "creator": "Studio A",
                "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"}]}}).encode())
        if url.startswith("https://archive.org/metadata/film_1950"):
            return _Reponse(json.dumps({"files": [{"name": "film_1950.mp4", "size": "1000",
                                                   "length": "20"}]}).encode())
        if url.startswith("https://archive.org/download/film_1950/film_1950.mp4"):
            return _Reponse(b"video")
        raise AssertionError(f"URL inattendue : {url}")
    return urlopen


def test_build_une_source_en_erreur_ne_bloque_pas_les_autres_et_la_cle_reste_secrete(
        tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(reseau, "PAUSE", 0)
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_fictif())
    monkeypatch.setenv("PIXABAY_API_KEY", "cle-tres-secrete")
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)          # pas de .env du dépôt
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["pixabay", "archive"]'), encoding="utf-8")
    code = corpus_cli.main(["build", str(theme), "--racine", str(tmp_path / "corpus")])
    sortie = capsys.readouterr()
    assert code == 0, sortie.err
    assert "HTTP 429" in sortie.out and "pixabay" in sortie.out
    assert "cle-tres-secrete" not in sortie.out + sortie.err
    corpus = tmp_path / "corpus" / "savoir-faire"
    assert (corpus / "clips" / "archive-film_1950.mp4").exists()
    assert json.loads((corpus / "clips" / "archive-film_1950.json").read_text(encoding="utf-8"))["licence"] \
        == "domaine-public"
    assert (corpus / "theme.toml").read_text(encoding="utf-8") == theme.read_text(encoding="utf-8")


def test_build_rejoue_depuis_la_copie_du_theme_du_corpus(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(reseau, "PAUSE", 0)
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_fictif())
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["archive"]'), encoding="utf-8")
    racine = str(tmp_path / "corpus")
    assert corpus_cli.main(["build", str(theme), "--racine", racine]) == 0
    assert "1 clip(s) téléchargé(s)" in capsys.readouterr().out
    copie = tmp_path / "corpus" / "savoir-faire" / "theme.toml"
    assert corpus_cli.main(["build", str(copie), "--racine", racine]) == 0
    assert "0 clip(s) téléchargé(s)" in capsys.readouterr().out


def test_build_sans_aucun_clip_n_est_pas_un_succes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(reseau, "PAUSE", 0)
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_fictif(archive_ok=False))
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["archive"]'), encoding="utf-8")
    code = corpus_cli.main(["build", str(theme), "--racine", str(tmp_path / "corpus")])
    sortie = capsys.readouterr()
    assert code == 1 and "HTTP 429" in sortie.out and "ERREUR" in sortie.err


def test_build_dossier_inscriptible_impossible(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    monkeypatch.setattr(corpus_cli.sources, "construire", lambda noms, env: [SourceFactice([_resultat("a")])])
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["archive"]'), encoding="utf-8")
    (tmp_path / "corpus").write_text("je suis un fichier, pas un dossier", encoding="utf-8")
    code = corpus_cli.main(["build", str(theme), "--racine", str(tmp_path / "corpus")])
    assert code == 2 and capsys.readouterr().err.startswith("ERREUR : ")


def test_lire_env(tmp_path, monkeypatch):
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    (tmp_path / ".env").write_text(
        '# commentaire\nPEXELS_API_KEY="cle-pexels"\nexport PIXABAY_API_KEY = cle-pixabay\nAUTRE=1\n',
        encoding="utf-8")
    assert corpus_cli.lire_env() == {"PEXELS_API_KEY": "cle-pexels", "PIXABAY_API_KEY": "cle-pixabay"}
    monkeypatch.setenv("PEXELS_API_KEY", "cle-de-l-environnement")                  # l'environnement prime
    assert corpus_cli.lire_env()["PEXELS_API_KEY"] == "cle-de-l-environnement"
    monkeypatch.setenv("PEXELS_API_KEY", "")                       # vide : le .env n'est pas consulté pour elle
    assert "PEXELS_API_KEY" not in corpus_cli.lire_env()


def test_lire_env_illisible_previent_sans_planter(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    monkeypatch.delenv("PEXELS_API_KEY", raising=False)
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    (tmp_path / ".env").write_bytes(b"PEXELS_API_KEY=\xff\xfe")
    assert corpus_cli.lire_env() == {}
    assert ".env" in capsys.readouterr().err
