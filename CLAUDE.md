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
- Follow the house settings in Tip the Can's `.claude/skills/tip-the-can-art/SKILL.md`, but
  ask for "flat front elevation, seen straight-on, no ground, transparent background" instead
  of its top-down wording.
- Changing or removing an asset can break both games. Say so in the PR, and list which games
  need their submodule pointer bumped.
- Work on a branch and open a PR; never push to main.

## Questions for Dan (needs-dan issues)

When blocked on a decision only Dan can make, open an issue labelled `needs-dan` titled
"[Street Kit] <question>", with context, 2-4 options (recommendation first) and what you are
doing meanwhile. Check open `needs-dan` issues at the start of every session and before
finishing; once Dan has answered, act on it, comment with what you did, and close the issue.
