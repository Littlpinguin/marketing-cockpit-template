#!/usr/bin/env python3
"""QA mesurable d'un rendu vidéo : ce qui se mesure avec ffprobe et ffmpeg.

Le script mesure ; il ne juge ni le goût, ni le message, ni la marque. C'est
le travail de l'agent video-reviewer, qui lit la planche produite ici.

Usage :
    python3 08-video/scripts/qa-video.py 08-video/projets/<slug>/exports/<slug>-reels.mp4 \\
        --plateforme reels --duree 45 --script 08-video/projets/<slug>/script.md
    python3 08-video/scripts/qa-video.py <video.mp4> --sans-audio --format json

Ce qu'il contrôle
-----------------
  flux-video, flux-audio      flux absent (audio non exigé avec --sans-audio)      erreur
  piste-muette                piste audio sur une vidéo déclarée muette             info
                              (--sans-audio) : son non jugé (loudness, silence)
  duree                       écart à --duree supérieur à 5 %                       erreur
  duree-max                   plus long que la limite de la plateforme              erreur
  format                      résolution hors des formats de la plateforme          erreur
  codec                       vidéo autre que H.264 yuv420p, audio autre que AAC    erreur
  faststart                   atome moov après mdat (lecture web retardée)          avertissement
  debit                       débit vidéo sous le plancher de la plateforme         avertissement
  loudness                    intégré hors cible ±1 LU, ou crête vraie trop haute   erreur
  noir                        plage noire hors ouverture (0,5 s) et fermeture (1 s) erreur
  fige                        image figée 2 s ou plus : risque de diaporama         avertissement
  silence                     silence de 1,5 s ou plus hors de la dernière seconde  avertissement
  plan-long                   plus de --max-plan s sans changement de plan          avertissement
  rythme                      nombre de plans, médiane, plan le plus long           info
  transcription-indisponible  ni --transcript, ni whisper-cli avec WHISPER_MODEL,   info
                              ou whisper-cli en échec (message distinct)
  transcription-vide          aucun mot transcrit alors qu'un script est fourni     erreur
  transcription-couverture    moins de 80 % des mots du script retrouvés            erreur
  planche-indisponible        images ou planche contact non extraites               info
  planche-partielle           plus de 60 plans : planche limitée aux 60 premiers    info

La transcription n'est pas jugée sur une vidéo sans flux audio, ni sur une vidéo
déclarée muette (--sans-audio), sauf si --transcript est fourni : sans piste,
flux-audio signale déjà le manque (sauf avec --sans-audio).

Une mesure qui ne tourne pas ne valide jamais : si une passe ffmpeg échoue ou ne
rend rien d'exploitable, le script s'arrête en erreur d'outil (code 2) au lieu de
rendre un rapport vide. Seule la planche contact est facultative.

Sorties : rapport texte ou JSON sur la sortie standard ; dans --sortie (défaut :
qa/<nom de la vidéo>/ à côté du dossier exports/), une image au milieu de chaque
plan (plan-NN.jpg), une planche contact (planche.jpg), rapport.md et rapport.json.
Un export qui est un lien symbolique n'est pas suivi : le dossier qa/ reste dans
le projet et porte le nom du lien.
Les valeurs non finies (crête de -inf sur un silence numérique) sont écrites null.

Codes de sortie : 0 aucun constat bloquant, 1 constat(s) bloquant(s), 2 erreur
d'usage ou d'outil (fichier absent, ffprobe introuvable, plateforme inconnue ou
fichier des plateformes illisible, passe ffmpeg en échec, dossier de sortie
non inscriptible).
"""
# Python 3.11 minimum (tomllib, comme le reste du dépôt). Pas de « from __future__ import
# annotations » : @dataclass résout alors le module de la classe dans sys.modules, ce qui
# échoue quand le script est chargé par importlib sans y être enregistré. Les annotations
# ci-dessous sont donc évaluées à l'exécution.
import argparse
import difflib
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import tomllib
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, BinaryIO

RACINE = Path(__file__).resolve().parents[2]
PLATEFORMES_DEFAUT = Path(__file__).resolve().parent / "plateformes.toml"

TOLERANCE_DUREE = 0.05
TOLERANCE_LUFS = 1.0
LUFS_DEFAUT = -14.0
CRETE_DEFAUT = -1.5
OUVERTURE_NOIR = 0.5
FERMETURE_NOIR = 1.0
NOIR_MIN = 0.1
FIGE_MIN = 2.0
SILENCE_MIN = 1.5
MAX_PLAN_DEFAUT = 4.0
SEUIL_SCENE = 0.3
COUVERTURE_MIN = 0.80
MAX_IMAGES = 60


