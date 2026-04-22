#!/usr/bin/env python3
"""
Scan operational files for unresolved Mustache-style placeholders.

Usage:
  python3 scripts/lint-placeholders.py [--paths PATH ...] [--json] [--allow NAMES]

By default, scans the 9 role folders and .claude/skills. Exits 0 when no placeholder
remains, 1 otherwise. /validate-setup relies on this exit code.

Files ignored:
- Anything under .git, .setup-archive, _bootstrap/inputs, _examples
- Binary files
- Files listed in --ignore

Placeholders ignored:
- Names listed in --allow (e.g. markers like TODO, MONTH_YEAR intentionally kept)
- Placeholders inside Markdown code fences (informational examples)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Z][A-Z0-9_]*)\s*\}\}")
DEFAULT_PATHS = [
    "01-brand",
    "02-strategy",
    "03-social-media",
    "04-email",
    "05-web-content",
    "06-graphic-design",
    "07-events",
    "08-mail-signatures",
    "09-blog-seo",
    ".claude/skills",
    "CLAUDE.md",
    "README.md",
]
IGNORE_DIRS = {".git", ".setup-archive", "_bootstrap", "_examples", "node_modules", "__pycache__", ".venv", "venv", "docs"}
TEXT_SUFFIXES = {".md", ".mdx", ".html", ".htm", ".txt", ".yaml", ".yml", ".json"}


def iter_files(paths: Iterable[str]) -> Iterable[Path]:
    for raw in paths:
        p = Path(raw)
        if not p.exists():
            continue
        if p.is_file():
            yield p
            continue
        for f in p.rglob("*"):
            if not f.is_file():
                continue
            if any(part in IGNORE_DIRS for part in f.parts):
                continue
            if f.suffix.lower() not in TEXT_SUFFIXES:
                continue
            yield f


def strip_code_fences(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out = []
    in_fence = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            out.append("\n")
            continue
        if in_fence:
            out.append("\n")
        else:
            out.append(line)
    return "".join(out)


def scan_file(path: Path, allow: set[str]) -> list[tuple[int, str]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    scrubbed = strip_code_fences(text)
    findings: list[tuple[int, str]] = []
    for match in PLACEHOLDER_RE.finditer(scrubbed):
        name = match.group(1)
        if name in allow:
            continue
        line_no = scrubbed.count("\n", 0, match.start()) + 1
        findings.append((line_no, name))
    return findings


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Lint unresolved {{PLACEHOLDER}} tokens.")
    parser.add_argument("--paths", nargs="*", default=DEFAULT_PATHS, help="Paths to scan (files or directories).")
    parser.add_argument("--allow", nargs="*", default=["TODO", "MONTH_YEAR", "NAME", "ROLE", "EMAIL", "PHONE", "LINKEDIN_URL"],
                        help="Placeholder names to ignore.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human text.")
    args = parser.parse_args(argv)

    allow = set(args.allow)
    total = 0
    results: dict[str, list[dict]] = {}
    for f in iter_files(args.paths):
        findings = scan_file(f, allow)
        if not findings:
            continue
        results[str(f)] = [{"line": ln, "placeholder": name} for ln, name in findings]
        total += len(findings)

    if args.json:
        print(json.dumps({"total": total, "files": results}, indent=2))
    else:
        if total == 0:
            print("OK — no unresolved placeholders.")
        else:
            print(f"FOUND {total} unresolved placeholder(s) across {len(results)} file(s):\n")
            for path, items in sorted(results.items()):
                print(f"  {path}")
                for item in items:
                    print(f"    line {item['line']}: {{{{{item['placeholder']}}}}}")
            print(f"\nAllowed markers (ignored): {', '.join(sorted(allow)) or '(none)'}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
