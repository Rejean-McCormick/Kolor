# Getting Started

## Requirements

- Windows with Python 3 installed.
- Pillow (installed via `INSTALLER_ET_LANCER.bat` or `py -m pip install -r requirements.txt`).
- An OpenAI API key is **optional**, only for the paid image-generation feature.

## Installation

1. Extract `Kolor_Studio` from the ZIP. Do not scatter its files across other directories.
2. Run `INSTALLER_ET_LANCER.bat`, or run `py Kolor_Studio.pyw` after installing requirements.
3. Choose **Français** or **English** in the header.
4. Select any role from the left-hand list. The complete distribution includes 38 imported sheets and 152 technical poses.

## Work with a role

1. Inspect the square sheet and the four pose thumbnails in the center.
2. Select the desired pose: **Main**, **Greeting**, **Accessory** or **Action**.
3. In the right panel, choose a multicolor palette and a separate skin tone.
4. If needed, click a color swatch (hair/top/bottom/shoes/accessories) to pick a custom HEX color. Skin is controlled by the skin-tone menu.
5. Check **I have reviewed this character** after verifying the drawing.
6. Click **Export for Kolor / Kontexte**. The application writes recolored results and the manifest to `projet/exports/`.

Changing a pose or color resets review for that role. Review it again before publishing.

## Import your own 2 × 2 sheet

Choose a role, click **Import a PNG sheet…**, and select a square PNG, JPEG or WebP file. The source must have a 1:1 aspect ratio; no arbitrary resolution is required. Kolor Studio splits it at 50% of width and height into four equal square cells and recenters content with an internal safety margin.

If the image side length is odd, the tool adds one white pixel to the right and bottom before splitting (to avoid unequal halves). It does not reduce the imported sheet to 1024 pixels.

## Generate new sheets (optional)

Use **Copy role prompt** to copy a prompt for an external generator, or provide your own API key and click **Generate this role**. The application does not save your API key. Generation can incur separate usage fees. Generated prompts remain in French because their technical structure has not been translated.

Next: [Bilingual Interface](Bilingual-Interface.md) or [Palettes and Skin Tones](Palettes-and-Skin-Tones.md).
