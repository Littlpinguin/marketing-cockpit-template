#!/usr/bin/env python3
"""
Construit l'inventaire des livrables dans _templates/inventory.md.

L'inventaire est l'index anti-répétition du repo : une ligne par livrable
produit (post, carrousel, email, article, deck, landing page, plan de com),
avec sa date, son canal, son type, son sujet, son chemin et son statut. Les
skills de production le lisent AVANT de rédiger et y ajoutent leur ligne
APRÈS livraison.

Usage:
  python3 scripts/build-inventory.py                  # reconstruit tout le tableau
  python3 scripts/build-inventory.py --check          # sort 1 si le tableau a dérivé
  python3 scripts/build-inventory.py --add <chemin>   # ajoute ou met à jour une ligne

Les dossiers inventoriés ne sont pas codés ici : ils sont déclarés dans
scripts/build-inventory.toml (un [[sources]] par dossier de production, avec
ses motifs de fichiers, son canal et son type). Un fork qui range ses
livrables ailleurs adapte ce fichier, pas le code.

Extensions retenues : `.md` et `.html`. Tout le reste est ignoré, y compris
les PDF, les images, les exports et les notes `.txt` : l'inventaire indexe le
livrable source, pas ses dérivés de fabrication.

Date d'un livrable, dans l'ordre : champ `date` du frontmatter, puis motif
`AAAA-MM-JJ` dans le nom du fichier, puis dans le nom du dossier parent. Un
fichier sans date exploitable n'est pas indexé ; le script le signale pour
qu'il soit renommé. Aucune date de modification n'est utilisée : elle change
au moindre clone et rendrait `--check` instable.

Les sujets repris d'un titre existant sont normalisés : les tirets longs,
bannis par la doctrine, deviennent des points médians.

Le script ne lit que du texte et n'écrit que _templates/inventory.md.
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import date as Date
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:    # tomllib est entré dans la bibliothèque standard en 3.11
    print(f"erreur : Python 3.11 ou plus récent est requis (module « tomllib » absent) ; "
          f"version courante : {sys.version.split()[0]}.", file=sys.stderr)
    raise SystemExit(2)

INVENTAIRE_REL = "_templates/inventory.md"
CONFIG_DEFAUT = Path(__file__).resolve().parent / "build-inventory.toml"

ENTETE = "| Date | Canal | Type | Sujet | Chemin | Statut |"
SEPARATEUR = "|---|---|---|---|---|---|"
LIGNE_MAJ_RE = re.compile(r"^> Dernière mise à jour : .*$", re.MULTILINE)

DATE_RE = re.compile(r"(20\d{2}-\d{2}-\d{2})")
H1_MD_RE = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_HTML_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
BALISE_RE = re.compile(r"<[^>]+>")
# Les gabarits de decks portent un long commentaire d'en-tête qui cite
# « <title> » dans son mode d'emploi : il fausserait l'extraction du sujet.
COMMENTAIRE_RE = re.compile(r"<!--.*?-->", re.DOTALL)

CELLULE_RE = re.compile(r"(?<!\\)\|")

SUJET_MAX = 90
SUJET_MOTS = 8


@dataclass(frozen=True)
class Source:
    """Un dossier de production : où chercher, et quoi en déduire."""

    dossier: str
    motifs: tuple[str, ...]
    canal: str
    type: str


# Les sources (un canal et un type par dossier) et les fichiers de service à
# ignorer viennent de scripts/build-inventory.toml. Le vocabulaire des canaux et
# des types est celui de la note d'usage de _templates/inventory.md.
SOURCES: tuple[Source, ...] = ()

# Un frontmatter `statut` prime sur la déduction par les métriques.
STATUTS_FRONTMATTER = {
    "publié": "publié",
    "publie": "publié",
    "rejeté": "archivé",
    "rejete": "archivé",
    "abandonné": "archivé",
    "abandonne": "archivé",
    "brouillon": "brouillon",
    "validé": "validé",
    "valide": "validé",
    "archivé": "archivé",
    "archive": "archivé",
}

# Un de ces champs renseigné signe un livrable réellement diffusé.
CHAMPS_DIFFUSION = ("sent", "url", "likes")

# Fichiers de service présents dans les dossiers de production : doctrine,
# mode d'emploi ou index, jamais un livrable. Complété par la configuration.
EXCLUS: set[str] = {"readme.md", "claude.md", ".gitkeep"}


class InventaireError(Exception):
    """Chemin hors périmètre, fichier illisible, inventaire ou configuration malformés."""


def charger_config(chemin: Path) -> None:
    """Lit les sources et les exclusions de scripts/build-inventory.toml.

    Renseigne les globales SOURCES, EXCLUS et INVENTAIRE_REL, que le reste du
    module lit. Une source s'écrit :

        [[sources]]
        dossier = "03-social-media/linkedin/examples"
        motifs = ["*.md"]
        canal = "linkedin"
        type = "post"
    """
    global SOURCES, EXCLUS, INVENTAIRE_REL
    if not chemin.exists():
        raise InventaireError(f"configuration introuvable : {chemin}")
    try:
        config = tomllib.loads(chemin.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as err:
        raise InventaireError(f"{chemin} n'est pas un TOML valide : {err}") from err

    sources = []
    for index, brut in enumerate(config.get("sources", [])):
        manquantes = [cle for cle in ("dossier", "motifs", "canal", "type") if not brut.get(cle)]
        if manquantes:
            raise InventaireError(
                f"{chemin} : la source {index} n'a pas {', '.join(manquantes)}"
            )
        sources.append(Source(
            dossier=str(brut["dossier"]).rstrip("/"),
            motifs=tuple(brut["motifs"]),
            canal=str(brut["canal"]),
            type=str(brut["type"]),
        ))
    if not sources:
        raise InventaireError(f"{chemin} : aucune source déclarée ([[sources]])")
    SOURCES = tuple(sources)
    EXCLUS = {"readme.md", "claude.md", ".gitkeep"} | {
        nom.lower() for nom in config.get("exclude_names", [])
    }
    INVENTAIRE_REL = config.get("inventory", INVENTAIRE_REL)


@dataclass(frozen=True)
class Livrable:
    date: str
    canal: str
    type: str
    sujet: str
    chemin: str
    statut: str


# --------------------------------------------------------------------------
# Lecture des fichiers source
# --------------------------------------------------------------------------

def lire_frontmatter(texte: str) -> dict[str, str]:
    """Lit un frontmatter YAML plat en `clé: valeur` (sans dépendance externe).

    Seules les paires de premier niveau sont retenues. Une valeur garde ses
    deux-points internes (`subject: "Hi: there"`). Une liste, en crochets ou en
    tirets, est conservée telle quelle du côté valeur et ses éléments indentés
    sont ignorés : le script ne consomme que des champs simples.

    Un frontmatter dont le `---` de fermeture manque est toléré : les champs
    déjà lus sont rendus plutôt que jetés, pour qu'un fichier mal fermé garde
    sa date et son sujet. Le dictionnaire rendu porte toutes les paires lues,
    mais le script n'en exploite que six : `date`, `subject`, `statut`, et les
    trois champs de diffusion `sent`, `url` et `likes`. Sur un fichier mal
    fermé, une ligne du corps qui ressemble à une paire est donc sans effet,
    sauf si elle porte justement l'un de ces six noms.
    """
    if not texte.startswith("---"):
        return {}
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != "---":
        return {}
    champs: dict[str, str] = {}
    for ligne in lignes[1:]:
        if ligne.strip() == "---":
            break
        if not ligne.strip() or ligne.startswith((" ", "\t", "-", "#")):
            continue
        cle, separateur, valeur = ligne.partition(":")
        if not separateur or not cle.strip():
            continue
        champs[cle.strip()] = valeur.strip().strip("\"'").strip()
    return champs


def nettoyer(texte: str) -> str:
    """Ramène un titre brut (markdown ou HTML) à une ligne de texte simple."""
    texte = BALISE_RE.sub(" ", texte)
    texte = html.unescape(texte)
    texte = re.sub(r"^#+\s*", "", texte.strip())
    texte = texte.replace("*", "").replace("`", "")
    # Les tirets longs des titres d'origine deviennent des points médians : le
    # séparateur reste lisible, et l'inventaire passe le linter de marque.
    texte = texte.replace("—", "·").replace("–", "·")
    texte = re.sub(r"\s+", " ", texte).strip()
    if len(texte) > SUJET_MAX:
        texte = texte[:SUJET_MAX].rstrip() + "…"
    return texte


def premiers_mots(corps: str) -> str:
    """Les premiers mots du corps, quand aucun titre ne se dégage."""
    for ligne in corps.splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith(("---", "<", "!", "|", ">")):
            continue
        mots = nettoyer(ligne).split()
        if mots:
            return " ".join(mots[:SUJET_MOTS])
    return ""


def corps_markdown(texte: str) -> str:
    """Le contenu d'un fichier markdown, frontmatter retiré."""
    if not texte.startswith("---"):
        return texte
    fin = texte.find("\n---", 3)
    return texte[fin + 4:] if fin != -1 else texte


