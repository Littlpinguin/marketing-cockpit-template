#!/usr/bin/env python3
"""Remplace les URL absolues vers la racine du dépôt par des chemins relatifs.

Une composition HTML ou une feuille CSS produite par un agent référence souvent
ses assets par une URL absolue qui part du dossier personnel de la machine
(`file:///home/<utilisateur>/...` ou `/Users/<utilisateur>/...`). Le fichier ne
s'ouvre alors que sur cette machine, et il casse dès que le dépôt est cloné
ailleurs. Ce script réécrit ces URL en chemins relatifs au dossier du fichier.

Ce qui est réécrit, deux formes :

  - `file://<racine>/<reste>`, quel que soit son contexte ;
  - le chemin absolu nu `<racine>/<reste>`, mais seulement là où il sert
    d'URL : après `href=`, `src=`, `srcset=` ou dans un `url()` CSS, et pour
    chaque candidat d'un `srcset`. Un chemin absolu écrit ailleurs, dans un
    commentaire ou dans de la prose, désigne un fichier dont on parle, pas une
    ressource que le navigateur charge : il est laissé intact.

L'URL se termine au premier guillemet, espace, parenthèse fermante ou chevron.

Ce qui ne l'est pas : les URL absolues qui pointent hors de la racine, par
exemple vers un dépôt frère (le code du site web, cloné à côté). Aucun chemin
relatif ne traverse proprement deux dépôts : elles restent telles quelles.

Encodage, en une passe : l'URL est d'abord coupée au premier `?` ou `#` non
encodé, car ce qui suit est une query ou un fragment, pas un nom de fichier
(`sprite.svg#icone` vise un fragment de `sprite.svg`) ; ce suffixe traverse le
script intact et se recolle au résultat. Seule la partie chemin est décodée
(`%20` redevient une espace) pour retrouver le fichier sur le disque, puis
ré-encodée à minima : espace, `#` et `?`, les trois caractères qui, à
l'intérieur d'un nom de fichier, casseraient l'URL. Les lettres accentuées sont
laissées telles quelles : les navigateurs les acceptent et le fichier reste
lisible.

Usage :
    python3 scripts/relativize-paths.py --dry-run fichier.html [autre.css ...]
    python3 scripts/relativize-paths.py fichier.html [autre.css ...]
"""
from __future__ import annotations

import argparse
import os
import pathlib
import re
import sys
from urllib.parse import unquote

EXTENSIONS = {".html", ".htm", ".css"}
# Fin d'URL : guillemet, espace, parenthèse fermante ou chevron.
FIN_URL = "\"'()<>\\s"
# Attributs dont la valeur est une URL. « srcset » avant « src » : l'alternance
# est testée dans l'ordre, et une frontière de mot referme chaque nom.
ATTRIBUTS_URL = r"\b(?:href|srcset|src)\b\s*=\s*[\"']?"
# Ouverture d'un `url()` CSS, guillemets facultatifs.
OUVERTURE_URL_CSS = r"url\(\s*[\"']?"
# Caractères ré-encodés dans le chemin relatif produit.
A_ENCODER = {" ": "%20", "#": "%23", "?": "%3F"}


def racine_du_depot() -> pathlib.Path:
    """Racine du dépôt, déduite de l'emplacement du script."""
    return pathlib.Path(__file__).resolve().parents[1]


def _reste() -> str:
    return "[^" + FIN_URL + "]*"


def _motif(racine: pathlib.Path) -> re.Pattern:
    """URL absolues réécrites hors d'un `srcset` : `file://` ou chemin nu en contexte.

    Le préfixe capturé (`href="`, `url(`…) est réémis tel quel par la
    substitution : seule la partie chemin change.
    """
    r = re.escape(str(racine))
    return re.compile(
        "(?P<prefixe>file://|" + ATTRIBUTS_URL + "|" + OUVERTURE_URL_CSS + ")"
        + r + "/(?P<reste>" + _reste() + ")")


def _motif_srcset() -> re.Pattern:
    """Valeur complète d'un attribut `srcset`, guillemets compris."""
    return re.compile(r"srcset\s*=\s*([\"'])(?P<valeur>.*?)\1", re.S)


def _motif_dans_srcset(racine: pathlib.Path) -> re.Pattern:
    """URL absolue à l'intérieur d'un `srcset`, `file://` facultatif.

    Un `srcset` liste plusieurs candidats séparés par des virgules. Seul le
    premier suit l'attribut : les suivants n'ont aucun préfixe, et ne se
    reconnaissent que parce qu'on sait déjà être dans un `srcset`. Cette passe
    prend donc les deux formes d'un coup, sans quoi elle couperait le `file://`
    d'un candidat en deux.
    """
    return re.compile(
        "(?:file://)?" + re.escape(str(racine)) + "/(?P<reste>" + _reste() + ")")


def _encoder(chemin: str) -> str:
    for brut, encode in A_ENCODER.items():
        chemin = chemin.replace(brut, encode)
    return chemin


def _couper_suffixe(url_reste: str) -> tuple[str, str]:
    """Sépare la partie chemin de l'URL de sa query et de son fragment.

    `sprite.svg#icone` vise un fragment du fichier, pas un fichier nommé
    « sprite.svg#icone » : le `#` et ce qui le suit sortent du chemin et
    traversent le script intacts.
    """
    positions = [p for p in (url_reste.find("?"), url_reste.find("#")) if p != -1]
    if not positions:
        return url_reste, ""
    coupe = min(positions)
    return url_reste[:coupe], url_reste[coupe:]


