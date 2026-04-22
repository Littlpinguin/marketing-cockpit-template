"""
sources/notion.py — connector for a Notion editorial-calendar database.

Queries the Notion database via the official REST API, filters on a
configurable Status value (e.g. "✅  Scheduled" — watch out for double spaces
and emoji prefixes when copied from Notion UI), optionally requires a
`Validated` checkbox, then fetches each page's blocks and flattens them into
light markdown for indexing.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Iterable

import requests

logger = logging.getLogger("qdrant_sync")

NOTION_API = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['NOTION_API_KEY']}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _query_database(database_id: str, filter_obj: dict | None) -> Iterable[dict]:
    url = f"{NOTION_API}/databases/{database_id}/query"
    payload: dict[str, Any] = {"page_size": 100}
    if filter_obj:
        payload["filter"] = filter_obj

    cursor: str | None = None
    while True:
        if cursor:
            payload["start_cursor"] = cursor
        r = requests.post(url, headers=_headers(), json=payload, timeout=30)
        if r.status_code != 200:
            logger.error("Notion query failed %d: %s", r.status_code, r.text[:300])
            return
        data = r.json()
        for page in data.get("results", []):
            yield page
        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            return


def _fetch_block_children(block_id: str) -> list[dict]:
    url = f"{NOTION_API}/blocks/{block_id}/children"
    blocks: list[dict] = []
    cursor: str | None = None
    while True:
        params = {"page_size": 100}
        if cursor:
            params["start_cursor"] = cursor
        r = requests.get(url, headers=_headers(), params=params, timeout=30)
        if r.status_code != 200:
            logger.warning("Notion blocks fetch %d: %s", r.status_code, r.text[:200])
            return blocks
        data = r.json()
        blocks.extend(data.get("results", []))
        if data.get("has_more") and data.get("next_cursor"):
            cursor = data["next_cursor"]
        else:
            return blocks


def _rich_text_to_plain(rich_text: list[dict]) -> str:
    return "".join(rt.get("plain_text", "") for rt in rich_text)


def _block_to_markdown(block: dict, depth: int = 0) -> str:
    btype = block.get("type")
    node = block.get(btype, {}) if btype else {}
    rt = node.get("rich_text", [])
    plain = _rich_text_to_plain(rt) if rt else ""
    indent = "  " * depth

    if btype == "paragraph":
        return f"{indent}{plain}\n" if plain else ""
    if btype == "heading_1":
        return f"\n# {plain}\n"
    if btype == "heading_2":
        return f"\n## {plain}\n"
    if btype == "heading_3":
        return f"\n### {plain}\n"
    if btype == "bulleted_list_item":
        return f"{indent}- {plain}\n"
    if btype == "numbered_list_item":
        return f"{indent}1. {plain}\n"
    if btype == "to_do":
        checked = "[x]" if node.get("checked") else "[ ]"
        return f"{indent}- {checked} {plain}\n"
    if btype == "quote":
        return f"{indent}> {plain}\n"
    if btype == "callout":
        return f"{indent}> {plain}\n"
    if btype == "code":
        lang = node.get("language", "")
        return f"\n```{lang}\n{plain}\n```\n"
    if btype == "divider":
        return "\n---\n"
    if btype == "toggle":
        return f"{indent}- {plain}\n"
    if plain:
        return f"{indent}{plain}\n"
    return ""


def _page_to_markdown(page_id: str) -> str:
    blocks = _fetch_block_children(page_id)
    lines: list[str] = []
    for block in blocks:
        lines.append(_block_to_markdown(block))
        # Handle one level of nesting for lists
        if block.get("has_children"):
            children = _fetch_block_children(block["id"])
            for child in children:
                lines.append(_block_to_markdown(child, depth=1))
    return "".join(lines).strip()


def _extract_page_properties(page: dict) -> dict:
    props = page.get("properties", {})
    out: dict[str, Any] = {}

    # Title
    for pname, pvalue in props.items():
        if pvalue.get("type") == "title":
            out["title"] = _rich_text_to_plain(pvalue.get("title", []))
            break

    # Statut (select)
    statut = props.get("Statut", {}).get("select") if props.get("Statut") else None
    out["statut"] = statut.get("name") if statut else None

    # Validé (checkbox)
    out["validated"] = bool(props.get("Validé", {}).get("checkbox", False))

    # Date de diffusion
    date_prop = props.get("Date de diffusion", {}).get("date") if props.get("Date de diffusion") else None
    out["publish_date"] = date_prop.get("start") if date_prop else None

    # Canal (multi-select) — returns the list of channel names
    canal = props.get("Canal", {}).get("multi_select", []) if props.get("Canal") else []
    out["canals"] = [c.get("name", "") for c in canal if c.get("name")]

    return out


def iter_documents(source_cfg: dict, global_cfg: dict) -> Iterable[dict]:
    database_id = source_cfg["database_id"]
    status_filter = source_cfg.get("status_filter")
    require_validated = source_cfg.get("require_validated_checkbox", True)
    channel_mapping = source_cfg.get("channel_mapping", {})
    source_key = source_cfg.get("_key", "notion")

    and_filters: list[dict] = []
    if status_filter:
        and_filters.append({"property": "Statut", "select": {"equals": status_filter}})
    if require_validated:
        and_filters.append({"property": "Validé", "checkbox": {"equals": True}})

    notion_filter: dict | None = {"and": and_filters} if and_filters else None

    for page in _query_database(database_id, notion_filter):
        page_id = page["id"]
        props = _extract_page_properties(page)

        if not props.get("validated") and require_validated:
            continue
        if status_filter and props.get("statut") != status_filter:
            # Defensive : Notion already filtered but verify
            continue

        try:
            content = _page_to_markdown(page_id)
        except Exception as e:
            logger.warning("Failed to fetch Notion page %s: %s", page_id, e)
            continue

        if not content.strip():
            logger.debug("Notion page %s has no content, skip", page_id)
            continue

        # Determine type/channel/author from the first matching canal
        canals = props.get("canals", [])
        chosen_mapping = None
        for c in canals:
            if c in channel_mapping:
                chosen_mapping = channel_mapping[c]
                break

        if not chosen_mapping:
            chosen_mapping = {"channel": "unknown", "type": "notion-page", "author": "n2"}

        title = props.get("title") or "(untitled)"
        full_text = f"# {title}\n\n{content}"

        metadata = {
            "type": chosen_mapping.get("type", "notion-page"),
            "source_key": source_key,
            "source_file": f"notion://{page_id}",
            "language": "both",
            "channel": chosen_mapping.get("channel", "unknown"),
            "author": chosen_mapping.get("author", "n2"),
            "status": "published",
            "tags": [f"canal:{c}" for c in canals],
            "date": props.get("publish_date"),
            "notion_last_edited": page.get("last_edited_time"),
        }

        yield {
            "source_file": f"notion://{page_id}",
            "content": full_text,
            "metadata": metadata,
        }