def slug_dossier(nom: str) -> str:
    """« carrousel-lancement-offre-2026-07-08 » devient « lancement offre »."""
    nom = DATE_RE.sub("", nom)
    nom = re.sub(r"^(carrousel|carousel|presentation|deck)[-_]", "", nom)
    return re.sub(r"[-_]+", " ", nom).strip()


def trouver_date(champs: dict[str, str], chemin: Path) -> str | None:
    """Date du frontmatter, sinon du nom de fichier, sinon du dossier parent."""
    valeur = champs.get("date", "")
    trouvee = DATE_RE.search(valeur)
    if trouvee:
        return trouvee.group(1)
    for nom in (chemin.name, chemin.parent.name):
        trouvee = DATE_RE.search(nom)
        if trouvee:
            return trouvee.group(1)
    return None


def trouver_statut(champs: dict[str, str]) -> str:
    """Statut déclaré s'il existe, sinon déduit des champs de diffusion.

    Un `statut` du frontmatter prime toujours. À défaut, un champ `sent`,
    `url` ou `likes` renseigné signe un `publié`, et le reste est `validé`.
    """
    declare = champs.get("statut", "").strip().lower()
    if declare in STATUTS_FRONTMATTER:
        return STATUTS_FRONTMATTER[declare]
    for champ in CHAMPS_DIFFUSION:
        valeur = champs.get(champ, "").strip()
        if valeur and valeur not in {"0", "-", "null", "none"}:
            return "publié"
    return "validé"


