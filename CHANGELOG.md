# Changelog

## Bilingual UI and documentation update — 2026-10-29

- Added French/English desktop language selector in the application header.
- Added `kolor_i18n.py` with translations for all 38 role names, their actions and objects, color-preset and skin-tone names, common dialogs, labels and status messages.
- Saved UI language in `projet/preferences.json`, without altering role IDs or asset manifest schemas.
- Added English `README.md` and English Markdown wiki with eight topic pages and optional GitHub Wiki navigation snippets.
- Added automated language/persistence/translation tests; existing 38 roles, palettes, and source assets retained.
- Kept independent skin tones, multicolor clothing/accessory choices, and locked exact black line art/white background.

This release does not modify the image-generation prompts (French), CLI command names or separate Kolor application code.
