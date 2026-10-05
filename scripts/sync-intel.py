#!/usr/bin/env python3
"""
Copie dans 00-intel/inbox/ les réunions exportées du Drive partagé des transcriptions.

Chaîne complète (voir _integrations/drive-transcripts/README.md) :
Drive partagé « Transcripts » → Apps Script du lundi (export Markdown) →
Mon Drive/Transcripts-md/ → Drive pour ordinateur → ce script → 00-intel/inbox/.

Le script ne fait que copier, sans IA, et ne traite que les nouveautés.
00-intel/.sync-state.json retient ce qui a déjà été importé (nom du fichier
source et `doc_id` du Google Doc) : un fichier déjà importé est reconnu à son
nom, sans être ouvert, donc sans être retéléchargé par Drive pour ordinateur,
et il ne revient jamais dans l'inbox, même après avoir été classé et renommé.
La profondeur d'historique (30 jours au premier passage) est fixée par l'Apps
Script : rien d'antérieur n'arrive dans Transcripts-md. Les exclusions de l'Apps Script
(entretiens de candidats, comptabilité) sont rejouées ici par sécurité.

Usage:
  python3 scripts/sync-intel.py              # copie les réunions nouvelles
  python3 scripts/sync-intel.py --dry-run    # montre ce qui serait copié, sans rien écrire

Source : --source, sinon la variable INTEL_DRIVE_MD_DIR (environnement ou
fichier .env à la racine), à faire pointer vers le dossier Transcripts-md
monté par Drive pour ordinateur, par exemple
~/Library/CloudStorage/GoogleDrive-<compte>/Mon Drive/Transcripts-md.

Codes de sortie : 0 succès (même sans nouveauté), 2 source introuvable
(Drive pour ordinateur arrêté, compte déconnecté ou Apps Script pas encore installé).

La dernière ligne est un bilan lisible par les routines :
  BILAN copies=N deja=N exclus=N vides=N apps_script=<ISO|inconnu> erreurs_drive=N alerte=<texte|aucune>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
# Même liste que CONFIG.EXCLUDE dans apps-script/Code.gs.
EXCLUSIONS = [
    re.compile(r"entrevue|candidat|interview|entretien d.embauche", re.I),
    re.compile(r"accounting|comptab|\bcompta\b|\bfinance\b", re.I),
]
# Note Gemini vide (réunion dans une autre langue que celle réglée sur Meet) : même
# règle que CONFIG.EMPTY_NOTE dans apps-script/Code.gs.
NOTE_VIDE = re.compile(r"A summary wasn't produced|Aucun résumé|résumé n'a pas été (généré|produit)", re.I)
NOTE_VIDE_MAX = 8000
APPS_SCRIPT_SILENCE = timedelta(days=8)  # le déclencheur tourne chaque lundi
DRIVE_SILENCE = timedelta(days=7)  # aucune nouvelle réunion depuis une semaine
DATE_EN_TETE = re.compile(r"^(\d{4}-\d{2}-\d{2}) ")  # « 2026-09-30 1532 Comité projet - … [a1b2c3].md »


def source_configuree() -> Path | None:
    """INTEL_DRIVE_MD_DIR depuis l'environnement, sinon depuis le .env de la racine."""
    valeur = os.environ.get("INTEL_DRIVE_MD_DIR")
    env = RACINE / ".env"
    if not valeur and env.exists():
        for ligne in env.read_text(encoding="utf-8").splitlines():
            cle, sep, val = ligne.partition("=")
            if sep and cle.strip() == "INTEL_DRIVE_MD_DIR":
                valeur = val.strip().strip('"').strip("'")
    return Path(valeur).expanduser() if valeur else None


def lire_frontmatter(texte: str) -> dict[str, str]:
    if not texte.startswith("---\n"):
        return {}
    fin = texte.find("\n---", 4)
    if fin == -1:
        return {}
    champs = {}
    for ligne in texte[4:fin].splitlines():
        cle, sep, valeur = ligne.partition(":")
        if not sep:
            continue
        valeur = valeur.strip()
        if valeur.startswith('"'):
            try:
                valeur = json.loads(valeur)
            except json.JSONDecodeError:
                pass
        champs[cle.strip()] = valeur
    return champs


def parse_iso(valeur: str | None) -> datetime | None:
    if not valeur:
        return None
    try:
        return datetime.fromisoformat(valeur.replace("Z", "+00:00"))
    except ValueError:
        return None


def charger_etat(chemin: Path) -> dict:
    if chemin.exists():
        return json.loads(chemin.read_text(encoding="utf-8"))
    return {"version": 1, "importes": {}}


