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


# ------------------------------------------------------------------ images clés, index, recherche (tâche 7)

from corpus_documentaire import images_cles, index  # noqa: E402


def test_temps_images_cles():
    assert images_cles.temps_images_cles(10.0, [4.0]) == [0.5, 3.5, 4.1, 6.5, 9.5]
    assert images_cles.temps_images_cles(0.6, []) == [0.3]
    assert images_cles.temps_images_cles(10.0, [3.6]) == [0.5, 3.5, 6.5, 9.5]   # 3.7 trop proche de 3.5


class EncodeurFactice:
    """Vecteur [1, 0, 0] pour tout ce qui parle de chameau, [0, 1, 0] sinon."""
    nom = "factice/1"

    @staticmethod
    def _vecteur(texte: str) -> list[float]:
        return [1.0, 0.0, 0.0] if "chameau" in texte else [0.0, 1.0, 0.0]

    def images(self, chemins):
        return [self._vecteur(Path(c).name) for c in chemins]

    def texte(self, texte):
        return self._vecteur(texte)


def _extraire_factice(clip, dossier, intervalle=3.0):
    sorties = []
    for i, t in enumerate((0.5, 3.5)):
        chemin = dossier / f"{clip.stem}-{i:03d}.jpg"
        chemin.write_bytes(b"jpg")
        sorties.append((t, chemin))
    return sorties


def test_index_et_recherche(tmp_path):
    dossier = _corpus_pret(tmp_path)
    (dossier / "clips" / "factice-chameau.mp4").write_bytes(b"x")
    (dossier / "clips" / "factice-chameau.json").write_text(json.dumps(
        {**_resultat("chameau").fiche(), "fichier": "factice-chameau.mp4"}), encoding="utf-8")
    assert index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice) == 6
    resultats = index.rechercher(dossier, "un chameau dans le désert", EncodeurFactice(), top=2)
    assert resultats[0]["clip"] == "factice-chameau.mp4"
    assert resultats[0]["score"] == pytest.approx(1.0)
    assert resultats[0]["fiche"]["titre"] == "Titre chameau"
    assert len({r["clip"] for r in resultats}) == len(resultats) == 2


def test_recherche_refuse_un_autre_encodeur(tmp_path):
    dossier = _corpus_pret(tmp_path)
    index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice)
    autre = EncodeurFactice()
    autre.nom = "autre/2"
    with pytest.raises(ValueError, match="reconstruire"):
        index.rechercher(dossier, "x", autre)


def test_index_vide_refuse(tmp_path):
    dossier = tmp_path / "vide"
    (dossier / "clips").mkdir(parents=True)
    with pytest.raises(ValueError, match="build"):
        index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice)


@requiert_ffmpeg
def test_extraction_reelle(tmp_path):
    clip = tmp_path / "mire.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    "testsrc2=s=320x240:r=25:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(clip)], check=True)
    images = images_cles.extraire(clip, tmp_path / "images")
    assert len(images) >= 2 and all(chemin.exists() for _, chemin in images)


def test_cli_index_sans_dependances(tmp_path):
    try:
        import open_clip  # noqa: F401
        pytest.skip("open_clip installé : le message d'absence ne s'applique pas")
    except ImportError:
        pass
    _corpus_pret(tmp_path)
    res = _cli("index", "savoir-faire", "--racine", str(tmp_path / "corpus"))
    assert res.returncode == 2 and "requirements-corpus.txt" in res.stderr


# ------------------------------------------------------------------ durcissement : images clés

def test_intervalle_nul_ou_negatif_refuse():
    for intervalle in (0, -1.0, float("nan")):
        with pytest.raises(ValueError, match="intervalle"):
            images_cles.temps_images_cles(10.0, [], intervalle)


def test_coupe_en_fin_de_clip_ignoree_et_ecart_minimal():
    assert images_cles.temps_images_cles(5.0, [4.95]) == [0.5, 3.5]          # 5.05 dépasse la durée
    instants = images_cles.temps_images_cles(30.0, [1.0, 1.2, 1.3, 7.7, 20.0])
    assert all(b - a >= images_cles.ECART_MIN for a, b in zip(instants, instants[1:]))
    assert 1.1 in instants and 20.1 in instants and 1.3 not in instants


def _mire(chemin: Path, duree: int = 4) -> Path:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    f"testsrc2=s=320x240:r=25:d={duree}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(chemin)],
                   check=True)
    return chemin


@requiert_ffmpeg
def test_extraction_refait_les_images_quand_l_intervalle_change(tmp_path):
    """Une image en cache sous le même numéro mais pour un autre instant fausserait l'index."""
    clip = _mire(tmp_path / "mire.mp4")
    images_cles.extraire(clip, tmp_path / "cache", intervalle=3.0)
    apres = images_cles.extraire(clip, tmp_path / "cache", intervalle=1.0)
    neuves = images_cles.extraire(clip, tmp_path / "neuf", intervalle=1.0)
    assert [t for t, _ in apres] == [t for t, _ in neuves] and len(apres) >= 4
    for (_, a), (_, b) in zip(apres, neuves):
        assert a.read_bytes() == b.read_bytes(), a.name


@requiert_ffmpeg
def test_extraction_retire_les_images_devenues_inutiles(tmp_path):
    clip = _mire(tmp_path / "mire.mp4")
    longue = images_cles.extraire(clip, tmp_path / "images", intervalle=1.0)
    courte = images_cles.extraire(clip, tmp_path / "images", intervalle=3.0)
    restantes = sorted(p.name for p in (tmp_path / "images").glob("mire-*.jpg"))
    assert len(longue) > len(courte) and restantes == sorted(p.name for _, p in courte)


