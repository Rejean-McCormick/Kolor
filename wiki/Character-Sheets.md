# Character Sheets and Technical Colors

## One character, four poses

Each image is **one square sheet (1:1)**, mentally divided into **two equal rows and two equal columns**. Each quadrant covers 25% of the sheet. The same character appears once inside each quadrant:

| Position | Pose |
| --- | --- |
| Upper left | Main: welcoming, front view, full body and both hands visible |
| Upper right | Greeting: smiling and waving |
| Lower left | Accessory: shows an object characteristic of the role |
| Lower right | Action: demonstrates a role-related gesture |

The same age, facial features, hairstyle, proportions, clothes and accessories must be preserved in all four poses. The source prompt requests no grid, captions, textures, shadows or background scenery.

## Layout and cropping

The generator is constrained by **proportions**, not specific pixel dimensions. It leaves at least **6.25% white space on each side of each cell**. Import accepts a square sheet and crops at its midpoint; it does not rescale it to a fixed sheet size. Each cropped pose keeps its original quadrant dimensions; the cropping step may center and scale the character **within that quadrant** to achieve the white margin.

The only fixed-size output is the **historical-compatible 512 × 512 export**, not the source sheet or native exported pose.

## Six source color codes

| Technical region | Input HEX |
| --- | --- |
| Skin | `#FFFF00` (yellow) |
| Hair | `#FF0000` (red) |
| Top | `#00FF00` (green) |
| Bottom | `#0000FF` (blue) |
| Shoes | `#FF00FF` (magenta) |
| Accessories | `#00FFFF` (cyan) |
| Outlines / line art | `#000000` (black, fixed) |
| Background / eye whites | `#FFFFFF` (white, fixed) |

The six bright fill colors are **technical region markers**, not the final natural-colored rendering. See [Palettes and Skin Tones](Palettes-and-Skin-Tones.md) to recolor the final output.

## Important limitation

If a generator applies the same source code to more than one semantic region (such as the red hair code inside a mouth), recoloring cannot reliably distinguish those regions. Always visually inspect output.

Next: [Exports and Integration](Exports-and-Integration.md).
