# _templates/

Source templates used by the wizard to generate operational files. You rarely need to touch these by hand — the wizard reads them, substitutes placeholders, and writes the resulting files to the appropriate location.

## Contents

```
_templates/
├── role-claudemd/         ← 9 role CLAUDE.md templates (source for /tools-setup)
│   ├── 01-brand.md
│   ├── 02-strategy.md
│   ├── 03-social-media.md
│   ├── 04-email.md
│   ├── 05-web-content.md
│   ├── 06-graphic-design.md
│   ├── 07-events.md
│   └── 09-blog-seo.md
├── brand/                 ← brand doctrine scaffolds (source for /brand-discover)
│   ├── voice.md
│   ├── style-guide.md
│   ├── personas.md
│   └── messaging-framework.md
└── connector-stub.py.tpl  ← generic connector skeleton (source for /tools-setup when a tool has no built-in)
```

## Which command uses what

| Wizard command | Reads | Writes |
|---|---|---|
| `/brand-discover` | `_templates/brand/*.md` | `01-brand/voice.md`, `style-guide.md`, `personas.md`, `messaging-framework.md` |
| `/tools-setup`   | `_templates/role-claudemd/<role>.md` | `<role>/CLAUDE.md` for each of the 9 roles, with tool placeholders substituted |
| `/tools-setup`   | `_templates/connector-stub.py.tpl` | `_integrations/connectors/<tool>.py` for every stub tool selected |

## Customizing the templates

You can edit these before running the wizard — your changes will be the starting point for every regenerated file. If you edit them after setup, nothing happens automatically: re-run `/tools-setup` or `/brand-discover` to apply changes, or apply your edits manually to the generated files.

## Conventions

- Placeholders use `{{UPPERCASE_UNDERSCORE}}` (Mustache-style). Canonical list in `docs/placeholders.json`.
- English only, per the template's operational language rule (content produced by the copilot still follows the brand language you pick at setup).
- No secrets. If a template references a secret, it references the **env variable name**, never the value.
