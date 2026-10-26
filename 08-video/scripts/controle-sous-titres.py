#!/usr/bin/env python3
"""Contrôle des sous-titres d'un projet vidéo : la forme ne dérive pas d'un film à l'autre.

Les sous-titres sont un élément récurrent : sans contrôle, leur forme dérive d'un film à l'autre
(lignes qui s'allongent, corps qui rétrécit). Les règles vivent dans 08-video/scripts/sous-titres.toml
(une section par toile) ; ce script les applique, et le hook du module
(.claude/hooks/controle-sous-titres.py) le lance à chaque écriture de sous-titres ou de composition.

Ce qui est contrôlé, sur chaque .srt de 08-video/projets/<slug>/sous-titres/ :
  - forme : lignes par segment, caractères par segment, durée, vitesse de lecture, chevauchements ;
  - coupes : aucun segment à cheval sur deux passages de montage/coupe.json (s'il existe) ;
  - fidélité : le texte suit la colonne Voix de script.md (mots retrouvés dans l'ordre).
Et dans les compositions HyperFrames du projet : le corps du texte des sous-titres (règles CSS dont
le sélecteur nomme st, sous-titre ou caption) ne descend pas sous la taille minimale de la toile.

Usage (depuis la racine du dépôt) :
    python3 08-video/scripts/controle-sous-titres.py 08-video/projets/<slug>   (ou un .srt, ou une composition)
Codes : 0 conforme (avertissements possibles), 1 au moins une erreur, 2 erreur d'usage.
"""
import argparse
import importlib.util
import json
import re
import sys
import tomllib
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1]  # 08-video/
REGLES = MODULE / "scripts" / "sous-titres.toml"

# fonctions de texte partagées avec la QA (mots normalisés, colonne Voix de script.md)
_spec = importlib.util.spec_from_file_location("qa_video", MODULE / "scripts" / "qa-video.py")
qa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(qa)

TC_RE = re.compile(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)")
SELECTEUR_RE = re.compile(r"(?:^|[\s.#,>\[\"'=-])(st|sous-?titres?|captions?|subtitles?)(?:$|[\s.,:>\]\"'-])", re.I)
REGLE_CSS_RE = re.compile(r"([^{}]+)\{\{?([^{}]*)\}?\}")
TAILLE_RE = re.compile(r"font-size\s*:\s*([\d.]+)px", re.I)


