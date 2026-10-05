#!/usr/bin/env python3
"""
Vendorise le moteur de slides depuis slides-agent, sa source de vérité.

slides-agent (https://github.com/Littlpinguin/slides-agent) porte le moteur de
présentations HTML : le starter, les composants, le catalogue de layouts, la QA
Playwright, l'export PDF et leurs tests. Ce template en garde une copie
vendorisée, et ce script est le seul chemin d'écriture de cette copie : un
fichier vendorisé ne s'édite jamais à la main. On change slides-agent, puis on
relance ce script.

Le script applique une table de correspondance explicite (COPIES), et seulement
des adaptations mécaniques, toutes documentées dans docs/vendored-slides.md :

  - REECRITURES : chemins de slides-agent réécrits en chemins du template
    (`scripts/qa.py` → `06-graphic-design/presentations/scripts/qa.py`,
    `presentations/` → `06-graphic-design/presentations/decks/`...), en une
    seule passe, pour qu'un chemin réécrit ne soit jamais réécrit deux fois ;
  - ADAPTATIONS : substitutions littérales propres à un fichier (profondeur des
    scripts dans l'arborescence, dossier des photos...). Chacune doit trouver
    son texte d'origine le nombre de fois attendu : si l'amont a changé, le
    script s'arrête au lieu de copier un fichier mal adapté ;
  - un en-tête « VENDORED » en tête de chaque fichier texte.

Les photos du catalogue et leurs fiches de crédit sont copiées octet pour octet.
Le commit source est consigné dans docs/vendored-slides.md, entre les marqueurs
`slides-engine-sync`.

Usage :
  python3 scripts/sync-slides-engine.py                  # vendorise
  python3 scripts/sync-slides-engine.py --check          # sort 1 si la copie a dérivé
  python3 scripts/sync-slides-engine.py --source CHEMIN  # checkout de slides-agent

Source par défaut : --source, sinon la variable d'environnement
SLIDES_AGENT_DIR, sinon un dossier `slides-agent` voisin du dépôt
(../slides-agent). Aucun accès réseau : cloner slides-agent d'abord.

Codes de sortie : 0 conforme ou écrit, 1 dérive (--check) ou adaptation qui ne
s'applique plus, 2 usage incorrect ou source introuvable.
Pur Python ≥ 3.10, bibliothèque standard seule (git est appelé s'il existe,
pour lire le commit source).
"""
from __future__ import annotations

import argparse
import fnmatch
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SOURCE_URL = "https://github.com/Littlpinguin/slides-agent"
ENV_SOURCE = "SLIDES_AGENT_DIR"
REGISTRE = "docs/vendored-slides.md"
MARQUEUR_DEBUT = "<!-- slides-engine-sync:start -->"
MARQUEUR_FIN = "<!-- slides-engine-sync:end -->"
BANDEAU_TETE = "VENDORED from slides-agent"
MOTEUR = "06-graphic-design/presentations"

# Fichiers qui prouvent qu'un dossier est bien un checkout de slides-agent.
SIGNATURE_SOURCE = ("templates/base.html", "scripts/qa.py")


# --------------------------------------------------------------------------
# Table de correspondance
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Copie:
    """Un fichier (ou un motif glob) de slides-agent et sa place dans le template."""
    source: str                 # chemin dans slides-agent ; un « * » en fait un motif
    cible: str                  # chemin dans le template ; un dossier (« / » final) pour un motif
    brut: bool = False          # copie octet pour octet : ni réécriture ni en-tête
    adaptations: tuple[str, ...] = ()
    note: str = ""              # phrase ajoutée à l'en-tête de ce fichier


NOTE_STARTER = ("A deck copied from this starter is yours: "
                "06-graphic-design/scripts/new-deck.py drops this note.")
NOTE_PARITE = ("Parity rule in this template: every engine change is made in slides-agent "
               "(the repository this page calls this repository), then synced here.")

