"""
sources/transcripts.py — connector for Google Meet / Gemini meeting transcripts.

Transcripts in `_sources/transcriptions/` are markdown files in Gemini Notes
format (title, Summary / Résumé, Next steps / Étapes suivantes, Details /
Détails — EN and FR variants both handled). Section-aware chunking is done
in phase 2 by `utils.chunk_by_transcript_section`.

This connector lists files and extracts metadata:
  - date from the filename
  - client from the path (if under `transcriptions/clients/<name>/`)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

logger = logging.getLogger("qdrant_sync")

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent.parent

DATE_RE = re.compile(r"(\d{4})[_-](\d{2})[_-](\d{2})")


def _extract_date_from_filename(name: str) -> str | None:
    m = DATE_RE.search(name)
    if not m:
        return None
    y, mo, d = m.groups()
    try:
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}T00:00:00Z"
    except ValueError:
        return None


def _extract_client_from_path(path: Path) -> str | None:
    parts = path.parts
    if "clients" in parts:
        idx = parts.index("clients")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return None


def iter_documents(source_cfg: dict, global_cfg: dict) -> Iterable[dict]:
    pattern = source_cfg["pattern"]
    source_key = source_cfg.get("_key", "transcripts")
    global_exclusions = global_cfg.get("global_exclusions", {})

    from utils import is_excluded

    paths = sorted(PROJECT_ROOT.glob(pattern))

    for path in paths:
        if not path.is_file():
            continue
        if is_excluded(path, global_exclusions):
            continue
        if path.name in set(source_cfg.get("exclude_files", [])):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.warning("Cannot read transcript %s: %s", path, e)
            continue

        if not content.strip():
            continue

        rel_path = path.relative_to(PROJECT_ROOT).as_posix()
        client = _extract_client_from_path(path)
        date = _extract_date_from_filename(path.name)

        tags = []
        if client:
            tags.append(f"client:{client}")
        tags.append("meeting")

        metadata = {
            "type": source_cfg.get("type", "transcript"),
            "source_key": source_key,
            "source_file": rel_path,
            "language": source_cfg.get("language", "fr"),
            "channel": source_cfg.get("channel", "internal"),
            "author": source_cfg.get("author", "n2"),
            "status": source_cfg.get("status", "published"),
            "tags": tags,
            "date": date,
        }

        yield {
            "source_file": rel_path,
            "content": content,
            "metadata": metadata,
        }
