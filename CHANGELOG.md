# Changelog

Each `## [x.y.z]` heading is a release. Merging a PR that adds a new heading at the top
publishes that version (see `.github/workflows/release.yml`).

Versioning for art:

- **Major**: an asset is removed or renamed, or its size or anchor changes. Games must be checked before upgrading.
- **Minor**: new assets added. Safe to upgrade.
- **Patch**: an existing asset repainted with the same file name, size and anchor. Safe to upgrade.

## [1.0.0]

Major because one file changes size: **`art/elevations/lamp_post_lit.png` is now 160x617
(was 160x638).** Check the lit lamp in Tip the Can and Kerby before upgrading. It is anchored
bottom-centre, so a game that places it by its foot sees the lamp head drop 21 px to where the
unlit lamp's head is; a game that positions it by its centre or top must adjust.

- The lit lamp post is now exactly the unlit one's size. SpriteCook painted it about 3% taller;
  processing now scales it to match (`same_size_as` in `manifest.json`), so switching the lamp
  on no longer makes it jump.
- Hopscotch fixed: the numbers now read 1, 2, 3, 4|5, 6, 7|8, 9 instead of repeating 7. Repainted
  as a SpriteCook edit of the old sheet (12 credits); same size (256x346), same slabs and chalk.
- The seven tiling strips no longer show a see-through ghost where they repeat. Processing used
  to fade the strip's two ends through each other, which left half-visible chimneys, windows
  and doors at the join; it now cuts from one end to the other along the line where they match
  best, with the strip's window moved (and stretched by at most 4%) to where the ends line
  up. Same sizes, no new painting:
  `terrace_row_brick`, `terrace_row_render`, `roofline`, `garden_wall`, `privet_hedge`,
  `closeboard_fence`, `garage_row`.

## [0.8.0]

- Three paintings from Kerby's second SpriteCook batch, in `art/elevations/`: a family hatchback
  seen side-on facing right (`car_escort.png`, 520x217, no badges or plate), and two kerb strips
  painted as edits of the granite kerb with the same layout, so they line up with it:
  concrete (`kerb_concrete.png`, 512x160) and a dropped kerb for driveways (`kerb_dropped.png`,
  512x168). Both kerbs tile left to right.
- Font: Bangers, a comic display face, with its OFL licence (`fonts/Bangers-Regular.ttf`).
- Kerby uses all four. Nothing existing changes.

## [0.7.0]

- The back-lane tarmac no longer has to repeat its patches. New `art/textures/lane_tarmac_plain.png`
  (512x512, tiles on both axes) is the same painting with its three patch repairs and one faint dark smudge lifted out, and
  the two big patches are now decals in `art/decals/` (`tarmac_patch_dark.png`,
  `tarmac_patch_grey.png`, centre anchor, at the texture's scale) to scatter over it at any angle.
  `lane_tarmac.png` is unchanged.
- No new SpriteCook run: `tools/process_spritecook.py --derive` makes all three from
  `lane_tarmac.png`. Their boxes are tied to that painting, so a raw run that rewrites it lists
  them to check rather than rebuilding them.

## [0.6.0]

- Two seamless ground textures for back lanes, seen from directly above, in `art/textures/`
  (512x512, tile on both axes): grey-brown pea gravel (`gravel.png`) and worn back-lane tarmac
  with patches and cracks (`lane_tarmac.png`). Painted to sit next to Tip the Can's pavement
  tile; Tip the Can uses them for street two, the lane behind the houses.
- Known flaws: the gravel's cross-faded tile edges are a little softer than its middle, and the
  tarmac's three patches repeat visibly every 512 px.

## [0.5.0]

- Two paintings from Kerby's SpriteCook batches: a distant roofline silhouette
  (`art/elevations/far_roofs.png`, a soft mauve band behind the detailed roofline) and a granite
  kerb section (`art/elevations/kerb_granite.png`, Kerby's gameplay strip, seen 20° down).
- Kerby's copy of the red-brick semi wasn't added: it's the same SpriteCook painting as
  `semi_house_red_brick.png`, which shipped in 0.2.0.
- This is the first published release. Versions 0.2.0 to 0.4.0 were never tagged, because they
  were merged before the release workflow reached main; everything they list is in this zip.

## [0.4.0]

- Ground decals: hopscotch (chalk on a patch of paving slabs), cast-iron drain cover and puddle,
  in `art/decals/`. This completes the planned kit.
- Known flaw: the hopscotch numbers repeat 7 where the right-hand square should be 8.

## [0.3.0]

- Painted the rest of the planned kit (16 assets, 17 files, all front elevations):
  - Houses and backdrop: pebble-dash semi, brick and rendered terrace rows, bungalow, roofline.
  - Street furniture: garden wall, privet hedge, close-board fence, wooden and iron gates, lamp
    post (unlit and lit), lock-up garage row.
  - Dressing: laburnum and lime street trees, ice-cream van, corner shop.
- Strips (terraces, roofline, wall, hedge, fence, garages) tile left to right.
- Each new output records its own SpriteCook asset id and prompt in `manifest.json`.
- Not in this release: the ground decals (hopscotch, drain cover, puddle), which ship in 0.4.0.

## [0.2.0]

- First paintings: the red-brick semi-detached house front (painted in Kerby's test batch) and
  the picket fence (painted for Tip the Can). Both games already use copies of these.
- Fonts: Fredoka and Cabin Sketch Bold, with their OFL licences.
- The manifest now lists the whole planned kit, with each file's planned path and width, and
  the shared palette.

## [0.1.0]

- First release: folder layout, house rules and an empty manifest. No art yet; lets the games
  install the kit and test their update script.
