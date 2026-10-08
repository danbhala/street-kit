# Changelog

Each `## [x.y.z]` heading is a release. Merging a PR that adds a new heading at the top
publishes that version (see `.github/workflows/release.yml`).

Versioning for art:

- **Major**: an asset is removed or renamed, or its size or anchor changes. Games must be checked before upgrading.
- **Minor**: new assets added. Safe to upgrade.
- **Patch**: an existing asset repainted with the same file name, size and anchor. Safe to upgrade.

## [0.2.0]

- First paintings: the red-brick semi-detached house front (painted in Kerby's test batch) and
  the picket fence (painted for Tip the Can). Both games already use copies of these.
- Fonts: Fredoka and Cabin Sketch Bold, with their OFL licences.
- The manifest now lists the whole planned kit, with each file's planned path and width, and
  the shared palette.

## [0.1.0]

- First release: folder layout, house rules and an empty manifest. No art yet; lets the games
  install the kit and test their update script.