COPIES: tuple[Copie, ...] = (
    Copie("templates/base.html", f"{MOTEUR}/templates/base.html", note=NOTE_STARTER),
    Copie("templates/components.md", f"{MOTEUR}/templates/components.md"),
    Copie("scripts/qa.py", f"{MOTEUR}/scripts/qa.py"),
    Copie("scripts/export_pdf.py", f"{MOTEUR}/scripts/export_pdf.py"),
    Copie("scripts/export-pdf.sh", f"{MOTEUR}/scripts/export-pdf.sh"),
    Copie("scripts/serve.sh", f"{MOTEUR}/scripts/serve.sh", adaptations=("serve-racine",)),
    Copie("scripts/shots.py", f"{MOTEUR}/scripts/shots.py"),
    Copie("scripts/pexels.py", f"{MOTEUR}/scripts/pexels.py",
          adaptations=("pexels-racine", "pexels-photos", "pexels-tokens")),
    Copie("docs/engine-parity.md", f"{MOTEUR}/docs/engine-parity.md", note=NOTE_PARITE),
    Copie("docs/pdf-export.md", f"{MOTEUR}/docs/pdf-export.md"),
    Copie("docs/design-system.md", f"{MOTEUR}/docs/design-system.md"),
    Copie("docs/pexels-setup.md", f"{MOTEUR}/docs/pexels-setup.md"),
    Copie("reference/catalogue-layouts.html", "_examples/deck-catalogue/catalogue.html"),
    Copie("reference/LAYOUTS.md", "_examples/deck-catalogue/LAYOUTS.md"),
    Copie("reference/photos/*.jpg", "_examples/deck-catalogue/photos/", brut=True),
    Copie("reference/photos/*.json", "_examples/deck-catalogue/photos/", brut=True),
    Copie("tests/test_qa.py", "scripts/tests/test_slides_qa.py", adaptations=("tests-racine",)),
    Copie("tests/test_print.py", "scripts/tests/test_slides_print.py", adaptations=("tests-racine",)),
    Copie("tests/test_engine.py", "scripts/tests/test_slides_engine.py", adaptations=("tests-racine",)),
    Copie("tests/test_pexels.py", "scripts/tests/test_slides_pexels.py",
          adaptations=("tests-racine-pathlib", "tests-pexels-deps")),
)

# Fichiers de slides-agent volontairement laissés hors du template. Toute autre
# nouveauté de l'amont est signalée à la synchronisation, pour être mappée ou
# écartée ici, en connaissance de cause (raisons dans docs/vendored-slides.md).
ECARTES: tuple[str, ...] = (
    "CLAUDE.md", "README.md", "CHANGELOG.md", "LICENSE", ".gitignore", ".env.example",
    ".claude/*", "brand/*", "assets/*", "presentations/*",
    "scripts/README.md", "scripts/gen-image.py", "docs/hosting.md",
)


# --------------------------------------------------------------------------
# Adaptations mécaniques
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Reecriture:
    """Un chemin de slides-agent et son équivalent dans le template (regex)."""
    id: str
    motif: str
    remplacement: str
    note: str


# L'ordre compte : à une même position, la première règle qui s'applique gagne.
# Les bornes gauches empêchent de réécrire un chemin déjà préfixé
# (`01-brand/tokens.json`, `../assets/photos/` relatif à un deck...).
REECRITURES: tuple[Reecriture, ...] = (
    Reecriture("catalogue", r"(?<![\w.-])reference/catalogue-layouts\.html",
               "_examples/deck-catalogue/catalogue.html",
               "le catalogue garde son chemin historique dans le template"),
    Reecriture("index-layouts", r"(?<![\w.-])reference/LAYOUTS\.md",
               "_examples/deck-catalogue/LAYOUTS.md", "l'index des layouts, à côté du catalogue"),
    Reecriture("photos-catalogue", r"(?<![\w.-])reference/photos/",
               "_examples/deck-catalogue/photos/", "les photos du catalogue, à côté de lui"),
    Reecriture("nom-catalogue", r"(?<![\w./-])catalogue-layouts\.html", "catalogue.html",
               "le nom de fichier seul, cité depuis le dossier du catalogue"),
    Reecriture("starter", r"(?<![\w.-])templates/(base\.html|components\.md|components/)",
               rf"{MOTEUR}/templates/\1", "le starter et les composants"),
    Reecriture("scripts",
               r"(?<![\w.-])scripts/(qa\.py|export_pdf\.py|export-pdf\.sh|serve\.sh|shots\.py|pexels\.py)",
               rf"{MOTEUR}/scripts/\1", "les scripts du moteur"),
    Reecriture("docs",
               r"(?<![\w.-])docs/(engine-parity|pdf-export|design-system|pexels-setup|hosting)\.md",
               rf"{MOTEUR}/docs/\1.md", "la documentation du moteur"),
    Reecriture("tests", r"(?<![\w.-])tests/test_(qa|print|engine|pexels)\.py",
               r"scripts/tests/test_slides_\1.py", "les tests, renommés test_slides_*"),
    Reecriture("pytest", r"\bpytest tests\b", "pytest scripts/tests",
               "la commande des tests, lancée depuis la racine"),
    Reecriture("tokens", r"(?<![\w.-])brand/tokens\.css", f"{MOTEUR}/tokens.css",
               "le fichier de marque du moteur (généré depuis 01-brand/tokens.json)"),
    Reecriture("decks", r"(?<![\w.-])presentations/", f"{MOTEUR}/decks/",
               "le dossier des decks (aussi dans les URL du serveur local)"),
    Reecriture("photos-decks", r"(?<![\w./-])assets/photos/", f"{MOTEUR}/assets/photos/",
               "les photos des decks ; `../assets/photos/` relatif à un deck reste tel quel"),
    Reecriture("skill-images", r"\bgenerate-image\b", "image-generation",
               "la skill de génération d'images porte un autre nom dans le template"),
)


