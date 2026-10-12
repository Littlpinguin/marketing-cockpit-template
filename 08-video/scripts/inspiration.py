#!/usr/bin/env python3
"""Bibliothèque d'inspiration : chercher des vidéos de référence réalisées avec Claude Opus 5.5.

Usage :
    python3 08-video/scripts/inspiration.py chercher "kinetic typography product launch" --top 8
    python3 08-video/scripts/inspiration.py chercher "orbit camera" --categorie 3d --tech threejs
    python3 08-video/scripts/inspiration.py chercher "data bar chart" --categorie explainer --avec-remake
    python3 08-video/scripts/inspiration.py montrer <slug>
    python3 08-video/scripts/inspiration.py categories
    options communes : [--source URL|FICHIER] [--rafraichir] [--format text|json] [--cache FICHIER]

Source : yihui-dev/awesome-opus5-5-videos (data/videos.json, 853 entrées à l'écriture).
Le dépôt est sous licence MIT, mais chaque vidéo et chaque prompt appartient à son
créateur : rien n'est copié dans le dépôt du template. Les données sont récupérées
à l'usage et gardées dans .cache/inspiration/opus-5-5-videos.json (dossier ignoré par
Git), valables 7 jours. Si le réseau manque, un cache périmé sert avec un avertissement.
Doctrine d'emploi : 08-video/inspiration.md.

chercher classe les vidéos par nombre de mots de la requête trouvés (sans accents ni
casse) dans le titre, le prompt et les techs, puis par date d'ajout décroissante. Les
mots courts (moins de 4 lettres) se comparent entiers, les autres par leur début
(« particle » trouve « particles »). La requête s'écrit en anglais : les prompts le sont.

Un cache daté du futur compte comme périmé. En sortie texte, les champs tiers
(titre, auteur, liens, techs) sont mis sur une ligne et bornés : ils ne peuvent ni
forger de lignes ni noyer le terminal ; la sortie JSON les rend tels quels.

Codes de sortie : 0 résultat(s) ; 1 aucun résultat (ou slug inconnu) ; 2 erreur
d'usage (adresse ou port de source invalide compris), requête vide, ou ni réseau ni
cache utilisable (source illisible comprise).
"""
from __future__ import annotations

import argparse
import http.client
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SOURCE_DEFAUT = "https://raw.githubusercontent.com/yihui-dev/awesome-opus5-5-videos/main/data/videos.json"
CACHE_DEFAUT = RACINE / ".cache" / "inspiration" / "opus-5-5-videos.json"
VALIDITE_JOURS = 7
TAILLE_MAX = 32 * 1024 * 1024          # octets lus au plus, source comme cache
DELAI = 30                             # secondes
EXTRAIT_MAX = 240                      # caractères
CHAMP_MAX = 160                        # caractères d'un titre, d'un auteur ou de la liste des techs affichés
LIEN_MAX = 300                         # caractères d'un lien affiché
TOP_DEFAUT = 8
CATEGORIES = ("motion", "explainer", "3d", "interactive")
SCHEMAS = ("http", "https")
USER_AGENT = "marketing-cockpit-template-inspiration/1.0 (+https://github.com/Littlpinguin/marketing-cockpit-template)"
RAPPEL = "Chaque vidéo et chaque prompt appartient à son créateur : s'en inspirer, ne rien recopier."
# Données tierces affichées dans un terminal : on retire les caractères de contrôle (séquences d'échappement
# comprises), les marques de réécriture du sens de lecture et les demi-paires UTF-16 isolées (« \ud83d »
# seul, valide en JSON mais ni encodable ni affichable). Retours à la ligne et tabulations restent.
CARACTERES_DE_CONTROLE = re.compile("[\x00-\x08\x0b-\x1f\x7f-\x9f\u202a-\u202e\u2066-\u2069\ud800-\udfff]")
MOTS_VIDES = frozenset(
    "a an the of and or to in on at with for from by is are it this that into as i "
    "le la les l d de du des un une et ou en au aux avec pour sur par dans".split())


