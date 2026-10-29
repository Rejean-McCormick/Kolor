# Command-Line Reference

Run commands from the extracted `Kolor_Studio` directory. The CLI's command names remain in French for backward compatibility, even when the desktop UI is set to English.

```powershell
py Kolor_Studio_CLI.py <action> [options]
```

| Action | Purpose |
| --- | --- |
| `etat` | Show number of imported and approved roles |
| `palettes` | List available palette and skin-tone IDs |
| `prompts` | Write 38 French technical prompts to `projet/prompts/` |
| `importer-dossier` | Import files from a directory (`<role-id>.png`) |
| `choisir-palette` | Assign palette and skin tone to one role |
| `choisir-couleur` | Override or reset a non-skin channel |
| `exporter` | Create all exports and manifests |

## Examples

```powershell
py Kolor_Studio_CLI.py etat
py Kolor_Studio_CLI.py palettes
py Kolor_Studio_CLI.py prompts
py Kolor_Studio_CLI.py importer-dossier "C:\mycode\Ekole\Kolor\source"
py Kolor_Studio_CLI.py importer-dossier "C:\mycode\Ekole\Kolor\source" --ecraser
py Kolor_Studio_CLI.py choisir-palette --role pecheur --palette ocean --skin-tone caramel
py Kolor_Studio_CLI.py choisir-couleur --role pecheur --region haut --hex '#E97B35'
py Kolor_Studio_CLI.py choisir-couleur --role pecheur --region haut --hex RESET
py Kolor_Studio_CLI.py exporter
```

`--projet` selects another project folder. `--ecraser` allows reimport of existing sheets. For `choisir-couleur`, available regions are `cheveux`, `haut`, `bas`, `chaussures`, and `accessoires`. The skin color is controlled with `--skin-tone`, not `--region peau`. `RESET` removes a region's custom override.

## Safety and automation

- CLI imports do not call the image-generation API.
- CLI exports do not modify source PNGs.
- Reimport of a source sheet resets that role's reviewed status.
- Pure black and white are locked, including from the CLI.
- CLI output and action names currently remain French; the `Français / English` setting applies to the **desktop UI**.

Next: [Bilingual Interface](Bilingual-Interface.md).