@dataclass
class Constat:
    niveau: str            # "erreur", "avertissement" ou "info"
    id: str
    message: str
    t: float | None = None


class ErreurOutil(Exception):
    """ffprobe ou ffmpeg absent ou en échec, fichier illisible."""


class EchecTranscription(Exception):
    """whisper-cli (ou l'extraction audio qui le précède) a tourné et a échoué."""


# ---------------------------------------------------------------- plateformes

def charger_plateformes(chemin: Path = PLATEFORMES_DEFAUT) -> dict[str, dict[str, Any]]:
    with Path(chemin).open("rb") as fichier:
        return tomllib.load(fichier)


# ---------------------------------------------------------------- analyse pure

def _flottant(valeur: Any) -> float | None:
    try:
        return float(valeur)
    except (TypeError, ValueError):
        return None


def _entier(valeur: Any) -> int | None:
    try:
        return int(valeur)
    except (TypeError, ValueError):
        return None


def _rotation(flux: dict[str, Any]) -> int:
    for donnee in flux.get("side_data_list") or []:
        if "rotation" in donnee:
            return int(float(donnee["rotation"]))
    tag = (flux.get("tags") or {}).get("rotate")
    return int(float(tag)) if tag else 0


def parse_ffprobe(donnees: dict[str, Any]) -> dict[str, Any]:
    """Résume la sortie JSON de ffprobe : durée, flux vidéo et audio, débit.

    Les dimensions rendues sont celles affichées : une rotation de 90 ou 270
    degrés (vidéo de smartphone) les inverse. Une vignette attachée (pochette)
    n'est pas le flux vidéo : son index absolu est gardé pour que les passes
    ffmpeg visent le même flux (voir flux_video).
    """
    flux = donnees.get("streams", [])
    video = next((f for f in flux if f.get("codec_type") == "video"
                  and not (f.get("disposition") or {}).get("attached_pic")), None)
    audio = next((f for f in flux if f.get("codec_type") == "audio"), None)
    fmt = donnees.get("format", {})
    duree = _flottant(fmt.get("duration")) or _flottant((video or {}).get("duration")) or 0.0
    resume: dict[str, Any] = {"duree": duree, "video": None, "audio": None,
                              "debit": _entier(fmt.get("bit_rate"))}
    if video:
        largeur, hauteur = int(video.get("width", 0)), int(video.get("height", 0))
        if abs(_rotation(video)) % 180 == 90:
            largeur, hauteur = hauteur, largeur
        resume["video"] = {"codec": video.get("codec_name"), "pix_fmt": video.get("pix_fmt"),
                           "largeur": largeur, "hauteur": hauteur,
                           "debit": _entier(video.get("bit_rate")), "index": _entier(video.get("index"))}
    if audio:
        resume["audio"] = {"codec": audio.get("codec_name")}
    return resume


def flux_video(video: dict[str, Any]) -> str:
    """Spécificateur -map du flux vidéo retenu par parse_ffprobe.

    « 0:v:0 » viserait le premier flux vidéo du fichier, qui peut être une
    pochette attachée placée avant le vrai flux.
    """
    index = video.get("index")
    return f"0:{index}" if isinstance(index, int) else "0:v:0"