class ErreurFatale(Exception):
    """Fin immédiate avec ERREUR et le code 2 (usage, ou aucune donnée utilisable)."""


class ErreurSource(Exception):
    """Source injoignable ou inutilisable : le cache peut prendre le relais."""


class _RedirectionRefusee(Exception):
    pass


# ------------------------------------------------------------------ texte

def sans_accents(texte: str) -> str:
    decompose = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in decompose if not unicodedata.combining(c)).lower()


def mots(texte: str) -> list[str]:
    """Mots en minuscules sans accents ; « three.js » et « three js » deviennent « threejs »."""
    propre = re.sub(r"three[ .\-]?js", "threejs", sans_accents(texte or ""))
    return re.findall(r"[a-z0-9]+", propre)


def mots_requete(requete: str) -> list[str]:
    """Mots distincts de la requête, mots vides retirés tant qu'il en reste un autre."""
    distincts = list(dict.fromkeys(mots(requete)))
    utiles = [m for m in distincts if m not in MOTS_VIDES]
    return utiles or distincts


def compacter(texte: str) -> str:
    return " ".join((texte or "").split())


def extrait(prompt: str, limite: int = EXTRAIT_MAX) -> str:
    texte = compacter(prompt)
    return texte if len(texte) <= limite else texte[:limite - 1] + "…"


def champ(texte: str | None, limite: int = CHAMP_MAX) -> str:
    """Un champ tiers pour l'affichage texte : sur une seule ligne, borné."""
    return extrait(texte or "", limite)


def etiquette(video: dict) -> str:
    """Le titre, ou à défaut le début du prompt."""
    titre = champ(video["title"])
    if titre:
        return titre
    debut = extrait(video["prompt"], 72)
    return debut or champ(video["slug"])


# ------------------------------------------------------------------ données

def nettoyer(texte: str) -> str:
    return CARACTERES_DE_CONTROLE.sub("", texte)


def normaliser(brut) -> dict | None:
    """Une entrée au format connu, ou None si elle n'a pas de slug exploitable."""
    if not isinstance(brut, dict):
        return None

    def texte(cle):
        valeur = brut.get(cle)
        valeur = nettoyer(valeur) if isinstance(valeur, str) else ""
        return valeur if valeur.strip() else None

    slug = texte("slug")
    if slug is None:
        return None
    techs = brut.get("tech_tags")
    prompt = brut.get("prompt")
    return {
        "slug": slug.strip(),
        "title": texte("title"),
        "author": texte("author"),
        "author_url": texte("author_url"),
        "post_url": texte("post_url"),
        "category": texte("category"),
        "tech_tags": [nettoyer(t).strip() for t in techs if isinstance(t, str) and nettoyer(t).strip()]
        if isinstance(techs, list) else [],
        "prompt": nettoyer(prompt) if isinstance(prompt, str) else "",
        "prompt_partial": bool(brut.get("prompt_partial")),
        "poster_url": texte("poster_url"),
        "skillry_url": texte("skillry_url"),
        "added": texte("added"),
        "has_remake": bool(brut.get("has_remake")),
    }


def analyser(octets: bytes) -> list[dict]:
    """Octets de la source en liste d'entrées ; ErreurSource si le contenu n'est pas exploitable."""
    texte = octets.decode("utf-8-sig", errors="replace")
    try:
        donnees = json.loads(texte)
    except (ValueError, RecursionError) as err:
        ligne = getattr(err, "lineno", None)
        raise ErreurSource("JSON invalide" + (f" (ligne {ligne})" if ligne else "")) from None
    if not isinstance(donnees, list):
        raise ErreurSource("JSON inattendu : une liste de vidéos est attendue")
    videos = [v for v in map(normaliser, donnees) if v]
    if not videos:
        raise ErreurSource("aucune vidéo exploitable dans la source")
    return videos


# ------------------------------------------------------------------ source