def trouver_sujet(texte: str, champs: dict[str, str], chemin: Path) -> str:
    """Sujet du livrable : `subject`, puis titre, puis premiers mots, puis slug."""
    sujet = nettoyer(champs.get("subject", ""))
    if sujet:
        return sujet
    if chemin.suffix == ".html":
        sans_commentaire = COMMENTAIRE_RE.sub(" ", texte)
        for motif in (TITLE_RE, H1_HTML_RE):
            trouve = motif.search(sans_commentaire)
            sujet = nettoyer(trouve.group(1)) if trouve else ""
            if sujet:
                return sujet
    else:
        corps = corps_markdown(texte)
        trouve = H1_MD_RE.search(corps)
        if trouve:
            return nettoyer(trouve.group(1))
        sujet = premiers_mots(corps)
        if sujet:
            return sujet
    nom = chemin.parent.name if chemin.name == "index.html" else chemin.stem
    return slug_dossier(nom) or chemin.stem


def source_de(rel: Path) -> Source | None:
    """La source qui régit ce chemin relatif, ou None s'il est hors périmètre."""
    if rel.name.lower() in EXCLUS:
        return None
    # Un gabarit n'est jamais un livrable, même s'il porte le nom d'un livrable.
    if "templates" in rel.parts:
        return None
    for source in SOURCES:
        dossier = Path(source.dossier)
        try:
            reste = rel.relative_to(dossier)
        except ValueError:
            continue
        for motif in source.motifs:
            if reste.match(motif) and len(reste.parts) == len(Path(motif).parts):
                return source
    return None


