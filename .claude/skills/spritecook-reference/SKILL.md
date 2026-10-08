---
name: spritecook-reference
description: Reference for everything SpriteCook can do (models and credit costs, MCP tools, REST API, tilesets, animation engines, character sets, UI kits, slicing, presets, Godot exports) as of 2026-10-08. Use before planning any SpriteCook generation, when choosing a model or workflow, when pricing a batch for Dan, or when asked what SpriteCook supports.
---

# SpriteCook reference

Everything public about SpriteCook, gathered on 2026-10-08 from spritecook.ai (all 145 pages,
`llms.txt`, docs, blog, API reference), the hosted MCP server's own tool list, the free read-only
API endpoints, and the official skill repos. It is a map, not a workflow: the official
`spritecook-*` skills say how to run each job, and each game's art skill (for example Tip the
Can's `tip-the-can-art`) holds its house settings.

**Credits are Dan's money.** Never spend without his yes for that batch: give the count and cost
first, call `get_credit_balance` before and after, and report the spend. Everything in
"Free calls" below costs nothing and can be run any time. Prices change: confirm with
`list_generation_models` / `list_character_workflows` before quoting.

Detail lives in:

- `references/mcp-tools.md`: all 43 MCP tools with parameters and defaults.
- `references/api.md`: REST endpoints, parameters, limits, errors.
- `refresh.sh`: re-snapshots the free endpoints and site so this skill can be updated.

## Account and access

- Dan's tier is **Adventurer** ($30/mo, 3,000 credits a month, 5 concurrent jobs, up to 8
  variations in the app, 4 via API/MCP). Subscription credits reset monthly; top-ups never expire.
  Free tier is 40 credits a month.