class _Redirections(urllib.request.HTTPRedirectHandler):
    """Ne suit une redirection que vers http ou https (jamais ftp ni file)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme.lower() not in SCHEMAS:
            raise _RedirectionRefusee("redirection refusée (http et https seulement)")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def classer_source(source: str) -> tuple[str, str]:
    """('url', adresse) ou ('fichier', chemin absolu) ; ErreurFatale pour tout autre schéma."""
    try:
        schema = urllib.parse.urlsplit(source).scheme.lower()
    except ValueError:
        raise ErreurFatale("adresse de source invalide") from None
    if schema in SCHEMAS:
        try:
            urllib.parse.urlsplit(source).port           # « :abc » ou « :99999 » lèvent ValueError
        except ValueError:
            raise ErreurFatale("adresse de source invalide : port non numérique ou hors de 0 à 65535") from None
        return "url", source
    if schema:
        raise ErreurFatale(f"adresse refusée : {schema}:// (http et https seulement)")
    try:
        return "fichier", str(Path(source).expanduser().resolve())
    except (OSError, ValueError, RuntimeError):
        raise ErreurFatale("chemin de source invalide") from None


def afficher(nature: str, cle: str) -> str:
    """La source telle qu'on la nomme dans un message : sans identifiants, paramètres ni fragment."""
    if nature == "fichier":
        return cle
    parts = urllib.parse.urlsplit(cle)
    hote = parts.hostname or ""
    port = f":{parts.port}" if parts.port else ""
    return f"{parts.scheme}://{hote}{port}{parts.path}"


def trop_gros() -> ErreurSource:
    return ErreurSource(f"réponse trop volumineuse (limite de {TAILLE_MAX / 1048576:.1f} Mo)")


def lire_url(adresse: str) -> bytes:
    requete = urllib.request.Request(adresse, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.build_opener(_Redirections).open(requete, timeout=DELAI) as reponse:
            octets = reponse.read(TAILLE_MAX + 1)
    except _RedirectionRefusee as err:
        raise ErreurSource(str(err)) from None
    except urllib.error.HTTPError as err:
        raise ErreurSource(f"HTTP {err.code}") from None
    except urllib.error.URLError as err:
        delai = isinstance(err.reason, TimeoutError)
        raise ErreurSource("délai dépassé" if delai else "connexion impossible") from None
    except TimeoutError:
        raise ErreurSource("délai dépassé") from None
    except http.client.HTTPException:
        raise ErreurSource("réponse HTTP invalide") from None
    except ValueError:
        raise ErreurSource("adresse invalide") from None
    except OSError as err:
        raise ErreurSource(f"lecture impossible ({type(err).__name__})") from None
    if len(octets) > TAILLE_MAX:
        raise trop_gros()
    return octets


def lire_fichier(chemin: str) -> bytes:
    try:
        with open(chemin, "rb") as source:
            octets = source.read(TAILLE_MAX + 1)
    except FileNotFoundError:
        raise ErreurSource("fichier introuvable") from None
    except IsADirectoryError:
        raise ErreurSource("c'est un dossier, pas un fichier") from None
    except PermissionError:
        raise ErreurSource("accès refusé") from None
    except (OSError, ValueError) as err:
        raise ErreurSource(f"lecture impossible ({type(err).__name__})") from None
    if len(octets) > TAILLE_MAX:
        raise trop_gros()
    return octets


# ------------------------------------------------------------------ cache

def lire_horodatage(valeur) -> datetime | None:
    if not isinstance(valeur, str):
        return None
    try:
        moment = datetime.fromisoformat(valeur)
    except ValueError:
        return None
    return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)


def lire_cache(chemin: Path) -> dict | None:
    """Le cache {source, recupere, videos}, ou None s'il manque, est abîmé ou vide."""
    try:
        with chemin.open("rb") as fichier:
            octets = fichier.read(TAILLE_MAX + 1)
        if len(octets) > TAILLE_MAX:
            return None
        enveloppe = json.loads(octets.decode("utf-8-sig", errors="replace"))
    except (OSError, ValueError, RecursionError):
        return None
    if not isinstance(enveloppe, dict) or not isinstance(enveloppe.get("videos"), list):
        return None
    videos = [v for v in map(normaliser, enveloppe["videos"]) if v]
    if not videos:
        return None
    source = enveloppe.get("source")
    return {"source": source if isinstance(source, str) else None,
            "recupere": lire_horodatage(enveloppe.get("recupere")), "videos": videos}


