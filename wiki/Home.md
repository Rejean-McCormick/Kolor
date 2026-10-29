# Kolor Studio — Wiki

Kolor Studio is a desktop tool for producing and managing **38 character roles** for Kolor and the Ekole / Kontexte legacy catalog. Each character is shown four times on a single square sheet; skin tone and clothing/accessory colors can be changed independently while black outlines remain black.

**UI languages:** French and English (select in the top-right corner). **Documentation language:** English.

## Navigation

1. [Getting Started](Getting-Started.md) — install, launch and first export.
2. [Bilingual Interface](Bilingual-Interface.md) — switch languages and understand persistent settings.
3. [Character Sheets](Character-Sheets.md) — 2 × 2 layout, crop behavior and source colors.
4. [Palettes and Skin Tones](Palettes-and-Skin-Tones.md) — mixed-color clothes, independent skin tones and locked line art.
5. [Exports and Integration](Exports-and-Integration.md) — output directories, manifests and legacy dimensions.
6. [Command-Line Reference](Command-Line-Reference.md) — import, export, preset and per-channel commands.
7. [Troubleshooting](Troubleshooting.md) — common setup and artwork issues.

## Key principles

- **Identity consistency:** the four images are the same character in different poses.
- **Resolution independence:** source sheets use a square 1:1 aspect ratio; pixel dimensions are not specified in prompts.
- **Non-destructive workflow:** originals are retained; previews and exports use selected colors.
- **Color isolation:** skin, hair, top, bottom, shoes, and accessories have separate technical region codes.
- **Outlines stay black:** exact `#000000` pixels and exact white background pixels `#FFFFFF` are preserved.
- **Review is still required:** import and color checks do not replace visual quality review.

## Where the data lives

- `data/roles.json`: the canonical 38 role identifiers.
- `data/palettes.json`: editable palette and skin-tone presets.
- `projet/etat.json`: per-role pose selection, review and color settings.
- `projet/preferences.json`: chosen UI language.
- `projet/exports/`: outputs for other apps.

Return to [README](../README.md).