@dataclass(frozen=True)
class Adaptation:
    """Substitution littérale propre à un fichier, ancrée sur le texte amont."""
    id: str
    avant: str
    apres: str
    note: str
    occurrences: int = 1


_PROFONDEUR = "06-graphic-design/presentations/scripts/ est trois niveaux sous la racine"

ADAPTATIONS: dict[str, Adaptation] = {a.id: a for a in (
    Adaptation("serve-racine",
               'ROOT="$(cd "$(dirname "$0")/.." && pwd)"',
               'ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"',
               f"le serveur local sert la racine du dépôt ({_PROFONDEUR}), pour qu'un deck "
               "atteigne 01-brand/assets/ en chemin relatif"),
    Adaptation("pexels-racine",
               "ROOT = pathlib.Path(__file__).resolve().parent.parent",
               "ROOT = pathlib.Path(__file__).resolve().parents[3]",
               f"`.env` et `.cache/` vivent à la racine du dépôt ({_PROFONDEUR})"),
    Adaptation("pexels-photos",
               'PHOTOS_DIR = ROOT / "assets" / "photos"',
               'PHOTOS_DIR = ROOT / "06-graphic-design" / "presentations" / "assets" / "photos"',
               "les photos téléchargées vont dans les assets des decks, que `../assets/photos/` "
               "atteint depuis decks/"),
    Adaptation("pexels-tokens",
               'TOKENS_PATH = ROOT / "brand" / "tokens.css"',
               'TOKENS_PATH = ROOT / "06-graphic-design" / "presentations" / "tokens.css"',
               "les couleurs des traitements se lisent dans le fichier de marque du moteur"),
    Adaptation("tests-racine",
               "ROOT = Path(__file__).resolve().parent.parent",
               'ROOT = Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"',
               "ROOT désigne le dossier du moteur, qui reproduit l'arborescence de slides-agent "
               "(templates/, scripts/)"),
    Adaptation("tests-racine-pathlib",
               "ROOT = pathlib.Path(__file__).resolve().parent.parent",
               'ROOT = pathlib.Path(__file__).resolve().parents[2] / "06-graphic-design" / "presentations"',
               "même chose, écrite avec pathlib"),
    Adaptation("tests-pexels-deps",
               "from PIL import Image\n",
               'pytest.importorskip("requests")\nImage = pytest.importorskip("PIL.Image")\n',
               "requests et Pillow restent optionnels dans le template : sans eux, les tests "
               "Pexels sont sautés au lieu de casser la collecte"),
)}


# --------------------------------------------------------------------------
# Transformation d'un fichier
# --------------------------------------------------------------------------

class SyncError(Exception):
    """La source ou la table ne permettent pas une copie fidèle."""


_GROUPES = re.compile("|".join(f"(?P<r{i}>{r.motif})" for i, r in enumerate(REECRITURES)))


def _remplacer(match: re.Match) -> str:
    for i, regle in enumerate(REECRITURES):
        if match.group(f"r{i}") is not None:
            return re.sub(regle.motif, regle.remplacement, match.group(0), count=1)
    return match.group(0)    # inatteignable : une des alternatives a forcément matché


def reecrire(texte: str) -> str:
    """Réécrit les chemins de slides-agent en une passe (aucun chemin réécrit deux fois)."""
    return _GROUPES.sub(_remplacer, texte)


