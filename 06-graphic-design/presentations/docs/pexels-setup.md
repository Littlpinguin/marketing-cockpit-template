<!--
  VENDORED from slides-agent (https://github.com/Littlpinguin/slides-agent), docs/pexels-setup.md,
  by scripts/sync-slides-engine.py. Do not edit here: change slides-agent,
  then run python3 scripts/sync-slides-engine.py. Mentions of CLAUDE.md,
  onboarding and the pexels-photos skill refer to slides-agent.
  Register: docs/vendored-slides.md
-->
# Pexels setup — real photography for your decks

[Pexels](https://www.pexels.com) is a free library of high-quality photographs with a free API. Connecting it lets the agent illustrate the slides that call for a real image (a place, a material, an object, a gesture, an atmosphere): it searches, looks at the results, downloads the best photo into `06-graphic-design/presentations/assets/photos/`, and credits every photographer on a closing slide.

- **Cost:** free. 200 requests per hour, 20,000 per month. A 24-slide deck typically uses 10 to 30.
- **Time:** about 3 minutes.
- **Optional:** without a key, decks use your own photos, AI illustrations (`image-generation`) or typography.

> **For the agent:** walk the user through this guide **one step at a time**, in their language. Give the current step only, wait for them to confirm, then move to the next. Never ask for the key in chat: the user pastes it into `.env` themselves. See "Step 5b" in `CLAUDE.md`.

---

## Step 1 — Create a free Pexels account

1. Open <https://www.pexels.com/api/> and click **Get Started**.
2. Pexels asks *"What do you mainly want to do?"*. Choose **I want to download** (this choice limits nothing; you can do everything later).
3. Sign up with an email address or a Google account. Confirm your email if Pexels asks you to.

Already have a Pexels account? Log in and go to step 2.

## Step 2 — Request your API key

1. Once logged in, go back to <https://www.pexels.com/api/> and click **Get Started** again.
2. Fill the short form describing your project. Plain, honest answers are enough, for example:
   - **Project name:** `Presentation decks` (or your company name)
   - **Description:** `Illustrating presentation slides with photographs, credited to the photographers on a closing slide.`
   - **Website:** your company website (or your LinkedIn profile if you have no site)
3. Accept the API terms and submit.
4. The key appears immediately: a long string of letters and digits. **Copy it.** You can come back to this page at any time to copy it again.

Pexels occasionally redesigns this form. If yours looks different, the goal is the same: reach the page that shows **Your API Key**.

## Step 3 — Put the key in `.env`

The key is personal: it lives in a local file, never in a chat, never in git.

1. At the root of the project, create `.env` from the template if it doesn't exist yet:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` in any text editor. On macOS:

   ```bash
   open -e .env
   ```

3. Find the line `PEXELS_API_KEY=` and paste your key right after the `=`:

   ```
   PEXELS_API_KEY=paste-your-key-here
   ```

   No quotes, no spaces, no line break.

4. Save and close the file.

`.env` is listed in `.gitignore`: it stays on your machine and is never committed.

## Step 4 — Test the key

```bash
python3 06-graphic-design/presentations/scripts/pexels.py check
```

Expected output:

```
OK · the Pexels API key works
quota: 19999 / 20000 requests left this month
```

The script needs two Python packages. If they're missing, it tells you; install them once with `python3 -m pip install requests pillow`.

---

## Troubleshooting

| Message | Likely cause | Fix |
|---|---|---|
| `PEXELS_API_KEY is not set` | `.env` doesn't exist, the key isn't on the `PEXELS_API_KEY=` line, or the file wasn't saved | Redo step 3, check the file is named exactly `.env` at the project root |
| `Pexels rejected the API key (HTTP 401)` or `(HTTP 403)` | Key truncated, or wrapped in quotes or spaces | Copy the key again from <https://www.pexels.com/api/> and paste it with nothing around it |
| `Pexels quota reached` | More than 200 requests in the last hour | Wait for the reset time shown. Past searches are cached in `.cache/pexels/` and cost nothing to reread |
| `the requests and Pillow packages are required` | Python packages missing | `python3 -m pip install requests pillow` |
| `request to Pexels failed` | No network, VPN or proxy blocking `api.pexels.com` | Check the connection, then run `check` again |

---

## What happens next

Ask for photos in plain words: *"illustrate slide 5 with a photo"*, *"a warmer, emptier picture for the cover"*. The agent also proposes photos on its own when a beat calls for one, never more than about one slide in four.

For each photo, it:

1. searches Pexels with concrete words (`harbour at dawn`, not `success`) and reads a numbered contact sheet of the results;
2. rejects stock clichés (handshakes, suits, smiling faces at the camera, lightbulbs, robot hands);
3. downloads the chosen photo into `06-graphic-design/presentations/assets/photos/pexels-<slug>-<id>.jpg`, with a `.json` sidecar that records the photographer and the source;
4. optionally writes a brand-tinted variant (`--treatment mono` or `duotone`, colours read from `06-graphic-design/presentations/tokens.css`);
5. places it in the slide, checks the text stays legible, and adds the **photo credits** slide at the end of the deck.

At the end, it lists every photo it chose with its Pexels link, so you can ask for a different one.

## Licence in short

The [Pexels License](https://www.pexels.com/license/) allows free use, including commercial use, and modification. Attribution isn't required but is appreciated: the credits slide handles it. Not allowed: selling unaltered copies of a photo, implying that people in a photo endorse your brand, showing identifiable people in a negative light, or redistributing the photos on another stock platform.

If you show Pexels attribution consistently and need more than the default limits, Pexels can raise them for free on request (see <https://www.pexels.com/api/>).
