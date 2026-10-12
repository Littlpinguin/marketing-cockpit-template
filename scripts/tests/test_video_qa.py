"""Tests de 08-video/scripts/qa-video.py (QA mesurable d'un rendu vidéo).

Les fonctions d'analyse sont pures et se testent sans ffmpeg ; deux tests de
bout en bout fabriquent une vidéo synthétique (mire, noir, aplat figé) et se
sautent si ffmpeg est absent.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "08-video" / "scripts" / "qa-video.py"
PLATEFORMES = REPO / "08-video" / "scripts" / "plateformes.toml"
FORMATS = REPO / "08-video" / "formats.md"


def _charger():
    spec = importlib.util.spec_from_file_location("qa_video", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa = _charger()
requiert_ffmpeg = pytest.mark.skipif(
    not (shutil.which("ffmpeg") and shutil.which("ffprobe")), reason="ffmpeg absent")


# ------------------------------------------------------------------ plateformes

def test_plateformes_nommees_dans_formats():
    plateformes = tomllib.loads(PLATEFORMES.read_text(encoding="utf-8"))
    formats = FORMATS.read_text(encoding="utf-8")
    assert set(plateformes) == {"reels", "tiktok", "shorts", "linkedin"}
    for cle, conf in plateformes.items():
        assert conf["nom"] in formats, f"{cle} : « {conf['nom']} » absent de formats.md"


def test_plateformes_champs_obligatoires():
    for cle, conf in qa.charger_plateformes(PLATEFORMES).items():
        for champ in ("nom", "formats", "duree_max", "debit_min_kbps", "lufs", "crete_dbtp"):
            assert champ in conf, f"{cle} : champ {champ} manquant"
        for fmt in conf["formats"]:
            largeur, hauteur = fmt.split("x")
            assert int(largeur) > 0 and int(hauteur) > 0


# ------------------------------------------------------------------ analyse pure

def test_parse_ffprobe_inverse_les_dimensions_d_une_video_tournee():
    donnees = {
        "streams": [
            {"codec_type": "video", "codec_name": "h264", "pix_fmt": "yuv420p",
             "width": 1920, "height": 1080, "side_data_list": [{"rotation": -90}]},
            {"codec_type": "audio", "codec_name": "aac"},
        ],
        "format": {"duration": "12.5", "bit_rate": "9000000"},
    }
    resume = qa.parse_ffprobe(donnees)
    assert (resume["video"]["largeur"], resume["video"]["hauteur"]) == (1080, 1920)
    assert resume["duree"] == 12.5 and resume["debit"] == 9_000_000
    assert resume["audio"] == {"codec": "aac"}


def test_parse_ffprobe_ignore_la_vignette_attachee():
    donnees = {"streams": [
        {"codec_type": "video", "codec_name": "mjpeg", "width": 300, "height": 300,
         "disposition": {"attached_pic": 1}},
        {"codec_type": "video", "codec_name": "h264", "pix_fmt": "yuv420p",
         "width": 1080, "height": 1920, "tags": {"rotate": "0"}},
    ], "format": {"duration": "3"}}
    resume = qa.parse_ffprobe(donnees)
    assert resume["video"]["codec"] == "h264" and resume["audio"] is None


def test_parse_ebur128_prend_le_resume_final():
    stderr = (
        "[Parsed_ebur128_0 @ 0x1] t: 1.0 TARGET:-23 LUFS M: -20.0 S: -21.0 I: -19.0 LUFS LRA: 0.0 LU\n"
        "[Parsed_ebur128_0 @ 0x1] Summary:\n\n"
        "  Integrated loudness:\n    I:         -14.3 LUFS\n    Threshold: -24.5 LUFS\n\n"
        "  True peak:\n    Peak:       -1.2 dBFS\n"
    )
    assert qa.parse_ebur128(stderr) == {"integre": -14.3, "crete": -1.2}
    assert qa.parse_ebur128("rien") == {"integre": None, "crete": None}


def test_parse_intervalles_complete_un_fige_jusqu_a_la_fin():
    stderr = (
        "[freezedetect @ 0x1] lavfi.freezedetect.freeze_start: 1.5\n"
        "[freezedetect @ 0x1] lavfi.freezedetect.freeze_duration: 2\n"
        "[freezedetect @ 0x1] lavfi.freezedetect.freeze_end: 3.5\n"
        "[freezedetect @ 0x1] lavfi.freezedetect.freeze_start: 8\n"
    )
    assert qa.parse_intervalles(stderr, "freezedetect", 10.0) == [(1.5, 3.5), (8.0, 10.0)]


def test_parse_intervalles_noir_et_silence():
    noir = "[blackdetect @ 0x1] black_start:2 black_end:2.5 black_duration:0.5\n"
    assert qa.parse_intervalles(noir, "blackdetect", 6.0) == [(2.0, 2.5)]
    silence = ("[silencedetect @ 0x1] silence_start: 3.2\n"
               "[silencedetect @ 0x1] silence_end: 5 | silence_duration: 1.8\n")
    assert qa.parse_intervalles(silence, "silencedetect", 6.0) == [(3.2, 5.0)]
    with pytest.raises(ValueError):
        qa.parse_intervalles("", "inconnu", 1.0)


def test_coupes_et_durees_de_plans():
    stderr = ("[Parsed_showinfo_1 @ 0x1] n:   0 pts:  60 pts_time:2.0 duration:1\n"
              "[Parsed_showinfo_1 @ 0x1] n:   1 pts: 135 pts_time:4.5 duration:1\n")
    coupes = qa.parse_coupes(stderr)
    assert coupes == [2.0, 4.5]
    assert qa.durees_de_plans(coupes, 6.0) == [2.0, 2.5, 1.5]
    assert qa.durees_de_plans([], 3.0) == [3.0]


def _boite(nom: bytes, charge: bytes = b"") -> bytes:
    return (8 + len(charge)).to_bytes(4, "big") + nom + charge


def test_moov_avant_mdat():
    faststart = _boite(b"ftyp", b"isom") + _boite(b"moov", b"x" * 20) + _boite(b"mdat", b"y" * 50)
    tardif = _boite(b"ftyp", b"isom") + _boite(b"mdat", b"y" * 50) + _boite(b"moov")
    assert qa.moov_avant_mdat(io.BytesIO(faststart)) is True
    assert qa.moov_avant_mdat(io.BytesIO(tardif)) is False
    assert qa.moov_avant_mdat(io.BytesIO(b"pas une video")) is None


def test_couverture():
    assert qa.couverture("Bonjour à tous, voici l'offre", "bonjour a tous voici l offre") == 1.0
    assert qa.couverture("un deux trois quatre", "un deux") == 0.5
    assert qa.couverture("", "n'importe quoi") == 1.0


def test_texte_attendu_lit_la_colonne_voix():
    script = ("# Script\n\n| t | Plan | Texte à l'écran | Audio/VO |\n|---|---|---|---|\n"
              "| 0-3 s | face | Accroche | Bonjour à tous |\n"
              "| 3-8 s | b-roll | Chiffre | voici le chiffre |\n\nNotes de fin.\n")
    assert qa.texte_attendu(script, ".md") == "Bonjour à tous voici le chiffre"
    assert qa.texte_attendu("tel quel", ".txt") == "tel quel"
    assert "Bonjour" in qa.texte_attendu("# Titre\n\nBonjour **à** tous", ".md")


def test_lire_transcription_json(tmp_path):
    segments = tmp_path / "w.json"
    segments.write_text(json.dumps({"transcription": [{"text": "bonjour"}, {"text": " à tous"}]}))
    assert qa.lire_transcription(segments).split() == ["bonjour", "à", "tous"]
    simple = tmp_path / "s.json"
    simple.write_text(json.dumps({"text": "salut"}))
    assert qa.lire_transcription(simple) == "salut"
    mauvais = tmp_path / "m.json"
    mauvais.write_text("[1, 2]")
    with pytest.raises(ValueError):
        qa.lire_transcription(mauvais)


# ------------------------------------------------------------------ évaluation

def _mesures(**surcharges):
    base = {
        "probe": {"duree": 30.0, "debit": 9_000_000,
                  "video": {"codec": "h264", "pix_fmt": "yuv420p", "largeur": 1080,
                            "hauteur": 1920, "debit": 8_500_000},
                  "audio": {"codec": "aac"}},
        "loudness": {"integre": -14.2, "crete": -2.0},
        "noirs": [], "figes": [], "silences": [], "plans": [2.0] * 15,
        "moov_avant_mdat": True,
    }
    base.update(surcharges)
    return base


def _ids(constats, niveau=None):
    return {c.id for c in constats if niveau is None or c.niveau == niveau}


PLATEFORMES_CONF = qa.charger_plateformes(PLATEFORMES)


def test_rendu_conforme_sans_erreur():
    constats = qa.evaluer(_mesures(), {"plateforme": PLATEFORMES_CONF["reels"],
                                       "nom_plateforme": "reels", "duree": 30})
    assert _ids(constats, "erreur") == set()
    assert "rythme" in _ids(constats, "info")


def test_duree_hors_tolerance():
    assert "duree" in _ids(qa.evaluer(_mesures(), {"duree": 25}), "erreur")
    assert "duree" not in _ids(qa.evaluer(_mesures(), {"duree": 29}))


def test_format_codec_et_debit():
    m = _mesures()
    m["probe"]["video"].update({"largeur": 1920, "hauteur": 1080, "codec": "hevc", "debit": 2_000_000})
    constats = qa.evaluer(m, {"plateforme": PLATEFORMES_CONF["reels"], "nom_plateforme": "reels"})
    assert {"format", "codec"} <= _ids(constats, "erreur")
    assert "debit" in _ids(constats, "avertissement")


def test_loudness():
    assert "loudness" in _ids(qa.evaluer(_mesures(loudness={"integre": -20.0, "crete": -3.0}), {}), "erreur")
    assert "loudness" in _ids(qa.evaluer(_mesures(loudness={"integre": -14.0, "crete": -0.5}), {}), "erreur")


def test_noir_tolere_en_ouverture_et_fermeture():
    assert "noir" not in _ids(qa.evaluer(_mesures(noirs=[(0.0, 0.4), (29.2, 30.0)]), {}))
    assert "noir" in _ids(qa.evaluer(_mesures(noirs=[(12.0, 12.3)]), {}), "erreur")


def test_fige_silence_et_plan_long():
    constats = qa.evaluer(_mesures(figes=[(5.0, 8.0)], silences=[(10.0, 12.0)],
                                   plans=[2.0, 6.0, 22.0]), {})
    assert {"fige", "silence", "plan-long"} <= _ids(constats, "avertissement")


def test_max_plan_zero_desactive_le_controle():
    assert "plan-long" not in _ids(qa.evaluer(_mesures(plans=[30.0]), {"max_plan": 0}))


def test_video_muette():
    m = _mesures()
    m["probe"]["audio"] = None
    m.pop("loudness")
    assert "flux-audio" in _ids(qa.evaluer(m, {}), "erreur")
    assert "flux-audio" not in _ids(qa.evaluer(m, {"sans_audio": True}))


def test_transcription():
    attendu = "bonjour à tous voici notre offre de printemps"
    assert "transcription-indisponible" in _ids(
        qa.evaluer(_mesures(attendu=attendu, transcription=None), {}), "info")
    assert "transcription-vide" in _ids(
        qa.evaluer(_mesures(attendu=attendu, transcription=""), {}), "erreur")
    assert "transcription-couverture" in _ids(
        qa.evaluer(_mesures(attendu=attendu, transcription="bonjour à tous"), {}), "erreur")
    assert not _ids(qa.evaluer(_mesures(attendu=attendu, transcription=attendu), {}), "erreur")


# ------------------------------------------------------------------ bout en bout

def _video_synthetique(chemin: Path, *, audio: bool = True) -> None:
    """1080x1920, 6 s : mire 0-2 s, noir 2-2,5 s, aplat figé 2,5-5,5 s, mire 5,5-6 s."""
    graphe = ("testsrc2=s=1080x1920:r=30:d=2[a];color=c=black:s=1080x1920:r=30:d=0.5[b];"
              "color=c=0x1E40AF:s=1080x1920:r=30:d=3[c];testsrc2=s=1080x1920:r=30:d=0.5[d];"
              "[a][b][c][d]concat=n=4:v=1:a=0[v]")
    commande = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
    if audio:
        commande += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=6"]
    commande += ["-filter_complex", graphe, "-map", "[v]"]
    if audio:
        commande += ["-map", "0:a", "-c:a", "aac"]
    commande += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(chemin)]
    subprocess.run(commande, check=True)


def _lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


@requiert_ffmpeg
def test_bout_en_bout(tmp_path):
    video = tmp_path / "exports" / "demo-reels.mp4"
    video.parent.mkdir()
    _video_synthetique(video)
    script = tmp_path / "script.txt"
    script.write_text("bonjour à tous", encoding="utf-8")
    transcript = tmp_path / "t.txt"
    transcript.write_text("bonjour à tous", encoding="utf-8")
    res = _lancer(str(video), "--plateforme", "reels", "--duree", "6", "--script", str(script),
                  "--transcript", str(transcript), "--format", "json")
    assert res.returncode == 1, res.stderr
    rapport = json.loads(res.stdout)
    ids = {c["id"] for c in rapport["constats"]}
    assert {"noir", "fige"} <= ids
    assert not ids & {"duree", "format", "codec", "transcription-couverture", "flux-audio"}
    dossier = tmp_path / "qa" / "demo-reels"
    for nom in ("planche.jpg", "rapport.json", "rapport.md", "plan-01.jpg"):
        assert (dossier / nom).exists(), nom


@requiert_ffmpeg
def test_video_sans_flux_audio(tmp_path):
    video = tmp_path / "muet.mp4"
    _video_synthetique(video, audio=False)
    res = _lancer(str(video), "--format", "json", "--sortie", str(tmp_path / "qa"))
    assert res.returncode == 1, res.stderr
    assert "flux-audio" in {c["id"] for c in json.loads(res.stdout)["constats"]}
    res = _lancer(str(video), "--sans-audio", "--format", "json", "--sortie", str(tmp_path / "qa2"))
    assert "flux-audio" not in {c["id"] for c in json.loads(res.stdout)["constats"]}


def test_erreurs_d_usage_code_2(tmp_path):
    assert _lancer(str(tmp_path / "absent.mp4")).returncode == 2
    factice = tmp_path / "f.mp4"
    factice.write_bytes(b"x")
    assert _lancer(str(factice), "--plateforme", "inconnue").returncode == 2


# ------------------------------------------------------------------ une mesure qui ne tourne pas ne valide jamais

def test_sans_piste_audio_la_transcription_n_est_pas_jugee():
    """Sans flux audio et sans --transcript, la couverture n'est pas mesurable : flux-audio le dit déjà."""
    m = _mesures(attendu="bonjour à tous")
    m["probe"]["audio"] = None
    m.pop("loudness")
    ids = _ids(qa.evaluer(m, {"sans_audio": True}))
    assert not ids & {"transcription-vide", "transcription-indisponible", "transcription-couverture"}
    ids = _ids(qa.evaluer(m, {}))
    assert "flux-audio" in ids
    assert not ids & {"transcription-vide", "transcription-indisponible", "transcription-couverture"}


