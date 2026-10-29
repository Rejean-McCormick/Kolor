# Exports and Integration

Kolor Studio prepares export assets for the historical Ekole / Kontexte catalog while preserving full-resolution project sources. Exports are made on demand using the button in the desktop UI or `py Kolor_Studio_CLI.py exporter`.

## Output locations

| Directory or file | Contents |
| --- | --- |
| `projet/planches/<id>.png` | Original imported 2 × 2 sheet, unmodified |
| `projet/variantes/<id>/01.png` … `04.png` | Cropped technical poses |
| `projet/exports/images/roles_natifs/<id>.png` | Selected pose, recolored, native pose resolution |
| `projet/exports/images/roles/<id>.png` | Selected pose, recolored, legacy **512 × 512** resolution |
| `projet/exports/images/roles_techniques/<id>.png` | Selected original technical pose, legacy resolution |
| `projet/exports/planches_ekole/roles-01.png` … `roles-05.png` | Reassembled historical role catalog sheets |
| `projet/exports/apercu_roles.jpg` | Contact sheet for visual quality review |
| `projet/exports/manifest.json` | Export paths, role IDs, palette settings and review flags |
| `projet/exports/palettes.json` | Snapshot of palette and skin-tone presets |

## Manifest compatibility

The manifest uses `kolor.studio.export/1` and contains `roles`, `exportes`, `attendus`, `a_verifier` and `planches_ekole`. Each role entry includes stable `visual_id`, output `chemin`, `chemin_natif`, `chemin_technique`, `statut`, `variante`, `palette_id`, `skin_tone_id`, `skin_tone_hex`, `couleurs` and `couleurs_personnalisees`.

The `statut` value is `pret` only after manual review in the studio; otherwise it is `a_verifier`. The interface can show English labels, but the manifest keys and status codes remain stable.

## Integrating into another application

Consume the exported PNGs and manifest according to the other application's directory and ID conventions. For a previously used project path such as `C:\mycode\Ekole\Kolor\source`, back up the destination before copying. Kolor Studio **does not automatically edit that other application's code or install exported images into it**.

Keep the source technical images if you want to change palettes in the future. Recoloring/export is designed to be non-destructive.

Next: [Troubleshooting](Troubleshooting.md).
