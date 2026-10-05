#!/usr/bin/env python3
"""Promeut un asset VALIDÉ dans la bibliothèque canonique + l'inscrit au catalogue.

À lancer dès qu'un visuel généré (sorties de staging dans
06-graphic-design/outputs/) est validé par un humain. Il :
  1. range le fichier dans 01-brand/assets/<categorie>/<sous-dossier>/ avec un
     nom CONFORME (`[categorie]_[sujet]_[variante]_[taille].[ext]`),
  2. insère une FICHE dans 01-brand/assets/index.md sous la bonne catégorie
     (section `## <categorie>/`, sinon en fin de catalogue).

Trois champs de droits sont OBLIGATOIRES : `--source`, `--droits`, `--auteur`.
Sans eux le script refuse, en listant ce qui manque : une fiche sans provenance
ni base légale n'a aucune valeur dans le registre des droits de la marque. Quand
le statut est réellement inconnu, l'écrire explicitement (`--droits "à confirmer"`).

Quand une fiche de génération `<source>.gen.json` accompagne le fichier (déposée
via `genmeta.finalize_output()` par le script de génération), le script la lit :
`--ia` vaut « oui » d'office, la source est déduite si elle n'est pas fournie, le
modèle et un extrait du prompt entrent dans la fiche du catalogue, et la fiche de
génération suit l'asset dans la bibliothèque. L'asset promu n'est jamais
réécrit : le marquage se fait sur la source de staging avant le transfert, la
copie est octet à octet, ce qui préserve le manifeste C2PA des sorties du modèle.

Usage :
  promote-asset.py <source> --dest <chemin/relatif/sous/assets/nom_conforme.ext> \
      --source "..." --droits "..." --auteur "..." \
      --role "..." [--palette "..."] [--style "..."] [--usage "..."] \
      [--not "..."] [--variants "..."] [--ia oui|non] [--copy]

Ex :
  promote-asset.py 06-graphic-design/outputs/2026-01-15-scene-atelier.png \
      --dest illustrations/scenes/illustrations_scene_atelier.png \
      --role "scène d'atelier au style de la marque" --usage "hero de post, cover de carrousel" \
      --droits "création interne, usage libre" --auteur "équipe marketing (modèle génératif)"
"""
import argparse, pathlib, re, shutil, sys, datetime

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import genmeta  # provenance : fiche de génération, C2PA, tag PNG

ASSETS_REL = pathlib.Path("01-brand") / "assets"
CATEGORIES = {"logos", "icons", "illustrations", "patterns", "photos", "banners", "archive",
              "docs", "sources"}  # les mêmes que le frontmatter « categories » de index.md
CONV = re.compile(r"^[a-z0-9]+(_[a-z0-9-]+)+\.[a-z0-9]+$")  # [cat]_[sujet]...
CHAMPS_DE_DROITS = ("source", "droits", "auteur")
VIDE = "aucune"  # jamais de tiret long dans une fiche : le linter de marque le refuse


