#!/usr/bin/env python3
"""Hook du module vidéo : contrôle des sous-titres après chaque écriture (PostToolUse).

Garde-fou contre la dérive de forme d'un film à l'autre. Quand un outil vient d'écrire un .srt de
08-video/projets/<slug>/sous-titres/ ou une composition HyperFrames (projets/<slug>/hyperframes*/…html),
le hook lance 08-video/scripts/controle-sous-titres.py sur le projet. Une erreur bloque : le message
revient à Claude (code 2), qui doit corriger avant de continuer. Module vidéo absent : rien à faire.

Write et Edit donnent le fichier touché. Un Bash (un script de construction qui écrit index.html,
un générateur de .srt) n'en donne pas : le hook regarde alors les fichiers de ce type modifiés
depuis moins de deux minutes.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "08-video"
CONTROLE = MODULE / "scripts" / "controle-sous-titres.py"
RECENT = 120  # s


def concerne(chemin):
    p = Path(chemin)
    if "projets" not in p.parts:
        return False
    return (p.suffix == ".srt" and p.parent.name == "sous-titres") or (p.suffix == ".html" and any(x.startswith("hyperframes") for x in p.parts))


def projet(chemin):
    p = Path(chemin).resolve()
    for parent in p.parents:
        if parent.parent.name == "projets":
            return parent
    return None


def main():
    if not CONTROLE.exists():
        return 0
    try:
        evt = json.load(sys.stdin)
    except Exception:
        return 0
    entree = evt.get("tool_input") or {}
    touches = []
    if entree.get("file_path"):
        touches.append(entree["file_path"])
    elif evt.get("tool_name") == "Bash":
        maintenant = time.time()
        for motif in ("projets/*/sous-titres/*.srt", "projets/*/hyperframes*/index.html", "projets/*/hyperframes*/compositions/*.html"):
            touches += [str(f) for f in MODULE.glob(motif) if maintenant - f.stat().st_mtime < RECENT]
    projets = sorted({projet(t) for t in touches if concerne(t) and projet(t)})
    messages = []
    for pr in projets:
        r = subprocess.run([sys.executable, str(CONTROLE), str(pr)], capture_output=True, text=True)
        if r.returncode == 1:
            erreurs = [l for l in r.stdout.splitlines() if l.startswith("[erreur]")]
            messages.append(f"Sous-titres hors règles dans {pr.name} (08-video/scripts/sous-titres.toml) :\n" + "\n".join(erreurs))
        elif r.returncode == 2:
            messages.append(f"Contrôle des sous-titres impossible sur {pr.name} : {r.stderr.strip()}")
    if messages:
        print("\n\n".join(messages) + "\n\nCorriger la forme (08-video/formats.md § Sous-titres) avant de continuer.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
