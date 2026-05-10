# Hosting & sharing

The deck is a **single, self-contained HTML file**. It carries its own CSS, JS, fonts (loaded from Google Fonts CDN), and references its assets via relative paths into `assets/`. That means hosting it is trivial — any static file server will do.

## Option 1 — Netlify Drop (zero config, public URL in 30 seconds)

The fastest way to share a deck with someone who can't run a local server.

1. Open <https://app.netlify.com/drop> in your browser.
2. Drag the **entire project folder** onto the page.
   - You can also drag just `06-graphic-design/presentations/decks/` plus `01-brand/assets/`, but the simpler path is to drag the whole repo.
3. Netlify gives you a public URL like `https://eloquent-name-12345.netlify.app/`.
4. Append `/decks/your-deck.html` to land directly on a specific deck.
5. Optional: claim the deployment under your Netlify account to get a custom subdomain.

**Caveat**: Netlify Drop URLs are public and shareable by anyone with the link. For confidential decks, password-protect them (Netlify free tier doesn't support this — see "Vercel" or "self-hosted" below) or send the file directly.

## Option 2 — Generic static host (S3, GitHub Pages, Cloudflare Pages, etc.)

Any static host works because the deck is a static file. The only requirement: when you upload, **keep the relative path between the deck and `assets/`**.

```
your-host/
├── decks/your-deck.html
└── assets/
    └── logos/your-logo.svg     ← referenced as ../assets/logos/your-logo.svg from the deck
```

**S3 + CloudFront**: upload the `decks/` plus the brand `assets/` folder to a public S3 bucket, point a CloudFront distribution at it. Set `Content-Type: text/html` on `.html` files.

**GitHub Pages**: push the project to a GitHub repo with `pages` enabled on the root. The deck lives at `https://<user>.github.io/<repo>/decks/your-deck.html`.

**Cloudflare Pages**: connect your repo, no build step needed (output dir = root). Same URL pattern.

## Option 3 — Local sharing only (privacy-first)

If the deck must stay private:

- **Run the local server**: `./scripts/serve.sh` — anyone on your network can open `http://your-machine.local:5173/decks/your-deck.html` while the script is running.
- **Send the file directly**: zip the project (or just the deck + the `assets/` it references), email or drop it. Anyone can open the `.html` directly in Chrome with no server needed.
- **Open from disk**: Chrome handles `file://...your-deck.html` perfectly, including all navigation and the print-to-PDF flow.

## A note on Google Fonts

`templates/base.html` loads Outfit + JetBrains Mono from Google Fonts. If your deck must work fully offline (e.g. in an air-gapped environment), self-host the fonts:

1. Run `npx google-fonts-helper download` (or visit <https://gwfh.mranftl.com/fonts>) to grab the woff2 files.
2. Drop them into `assets/fonts/`.
3. Replace the `<link>` tag in the deck with `@font-face` declarations pointing to the local files.

For online sharing, the CDN is fine.

## A note on confidentiality

Decks for internal-only use should not be uploaded to public hosts. Netlify Drop URLs are obfuscated but not protected. For sensitive material, use:

- A password-protected static host (Vercel hobby plan: yes; Cloudflare Pages: via Cloudflare Access; Netlify: paid tier only)
- A signed URL on a private S3 bucket
- Or just send the file directly via your normal secure channel

The deck contains no telemetry and makes no outbound calls beyond the Google Fonts CDN. Once loaded, it works fully offline.