def dims_transp(p):
    p = pathlib.Path(p)
    if p.suffix.lower() == ".svg":
        t = p.read_text(errors="ignore")
        m = re.search(r'viewBox="[\d.\- ]*?([\d.]+) ([\d.]+)"', t)
        return (f"{float(m.group(1)):.0f}x{float(m.group(2)):.0f}" if m else "vectoriel"), "oui (vectoriel)"
    try:
        from PIL import Image
        im = Image.open(p)
        alpha = im.mode in ("RGBA", "LA") and im.getchannel("A").getextrema()[0] < 255
        return f"{im.size[0]}x{im.size[1]}", ("oui" if alpha else "non")
    except Exception:
        return "?", "?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source_file", metavar="source", help="fichier à promouvoir")
    ap.add_argument("--root", default=str(pathlib.Path(__file__).resolve().parents[2]),
                    help="racine du dépôt (défaut : le dépôt courant)")
    ap.add_argument("--dest", required=True, help="chemin relatif sous 01-brand/assets/ (avec nom conforme)")
    ap.add_argument("--role", default="à confirmer")
    ap.add_argument("--palette", default="")
    ap.add_argument("--style", default="")
    ap.add_argument("--usage", default="à confirmer")
    ap.add_argument("--not", dest="not_use", default="")
    ap.add_argument("--variants", default="")
    ap.add_argument("--source", dest="provenance", default=None,
                    help="(obligatoire) origine du fichier : photo fournie, banque, fournisseur, généré, site… "
                         "Déduite de la fiche de génération quand il y en a une à côté de la source")
    ap.add_argument("--droits", default=None,
                    help="(obligatoire) licence ou base légale : OFL 1.1, autorisation client du JJ/MM/AAAA, "
                         "consentement de la personne photographiée, à confirmer…")
    ap.add_argument("--auteur", default=None,
                    help="(obligatoire) qui l'a produit : photographe, agence, équipe interne, modèle génératif")
    ap.add_argument("--ia", choices=("oui", "non"), default=None,
                    help="asset généré par IA (champ « généré-par-ia », cf. la politique de divulgation IA "
                         "de la marque). Défaut : « oui » si une fiche de génération accompagne la source, "
                         "sinon « non »")
    ap.add_argument("--copy", action="store_true", help="copier au lieu de déplacer")
    a = ap.parse_args()

    src = pathlib.Path(a.source_file)
    # Fiche de génération déposée à la génération : elle renseigne d'office
    # l'origine IA, le modèle et le prompt, et suivra l'asset dans la bibliothèque.
    gen = genmeta.read_sidecar(src)
    modele = (gen or {}).get("model") or ""
    # `gen is not None` et non `if gen` : une fiche vide reste une fiche, donc
    # l'asset vient bien d'une génération.
    a_une_fiche = gen is not None
    if a.ia is None:
        a.ia = "oui" if a_une_fiche else "non"
    if a_une_fiche and not a.provenance:
        a.provenance = (f"généré par {modele or 'un modèle génératif'} "
                        f"(fiche de génération {src.name}{genmeta.SIDECAR_SUFFIX})")

    manquants = [f"--{nom}" for nom, valeur in
                 zip(CHAMPS_DE_DROITS, (a.provenance, a.droits, a.auteur)) if not valeur]
    if manquants:
        raise SystemExit(
            "ERREUR : champs de droits obligatoires manquants : " + ", ".join(manquants) + ".\n"
            "         Chaque fiche doit dire d'où vient le fichier, sous quelle licence ou base "
            "légale il est utilisable, et qui l'a produit.\n"
            "         Si le statut est inconnu, l'écrire : --droits \"à confirmer\" "
            "(et l'inscrire au registre des droits de la marque).")

    root = pathlib.Path(a.root).resolve()
    assets = root / ASSETS_REL
    index = assets / "index.md"

    if not src.exists():
        raise SystemExit(f"ERREUR : source introuvable : {src}")
    dest = assets / a.dest
    topcat = a.dest.split("/")[0]
    if topcat not in CATEGORIES:
        raise SystemExit(f"ERREUR : catégorie '{topcat}' inconnue {sorted(CATEGORIES)}")
    if not CONV.match(dest.name):
        raise SystemExit(f"ERREUR : nom non conforme '{dest.name}'. "
                         f"Attendu : [categorie]_[sujet]_[variante]_[taille].[ext], minuscules, _, sans accent.")
    if dest.exists():
        raise SystemExit(f"ERREUR : destination déjà existante (pas d'écrasement) : {dest}")
    if not index.exists():
        raise SystemExit(f"ERREUR : catalogue introuvable : {index}. Créer 01-brand/assets/index.md "
                         f"(une section « ## <categorie>/ » par catégorie) avant la première promotion.")

    reel = genmeta.detect_format(src)
    if reel and dest.suffix.lower() not in genmeta.EXTENSIONS[reel]:
        print(f"⚠ ATTENTION : les octets disent {reel}, la destination dit '{dest.suffix}'. "
              f"Renommer la source avant de promouvoir (ne jamais convertir : "
              f"un réencodage efface le manifeste C2PA).")

    # Le marquage se fait AVANT le transfert : un asset déjà rangé dans la
    # bibliothèque ne se réécrit jamais, sa copie est octet à octet (c'est ce qui
    # préserve le manifeste C2PA des sorties JPEG du modèle).
    if a.ia == "oui" and reel == "png" and modele and not genmeta.has_c2pa(src):
        genmeta.tag_png(src, genmeta.TAG_KEY, modele)

    dest.parent.mkdir(parents=True, exist_ok=True)
    transfere = shutil.copy2 if a.copy else shutil.move
    transfere(str(src), str(dest))
    if a_une_fiche:
        transfere(str(genmeta.sidecar_path(src)), str(genmeta.sidecar_path(dest)))
        # La fiche qui suit l'asset doit décrire l'asset, pas le fichier de
        # staging : le tag a pu changer les octets, et un écart signale une
        # retouche entre la génération et la promotion.
        empreinte = genmeta.sha256_file(dest)
        if gen.get("sha256") and gen["sha256"] != empreinte:
            print(f"⚠ ATTENTION : le sha256 de la fiche de génération ne vaut plus celui "
                  f"de l'asset promu (le fichier a été retouché, ou marqué à l'instant). "
                  f"La fiche recopiée porte l'empreinte du fichier rangé.")
        gen["sha256"] = empreinte
        genmeta.write_sidecar(dest, gen)
    dim, transp = dims_transp(dest)

    asset_id = dest.stem
    provenance_ia = ""
    if a_une_fiche:
        extrait = genmeta.prompt_excerpt(gen.get("prompt"))
        provenance_ia = (f"- modèle: {modele or 'à confirmer'}\n"
                         f"- prompt: {extrait or 'à confirmer'}\n")
    fiche = (f"\n### {asset_id}\n"
             f"- chemin: `{a.dest}`\n"
             f"- role: {a.role}\n"
             f"- dimensions: {dim}\n"
             f"- palette: {a.palette or VIDE}\n"
             f"- style: {a.style or VIDE}\n"
             f"- transparence: {transp}\n"
             f"- utiliser: {a.usage}\n"
             f"- ne PAS utiliser: {a.not_use or 'à confirmer'}\n"
             f"- variantes: {a.variants or VIDE}\n"
             f"- source: {a.provenance}\n"
             f"- droits: {a.droits}\n"
             f"- auteur: {a.auteur}\n"
             f"- généré-par-ia: {a.ia}\n"
             f"{provenance_ia}"
             f"- ajouté: {datetime.date.today().isoformat()} (validé)\n")

    # Insertion sous la section « ## <topcat>/ » du catalogue (sinon en fin).
    txt = index.read_text(encoding="utf-8")
    head = re.search(rf"(?m)^## {re.escape(topcat)}/.*$", txt)
    if not head:  # titre de section groupé, par exemple « ## docs/ · sources/ »
        head = re.search(rf"(?m)^## [^\n]*[^\w-]{re.escape(topcat)}/.*$", txt)
    if head:
        nxt = re.search(r"(?m)^## ", txt[head.end():])
        pos = head.end() + (nxt.start() if nxt else len(txt) - head.end())
        txt = txt[:pos] + fiche + txt[pos:]
    else:
        txt += fiche
    index.write_text(txt, encoding="utf-8")

    print(f"✓ {'copié' if a.copy else 'rangé'} : {src.name}  →  01-brand/assets/{a.dest}")
    print(f"✓ fiche ajoutée à index.md (section {topcat}/)  | dims {dim}, transp {transp}")
    print(f"✓ droits : source « {a.provenance} » | {a.droits} | auteur « {a.auteur} » | IA : {a.ia}")
    if a_une_fiche:
        print(f"✓ provenance : {modele or 'modèle inconnu'} | fiche de génération "
              f"reportée en {a.dest}{genmeta.SIDECAR_SUFFIX}")
    print("→ Relire la fiche (role/usage/'ne pas utiliser') et compléter si « à confirmer ».")
    print("→ Si les droits sont « à confirmer », l'inscrire au registre des droits de la marque.")


if __name__ == "__main__":
    main()