def secondes(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def lire_srt(chemin):
    segments = []
    for bloc in re.split(r"\n\s*\n", Path(chemin).read_text(encoding="utf-8").strip()):
        lignes = [l for l in bloc.splitlines() if l.strip()]
        for i, l in enumerate(lignes):
            m = TC_RE.search(l)
            if m:
                segments.append({"debut": secondes(*m.groups()[:4]), "fin": secondes(*m.groups()[4:]), "lignes": lignes[i + 1:]})
                break
    return segments


def projet_de(chemin):
    chemin = Path(chemin).resolve()
    for parent in [chemin, *chemin.parents]:
        if parent.parent.name == "projets":
            return parent
    return None


def toile_de(projet):
    """Toile du projet : frame.md (unit), sinon data-width/height de la composition, sinon 9:16."""
    for frame in sorted(projet.glob("hyperframes*/frame.md")):
        m = re.search(r"(\d{3,4})\s*[×x]\s*(\d{3,4})", frame.read_text(encoding="utf-8"))
        if m:
            return f"{m.group(1)}x{m.group(2)}"
    for index in sorted(projet.glob("hyperframes*/index.html")):
        t = index.read_text(encoding="utf-8")
        w, h = re.search(r'data-width="(\d+)"', t), re.search(r'data-height="(\d+)"', t)
        if w and h:
            return f"{w.group(1)}x{h.group(1)}"
    return "1080x1920"


def passages(projet):
    coupe = projet / "montage" / "coupe.json"
    if not coupe.exists():
        return []
    d = json.loads(coupe.read_text())
    return [(m["montage_debut"], m["montage_debut"] + (m["image_fin"] - m["image_debut"]) / d.get("ips", 30)) for m in d.get("morceaux", [])]


def controler_srt(chemin, regles, toile, projet, constats, statique=False):
    c, t = regles["commun"], regles["toile"][toile]
    segs = lire_srt(chemin)
    nom = Path(chemin).name
    if not segs:
        constats.append(("erreur", f"{nom} : aucun segment lisible"))
        return
    coupes = passages(projet) if projet else []
    for k, s in enumerate(segs, 1):
        texte = " ".join(s["lignes"])
        duree = s["fin"] - s["debut"]
        ou = f"{nom} #{k} ({s['debut']:.2f} s, « {texte} »)"
        if len(s["lignes"]) > t["lignes_max"]:
            constats.append(("erreur", f"{ou} : {len(s['lignes'])} lignes, {t['lignes_max']} au plus en {toile}"))
        long = max(len(l) for l in s["lignes"])
        if long > t["car_max"]:
            constats.append(("erreur", f"{ou} : {long} caractères, {t['car_max']} au plus en {toile}"))
        if duree < c["duree_min"]:
            constats.append(("erreur", f"{ou} : affiché {duree:.2f} s, {c['duree_min']} s au moins"))
        elif duree > c["duree_max"]:
            constats.append(("avertissement", f"{ou} : affiché {duree:.2f} s, plus de {c['duree_max']} s"))
        cps = len(texte) / max(duree, 1e-3)
        if cps > c["cps_max"]:
            constats.append(("erreur", f"{ou} : {cps:.0f} caractères par seconde, {c['cps_max']:.0f} au plus"))
        elif statique and cps > c["cps_alerte"]:
            constats.append(("avertissement", f"{ou} : {cps:.0f} car./s, {c['cps_alerte']:.0f} au plus pour un sous-titre statique"))
        if k > 1 and s["debut"] < segs[k - 2]["fin"] - 1e-3:
            constats.append(("erreur", f"{ou} : chevauche le segment précédent"))
        for a, b in coupes:
            if s["debut"] < b - 0.02 and s["fin"] > b + 0.02 and s["debut"] >= a - 0.02:
                constats.append(("erreur", f"{ou} : à cheval sur la coupe de {b:.2f} s"))
    script = projet / "script.md" if projet else None
    if script and script.exists():
        attendu = qa.texte_attendu(script.read_text(encoding="utf-8"), ".md")
        dit = " ".join(" ".join(s["lignes"]) for s in segs)
        norme = lambda x: re.sub(r"€", " euros ", re.sub(r"(\d)\s*h\s*(\d)", r"\1h\2", x))
        part = qa.couverture(norme(attendu), norme(dit))
        if part < c["fidelite_min"]:
            constats.append(("erreur", f"{nom} : {part:.0%} des mots de la colonne Voix de script.md retrouvés, {c['fidelite_min']:.0%} au moins"))


def controler_composition(chemin, regles, toile, constats):
    t = regles["toile"][toile]
    css = " ".join(re.findall(r"<style[^>]*>(.*?)</style>", Path(chemin).read_text(encoding="utf-8"), flags=re.S))
    trouve = False
    for selecteur, corps in REGLE_CSS_RE.findall(css):
        if not SELECTEUR_RE.search(selecteur):
            continue
        for taille in TAILLE_RE.findall(corps):
            trouve = True
            if float(taille) < t["taille_min_px"]:
                constats.append(("erreur", f"{Path(chemin).name} : « {selecteur.strip()} » en {float(taille):.0f} px, {t['taille_min_px']} px au moins en {toile}"))
    return trouve


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("cible", help="projets/<slug>, un .srt ou une composition .html")
    ap.add_argument("--json", action="store_true", help="sortie lisible par un hook")
    ap.add_argument("--statique", action="store_true", help="sous-titres statiques (sans karaoké) : repère de 15 car./s")
    args = ap.parse_args()
    cible = Path(args.cible)
    if not cible.exists():
        print(f"introuvable : {cible}", file=sys.stderr)
        return 2
    regles = tomllib.loads(REGLES.read_text(encoding="utf-8"))
    projet = projet_de(cible)
    toile = toile_de(projet) if projet else "1080x1920"
    if toile not in regles["toile"]:
        print(f"toile {toile} absente de {REGLES.name}", file=sys.stderr)
        return 2
    constats = []
    srts = [cible] if cible.suffix == ".srt" else (sorted((projet / "sous-titres").glob("*.srt")) if projet else [])
    compos = [cible] if cible.suffix == ".html" else (sorted(projet.glob("hyperframes*/index.html")) + sorted(projet.glob("hyperframes*/compositions/*.html")) if projet else [])
    for s in srts:
        controler_srt(s, regles, toile, projet, constats, args.statique)
    tailles = [controler_composition(h, regles, toile, constats) for h in compos]
    if compos and not any(tailles):
        constats.append(("avertissement", "aucune règle CSS de sous-titres trouvée (sélecteur st, sous-titre ou caption) : taille non vérifiée"))
    if not srts:
        constats.append(("avertissement", "aucun .srt dans sous-titres/ : forme et fidélité non vérifiées"))
    erreurs = [x for x in constats if x[0] == "erreur"]
    if args.json:
        print(json.dumps({"projet": str(projet), "toile": toile, "constats": constats}, ensure_ascii=False))
    else:
        print(f"Sous-titres : {projet or cible} · toile {toile} · règles {REGLES.name}")
        for niveau, texte in constats:
            print(f"[{niveau}] {texte}")
        print(f"{len(erreurs)} erreur(s), {len(constats) - len(erreurs)} avertissement(s)")
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