def test_extraction_ecarte_une_image_vide(tmp_path, monkeypatch):
    """ffmpeg peut laisser un fichier de 0 octet (instant hors du clip) : pas d'image, pas d'entrée d'index."""
    def faux(commande):
        if commande[0] == "ffprobe":
            return subprocess.CompletedProcess(commande, 0, '{"format": {"duration": "4.0"}}', "")
        if "-frames:v" in commande:
            Path(commande[-1]).write_bytes(b"" if "0.50" in commande else b"jpg")
        return subprocess.CompletedProcess(commande, 0, "", "")

    monkeypatch.setattr(images_cles.shutil, "which", lambda nom: "/usr/bin/" + nom)
    monkeypatch.setattr(images_cles, "_executer", faux)
    sorties = images_cles.extraire(tmp_path / "c.mp4", tmp_path / "images")
    assert [t for t, _ in sorties] == [3.5] and not (tmp_path / "images" / "c-000.jpg").exists()


@requiert_ffmpeg
def test_extraction_d_un_fichier_illisible_ne_rend_rien(tmp_path):
    casse = tmp_path / "casse.mp4"
    casse.write_bytes(b"ce n'est pas une video")
    assert images_cles.extraire(casse, tmp_path / "images") == []


def test_extraction_sans_ffmpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(images_cles.shutil, "which", lambda nom: None)
    with pytest.raises(images_cles.OutilAbsent, match="ffmpeg"):
        images_cles.extraire(tmp_path / "x.mp4", tmp_path / "images")
    assert issubclass(images_cles.OutilAbsent, RuntimeError)


def test_ffmpeg_et_ffprobe_decodes_sans_planter(tmp_path, monkeypatch):
    """Sortie d'outil en octets quelconques : décodée avec remplacement, jamais fatale."""
    appels = []

    def faux_run(commande, **options):
        appels.append(options)
        sortie = '{"format": {"duration": "4.0"}}' if commande[0] == "ffprobe" else "pts_time:2.5 �"
        return subprocess.CompletedProcess(commande, 0, sortie, sortie)

    monkeypatch.setattr(images_cles.shutil, "which", lambda nom: "/usr/bin/" + nom)
    monkeypatch.setattr(images_cles.subprocess, "run", faux_run)
    assert images_cles.duree_video(tmp_path / "x.mp4") == 4.0
    assert images_cles.coupes_video(tmp_path / "x.mp4") == [2.5]
    assert all(o["encoding"] == "utf-8" and o["errors"] == "replace" for o in appels) and len(appels) == 2


@pytest.mark.parametrize("sortie, code", [("", 1), ("pas du json", 0), ('{"format": {}}', 0),
                                          ('{"format": {"duration": "N/A"}}', 0),
                                          ('{"format": {"duration": "nan"}}', 0)])
def test_duree_illisible_vaut_zero(tmp_path, monkeypatch, sortie, code):
    monkeypatch.setattr(images_cles.subprocess, "run",
                        lambda commande, **options: subprocess.CompletedProcess(commande, code, sortie, ""))
    assert images_cles.duree_video(tmp_path / "x.mp4") == 0.0


# ------------------------------------------------------------------ durcissement : index

def _extraire_sans_images_pour_a(clip, dossier, intervalle=3.0):
    return [] if clip.name == "factice-a.mp4" else _extraire_factice(clip, dossier, intervalle)


def test_un_clip_sans_image_cle_est_signale_pas_tu(tmp_path):
    dossier = _corpus_pret(tmp_path)
    ignores = []
    nombre = index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_sans_images_pour_a,
                                    avertir=ignores.append)
    assert nombre == 2 and len(ignores) == 1 and "factice-a.mp4" in ignores[0]
    meta = json.loads((dossier / "index.json").read_text(encoding="utf-8"))
    assert {e["clip"] for e in meta["images"]} == {"factice-b.mp4"}


def test_aucune_image_cle_nommee_comme_telle(tmp_path):
    dossier = _corpus_pret(tmp_path)
    with pytest.raises(ValueError, match="aucune image clé extraite de 2 clip"):
        index.construire_index(dossier, EncodeurFactice(), extraire=lambda clip, d, i=3.0: [])
    assert not (dossier / "index.json").exists()


def test_un_index_refait_remplace_le_precedent_sans_reste(tmp_path):
    dossier = _corpus_pret(tmp_path)
    index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice)
    (dossier / "clips" / "factice-a.mp4").unlink()
    assert index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice) == 2
    meta = json.loads((dossier / "index.json").read_text(encoding="utf-8"))
    assert len(meta["images"]) == 2 and (dossier / "index.f32").stat().st_size == 2 * meta["dimension"] * 4
    assert not list(dossier.glob("*.tmp"))


class EncodeurQuiPerdDesImages(EncodeurFactice):
    def images(self, chemins):
        return super().images(chemins)[:-1]


class EncodeurDeDimensionsMelangees(EncodeurFactice):
    def images(self, chemins):
        vecteurs = super().images(chemins)
        vecteurs[-1] = vecteurs[-1] + [0.0]
        return vecteurs


@pytest.mark.parametrize("encodeur", [EncodeurQuiPerdDesImages(), EncodeurDeDimensionsMelangees()])
def test_encodeur_incoherent_ne_produit_pas_d_index(tmp_path, encodeur):
    dossier = _corpus_pret(tmp_path)
    with pytest.raises(ValueError, match="encodeur"):
        index.construire_index(dossier, encodeur, extraire=_extraire_factice)
    assert not (dossier / "index.json").exists() and not (dossier / "index.f32").exists()


def _index_pret(tmp_path) -> Path:
    dossier = _corpus_pret(tmp_path)
    index.construire_index(dossier, EncodeurFactice(), extraire=_extraire_factice)
    return dossier


def test_recherche_refuse_un_index_f32_tronque(tmp_path):
    dossier = _index_pret(tmp_path)
    brut = (dossier / "index.f32").read_bytes()
    for tronque in (brut[:-4], brut[:-3]):                 # un vecteur de moins ; un octet de travers
        (dossier / "index.f32").write_bytes(tronque)
        with pytest.raises(ValueError, match="reconstruire"):
            index.rechercher(dossier, "x", EncodeurFactice())


@pytest.mark.parametrize("contenu", ["pas du json", "[]", '{"encodeur": "factice/1"}',
                                     '{"encodeur": "factice/1", "dimension": 3, "images": [{"clip": "a"}]}',
                                     '{"encodeur": "factice/1", "dimension": 0, "images": []}'])