def extraire(root: Path, rel: Path) -> Livrable | None:
    """Construit la ligne d'inventaire d'un fichier, ou None s'il est inexploitable."""
    source = source_de(rel)
    if source is None:
        return None
    chemin = root / rel
    if not chemin.is_file():
        return None
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    champs = lire_frontmatter(texte) if chemin.suffix == ".md" else {}
    date = trouver_date(champs, rel)
    if date is None:
        return None
    return Livrable(
        date=date,
        canal=source.canal,
        type=source.type,
        sujet=trouver_sujet(texte, champs, rel),
        chemin=rel.as_posix(),
        statut=trouver_statut(champs),
    )


def collecter(root: Path) -> list[Livrable]:
    """Parcourt tous les dossiers de production et rend les livrables triés."""
    livrables: list[Livrable] = []
    for source in SOURCES:
        base = root / source.dossier
        if not base.is_dir():
            continue
        for motif in source.motifs:
            for chemin in base.glob(motif):
                if not chemin.is_file():
                    continue
                livrable = extraire(root, chemin.relative_to(root))
                if livrable is not None:
                    livrables.append(livrable)
    return trier(livrables)


def sans_date(root: Path) -> list[str]:
    """Les fichiers du périmètre qu'aucune date ne permet d'indexer."""
    orphelins: list[str] = []
    for source in SOURCES:
        base = root / source.dossier
        if not base.is_dir():
            continue
        for motif in source.motifs:
            for chemin in sorted(base.glob(motif)):
                rel = chemin.relative_to(root)
                if not chemin.is_file() or source_de(rel) is None:
                    continue
                texte = chemin.read_text(encoding="utf-8", errors="replace")
                champs = lire_frontmatter(texte) if chemin.suffix == ".md" else {}
                if trouver_date(champs, rel) is None:
                    orphelins.append(rel.as_posix())
    return orphelins


def trier(livrables: list[Livrable]) -> list[Livrable]:
    """Du plus récent au plus ancien, chemin croissant à date égale."""
    par_chemin = sorted(livrables, key=lambda l: l.chemin)
    return sorted(par_chemin, key=lambda l: l.date, reverse=True)


# --------------------------------------------------------------------------
# Lecture et écriture du tableau
# --------------------------------------------------------------------------

def echapper(valeur: str) -> str:
    return valeur.replace("|", r"\|")


def desechapper(valeur: str) -> str:
    return valeur.replace(r"\|", "|")


def rendre_tableau(livrables: list[Livrable]) -> str:
    lignes = [ENTETE, SEPARATEUR]
    for l in livrables:
        cellules = [l.date, l.canal, l.type, echapper(l.sujet), l.chemin, l.statut]
        lignes.append("| " + " | ".join(cellules) + " |")
    return "\n".join(lignes)


def decouper_tableau(texte: str) -> tuple[int, int]:
    """Bornes (début, fin exclue) du bloc de tableau dans le fichier."""
    lignes = texte.splitlines()
    for index, ligne in enumerate(lignes):
        if ligne.strip().startswith("| Date "):
            fin = index + 1
            while fin < len(lignes) and lignes[fin].lstrip().startswith("|"):
                fin += 1
            return index, fin
    raise InventaireError(
        f"{INVENTAIRE_REL} : en-tête de tableau introuvable (ligne « {ENTETE} »)"
    )


