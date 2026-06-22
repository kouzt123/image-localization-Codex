---
name: ad-image-localization
description: Localize and prepare image creatives for ads, social posts, ecommerce, and campaign delivery. Use when Codex needs to adapt images into platform-specific dimensions, translate text inside images, preserve native visual quality, apply brand terminology rules, handle RTL-aware localization with QA fallback for Arabic and other RTL languages, run culture-aware QA risk checks for target markets, export standardized filenames, and visually QA generated batches. Prefer Codex built-in vision, image generation, and image editing; use local scripts only for deterministic resizing, cropping, naming, manifests, file flagging, and QA sheets.
---

# Ad Image Localization

## Purpose

Use this skill to turn source image creatives into localized, platform-ready assets. The priority is native visual quality: use Codex built-in vision and image generation/editing for recognition, translation, layout reflow, canvas extension, and visual repair. Use code only for deterministic file operations.

## Core Principles

- Inspect the source image before generating variants.
- Translate all visible user-facing text unless it is a brand/product term that should be preserved.
- For RTL languages such as Arabic, Hebrew, Persian, and Urdu, attempt RTL-aware localization by default, then fall back to copy-only localization if QA judges the adapted layout worse.
- Preserve logos, products, characters, UI hierarchy, legibility, and crop-safe zones.
- Prefer model-native aspect-ratio generation over local design reconstruction.
- Use deterministic scripts only for exact resize, cover-crop, naming, manifest generation, and contact-sheet QA.
- Never use blurred padding as the default delivery method.
- QA every deliverable before presenting the batch.
- Run Culture-Aware QA during QA; flag potential market-specific cultural, legal, religious, social, or political risks without modifying the creative unless the user asks.

## Typical Capabilities

- Generate localized versions for one or more target languages.
- Apply RTL-aware localization for RTL languages by default, with QA-controlled fallback to copy-only localization.
- Adapt one creative into common ad/social sizes such as `1200x1200`, `1920x1080`, `1080x1350`, `1080x1920`, and `1200x628`.
- Handle special resolutions by generating the closest safe model-native ratio, then applying deterministic cover-crop when appropriate.
- Maintain brand/product terminology memory across tasks.
- Export clean filenames and manifests for upload-ready batches.
- Regenerate failed outputs once, then report any remaining issues.
- Flag culturally sensitive outputs into `Flagged by Culture-Aware QA/` for user review before launch.

## Workflow

1. **Recognize the source**
   - Identify visible text, language, subject, brand/product signals, logo, CTA, layout, important edges, and crop risks.
   - For batches, inspect each distinct source image at least once.

2. **Build a job spec**
   - Track source image, brand, product, target languages, target dimensions, output directory, naming slug, protected terms, localization mode, and QA notes.
   - Keep brand-level terminology separate from product-level terminology.
   - For RTL target languages, set localization mode to `rtl-aware` by default unless the user explicitly requests copy-only layout preservation.

3. **Check terminology memory**
   - Read `$CODEX_HOME/skills/ad-image-localization/brand_term_memory.json` when available.
   - If the workspace has `.ad-image-localization/brand_term_memory.json`, prefer it for project-local rules.
   - Persist only user-approved rules, such as "translate X as Y" or "do not translate X".
   - If the current image appears to belong to a different brand/product family than the last task, warn the user and suggest starting a separate task/output folder before applying remembered terms.

4. **Generate model-native variants**
   - Use Codex built-in image generation/editing for translation, text replacement, layout reflow, and canvas extension.
   - For each language, prefer generating a strong anchor version first, then use it as the visual reference for the same language's other sizes.
   - For RTL languages, first attempt RTL-aware localization:
     - Adapt headline, body copy, CTA, and text blocks for right-to-left reading.
     - Prefer right alignment or RTL-friendly text grouping when it improves reading flow.
     - Adjust visual weight, information hierarchy, UI labels, dialogue bubbles, or local layout only when it improves natural RTL reading.
     - Do not mechanically mirror the whole design.
     - Do not flip logos, brand marks, product identity, or important brand recognition unless the user explicitly requests it.
   - For `16:9` sources that will feed `1200x628`, ask the model to keep important content away from the top/bottom edge.

