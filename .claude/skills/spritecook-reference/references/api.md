# SpriteCook REST API (snapshot 2026-10-08)

Base `https://api.spritecook.ai`, header `Authorization: Bearer $SPRITECOOK_API_KEY`.
Source: https://www.spritecook.ai/api-docs (its "Copy Documentation" text) plus live responses.
The MCP tools wrap the same backend and have more features (tilesets, UI kits, slicing,
presets, projects, Godot exports), so prefer MCP; use REST for scripts.

## Endpoints

| Method | Path | Scope | What it does |
|---|---|---|---|
| GET | `/v1/api/models` | generate | Model catalogue, limits and per-image costs (free) |
| GET | `/v1/api/character-workflows` | generate | Perspectives, preset animations, prep and costs (free) |
| POST | `/v1/api/characters` | generate | Base pixel character (64 px, transparent, 12 credits); job's first asset is `character_id` |
| POST | `/v1/api/characters/{character_id}/animations` | generate | Preset and custom animation run; returns `credits_reserved` |
| GET | `/v1/api/character-animation-runs/{run_id}` | generate | Run status, per-item status, asset ids |
| POST | `/v1/api/generate-sync` | generate | Generate and wait up to 90 s (recommended for scripts) |
| POST | `/v1/api/generate` | generate | Generate, returns `job_id` to poll |
| POST | `/v1/api/animate-sync` | generate | Animate and wait up to 90 s |
| POST | `/v1/api/animate` | generate | Animate, returns `job_id` |
| POST | `/v1/api/assets/import` | generate | `{image: data URL, pixel, display_name}` → owned asset |
| POST | `/v1/api/remove-background` | generate | `asset_id` or `image`/`file`; temporary file result; 1 credit still, 2 animated |
| GET | `/v1/api/jobs/{job_id}` | read_assets | Poll; stills return `assets`, animations `output`, bg removal `file` |
| GET | `/v1/api/assets/recent?limit=10` | read_assets | Recent assets with `sprite_url`, `spritesheet_url` |
| GET | `/v1/api/assets/{asset_id}` | read_assets | Full metadata: prompt, theme/style snapshots, model, refs, animation details |
| POST | `/v1/api/jobs/{job_id}/cancel` | generate | Cancel; animations may return a pending refund |
| GET | `/v1/api/credits` | – | `{total, subscription_credits, topup_credits, tier, concurrent_jobs}` (free) |

Every paid response includes `credits_used` and `credits_remaining`.

## Generate parameters

`prompt` (required); `width`/`height` 16–512 (default 64, hints only); `variations` 1–4;
`pixel` (true); `pixel_perfect` (true, grid-aligned post-processing); `bg_mode`
(`transparent` | `white` | `include`); `theme`; `style`; `aspect_ratio` (`1:1` | `16:9` | `9:16`);
`smart_crop` (true); `mode` (`assets` | `texture` | `ui`); `model`; `resolution`
(`1K` | `2K` | `4K`); `quality` (`low` | `medium` | `high`, GPT models only); `colors` (≤64 hex);
`reference_asset_id`; `edit_asset_id`; `runpod_alpha_threshold_enabled` (true) and
`runpod_alpha_cutoff` (96) for Basic background removal; `project_id`.
REST has no `style_asset_ids`; use MCP for multiple style guides.

## Animate parameters

`asset_id`, `prompt` (required); `pixel` (inferred from the source); `removebg`
(`Basic` default | `None` | `Pro`); `output_frames` (8; even, pixel 2–16, detailed 2–24);
`output_format` (`webp` | `gif` | `spritesheet`); `negative_prompt`; `matte_color` (`#808080`);
`colors` (24, pixel only); alpha threshold fields as above.
Pixel mode: PNG, up to 256x256. Detailed mode: PNG or JPEG, 256x256 to 2048x2048.
Output `metadata`: `frame_count`, `fps` (8), `frame_width`, `frame_height`, `animation_mode`.
The MCP tool adds `model` (`pixel-engine-v1.5`), `auto_enhance_prompt` and `edge_margin`.

## Asset URLs

`.../v1/assets/{id}/content/pixel` is the processed sprite; `.../content/raw` is the raw
spritesheet for animations. Use `sprite_url` first and `spritesheet_url` only when present.

## Errors

`402 insufficient_credits`, `429 rate_limited` (too many concurrent jobs; Adventurer allows 5),
`403 scope_denied`, `400 invalid_request`, `404 job_not_found`.
