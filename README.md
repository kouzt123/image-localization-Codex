# Image Localization Codex Skill

**Localize image creatives with Codex built-in image generation. No extra image API required.**

[中文说明](./README.zh-CN.md) · [Installation](./install.md) · [Skill](./SKILL.md) · [License](./LICENSE)

Image Localization is a Codex skill for turning source image creatives into localized, platform-ready ad and social assets. It is designed for marketers, UA teams, ecommerce operators, and creators who need multilingual creative variants without setting up a separate image-generation API.

![Image localization workflow overview](./examples/workflow-split-overview.png)

## Why This Skill

- **Uses your Codex subscription quota** for image generation and editing.
- **No extra API setup**: no image API key, no separate billing account, no external generation service required.
- **Native visual output**: relies on Codex built-in vision, image generation, and image editing instead of simple masking or mechanical text replacement.
- **Campaign-ready workflow**: standardized filenames, manifests, common ad sizes, and visual QA before delivery.
- **Good long-running value**: slower than a dedicated batch API, but low setup cost and strong output quality make it useful for marketing teams that can let jobs run in the background.

## Tradeoff

The built-in Codex image workflow is slower than purpose-built bulk image APIs. This skill is optimized for convenience, native visual quality, and low setup cost rather than maximum throughput.

Future work may include a separate high-throughput skill based on the Nano Banana API for faster batch production.

## What It Does

- Translates visible text inside images into target languages.
- Preserves brand names, product names, logos, subjects, and visual hierarchy.
- Adapts creatives into common ad/social sizes:
  - `1200x1200`
  - `1920x1080`
  - `1080x1350`
  - `1080x1920`
  - `1200x628`
- Handles special resolutions by generating the closest safe aspect ratio, then applying deterministic cover-crop when appropriate.
- Maintains brand/product terminology memory.
- Produces clean upload-ready filenames and manifests.
- Runs visual QA before delivery, with one regeneration pass for failed outputs.

![Organized output folder demo](./examples/organized-output-folder.png)

## How It Is Different

This is not a general image translation tool.

Most image translation projects focus on OCR, text removal, translation, and re-rendering. This skill focuses on **ad creative localization delivery**: translating in-image copy, preserving brand/product terms, adapting to common ad sizes, generating upload-ready filenames, writing manifests, and running visual QA inside a Codex workflow.

![Fictional ad localization demos](./examples/demo-localization-grid.png)

## Installation

Install directly into your Codex skills directory:

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/kouzt123/image-localization-Codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/image-localization"
```

If you prefer to clone elsewhere, symlink the whole repo:

```bash
git clone https://github.com/kouzt123/image-localization-Codex ~/Developer/image-localization-Codex
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -sfn ~/Developer/image-localization-Codex \
  "${CODEX_HOME:-$HOME/.codex}/skills/image-localization"
```

Restart Codex or refresh skills if your environment requires it.

See [install.md](./install.md) for manual setup and update notes.

## Usage

In Codex, ask for the skill explicitly:

```text
Use image-localization to translate this game ad into German, French, Spanish, Japanese, and Korean. Export 1200x1200, 1920x1080, 1080x1350, 1080x1920, and 1200x628.
```

Other examples:

```text
Localize this poster into Arabic and Vietnamese. Preserve the product name in English and make sure the 1200x628 output does not stretch the text.
```

```text
Remember that "Codex" should not be translated for OpenAI assets.
```

## Prompt Cookbook

### Game Ad

```text
Use image-localization to localize this game ad into German, Spanish, Japanese, and Arabic. Preserve the game title, translate all character traits and UI labels, and export 1200x1200, 1920x1080, 1080x1350, 1080x1920, and 1200x628.
```

### Ecommerce Product Image

```text
Use image-localization to create French and Portuguese versions of this product banner. Keep the brand name unchanged, localize the offer text, and output Meta feed, story, and 1200x628 link-ad sizes.
```

### SaaS Banner

```text
Use image-localization to localize this SaaS launch banner into Japanese and Korean. Keep product UI readable, preserve the logo, and generate 16:9 plus 1200x628 with safe margins.
```

### App Store / Social Screenshot

```text
Use image-localization to turn these app screenshots into Indonesian and Vietnamese campaign creatives. Translate visible marketing copy, keep UI labels natural, and export upload-ready filenames with manifest.json.
```

## Size Handling

For special sizes such as `1200x628`, the recommended workflow is:

1. Generate a strong `16:9` version with top/bottom safe margins.
2. Resize proportionally from `1920x1080` to `1200x675`.
3. Crop the vertical overflow to `1200x628`.

This preserves geometry and avoids non-uniform stretching.

## Terminology Memory

The skill supports a JSON memory file for user-approved terminology:

```json
{
  "version": 1,
  "brands": {
    "example-brand": {
      "display_name": "Example Brand",
      "rules": [
        {"term": "Example Brand", "action": "preserve"}
      ],
      "products": {}
    }
  }
}
```

Brand-level rules apply across products. Product-level rules can override brand rules.

## Repository Structure

```text
image-localization-Codex/
├── SKILL.md
├── README.md
├── README.zh-CN.md
├── install.md
├── LICENSE
├── examples/
├── brand_term_memory.json
└── agents/
    └── openai.yaml
```

## License

MIT. See [LICENSE](./LICENSE).
