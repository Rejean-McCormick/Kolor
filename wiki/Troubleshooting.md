# Troubleshooting

## The app does not open

Make sure Python 3 and Pillow are installed. Try running `py Kolor_Studio.pyw` from a command prompt in the `Kolor_Studio` directory to see diagnostic output. Use `py -m pip install -r requirements.txt` if Pillow is missing.

## A file is rejected as non-square

The imported sheet must have a **1:1 aspect ratio**, but it does **not** need to be 1024 × 1024 pixels. An odd-sized square is padded by one white pixel on the right and bottom. Non-square images are rejected rather than stretched.

## Some content overlaps a cell border

Keep each full character inside its own quadrant with **at least 6.25% white margin within each cell**. After import, inspect all four cropped poses. The app cannot reliably reconstruct limbs or props already drawn outside a quadrant.

## Skin tone changes my outfit

Skin tone is designed to change only the skin region, while the palette controls hair, top, bottom, shoes and accessories. If the generated sheet misuses the technical region codes, the program may not be able to separate these regions. Compare against **Show original technical colors**.

## Black outlines or the background look different

Exact `#000000` source pixels remain black and exact `#FFFFFF` source pixels remain white. Anti-aliased pixels and imported images with nontechnical colors may have intermediate values; inspect native exports at full zoom. Custom fill colors cannot be pure black or pure white.

## I changed a palette but my export did not update

The preview updates immediately. Click **Export for Kolor / Kontexte** to regenerate output files. Changing a palette may also clear the **reviewed** flag for that role.

## The interface starts in French

French is the default. Use the upper-right **Langue** selector to choose **English**. Preferences are saved in `projet/preferences.json`. If you want to reset the language, set `"language": "fr"` in that file or remove it.

## I cannot access a file in another Kolor application

This Studio archive does not install files into an external Kolor project or modify its application code. Export files are available under `projet/exports/`; copy/integrate them according to the destination project's conventions.

## Image generation fails

The API key is optional and not stored by Kolor Studio. Check that your key is valid, the selected image model is available to your API account and your network is connected. API usage is billed separately. You can always import an already generated square sheet instead.

Back to [Wiki Home](Home.md).