EBUR_I_RE = re.compile(r"\bI:\s+(-?[\d.]+|-inf)\s+LUFS")
EBUR_PEAK_RE = re.compile(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS")


def _db(texte: str) -> float:
    return float("-inf") if texte == "-inf" else float(texte)


def parse_ebur128(stderr: str) -> dict[str, float | None]:
    """Loudness intégrée et crête vraie, lues dans le résumé final d'ebur128."""
    integre = EBUR_I_RE.findall(stderr)
    crete = EBUR_PEAK_RE.findall(stderr)
    return {"integre": _db(integre[-1]) if integre else None,
            "crete": _db(crete[-1]) if crete else None}


def _apparier(debuts: list[float], fins: list[float], duree: float | None) -> list[tuple[float, float]]:
    paires = list(zip(debuts, fins))
    if duree is not None:
        paires += [(d, duree) for d in debuts[len(fins):]]
    return paires


def parse_intervalles(stderr: str, filtre: str, duree: float | None = None) -> list[tuple[float, float]]:
    """Intervalles (début, fin) relevés par blackdetect, freezedetect ou silencedetect.

    Un figé ou un silence qui dure jusqu'à la fin n'a pas de fin dans la sortie
    de ffmpeg : il est fermé à `duree`.
    """
    if filtre == "blackdetect":
        return [(float(a), float(b)) for a, b in
                re.findall(r"black_start:\s*(-?[\d.]+)\s+black_end:\s*(-?[\d.]+)", stderr)]
    if filtre == "freezedetect":
        return _apparier([float(x) for x in re.findall(r"freeze_start:\s*(-?[\d.]+)", stderr)],
                         [float(x) for x in re.findall(r"freeze_end:\s*(-?[\d.]+)", stderr)], duree)
    if filtre == "silencedetect":
        return _apparier([float(x) for x in re.findall(r"silence_start:\s*(-?[\d.]+)", stderr)],
                         [float(x) for x in re.findall(r"silence_end:\s*(-?[\d.]+)", stderr)], duree)
    raise ValueError(f"filtre inconnu : {filtre}")


SCENE_RE = re.compile(r"pts_time:\s*(-?[\d.]+)")


def parse_coupes(stderr: str) -> list[float]:
    """Instants des changements de plan relevés par select='gt(scene,…)',showinfo."""
    return sorted({round(float(t), 3) for t in SCENE_RE.findall(stderr) if float(t) > 0})


def durees_de_plans(coupes: list[float], duree: float) -> list[float]:
    bornes = [0.0] + [c for c in coupes if 0 < c < duree] + [duree]
    return [round(b - a, 3) for a, b in zip(bornes, bornes[1:]) if b - a > 0]


def moov_avant_mdat(flux: BinaryIO) -> bool | None:
    """Ordre des boîtes MP4 de premier niveau : True si moov précède mdat.

    Rend None si ni l'une ni l'autre n'est trouvée (fichier non MP4).
    """
    while True:
        entete = flux.read(8)
        if len(entete) < 8:
            return None
        taille = int.from_bytes(entete[:4], "big")
        nom = entete[4:8]
        if nom == b"moov":
            return True
        if nom == b"mdat":
            return False
        if taille == 1:
            etendue = flux.read(8)
            if len(etendue) < 8:
                return None
            reste = int.from_bytes(etendue, "big") - 16
        elif taille < 8:
            return None
        else:
            reste = taille - 8
        if reste < 0:
            return None
        flux.seek(reste, os.SEEK_CUR)


def mots(texte: str) -> list[str]:
    """Mots normalisés : minuscules, sans accents, alphanumériques."""
    decompose = unicodedata.normalize("NFKD", texte.lower())
    sans_accents = "".join(c for c in decompose if not unicodedata.combining(c))
    return re.findall(r"[a-z0-9]+", sans_accents)


def couverture(attendu: str, transcrit: str) -> float:
    """Part des mots du script retrouvés, dans l'ordre, dans la transcription."""
    a, b = mots(attendu), mots(transcrit)
    if not a:
        return 1.0
    blocs = difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks()
    return sum(bloc.size for bloc in blocs) / len(a)


ENTETE_VOIX_RE = re.compile(r"voix|\bvo\b|narration|audio", re.I)
SEPARATEUR_RE = re.compile(r"^\s*\|[\s:|-]+\|\s*$")


def _cellules(ligne: str) -> list[str]:
    return [c.strip() for c in ligne.strip().strip("|").split("|")]


def texte_attendu(contenu: str, suffixe: str) -> str:
    """Narration attendue : un .txt tel quel ; un .md, la colonne voix de son
    tableau minuté s'il en a une, sinon son texte débarrassé de la syntaxe."""
    if suffixe.lower() != ".md":
        return contenu
    lignes = contenu.splitlines()
    for index, ligne in enumerate(lignes[:-1]):
        if not ligne.strip().startswith("|") or not SEPARATEUR_RE.match(lignes[index + 1]):
            continue
        colonnes = [i for i, e in enumerate(_cellules(ligne)) if ENTETE_VOIX_RE.search(e)]
        if not colonnes:
            continue
        colonne = colonnes[-1]
        textes = []
        for suite in lignes[index + 2:]:
            if not suite.strip().startswith("|"):
                break
            cellules = _cellules(suite)
            if colonne < len(cellules) and cellules[colonne]:
                textes.append(cellules[colonne])
        return " ".join(textes)
    sans_code = re.sub(r"```.*?```", " ", contenu, flags=re.S)
    return re.sub(r"[#>*_`|\[\]()]", " ", sans_code)


def lire_transcription(chemin: Path) -> str:
    """Texte d'une transcription : .txt tel quel, .json de whisper (text, transcription ou segments)."""
    contenu = Path(chemin).read_text(encoding="utf-8")
    if Path(chemin).suffix.lower() != ".json":
        return contenu
    donnees = json.loads(contenu)
    if isinstance(donnees, dict):
        if isinstance(donnees.get("text"), str):
            return donnees["text"]
        for cle in ("transcription", "segments"):
            if isinstance(donnees.get(cle), list):
                return " ".join(str(s.get("text", "")).strip()
                                for s in donnees[cle] if isinstance(s, dict))
    raise ValueError(f"{chemin} : transcription JSON non reconnue (clés text, transcription ou segments)")


def evaluer(mesures: dict[str, Any], options: dict[str, Any]) -> list[Constat]:
    """Transforme les mesures en constats. Fonction pure : aucun accès disque."""
    constats: list[Constat] = []
    probe = mesures["probe"]
    duree = probe["duree"]
    video, audio = probe["video"], probe["audio"]
    conf = options.get("plateforme")
    nom = (conf or {}).get("nom") or options.get("nom_plateforme") or "plateforme"   # « Instagram Reels », pas « reels »

    if video is None:
        constats.append(Constat("erreur", "flux-video", "aucun flux vidéo"))
    sans_audio = bool(options.get("sans_audio"))
    if audio is None and not sans_audio:
        constats.append(Constat("erreur", "flux-audio",
                                "aucun flux audio (--sans-audio pour une vidéo muette assumée)"))
    if audio is not None and sans_audio:
        constats.append(Constat("info", "piste-muette",
                                "piste audio présente mais vidéo déclarée muette (--sans-audio) : "
                                "loudness et silences non jugés"))
    son_juge = audio is not None and not sans_audio

    attendue = options.get("duree")
    if attendue:
        ecart = abs(duree - attendue) / attendue
        if ecart > TOLERANCE_DUREE:
            constats.append(Constat("erreur", "duree",
                                    f"durée {duree:.2f} s pour {attendue:g} s attendues (écart {ecart:.0%})"))

    if conf:
        if conf.get("duree_max") and duree > conf["duree_max"]:
            constats.append(Constat("erreur", "duree-max",
                                    f"{duree:.1f} s dépasse la limite {nom} ({conf['duree_max']} s)"))
        if video:
            formats = [tuple(int(x) for x in f.split("x")) for f in conf.get("formats", [])]
            if formats and (video["largeur"], video["hauteur"]) not in formats:
                constats.append(Constat("erreur", "format",
                                        f"{video['largeur']}x{video['hauteur']} hors des formats {nom} : "
                                        + ", ".join(conf["formats"])))
            debit = video.get("debit") or probe.get("debit")
            plancher = conf.get("debit_min_kbps")
            if debit and plancher and debit < plancher * 1000:
                constats.append(Constat("avertissement", "debit",
                                        f"débit vidéo {debit // 1000} kb/s sous le plancher {nom} ({plancher} kb/s)"))

    if video and (video["codec"] != "h264" or video["pix_fmt"] != "yuv420p"):
        constats.append(Constat("erreur", "codec",
                                f"vidéo {video['codec']} {video['pix_fmt']} : H.264 yuv420p attendu"))
    if audio and audio["codec"] != "aac":
        constats.append(Constat("erreur", "codec", f"audio {audio['codec']} : AAC attendu"))
    if mesures.get("moov_avant_mdat") is False:
        constats.append(Constat("avertissement", "faststart",
                                "atome moov en fin de fichier : réencoder avec -movflags +faststart"))

    loudness = mesures.get("loudness")
    if son_juge and loudness:
        cible = (conf or {}).get("lufs", LUFS_DEFAUT)
        plafond = (conf or {}).get("crete_dbtp", CRETE_DEFAUT)
        integre, crete = loudness.get("integre"), loudness.get("crete")
        if integre is not None and abs(integre - cible) > TOLERANCE_LUFS:
            constats.append(Constat("erreur", "loudness",
                                    f"loudness intégrée {integre:.1f} LUFS pour {cible:g} ±{TOLERANCE_LUFS:g} attendus"))
        if crete is not None and crete > plafond:
            constats.append(Constat("erreur", "loudness",
                                    f"crête vraie {crete:.1f} dBTP au-dessus du plafond {plafond:g} dBTP"))

    for debut, fin in mesures.get("noirs", []):
        if fin - debut < NOIR_MIN or fin <= OUVERTURE_NOIR or debut >= duree - FERMETURE_NOIR:
            continue
        constats.append(Constat("erreur", "noir", f"plage noire de {fin - debut:.2f} s en cours de vidéo",
                                t=round(debut, 2)))
    for debut, fin in mesures.get("figes", []):
        if fin - debut >= FIGE_MIN:
            constats.append(Constat("avertissement", "fige",
                                    f"image figée {fin - debut:.1f} s : risque de diaporama si le mouvement était promis",
                                    t=round(debut, 2)))
    if son_juge:
        for debut, fin in mesures.get("silences", []):
            if fin - debut >= SILENCE_MIN and debut < duree - 1.0:
                constats.append(Constat("avertissement", "silence", f"silence de {fin - debut:.1f} s",
                                        t=round(debut, 2)))

    plans = mesures.get("plans") or []
    if plans:
        max_plan = options.get("max_plan", MAX_PLAN_DEFAUT)
        if max_plan and max_plan > 0:
            debut = 0.0
            for longueur in plans:
                if longueur > max_plan:
                    constats.append(Constat("avertissement", "plan-long",
                                            f"plan de {longueur:.1f} s sans changement (plafond {max_plan:g} s)",
                                            t=round(debut, 2)))
                debut += longueur
        constats.append(Constat("info", "rythme",
                                f"{len(plans)} plans, médiane {statistics.median(plans):.2f} s, "
                                f"plus long {max(plans):.2f} s"))

    attendu = mesures.get("attendu")
    transcrit = mesures.get("transcription")
    if attendu and not (not son_juge and transcrit is None):
        if transcrit is None:
            echec = mesures.get("transcription_echec")
            if echec:
                message = f"whisper-cli en échec ({echec}) : fidélité de la narration non mesurée"
            else:
                message = ("ni --transcript, ni whisper-cli avec WHISPER_MODEL : "
                           "fidélité de la narration non mesurée")
            constats.append(Constat("info", "transcription-indisponible", message))
        elif not mots(transcrit):
            constats.append(Constat("erreur", "transcription-vide", "aucun mot transcrit : audio absent ou muet"))
        else:
            taux = couverture(attendu, transcrit)
            if taux < COUVERTURE_MIN:
                constats.append(Constat("erreur", "transcription-couverture",
                                        f"{taux:.0%} des mots du script retrouvés (minimum {COUVERTURE_MIN:.0%}) : "
                                        "narration coupée ou divergente"))
    return constats


# ---------------------------------------------------------------- mesures (ffmpeg)

def executer(commande: list[str]) -> subprocess.CompletedProcess:
    # errors="replace" : ffmpeg recopie parfois des métadonnées dans un autre encodage que l'UTF-8.
    try:
        return subprocess.run(commande, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", check=False)
    except FileNotFoundError as err:
        raise ErreurOutil(f"{commande[0]} introuvable : installer ffmpeg (brew install ffmpeg)") from err


def exiger(res: subprocess.CompletedProcess, passe: str) -> None:
    """Une passe de mesure en échec n'est jamais ignorée : erreur d'outil, code de sortie 2."""
    if res.returncode != 0:
        # Les dernières lignes : les premières sont la bannière de version et de configuration.
        fin = " ".join(ligne.strip() for ligne in res.stderr.strip().splitlines()[-3:])[-300:]
        raise ErreurOutil(f"ffmpeg a échoué à la passe {passe} (code {res.returncode}) : {fin or 'aucun message'}")


def sonder(video: Path) -> dict[str, Any]:
    res = executer(["ffprobe", "-v", "error", "-print_format", "json",
                    "-show_format", "-show_streams", str(video)])
    if res.returncode != 0:
        raise ErreurOutil(f"ffprobe n'a pas pu lire {video} : {res.stderr.strip()[:300]}")
    return json.loads(res.stdout)


def analyser_video(video: Path, duree: float, flux: str = "0:v:0") -> dict[str, Any]:
    detections = executer(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", flux,
                           "-vf", f"blackdetect=d={NOIR_MIN}:pix_th=0.10,freezedetect=n=-60dB:d={FIGE_MIN}",
                           "-f", "null", "-"])
    exiger(detections, "blackdetect/freezedetect")
    scenes = executer(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", flux,
                       "-vf", f"select='gt(scene,{SEUIL_SCENE})',showinfo", "-f", "null", "-"])
    exiger(scenes, "détection des plans (scene)")
    coupes = parse_coupes(scenes.stderr)
    return {"noirs": parse_intervalles(detections.stderr, "blackdetect", duree),
            "figes": parse_intervalles(detections.stderr, "freezedetect", duree),
            "coupes": coupes, "plans": durees_de_plans(coupes, duree)}