def test_echec_de_transcription_a_son_propre_message():
    m = _mesures(attendu="bonjour à tous", transcription=None,
                 transcription_echec="code 1")
    constat = next(c for c in qa.evaluer(m, {}) if c.id == "transcription-indisponible")
    assert constat.niveau == "info" and "whisper-cli en échec" in constat.message
    sans_echec = next(c for c in qa.evaluer(_mesures(attendu="bonjour", transcription=None), {})
                      if c.id == "transcription-indisponible")
    assert "en échec" not in sans_echec.message


def test_valeurs_non_finies_serialisees_en_null():
    texte = qa.serialiser_json({"loudness": {"integre": -70.0, "crete": float("-inf")},
                                "liste": [float("inf"), float("nan"), 1.5]})
    assert "Infinity" not in texte and "NaN" not in texte
    assert json.loads(texte) == {"loudness": {"integre": -70.0, "crete": None},
                                 "liste": [None, None, 1.5]}
    # le constat reste calculé sur la vraie valeur
    constats = qa.evaluer(_mesures(loudness={"integre": float("-inf"), "crete": float("-inf")}), {})
    assert "loudness" in _ids(constats, "erreur")


def test_dossier_sortie_resout_le_chemin(tmp_path, monkeypatch):
    (tmp_path / "exports").mkdir()
    monkeypatch.chdir(tmp_path / "exports")
    assert qa.dossier_sortie(Path("demo.mp4")) == (tmp_path / "qa" / "demo").resolve()