def decouper_ligne(ligne: str) -> list[str]:
    """Cellules d'une ligne de tableau, en respectant les barres échappées."""
    cellules = CELLULE_RE.split(ligne.strip())
    return [c.strip() for c in cellules[1:-1]]


def lire_tableau(texte: str) -> list[Livrable]:
    debut, fin = decouper_tableau(texte)
    livrables: list[Livrable] = []
    for ligne in texte.splitlines()[debut:fin]:
        if ligne.startswith("| Date ") or set(ligne.strip()) <= set("|- "):
            continue
        cellules = decouper_ligne(ligne)
        if len(cellules) != 6:
            raise InventaireError(f"{INVENTAIRE_REL} : ligne à {len(cellules)} colonnes : {ligne}")
        livrables.append(
            Livrable(
                date=cellules[0],
                canal=cellules[1],
                type=cellules[2],
                sujet=desechapper(cellules[3]),
                chemin=cellules[4],
                statut=cellules[5],
            )
        )
    return livrables


def composer(texte: str, livrables: list[Livrable], mode: str, jour: str) -> str:
    """Réinjecte le tableau et la ligne de fraîcheur dans le fichier."""
    debut, fin = decouper_tableau(texte)
    lignes = texte.splitlines()
    nouveau = lignes[:debut] + rendre_tableau(livrables).splitlines() + lignes[fin:]
    sortie = "\n".join(nouveau)
    if texte.endswith("\n"):
        sortie += "\n"
    return LIGNE_MAJ_RE.sub(f"> Dernière mise à jour : {jour} (mode : {mode})", sortie, count=1)


def ecrire(cible: Path, contenu: str) -> bool:
    """Écrit le fichier et dit s'il a changé."""
    if cible.exists() and cible.read_text(encoding="utf-8") == contenu:
        return False
    cible.write_text(contenu, encoding="utf-8")
    return True


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def reconstruire(root: Path, jour: str) -> tuple[list[Livrable], str]:
    cible = root / INVENTAIRE_REL
    if not cible.exists():
        raise InventaireError(f"{INVENTAIRE_REL} introuvable sous {root}")
    livrables = collecter(root)
    return livrables, composer(cible.read_text(encoding="utf-8"), livrables, "reconstruction", jour)


def ajouter(root: Path, rel: Path, jour: str) -> tuple[Livrable, str]:
    cible = root / INVENTAIRE_REL
    if not cible.exists():
        raise InventaireError(f"{INVENTAIRE_REL} introuvable : lancer d'abord une reconstruction")
    if source_de(rel) is None:
        raise InventaireError(
            f"{rel} est hors périmètre de l'inventaire (dossiers couverts : "
            + ", ".join(source.dossier for source in SOURCES)
            + ")"
        )
    if not (root / rel).is_file():
        raise InventaireError(f"{rel} introuvable sous {root}")
    livrable = extraire(root, rel)
    if livrable is None:
        raise InventaireError(
            f"{rel} : aucune date exploitable (champ `date` du frontmatter ou "
            "motif AAAA-MM-JJ dans le nom du fichier ou du dossier)"
        )
    texte = cible.read_text(encoding="utf-8")
    livrables = [l for l in lire_tableau(texte) if l.chemin != livrable.chemin]
    livrables.append(livrable)
    return livrable, composer(texte, trier(livrables), "incrément", jour)


def verifier(root: Path) -> tuple[bool, list[Livrable]]:
    """Compare le tableau versionné au tableau attendu, sans rien écrire.

    Seules les lignes comptent : la ligne « Dernière mise à jour » porte la date
    du dernier passage et ne doit pas faire échouer la vérification.
    """
    cible = root / INVENTAIRE_REL
    if not cible.exists():
        raise InventaireError(f"{INVENTAIRE_REL} introuvable sous {root}")
    attendus = collecter(root)
    actuels = lire_tableau(cible.read_text(encoding="utf-8"))
    return actuels == attendus, attendus