def analyser_audio(video: Path, duree: float) -> dict[str, Any]:
    res = executer(["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-map", "0:a:0",
                    "-af", f"ebur128=peak=true,silencedetect=noise=-50dB:d={SILENCE_MIN}",
                    "-f", "null", "-"])
    exiger(res, "ebur128/silencedetect")
    loudness = parse_ebur128(res.stderr)
    if loudness["integre"] is None or loudness["crete"] is None:
        raise ErreurOutil("la passe ebur128/silencedetect n'a rendu ni loudness intégrée ni crête vraie : "
                          "mesure impossible, rapport non fiable")
    return {"loudness": loudness,
            "silences": parse_intervalles(res.stderr, "silencedetect", duree)}


def milieux_de_plans(plans: list[float]) -> list[float]:
    milieux, debut = [], 0.0
    for longueur in plans:
        milieux.append(round(debut + longueur / 2, 3))
        debut += longueur
    return milieux


def extraire_planche(video: Path, temps: list[float], dossier: Path, flux: str = "0:v:0") -> Path | None:
    """Une image au milieu de chaque plan, puis une planche contact.

    Rend le chemin de la planche, ou None si une image ou la planche n'a pas pu être
    produite (la planche est facultative : le rapport ne dépend pas d'elle). Une erreur
    d'écriture du dossier (OSError) remonte.
    """
    dossier.mkdir(parents=True, exist_ok=True)
    planche = dossier / "planche.jpg"
    for ancienne in list(dossier.glob("plan-*.jpg")) + [planche]:
        ancienne.unlink(missing_ok=True)
    images = []
    try:
        for index, t in enumerate(temps[:MAX_IMAGES], start=1):
            sortie = dossier / f"plan-{index:02d}.jpg"
            res = executer(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{t:.3f}",
                            "-i", str(video), "-map", flux, "-frames:v", "1", "-vf", "scale=540:-2",
                            str(sortie)])
            if res.returncode != 0 or not sortie.exists():
                return None
            images.append(sortie)
        if not images:
            return None
        colonnes = min(6, len(images))
        lignes = -(-len(images) // colonnes)
        res = executer(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(dossier / "plan-%02d.jpg"),
                        "-vf", f"scale=270:-2,tile={colonnes}x{lignes}:padding=6:color=white",
                        "-frames:v", "1", str(planche)])
    except ErreurOutil:
        return None
    return planche if res.returncode == 0 and planche.exists() else None


