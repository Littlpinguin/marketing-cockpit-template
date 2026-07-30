#!/usr/bin/env python3
"""Keeps the README's skill/agent counts in sync with the actual repo content.

Counts .claude/skills/*/SKILL.md and .claude/agents/*.md from the filesystem,
then rewrites the three contextual count patterns in README.md:
  - the tagline:      "NN production skills · NN specialist agents"
  - the section head: "**NN skills**, organized by function"
  - the agents head:  "**NN agents** (`.claude/agents/`)"
It never touches dated history (CHANGELOG) or third-party product mentions.
Also warns (without failing) when the per-category table no longer sums to the
real count — that table needs a human to categorize new skills.

Run by .github/workflows/notify-site.yml on every skills/agents change,
before the site is notified. Idempotent; exits 0 whether or not it changed
anything (the workflow detects changes via git diff).
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

skills = len(list((ROOT / ".claude" / "skills").glob("*/SKILL.md")))
agents = len(list((ROOT / ".claude" / "agents").glob("*.md")))

if not (20 <= skills <= 200 and 5 <= agents <= 50):
    print(f"REFUSED: counts out of plausibility bounds (skills={skills}, agents={agents})")
    sys.exit(1)

text = README.read_text(encoding="utf-8")
out = text
out = re.sub(r"\d+ production skills · \d+ specialist agents",
             f"{skills} production skills · {agents} specialist agents", out)
out = re.sub(r"\*\*\d+ skills\*\*, organized by function",
             f"**{skills} skills**, organized by function", out)
out = re.sub(r"\*\*\d+ agents\*\* \(`\.claude/agents/`\)",
             f"**{agents} agents** (`.claude/agents/`)", out)

table_sum = sum(int(n) for n in re.findall(r"\| (\d+) \|", out))
if table_sum != skills:
    print(f"::warning::README category table sums to {table_sum} but repo has "
          f"{skills} skills — categorize the new skills in the table.")

if out != text:
    README.write_text(out, encoding="utf-8")
    print(f"README updated: {skills} skills, {agents} agents")
else:
    print(f"README already in sync: {skills} skills, {agents} agents")
