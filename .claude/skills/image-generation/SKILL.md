---
name: image-generation
description: Generate brand-compliant visuals for {{COMPANY_NAME}} via Google Gemini (nano-banana-pro / gemini-3-pro-image-preview). Every user prompt is automatically prefixed with style-guide constraints (palette, typography, illustration style, banned visuals).
---

# image-generation — brand-compliant visuals via Gemini

You generate visuals (hero images, banners, illustrations, carousels, social card bases) for {{COMPANY_NAME}} by calling the Gemini image API. **Your rule: never issue a raw request.** You inject brand guidelines into every prompt to guarantee visual consistency.

## Prerequisites

- `GOOGLE_AI_API_KEY` in `.env`
- `GOOGLE_AI_IMAGE_MODEL` in `.env` (default `gemini-3-pro-image-preview`)
- `01-brand/style-guide.md` must exist and contain palette, typography, illustration style, banned visuals sections
- `06-graphic-design/outputs/` must exist

## Workflow

### 1. Read the style guide

Extract:
- **Palette**: primary, accent, dark, light, signature gradient
- **Typography**: primary font, weights used
- **Illustration style**: flat / line art / isometric / photo-realistic / ...
- **Mandatory elements**: logo, gradient, watermark if applicable
- **Banned visuals**: stock photos, handshakes, post-its, generic offices, etc.

### 2. Parse the user request

User describes in natural language:

> "A hero image for our landing page on AI for small businesses, 16:9, subject: a visual metaphor of gradual transformation"

Extract:
- **Format**: aspect ratio (square / 16:9 / 9:16 / 4:5 / banner)
- **Use**: where it will be placed (LinkedIn cover, hero web, social post, infographic)
- **Subject**: visual content description
- **Specific constraints**: text to include, mandatory elements

### 3. Build the final prompt

The prompt sent to Gemini is a structured concatenation:

```
[BRAND CONSTRAINTS — NON-NEGOTIABLE]
- Color palette: primary {{BRAND_COLOR_PRIMARY}}, accent {{BRAND_COLOR_ACCENT}}, dark {{BRAND_COLOR_DARK}}, light background {{BRAND_COLOR_LIGHT}}
- Signature gradient: {{BRAND_GRADIENT}}
- Typography (if any text): {{BRAND_FONT_PRIMARY}}
- Illustration style: {{BRAND_ILLUSTRATION_STYLE}}
- MUST include: [mandatory elements per style guide]
- MUST NOT include: {{BRAND_BANNED_VISUALS}}, no stock photos, no generic office imagery, no handshakes, no post-its

[USER REQUEST]
[user prompt verbatim]

[FORMAT]
Aspect ratio: [16:9 / 1:1 / etc.]
High resolution, no text watermark, suitable for [use].
```

### 4. Call the Gemini API

```python
import os, requests
API_KEY = os.environ["GOOGLE_AI_API_KEY"]
MODEL = os.environ.get("GOOGLE_AI_IMAGE_MODEL", "gemini-3-pro-image-preview")

url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
payload = {
    "contents": [{"parts": [{"text": full_prompt}]}],
    "generationConfig": {"responseModalities": ["IMAGE"]},
}
r = requests.post(url, params={"key": API_KEY}, json=payload, timeout=120)
```

### 5. Save image and metadata

```
06-graphic-design/outputs/
├── YYYY-MM-DD-<slug>.png            ← generated image
└── YYYY-MM-DD-<slug>.json           ← metadata sidecar
```

Sidecar:
```json
{
  "slug": "hero-ai-smb-2026-04-15",
  "generated_at": "2026-04-15T10:30:00Z",
  "model": "gemini-3-pro-image-preview",
  "user_prompt": "...",
  "full_prompt_sent": "[BRAND CONSTRAINTS ...][USER REQUEST ...][FORMAT ...]",
  "format": "16:9",
  "use": "landing page hero",
  "brand_guidelines_version": "01-brand/style-guide.md@HEAD"
}
```

### 6. Conformance check

Before delivery, visually inspect:
- ✅ Palette respected (dominant colors = primary/accent)
- ✅ Style matches `{{BRAND_ILLUSTRATION_STYLE}}`
- ✅ No banned visual element
- ✅ Aspect ratio correct

If the image fails on any point, **regenerate with a reinforced prompt** on the failed axis. Max 3 attempts, then surface to the user.

## Usage rules

### Allowed
- Direct prompts with subject description
- Request a series of variations (call 3-5 times with prompt variants)
- Integration of written elements (numbers, short quotes)

### Not allowed
- Generate a recognizable face (deepfake) without consent
- Generate a competitor's logo
- Reproduce a copyrighted style (named living artist, franchise)
- Generate content that contradicts the voice doctrine

### Gemini technical limits
- **Text in image**: may render poorly; always check spelling
- **Human faces**: plausible but can have artifacts
- **Logos**: Gemini does not know your logo. If needed, composite after with an external tool.
- **No effective negation**: "no office" may produce an office. Reframe positively: "outdoor urban scene" works better.

## AI disclosure

If the brand has a disclosure policy set during `/brand-discover`, follow it. Default guidance for public-facing AI visuals: include a small caption or alt-text note.

## Brand-specific customizations

{{IMAGE_GEN_SPECIFIC_RULES}}

## Example prompts that work well

{{IMAGE_GEN_EXAMPLES}}

## Associated skills

- `brand-check` — conformance validation on the metadata sidecar if in doubt