def constats_planche(planche: Path | None, nb_plans: int) -> list[Constat]:
    """Ce que le rapport doit dire de la planche : absente, ou limitée aux MAX_IMAGES premiers plans."""
    if planche is None:
        return [Constat("info", "planche-indisponible",
                        "images ou planche contact non extraites : regarder la vidéo "
                        "directement ou relancer après avoir vérifié ffmpeg")]
    if nb_plans > MAX_IMAGES:
        return [Constat("info", "planche-partielle",
                        f"{nb_plans} plans : images et planche limitées aux {MAX_IMAGES} premiers, "
                        "regarder la suite dans la vidéo")]
    return []


def modele_whisper() -> str | None:
    """Chemin du modèle whisper : variable WHISPER_MODEL, sinon ligne du .env."""
    valeur = os.environ.get("WHISPER_MODEL")
    env = RACINE / ".env"
    if not valeur and env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            if ligne.strip().startswith("WHISPER_MODEL="):
                valeur = ligne.split("=", 1)[1].strip().strip('"').strip("'")
    if valeur and Path(valeur).expanduser().exists():
        return str(Path(valeur).expanduser())
    return None


def transcrire(video: Path, langue: str) -> str | None:
    """Transcrit l'audio du rendu avec whisper-cli.

    Rend None si l'outil ou son modèle manque (transcription non tentée) ; lève
    EchecTranscription si l'outil a tourné et a échoué.
    """
    modele = modele_whisper()
    if not modele or shutil.which("whisper-cli") is None:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / "audio.wav"
        extraction = executer(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
                               "-vn", "-ac", "1", "-ar", "16000", str(wav)])
        if extraction.returncode != 0 or not wav.exists():
            raise EchecTranscription("extraction audio impossible")
        base = Path(tmp) / "transcription"
        res = executer(["whisper-cli", "-m", modele, "-f", str(wav), "-l", langue,
                        "-otxt", "-of", str(base), "-np"])
        texte = base.with_suffix(".txt")
        if res.returncode != 0:
            raise EchecTranscription(f"code {res.returncode}")
        if not texte.exists():
            raise EchecTranscription("aucun fichier de transcription produit")
        return texte.read_text(encoding="utf-8")


