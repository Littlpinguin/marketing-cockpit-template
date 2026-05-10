# mail-signatures — HTML email signature generator

This is a sub-area of `06-graphic-design`. It generates HTML email signatures for team members of {{COMPANY_NAME}}, consistent with the brand style guide. Utility scope: no brand-check gate — but the output must render correctly across Gmail, Outlook, and Apple Mail.

## Mandatory references

- Style guide: `../../01-brand/style-guide.md` (colors, fonts, logo)
- Team list: `../../01-brand/stakeholders.md` (names and roles)

## Email client constraints

Email clients are notoriously limited for HTML/CSS. Non-negotiables:

1. **Tables for layout** — `<div>` flex/grid is not universally supported. Nested `<table>` is the safe path.
2. **Inline styles only** — Gmail strips most `<style>` blocks. Every style goes directly on the tag.
3. **System fonts** — Google Fonts do not load in Outlook Desktop. Fallback: `Arial`, `Helvetica`, `sans-serif`.
4. **Externally hosted images** — HTTPS-accessible via CDN or brand site. No data URIs (Outlook breaks on those).
5. **Max width 600 px** — standard responsive email.
6. **No JavaScript** — no email client executes it.
7. **Test on at least 3 clients**: Gmail web, Apple Mail, Outlook Desktop.

## Signature content

Per member:
- Full name
- Role / title
- Company with logo
- Email, phone (optional)
- Website link
- LinkedIn (primary social)
- One brand visual element (logo band, accent separator)
- Optional CTA (newsletter, upcoming event, whitepaper)

## Template

See `./template.html`. Placeholders: `{{NAME}}`, `{{ROLE}}`, `{{EMAIL}}`, `{{PHONE}}`, `{{LINKEDIN_URL}}`.

Brand tokens injected:
- `{{BRAND_COLOR_PRIMARY}}` — name and accent border
- `{{BRAND_COLOR_DARK}}` — body text
- `{{BRAND_FONT_PRIMARY}}` — with Arial fallback
- Logo: `../../01-brand/assets/logo-email-signature.png` (size per style guide)

## Workflow

1. Gather member data: name, role, email, phone, LinkedIn, optional photo (square, 100×100 minimum).
2. Fill the template by substituting placeholders. Use `./members.yaml` if you maintain the team data there.
3. Write output to `./generated/<slug>.html`.
4. Generate a plain-text fallback at `./generated/<slug>.txt`.
5. Visual sanity check: open HTML in a browser, confirm logo renders, separator color matches, phone/LinkedIn show only if provided, no broken image paths.
6. Test in Gmail + Outlook + Apple Mail by sending yourself an email with the signature pasted.

## Deployment

Each member copies the HTML from `./generated/<slug>.html` into their email client settings. No central signature management unless a third-party tool is configured — if so, configure that separately.

## Skills associated

- `brand-check` — optional, for color/logo conformance verification

## What this utility does NOT do

- ❌ Produce editorial content
- ❌ Manage email aliases or accounts (→ IT admin)
- ❌ Design logos or create brand assets (→ parent folder `06-graphic-design/`)
- ❌ Push signatures to clients automatically
