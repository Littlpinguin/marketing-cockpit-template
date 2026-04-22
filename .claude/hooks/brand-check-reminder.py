#!/usr/bin/env python3
"""
PostToolUse hook: remind Claude to invoke the brand-check skill after any
Write/Edit of content in a production folder.

Triggers:
- Write or Edit tool
- Path containing /03-social-media/, /04-email/, /05-web-content/,
  /07-events/, or /09-blog-seo/
- Extension .md or .html

Exclusions:
- CLAUDE.md, README.md, STATUS.md (meta)
- Subfolders templates/, examples/, archives/, drafts/wip/ (references)
- Technical files (.py, .js, .sh, .json, etc.)
- Files marked [WIP] in the name
"""

import json
import os
import re
import sys

PRODUCTION_FOLDERS = (
    "/03-social-media/",
    "/04-email/",
    "/05-web-content/",
    "/07-events/",
    "/09-blog-seo/",
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