# ---------------------------------------------------------------- rapports

def resume(constats: list[Constat]) -> dict[str, int]:
    return {"erreurs": sum(c.niveau == "erreur" for c in constats),
            "avertissements": sum(c.niveau == "avertissement" for c in constats),
            "infos": sum(c.niveau == "info" for c in constats)}


def _ligne(c: Constat) -> str:
    instant = f" à {c.t:.2f} s" if c.t is not None else ""
    return f"[{c.niveau}] {c.id}{instant} : {c.message}"


def rendu_texte(video: Path, constats: list[Constat], planche: Path | None) -> str:
    r = resume(constats)
    lignes = [f"QA vidéo : {video}"]
    lignes += [_ligne(c) for c in constats] or ["aucun constat"]
    lignes.append(f"{r['erreurs']} erreur(s), {r['avertissements']} avertissement(s), {r['infos']} info(s)")
    if planche:
        lignes.append(f"planche : {planche}")
    return "\n".join(lignes)


def rendu_markdown(video: Path, constats: list[Constat], mesures: dict[str, Any],
                   planche: Path | None) -> str:
    r = resume(constats)
    probe = mesures["probe"]
    v = probe["video"] or {}
    lignes = [f"# QA vidéo : {video.name}", "",
              f"- Durée : {probe['duree']:.2f} s",
              f"- Image : {v.get('largeur', '?')}x{v.get('hauteur', '?')} {v.get('codec', '?')}",
              f"- Bilan : {r['erreurs']} erreur(s), {r['avertissements']} avertissement(s)", "",
              "| Niveau | Constat | Instant | Détail |", "|---|---|---|---|"]
    for c in constats:
        lignes.append(f"| {c.niveau} | `{c.id}` | {'' if c.t is None else f'{c.t:.2f} s'} | {c.message} |")
    if planche:
        lignes += ["", "Planche : `planche.jpg` (une image au milieu de chaque plan)."]
    elif any(c.id == "planche-indisponible" for c in constats):
        lignes += ["", "Planche : indisponible (constat `planche-indisponible`)."]
    elif probe["video"] is None:                     # flux-video le dit déjà : pas de second constat
        lignes += ["", "Planche : sans objet, aucun flux vidéo (constat `flux-video`)."]
    else:
        lignes += ["", "Planche : indisponible."]
    return "\n".join(lignes) + "\n"