def diagnostic(attendus: list[Livrable], actuels: list[Livrable]) -> list[str]:
    """Les écarts, en clair, entre le tableau versionné et l'état des dossiers."""
    par_chemin_attendus = {l.chemin: l for l in attendus}
    par_chemin_actuels = {l.chemin: l for l in actuels}
    ecarts = []
    for chemin in sorted(set(par_chemin_attendus) - set(par_chemin_actuels)):
        ecarts.append(f"  manquant : {chemin}")
    for chemin in sorted(set(par_chemin_actuels) - set(par_chemin_attendus)):
        ecarts.append(f"  en trop  : {chemin}")
    for chemin in sorted(set(par_chemin_attendus) & set(par_chemin_actuels)):
        if par_chemin_attendus[chemin] != par_chemin_actuels[chemin]:
            ecarts.append(f"  modifié  : {chemin}")
    return ecarts


def signaler_orphelins(root: Path, flux) -> list[str]:
    """Annonce les fichiers du périmètre qu'aucune date ne permet d'indexer.

    Le mode `--check` l'écrit sur la sortie d'erreur sans changer son code de
    sortie : un inventaire conforme peut rester aveugle à un livrable réel, et
    c'est cette commande que la vérification anti-répétition prescrit.
    """
    orphelins = sans_date(root)
    if orphelins:
        print(
            f"avertissement : {len(orphelins)} fichiers non indexés, faute de date exploitable "
            "(renommer en AAAA-MM-JJ-… ou ajouter un champ `date`) :",
            file=flux,
        )
        for chemin in orphelins:
            print(f"  {chemin}", file=flux)
    return orphelins


def repartition(livrables: list[Livrable]) -> str:
    compte: dict[str, int] = {}
    for l in livrables:
        compte[l.canal] = compte.get(l.canal, 0) + 1
    return ", ".join(f"{canal} {n}" for canal, n in sorted(compte.items()))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Construit l'inventaire des livrables dans _templates/inventory.md.",
    )
    parser.add_argument("--check", action="store_true",
                        help="compare sans écrire ; sort 1 si le tableau a dérivé")
    parser.add_argument("--add", metavar="CHEMIN",
                        help="ajoute ou met à jour la ligne d'un seul livrable")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                        help="racine du repo (par défaut : le repo courant)")
    parser.add_argument("--config", default=str(CONFIG_DEFAUT),
                        help="sources inventoriées, en TOML (défaut : scripts/build-inventory.toml)")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    jour = Date.today().isoformat()

    try:
        charger_config(Path(args.config))
        cible = root / INVENTAIRE_REL
        if args.check and args.add:
            parser.error("--check et --add ne se combinent pas")

        if args.check:
            conforme, attendus = verifier(root)
            signaler_orphelins(root, sys.stderr)
            if conforme:
                print(f"inventaire à jour : {len(attendus)} livrables ({repartition(attendus)})")
                return 0
            actuels = lire_tableau(cible.read_text(encoding="utf-8"))
            print("inventaire périmé, relancer python3 scripts/build-inventory.py")
            for ecart in diagnostic(attendus, actuels):
                print(ecart)
            return 1

        if args.add:
            rel = Path(args.add)
            if rel.is_absolute():
                try:
                    rel = rel.resolve().relative_to(root)
                except ValueError:
                    raise InventaireError(f"{args.add} est hors de la racine {root}") from None
            livrable, contenu = ajouter(root, rel, jour)
            change = ecrire(cible, contenu)
            etat = "ligne écrite" if change else "ligne déjà à jour"
            print(f"{etat} : {livrable.date} · {livrable.canal} · {livrable.sujet}")
            return 0

        livrables, contenu = reconstruire(root, jour)
        ecrire(cible, contenu)
        print(f"{len(livrables)} livrables indexés ({repartition(livrables)})")
        signaler_orphelins(root, sys.stdout)
        return 0
    except InventaireError as erreur:
        print(f"erreur : {erreur}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
