---
name: street-kit-art
description: Paint Street Kit assets (shared front elevations, decals and textures for Tip the Can and Kerby) with SpriteCook, process them into art/, and record them in manifest.json. Use for any new or repainted Street Kit asset.
---

# Painting Street Kit with SpriteCook

Use with `spritecook-workflow-essentials` and `spritecook-generate-sprites`. Read README.md's
"one rule" first: only front elevations, top-down decals and tiling textures belong here.

## Before spending anything

1. Credits are Dan's. Spend only on a batch he has said yes to; say the count and cost first.
2. `get_credit_balance` before and after every batch; report the spend and the balance.
3. If SpriteCook tools are missing, `SPRITECOOK_API_KEY` isn't set in this environment. Stop
   and tell Dan; never ask for the key in chat or write it anywhere.
4. Reuse before painting: an asset id already in `manifest.json` (or in Tip the Can's or
   Kerby's `art/spritecook-assets.json`) is reused, not regenerated.

## Costs (from Tip the Can's notes, 2026-10-08; confirm with `list_generation_models`)

| Job | Credits |
| --- | --- |
| Still, `gemini-nano-banana-2.1`, 1K | 12 per variation |
| Background removal | about 1 |

## House settings for every still

- `model="gemini-nano-banana-2.1"`, `pixel=false`, `resolution="1K"`,
  `project_id="a15fc08b-1b06-4d31-a11b-e12f2be148f0"`.
- `style_asset_ids=["f2288672-913a-4a2e-9a9a-37b473507d60", "dea237b6-43e8-4104-acc2-c94451977ee7"]`
  (Tip the Can's hero kid for the hand, the red-brick semi for elevation framing).
- `style`: "flat gouache picture-book illustration matching the style references: soft-edged
  flat colour fills with visible brush texture, warm neutral daylight from the upper left, a
  soft self-shadow on the right side only, no cast shadow, no black outlines".
- `colors`: the relevant hexes from `manifest.json` `palette` (brick `#B8614A`, brick shade
  `#7E3F3A`, cream render `#EADBC0`, hedge `#3E6B4A`, hedge lit `#6E9460`, fence wood
  `#8C6A4A`, kerb `#E6DCCB`, chalk `#F3EEE2`).
- Every elevation prompt ends: "Seen straight-on from the street, flat front elevation, not
  angled. Only this, no ground, no pavement, no people, transparent background."
- Strips that must tile: "one long straight horizontal run filling the whole width and
  continuing past both edges, evenly lit, no ends or corners".
- Several small things on one sheet: "N separate ... in a single row with wide empty space
  between them, not touching"; `tools/process_spritecook.py` slices them for free.
- Decals: "seen from directly above, flat, evenly lit, transparent background".

What failed before (Tip the Can): asking for a hedge or fence "in three-quarter view" gives
isometric blocks. Ask for the front elevation only.

## The planned kit (raw name → what to ask for)

Output paths, processing mode and width for each raw are already in `manifest.json`.

| Raw | Prompt subject |
| --- | --- |
| `semi_house_pebble_dash` | The same 1930s semi as the reference, but the whole front in cream pebble-dash render, white UPVC bay with net curtains, hipped slate roof, chimney |
| `terrace_row_brick` | A row of Victorian terraced houses in terracotta brick: sash windows, front doors in different colours, slate roof with chimney stacks along the ridge (strip) |
| `terrace_row_render` | The same terrace row with cream-rendered fronts and painted window surrounds (strip) |
| `bungalow` | A 1960s British bungalow: low hipped roof, picture window, porch, pebble-dash |
| `roofline` | Distant rooftops and chimney pots as a silhouette band, slate and brick tones, no windows (strip) |
| `garden_wall` | A low red-brick front-garden wall with a coping course (strip) |
| `privet_hedge` | A neatly clipped privet hedge, about waist high (strip) |
| `closeboard_fence` | A close-board wooden garden fence with concrete posts (strip) |
| `gates_sheet` | Two garden gates in a row: a wooden picket gate and a black wrought-iron gate |
| `lamp_post_unlit` | A grey 1970s concrete street lamp post with a sodium lantern, unlit |
| `lamp_post_lit` | The same lamp post with its sodium lantern glowing amber `#FFB347` (use the unlit one as a reference) |
| `garage_row` | A row of lock-up garages with up-and-over doors in faded colours (strip) |
| `tree_laburnum` | A laburnum street tree in yellow bloom |
| `tree_lime` | A lime street tree, full summer leaf |
| `ice_cream_van` | A 1990s British ice-cream van, side-on, cream and pastel livery, a cone on the roof, no brand names or text |
| `corner_shop` | A corner shop front: awning, window with posters (no readable text), door, flat above |
| `decals_sheet` | Three ground decals in a row, seen from above: a chalk hopscotch grid, a cast-iron drain cover, a shallow puddle |

Order Dan approved in the asset list doc: pilot `roofline` + one house first and check them in
both games; then houses and backdrop; then street furniture; then dressing.

## Processing and recording

1. Download each finished asset's `sprite_url` into a scratch folder as `<raw>.png`.
2. `python3 tools/process_spritecook.py <scratch_dir>` writes the outputs and fills `size`
   and `sha12` in `manifest.json`.
3. Look at every output (Read the PNG). Repaint anything with a ground plane, cast shadow,
   angled view or text.
4. In `manifest.json`: set the asset's `status` to `shipped`, `since` to the release version,
   and `spritecook.asset_id` and `spritecook.prompt`.
5. `python3 tools/process_spritecook.py --check`, add a CHANGELOG version (minor for new art),
   and open a PR with before/after images and the credits spent.
