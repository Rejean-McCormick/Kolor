# Palettes and Skin Tones

Kolor Studio ships with **13 palettes** (12 multicolor presets plus the technical default) and **12 skin tones** (11 natural tones plus technical yellow). These are independent selections. The 38 roles have varied default combinations, but a saved user choice always takes precedence.

## Independent color channels

Each role can use a different color for:

- **Skin:** selected from skin tones only.
- **Hair:** individual HEX override or palette default.
- **Top:** individual HEX override or palette default.
- **Bottom:** individual HEX override or palette default.
- **Shoes:** individual HEX override or palette default.
- **Accessories:** individual HEX override or palette default.

The **Generate multicolor combination** button chooses independent colors for the five non-skin channels without changing the current skin tone. **Reset custom colors to palette** removes individual overrides and keeps the selected skin tone.

## Permanent safety rules

**Pure black `#000000` belongs to line art and never changes. Pure white `#FFFFFF` belongs to the background and never changes.** Neither can be chosen as a custom fill color. The technical-color PNG sheets and poses remain stored separately and are not overwritten by a palette selection.

Colors are chosen for **each character**. Selecting a different role restores that role's saved colors. Color changes clear its approval status until reviewed again.

## Edit or extend preset catalogs

Edit `data/palettes.json` (UTF-8). The catalog contains `palettes` (each with `id`, `nom`, `cheveux`, `haut`, `bas`, `chaussures`, `accessoires`) and `carnations` (each with `id`, `nom`, `couleur`). Keep stable ASCII IDs and `#RRGGBB` colors. To add an English label for a new preset, add its ID to `PALETTE_EN` or `SKIN_EN` in `kolor_i18n.py`, then restart the application.

Example palette entry (illustrative only):

```json
{
  "id": "custom-bright",
  "nom": "Palette vive",
  "cheveux": "#684132",
  "haut": "#F37A32",
  "bas": "#3877C9",
  "chaussures": "#D94A7F",
  "accessoires": "#4BBE82"
}
```

The palette catalog is copied to `projet/exports/palettes.json` when exporting. Per-role overrides appear in `projet/etat.json` as `couleurs_libres` and in the export manifest as `couleurs_personnalisees`.

## Preview versus export

**Show original technical colors** is only a preview comparison mode. It does not change the selected export palette. To update exported images after any color change, run **Export for Kolor / Kontexte** again.

Next: [Exports and Integration](Exports-and-Integration.md).