def test_recherche_refuse_un_index_json_abime(tmp_path, contenu):
    dossier = _index_pret(tmp_path)
    (dossier / "index.json").write_text(contenu, encoding="utf-8")
    with pytest.raises(ValueError, match="reconstruire"):
        index.rechercher(dossier, "x", EncodeurFactice())


@pytest.mark.parametrize("abimer", [
    lambda meta: meta["images"][0].pop("t"),               # une entrée sans instant, nombre d'entrées intact
    lambda meta: meta.update(dimension="3"),               # dimension qui n'est pas un entier
    lambda meta: meta.update(encodeur=7),
], ids=["entree-sans-instant", "dimension-texte", "encodeur-numerique"])
def test_recherche_refuse_un_index_json_de_structure_fausse_mais_de_bonne_taille(tmp_path, abimer):
    dossier = _index_pret(tmp_path)
    meta = json.loads((dossier / "index.json").read_text(encoding="utf-8"))
    abimer(meta)
    (dossier / "index.json").write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError, match="reconstruire"):
        index.rechercher(dossier, "x", EncodeurFactice())


def test_recherche_top_invalide(tmp_path):
    dossier = _index_pret(tmp_path)
    for top in (0, -2):
        with pytest.raises(ValueError, match="top"):
            index.rechercher(dossier, "x", EncodeurFactice(), top=top)


def test_recherche_nomme_la_fiche_illisible(tmp_path):
    dossier = _index_pret(tmp_path)
    (dossier / "clips" / "factice-b.json").write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ValueError, match="factice-b.json"):
        index.rechercher(dossier, "x", EncodeurFactice(), top=10)


def test_recherche_refuse_une_requete_de_mauvaise_dimension(tmp_path):
    dossier = _index_pret(tmp_path)

    class Large(EncodeurFactice):
        def texte(self, texte):
            return [1.0, 0.0, 0.0, 0.0]

    with pytest.raises(ValueError, match="dimension"):
        index.rechercher(dossier, "x", Large())


def test_recherche_top_et_fiche_absente(tmp_path):
    dossier = _index_pret(tmp_path)
    (dossier / "clips" / "factice-b.json").unlink()
    resultats = index.rechercher(dossier, "chameau", EncodeurFactice(), top=10)
    assert len(resultats) == 2                                          # top plafonné au nombre de clips
    assert {r["clip"]: r["fiche"] is None for r in resultats} == {"factice-a.mp4": False, "factice-b.mp4": True}


# ------------------------------------------------------------------ durcissement : encodeur réel (modules fictifs)

class _Tenseur:
    """Le strict nécessaire de torch.Tensor pour EncodeurClip : norm, division, indexation, tolist."""

    def __init__(self, lignes):
        self.lignes = lignes

    def norm(self, dim=-1, keepdim=False):
        return _Tenseur([[sum(x * x for x in ligne) ** 0.5] for ligne in self.lignes])

    def __truediv__(self, autre):
        return _Tenseur([[x / n[0] for x in ligne] for ligne, n in zip(self.lignes, autre.lignes)])

    def __getitem__(self, i):
        return _Tenseur(self.lignes[i])

    def tolist(self):
        return self.lignes


class _FausseImage:
    def __init__(self, nom):
        self.nom = nom

    def __enter__(self):
        return self

    def __exit__(self, *erreur):
        return False

    def convert(self, mode):
        assert mode == "RGB"
        return self


def _modules_fictifs(monkeypatch, *, echec_modele=None):
    import contextlib
    import types

    torch = types.ModuleType("torch")
    torch.no_grad = contextlib.nullcontext
    torch.stack = lambda elements: _Tenseur([e for e in elements])
    pil, pil_image = types.ModuleType("PIL"), types.ModuleType("PIL.Image")
    pil_image.open = lambda chemin: _FausseImage(Path(chemin).name)
    pil.Image = pil_image

    class Modele:
        def eval(self):
            return self

        def encode_image(self, lot):         # un vecteur par image : sa longueur de nom, puis 1
            return _Tenseur([[float(len(image.nom)), 1.0] for image in lot.lignes])

        def encode_text(self, jetons):
            return _Tenseur([[3.0, 4.0]])

    def creer(modele, pretrained):
        if echec_modele:
            raise echec_modele
        return Modele(), None, lambda image: image          # (modèle, prétraitement d'entraînement, de validation)

    open_clip = types.ModuleType("open_clip")
    open_clip.create_model_and_transforms = creer
    open_clip.get_tokenizer = lambda modele: (lambda textes: textes)
    for nom, module in (("torch", torch), ("PIL", pil), ("PIL.Image", pil_image), ("open_clip", open_clip)):
        monkeypatch.setitem(sys.modules, nom, module)


def test_encodeur_clip_normalise_et_garde_l_ordre(monkeypatch):
    _modules_fictifs(monkeypatch)
    encodeur = index.EncodeurClip("ViT-B-32", "poids-x")
    assert encodeur.nom == "ViT-B-32/poids-x"
    chemins = [Path(f"image-{i}" + "x" * i + ".jpg") for i in range(70)]       # 3 lots de 32, 32 et 6
    vecteurs = encodeur.images(chemins)
    assert len(vecteurs) == 70
    for chemin, vecteur in zip(chemins, vecteurs):
        longueur = float(len(chemin.name))
        norme = (longueur ** 2 + 1) ** 0.5
        assert vecteur == pytest.approx([longueur / norme, 1 / norme])
    assert encodeur.texte("un chameau") == pytest.approx([0.6, 0.8])


@pytest.mark.parametrize("manquant", ["open_clip", "torch", "PIL"])
def test_encodeur_clip_dependance_absente(monkeypatch, manquant):
    _modules_fictifs(monkeypatch)
    monkeypatch.setitem(sys.modules, manquant, None)                # import impossible
    with pytest.raises(index.DependanceManquante, match="requirements-corpus.txt"):
        index.EncodeurClip()


def test_encodeur_clip_modele_indisponible_est_une_dependance_manquante(monkeypatch):
    _modules_fictifs(monkeypatch, echec_modele=RuntimeError("Model config for ViT-Z not found"))
    with pytest.raises(index.DependanceManquante, match="ViT-Z"):
        index.EncodeurClip("ViT-Z", "poids-x")