def chemin_relatif(url_reste: str, fichier: pathlib.Path,
                   racine: pathlib.Path) -> str:
    """Chemin relatif, depuis le dossier du fichier, vers la cible de l'URL."""
    chemin, suffixe = _couper_suffixe(url_reste)
    cible = racine / unquote(chemin)
    relatif = os.path.relpath(cible, fichier.parent)
    return _encoder(relatif) + suffixe


def _reecrire_srcsets(contenu: str, fichier: pathlib.Path, racine: pathlib.Path,
                      trouves: list[tuple[str, str]]) -> str:
    """Réécrit les URL de chaque `srcset`, candidats suivants compris.

    Cette passe court avant la passe générale : ce qu'elle a déjà rendu relatif
    ne commence plus par la racine, donc la passe suivante ne le revoit pas.
    """
    nu = _motif_dans_srcset(racine)

    def dans_la_valeur(attribut: re.Match) -> str:
        def un_candidat(m: re.Match) -> str:
            relatif = chemin_relatif(m.group("reste"), fichier, racine)
            trouves.append((m.group(0), relatif))
            return relatif
        return attribut.group(0).replace(
            attribut.group("valeur"), nu.sub(un_candidat, attribut.group("valeur")))

    return _motif_srcset().sub(dans_la_valeur, contenu)


def reecrire(contenu: str, fichier: pathlib.Path,
             racine: pathlib.Path) -> tuple[str, list[tuple[str, str]]]:
    """Rend le contenu réécrit et les couples (url absolue, chemin relatif)."""
    trouves: list[tuple[str, str]] = []
    contenu = _reecrire_srcsets(contenu, fichier, racine, trouves)

    def un(m: re.Match) -> str:
        # « file:// » disparaît avec le chemin absolu qu'il ouvrait ; un préfixe
        # d'attribut ou de `url()`, lui, est réémis tel quel.
        prefixe = m.group("prefixe")
        garde = "" if prefixe == "file://" else prefixe
        remplace = garde + chemin_relatif(m.group("reste"), fichier, racine)
        trouves.append((m.group(0), remplace))
        return remplace

    return _motif(racine).sub(un, contenu), trouves


def remplacements(contenu: str, fichier: pathlib.Path,
                  racine: pathlib.Path) -> list[tuple[str, str]]:
    """Liste des couples (url absolue, chemin relatif) trouvés dans le contenu."""
    return reecrire(contenu, fichier, racine)[1]


def relativiser_fichier(fichier: pathlib.Path, racine: pathlib.Path,
                        ecrire: bool = True) -> int:
    """Réécrit un fichier. Renvoie le nombre de remplacements.

    Avec `ecrire=False`, compte sans rien toucher. Un fichier sans occurrence
    n'est jamais réécrit, pour ne pas bouger sa date de modification.
    """
    fichier = pathlib.Path(fichier)
    contenu = fichier.read_text(encoding="utf-8")
    nouveau, couples = reecrire(contenu, fichier, racine)
    if not couples:
        return 0
    if ecrire:
        fichier.write_text(nouveau, encoding="utf-8")
    return len(couples)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="relativize-paths.py",
        description="Remplace les URL absolues vers la racine du dépôt, "
                    "file://<racine>/… comme chemin nu <racine>/… en position "
                    "d'URL, par des chemins relatifs, dans des .html et des .css.",
        epilog="Les URL pointant hors de la racine (un dépôt frère, par exemple) "
               "sont laissées intactes : aucun chemin relatif ne traverse deux dépôts.",
    )
    parser.add_argument("fichier", nargs="+",
                        help="fichier .html ou .css à réécrire. Répétable.")
    parser.add_argument("--root", default=None,
                        help="racine des URL absolues à remplacer "
                             "(défaut : la racine du dépôt).")
    parser.add_argument("--dry-run", action="store_true",
                        help="lister les remplacements sans rien écrire.")
    args = parser.parse_args(argv)

    racine = pathlib.Path(args.root).resolve() if args.root else racine_du_depot()

    fichiers = [pathlib.Path(f) for f in args.fichier]
    erreurs = 0
    for f in fichiers:
        if not f.is_file():
            sys.stderr.write(f"fichier introuvable : {f}\n")
            erreurs += 1
        elif f.suffix.lower() not in EXTENSIONS:
            sys.stderr.write(
                f"extension non traitée : {f} "
                f"(attendu : {', '.join(sorted(EXTENSIONS))})\n")
            erreurs += 1
    if erreurs:
        return 1

    total, touches = 0, 0
    for f in fichiers:
        contenu = f.read_text(encoding="utf-8")
        couples = remplacements(contenu, f, racine)
        if not couples:
            continue
        touches += 1
        total += len(couples)
        print(f"{f} : {len(couples)} remplacement(s)")
        for avant, apres in couples[:3]:
            print(f"    {avant}\n  → {apres}")
        if len(couples) > 3:
            print(f"    … et {len(couples) - 3} autre(s)")
        if not args.dry_run:
            relativiser_fichier(f, racine, ecrire=True)

    verbe = "à réécrire" if args.dry_run else "réécrits"
    print(f"{touches} fichier(s) {verbe}, {total} remplacement(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
