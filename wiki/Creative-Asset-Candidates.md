# Creative asset candidates for UCKK (draft only)

Kolor retains its existing `kolor.studio.export/1` and all historical Ekole/Kontexte paths. Whenever a local export is generated, it additionally creates `projet/exports/creative-candidates.json` in the **proposed** `koa.creative-asset-candidates/draft-1` format. This file is an **editorial review proposal**, not a publication or an integrated UCKK import.

Each available role contains its stable `visual_id`, French title, selected variant, palette and skin-tone identifiers, and SHA-256 checksums for **the actual exported colored compatibility and native PNG files**. The legacy technical-color source PNGs are left unmodified. If Kolor marked a pose as reviewed, `studio_review=reviewed`; that **does not** mean UCKK has approved it. Every row has `uckk_review=pending`, `rights.status=unverified`, and no invented license or attribution.

To use a candidate, manually provide `creative-candidates.json` plus referenced PNGs to an authorized UCKK reviewer. The reviewer must verify all file hashes, establish rights and attribution, and decide the destination and audience before any material is imported into UCKK's asset library or a course. Unknown rights, a failed image review or mismatched bytes block publication. `UCKK-Assets/Integrations/creative-assets/README.md` specifies the receiving owner's manual review process.

The proposal is additive. Existing `manifest.json`, PNG dimensions, review UI, CLI command names and `planches_ekole` sheets are unaffected. No automatic write occurs in another repository. Use `python -m unittest discover -s tests -v` for local checks.