def cache_frais(cache: dict) -> bool:
    """Récupéré il y a 7 jours au plus. Une date dans le futur (horloge déréglée, cache retouché) est périmée."""
    if cache["recupere"] is None:
        return False
    age = datetime.now(timezone.utc) - cache["recupere"]
    return timedelta(0) <= age <= timedelta(days=VALIDITE_JOURS)


def ecrire_cache(chemin: Path, cle: str, videos: list[dict]) -> None:
    """Écriture atomique : un cache n'est jamais lu à moitié écrit, et un échec ne laisse pas de fichier .tmp.

    JSON en ASCII (ensure_ascii) : un caractère que l'UTF-8 ne sait pas encoder, comme une demi-paire
    UTF-16 isolée venue de la source, s'écrit échappé au lieu de faire échouer l'écriture.
    """
    enveloppe = {"source": cle, "recupere": datetime.now(timezone.utc).isoformat(timespec="seconds"), "videos": videos}
    temporaire = chemin.with_name(f"{chemin.name}.{os.getpid()}.tmp")
    try:
        chemin.parent.mkdir(parents=True, exist_ok=True)
        temporaire.write_text(json.dumps(enveloppe, ensure_ascii=True) + "\n", encoding="utf-8")
        temporaire.replace(chemin)
    except BaseException:
        try:
            temporaire.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def avertir(message: str) -> None:
    print(f"avertissement : {message}", file=sys.stderr)


def charger(args) -> list[dict]:
    """Les vidéos : cache frais de cette source, sinon source (et cache réécrit), sinon cache de repli."""
    nature, cle = classer_source(args.source)
    cache = lire_cache(args.cache)
    meme_source = cache is not None and cache["source"] == cle
    if meme_source and not args.rafraichir and cache_frais(cache):
        return cache["videos"]
    try:
        octets = lire_url(cle) if nature == "url" else lire_fichier(cle)
        videos = analyser(octets)
    except ErreurSource as err:
        nom = afficher(nature, cle)
        if meme_source:
            date_cache = cache["recupere"].date().isoformat() if cache["recupere"] else "date inconnue"
            etat = "à jour" if cache_frais(cache) else f"périmé, plus de {VALIDITE_JOURS} jours"
            avertir(f"{nom} : {err} ; cache du {date_cache} utilisé ({etat})")
            return cache["videos"]
        suite = ("le cache existant vient d'une autre source" if cache is not None
                 else f"aucun cache dans {afficher('fichier', str(args.cache))}")
        raise ErreurFatale(f"source inutilisable ({nom} : {err}) et {suite}") from None
    try:
        ecrire_cache(args.cache, cle, videos)
    except (OSError, ValueError) as err:           # UnicodeError dérive de ValueError
        avertir(f"cache non écrit ({type(err).__name__}), la prochaine recherche relira la source")
    return videos


# ------------------------------------------------------------------ recherche

def date_ordinale(video: dict) -> int:
    try:
        return date.fromisoformat(video["added"] or "").toordinal()
    except ValueError:
        return 0


def classer(videos: list[dict], requete_mots: list[str], categorie: str | None, tech: str | None,
            avec_remake: bool) -> list[tuple[int, dict]]:
    """(score, vidéo) triés : plus de mots trouvés d'abord, puis plus récent, puis par slug."""
    tech = sans_accents(tech).strip() if tech else None
    trouvees = []
    for video in videos:
        if categorie and sans_accents(video["category"] or "") != categorie:
            continue
        if tech and tech not in {sans_accents(t).strip() for t in video["tech_tags"]}:
            continue
        if avec_remake and not video["has_remake"]:
            continue
        meule = set(mots(video["title"] or "")) | set(mots(video["prompt"])) | set(mots(" ".join(video["tech_tags"])))
        score = sum(1 for mot in requete_mots
                    if (mot in meule if len(mot) < 4 else any(t.startswith(mot) for t in meule)))
        if score:
            trouvees.append((score, video))
    trouvees.sort(key=lambda sv: (-sv[0], -date_ordinale(sv[1]), sv[1]["slug"]))
    return trouvees


