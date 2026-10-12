#!/usr/bin/env python3
"""Corpus documentaire : constituer, indexer et interroger des archives vidéo libres.

Usage :
    python3 08-video/scripts/corpus.py build 08-video/corpus/themes/exemple-savoir-faire.toml
    python3 08-video/scripts/corpus.py index savoir-faire
    python3 08-video/scripts/corpus.py search savoir-faire "mains qui rabotent une planche" --top 5
    python3 08-video/scripts/corpus.py search savoir-faire --emplacement ouverture
    python3 08-video/scripts/corpus.py credits savoir-faire [--selection selections.json]
    python3 08-video/scripts/corpus.py list savoir-faire

Sources : pexels (PEXELS_API_KEY), pixabay (PIXABAY_API_KEY), archive, wikimedia,
nasa (sans clé). Les clés se lisent dans l'environnement puis dans .env, jamais
affichées. index et search exigent les dépendances facultatives de
08-video/requirements-corpus.txt. Doctrine : 08-video/documentaire.md.

Codes de sortie : 0 fait ; 1 aucune source utilisable, corpus vide à l'issue de
build, ou donnée du corpus invalide (fiche illisible, sélection mal formée) ;
2 usage, thème invalide, fichier ou corpus introuvable, ou dépendance manquante.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from corpus_documentaire import credits, sources  # noqa: E402
from corpus_documentaire.construire import charger_theme, construire  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_DEFAUT = RACINE / "08-video" / "corpus"
CLES = ("PEXELS_API_KEY", "PIXABAY_API_KEY")


def lire_env() -> dict[str, str]:
    """Clés des sources : environnement d'abord, puis .env à la racine du dépôt."""
    env = {cle: os.environ[cle] for cle in CLES if os.environ.get(cle)}
    fichier = RACINE / ".env"
    lignes: list[str] = []
    if fichier.is_file():
        try:
            lignes = fichier.read_text(encoding="utf-8").splitlines()
        except (OSError, ValueError):
            print("avertissement : .env illisible, clés lues dans l'environnement seulement", file=sys.stderr)
    for ligne in lignes:
        ligne = ligne.strip()
        if ligne.startswith("export "):
            ligne = ligne[len("export "):]
        cle, _, valeur = ligne.partition("=")
        cle, valeur = cle.strip(), valeur.strip().strip('"').strip("'")
        if cle in CLES and cle not in os.environ and valeur:
            env[cle] = valeur
    return env


def dossier_theme(args) -> Path | None:
    dossier = Path(args.racine) / args.theme
    if not (dossier / "clips").is_dir():
        print(f"ERREUR : corpus « {args.theme} » introuvable dans {args.racine} "
              "(lancer d'abord corpus.py build)", file=sys.stderr)
        return None
    return dossier


def cmd_build(args) -> int:
    chemin = Path(args.theme)
    try:
        theme = charger_theme(chemin)
    except (OSError, ValueError) as err:
        print(f"ERREUR : thème {chemin} illisible ou invalide : {err}", file=sys.stderr)
        return 2
    instances = sources.construire(theme.sources, lire_env())
    if not any(s.disponible()[0] for s in instances):
        for s in instances:
            print(f"source ignorée : {s.nom} : {s.disponible()[1]}")
        print("ERREUR : aucune source utilisable pour ce thème", file=sys.stderr)
        return 1
    dossier = Path(args.racine) / theme.nom
    try:
        dossier.mkdir(parents=True, exist_ok=True)
        copie = dossier / "theme.toml"
        if not (copie.exists() and os.path.samefile(chemin, copie)):     # rejouer depuis la copie du corpus
            shutil.copyfile(chemin, copie)
        rapport = construire(theme, dossier, instances)
    except OSError as err:
        print(f"ERREUR : écriture dans {dossier} impossible : {err}", file=sys.stderr)
        return 2
    print(f"corpus {theme.nom} : {rapport.telecharges} clip(s) téléchargé(s), {rapport.deja_presents} déjà présent(s), "
          f"{rapport.ecartes_licence} écarté(s) pour licence, {rapport.ecartes_duree} pour durée")
    for ligne in rapport.sources_ignorees:
        print(f"source ignorée : {ligne}")
    for ligne in rapport.erreurs:
        print(f"erreur : {ligne}")
    if rapport.telecharges + rapport.deja_presents == 0:
        print(f"ERREUR : aucun clip dans le corpus {theme.nom} (voir les lignes ci-dessus)", file=sys.stderr)
        return 1
    return 0


def cmd_credits(args) -> int:
    dossier = dossier_theme(args)
    if dossier is None:
        return 2
    try:
        sortie = credits.ecrire_credits(dossier, Path(args.selection) if args.selection else None)
    except OSError as err:
        print(f"ERREUR : lecture ou écriture impossible : {err}", file=sys.stderr)
        return 2
    except ValueError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1
    print(f"écrit : {sortie}")
    return 0


def cmd_list(args) -> int:
    dossier = dossier_theme(args)
    if dossier is None:
        return 2
    try:
        fiches = credits.lire_fiches(dossier)
    except OSError as err:
        print(f"ERREUR : lecture impossible : {err}", file=sys.stderr)
        return 2
    except ValueError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1
    licences = Counter(f.get("licence") or "inconnue" for f in fiches)
    duree = sum(f["duree"] for f in fiches if isinstance(f.get("duree"), (int, float)))
    print(f"{dossier.name} : {len(fiches)} clip(s), {duree / 60:.1f} min connues")
    for licence, nombre in sorted(licences.items()):
        print(f"  {licence} : {nombre}")
    print(f"index : {'présent' if (dossier / 'index.json').exists() else 'absent (corpus.py index)'}")
    return 0


def construire_parseur() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Corpus documentaire : archives vidéo libres, index CLIP, recherche.")
    p.add_argument("--racine", default=str(DOSSIER_DEFAUT), help="dossier des corpus (défaut : 08-video/corpus)")
    sous = p.add_subparsers(dest="commande", required=True)
    b = sous.add_parser("build", help="rechercher et télécharger les clips d'un thème")
    b.add_argument("theme", help="fichier thème TOML")
    b.set_defaults(fonction=cmd_build)
    c = sous.add_parser("credits", help="écrire credits.md")
    c.add_argument("theme")
    c.add_argument("--selection", help="selections.json (sinon : tout le corpus)")
    c.set_defaults(fonction=cmd_credits)
    li = sous.add_parser("list", help="inventaire du corpus")
    li.add_argument("theme")
    li.set_defaults(fonction=cmd_list)
    return p


def remonter_racine(argv: list[str]) -> list[str]:
    """--racine est accepté après la sous-commande comme avant : on le replace en tête."""
    for i, arg in enumerate(argv):
        if i == 0:
            continue
        if arg.startswith("--racine="):
            return [arg] + argv[:i] + argv[i + 1:]
        if arg == "--racine" and i + 1 < len(argv):
            return argv[i:i + 2] + argv[:i] + argv[i + 2:]
    return argv


def main(argv: list[str] | None = None) -> int:
    argv = remonter_racine(list(sys.argv[1:] if argv is None else argv))
    args = construire_parseur().parse_args(argv)
    return args.fonction(args)


if __name__ == "__main__":
    sys.exit(main())