# ------------------------------------------------------------------ durcissement : commandes index et search

def _avec_encodeur_factice(monkeypatch, extraire=_extraire_factice):
    """index et search en processus : encodeur CLIP et extraction ffmpeg remplacés."""
    monkeypatch.setattr(corpus_cli, "_encodeur", lambda args: EncodeurFactice())
    original = corpus_cli.index.construire_index
    monkeypatch.setattr(corpus_cli.index, "construire_index",
                        lambda dossier, encodeur, **options: original(dossier, encodeur, extraire=extraire,
                                                                      **options))


def _corpus_a_deux_emplacements(tmp_path) -> Path:
    dossier = _corpus_pret(tmp_path)
    (dossier / "clips" / "factice-chameau.mp4").write_bytes(b"x")
    (dossier / "clips" / "factice-chameau.json").write_text(json.dumps(
        {**_resultat("chameau").fiche(), "fichier": "factice-chameau.mp4",
         "attribution_exigee": False}), encoding="utf-8")
    (dossier / "theme.toml").write_text(THEME.replace("mains d'artisan qui travaillent le bois, gros plan",
                                                      "un chameau dans le sable") + """
[[emplacements]]
id = "fin"
description = "un atelier vide au crépuscule"
requetes = ["empty workshop"]
""", encoding="utf-8")
    return dossier