def adapter(texte: str, ids: tuple[str, ...], source: str) -> str:
    for ident in ids:
        adaptation = ADAPTATIONS[ident]
        trouvees = texte.count(adaptation.avant)
        if trouvees != adaptation.occurrences:
            raise SyncError(
                f"adaptation « {ident} » : {source} contient {trouvees} fois le texte d'origine "
                f"au lieu de {adaptation.occurrences}. L'amont a changé : mettre à jour "
                f"ADAPTATIONS dans scripts/sync-slides-engine.py et {REGISTRE}."
            )
        texte = texte.replace(adaptation.avant, adaptation.apres)
    return texte


def lignes_bandeau(source: str, note: str = "") -> list[str]:
    lignes = [
        f"{BANDEAU_TETE} ({SOURCE_URL}), {source},",
        "by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,",
        "then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,",
        "onboarding and the pexels-photos skill refer to slides-agent.",
        f"Register: {REGISTRE}",
    ]
    return lignes + ([note] if note else [])


def poser_bandeau(texte: str, source: str, cible: str, note: str = "") -> str:
    lignes = lignes_bandeau(source, note)
    suffixe = Path(cible).suffix.lower()
    if suffixe in (".py", ".sh"):
        bloc = "".join(f"# {ligne}\n" for ligne in lignes)
        if texte.startswith("#!"):
            fin = texte.find("\n") + 1 or len(texte)
            return texte[:fin] + bloc + texte[fin:]
        return bloc + texte
    if suffixe in (".html", ".md"):
        corps = "\n".join(f"  {ligne}" for ligne in lignes)
        bloc = f"<!--\n{corps}\n-->\n"
        premiere = texte.split("\n", 1)[0]
        if suffixe == ".html" and premiere.strip().lower().startswith("<!doctype"):
            fin = len(premiere) + 1
            return texte[:fin] + bloc + texte[fin:]
        return bloc + texte
    raise SyncError(f"{cible} : pas de syntaxe de commentaire connue pour l'en-tête")


def transformer(copie: Copie, source_rel: str, contenu: str, cible: str) -> str:
    """Contenu vendorisé d'un fichier texte : adaptations, réécritures, en-tête."""
    texte = adapter(contenu, copie.adaptations, source_rel)
    texte = reecrire(texte)
    return poser_bandeau(texte, source_rel, cible, copie.note)


# --------------------------------------------------------------------------
# Plan de synchronisation
# --------------------------------------------------------------------------

@dataclass
class Attendu:
    source: Path
    cible: str
    contenu: bytes
    executable: bool
    brut: bool


def _fichiers_du_motif(source: Path, motif: str) -> list[str]:
    dossier, _, nom = motif.rpartition("/")
    base = source / dossier
    if not base.is_dir():
        return []
    return sorted(f"{dossier}/{p.name}" for p in base.iterdir()
                  if p.is_file() and fnmatch.fnmatch(p.name, nom))


def attendus(source: Path) -> tuple[list[Attendu], list[tuple[str, str]]]:
    """Ce que la source produirait : fichiers attendus, et motifs (dossier cible, glob)."""
    produits: list[Attendu] = []
    motifs: list[tuple[str, str]] = []
    for copie in COPIES:
        if "*" in copie.source:
            noms = _fichiers_du_motif(source, copie.source)
            if not noms:
                raise SyncError(f"aucun fichier amont pour le motif {copie.source}")
            motifs.append((copie.cible, copie.source.rpartition("/")[2]))
            paires = [(rel, copie.cible + rel.rpartition("/")[2]) for rel in noms]
        else:
            paires = [(copie.source, copie.cible)]
        for rel, cible in paires:
            chemin = source / rel
            if not chemin.is_file():
                raise SyncError(f"fichier amont absent : {rel} (table COPIES obsolète ?)")
            if copie.brut:
                contenu = chemin.read_bytes()
            else:
                texte = transformer(copie, rel, chemin.read_text(encoding="utf-8"), cible)
                contenu = texte.encode("utf-8")
            produits.append(Attendu(chemin, cible, contenu, os.access(chemin, os.X_OK), copie.brut))
    return produits, motifs