5. **Post-process deterministically**
   - Use exact resize when the raw model output already matches the target aspect ratio.
   - Use cover-crop when the target ratio is close to a generated common ratio and the model output has safe margins.
   - Use model-generated canvas extension or reflow instead of blur padding when crop would remove important content.
   - Prefer the bundled helper for repeatable local operations:
     `python scripts/ad_image_localization_tools.py cover-crop <input> <output> --size 1200x628`.

6. **Export**
   - Default filename pattern:
     `<creative-name>_<language-or-locale>_<width>x<height>_<yyyymmdd>.<ext>`
   - Use lowercase English slugs for creative names.
   - Keep source files untouched.
   - Write a manifest when producing batches.
   - For batch folders, use the helper to write manifests:
     `python scripts/ad_image_localization_tools.py manifest <output-folder>`.

7. **QA**
   - Check dimensions, language, readability, crop safety, missing objects, malformed text, visual artifacts, and brand/product preservation.
   - For RTL outputs, judge whether the RTL-aware layout is natural, readable, balanced, and brand-safe.
   - If RTL-aware localization improves reading without hurting composition, keep it and tell the user RTL-aware localization was used.
   - If the RTL-aware version looks worse, such as unbalanced composition, damaged brand recognition, unnatural layout, or abnormal text flow, generate a fallback version using copy-only localization: translate visible copy but preserve the original overall composition and layout structure.
   - Compare the RTL-aware and copy-only fallback outputs; deliver the stronger version and state which mode was used.
   - Run Culture-Aware QA for each target language/market:
     - Look for plausible market-specific concerns in localized imagery, copy, symbols, maps, borders, gestures, clothing, religious references, food/animals, political context, regulated categories, social norms, and legal or platform sensitivities.
     - Use common knowledge, not a rigid blacklist. If the risk depends on current law, politics, platform rules, or a specific target market and you are uncertain, search the web and cite the source in the final notes.
     - If a creative has a reasonable risk, do not rewrite it by default. Move that creative's affected sizes into `Flagged by Culture-Aware QA/` inside the project output folder and tell the user to review or modify before launch.
     - If only one size reveals the issue because of cropping or layout, flag that size; if the issue is inherent to the creative/language/market, flag all sizes for that creative variant.
   - Use `verify` for filename/dimension checks and `contact-sheet` to create a visual QA sheet before final review.
   - If an output fails, regenerate or re-edit once.
   - If the second attempt still fails, deliver the best available output only with a clear warning.

## Culture-Aware QA

Culture-Aware QA is a QA flagging step, not automatic creative editing and not legal advice. Use it to protect the user from obvious or plausible localization risks before media spend.

- Consider the target market, language, platform, product category, and the specific visual/copy context.
- Flag risks such as religious sensitivity, restricted symbols, disputed maps or borders, political references, culturally sensitive animals or food, gestures, alcohol/gambling/medical/financial claims, modesty norms, or local advertising restrictions when they are relevant to the target market.
- Do not maintain or apply a hard-coded blacklist. Judge the actual creative in context.
- When flagged, leave image content unchanged and move the files into `Flagged by Culture-Aware QA/` with a short reason. Do not alter the image unless the user explicitly asks for a safer revision.
- Tell the user which files were flagged, why, and that they should confirm locally before launch.

## RTL-aware Localization

RTL-aware is the default attempt for RTL languages, with fallback to copy-only localization when QA judges the adapted layout to be worse.

- **Option A: RTL-aware enabled**: default for Arabic and other RTL languages. Adapt visible copy, alignment, local text grouping, CTA flow, and limited UI/dialogue layout for right-to-left reading when it benefits readability and native feel.
- **Option B: RTL-aware disabled / fallback**: translate visible copy only and preserve the original layout structure when RTL layout adaptation reduces quality.