def sans_non_finis(valeur: Any) -> Any:
    """Remplace par None les flottants non finis (-inf d'un silence numérique, nan), récursivement."""
    if isinstance(valeur, float) and not math.isfinite(valeur):
        return None
    if isinstance(valeur, dict):
        return {cle: sans_non_finis(v) for cle, v in valeur.items()}
    if isinstance(valeur, (list, tuple)):
        return [sans_non_finis(v) for v in valeur]
    return valeur


def serialiser_json(rapport: dict[str, Any]) -> str:
    """JSON strict (RFC 8259) : jamais de -Infinity ni de NaN."""
    return json.dumps(sans_non_finis(rapport), ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def dossier_sortie(video: Path) -> Path:
    # abspath et non resolve : un export qui est un lien symbolique (rendu rangé sur le Drive)
    # garde son rapport dans le projet, sous le nom du lien.
    video = Path(os.path.abspath(video))
    base = video.parent.parent if video.parent.name == "exports" else video.parent
    return base / "qa" / video.stem


# ---------------------------------------------------------------- CLI

def construire_parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="QA mesurable d'un rendu vidéo (ffprobe et ffmpeg).")
    p.add_argument("video", help="fichier vidéo rendu (mp4)")
    p.add_argument("--plateforme", help="reels, tiktok, shorts ou linkedin (08-video/scripts/plateformes.toml)")
    p.add_argument("--duree", type=float, help="durée attendue en secondes (tolérance 5 %%)")
    p.add_argument("--script", help="narration attendue : .txt, ou script.md (colonne voix du tableau minuté)")
    p.add_argument("--transcript", help="transcription déjà faite (.txt, ou .json de whisper)")
    p.add_argument("--langue", default="fr", help="langue de la transcription whisper (défaut : fr)")
    p.add_argument("--sans-audio", action="store_true", help="vidéo muette assumée : pas d'erreur flux-audio, son "
                   "d'une éventuelle piste ni mesuré ni jugé")
    p.add_argument("--max-plan", type=float, default=MAX_PLAN_DEFAUT,
                   help=f"plafond d'un plan sans changement, en s (défaut {MAX_PLAN_DEFAUT:g}, 0 pour désactiver)")
    p.add_argument("--sortie", help="dossier des images et rapports (défaut : qa/<nom>/ à côté de exports/)")
    p.add_argument("--plateformes", default=str(PLATEFORMES_DEFAUT), help="fichier TOML des plateformes")
    p.add_argument("--format", choices=("text", "json"), default="text")
    return p


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)
    video = Path(args.video)
    if not video.is_file():
        print(f"ERREUR : {video} introuvable", file=sys.stderr)
        return 2
    video = Path(os.path.abspath(video))             # pas resolve : voir dossier_sortie
    try:
        return analyser(args, video)
    except (ErreurOutil, OSError, ValueError, tomllib.TOMLDecodeError) as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2