def perimes(racine: Path, produits: list[Attendu], motifs: list[tuple[str, str]]) -> list[str]:
    """Fichiers vendorisés par un motif que la source ne produit plus."""
    voulus = {a.cible for a in produits}
    restes: list[str] = []
    for dossier, glob in motifs:
        base = racine / dossier
        if base.is_dir():
            restes += [dossier + p.name for p in sorted(base.iterdir())
                       if p.is_file() and fnmatch.fnmatch(p.name, glob)
                       and dossier + p.name not in voulus]
    return restes


def _git(source: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(source), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def est_un_depot(source: Path) -> bool:
    """Vrai si `source` est la racine d'un dépôt git (pas un sous-dossier d'un autre)."""
    try:
        return Path(_git(source, "rev-parse", "--show-toplevel")).resolve() == source.resolve()
    except (OSError, subprocess.CalledProcessError):
        return False


def fichiers_amont(source: Path) -> list[str]:
    """Fichiers suivis de la source (git ls-files), sinon parcours du dossier."""
    if est_un_depot(source):
        return sorted(ligne for ligne in _git(source, "ls-files").splitlines() if ligne)
    fichiers: list[str] = []
    for dossier, sous, noms in os.walk(source):
        sous[:] = [s for s in sous if not s.startswith(".") and s != "__pycache__"]
        fichiers += [os.path.relpath(os.path.join(dossier, n), source) for n in noms
                     if not n.startswith(".") and not n.endswith(".pyc")]
    return sorted(f.replace(os.sep, "/") for f in fichiers)


def non_mappes(source: Path) -> list[str]:
    connus = [c.source for c in COPIES] + list(ECARTES)
    return [f for f in fichiers_amont(source)
            if not any(f == m or fnmatch.fnmatch(f, m) for m in connus)
            and not f.endswith("/.gitkeep")]


def commit_source(source: Path) -> tuple[str, str, bool]:
    """(commit, date ISO du commit, copie de travail modifiée) ; « inconnu » hors git."""
    if not est_un_depot(source):
        return "inconnu", "", False
    try:
        commit = _git(source, "rev-parse", "HEAD")
        date = _git(source, "log", "-1", "--format=%cs")
        chemins = sorted({c.source.rpartition("/")[0] if "*" in c.source else c.source
                          for c in COPIES})
        sale = bool(_git(source, "status", "--porcelain", "--", *chemins))
        return commit, date, sale
    except (OSError, subprocess.CalledProcessError):
        return "inconnu", "", False


# --------------------------------------------------------------------------
# Registre
# --------------------------------------------------------------------------

def bloc_registre(commit: str, date: str, sale: bool, produits: list[Attendu]) -> str:
    textes = sum(1 for a in produits if not a.brut)
    origine = f"`{commit}`" + (f" ({date})" if date else "")
    if sale:
        origine += ", **plus des modifications non commitées** : resynchroniser sur un commit"
    return (
        f"{MARQUEUR_DEBUT}\n"
        f"- Source : <{SOURCE_URL}>, commit {origine}\n"
        f"- Fichiers vendorisés : {len(produits)} ({textes} textes adaptés, "
        f"{len(produits) - textes} copies brutes)\n"
        f"{MARQUEUR_FIN}"
    )


REGISTRE_MINIMAL = (
    "# Moteur de slides vendorisé depuis slides-agent\n\n"
    "Registre écrit par scripts/sync-slides-engine.py.\n\n"
)


def registre_mis_a_jour(actuel: str | None, bloc: str) -> str:
    if actuel is None:
        return REGISTRE_MINIMAL + bloc + "\n"
    debut, fin = actuel.find(MARQUEUR_DEBUT), actuel.find(MARQUEUR_FIN)
    if debut == -1 or fin == -1 or fin < debut:
        raise SyncError(f"marqueurs {MARQUEUR_DEBUT} / {MARQUEUR_FIN} introuvables dans {REGISTRE}")
    return actuel[:debut] + bloc + actuel[fin + len(MARQUEUR_FIN):]


def commit_du_registre(texte: str | None) -> str | None:
    if not texte:
        return None
    trouve = re.search(re.escape(MARQUEUR_DEBUT) + r".*?commit `([^`]+)`", texte, re.S)
    return trouve.group(1) if trouve else None


# --------------------------------------------------------------------------
# Exécution
# --------------------------------------------------------------------------

def trouver_source(option: str | None, racine: Path) -> Path:
    if option:
        source, origine = Path(option), "--source"
    elif os.environ.get(ENV_SOURCE):
        source, origine = Path(os.environ[ENV_SOURCE]), ENV_SOURCE
    else:
        source, origine = racine.parent / "slides-agent", "dossier voisin ../slides-agent"
    source = source.expanduser().resolve()
    manquants = [rel for rel in SIGNATURE_SOURCE if not (source / rel).is_file()]
    if manquants:
        raise FileNotFoundError(
            f"checkout de slides-agent introuvable ({origine} : {source}). "
            f"Cloner {SOURCE_URL}, puis passer --source CHEMIN ou {ENV_SOURCE}."
        )
    return source


def synchroniser(racine: Path, source: Path, *, check: bool = False) -> int:
    produits, motifs = attendus(source)
    commit, date, sale = commit_source(source)
    a_supprimer = perimes(racine, produits, motifs)

    derives: list[str] = []
    for attendu in produits:
        chemin = racine / attendu.cible
        actuel = chemin.read_bytes() if chemin.exists() else None
        mode_ok = actuel is None or os.access(chemin, os.X_OK) == attendu.executable
        if actuel == attendu.contenu and mode_ok:
            continue
        derives.append(attendu.cible if actuel is not None
                       else f"{attendu.cible} ({'absent' if check else 'nouveau'})")
        if not check:
            chemin.parent.mkdir(parents=True, exist_ok=True)
            chemin.write_bytes(attendu.contenu)
            os.chmod(chemin, 0o755 if attendu.executable else 0o644)

    registre = racine / REGISTRE
    texte_registre = registre.read_text(encoding="utf-8") if registre.exists() else None
    if check:
        derives += [f"{rel} (n'existe plus dans slides-agent)" for rel in a_supprimer]
    else:
        for rel in a_supprimer:
            (racine / rel).unlink()
        nouveau = registre_mis_a_jour(texte_registre,
                                      bloc_registre(commit, date, sale, produits))
        if nouveau != texte_registre:
            registre.parent.mkdir(parents=True, exist_ok=True)
            registre.write_text(nouveau, encoding="utf-8")

    for rel in non_mappes(source):
        print(f"note : fichier amont ni vendorisé ni écarté : {rel} "
              "(le mapper dans COPIES ou l'écarter dans ECARTES)")
    if sale:
        print(f"attention : {source} a des modifications non commitées dans le périmètre "
              "vendorisé ; resynchroniser sur un commit avant de livrer.")

    if check:
        if derives:
            print(f"DÉRIVE : {len(derives)} fichier(s) ne correspondent plus à slides-agent "
                  f"({commit[:12]}) :")
            for rel in derives:
                print(f"  - {rel}")
            print("Ne pas les corriger à la main : python3 scripts/sync-slides-engine.py")
            return 1
        consigne = commit_du_registre(texte_registre)
        if consigne and consigne != commit:
            print(f"note : fichiers conformes, mais {REGISTRE} consigne le commit {consigne[:12]} "
                  f"et la source est en {commit[:12]} ; relancer sans --check pour l'actualiser.")
        print(f"OK : les {len(produits)} fichiers vendorisés correspondent à slides-agent "
              f"({commit[:12]}).")
        return 0

    for rel in derives:
        print(f"écrit : {rel}")
    for rel in a_supprimer:
        print(f"supprimé : {rel}")
    if not derives and not a_supprimer:
        print("Rien à faire : la copie vendorisée est déjà conforme.")
    print(f"Source : slides-agent {commit[:12]}{' (' + date + ')' if date else ''}, "
          f"{len(produits)} fichiers.")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Vendorise le moteur de slides depuis un checkout de slides-agent "
                    "(table et adaptations : docs/vendored-slides.md).")
    parser.add_argument("--check", action="store_true",
                        help="ne rien écrire ; sortir 1 si un fichier vendorisé a dérivé")
    parser.add_argument("--source", metavar="CHEMIN",
                        help=f"checkout de slides-agent (défaut : ${ENV_SOURCE}, "
                             "sinon ../slides-agent)")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
                        help="racine du template (défaut : le dossier parent de scripts/)")
    args = parser.parse_args(argv)

    racine = Path(args.root).resolve()
    try:
        source = trouver_source(args.source, racine)
    except FileNotFoundError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 2
    try:
        return synchroniser(racine, source, check=args.check)
    except SyncError as err:
        print(f"ERREUR : {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
