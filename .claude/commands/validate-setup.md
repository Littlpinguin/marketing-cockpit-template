---
name: validate-setup
description: Final gate of the wizard. Runs the placeholder linter, generates a sample post + newsletter paragraph + article headline, passes them through brand-check, and asks the user "does this sound like you?" On approval, writes .setup-completed and archives _bootstrap/.
---

# /validate-setup — lockdown the setup

Load the `copilot-setup` skill first.

## Intent

Before claiming setup is done, the wizard must prove the copilot produces output that actually matches the brand. This command runs three checks:

1. **Static check**: are there any unresolved `{{PLACEHOLDER}}` left in operational files?
2. **Dynamic check**: can the copilot generate 3 sample artifacts that pass brand-check on the first try?
3. **User check**: does the user recognize their own voice in those samples?

Only when all three pass does the wizard write `.setup-completed` and hand back.

## Flow

### Step 1 — Run the placeholder linter

```
python3 scripts/lint-placeholders.py
```

If the exit code is non-zero:
- Show the user the list of remaining placeholders and their files.
- Offer three resolutions:
  - Return to `/brand-discover` to fill visual / voice placeholders
  - Return to `/tools-setup` to fill tool placeholders
  - Mark the placeholder as intentional (add it to the `allow` list in `scripts/lint-placeholders.py`)
- Do **not** proceed to step 2 until the linter passes.

### Step 1b — Secrets hygiene check

Non-negotiable before lockdown (see `SECURITY.md`):

```bash
git check-ignore -q .mcp.json && echo "OK: .mcp.json ignored" || echo "FAIL"
git ls-files .mcp.json        # must print NOTHING (.mcp.json never tracked)
git diff --cached | grep -iE "api_key|secret|token|password"   # must print nothing suspicious
```

If `.mcp.json` is tracked or not ignored: stop, run `git rm --cached .mcp.json`, fix `.gitignore`, and tell the user to revoke any token already pushed. Also remind: MCP server tokens live in the local `.mcp.json` (real values — `${VAR}` references are NOT expanded from the project `.env`), script tokens live in `.env`.

### Step 2 — Generate sample artifacts

Produce three samples using the corresponding production skills:

#### Sample 1 — LinkedIn post

Prompt the `social-content` skill with:

> Write a short LinkedIn post (80-120 words) about a recent insight in our field. Use our actual voice, cite one real number from our messaging framework, and end with a clear CTA. Focus on one of our content pillars, your choice.

Read the output. Pass it through `brand-check`.

#### Sample 2 — Newsletter paragraph

Prompt the `email` skill with:

> Write the opening paragraph of our next monthly newsletter (60-100 words). It should: set a single theme for the month, reference a real proof point, and hint at what's coming in the issue. Use our actual voice.

Read the output. Pass it through `brand-check`.

#### Sample 3 — Blog article headline + meta

Prompt the `seo` skill with:

> Propose a single blog article title (< 60 chars), meta description (< 155 chars), and slug for a future article tied to one of our content pillars. Must use our brand vocabulary and target one of our personas.

Read the output. Pass it through `brand-check`.

### Step 3 — Present to the user

Show all three samples back-to-back:

```
## Sample #1 — LinkedIn post
[full draft]

Brand-check verdict: ✅ PASS

## Sample #2 — Newsletter opening
[full draft]

Brand-check verdict: ✅ PASS

## Sample #3 — Blog headline
Title: [...]
Meta: [...]
Slug: [...]

Brand-check verdict: ✅ PASS
```

Then ask:

> Does this sound like you?
>
> 1. ✅ **Ship it** — I'll write `.setup-completed` and the copilot is live.
> 2. 🔁 **Adjust voice** — one or more samples are off. I'll take your feedback and go back to `/brand-discover` to refine the voice doctrine.
> 3. ❌ **Restart** — something fundamental is wrong. I'll back up the current state to `.setup-archive/` and restart.

### Step 4a — If 🔁 Adjust voice

Ask the user specifically:
- Which sample(s) are off?
- What's wrong — vocabulary, tone, rhythm, data references?
- Is the issue in the voice doctrine (need to fix `01-brand/voice.md`) or in how the skill applied it (need to strengthen the skill's customizations)?

Take the feedback. Update the relevant file. Then re-run step 2 with the updated doctrine. Max 3 rounds — if it's still not working after 3, surface the issue and suggest manual editing of `01-brand/voice.md`.

### Step 4b — If ❌ Restart

Confirm destructive action:

> This will move your current `01-brand/` and wizard log to `.setup-archive/v0.2-abandoned-<ISO8601>/`. No data is deleted. Proceed? (yes / no)

On yes: `git mv` current state to archive, clear `.setup-completed` if written, return to `/start-copilot`.

### Step 4c — If ✅ Ship it

#### 4c.1 — Write `.setup-completed`

Construct the JSON conforming to `docs/setup-completed.schema.json`. Write to `.setup-completed`.

#### 4c.2 — Archive `_bootstrap/inputs/`

If `_bootstrap/inputs/` has any user-dropped files, move them to `.setup-archive/v0.2-inputs/`. Confirm before moving.

#### 4c.3 — Update tool-status board in README

Call the subroutine in `copilot-setup` skill to regenerate the tool-status table between `<!-- tool-status:start -->` and `<!-- tool-status:end -->` markers. If the markers do not exist yet in `README.md`, append a "## Tool status" section at the end of the README with both markers, then fill it.

#### 4c.4 — Final recap

Output:

> ✅ Setup complete.
>
> Your copilot is live. Try:
>
> - "Write a LinkedIn post about [topic]" — `social-content` skill engages automatically
> - "Draft the next monthly newsletter" — `email` skill
> - "Propose a blog article on [topic]" — `seo` skill
> - `/health-check` any time — verifies env keys, MCP servers, hook wiring, cron
> - `/tools-setup` to add/change tools later
> - `/brand-discover` to refine the voice doctrine later
>
> Security reminders:
>
> - API keys live in `.env` (scripts) or in the local, untracked `.mcp.json` (MCP servers) — both gitignored, never in a tracked file
> - Use `dry-run-push.py` before every production push
> - Full rules: `SECURITY.md`
>
> Happy shipping.

## Failure modes to avoid

- **Don't write `.setup-completed` on anything less than ✅ Ship it.** No partial lockdown.
- **Don't skip the linter** even if step 2 passes. Orphaned placeholders cause silent misbehavior later.
- **Don't approve step 2 on synthetic PASS.** The brand-check skill's verdicts should match what a human would say. If a sample looks wrong to you but gets ✅, surface that discrepancy — the skill or doctrine needs strengthening.
- **Don't allow skip on step 3.** The user signing off on real samples is the whole point of this command.
