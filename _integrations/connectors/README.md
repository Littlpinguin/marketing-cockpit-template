# _integrations/connectors/

Push-side connectors for outbound tools (email platforms, editorial calendars, events platforms, CRMs, blog CMS).

Pull-side connectors (ingestion into Qdrant) live in `_integrations/qdrant/sources/` — that's a separate contract covered by `config.yaml`.

## Contract

Every connector in this folder exposes these functions:

```python
def dry_run(content: dict) -> dict:
    """Build the payload without making any HTTP call. Called by scripts/dry-run-push.py."""

def push(content: dict, *, confirm: bool = True) -> dict:
    """Perform the real push. Honor DRY_RUN=true env var. Default to draft/scheduled, never auto-send."""
```

Optional, for connectors that are also ingestion sources:

```python
def list_items() -> Iterable[dict]:
    """Yield items to index in Qdrant."""
```

`content` arrives shaped like:

```python
{
  "frontmatter": { ... YAML frontmatter as dict ... },
  "body":        "...markdown body...",
  "path":        "path/to/source/file.md",
}
```

## Status in v0.2.0

| Tool | Push connector | Notes |
|---|---|---|
| Notion | 🟠 stub | Dry-run payload builder exists in `scripts/dry-run-push.py`. Ingestion ready (`qdrant/sources/notion.py`). |
| MailerLite | 🟠 stub | Dry-run payload builder exists. Real push not yet implemented. |
| Mailchimp | 🟠 stub | Same. |
| Outline | 🟠 stub | Dry-run payload builder exists. Ingestion ready (`qdrant/sources/outline.py`). |
| Airtable, Resend, Brevo, Livestorm, HubSpot, ... | ❌ not implemented | Stubs generated on demand by `/tools-setup`. |

The `dry-run-push.py` script has payload-building examples for Notion, MailerLite, Mailchimp, and Outline. Use them as starting points when implementing the corresponding `push()` function.

## Implementing a stub

1. Run `/tools-setup`, pick your tool when prompted, confirm the stub generation. A file at `_integrations/connectors/<tool>.py` is scaffolded from `_templates/connector-stub.py.tpl`.
2. Open the file. The contract is pre-wired; you fill in the HTTP call.
3. Use the SDK if one exists (`pip install <sdk>`), otherwise `requests`.
4. Default creation mode should be **draft** or **scheduled**, never immediate send. The human confirms the final push in the tool UI.
5. Test end-to-end:
   ```
   DRY_RUN=true python3 scripts/dry-run-push.py --target <tool> --file <draft>
   # inspect payload, verify ids resolved correctly
   python3 scripts/dry-run-push.py --target <tool> --file <draft>
   # then the real push in a test environment first
   ```
6. Update `docs/tools.json`: flip `connector_status` from `stub` to `ready`, add the `connector_path`.
7. Re-run `/tools-setup` to refresh the README tool-status board.

## Security

- Connectors read secrets via `os.environ.get(...)` at function time. Never cached, never echoed.
- Log at `INFO` level with payload size and destination URL; never log full payloads (they may contain drafts).
- Wrap all HTTP with reasonable timeouts (60 s default).
- Handle partial failures. A dropped connection in the middle of a multi-recipient push is the kind of thing to surface loudly.

## Contributing a connector back to the upstream template

This template is meant to be cloned and adapted per-company, not a project soliciting PRs. But a clean, well-documented connector you're willing to share benefits everyone. Open a discussion on the source repo with your implementation.
