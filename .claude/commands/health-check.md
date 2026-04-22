---
name: health-check
description: Ongoing. Verify env vars are set, MCP servers reachable, placeholder lint passes, brand-check hook wired, cron loaded (if applicable). Run monthly or when things feel off.
---

# /health-check — verify runtime health

Load the `copilot-setup` skill first.

## Intent

Things drift. API keys expire. MCP servers stop. Hooks get disabled. Cron jobs fail silently. This command runs a battery of non-destructive checks and reports what's healthy and what needs attention.

Safe to run any time. No writes, no external API calls beyond reachability tests.

## Checks

### 1. `.setup-completed` exists and is valid

- Read `.setup-completed`.
- Validate against `docs/setup-completed.schema.json`.
- If missing: warn that setup is incomplete and suggest `/start-copilot`.
- If malformed: show the validation error.

### 2. Placeholder linter

```
python3 scripts/lint-placeholders.py
```

Report exit code.

### 3. `.env` completeness

For every tool enabled in `.setup-completed.tools.*`, verify the required env keys are present in `.env` (presence only — do not print values).

Flag missing keys.

### 4. MCP server reachability

Read `.mcp.json`. For each configured server, test that the command starts without error (run it in `--help` or equivalent probe mode, not full startup). Report which are healthy.

### 5. Qdrant reachability (if enabled)

If `.setup-completed.features.qdrant.enabled == true`:
- `curl -s -H "api-key: $QDRANT_API_KEY" $QDRANT_URL/collections -o /dev/null -w "%{http_code}"` — should be 200.
- `python3 _integrations/qdrant/sync.py --stats` — should report collection size and last sync date.

### 6. Brand-check hook wiring

- Verify `.claude/settings.json` has the PostToolUse hook registered.
- Verify `.claude/hooks/brand-check-reminder.py` exists and is executable.
- Run the hook with a synthetic payload to confirm it fires correctly:
  ```
  echo '{"tool_input":{"file_path":"03-social-media/linkedin/drafts/test.md"}}' | python3 .claude/hooks/brand-check-reminder.py
  ```

### 7. Cron state (macOS only, if Qdrant enabled)

- `launchctl list | grep qdrant` — should show the loaded agent.
- Tail the last 20 lines of `_integrations/qdrant/logs/cron-weekly.stderr.log` — look for recent errors.
- Check the last modified timestamp of `_integrations/qdrant/registry.json` — should be within the last 8 days.

### 8. Tool-status board freshness

- Compare the tool-status table in `README.md` against `.setup-completed.tools.*`.
- If mismatch, suggest running `/tools-setup` to re-render the board.

### 9. Git hygiene

- `git status --porcelain` — flag uncommitted changes to operational files (suggest commit or stash).
- `grep -r "API_KEY\|TOKEN\|SECRET" --include="*.md" --include="*.py" .` (excluding `.env*`, `.setup-archive/`, `docs/`) — flag any hardcoded secret-looking strings.

## Report format

```
## Health Check — <ISO 8601>

| Check | Status | Detail |
|---|---|---|
| .setup-completed | ✅ | Valid, version 0.2.0 |
| Placeholders | ✅ | No unresolved {{*}} |
| .env completeness | 🟠 | Missing: MAILCHIMP_SERVER_PREFIX |
| MCP reachability | ✅ | qdrant MCP responds |
| Qdrant cluster | ✅ | 200 OK, 1,247 points indexed |
| Brand-check hook | ✅ | PostToolUse registered, hook executable |
| Weekly cron | 🟠 | Loaded but last log shows error: "403 on collection fetch" |
| Tool-status board | ✅ | Matches .setup-completed |
| Git hygiene | ✅ | Clean |

### Action items
1. Add MAILCHIMP_SERVER_PREFIX to .env (see .env.example)
2. Investigate last cron error — likely an expired Qdrant key, re-check in Qdrant Cloud

### All green?
No — 2 warnings, 0 blocks. System is operational but needs attention before next month's newsletter.
```

## Output disposition

- All green: end with "✅ All systems operational."
- Warnings only: list action items, allow continued work.
- Blocks: surface each block, explain the impact, and propose remediation.

## Failure modes to avoid

- **Don't attempt remediation automatically.** This command is diagnostic.
- **Don't print secrets.** Presence checks only; use `[set] / [unset]` in the report.
- **Don't run long sync jobs.** Reachability tests only.
- **Don't modify files.** Zero writes.
