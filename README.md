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
- Style reference: Tip the Can's hero kid, asset `f2288672-913a-4a2e-9a9a-37b473507d60`.
- Light: low warm sun from the upper left (golden hour). Tip the Can's last-light shader takes
  it to dusk; Kerby uses it as is.
- No black outlines on environment art. One painted shadow shape, lower right.
- Authored at 128 px per Tip the Can tile.

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

Each game pulls this repo in as a git submodule at `addons/street_kit/`:

```
git submodule add https://github.com/danbhala/street-kit addons/street_kit
```

Godot then sees the files as `res://addons/street_kit/...`. Update with
`git submodule update --remote addons/street_kit` and commit the new pointer.

## Asset list and plan

See the Street Kit asset list doc:
https://claude.ai/code/artifact/773ae55b-0b3c-462c-ad6a-3e39223edf53
