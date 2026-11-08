# Upstream documentation (reference only)

These files are the original READMEs and changelog of the two merged packs:

- `UPSTREAM-GH-README.md` — Goohai MiniMax H3 Integration
- `UPSTREAM-RefMod-README.md` / `UPSTREAM-RefMod-CHANGELOG.md` — ComfyUI-MiniMaxH3Mod

They describe the individual node sets in detail. Some statements no longer match
the merged pack:

- `Load H3 RefMods` still exists, but the integrated node now embeds its role
  (RefMod rows auto-bound to `<Video n>` plus one merged `mods` output);
- the RefMod examples folder and the bundled `vanellope_example.safetensors`
  are not shipped here;
- file paths that point at `ComfyUI-MiniMaxH3Mod/...` map to `refmod/...` in
  this pack (and the GH files map to `gh/...`).

## Pack-specific documents

- `LONG_VIDEO_SEGMENTS_DESIGN.md` — design for the 8-segment long-video
  continuation mode (UI, `segments` output, runner node, wiring).