- MCP: `https://api.spritecook.ai/mcp/` with `Authorization: Bearer $SPRITECOOK_API_KEY`
  (Tip the Can's `.mcp.json`). The official plugin uses `https://mcp.spritecook.ai/mcp/claude`
  with a browser sign-in instead of a key.
- REST: `https://api.spritecook.ai/v1/api/...`, same Bearer key. Never print or commit the key.
- Assets are Dan's to use commercially; no credit to SpriteCook required.

## Still-image models (live catalogue, credits per image)

| `model` | Name | 1K | 2K | 4K | Notes |
|---|---|---|---|---|---|
| `gemini-nano-banana-2.1` | Nano Banana 2.1 | 12 | 18 | 30 | **Server default and our house model.** 14 refs. |
| `gemini-3.1-flash-image` | Nano Banana 2 | 12 | 18 | 30 | Previous default. 14 refs. |
| `gemini-3.1-flash-lite-image` | Nano Banana 2 Lite | 8 | – | – | Fast, cheaper drafts; weaker consistency. 1K only. |
| `gemini-3-pro-image` | Nano Banana Pro | 16 | 24 | 40 | Best at holding a tight pixel grid; 10 refs, 20 rpm. |
| `gpt-image-2` | GPT-Image-2 | 2 / 9 / 36 | 2 / 7 / 28 | 4 / 17 / 68 | low / medium / high quality. Best for UI, layouts, text. |
| `gpt-image-2.5-flare` | GPT 2.5 Flare ("fast") | 5 / 8 / 25 | 8 / 14 / 47 | 9 / 17 / 59 | **Native transparency.** +8 per reference image; non-square 1K billed as 2K. |
| `gpt-image-2.5-sunburst` | GPT 2.5 Sunburst ("precision") | same as Flare | | | Native transparency, same pricing rules as Flare. |
| `gemini-2.5-flash-image` | Nano Banana | 8 | – | – | Deprecated. |

Variations multiply the cost. `supports_transparency` is true only for the two GPT 2.5 models;
the others paint on a background that SpriteCook removes.

Model picks from SpriteCook's own comparisons: Nano Banana 2/2.1 for consistent sets and
characters; Lite for cheap exploration; Pro plus a checkerboard style reference for tiny
16–32 px pixel art; GPT-Image-2 for UI, HUDs, menus, signage and any text in the image.

## `generate_game_art` essentials

- `pixel=true` (default) snaps to a pixel grid; `pixel=false` is detailed/HD in any style named in
  the prompt or `style`. `width`/`height` (16–512) are only size hints.
- `mode`: `assets` (default), `texture` (seamless 2x2 tiling; with `bg_mode="transparent"` it
  makes tiling decals such as scattered leaves), `ui` (one isolated UI piece only).
- `bg_mode`: `transparent`, `white`, `include` (painted scene behind).
- `smart_crop` + `smart_crop_mode` (`tightest` default, `power_of_2` on request).
- `aspect_ratio`: `1:1`, `16:9`, `9:16`. `resolution`: `1K`, `2K`, `4K`.
- `theme` (the world) and `style` (the look) ride along with the prompt; keep both identical
  across a set. `colors`: up to 64 hex codes, a nudge not a hard limit.
- Three kinds of reference, do not mix them up:
  - `style_asset_ids`: up to 14 ambient style guides (model limit applies; Pro allows 10).
  - `reference_asset_id`: one specific subject/context image ("same character, new pose").
  - `edit_asset_id`: the one image being changed ("add a red cape"); geometry is best-effort.
- `variations` 1–4, `project_id` to file it, `wait_seconds` up to 90 to block.
- Packing trick: ask for "8 separate X in a grid on transparent background" in one generation,
  then `auto_slice_asset`. One image costs the same however many things are on it, and things
  generated together match better.

## Animation (`animate_game_art`)

Image-to-animation from an owned `asset_id` (import local files first). Short loops, not video.

| `model` | Modes | Frames | Credits | Use for |
|---|---|---|---|---|
| `pixel-engine-v1.1` (default, pixel) | pixel ≤256 px | even, 2–16 | 20 | Walks, idles, clean loops, whole-body motion. Takes `negative_prompt`. |
| `frame-engine-v1.1` (default, detailed) | detailed 256–2048 px | even, 2–24 | 20 | HD/painted art (our house style). |
| `pixel-engine-v1.5` | pixel ≤320 px **and** detailed | any 3–16 | 26 | Specific or two-part actions ("raise shield, keep sword down"). Slower, steadier, stiffer; no `negative_prompt`. |

- Mode is inferred from the source: up to 256 px is pixel, 256–2048 px is detailed.
- `removebg`: `Basic` (default), `None`, `Pro` (extra per-frame cost; the web app auto-picks Pro
  for detailed art, the API does not).
- `output_format`: `webp`, `gif`, `spritesheet`. The job's `spritesheet_url` is the PNG strip.
- `auto_enhance_prompt` (default true) expands short prompts; turn it off for exact control.
- `edge_margin` (default 6 %): keep it low; add room only for jumps (10–15 %) or swings (5–10 %).
- Never resubmit a queued job: every submit bills a new one. Poll `check_job_status`.
- The source must already be in the final camera view; animation will not change perspective.
- Web app only (not in the API/MCP): keyframe **Frame Animation** (up to 8 reference frames,
  per-frame prompts, regenerate only marked frames), onion-skin alignment, mirroring and
  power-of-2 canvas snapping.

## Guided characters (`generate_character` → `generate_character_animations`)

**Pixel art only**, 64 px base, 12 credits. Perspectives and presets:

- `platformer`: idle, walk, jump (defaults), run, attack, hurt, death.
- `isometric`: idle, walk_down, walk_right (defaults) plus back variants, run, jump, attack, hurt, death.
- `topdown`: idle, walk_up, walk_right, walk_down (defaults) plus idle/walk/run/attack/hurt/death
  in back, left and right.

Each animation is 20 credits (8 frames; run 10, death 12) plus 12 for a "prep" pose when it
needs a different source view (back, side, walk or run pose). Basic background removal is the
default; `photoroom` costs 36–44 per animation. `custom_animations` take
`{label, prompt, source_view, output_frames}`. The app discounts batches. A prep pose that lands
on the wrong pixel grid fails the run and refunds it; retrying the same character rarely helps,
more internal detail or the Pro model does. Finish with `export_godot_character_package` for a
Godot 4 project with SpriteFrames and AnimatedSprite2D scenes.

## Tilesets (`generate_tileset`)

| Style | Perspective | Piece sets | Tile sizes |
|---|---|---|---|
| pixel | topdown | `15-piece` (4x4, default), `17-piece-base` (5x4) | 16, 32 |
| pixel | platformer | `autotile-16-set` (4x4 Match Sides) | 16, 32, 64 |
| pixel | isometric | `isometric-3x5-32`, `isometric-2x4-64` | 32, 64 |
| **detailed** | topdown | `15-piece`, `17-piece-base` | **64, 128, 256** |

- `edges`: `transparent` or `two_surfaces` (15-piece top-down only: two materials meeting,
  e.g. grass into pavement). `elevation`: `no-elevation` or `minimal`.
- `colors` / `force_enabled` + `force_colors` for palette lock; `style_asset_id` (single) for
  style; `reference_asset_id` / `edit_asset_id` inherit settings from an existing tileset.
- `export_godot_tileset_package(asset_id)` returns the sheet plus a `.tres` TileSet with terrain
  already set up for 15/17-piece and platformer sets (paint from the Terrains tab of a
  TileMapLayer). The app can also expand a sheet to the 47-piece blob layout.
- Dual-grid rendering of 15-piece sets: see the official `spritecook-use-dual-grid-tilesets`.
- Free web tools: Tileset Base Generator, Pixel Grid Detector, Sprite Sheet Slicer.

## UI kits (`create_ui_kit` and friends)

Concept first, then pieces: create kit → `generate_ui_kit_concepts` (or pass an existing
`concept_asset_id` / uploaded mockup) → `select_ui_kit_concept` →
`generate_ui_kit_component_sheets` (1–3 sheets; `state_mode="complete-states"` adds hover,
pressed, disabled, checked families) → `extract_ui_kit_components` (check `quality_summary`) →
`finalize_ui_kit`. Defaults to `gpt-image-2`; component sheets always use it. Screen types: main
menu, HUD, pause, settings, inventory, dialogue, shop, quest log, character select, map, game
over, custom; platform `desktop-console` or `mobile`. Concepts are priced per image and sheets per
sheet; slicing, naming, 9-slice borders and exports are free. The app's Godot export gives PNGs,
StyleBoxTexture resources with 9-slice margins, and Theme mappings. Use `parent_ui_kit_id` to
build the next screen in the same family. Full flow: official `spritecook-build-ui-kits`.

## Other tools

- `remove_background(asset_id | image)`: 1 credit for a still, 2 for animated WebP.
- `auto_slice_asset(asset_id)`: splits a multi-sprite image or animation by connected alpha,
  with smart alpha for overlaps; returns a `manual_slice_url` for hand-drawn boxes.
- Uploads: `create_asset_upload` → HTTP PUT → `finalize_asset_upload` for local files (never log
  the upload URL or token); `import_asset` only for small base64. See official
  `spritecook-upload-assets`.
- Organising: `list_projects`, `create_project`, `list_collections`, `create_collection`,
  `assign_assets_to_project`, `assign_assets_to_collection`, `update_asset_label`.
- Presets: `list_presets`, `get_preset_settings`, `save_private_preset`. A preset stores model,
  size, aspect, palette, background and removal settings, crop, style guides, pixel-perfect and
  any reference/edit image, but **not** the prompt or theme. Paid accounts get unlimited private
  presets; publishing makes any reference image public.
- Recovery: `list_recent_assets`, `get_asset_metadata`, `list_animation_outputs`,
  `list_active_jobs`, `cancel_job` (animations may refund pending).

## Free calls (no credits)

`get_credit_balance`, `list_generation_models`, `list_character_workflows`,
`list_tileset_options`, `list_presets`, `get_preset_settings`, `list_recent_assets`,
`get_asset_metadata`, `check_job_status`, `list_*` organisers, `export_godot_*_package`,
and over REST `GET /v1/api/models`, `/character-workflows`, `/credits`, `/assets/recent`,
`/assets/{id}`, `/jobs/{id}`.

## Best practice that holds across the docs

1. Set theme and style once; generate one hero asset, approve it, then pass its id as a style
   reference to everything after. Save the winning setup as a private preset so months-later
   batches match.
2. Keep prompts short: one subject and one or two distinctive traits. Name the view ("side
   view", "front view", "seen from directly above") or models drift to three-quarter.
3. Keep every asset id in a local manifest (here, `manifest.json`); recover lost ones with
   `list_recent_assets` rather than regenerating.
4. Pack many small things into one generation and slice; it is cheaper and more consistent.
5. Nano Banana pixel art is painted, not grid-true: use `pixel=true` post-processing or the Pixel
   Grid Detector before engine import.
6. Let the agent check its own output against the set and regenerate what is off, but only
   within the batch Dan approved.

## Official skills and community

SpriteCook publishes nine skills (identical copies in `SpriteCook/skills`,
`SpriteCook/claude-plugin` v0.1.9 and the Codex, Cursor and OpenCode plugins):
workflow-essentials, generate-sprites, animate-assets, generate-tilesets, use-dual-grid-tilesets,
use-presets, use-assets-in-godot, **upload-assets** and **build-ui-kits**. Tip the Can vendors the
first seven (byte-identical to upstream on 2026-10-08); the last two are not vendored yet.
`npx skills add spritecook/skills` installs them anywhere. No third-party SpriteCook skills
exist: the directory listings (skills.sh, claudemarketplaces.com) all point back to these repos.

Known doc drift: `spritecook-upload-assets` says `style_asset_ids` takes up to 10 ids; the server
says 14 (model limit applies). The API page's default model is still Nano Banana 2; the live
server default is Nano Banana 2.1.