# ------------------------------------------------------------------ sorties

def ligne_auteur(video: dict) -> str:
    nom = champ(video["author"]) or "inconnu"
    lien = champ(video["author_url"], LIEN_MAX)
    return f"{nom} ({lien})" if lien else nom


def ligne_techs(video: dict) -> str:
    return champ(", ".join(video["tech_tags"])) or "(aucune)"


def bloc_resultat(rang: int, score: int, total_mots: int, video: dict) -> str:
    marque = " (prompt partiel)" if video["prompt_partial"] else ""
    lignes = [
        f"{rang}. {etiquette(video)}  [{champ(video['category']) or 'sans catégorie'}]",
        f"   mots trouvés : {score} sur {total_mots}",
        f"   techs : {ligne_techs(video)}",
        f"   auteur : {ligne_auteur(video)}",
        f"   prompt : {extrait(video['prompt']) or '(vide)'}{marque}",
        f"   publication : {champ(video['post_url'], LIEN_MAX) or '(aucune)'}",
    ]
    if video["skillry_url"]:
        lignes.append(f"   skillry : {champ(video['skillry_url'], LIEN_MAX)}")
    lignes.append(f"   slug : {champ(video['slug'])}")
    return "\n".join(lignes)


def json_resultat(score: int, video: dict) -> dict:
    sortie = {cle: valeur for cle, valeur in video.items() if cle != "prompt"}
    return {"score": score, **sortie, "extrait": extrait(video["prompt"])}


def afficher_json(donnees) -> None:
    print(json.dumps(donnees, ensure_ascii=False, indent=2))


def cmd_chercher(args) -> int:
    requete = compacter(" ".join(args.mots))
    requete_mots = mots_requete(requete)
    if not requete_mots:
        print("ERREUR : requête vide : donner quelques mots en anglais "
              "(par exemple chercher \"logo reveal particles\")", file=sys.stderr)
        return 2
    videos = charger(args)
    trouvees = classer(videos, requete_mots, args.categorie, args.tech, args.avec_remake)[:args.top]
    if args.format == "json":
        afficher_json([json_resultat(score, video) for score, video in trouvees])
    elif trouvees:
        print("\n\n".join(bloc_resultat(i, score, len(requete_mots), video)
                          for i, (score, video) in enumerate(trouvees, 1)))
        print(f"\n{RAPPEL}")
    else:
        print(f"aucun résultat pour « {requete} »" +
              (" avec ces filtres" if args.categorie or args.tech or args.avec_remake else ""))
    return 0 if trouvees else 1


def cmd_montrer(args) -> int:
    videos = charger(args)
    video = next((v for v in videos if v["slug"] == args.slug), None)
    if video is None:
        print(f"ERREUR : aucune vidéo de slug « {args.slug} » (le trouver avec la commande chercher)", file=sys.stderr)
        return 1
    if args.format == "json":
        afficher_json(video)
        return 0
    lignes = [
        f"slug : {champ(video['slug'])}",
        f"titre : {champ(video['title']) or '(sans titre)'}",
        f"catégorie : {champ(video['category']) or '(aucune)'}",
        f"techs : {ligne_techs(video)}",
        f"auteur : {ligne_auteur(video)}",
        f"ajoutée le : {champ(video['added']) or '(date inconnue)'}",
        f"publication : {champ(video['post_url'], LIEN_MAX) or '(aucune)'}",
    ]
    if video["skillry_url"]:
        lignes.append(f"skillry : {champ(video['skillry_url'], LIEN_MAX)}")
    if video["poster_url"]:
        lignes.append(f"affiche : {champ(video['poster_url'], LIEN_MAX)}")
    lignes += ["prompt :", video["prompt"] or "(vide)"]
    if video["prompt_partial"]:
        lignes.append("(prompt partiel)")
    lignes += ["", RAPPEL]
    print("\n".join(lignes))
    return 0