def analyser(args: argparse.Namespace, video: Path) -> int:
    conf = None
    if args.plateforme:
        plateformes = charger_plateformes(Path(args.plateformes))
        if args.plateforme not in plateformes:
            raise ValueError(f"plateforme inconnue « {args.plateforme} » "
                             f"(connues : {', '.join(sorted(plateformes))})")
        conf = plateformes[args.plateforme]

    probe = parse_ffprobe(sonder(video))
    mesures: dict[str, Any] = {"probe": probe}
    if probe["video"]:
        mesures.update(analyser_video(video, probe["duree"], flux_video(probe["video"])))
    if probe["audio"] and not args.sans_audio:       # vidéo déclarée muette : son non mesuré ni jugé
        mesures.update(analyser_audio(video, probe["duree"]))
    with video.open("rb") as flux:
        mesures["moov_avant_mdat"] = moov_avant_mdat(flux)
    if args.script:
        chemin = Path(args.script)
        mesures["attendu"] = texte_attendu(chemin.read_text(encoding="utf-8"), chemin.suffix)
        if args.transcript:
            mesures["transcription"] = lire_transcription(Path(args.transcript))
        elif probe["audio"] and not args.sans_audio:
            try:
                mesures["transcription"] = transcrire(video, args.langue)
            except EchecTranscription as err:
                mesures["transcription"] = None
                mesures["transcription_echec"] = str(err)
        # sans flux audio (ou vidéo déclarée muette) ni --transcript : rien à transcrire

    constats = evaluer(mesures, {"plateforme": conf, "nom_plateforme": args.plateforme,
                                 "duree": args.duree, "sans_audio": args.sans_audio,
                                 "max_plan": args.max_plan})
    sortie = Path(os.path.abspath(args.sortie)) if args.sortie else dossier_sortie(video)
    planche = None
    if probe["video"]:
        temps = milieux_de_plans(mesures.get("plans") or [probe["duree"]])
        planche = extraire_planche(video, temps, sortie, flux_video(probe["video"]))
        constats += constats_planche(planche, len(temps))
    sortie.mkdir(parents=True, exist_ok=True)
    rapport = {"video": str(video), "plateforme": args.plateforme, "resume": resume(constats),
               "mesures": {"duree": probe["duree"], "video": probe["video"], "audio": probe["audio"],
                           "loudness": mesures.get("loudness"), "plans": mesures.get("plans")},
               "constats": [asdict(c) for c in constats],
               "planche": str(planche) if planche else None}
    texte_json = serialiser_json(rapport)
    (sortie / "rapport.json").write_text(texte_json, encoding="utf-8")
    (sortie / "rapport.md").write_text(rendu_markdown(video, constats, mesures, planche), encoding="utf-8")
    if args.format == "json":
        print(texte_json, end="")
    else:
        print(rendu_texte(video, constats, planche))
    return 1 if any(c.niveau == "erreur" for c in constats) else 0


if __name__ == "__main__":
    sys.exit(main())