def sauver_etat(chemin: Path, etat: dict) -> None:
    tmp = chemin.with_suffix(".tmp")
    tmp.write_text(json.dumps(etat, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(chemin)


def destination_libre(inbox: Path, nom: str) -> Path:
    cible = inbox / nom
    n = 2
    while cible.exists():
        cible = inbox / f"{Path(nom).stem} ({n}).md"
        n += 1
    return cible


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--dry-run", action="store_true", help="ne rien écrire")
    parser.add_argument("--source", type=Path, help="dossier Transcripts-md")
    parser.add_argument("--intel", type=Path, default=RACINE / "00-intel", help="dossier 00-intel")
    args = parser.parse_args()

    source = args.source or source_configuree()
    if source is None or not source.is_dir():
        print(f"Source introuvable : {source}")
        print("INTEL_DRIVE_MD_DIR est-il renseigné, Drive pour ordinateur lancé, l'Apps Script installé ?")
        print("BILAN copies=0 deja=0 exclus=0 vides=0 apps_script=inconnu erreurs_drive=0 alerte=source-introuvable")
        return 2

    inbox = args.intel / "inbox"
    chemin_etat = args.intel / ".sync-state.json"
    etat = charger_etat(chemin_etat)
    importes = etat.setdefault("importes", {})
    sources_vues = {v.get("source") for v in importes.values()}
    exclus_vus = etat.setdefault("exclus", [])

    copies, deja, exclus, vides = [], 0, 0, 0
    derniere_reunion: date | None = None
    for fichier in sorted(source.glob("*.md")):
        if fichier.name.startswith("_"):
            continue  # _etat.json, _test.md
        m = DATE_EN_TETE.match(fichier.name)
        jour = date.fromisoformat(m.group(1)) if m else None
        if jour and (derniere_reunion is None or jour > derniere_reunion):
            derniere_reunion = jour
        # Reconnu à son nom : un fichier déjà importé n'est jamais ouvert,
        # donc jamais retéléchargé par Drive pour ordinateur.
        if fichier.name in sources_vues:
            deja += 1
            continue
        if fichier.name in exclus_vus:
            exclus += 1  # exclu ou vide lors d'un passage précédent
            continue
        texte = fichier.read_text(encoding="utf-8")
        meta = lire_frontmatter(texte)
        doc_id = meta.get("doc_id")
        if not doc_id:
            print(f"  ignoré (pas de doc_id) : {fichier.name}")
            continue
        if any(r.search(meta.get("titre", fichier.name)) for r in EXCLUSIONS):
            exclus += 1
            if not args.dry_run:
                exclus_vus.append(fichier.name)
            continue
        if NOTE_VIDE.search(texte) and len(texte) < NOTE_VIDE_MAX:
            vides += 1
            if not args.dry_run:
                exclus_vus.append(fichier.name)
            continue
        if doc_id in importes:
            deja += 1
            continue
        cible = destination_libre(inbox, fichier.name)
        copies.append(cible.name)
        if not args.dry_run:
            inbox.mkdir(parents=True, exist_ok=True)
            cible.write_text(texte, encoding="utf-8")
            importes[doc_id] = {
                "source": fichier.name,
                "fichier": cible.name,
                "importe": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }

    if not args.dry_run:
        # Toujours écrit : son existence signale aux routines que la chaîne est en route.
        etat["derniere_synchro"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        sauver_etat(chemin_etat, etat)

    # Santé de la chaîne côté Google.
    alertes = []
    apps_script = "inconnu"
    erreurs_drive = 0
    chemin_etat_drive = source / "_etat.json"
    if chemin_etat_drive.exists():
        etat_drive = json.loads(chemin_etat_drive.read_text(encoding="utf-8"))
        derniere = parse_iso(etat_drive.get("derniere_execution"))
        apps_script = derniere.isoformat(timespec="minutes") if derniere else "inconnu"
        erreurs = etat_drive.get("erreurs") or []
        erreurs_drive = len(erreurs)
        for e in erreurs:
            print(f"  erreur Drive : {e.get('titre')} ({e.get('message')})")
        if derniere and datetime.now(timezone.utc) - derniere > APPS_SCRIPT_SILENCE:
            alertes.append("apps-script-silencieux")
        if erreurs_drive:
            alertes.append("erreurs-export")
    else:
        alertes.append("etat-apps-script-absent")
    if derniere_reunion and date.today() - derniere_reunion > DRIVE_SILENCE:
        alertes.append("aucune-reunion-depuis-7-jours")

    verbe = "à copier" if args.dry_run else "copiés"
    print(f"{len(copies)} fichier(s) {verbe} dans {inbox} :")
    for nom in copies:
        print(f"  + {nom}")
    print(
        f"BILAN copies={len(copies)} deja={deja} exclus={exclus} vides={vides} "
        f"apps_script={apps_script} erreurs_drive={erreurs_drive} "
        f"alerte={','.join(alertes) or 'aucune'}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
