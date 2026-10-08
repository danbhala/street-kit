# Street Kit

Shared art (and, later, shared code) for Dan's British street games:

- [Tip the Can](https://github.com/danbhala/tip-the-can-game): top-down, tilted
- [Kerby](https://github.com/danbhala/kerby-game): side-on, about 20° down

Both games are set on the same 1990s British suburb and painted in the same flat-gouache
picture-book style with SpriteCook. Anything that looks right from both cameras lives here,
so it is painted once.

## The one rule: front elevations or top-down decals

The two games look at the street from different angles, so shared art must be one of:

- **Front elevation:** seen straight-on, cut out on transparent, no ground plane
  (house fronts, walls, hedges, fences, gates, lamp posts, garages, trees, vans, shop fronts).
  Kerby stacks them as parallax layers; Tip the Can uses them as the front faces of tall tiles,
  its sky band, title screen and street map.
- **Top-down decal or tiling texture:** seen from directly above (hopscotch, drain covers,
  puddles, pavement). Kerby foreshortens them through `Polygon2D` UVs.

Anything drawn in three-quarter view belongs to one game only and stays in that game's repo.
Characters and UI stay in each game too.

## House style

- SpriteCook project `a15fc08b-1b06-4d31-a11b-e12f2be148f0`, model `gemini-nano-banana-2.1`,
  `pixel=false`, 1K.
- Style references: Tip the Can's hero kid (`f2288672-913a-4a2e-9a9a-37b473507d60`) and,
  for elevations, the red-brick semi (`dea237b6-43e8-4104-acc2-c94451977ee7`).
- Light: neutral warm daylight from the upper left, no baked time of day. Each game grades it:
  Kerby with its golden-hour modulate, Tip the Can with its last-light tint.
- No baked cast shadow, only a soft self-shadow on the right; each game draws its own shadow.
  No black outlines.
- Shared palette hexes for shared materials (listed in `manifest.json`).

These rules match section 9 of Kerby's `ART_DIRECTION.md`.

Docs site: **https://danbhala.github.io/street-kit/** (built from `manifest.json` on every
merge to main).

## Painting new assets

This repo has the SpriteCook connection (`.mcp.json`, key from `SPRITECOOK_API_KEY`) and the
`street-kit-art` skill, so a Claude session here can paint the kit directly. Every planned
asset in `manifest.json` already has its output files listed; paint the raw, then run
`python3 tools/process_spritecook.py <raw_dir>`, which writes the files and fills in sizes and
hashes. `python3 tools/process_spritecook.py --check` verifies every shipped file.

## Layout

```
art/elevations/   front-on, transparent PNGs
art/decals/       top-down decals
art/textures/     top-down tiling textures
art/fx/           particle and effect textures
fonts/            shared OFL fonts (with licences)
tools/            processing scripts
manifest.json     every asset: SpriteCook id, prompt, outputs, which games use it
```

## Using it in a game

Street Kit ships as versioned GitHub Releases, each with one `street-kit.zip`. Every game
keeps a committed copy in `addons/street_kit/` and upgrades on purpose:

```
tools/update_street_kit.sh 0.2.0     # a specific version
tools/update_street_kit.sh           # the latest release
```

The script downloads that release, replaces `addons/street_kit/` with it, and leaves
`addons/street_kit/VERSION` saying which version is installed. Godot sees the files as
`res://addons/street_kit/...`. After running it: import (`godot --headless --import --path .`),
check the game, and commit `addons/street_kit/` including the new `.import` files.

No submodules and no package tokens: the files live in each game's repo, so exports and CI
need no extra step.

## Releasing

Add a `## [x.y.z]` section at the top of `CHANGELOG.md` in your PR (rules for picking the
number are at the top of that file). When the PR is merged, the Release workflow tags `vx.y.z`
and publishes `street-kit.zip`.

## Asset list and plan

See the Street Kit asset list doc:
https://claude.ai/code/artifact/773ae55b-0b3c-462c-ad6a-3e39223edf53
