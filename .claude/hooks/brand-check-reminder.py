#!/usr/bin/env python3
"""
PostToolUse hook: remind Claude to invoke the brand-check skill after any
Write/Edit of content in a production folder.

Triggers:
- Write or Edit tool
- Path containing /03-social-media/, /04-email/, /05-web-content/,
  /06-graphic-design/presentations/, /07-events/, /08-video/, or /09-seo/
- Extension .md or .html

Exclusions:
- CLAUDE.md, README.md, STATUS.md (meta)
- Subfolders templates/, examples/, archives/, drafts/wip/ (references)
- Technical files (.py, .js, .sh, .json, etc.)
- Files marked [WIP] in the name

On top of the reminder, the hook runs `scripts/lint-brand.py` on the written
file and attaches its findings to the context (brand-check step 0). The hook
never blocks a write: linter missing, failing, too slow or with an unexpected
output, it silently falls back to the plain reminder and always exits 0.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LINTER = REPO / "scripts" / "lint-brand.py"
TIMEOUT_LINT_S = 20
MAX_LIGNES_LINT = 40

PRODUCTION_FOLDERS = (
    "/03-social-media/",
    "/04-email/",
    "/05-web-content/",
    "/06-graphic-design/presentations/",
    "/07-events/",
    "/08-video/",
    "/09-seo/",
)

EXCLUDED_SUBPATHS = (
    "/templates/",
    "/examples/",
    "/archives/",
    "/drafts/wip/",
    "/wip/",
)

META_FILENAMES = ("CLAUDE.md", "README.md", "STATUS.md", "TODO.md", ".gitignore")


def should_trigger(file_path: str) -> bool:
    if not file_path:
        return False

    basename = os.path.basename(file_path)
    if basename in META_FILENAMES:
        return False

    if not re.search(r"\.(md|html|mdx)$", file_path, re.IGNORECASE):
        return False

    if not any(folder in file_path for folder in PRODUCTION_FOLDERS):
        return False

    if any(sub in file_path for sub in EXCLUDED_SUBPATHS):
        return False

    if "[WIP]" in basename or "[wip]" in basename:
        return False

    return True


NIVEAUX_FR = {"error": "erreur", "warning": "avertissement"}


def _formater(constat: dict) -> str:
    position = f"{constat.get('line', '?')}"
    if constat.get("column"):
        position += f":{constat['column']}"
    niveau = constat.get("level", "?")
    return (
        f"  ligne {position} [{constat.get('rule', '?')}] "
        f"{NIVEAUX_FR.get(niveau, niveau)} : {constat.get('message', '')}"
    )


def bloc_lint(file_path: str) -> str | None:
    """Lance le linter de marque sur le fichier et rend un bloc de contexte.

    Rend None dès que le résultat n'est pas exploitable (linter absent, échec
    d'exécution, délai dépassé, JSON inattendu) : l'appelant retombe alors sur le
    rappel seul. Cette fonction ne lève jamais.
    """
    try:
        if not LINTER.exists():
            return None

        resultat = subprocess.run(
            [sys.executable, str(LINTER), file_path, "--format", "json"],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_LINT_S,
            cwd=str(REPO),
        )
        rapport = json.loads(resultat.stdout)
        resume = rapport["summary"]
        constats = rapport["findings"]
        erreurs = int(resume.get("errors", 0))
        avertissements = int(resume.get("warnings", 0))

        if erreurs:
            titre = f"🔴 LINT DE MARQUE : {erreurs} erreur" + ("s" if erreurs > 1 else "")
            if avertissements:
                titre += f", {avertissements} avertissement" + ("s" if avertissements > 1 else "")
            consigne = (
                "Les erreurs sont bloquantes : corrige-les avant toute autre étape du "
                "brand check. Les avertissements ne bloquent pas mais doivent être lus."
            )
        elif avertissements:
            titre = f"🟠 LINT DE MARQUE : {avertissements} avertissement" + (
                "s" if avertissements > 1 else ""
            )
            consigne = (
                "Aucune erreur bloquante. Lis chaque avertissement et tranche : "
                "corriger, ou justifier dans le rapport de brand check."
            )
        else:
            return "✅ LINT DE MARQUE : aucun constat déterministe sur ce fichier.\n"

        lignes = [_formater(c) for c in constats[:MAX_LIGNES_LINT]]
        reste = len(constats) - len(lignes)
        if reste > 0:
            lignes.append(
                f"  … et {reste} autres constats, relancer le linter pour la liste complète."
            )

        return (
            f"{titre}\n"
            + "\n".join(lignes)
            + f"\n\nRelancer après correction : `python3 scripts/lint-brand.py {file_path}`\n"
            + consigne
            + "\n"
        )
    except Exception:
        # Toute forme inattendue du rapport (findings qui n'est pas une liste,
        # constat sans les clés attendues, summary absent) tombe ici comme un
        # linter absent : on rend le rappel simple, jamais un traceback.
        return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    tool_input = payload.get("tool_input", {}) or {}
    file_path = tool_input.get("file_path", "") or ""

    if not should_trigger(file_path):
        return 0

    reminder = (
        "BRAND CHECK REQUIRED\n\n"
        f"You just wrote or edited `{os.path.basename(file_path)}` "
        f"in a production folder (`{file_path}`).\n\n"
        "**Before handing back to the user**, you MUST invoke the `brand-check` "
        "skill via the Skill tool to validate this draft against the brand "
        "standards (5-point filter: vocabulary, tone, proof, audience, visual).\n\n"
        "Apply all 🟠 corrections before delivery. Surface every 🔴 to the user. "
        "Do NOT announce the draft as validated until brand-check returns "
        "✅ PASS. This step is non-negotiable."
    )

    lint = bloc_lint(file_path)
    if lint:
        reminder = f"{lint}\n---\n\n{reminder}"

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": reminder,
        }
    }

    print(json.dumps(output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