def test_plateformes_illisibles_code_2(tmp_path):
    factice = tmp_path / "f.mp4"
    factice.write_bytes(b"x")
    manquant = _lancer(str(factice), "--plateforme", "reels", "--plateformes", str(tmp_path / "absent.toml"))
    assert manquant.returncode == 2 and "ERREUR" in manquant.stderr
    assert "Traceback" not in manquant.stderr
    casse = tmp_path / "casse.toml"
    casse.write_text("[reels\nnom = = 1", encoding="utf-8")
    invalide = _lancer(str(factice), "--plateforme", "reels", "--plateformes", str(casse))
    assert invalide.returncode == 2 and "ERREUR" in invalide.stderr
    assert "Traceback" not in invalide.stderr


# ---- bout en bout avec de fausses commandes ffmpeg / whisper-cli placées en tête du PATH

@pytest.fixture(scope="module")
def video_av(tmp_path_factory):
    chemin = tmp_path_factory.mktemp("av") / "demo.mp4"
    _video_synthetique(chemin)
    return chemin


@pytest.fixture(scope="module")
def video_muette(tmp_path_factory):
    chemin = tmp_path_factory.mktemp("muette") / "muet.mp4"
    _video_synthetique(chemin, audio=False)
    return chemin


def _fausse_commande(dossier: Path, nom: str, corps: str) -> Path:
    """Crée un script shell exécutable `nom` dans `dossier` ; rend `dossier`."""
    dossier.mkdir(exist_ok=True)
    chemin = dossier / nom
    chemin.write_text("#!/bin/sh\n" + corps + "\n", encoding="utf-8")
    chemin.chmod(0o755)
    return dossier


