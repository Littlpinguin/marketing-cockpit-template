"""Crédits d'un corpus ou d'une sélection : une ligne par clip, licence lisible."""
from __future__ import annotations

import json
from pathlib import Path

from .licences import LIBELLES


def lire_fiches(dossier: Path) -> list[dict]:
    """Les fiches de clips/*.json. Une fiche illisible est une ValueError qui nomme le fichier."""
    fiches = []
    for chemin in sorted((dossier / "clips").glob("*.json")):
        try:
            fiche = json.loads(chemin.read_text(encoding="utf-8"))
        except ValueError as err:       # JSON invalide ou UTF-8 invalide
            raise ValueError(f"fiche {chemin.name} illisible : {err}") from None
        if not isinstance(fiche, dict):
            raise ValueError(f"fiche {chemin.name} illisible : un objet JSON est attendu")
        fiches.append(fiche)
    return fiches


def _clips_choisis(selection: Path) -> set[str]:
    """Les noms de clips d'un selections.json ({emplacement: [{clip, ...}]})."""
    try:
        donnees = json.loads(Path(selection).read_text(encoding="utf-8"))
    except ValueError as err:
        raise ValueError(f"{Path(selection).name} illisible : {err}") from None
    forme = (isinstance(donnees, dict)
             and all(isinstance(resultats, list) and all(isinstance(r, dict) and isinstance(r.get("clip"), str)
                                                         for r in resultats)
                     for resultats in donnees.values()))
    if not forme:
        raise ValueError(f"{Path(selection).name} mal formé : attendu {{emplacement: [{{\"clip\": \"...mp4\"}}]}}")
    return {r["clip"] for resultats in donnees.values() for r in resultats}


def _ligne(texte) -> str:
    """Un texte d'API sur une seule ligne : un retour à la ligne casserait la liste Markdown."""
    return " ".join(str(texte or "").split())


def ecrire_credits(dossier: Path, selection: Path | None = None) -> Path:
    fiches = lire_fiches(dossier)
    if selection:
        choisis = _clips_choisis(selection)
        connus = {f.get("fichier") for f in fiches}
        absents = sorted(choisis - connus)
        if absents:
            raise ValueError(f"{Path(selection).name} cite des clips sans fiche dans le corpus : "
                             f"{', '.join(absents)} (corpus modifié depuis la sélection ?)")
        fiches = [f for f in fiches if f.get("fichier") in choisis]
    if not fiches:
        raise ValueError("aucun clip à créditer" + (" dans la sélection" if selection else " : corpus vide"))
    lignes = [f"# Crédits du corpus {dossier.name}", ""]
    for fiche in sorted(fiches, key=lambda f: (_ligne(f.get("source")), _ligne(f.get("titre")))):
        licence = _ligne(fiche.get("licence")) or "inconnue"
        mention = LIBELLES.get(licence, licence)
        attribution = " Attribution obligatoire au générique ou en légende." if fiche.get("attribution_exigee") else ""
        auteur = _ligne(fiche.get("auteur")) or "auteur non renseigné"
        titre = _ligne(fiche.get("titre")) or _ligne(fiche.get("id")) or "sans titre"
        lignes.append(f"- « {titre} », {auteur}. Source : {_ligne(fiche.get('source'))} "
                      f"({_ligne(fiche.get('page'))}). Licence : {mention}.{attribution}")
    sortie = dossier / "credits.md"
    sortie.write_text("\n".join(lignes) + "\n", encoding="utf-8")
    return sortie
