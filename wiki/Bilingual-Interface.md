# Bilingual Interface (French / English)

Use the **Langue / Language** selector in the upper-right corner of Kolor Studio. Choose **Français** or **English**. The visible UI is rebuilt in the selected language without restarting the application.

## What changes

- Navigation headings, buttons, checkboxes and status messages.
- All 38 role display names, including **Pêcheur → Fisherman** and **Sorcière → Witch**.
- Role descriptions (actions and objects).
- Palette and skin-tone display names.
- Dialogs for importing, generating, reviewing and exporting.
- Quality notices commonly shown beneath the pose thumbnails.

## What stays stable

- Role IDs such as `pecheur` and `createur-jeux`.
- Palette IDs such as `ocean`, `technique` and `arc-en-ciel`.
- Region keys such as `haut`, `bas`, `chaussures` and `accessoires`.
- JSON field names, file paths, command-line action names, and source generation prompts.

These identifiers are **intentionally not translated** to avoid breaking saved styles, external manifests, scripts or existing asset references. The CLI is not a separate localized UI.

## Persistence

The language choice is written to `projet/preferences.json`:

```json
{
  "language": "en"
}
```

Use `"fr"` for French or `"en"` for English. If the file is missing or invalid, the application starts in French. Changing the language does not modify `projet/etat.json` or the role assets.

## Adding translations

`kolor_i18n.py` contains UI text, role-display translations, actions and objects, palette names and skin-tone names. New text should be added to `EN`. Keep `data/roles.json` and `data/palettes.json` IDs unchanged. The French text is used as the default translation key.

Next: [Character Sheets](Character-Sheets.md).
