"""Images clés d'un clip : une après chaque changement de plan, et au moins une toutes les N secondes."""
from __future__ import annotations

import glob
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

ECART_MIN = 0.5
SEUIL_SCENE = 0.3


class OutilAbsent(RuntimeError):
    """ffmpeg ou ffprobe introuvable."""


def temps_images_cles(duree: float, coupes: list[float], intervalle: float = 3.0) -> list[float]:
    if not intervalle > 0:                       # écarte aussi NaN ; sans cela, la boucle ci-dessous ne finirait pas
        raise ValueError(f"intervalle {intervalle} invalide : un nombre de secondes positif est attendu")
    instants = {round(c + 0.1, 2) for c in coupes if 0 <= c + 0.1 < duree}
    t = min(0.5, duree / 2)
    while t < duree:
        instants.add(round(t, 2))
        t += intervalle
    retenus: list[float] = []
    for instant in sorted(instants):
        if not retenus or instant - retenus[-1] >= ECART_MIN:
            retenus.append(instant)
    return retenus


def _ffmpeg_present() -> None:
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        raise OutilAbsent("ffmpeg et ffprobe sont requis (brew install ffmpeg)")


def _executer(commande: list[str]) -> subprocess.CompletedProcess:
    # Sortie d'outil décodée avec remplacement : un octet étranger ne doit jamais faire échouer l'analyse.
    return subprocess.run(commande, capture_output=True, text=True, encoding="utf-8", errors="replace")


def duree_video(clip: Path) -> float:
    """Durée en secondes, 0.0 si le fichier est illisible (jamais une valeur inventée)."""
    res = _executer(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", str(clip)])
    if res.returncode != 0:
        return 0.0
    try:
        duree = float(json.loads(res.stdout)["format"]["duration"])
    except (KeyError, TypeError, ValueError):       # JSONDecodeError est une ValueError
        return 0.0
    return duree if math.isfinite(duree) else 0.0


def coupes_video(clip: Path) -> list[float]:
    """Instants des changements de plan. Si la détection échoue, les images d'intervalle restent."""
    res = _executer(["ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-i", str(clip), "-map", "0:v:0",
                     "-vf", f"select='gt(scene,{SEUIL_SCENE})',showinfo", "-f", "null", "-"])
    return sorted({round(float(t), 3) for t in re.findall(r"pts_time:\s*([\d.]+)", res.stderr) if float(t) > 0})


def extraire(clip: Path, dossier: Path, intervalle: float = 3.0) -> list[tuple[float, Path]]:
    """Extrait les images clés dans `dossier` sous <clip>-NNN.jpg ; [] si le clip est illisible.

    Les images d'une extraction précédente du même clip sont retirées d'abord : un
    numéro identique pour un autre instant (intervalle modifié) fausserait l'index.
    """
    _ffmpeg_present()
    dossier.mkdir(parents=True, exist_ok=True)
    for ancienne in dossier.glob(f"{glob.escape(clip.stem)}-[0-9][0-9][0-9].jpg"):
        ancienne.unlink()
    duree = duree_video(clip)
    if duree <= 0:
        return []
    sorties = []
    for i, t in enumerate(temps_images_cles(duree, coupes_video(clip), intervalle)):
        chemin = dossier / f"{clip.stem}-{i:03d}.jpg"
        _executer(["ffmpeg", "-hide_banner", "-nostdin", "-loglevel", "error", "-y", "-ss", f"{t:.2f}", "-i", str(clip),
                   "-frames:v", "1", "-vf", "scale=336:-2", str(chemin)])
        if chemin.exists() and chemin.stat().st_size > 0:
            sorties.append((t, chemin))
        else:
            chemin.unlink(missing_ok=True)
    return sorties