def compter(valeurs) -> dict[str, int]:
    compte: dict[str, int] = {}
    for valeur in valeurs:
        compte[valeur] = compte.get(valeur, 0) + 1
    return dict(sorted(compte.items(), key=lambda kv: (-kv[1], kv[0])))


def cmd_categories(args) -> int:
    videos = charger(args)
    categories = compter(v["category"] for v in videos if v["category"])
    techs = compter(t for v in videos for t in dict.fromkeys(v["tech_tags"]))
    if args.format == "json":
        afficher_json({"total": len(videos), "categories": categories, "techs": techs})
        return 0
    lignes = [f"{len(videos)} vidéo(s) de référence", "catégories :"]
    lignes += [f"  {champ(nom)} : {nombre}" for nom, nombre in categories.items()]
    lignes.append("techs :")
    lignes += [f"  {champ(nom)} : {nombre}" for nom, nombre in techs.items()]
    print("\n".join(lignes))
    return 0


# ------------------------------------------------------------------ ligne de commande

def _entier_positif(valeur: str) -> int:
    try:
        nombre = int(valeur)
    except ValueError:
        nombre = 0
    if nombre < 1:
        raise argparse.ArgumentTypeError(f"« {valeur} » n'est pas un entier d'au moins 1")
    return nombre


def construire_parseur() -> argparse.ArgumentParser:
    communs = argparse.ArgumentParser(add_help=False)
    communs.add_argument("--source", default=SOURCE_DEFAUT,
                         help="URL http(s) ou fichier de données (défaut : le videos.json du dépôt awesome-opus5-5-videos)")
    communs.add_argument("--rafraichir", action="store_true",
                         help="relire la source même si le cache est valable (7 jours)")
    communs.add_argument("--format", choices=("text", "json"), default="text", help="forme de la sortie (défaut : text)")
    communs.add_argument("--cache", type=Path, default=CACHE_DEFAUT,
                         help="fichier de cache (défaut : .cache/inspiration/opus-5-5-videos.json, ignoré par Git)")
    p = argparse.ArgumentParser(prog="inspiration.py",
                                description="Vidéos de référence réalisées avec Claude Opus 5.5 : chercher, montrer, compter. "
                                            "Chaque vidéo et chaque prompt appartient à son créateur.")
    sous = p.add_subparsers(dest="commande", required=True)
    c = sous.add_parser("chercher", parents=[communs], help="chercher des références par mots (en anglais)")
    c.add_argument("mots", nargs="*", help="mots de la requête, en anglais")
    c.add_argument("--categorie", choices=CATEGORIES, help="ne garder qu'une catégorie")
    c.add_argument("--tech", help="ne garder que les vidéos portant ce tag technique (canvas, svg, threejs, shader, gsap...)")
    c.add_argument("--avec-remake", action="store_true", help="ne garder que les vidéos qui ont un remake publié")
    c.add_argument("--top", type=_entier_positif, default=TOP_DEFAUT,
                   help=f"nombre de résultats (défaut : {TOP_DEFAUT})")
    c.set_defaults(fonction=cmd_chercher)
    m = sous.add_parser("montrer", parents=[communs], help="afficher une entrée en entier")
    m.add_argument("slug")
    m.set_defaults(fonction=cmd_montrer)
    k = sous.add_parser("categories", parents=[communs], help="compter les catégories et les techs")
    k.set_defaults(fonction=cmd_categories)
    return p


def main(argv: list[str] | None = None) -> int:
    for flux in (sys.stdout, sys.stderr):       # un terminal sans UTF-8 ne doit pas faire planter l'affichage
        try:
            flux.reconfigure(errors="replace")
        except (AttributeError, ValueError, OSError):
            pass
    try:
        args = construire_parseur().parse_args(sys.argv[1:] if argv is None else argv)
    except SystemExit as sortie:
        return sortie.code if isinstance(sortie.code, int) else 2
    try:
        return args.fonction(args)
    except ErreurFatale as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
