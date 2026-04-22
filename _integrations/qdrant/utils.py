"""
utils.py – Fonctions communes : config, hash, chunking, logging, registry.

Pas de logique métier ici, seulement des briques réutilisées par sync.py et les connecteurs.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parent.parent


def load_env() -> None:
    load_dotenv(PROJECT_ROOT / ".env")


def load_config() -> dict:
    with open(HERE / "config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def setup_logging(level: str = "INFO") -> logging.Logger:
    logs_dir = HERE / "logs"
    logs_dir.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d-%H%M")
    log_file = logs_dir / f"{ts}-sync.log"

    logger = logging.getLogger("qdrant_sync")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S")

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    logger.info("Log file: %s", log_file)
    return logger


# -----------------------------------------------------------------------------
# Hashing
# -----------------------------------------------------------------------------

_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    return _WS_RE.sub(" ", text.strip().lower())


def content_hash(text: str) -> str:
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()


def point_uuid(source_file: str, chunk_index: int) -> str:
    """Deterministic UUID for a chunk. Same source_file + chunk_index → same UUID."""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, f"n2-knowledge::{source_file}::{chunk_index}"))


# -----------------------------------------------------------------------------
# Chunking
# -----------------------------------------------------------------------------

def approx_token_count(text: str) -> int:
    """Rough token count : 1 token ≈ 4 chars for latin text. Good enough for chunking."""
    return max(1, len(text) // 4)


def chunk_whole(text: str) -> list[str]:
    return [text.strip()] if text.strip() else []


def chunk_by_section_h2(text: str) -> list[str]:
    """Split by H2 headings. Keeps the heading as part of its section."""
    if not text.strip():
        return []
    lines = text.splitlines()
    sections: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if line.startswith("## ") and current:
            sections.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        sections.append(current)
    return ["\n".join(s).strip() for s in sections if "".join(s).strip()]


def chunk_sliding_window(text: str, size_tokens: int = 600, overlap_tokens: int = 100) -> list[str]:
    """Simple character-based sliding window approximating tokens."""
    text = text.strip()
    if not text:
        return []
    size_chars = size_tokens * 4
    overlap_chars = overlap_tokens * 4
    step = max(1, size_chars - overlap_chars)
    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + size_chars].strip())
        if i + size_chars >= len(text):
            break
        i += step
    return [c for c in chunks if c]


TRANSCRIPT_TIMESTAMP_H3 = re.compile(r"^### \d{1,2}:\d{2}:\d{2}")


def chunk_by_transcript_section(text: str, target_tokens: int = 800, max_tokens: int = 1200) -> list[str]:
    """
    Chunk a Gemini-formatted meeting transcript.

    Works with transcripts produced in English (### Summary, ### Next steps, ### Details)
    or French (### Résumé, ### Étapes suivantes, ### Détails) — the logic keys on whether
    an H3 is a timestamp or a structural heading, not on the heading text itself.

      - Structural H3 headings always flush and start a new chunk. Rare (3-5 per meeting).
      - Timestamp H3 headings (### HH:MM:SS) are in-section markers: they DO NOT
        flush unless the current chunk already exceeds target_tokens. This prevents a meeting
        with 70+ timestamps from producing 70+ micro-chunks.
      - Inside the "Details" section, bullets are grouped by token budget.
      - Hard cap at max_tokens to avoid unbounded chunks.

    Before this logic: a typical 1h meeting produced 114 chunks (1 per bullet + 1 per timestamp).
    After: the same meeting produces ~15-25 chunks, each carrying enough context for retrieval.
    """
    if not text.strip():
        return []

    lines = text.splitlines()
    chunks: list[list[str]] = []
    current: list[str] = []
    in_details = False

    def flush() -> None:
        nonlocal current
        if current and "".join(current).strip():
            chunks.append(current)
        current = []

    def current_token_count() -> int:
        return approx_token_count("\n".join(current))

    for line in lines:
        stripped = line.strip()
        is_h3 = line.startswith("### ")
        is_timestamp = bool(TRANSCRIPT_TIMESTAMP_H3.match(line))
        is_structural = is_h3 and not is_timestamp

        # Structural H3 (Summary / Résumé, Next steps / Étapes suivantes, Details / Détails, etc.)
        # always opens a new chunk.
        if is_structural:
            flush()
            lower = stripped.lower()
            in_details = (
                lower.startswith("### détails")
                or lower.startswith("### details")
            )
            current = [line]
            continue

        # Timestamp H3: flush only if we already reached the target, otherwise keep grouping
        if is_timestamp:
            if current and current_token_count() >= target_tokens:
                flush()
            current.append(line)
            continue

        # Détails section: group bullets by token budget
        if in_details:
            is_bullet = line.lstrip().startswith("* ")
            if is_bullet and current and current_token_count() >= target_tokens:
                flush()
                current = [line]
                continue

        current.append(line)

        # Hard cap to prevent unbounded chunks
        if current_token_count() >= max_tokens:
            flush()

    flush()
    return ["\n".join(c).strip() for c in chunks if "\n".join(c).strip()]


CHUNK_STRATEGIES = {
    "whole": lambda text, _cfg: chunk_whole(text),
    "by_section_h2": lambda text, _cfg: chunk_by_section_h2(text),
    "by_section": lambda text, _cfg: chunk_by_section_h2(text),
    "sliding_window": lambda text, cfg: chunk_sliding_window(
        text,
        size_tokens=cfg.get("chunk_size_tokens", 600),
        overlap_tokens=cfg.get("chunk_overlap_tokens", 100),
    ),
    "by_transcript_section": lambda text, cfg: chunk_by_transcript_section(
        text,
        target_tokens=cfg.get("transcript_target_tokens", 500),
        max_tokens=cfg.get("transcript_max_tokens", 800),
    ),
}


def chunk_text(text: str, strategy: str, source_cfg: dict) -> list[str]:
    fn = CHUNK_STRATEGIES.get(strategy)
    if fn is None:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
    return fn(text, source_cfg)


# -----------------------------------------------------------------------------
# Registry
# -----------------------------------------------------------------------------

REGISTRY_PATH = HERE / "registry.json"


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {"version": 1, "last_sync": {}, "entries": {}}
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(registry: dict) -> None:
    # Backup previous version to logs/
    if REGISTRY_PATH.exists():
        backup_dir = HERE / "logs"
        backup_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_path = backup_dir / f"registry-{ts}.json.bak"
        backup_path.write_bytes(REGISTRY_PATH.read_bytes())
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2, ensure_ascii=False, sort_keys=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# -----------------------------------------------------------------------------
# File filtering (global exclusions from config)
# -----------------------------------------------------------------------------

def is_excluded(path: Path, global_exclusions: dict) -> bool:
    name = path.name
    posix = path.as_posix()

    if name in set(global_exclusions.get("filenames", [])):
        return True

    for frag in global_exclusions.get("path_contains", []):
        if frag in posix:
            return True

    for pattern in global_exclusions.get("filename_patterns", []):
        # Simple wildcard matching: *X* matches if X is in name
        if pattern.startswith("*") and pattern.endswith("*"):
            inner = pattern.strip("*")
            if inner and inner in name:
                return True
        elif pattern.startswith("*"):
            if name.endswith(pattern[1:]):
                return True
        elif pattern.endswith("*"):
            if name.startswith(pattern[:-1]):
                return True

    return False
