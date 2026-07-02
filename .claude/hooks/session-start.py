#!/usr/bin/env python3
"""Hook SessionStart — snapshot de contexte au démarrage de session.

Affiche (uniquement si pertinent) :
  1. Un snapshot marque (5 lignes max) depuis .setup-completed + 01-brand/
  2. Les fichiers non traités dans 00-intel/inbox/
  3. L'existence d'un progress.md à reprendre
  4. Les 3 prochaines entrées du calendrier éditorial

Contrat : ne jamais planter (toujours exit 0), silencieux si rien à signaler,
aucune lecture de secrets (.env jamais ouvert).
"""

import datetime
import json
import os
import re
import sys

MAX_LINE = 100  # longueur max d'une ligne affichée


def project_dir() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def truncate(text: str, limit: int = MAX_LINE) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def extract_after_heading(content: str, keywords) -> str:
    """Première ligne de texte non vide sous un titre contenant un des mots-clés."""
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if not line.lstrip().startswith("#"):
            continue
        title = line.lower()
        if any(k in title for k in keywords):
            for follow in lines[i + 1 : i + 8]:
                cleaned = follow.strip().strip(">-*• ").strip()
                if cleaned and not cleaned.startswith("#") and "{{" not in cleaned:
                    return truncate(cleaned)
    return ""


def brand_snapshot(root: str):
    """Snapshot 5 lignes max : nom, mission, ton. Vide si non configuré."""
    setup_path = os.path.join(root, ".setup-completed")
    if not os.path.isfile(setup_path):
        return []
    lines = []
    company = ""
    try:
        with open(setup_path, encoding="utf-8", errors="replace") as f:
            company = str(json.load(f).get("company", "")).strip()
    except Exception:
        pass
    if company and "{{" not in company:
        lines.append(f"Marque : {company}")

    brand_dir = os.path.join(root, "01-brand")
    sources = {
        "Mission": (["mission", "purpose", "raison d"], ["messaging-framework.md", "voice.md"]),
        "Ton": (["ton", "tone", "voice", "voix"], ["voice.md"]),
    }
    for label, (keywords, files) in sources.items():
        for name in files:
            path = os.path.join(brand_dir, name)
            if not os.path.isfile(path):
                continue
            try:
                with open(path, encoding="utf-8", errors="replace") as f:
                    found = extract_after_heading(f.read(), keywords)
            except Exception:
                found = ""
            if found:
                lines.append(f"{label} : {found}")
                break
    return lines[:5]


def inbox_files(root: str):
    """Fichiers non traités dans 00-intel/inbox/ (hors fichiers cachés/.gitkeep)."""
    inbox = os.path.join(root, "00-intel", "inbox")
    found = []
    if not os.path.isdir(inbox):
        return found
    try:
        for dirpath, dirnames, filenames in os.walk(inbox):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                found.append(os.path.relpath(os.path.join(dirpath, name), inbox))
    except Exception:
        pass
    return found


def find_progress(root: str):
    """progress.md à la racine ou à un niveau de profondeur."""
    hits = []
    try:
        candidates = [os.path.join(root, "progress.md")]
        for entry in sorted(os.listdir(root)):
            sub = os.path.join(root, entry)
            if os.path.isdir(sub) and not entry.startswith((".", "_")):
                candidates.append(os.path.join(sub, "progress.md"))
        hits = [os.path.relpath(p, root) for p in candidates if os.path.isfile(p)]
    except Exception:
        pass
    return hits


DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


def next_calendar_entries(root: str, count: int = 3):
    """Les `count` prochaines entrées datées (>= aujourd'hui) du calendrier."""
    path = os.path.join(root, "02-strategy", "calendar", "calendar.md")
    if not os.path.isfile(path):
        return []
    today = datetime.date.today()
    entries = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("|") or "{{" in line:
                    continue
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) < 5:
                    continue
                m = DATE_RE.match(cells[0])
                if not m:
                    continue
                try:
                    date = datetime.date(*(int(g) for g in m.groups()))
                except ValueError:
                    continue
                if date < today:
                    continue
                canal, sujet, statut = cells[1], cells[2], cells[4]
                entries.append((date, f"{date.isoformat()} · {canal} · {truncate(sujet, 60)} [{statut}]"))
    except Exception:
        return []
    entries.sort(key=lambda e: e[0])
    return [text for _, text in entries[:count]]


def main() -> int:
    try:
        sys.stdin.read()  # payload du hook, non utilisé mais consommé
    except Exception:
        pass

    root = project_dir()
    sections = []

    brand = brand_snapshot(root)
    if brand:
        sections.append("## Snapshot marque\n" + "\n".join(f"- {l}" for l in brand))

    inbox = inbox_files(root)
    if inbox:
        shown = inbox[:5]
        extra = f" (+{len(inbox) - 5} autres)" if len(inbox) > 5 else ""
        sections.append(
            f"## 00-intel/inbox — {len(inbox)} fichier(s) non traité(s){extra}\n"
            + "\n".join(f"- {f}" for f in shown)
            + "\n→ Proposer une session de classification (voir 00-intel/CLAUDE.md)."
        )

    progress = find_progress(root)
    if progress:
        sections.append(
            "## Travail en cours\n"
            + "\n".join(f"- `{p}` existe — proposer de reprendre là où on s'était arrêté." for p in progress)
        )

    calendar = next_calendar_entries(root)
    if calendar:
        sections.append("## Prochaines échéances du calendrier\n" + "\n".join(f"- {l}" for l in calendar))

    if sections:
        print("# Contexte de session — marketing copilot\n")
        print("\n\n".join(sections))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # jamais bloquant
