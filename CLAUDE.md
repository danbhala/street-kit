# Street Kit: notes for Claude

Shared art for Tip the Can and Kerby. Read README.md first; its "one rule" decides what may live here.

## Rules

- Only front elevations, top-down decals and tiling textures belong here. A three-quarter-view
  asset, a character or a game's UI goes in that game's repo instead.
- Every asset gets an entry in `manifest.json`: SpriteCook `asset_id`, the prompt, its outputs
  with sha12, and `used_by` (which games use it). Reuse an existing asset id before generating.
- SpriteCook costs Dan's paid credits. Never spend without his yes for that batch: state the
  count and cost first, call `get_credit_balance` before and after, and report the spend.
  Never ask for the API key in chat or write it to a file; it comes from `SPRITECOOK_API_KEY`.
- Load the SpriteCook skills before any SpriteCook work (painting, animating, pricing or
  planning): `spritecook-reference` (models, costs, every MCP tool), `street-kit-art`, and the
  official `spritecook-*` skill for the job (`spritecook-workflow-essentials` always). Any that
  are missing are at https://github.com/SpriteCook/skills.
- To paint, use the `street-kit-art` skill (house settings, prompts per asset, costs, the
  processing step). Then set the asset's `status` to `shipped`, fill `spritecook` and `since`,
  and run `python3 tools/process_spritecook.py --check`.
- The docs site (`site/`) is built from `manifest.json`; keep the manifest accurate and it
  stays accurate. Check it locally with `python3 -m http.server` after copying `manifest.json`,
  `CHANGELOG.md`, `art/` and `fonts/` next to `site/index.html` (the Pages workflow does this).
- Every PR that changes what ships (art, fonts, manifest) adds a new `## [x.y.z]` section at
  the top of `CHANGELOG.md`; merging it publishes the release. Removing or renaming an asset,
  or changing its size or anchor, is a major version: say so in the PR and list which games
  use it (from `used_by`), because they must be checked before upgrading.
- Work on a branch and open a PR with the `open-pr` skill; never push to main.

## Questions for Dan (needs-dan issues)

When blocked on a decision only Dan can make, open an issue labelled `needs-dan` titled
"[Street Kit] <question>", with context, 2-4 options (recommendation first) and what you are
doing meanwhile. Check open `needs-dan` issues at the start of every session and before
finishing; once Dan has answered, act on it, comment with what you did, and close the issue.