def test_index_puis_search_par_emplacement_enregistre_la_selection(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    assert "6 image(s) clé(s) (factice/1)" in capsys.readouterr().out
    assert corpus_cli.main(["search", "savoir-faire", "--emplacement", "ouverture", "--top", "2",
                            "--racine", racine]) == 0
    sortie = capsys.readouterr().out
    assert sortie.splitlines()[0].startswith("1.000  factice-chameau.mp4 à 0.5 s  « Titre chameau » (cc0)")
    assert "sélection enregistrée" in sortie
    assert corpus_cli.main(["search", "savoir-faire", "--emplacement", "fin", "--top", "1", "--racine", racine]) == 0
    selections = json.loads((dossier / "selections.json").read_text(encoding="utf-8"))
    assert set(selections) == {"ouverture", "fin"}                    # la deuxième recherche n'efface pas la première
    assert len(selections["ouverture"]) == 2 and len(selections["fin"]) == 1
    assert selections["ouverture"][0]["clip"] == "factice-chameau.mp4"
    assert set(selections["ouverture"][0]) == {"clip", "t", "score", "image"}        # sans la fiche
    assert not list(dossier.glob("*.tmp"))
    # La sélection nourrit les crédits : seulement les clips retenus.
    assert corpus_cli.main(["credits", "savoir-faire", "--selection", str(dossier / "selections.json"),
                            "--racine", racine]) == 0
    texte = (dossier / "credits.md").read_text(encoding="utf-8")
    assert "Titre chameau" in texte


def test_search_par_texte_libre_n_ecrit_pas_de_selection(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    assert corpus_cli.main(["search", "savoir-faire", "un chameau", "--racine", racine]) == 0
    assert "factice-chameau.mp4" in capsys.readouterr().out and not (dossier / "selections.json").exists()


def test_search_erreurs_d_usage(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)

    def chercher(*args) -> tuple[int, str]:
        code = corpus_cli.main(["search", "savoir-faire", *args, "--racine", racine])
        return code, capsys.readouterr().err

    code, err = chercher("un chameau")
    assert code == 2 and "index absent" in err                         # pas encore d'index
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    capsys.readouterr()
    code, err = chercher()
    assert code == 2 and "texte ou --emplacement" in err
    code, err = chercher("un chameau", "--emplacement", "ouverture")
    assert code == 2 and "pas les deux" in err
    code, err = chercher("--emplacement", "inconnu")
    assert code == 2 and "inconnu" in err
    for top in ("0", "-3", "beaucoup"):
        with pytest.raises(SystemExit) as sortie:
            chercher("un chameau", "--top", top)
        assert sortie.value.code == 2
        assert "--top" in capsys.readouterr().err
    (dossier / "theme.toml").write_text("nom = ", encoding="utf-8")
    code, err = chercher("--emplacement", "ouverture")
    assert code == 2 and err.startswith("ERREUR : ") and "theme.toml" in err
    (dossier / "theme.toml").unlink()
    code, err = chercher("--emplacement", "ouverture")
    assert code == 2 and err.startswith("ERREUR : ")


def test_search_ne_ecrase_pas_une_selection_illisible(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    capsys.readouterr()
    (dossier / "selections.json").write_text('{"ouverture": 3}', encoding="utf-8")
    code = corpus_cli.main(["search", "savoir-faire", "--emplacement", "fin", "--racine", racine])
    assert code == 1 and "selections.json" in capsys.readouterr().err
    assert (dossier / "selections.json").read_text(encoding="utf-8") == '{"ouverture": 3}'


def test_search_avec_un_index_incomplet_est_une_erreur_propre(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    capsys.readouterr()
    (dossier / "index.f32").unlink()
    assert corpus_cli.main(["search", "savoir-faire", "un chameau", "--racine", racine]) == 2
    assert capsys.readouterr().err.startswith("ERREUR : ")
    assert not (dossier / "selections.json").exists()


def test_search_avec_un_index_d_un_autre_encodeur_demande_de_reconstruire(tmp_path, monkeypatch, capsys):
    _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    capsys.readouterr()

    class Autre(EncodeurFactice):
        nom = "autre/2"

    monkeypatch.setattr(corpus_cli, "_encodeur", lambda args: Autre())
    assert corpus_cli.main(["search", "savoir-faire", "un chameau", "--racine", racine]) == 2
    assert "reconstruire" in capsys.readouterr().err


def test_index_signale_les_clips_non_indexes_et_reste_a_zero(tmp_path, monkeypatch, capsys):
    _corpus_pret(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch, extraire=_extraire_sans_images_pour_a)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    sortie = capsys.readouterr()
    assert "avertissement" in sortie.err and "factice-a.mp4" in sortie.err
    assert "2 image(s) clé(s)" in sortie.out and "1 clip(s) non indexé(s)" in sortie.out


def test_index_sans_aucune_image_cle_echoue(tmp_path, monkeypatch, capsys):
    _corpus_pret(tmp_path)
    _avec_encodeur_factice(monkeypatch, extraire=lambda clip, dossier, intervalle=3.0: [])
    assert corpus_cli.main(["index", "savoir-faire", "--racine", str(tmp_path / "corpus")]) == 1
    assert capsys.readouterr().err.startswith("ERREUR : aucune image clé")


def test_index_sans_ffmpeg_est_un_outil_absent(tmp_path, monkeypatch, capsys):
    _corpus_pret(tmp_path)
    monkeypatch.setattr(corpus_cli, "_encodeur", lambda args: EncodeurFactice())
    monkeypatch.setattr(images_cles.shutil, "which", lambda nom: None)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", str(tmp_path / "corpus")]) == 2
    assert "ffmpeg" in capsys.readouterr().err


def test_index_image_illisible_est_une_erreur_propre(tmp_path, monkeypatch, capsys):
    _corpus_pret(tmp_path)

    class Illisible(EncodeurFactice):
        def images(self, chemins):
            raise OSError("cannot identify image file")

    monkeypatch.setattr(corpus_cli, "_encodeur", lambda args: Illisible())
    original = corpus_cli.index.construire_index
    monkeypatch.setattr(corpus_cli.index, "construire_index",
                        lambda dossier, encodeur, **options: original(dossier, encodeur,
                                                                      extraire=_extraire_factice, **options))
    assert corpus_cli.main(["index", "savoir-faire", "--racine", str(tmp_path / "corpus")]) == 1
    assert capsys.readouterr().err.startswith("ERREUR : ")


def test_cli_search_sans_index_ni_dependances(tmp_path):
    _corpus_pret(tmp_path)
    racine = str(tmp_path / "corpus")
    res = _cli("search", "savoir-faire", "un chameau", "--racine", racine)
    assert res.returncode == 2 and res.stderr.startswith("ERREUR : ") and "Traceback" not in res.stderr
    assert _cli("search", "absent", "x", "--racine", racine).returncode == 2


# ------------------------------------------------------------------ revue 1 : téléchargements, durées, licences, crédits

@pytest.fixture(autouse=True)
def _sans_pause_reseau(monkeypatch):
    """Les pauses de politesse envers les API n'ont pas leur place dans des tests hors ligne."""
    monkeypatch.setattr(reseau, "PAUSE", 0)


class _ReponseAvecEntetes(io.BytesIO):
    def __init__(self, corps: bytes, **entetes):
        super().__init__(corps)
        self.headers = entetes


def test_telecharger_refuse_un_telechargement_tronque(tmp_path, monkeypatch):
    """Le serveur annonce 100000 octets et coupe après 10 : ce n'est pas un clip complet."""
    monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0:
                        _ReponseAvecEntetes(b"0123456789", **{"Content-Length": "100000"}))
    with pytest.raises(reseau.ErreurReseau, match="incomplet") as err:
        reseau.telecharger("https://exemple.org/f.mp4?jeton=secret", tmp_path / "f.mp4")
    assert "secret" not in str(err.value) and "10" in str(err.value) and "100000" in str(err.value)
    assert list(tmp_path.iterdir()) == []                      # ni clip, ni .part


def test_telecharger_compare_a_la_longueur_annoncee_sans_la_croire_aveuglement(tmp_path, monkeypatch):
    for annonce, accepte in (("5", True), ("pas un nombre", True), ("-3", True), ("6", False)):
        monkeypatch.setattr(reseau.urllib.request, "urlopen", lambda requete, timeout=0, a=annonce:
                            _ReponseAvecEntetes(b"video", **{"Content-Length": a}))
        cible = tmp_path / f"f{annonce[:2]}.mp4"
        if accepte:
            assert reseau.telecharger("https://exemple.org/f.mp4", cible).read_bytes() == b"video"
        else:
            with pytest.raises(reseau.ErreurReseau, match="incomplet"):
                reseau.telecharger("https://exemple.org/f.mp4", cible)


def test_reseau_fait_une_pause_apres_une_erreur_http(tmp_path, monkeypatch):
    """Un 429 suivi aussitôt d'une autre requête aggraverait le refus : on temporise aussi à l'échec."""
    pauses = []
    monkeypatch.setattr(reseau, "PAUSE", 0.25)
    monkeypatch.setattr(reseau.time, "sleep", pauses.append)
    monkeypatch.setattr(reseau.urllib.request, "urlopen", _urlopen_qui_leve(
        urllib.error.HTTPError("https://exemple.org/api", 429, "Too Many Requests", {}, None)))
    with pytest.raises(reseau.ErreurReseau):
        reseau.obtenir_json("https://exemple.org/api")
    with pytest.raises(reseau.ErreurReseau):
        reseau.telecharger("https://exemple.org/f.mp4", tmp_path / "f.mp4")
    assert pauses == [0.25, 0.25]


# --- durée maximale quand la source ne donne pas de durée

def _theme_limite(tmp_path):
    return _theme(tmp_path)          # duree_max = 60


def _sans_duree(ident, **options):
    resultat = _resultat(ident, **options)
    resultat.duree = None
    return resultat


def test_duree_inconnue_mesuree_apres_telechargement_et_ecartee_si_trop_longue(tmp_path):
    mesures = []

    def mesurer(video):
        mesures.append(video.name)
        return {"factice-long.mp4": 300.0, "factice-court.mp4": 20.5}[video.name]

    dossier = tmp_path / "c"
    rapport = cons.construire(_theme_limite(tmp_path), dossier,
                              [SourceFactice([_sans_duree("long"), _sans_duree("court")])],
                              telecharger=_telecharger, mesurer=mesurer)
    clips = dossier / "clips"
    assert not (clips / "factice-long.mp4").exists() and not (clips / "factice-long.json").exists()
    assert rapport.ecartes_duree >= 1 and rapport.telecharges == 1
    fiche = json.loads((clips / "factice-court.json").read_text(encoding="utf-8"))
    assert fiche["duree"] == 20.5                              # la durée mesurée est conservée
    assert "factice-long.mp4" in mesures


def test_un_clip_trop_long_n_est_pas_retelecharge_par_la_requete_suivante(tmp_path):
    appels = []

    def telecharger(url, destination):
        appels.append(url)
        return _telecharger(url, destination)

    rapport = cons.construire(_theme_limite(tmp_path), tmp_path / "c", [SourceFactice([_sans_duree("long")])],
                              telecharger=telecharger, mesurer=lambda video: 300.0)      # le thème a deux requêtes
    assert appels == ["https://exemple/long.mp4"] and rapport.ecartes_duree == 1


def test_duree_connue_n_est_pas_remesuree_et_sans_limite_on_ne_mesure_pas(tmp_path):
    def mesurer(video):
        raise AssertionError("ffprobe ne doit pas être appelé")

    cons.construire(_theme_limite(tmp_path), tmp_path / "c", [SourceFactice([_resultat("a")])],
                    telecharger=_telecharger, mesurer=mesurer)
    sans_limite = tmp_path / "sans-limite.toml"
    sans_limite.write_text(THEME.replace("duree_max = 60\n", "").replace('["archive", "nasa"]', '["archive"]'),
                           encoding="utf-8")
    theme = cons.charger_theme(sans_limite)
    assert theme.duree_max is None
    cons.construire(theme, tmp_path / "d", [SourceFactice([_sans_duree("x")])],
                    telecharger=_telecharger, mesurer=mesurer)
    assert (tmp_path / "d" / "clips" / "factice-x.json").exists()


def test_ffprobe_absent_garde_le_clip_et_le_dit(tmp_path):
    def mesurer(video):
        raise cons.ErreurMesure("ffprobe introuvable")

    rapport = cons.construire(_theme_limite(tmp_path), tmp_path / "c",
                              [SourceFactice([_sans_duree("a"), _sans_duree("b")])],
                              telecharger=_telecharger, mesurer=mesurer)
    assert rapport.telecharges == 2
    assert len(rapport.avertissements) == 1                    # une ligne pour le lot, pas une par clip et par requête
    assert "ffprobe" in rapport.avertissements[0] and "2 clip" in rapport.avertissements[0]
    fiche = json.loads((tmp_path / "c" / "clips" / "factice-a.json").read_text(encoding="utf-8"))
    assert fiche["duree"] is None


def test_fichier_illisible_pour_ffprobe_est_ecarte(tmp_path):
    rapport = cons.construire(_theme_limite(tmp_path), tmp_path / "c", [SourceFactice([_sans_duree("a")])],
                              telecharger=_telecharger, mesurer=lambda video: None)
    assert rapport.telecharges == 0 and any("factice-a" in e and "illisible" in e for e in rapport.erreurs)
    assert not list((tmp_path / "c" / "clips").iterdir())


@requiert_ffmpeg
def test_mesure_reelle_avec_ffprobe(tmp_path):
    clip = _mire(tmp_path / "mire.mp4", duree=4)
    assert cons.mesurer_duree(clip) == pytest.approx(4.0, abs=0.2)
    casse = tmp_path / "casse.mp4"
    casse.write_bytes(b"ce n'est pas une video")
    assert cons.mesurer_duree(casse) is None


def test_mesure_sans_ffprobe(tmp_path, monkeypatch):
    monkeypatch.setattr(cons.shutil, "which", lambda nom: None)
    with pytest.raises(cons.ErreurMesure, match="ffprobe"):
        cons.mesurer_duree(tmp_path / "x.mp4")


def test_build_signale_les_durees_non_verifiees(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(corpus_cli, "RACINE", tmp_path)
    monkeypatch.setattr(corpus_cli.sources, "construire", lambda noms, env: [SourceFactice([_sans_duree("a")])])
    monkeypatch.setattr(reseau, "telecharger", _telecharger)
    monkeypatch.setattr(cons.shutil, "which", lambda nom: None)       # ni ffprobe ni ffmpeg
    theme = tmp_path / "t.toml"
    theme.write_text(THEME.replace('["archive", "nasa"]', '["archive"]'), encoding="utf-8")
    assert corpus_cli.main(["build", str(theme), "--racine", str(tmp_path / "corpus")]) == 0
    assert "avertissement : " in capsys.readouterr().out


# --- conversion impossible : on ne télécharge pas pour rien

def test_un_format_a_convertir_n_est_pas_telecharge_sans_ffmpeg(tmp_path, monkeypatch):
    monkeypatch.setattr(cons.shutil, "which", lambda nom: None)
    webm = _resultat("w")
    webm.url_fichier = "https://exemple/w.webm"
    telecharges = []

    def telecharger(url, destination):
        telecharges.append(url)
        return _telecharger(url, destination)

    rapport = cons.construire(_theme(tmp_path), tmp_path / "c", [SourceFactice([webm, _resultat("m")])],
                              telecharger=telecharger)
    assert telecharges == ["https://exemple/m.mp4"] and rapport.telecharges == 1
    assert len([e for e in rapport.erreurs if "factice-w" in e and "ffmpeg" in e]) == 1     # dite une fois, pas par requête
    assert not list((tmp_path / "c" / "clips").glob("factice-w*"))


# --- crédits : la mention d'origine des licences Creative Commons

@pytest.mark.parametrize("brute, attendu", [
    ("CC BY 3.0", "Licence : CC BY (CC BY 3.0)."),
    ("https://creativecommons.org/licenses/by/4.0/", "Licence : CC BY (https://creativecommons.org/licenses/by/4.0/)."),
    ("CC BY", "Licence : CC BY."),                      # rien à ajouter quand la mention est déjà le libellé
    ("cc-by", "Licence : CC BY."),
])
def test_credits_reprennent_la_mention_d_origine_des_cc(tmp_path, brute, attendu):
    dossier = _corpus_pret(tmp_path)
    fiche = dossier / "clips" / "factice-a.json"
    donnees = json.loads(fiche.read_text(encoding="utf-8"))
    donnees["licence_brute"] = brute
    fiche.write_text(json.dumps(donnees), encoding="utf-8")
    ligne = next(l for l in credits.ecrire_credits(dossier).read_text(encoding="utf-8").splitlines()
                 if "Titre a" in l)
    assert attendu in ligne and ligne.endswith("Attribution obligatoire au générique ou en légende.")


def test_credits_sans_attribution_ne_citent_pas_la_mention_brute(tmp_path):
    dossier = _corpus_pret(tmp_path)
    fiche = dossier / "clips" / "factice-b.json"
    donnees = json.loads(fiche.read_text(encoding="utf-8"))
    donnees["licence_brute"] = "http://creativecommons.org/publicdomain/mark/1.0/"
    fiche.write_text(json.dumps(donnees), encoding="utf-8")
    ligne = next(l for l in credits.ecrire_credits(dossier).read_text(encoding="utf-8").splitlines()
                 if "Titre b" in l)
    assert "Licence : domaine public." in ligne and "creativecommons" not in ligne


# --- licences : le texte libre ambigu ne passe pas pour une licence plus large

@pytest.mark.parametrize("brute, attendue", [
    ("CC BY-NC-SA 2.0 (derived from a public domain work)", "cc-by-nc-sa"),
    ("CC BY Non-Commercial 4.0", "cc-by-nc"),
    ("CC BY NonCommercial 4.0", "cc-by-nc"),
    ("Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International", "cc-by-nc-sa"),
    ("Creative Commons Attribution-NoDerivatives 4.0", "cc-by-nd"),
    ("CC BY No Derivatives 3.0", "cc-by-nd"),
    ("CC BY ShareAlike 4.0", "cc-by-sa"),
    ("CC BY Non Commercial, No Derivs 4.0", "cc-by-nc-nd"),
    ("Attribution-NonCommercial 2.0 Generic", "cc-by-nc"),
    ("https://creativecommons.org/licenses/by/4.0/ (non-commercial use only)", "cc-by-nc"),
    ("CC BY-SA with No Derivatives", "inconnue"),                    # contradictoire
    ("CC BY 4.0 / CC BY-NC 3.0", "inconnue"),                         # deux licences : on ne choisit pas la plus large
    ("Public domain, all rights reserved", "inconnue"),
    ("Public domain or GFDL", "inconnue"),
    ("PD-self, GFDL", "inconnue"),
    ("Public domain for non-commercial use only", "inconnue"),
    # tirets Unicode (insécable, demi-cadratin, cadratin, signe moins) : repliés sur « - »
    ("CC BY\u2011NC 4.0", "cc-by-nc"),
    ("CC BY\u2013NC\u2013SA 3.0", "cc-by-nc-sa"),
    ("CC BY\u2014ND 4.0", "cc-by-nd"),
    ("CC BY\u2212SA 4.0", "cc-by-sa"),
    ("CC\u2010BY\u2010NC\u2010ND", "cc-by-nc-nd"),
    # « non-derivative » et ses variantes
    ("Creative Commons Attribution-NonDerivative 4.0", "cc-by-nd"),
    ("Creative Commons Attribution Non-Derivatives 4.0", "cc-by-nd"),
    ("CC BY 4.0, non derivs", "cc-by-nd"),
    ("Public domain, non-derivative use only", "inconnue"),
])
def test_normaliser_licence_ambigue(brute, attendue):
    assert licences.normaliser(brute) == attendue


@pytest.mark.parametrize("brute, attendue", [        # garde-fous : le durcissement ne doit pas refuser l'évident
    ("PD-old-70", "domaine-public"),
    ("Public domain in the United States", "domaine-public"),
    ("public domain", "domaine-public"),
    ("CC0 1.0 Universal Public Domain Dedication", "cc0"),
    ("CC BY 4.0 International", "cc-by"),
    ("cc-by-sa", "cc-by-sa"),
    ("Non-commercial use only", "inconnue"),
    ("CC BY-NC-ND 4.0", "cc-by-nc-nd"),
    ("cc by sand", "cc-by"),                          # « sand » n'est pas « sa »
])
def test_normaliser_licence_garde_fous(brute, attendue):
    assert licences.normaliser(brute) == attendue


@pytest.mark.parametrize("brute, attendue", [
    # toute la ponctuation de catégorie Pd est repliée sur « - »
    ("CC BY﹣NC 4.0", "cc-by-nc"),                # petit trait d'union-moins
    ("CC BY－SA 4.0", "cc-by-sa"),                # trait d'union-moins pleine chasse
    ("CC BY⸺ND 4.0", "cc-by-nd"),                # tiret double cadratin
    ("CC BY⸗NC", "cc-by-nc"),                    # double trait d'union oblique
    ("CC BY֊NC֊SA", "cc-by-nc-sa"),         # trait d'union arménien
    ("CC BY〜NC", "cc-by-nc"),                    # tiret ondulé
    ("CC BY﹘ND", "cc-by-nd"),                    # petit tiret cadratin
    # caractères de format invisibles (catégorie Cf) retirés
    ("CC BY­-NC 4.0", "cc-by-nc"),               # trait d'union conditionnel
    ("CC BY​-NC 4.0", "cc-by-nc"),               # espace sans chasse
    ("CC BY-N­C 4.0", "cc-by-nc"),
    ("CC BY⁠-SA", "cc-by-sa"),                   # gluon de mots
    ("CC BY Non­Commercial 4.0", "cc-by-nc"),
    ("CC BY­NC 4.0", "inconnue"),                # collé une fois le caractère retiré : jamais cc-by
    ("CC BY​SA", "inconnue"),
    # séparateurs ASCII entre BY et la restriction
    ("CC BY/NC 4.0", "cc-by-nc"),
    ("CC BY_NC 4.0", "cc-by-nc"),
    ("CC BY.NC 4.0", "cc-by-nc"),
    ("CC BY+NC 4.0", "cc-by-nc"),
    ("CC BY, NC 4.0", "cc-by-nc"),
    ("CC BY (NC) 4.0", "cc-by-nc"),
    ("CC BY: ND", "cc-by-nd"),
    ("CC BY/NC/SA", "cc-by-nc-sa"),
    ("CC BY_NC_ND 4.0", "cc-by-nc-nd"),
    ("CC BY+SA+ND", "inconnue"),                      # contradictoire
    # restrictions en toutes lettres, mêmes séparateurs
    ("CC BY Non_Commercial 4.0", "cc-by-nc"),
    ("CC BY Share_Alike", "cc-by-sa"),
    ("CC BY No_Derivs", "cc-by-nd"),
    ("CC BY Non.Commercial 4.0", "cc-by-nc"),
    ("Public domain, Non_Commercial use only", "inconnue"),
    ("Public domain, Share_Alike", "inconnue"),
])
def test_normaliser_licence_separateurs_exotiques(brute, attendue):
    assert licences.normaliser(brute) == attendue


@pytest.mark.parametrize("brute, attendue", [        # un mot qui commence par nc/sa/nd n'est pas une restriction
    ("CC BY - Sandra Martin", "cc-by"),
    ("CC BY / Ndiaye", "cc-by"),
    ("CC BY. Ncube", "cc-by"),
    ("CC BY, voir sa page", "cc-by"),                 # seul ce qui suit immédiatement « BY » compte
    ("﻿CC BY 4.0", "cc-by"),
    ("​pexels", "pexels"),
])
def test_normaliser_licence_separateurs_garde_fous(brute, attendue):
    assert licences.normaliser(brute) == attendue


# --- sources

def test_wikimedia_decode_les_entites_html(monkeypatch):
    _faux_reseau(monkeypatch, {"https://commons.wikimedia.org/w/api.php": {"query": {"pages": {
        "9": {"pageid": 9, "index": 1, "title": "File:X.webm", "imageinfo": [{
            "url": "https://upload.wikimedia.org/x.webm", "descriptionurl": "https://commons/x",
            "extmetadata": {"LicenseShortName": {"value": "CC BY 4.0"},
                            "Artist": {"value": '<a href="x">Tom &amp; Jerry &#039;s</a>'},
                            "ObjectName": {"value": "Caf&eacute; &lt;b&gt;"}}}]}}}}})
    r = sources.SOURCES["wikimedia"]().rechercher("x", 1)[0]
    assert r.auteur == "Tom & Jerry 's" and r.titre == "Café <b>"


def _panne(url, params):
    raise reseau.ErreurReseau(f"HTTP 503 sur {url}")


def test_archive_ignore_un_element_en_panne_et_garde_les_autres(monkeypatch):
    _faux_reseau(monkeypatch, {
        "https://archive.org/advancedsearch.php": {"response": {"docs": [
            {"identifier": "casse", "title": "A", "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"},
            {"identifier": "bon", "title": "B", "licenseurl": "http://creativecommons.org/publicdomain/mark/1.0/"}]}},
        "https://archive.org/metadata/casse": _panne,
        "https://archive.org/metadata/bon": {"files": [{"name": "bon.mp4", "size": "1000", "length": "10"}]}})
    resultats = sources.SOURCES["archive"]().rechercher("x", 2)
    assert [r.id for r in resultats] == ["bon"]


def test_nasa_ignore_un_element_en_panne_et_garde_les_autres(monkeypatch):
    _faux_reseau(monkeypatch, {
        "https://images-api.nasa.gov/search": {"collection": {"items": [
            {"href": "https://images-assets.nasa.gov/video/A/collection.json", "data": [{"nasa_id": "A"}]},
            {"href": "https://images-assets.nasa.gov/video/B/collection.json", "data": [{"nasa_id": "B"}]}]}},
        "https://images-assets.nasa.gov/video/A/collection.json": _panne,
        "https://images-assets.nasa.gov/video/B/collection.json": ["http://images-assets.nasa.gov/video/B/B~medium.mp4"]})
    assert [r.id for r in sources.SOURCES["nasa"]().rechercher("x", 2)] == ["B"]


def test_la_requete_de_recherche_en_panne_reste_une_erreur(monkeypatch):
    """Seul l'élément isolé est ignoré : une recherche qui échoue remonte, pour que build la consigne."""
    _faux_reseau(monkeypatch, {"https://archive.org/advancedsearch.php": _panne})
    with pytest.raises(reseau.ErreurReseau):
        sources.SOURCES["archive"]().rechercher("x", 2)


# --- search : fiches et encodeur

def _corpus_indexe(tmp_path, monkeypatch, capsys):
    dossier = _corpus_a_deux_emplacements(tmp_path)
    racine = str(tmp_path / "corpus")
    _avec_encodeur_factice(monkeypatch)
    assert corpus_cli.main(["index", "savoir-faire", "--racine", racine]) == 0
    capsys.readouterr()
    return dossier, racine


@pytest.mark.parametrize("contenu", ["{pas du json", "[1, 2]", '"texte"', "null"])
def test_search_fiche_illisible_meme_code_que_list_et_credits(tmp_path, monkeypatch, capsys, contenu):
    dossier, racine = _corpus_indexe(tmp_path, monkeypatch, capsys)
    (dossier / "clips" / "factice-chameau.json").write_text(contenu, encoding="utf-8")
    assert corpus_cli.main(["list", "savoir-faire", "--racine", racine]) == 1
    capsys.readouterr()
    assert corpus_cli.main(["search", "savoir-faire", "un chameau", "--racine", racine]) == 1
    erreur = capsys.readouterr().err
    assert erreur.startswith("ERREUR : ") and "factice-chameau.json" in erreur
    assert not (dossier / "selections.json").exists()


def test_search_encodeur_en_echec_est_une_erreur_propre(tmp_path, monkeypatch, capsys):
    dossier, racine = _corpus_indexe(tmp_path, monkeypatch, capsys)

    class Tombe(EncodeurFactice):
        def texte(self, texte):
            raise RuntimeError("CUDA out of memory")

    monkeypatch.setattr(corpus_cli, "_encodeur", lambda args: Tombe())
    assert corpus_cli.main(["search", "savoir-faire", "un chameau", "--racine", racine]) == 2
    assert "CUDA" in capsys.readouterr().err
