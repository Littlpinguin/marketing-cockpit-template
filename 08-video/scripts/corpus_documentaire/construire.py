"""Constitution d'un corpus : thème, recherche, filtre de licence, téléchargement, fiches."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from . import images_cles, reseau
from .licences import ADMISES_DEFAUT, CONNUES, admise, attribution_exigee
from .sources import SOURCES
from .sources.base import Source

NOM_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
EXTENSIONS = {".mp4", ".webm", ".ogv", ".ogg", ".mov", ".m4v", ".mkv", ".avi", ".mpg", ".mpeg", ".wmv", ".flv"}
# Ce qu'une source peut renvoyer de travers : champ absent, type inattendu, valeur illisible.
REPONSE_INATTENDUE = (KeyError, TypeError, ValueError, AttributeError, IndexError)


class ErreurConversion(Exception):
    """Conversion en mp4 impossible (ffmpeg absent ou en échec)."""


class ErreurMesure(Exception):
    """Durée impossible à mesurer parce que ffprobe est absent."""


@dataclass
class Emplacement:
    id: str
    description: str
    requetes: list[str]


@dataclass
class Theme:
    nom: str
    sources: list[str]
    licences: frozenset[str]
    par_requete: int
    duree_max: float | None
    emplacements: list[Emplacement]


@dataclass
class Rapport:
    telecharges: int = 0
    deja_presents: int = 0
    ecartes_licence: int = 0
    ecartes_duree: int = 0
    erreurs: list[str] = field(default_factory=list)
    sources_ignorees: list[str] = field(default_factory=list)
    avertissements: list[str] = field(default_factory=list)     # contrôle non fait, clip conservé


def _liste_de_textes(valeur, nom: str) -> list[str]:
    if not isinstance(valeur, list) or not valeur or not all(isinstance(v, str) and v for v in valeur):
        raise ValueError(f"« {nom} » doit être une liste non vide de textes")
    return valeur


def charger_theme(chemin: Path) -> Theme:
    """Lit et valide un thème. Toute anomalie du fichier est une ValueError au message lisible."""
    donnees = tomllib.loads(Path(chemin).read_text(encoding="utf-8"))
    nom = donnees.get("nom") or Path(chemin).stem
    if not isinstance(nom, str) or not NOM_RE.fullmatch(nom):
        raise ValueError(f"nom de thème « {nom} » invalide (minuscules, chiffres et tirets)")
    noms_sources = _liste_de_textes(donnees.get("sources", list(SOURCES)), "sources")
    inconnues = [s for s in noms_sources if s not in SOURCES]
    if inconnues:
        raise ValueError(f"source inconnue : {', '.join(inconnues)} (connues : {', '.join(SOURCES)})")
    admises = frozenset(_liste_de_textes(donnees["licences"], "licences")) if "licences" in donnees \
        else ADMISES_DEFAUT
    hors = sorted(admises - CONNUES)
    if hors:
        raise ValueError(f"licence inconnue : {', '.join(hors)} (connues : {', '.join(sorted(CONNUES))})")
    par_requete = donnees.get("par_requete", 3)
    if isinstance(par_requete, bool) or not isinstance(par_requete, int) or par_requete < 1:
        raise ValueError("« par_requete » doit être un entier d'au moins 1")
    duree_max = donnees.get("duree_max")
    if duree_max is not None and (isinstance(duree_max, bool) or not isinstance(duree_max, (int, float))
                                  or duree_max < 0):
        raise ValueError("« duree_max » doit être un nombre de secondes positif (0 : sans limite)")
    brutes = donnees.get("emplacements", [])
    if not isinstance(brutes, list) or not all(isinstance(b, dict) for b in brutes):
        raise ValueError("« emplacements » doit être une suite de tables [[emplacements]]")
    emplacements, vus = [], set()
    for brut in brutes:
        ident, description, requetes = brut.get("id"), brut.get("description"), brut.get("requetes")
        if not (isinstance(ident, str) and ident and isinstance(description, str) and description):
            raise ValueError("chaque emplacement exige un « id » et une « description » en texte")
        if not isinstance(requetes, list) or not requetes or not all(isinstance(r, str) and r for r in requetes):
            raise ValueError(f"emplacement « {ident} » : « requetes » doit être une liste non vide")
        if ident in vus:
            raise ValueError(f"emplacement « {ident} » en double")
        vus.add(ident)
        emplacements.append(Emplacement(ident, description, requetes))
    if not emplacements:
        raise ValueError("aucun emplacement ([[emplacements]]) dans le thème")
    return Theme(nom, noms_sources, admises, par_requete, float(duree_max) if duree_max else None, emplacements)


def _extension(url: str) -> str:
    suffixe = Path(urlparse(url).path).suffix.lower()
    return suffixe if suffixe in EXTENSIONS else ".mp4"


def convertir_en_mp4(source: Path, cible: Path) -> Path:
    if shutil.which("ffmpeg") is None:
        raise ErreurConversion(f"ffmpeg introuvable : {source.name} reste au format {source.suffix}")
    res = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart",
                          str(cible)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if res.returncode != 0 or not cible.exists():
        cible.unlink(missing_ok=True)       # pas de mp4 tronqué qui passerait pour un clip présent
        raise ErreurConversion(f"conversion de {source.name} en mp4 impossible : {res.stderr.strip()[:200]}")
    source.unlink(missing_ok=True)
    return cible


def mesurer_duree(video: Path) -> float | None:
    """Durée mesurée par ffprobe ; None si le fichier est illisible ; ErreurMesure si ffprobe manque."""
    if shutil.which("ffprobe") is None:
        raise ErreurMesure("ffprobe introuvable")
    duree = images_cles.duree_video(video)
    return duree if duree > 0 else None


def construire(theme: Theme, dossier: Path, sources: list[Source], *,
               telecharger=None, convertir=convertir_en_mp4, mesurer=None) -> Rapport:
    """Cherche, filtre, télécharge. `mesurer(video)` donne la durée quand la source n'en donne pas
    (par défaut ffprobe) ; un convertisseur injecté est présumé prêt, le convertisseur par défaut exige ffmpeg."""
    telecharger = telecharger or reseau.telecharger
    mesurer = mesurer or mesurer_duree
    conversion_possible = convertir is not convertir_en_mp4 or shutil.which("ffmpeg") is not None
    non_mesures: list[str] = []
    rejetes: set[str] = set()       # trouvés trop longs ou illisibles : pas de nouveau téléchargement dans le même lot
    clips = dossier / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    rapport = Rapport()
    actives = []
    for source in sources:
        ok, raison = source.disponible()
        if ok:
            actives.append(source)
        else:
            rapport.sources_ignorees.append(f"{source.nom} : {raison}")
    for emplacement in theme.emplacements:
        for requete in emplacement.requetes:
            for source in actives:
                try:
                    resultats = source.rechercher(requete, theme.par_requete)
                except reseau.ErreurReseau as err:
                    rapport.erreurs.append(f"{source.nom}, « {requete} » : {err}")
                    continue
                except REPONSE_INATTENDUE as err:
                    rapport.erreurs.append(
                        f"{source.nom}, « {requete} » : réponse inattendue de la source ({type(err).__name__})")
                    continue
                for resultat in resultats:
                    resultat.emplacement = emplacement.id
                    if not admise(resultat.licence, theme.licences):
                        rapport.ecartes_licence += 1
                        continue
                    if theme.duree_max and resultat.duree and resultat.duree > theme.duree_max:
                        rapport.ecartes_duree += 1
                        continue
                    fiche = clips / f"{resultat.nom_fichier}.json"
                    video = clips / f"{resultat.nom_fichier}.mp4"
                    if fiche.exists() and video.exists():
                        rapport.deja_presents += 1
                        continue
                    if resultat.nom_fichier in rejetes:
                        continue
                    extension = _extension(resultat.url_fichier)
                    if extension != ".mp4" and not conversion_possible:      # inutile de télécharger ce qu'on ne saura pas convertir
                        ligne = (f"{resultat.nom_fichier} : format {extension} à convertir en mp4 mais ffmpeg est "
                                 "introuvable, non téléchargé")
                        if ligne not in rapport.erreurs:
                            rapport.erreurs.append(ligne)
                        continue
                    try:
                        brut = telecharger(resultat.url_fichier, clips / f"{resultat.nom_fichier}{extension}")
                        if brut.suffix.lower() != ".mp4":
                            convertir(brut, video)
                        if theme.duree_max and resultat.duree is None:
                            # La source ne donne pas de durée (NASA jamais, Wikimedia rarement) : on la mesure,
                            # sinon la limite du thème serait contournée.
                            try:
                                mesuree = mesurer(video)
                            except ErreurMesure:
                                non_mesures.append(resultat.nom_fichier)
                            else:
                                if mesuree is None:
                                    video.unlink(missing_ok=True)
                                    rejetes.add(resultat.nom_fichier)
                                    rapport.erreurs.append(f"{resultat.nom_fichier} : fichier illisible par ffprobe, écarté")
                                    continue
                                if mesuree > theme.duree_max:
                                    video.unlink(missing_ok=True)
                                    rejetes.add(resultat.nom_fichier)
                                    rapport.ecartes_duree += 1
                                    continue
                                resultat.duree = mesuree
                        # La fiche vient en dernier : elle atteste que le clip est complet.
                        fiche.write_text(json.dumps(
                            {**resultat.fiche(), "fichier": video.name,
                             "attribution_exigee": attribution_exigee(resultat.licence)},
                            ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    except (reseau.ErreurReseau, ErreurConversion, OSError) as err:
                        rapport.erreurs.append(f"{resultat.nom_fichier} : {err}")
                        continue
                    rapport.telecharges += 1
    if non_mesures:
        noms = sorted(set(non_mesures))
        rapport.avertissements.append(
            f"durée inconnue et non mesurée (ffprobe introuvable) pour {len(noms)} clip(s), "
            f"limite de {theme.duree_max:g} s non vérifiée : {', '.join(noms[:5])}{' …' if len(noms) > 5 else ''}")
    return rapport
