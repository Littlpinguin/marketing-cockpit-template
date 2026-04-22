#!/usr/bin/env python3
"""
Dry-run mode for any outbound connector. Emits the payload that would be sent
to an external service without actually sending it.

Usage:
  python3 scripts/dry-run-push.py --target <tool> --file <content-file> [--extra key=value ...]

Supported targets (0.2.0):
  - notion          : creates a page in a Notion database
  - mailerlite      : creates a campaign draft
  - mailchimp       : creates a campaign draft
  - outline         : creates a document in an Outline collection
  - generic         : prints a generic payload based on the file content

This script NEVER makes a real HTTP request. It only constructs the payload,
validates env presence, and prints what would be sent. Real push is a separate
script in _integrations/connectors/<target>.py.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def load_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(2)
    text = path.read_text(encoding="utf-8")
    front: dict[str, Any] = {}
    body = text
    if text.startswith("---\n"):
        try:
            import yaml  # type: ignore
        except ImportError:
            print("pyyaml not installed; frontmatter will not be parsed.", file=sys.stderr)
        else:
            end = text.find("\n---\n", 4)
            if end != -1:
                front = yaml.safe_load(text[4:end]) or {}
                body = text[end + 5 :]
    return {"frontmatter": front, "body": body, "path": str(path)}


def check_env(keys: list[str]) -> dict[str, str]:
    status = {}
    for k in keys:
        status[k] = "[set]" if os.environ.get(k) else "[UNSET]"
    return status


def build_payload(target: str, content: dict[str, Any], extra: dict[str, str]) -> dict[str, Any]:
    fm = content["frontmatter"]
    body = content["body"]

    if target == "notion":
        env = check_env(["NOTION_API_KEY", "NOTION_EDITORIAL_DATABASE_ID"])
        return {
            "env": env,
            "endpoint": "POST https://api.notion.com/v1/pages",
            "request_body": {
                "parent": {"database_id": os.environ.get("NOTION_EDITORIAL_DATABASE_ID", "<UNSET>")},
                "properties": {
                    "Name":   {"title":      [{"text": {"content": fm.get("title", extra.get("title", "Untitled"))}}]},
                    "Status": {"select":     {"name": extra.get("status", "Draft")}},
                    "Pillar": {"multi_select": [{"name": fm.get("category", "")}]} if fm.get("category") else {},
                },
                "children": _markdown_to_notion_blocks(body),
            },
        }

    if target == "mailerlite":
        env = check_env(["MAILERLITE_API_KEY", "MAILERLITE_GROUP_ID"])
        return {
            "env": env,
            "endpoint": "POST https://connect.mailerlite.com/api/campaigns",
            "request_body": {
                "name":    fm.get("subject", extra.get("subject", fm.get("title", "Untitled"))),
                "type":    "regular",
                "groups":  [os.environ.get("MAILERLITE_GROUP_ID", "<UNSET>")],
                "subject": fm.get("subject", extra.get("subject", "")),
                "from":    extra.get("from", "team@example.com"),
                "from_name": extra.get("from_name", "Marketing"),
                "emails":  [{"subject": fm.get("subject", ""), "from": extra.get("from", ""), "from_name": extra.get("from_name", ""), "content": body}],
            },
        }

    if target == "mailchimp":
        env = check_env(["MAILCHIMP_API_KEY", "MAILCHIMP_AUDIENCE_ID", "MAILCHIMP_SERVER_PREFIX"])
        server = os.environ.get("MAILCHIMP_SERVER_PREFIX", "<SERVER>")
        return {
            "env": env,
            "endpoint": f"POST https://{server}.api.mailchimp.com/3.0/campaigns",
            "request_body": {
                "type": "regular",
                "recipients": {"list_id": os.environ.get("MAILCHIMP_AUDIENCE_ID", "<UNSET>")},
                "settings": {
                    "subject_line": fm.get("subject", extra.get("subject", "")),
                    "title":        fm.get("title", ""),
                    "from_name":    extra.get("from_name", "Marketing"),
                    "reply_to":     extra.get("reply_to", "team@example.com"),
                },
            },
            "body_note": "After campaign creation, a second PUT to /campaigns/{id}/content sends the HTML body.",
        }

    if target == "outline":
        env = check_env(["OUTLINE_API_KEY", "OUTLINE_URL"])
        return {
            "env": env,
            "endpoint": f"{os.environ.get('OUTLINE_URL', '<URL>')}/api/documents.create",
            "request_body": {
                "title":      fm.get("title", "Untitled"),
                "text":       body,
                "collectionId": extra.get("collection_id", "<COLLECTION_ID>"),
                "publish":    False,
            },
        }

    if target == "generic":
        return {
            "note": "Generic dry-run. No connector matched this target. Inspect and adapt.",
            "frontmatter": fm,
            "body_preview": body[:500] + ("..." if len(body) > 500 else ""),
        }

    print(f"ERROR: unknown target '{target}'.", file=sys.stderr)
    print("Supported: notion, mailerlite, mailchimp, outline, generic", file=sys.stderr)
    sys.exit(2)


def _markdown_to_notion_blocks(_body: str) -> list[dict[str, Any]]:
    """Placeholder: real conversion lives in _integrations/connectors/notion.py."""
    return [{"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": "<markdown conversion handled at real push time>"}}]}}]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Dry-run an outbound connector.")
    parser.add_argument("--target", required=True, help="notion | mailerlite | mailchimp | outline | generic")
    parser.add_argument("--file", required=True, type=Path, help="Path to the content file.")
    parser.add_argument("--extra", nargs="*", default=[], help="key=value pairs injected as extras.")
    args = parser.parse_args(argv)

    extras: dict[str, str] = {}
    for pair in args.extra:
        if "=" not in pair:
            print(f"WARNING: ignoring malformed --extra '{pair}' (expected key=value).", file=sys.stderr)
            continue
        k, v = pair.split("=", 1)
        extras[k] = v

    content = load_file(args.file)
    payload = build_payload(args.target, content, extras)

    print("=" * 80)
    print(f"DRY-RUN — target: {args.target}")
    print(f"Source file: {args.file}")
    print("=" * 80)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("=" * 80)
    print("No HTTP request made. Inspect the payload above, then run the real connector if it looks correct.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
