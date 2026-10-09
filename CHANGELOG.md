# Changelog

Each `## [x.y.z]` heading is a release. Merging a PR that adds a new heading at the top
publishes that version (see `.github/workflows/release.yml`).

Versioning for art:

- **Major**: an asset is removed or renamed, or its size or anchor changes. Games must be checked before upgrading.
- **Minor**: new assets added. Safe to upgrade.
- **Patch**: an existing asset repainted with the same file name, size and anchor. Safe to upgrade.

## [0.7.0]

- The back-lane tarmac no longer has to repeat its patches. New `art/textures/lane_tarmac_plain.png`
  (512x512, tiles on both axes) is the same painting with its three patch repairs lifted out, and
  the two big patches are now decals in `art/decals/` (`tarmac_patch_dark.png`,
  `tarmac_patch_grey.png`, centre anchor, at the texture's scale) to scatter over it at any angle.
  `lane_tarmac.png` is unchanged.
- No new SpriteCook run: `tools/process_spritecook.py --derive` makes all three from
  `lane_tarmac.png`, and rebuilds them after every raw run.

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