def _ffmpeg_truque(dossier: Path, avant: str) -> Path:
    """Faux ffmpeg : exécute `avant` (shell, qui peut quitter), sinon délègue au vrai ffmpeg."""
    return _fausse_commande(dossier, "ffmpeg", f'{avant}\nexec "{shutil.which("ffmpeg")}" "$@"')


def _lancer_env(env: dict[str, str], *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          env={**os.environ, **env}, cwd=cwd)


def _devant_le_path(dossier: Path) -> dict[str, str]:
    return {"PATH": f"{dossier}{os.pathsep}{os.environ['PATH']}"}


def _json_strict(texte: str):
    def refuser(constante):
        raise AssertionError(f"JSON invalide : {constante}")
    return json.loads(texte, parse_constant=refuser)


@requiert_ffmpeg
@pytest.mark.parametrize("avant, passe", [
    ("exit 1", "blackdetect"),
    ('case "$*" in *select=*) echo boom >&2; exit 1;; esac', "plans"),
    ('case "$*" in *ebur128*) echo boom >&2; exit 1;; esac', "ebur128"),
    ('case "$*" in *ebur128*) exit 0;; esac', "ebur128"),
], ids=["tout-echoue", "passe-plans", "passe-audio", "audio-sans-mesure"])
def test_mesure_qui_ne_tourne_pas_donne_code_2(tmp_path, video_av, avant, passe):
    stubs = _ffmpeg_truque(tmp_path / "bin", avant)
    res = _lancer_env(_devant_le_path(stubs), str(video_av), "--plateforme", "reels",
                      "--format", "json", "--sortie", str(tmp_path / "qa"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "ERREUR" in res.stderr and passe in res.stderr
    assert "Traceback" not in res.stderr
    assert "erreur(s)" not in res.stdout and "constats" not in res.stdout


@requiert_ffmpeg
def test_planche_en_echec_ne_fait_pas_echouer_le_rapport(tmp_path, video_av):
    stubs = _ffmpeg_truque(tmp_path / "bin", 'case " $* " in *" -ss "*) exit 1;; esac')
    res = _lancer_env(_devant_le_path(stubs), str(video_av), "--format", "json",
                      "--sortie", str(tmp_path / "qa"))
    assert res.returncode in (0, 1), res.stderr
    rapport = _json_strict(res.stdout)
    constat = next(c for c in rapport["constats"] if c["id"] == "planche-indisponible")
    assert constat["niveau"] == "info" and rapport["planche"] is None


@requiert_ffmpeg
def test_whisper_en_echec_message_distinct(tmp_path, video_av):
    modele = tmp_path / "modele.bin"
    modele.write_bytes(b"x")
    stubs = _fausse_commande(tmp_path / "bin", "whisper-cli", "echo boom >&2; exit 1")
    script = tmp_path / "script.txt"
    script.write_text("bonjour à tous", encoding="utf-8")
    res = _lancer_env({**_devant_le_path(stubs), "WHISPER_MODEL": str(modele)}, str(video_av),
                      "--script", str(script), "--format", "json", "--sortie", str(tmp_path / "qa"))
    assert res.returncode in (0, 1), res.stderr
    constat = next(c for c in _json_strict(res.stdout)["constats"] if c["id"] == "transcription-indisponible")
    assert constat["niveau"] == "info" and "whisper-cli en échec" in constat["message"]


@requiert_ffmpeg
def test_stderr_non_utf8_ne_plante_pas(tmp_path, video_av):
    stubs = _ffmpeg_truque(tmp_path / "bin", r"printf 'titre \351\377 invalide\n' >&2")
    res = _lancer_env(_devant_le_path(stubs), str(video_av), "--format", "json",
                      "--sortie", str(tmp_path / "qa"))
    assert "Traceback" not in res.stderr, res.stderr
    assert res.returncode in (0, 1)
    assert {"noir", "fige"} <= {c["id"] for c in _json_strict(res.stdout)["constats"]}


@requiert_ffmpeg
def test_sortie_non_inscriptible_code_2(tmp_path, video_av):
    bloc = tmp_path / "bloc"
    bloc.write_text("un fichier, pas un dossier", encoding="utf-8")
    res = _lancer(str(video_av), "--format", "json", "--sortie", str(bloc / "qa"))
    assert res.returncode == 2, res.stdout + res.stderr
    assert "ERREUR" in res.stderr and "Traceback" not in res.stderr


@requiert_ffmpeg
def test_sans_audio_et_script_sur_video_muette(tmp_path, video_muette):
    script = tmp_path / "script.txt"
    script.write_text("bonjour à tous", encoding="utf-8")
    res = _lancer(str(video_muette), "--sans-audio", "--script", str(script), "--format", "json",
                  "--sortie", str(tmp_path / "qa"))
    ids = {c["id"] for c in _json_strict(res.stdout)["constats"]}
    assert not ids & {"transcription-vide", "transcription-indisponible", "flux-audio"}


@requiert_ffmpeg
def test_silence_numerique_donne_un_json_valide(tmp_path):
    video = tmp_path / "silence.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-f", "lavfi", "-i", "testsrc2=s=1080x1920:r=30", "-t", "3",
                    "-c:a", "aac", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    str(video)], check=True)
    res = _lancer(str(video), "--format", "json", "--sortie", str(tmp_path / "qa"))
    rapport = _json_strict(res.stdout)
    assert rapport["mesures"]["loudness"]["crete"] is None
    assert "loudness" in {c["id"] for c in rapport["constats"]}
    _json_strict((tmp_path / "qa" / "rapport.json").read_text(encoding="utf-8"))


@requiert_ffmpeg
def test_chemins_resolus_depuis_un_chemin_relatif(tmp_path, video_av):
    exports = tmp_path / "projet" / "exports"
    exports.mkdir(parents=True)
    shutil.copy(video_av, exports / "demo.mp4")
    res = _lancer_env({}, "demo.mp4", "--format", "json", cwd=exports)
    rapport = _json_strict(res.stdout)
    assert Path(rapport["video"]).is_absolute()
    assert Path(rapport["planche"]).is_absolute()
    assert (tmp_path / "projet" / "qa" / "demo" / "rapport.json").exists()
