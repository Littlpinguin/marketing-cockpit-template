#!/usr/bin/env python3
"""
Crée un deck à partir du starter du moteur de slides, aux couleurs de la marque.

Le starter `06-graphic-design/presentations/templates/base.html` est vendorisé
depuis slides-agent (docs/vendored-slides.md) : il porte le moteur complet et un
`:root` aux valeurs neutres d'exemple. La marque du projet vit dans
`06-graphic-design/presentations/tokens.css`, dont le bloc de marque est généré
depuis `01-brand/tokens.json` par `scripts/build-tokens.py`.

Ce script fait le pont entre les deux, sans rien réécrire du moteur :

  1. copie le starter dans `06-graphic-design/presentations/decks/<slug>.html` ;
  2. remplace son premier bloc `:root { ... }` par le premier bloc `:root` de
     tokens.css (mêmes noms de variables, valeurs de la marque) ;
  3. retire la note « VENDORED » du starter : le deck appartient au projet ;
  4. remplit le `{{DECK_TITLE}}` du <title> si --titre est donné.

Le moteur, lui, se reprend tel quel : la QA du deck vérifie sa présence.

Usage :
  python3 06-graphic-design/scripts/new-deck.py <slug> [--titre "Titre"] [--force]

Puis : python3 06-graphic-design/presentations/scripts/qa.py \\
       06-graphic-design/presentations/decks/<slug>.html

Codes de sortie : 0 deck écrit, 1 deck déjà présent (sans --force), 2 usage
incorrect ou fichier source illisible.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

MOTEUR = "06-graphic-design/presentations"
STARTER = f"{MOTEUR}/templates/base.html"
TOKENS = f"{MOTEUR}/tokens.css"
DECKS = f"{MOTEUR}/decks"
BANDEAU_TETE = "VENDORED from slides-agent"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
ROOT_RE = re.compile(r":root\s*\{")


class DeckError(Exception):
    """Starter ou fichier de marque inutilisable."""


def bloc_root(texte: str, debut_recherche: int = 0) -> tuple[int, int]:
    """Bornes [début, fin) du premier bloc `:root { ... }` hors commentaire CSS.

    Les accolades sont appariées en ignorant celles des commentaires et des
    chaînes (une data-URI peut en contenir).
    """
    i, n = debut_recherche, len(texte)
    while i < n:
        if texte.startswith("/*", i):
            fin = texte.find("*/", i + 2)
            i = n if fin == -1 else fin + 2
            continue
        trouve = ROOT_RE.match(texte, i)
        if trouve:
            profondeur, j, quote = 1, trouve.end(), ""
            while j < n and profondeur:
                c = texte[j]
                if quote:
                    if c == "\\":
                        j += 1
                    elif c == quote:
                        quote = ""
                elif texte.startswith("/*", j):
                    fin = texte.find("*/", j + 2)
                    j = n if fin == -1 else fin + 1
                elif c in "\"'":
                    quote = c
                elif c == "{":
                    profondeur += 1
                elif c == "}":
                    profondeur -= 1
                j += 1
            if profondeur:
                raise DeckError("bloc :root non refermé")
            return i, j
        i += 1
    raise DeckError("aucun bloc :root trouvé")


def sans_bandeau(html: str) -> str:
    """Retire le commentaire HTML qui porte la note « VENDORED » du starter."""
    position = html.find(BANDEAU_TETE)
    if position == -1:
        return html
    debut = html.rfind("<!--", 0, position)
    fin = html.find("-->", position)
    if debut == -1 or fin == -1:
        return html
    fin += 3
    if html[fin:fin + 1] == "\n":
        fin += 1
    return html[:debut] + html[fin:]


FAMILLES_GENERIQUES = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui",
                       "ui-serif", "ui-sans-serif", "ui-monospace", "ui-rounded"}


def familles_manquantes(deck: str) -> list[str]:
    """Familles de marque (--font-display / --font-mono) que le <link> Google Fonts
    du deck ne charge pas : le starter ne charge que celles de la palette d'exemple."""
    debut, fin = bloc_root(deck, max(deck.find("<style"), 0))
    familles = []
    for valeur in re.findall(r"--font-(?:display|mono)\s*:\s*([^;]+);", deck[debut:fin]):
        premiere = valeur.split(",")[0].strip().strip("\"'")
        if premiere and premiere.lower() not in FAMILLES_GENERIQUES:
            familles.append(premiere)
    chargees = {f.replace("+", " ") for f in re.findall(r"family=([^:&\"']+)", deck)}
    return [f for f in familles if f not in chargees]


def composer(starter: str, tokens_css: str, titre: str | None = None) -> str:
    """Le starter, avec le :root de la marque à la place de son :root neutre."""
    style = starter.find("<style")
    if style == -1:
        raise DeckError("le starter n'a pas de bloc <style>")
    debut, fin = bloc_root(starter, style)
    t_debut, t_fin = bloc_root(tokens_css)
    deck = starter[:debut] + tokens_css[t_debut:t_fin] + starter[fin:]
    deck = sans_bandeau(deck)
    if titre:
        echappe = titre.replace("&", "&amp;").replace("<", "&lt;")
        deck = re.sub(r"(<title>[^<]*)\{\{DECK_TITLE\}\}", lambda m: m.group(1) + echappe,
                      deck, count=1)
    return deck


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Crée un deck depuis le starter vendorisé, avec le :root de "
                    f"{TOKENS} (la marque du projet).")
    parser.add_argument("slug", help="nom du fichier, en minuscules et tirets "
                                     "(ex. revue-t3-2026-v1)")
    parser.add_argument("--titre", help="remplit {{DECK_TITLE}} (le <title> du deck)")
    parser.add_argument("--force", action="store_true", help="écraser un deck existant")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]),
                        help="racine du dépôt (défaut : deux niveaux au-dessus de scripts/)")
    args = parser.parse_args(argv)

    if not SLUG_RE.match(args.slug):
        print(f"ERREUR : slug invalide « {args.slug} » (minuscules, chiffres, tirets)",
              file=sys.stderr)
        return 2
    racine = Path(args.root)
    cible = racine / DECKS / f"{args.slug}.html"
    if cible.exists() and not args.force:
        print(f"ERREUR : {cible.relative_to(racine)} existe déjà (--force pour l'écraser)",
              file=sys.stderr)
        return 1
    try:
        starter = (racine / STARTER).read_text(encoding="utf-8")
        tokens_css = (racine / TOKENS).read_text(encoding="utf-8")
        deck = composer(starter, tokens_css, args.titre)
    except (OSError, DeckError) as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2

    cible.parent.mkdir(parents=True, exist_ok=True)
    cible.write_text(deck, encoding="utf-8")
    rel = cible.relative_to(racine)
    print(f"écrit : {rel}")
    manquantes = familles_manquantes(deck)
    if manquantes:
        print(f"polices : le <link> du starter ne charge pas {', '.join(manquantes)}. "
              "Le remplacer par les polices de la marque (woff2 locaux de "
              "01-brand/assets/fonts/ pour un livrable, Google Fonts pour un deck interne).")
    print(f"QA : python3 {MOTEUR}/scripts/qa.py {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