Use RTL-aware adaptation as a reading-flow improvement, not as a blanket mirror operation. Preserve logos, brand identity, product imagery, and recognizable campaign structure unless the user asks otherwise.

## Bundled Helper Script

Use `scripts/ad_image_localization_tools.py` only for deterministic last-mile work. It does not call image APIs and does not replace Codex built-in image generation.

```bash
python scripts/ad_image_localization_tools.py cover-crop in.png out.jpg --size 1200x628
python scripts/ad_image_localization_tools.py manifest localized_output/
python scripts/ad_image_localization_tools.py verify localized_output/
python scripts/ad_image_localization_tools.py contact-sheet localized_output/ qa_contact_sheet.jpg
python scripts/ad_image_localization_tools.py flag-culture-aware localized_output/ rabbit-social-networks_ar_1200x628_20260622.jpg --market "GCC" --reason "Animal/food symbolism may need local review"
python scripts/ad_image_localization_tools.py memory-add brand_term_memory.json --brand openai --term Codex --action preserve
```

The helper expects Pillow. In Codex desktop environments, use the bundled Python runtime when available; outside Codex, install Pillow locally if needed.

## Size Adaptation Rules

Use this priority order:

1. **Generate the requested aspect ratio natively** when text, products, faces, logos, or UI are near edges.
2. **Generate the closest common ratio with safe margins, then cover-crop** when the target is close to a standard format.
3. **Use model-based canvas extension or layout reflow** when crop would damage important content.
4. **Use non-uniform resize only when explicitly requested or when distortion is visually negligible.**

Deterministic cover-crop:

```text
scale = max(target_width / source_width, target_height / source_height)
resized_width = round(source_width * scale)
resized_height = round(source_height * scale)
crop_left = (resized_width - target_width) // 2
crop_top = (resized_height - target_height) // 2
```

Example: `1920x1080` to `1200x628`

- Resize proportionally by width to `1200x675`.
- Crop `47` vertical pixels total.
- Default crop removes about `23` px from the top and `24` px from the bottom.
- If QA shows edge risk, regenerate the `16:9` image with stronger safe-margin instructions or shift the crop toward empty space.

The `cover-crop` helper implements this exact algorithm and reports the resized size and crop box for auditability.

## Terminology Memory

Recommended memory file:

```json
{
  "version": 1,
  "brands": {
    "openai": {
      "display_name": "OpenAI",
      "rules": [
        {"term": "OpenAI", "action": "preserve", "notes": "Brand name"}
      ],
      "products": {
        "codex": {
          "display_name": "Codex",
          "rules": [
            {"term": "Codex", "action": "preserve", "notes": "Product name"}
          ]
        }
      }
    }
  }
}
```

Brand rules apply to all products under the brand. Product rules override brand rules for that product.

## Default Sizes

- `1200x1200` square ad
- `1920x1080` landscape / 16:9
- `1080x1350` portrait feed / 4:5
- `1080x1920` story / 9:16
- `1200x628` social link/feed ad

## Usage Examples

- "Localize this game ad into German, French, Spanish, Japanese, and Korean, then export the common ad sizes."
- "Localize this poster into Arabic. Try RTL-aware layout adaptation first; if QA shows it hurts the composition, fall back to copy-only localization."
- "把这张图里的所有文字翻译成葡萄牙语，品牌名不要翻译，输出 `1200x1200`、`1080x1920` 和 `1200x628`。"
- "Generate `1200x628` from the 16:9 version with safe cropping. Do not stretch the image."
- "Remember that this product name should stay in English for this brand."

## Limitations

- Built-in image generation can still distort small text, logos, hands, faces, or dense UI.
- Exact font matching is best-effort unless editable source files or fonts are provided.
- Large batches should be processed in smaller groups so QA remains reliable.
- Codex built-in image generation currently has no stable user-controlled concurrency setting; prefer correctness over speed.
