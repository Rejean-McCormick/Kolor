# Kolor Studio

**Bilingual (French / English) character production studio for Kolor and Ekole / Kontexte.**

Kolor Studio manages **38 character roles**, each represented by one square **2 × 2 pose sheet** (four poses of the same character). The included distribution contains 38 imported source sheets, 152 cropped poses, per-role color presets, and exports for the historical Kontexte / Ekole asset layout.

The interface supports **Français** and **English**. Select the language using the menu in the upper-right corner. The choice is saved locally in `projet/preferences.json`. Technical file names, role IDs and exported JSON fields do not change when you switch languages.

## Quick start (Windows)

1. Extract the ZIP, keeping the `Kolor_Studio` folder intact.
2. Run **`INSTALLER_ET_LANCER.bat`** (Python 3 is required; the script installs Pillow for your user account).
3. Use the **Français / English** selector in the header.
4. Select a role from the left panel. The center panel shows the sheet and its four poses.
5. In **Palettes and skin tones**, choose a multicolor palette and a separate skin tone. Click a hair/top/bottom/shoes/accessories swatch to customize that channel independently.
6. Review the artwork, choose a pose, mark it as reviewed, then click **Export for Kolor / Kontexte**.

Alternatively, with Python and Pillow already installed:

```powershell
py -m pip install -r requirements.txt
py Kolor_Studio.pyw
```

> API image generation is **optional**. It requires your own API key and may incur separate costs. Existing images can be imported without an API key.

## What remains locked

- **Black outlines and black line art:** `#000000` — never recolored.
- **White background:** `#FFFFFF` — never recolored.
- **Skin tones:** selected independently from clothes, hair, shoes and accessories.
- **Source sheets and cropped technical poses:** retained without color replacement; recoloring is done for previews and exports.

All generated prompts use the six technical region colors: skin `#FFFF00`, hair `#FF0000`, top `#00FF00`, bottom `#0000FF`, shoes `#FF00FF`, and accessories `#00FFFF`. The specific target colors come from the chosen palette/skin tone. **No additional image pixel size is imposed in the prompts:** only the **1:1 sheet aspect ratio**, a **2 × 2 layout** and a **6.25% internal safety margin per cell**. A fixed **512 × 512** size is used *only* for compatibility exports to the historical Kontexte/Ekole format.

## Project layout

| Path | Purpose |
| --- | --- |
| `Kolor_Studio.pyw` | Desktop interface, in French and English |
| `kolor_i18n.py` | UI text translations and language preferences |
| `Kolor_Studio_CLI.py` | Command-line import, presets and export |
| `data/roles.json` | 38 canonical role IDs and source metadata |
| `data/palettes.json` | Color presets and skin-tone catalog |
| `projet/planches/<id>.png` | Original 2 × 2 sheet, at its imported resolution |
| `projet/variantes/<id>/01.png` – `04.png` | Four source poses |
| `projet/etat.json` | Saved role selections, review state and colors |
| `projet/preferences.json` | UI language preference (`fr` or `en`) |
| `projet/exports/images/roles_natifs/` | Recolored chosen poses at original resolution |
| `projet/exports/images/roles/` | Recolored 512 × 512 historical-compatible poses |
| `projet/exports/images/roles_techniques/` | Technical-color 512 × 512 reference poses |
| `projet/exports/planches_ekole/` | Reassembled legacy catalog sheets |
| `projet/exports/manifest.json` | Per-role paths, colors and review status |
| `projet/exports/creative-candidates.json` | Additional proposed UCKK review candidates with exported PNG hashes and unverified rights |
| `projet/exports/palettes.json` | Palette catalog copied alongside exports |
| `wiki/` | English-language project wiki (Markdown) |

## Command line

The CLI uses stable French action names to preserve compatibility with prior scripts:

```powershell
py Kolor_Studio_CLI.py etat
py Kolor_Studio_CLI.py palettes
py Kolor_Studio_CLI.py importer-dossier "C:\mycode\Ekole\Kolor\source"
py Kolor_Studio_CLI.py choisir-palette --role pecheur --palette ocean --skin-tone caramel
py Kolor_Studio_CLI.py choisir-couleur --role pecheur --region haut --hex '#E97B35'
py Kolor_Studio_CLI.py exporter
```

See [Command-Line Reference](wiki/Command-Line-Reference.md) for options and details.

## Documentation (English wiki)

Start at **[Wiki Home](wiki/Home.md)**, or jump to [Getting Started](wiki/Getting-Started.md), [Bilingual Interface](wiki/Bilingual-Interface.md), [Character Sheets](wiki/Character-Sheets.md), [Palettes and Skin Tones](wiki/Palettes-and-Skin-Tones.md), [Exports and Integration](wiki/Exports-and-Integration.md), [Command-Line Reference](wiki/Command-Line-Reference.md), or [Troubleshooting](wiki/Troubleshooting.md).

The wiki pages are written as standalone Markdown so they can also be copied into a GitHub Wiki repository if you maintain one. **This ZIP does not publish them to GitHub.**

## Tests

```powershell
py -m unittest discover -s tests -v
```

The tests use local fixtures and make no billable image API calls. The 38 bundled roles may still need human visual inspection before publication: automated quality checks are only heuristics.

## Compatibility and limitations

- Language switching changes the **desktop UI**, not the French technical-generation prompts, CLI command names, role IDs or exported schema.
- A source image with incorrect technical colors may recolor ambiguously (for example, red used for both hair and a mouth). Always review the output.
- The application prepares files for another Kolor / Kontexte project, but does not automatically edit that separate application's source code.
- Keep a backup of your `projet/` directory before applying updates to an older installation.

## UCKK asset review proposals (optional)

The same manual local export produces an additional **candidate-only** index. It does not assign rights, copy files to UCKK or modify a Kontexte/Ékole project. See [Creative Asset Candidates](wiki/Creative-Asset-Candidates.md). The receiving UCKK-Assets owner decides institutional/content admission separately.
