# SpriteCook MCP tools (server 2.14.5, snapshot 2026-10-08)

Generated from the hosted server's `tools/list` (free to call). Parameters show their defaults. Re-run `refresh.sh` to update.

- **`generate_game_art`**(prompt*, width=64, height=64, variations=1, pixel=true, bg_mode="transparent", theme, style, aspect_ratio="1:1", smart_crop=true, smart_crop_mode="tightest", model, mode="assets", resolution="1K", quality="medium", colors, reference_asset_id, edit_asset_id, style_asset_ids, project_id, wait_seconds=0): Generate still-image game art assets from a text description.
- **`create_ui_kit`**(name*, screen_type="main-menu", platform="desktop-console", aspect_ratio="16:9", style_preset_id="clean-modern", style_text, game_description, instructions, density="standard", model="gpt-image-2", state_mode="visible-only", style_asset_ids, concept_asset_id, parent_ui_kit_id): Create a durable concept-first UI kit workflow.
- **`list_ui_kits`**(limit=20): List recent UI kits so an agent can recover a kit ID and continue it.
- **`get_ui_kit`**(ui_kit_id*): Get compact UI-kit status, jobs, concepts, sheets, manifest, and next action.
- **`generate_ui_kit_concepts`**(ui_kit_id*, count=3, revision_notes, edit_source_asset_id, edit_notes): Enqueue concept options for a UI kit and return immediately with job IDs.
- **`select_ui_kit_concept`**(ui_kit_id*, asset_id*): Select one owned concept asset as the source for component sheets.
- **`generate_ui_kit_component_sheets`**(ui_kit_id*, state_mode, focus_notes, supplemental_notes, sheet_count, revision_notes, edit_source_asset_id, edit_notes, high_resolution=false): Enqueue transparent component sheets from the selected UI concept.
- **`extract_ui_kit_components`**(ui_kit_id*, sheet_asset_ids, alpha_threshold=1, min_area=24, padding=0, merge_distance=1): Detect, name, classify, and save a component draft for one UI kit.
- **`finalize_ui_kit`**(ui_kit_id*, components, smart_alpha=true): Create reusable UI-element assets from a saved or supplied component draft.
- **`cancel_ui_kit`**(ui_kit_id*): Cancel active concept or component-sheet jobs for one owned UI kit.
- **`generate_tileset`**(prompt*, style_mode="pixel", perspective="topdown", piece_set, tile_size, elevation, edges="transparent", variations=1, project_id, theme, style, model, colors, force_enabled=false, force_colors, force_automatic=false, force_color_count, reference_asset_id, edit_asset_id, style_asset_id, wait_seconds=0): Generate a SpriteCook tileset with tileset-specific validation and post-processing.
- **`animate_game_art`**(prompt*, asset_id*, auto_enhance_prompt=true, edge_margin=6, pixel, model, output_frames=8, output_format="webp", negative_prompt, matte_color="#808080", removebg="Basic", colors=24): Animate a SpriteCook asset into a short pixel-art or detailed animation.
- **`create_asset_upload`**(file_name*, content_type*, display_name, project_id, collection_id, pixel=true, size_bytes): Create a short-lived upload URL for importing a local image file.
- **`import_asset`**(image*, pixel=true, display_name, file_name, project_id): Import local image bytes into SpriteCook as an owned asset.
- **`finalize_asset_upload`**(upload_token*): Finalize a local-file upload into a normal SpriteCook asset.
- **`auto_slice_asset`**(asset_id*, source_variant="auto", alpha_threshold=1, min_area=24, padding=0, merge_distance=1): Automatically split an owned SpriteCook asset into separate assets.
- **`remove_background`**(asset_id, image, runpod_alpha_threshold_enabled, runpod_alpha_cutoff, wait_seconds=0): Remove the background from an owned SpriteCook asset or inline image.
- **`check_job_status`**(job_id*): Check the status of a SpriteCook generation or animation job.
- **`list_active_jobs`**(): List active jobs for the authenticated user.
- **`list_recent_assets`**(limit=10): List recent owned assets so agents can recover lost asset IDs and fetch fresh links.
- **`list_projects`**(): List projects owned by the authenticated SpriteCook user.
- **`create_project`**(name*): Create a SpriteCook project for organizing assets.
- **`list_collections`**(project_id): List owned SpriteCook collections, which act like folders for assets.
- **`create_collection`**(name*, project_id): Create a folder-like SpriteCook collection.
- **`assign_assets_to_project`**(asset_ids*, project_id): Move owned assets into a project, or out of all projects.
- **`assign_assets_to_collection`**(asset_ids*, collection_id): Move owned assets into a collection, or remove collection membership.
- **`cancel_job`**(job_id*): Cancel an owned SpriteCook job by ID.
- **`list_animation_outputs`**(asset_id*, limit=10): List recent animation outputs derived from an owned source asset.
- **`get_credit_balance`**(): Check your remaining SpriteCook credits and subscription tier.
- **`list_generation_models`**(): List available still-image generation models and SpriteCook credit costs.
- **`list_tileset_options`**(): List supported SpriteCook tileset generation options.
- **`list_character_workflows`**(): List guided pixel-art character perspectives and available animations.
- **`generate_character`**(prompt*, perspective*, model, quality="medium", wait_seconds=0): Generate a guided base pixel-art character for animation.
- **`generate_character_animations`**(character_id*, perspective*, animation_ids, custom_animations, bg_removal_provider="basic", wait_seconds=0): Generate preset and/or custom animations for a base character.
- **`check_character_animation_run`**(run_id*): Check a guided character animation run by id.
- **`export_godot_tileset_package`**(asset_id*): Build a Godot-ready package manifest for an owned tileset asset.
- **`export_godot_character_package`**(run_id, animation_asset_ids, character_name, state_hints_by_asset_id): Build a Godot-ready character animation package manifest.
- **`get_asset_metadata`**(asset_id*): Get metadata for one of your SpriteCook assets.
- **`list_presets`**(query, status, mode, pixel, limit=20, offset=0): List the authenticated user's saved SpriteCook presets.
- **`get_preset_settings`**(preset_id*): Fetch apply-ready settings for a saved SpriteCook preset.
- **`save_private_preset`**(title*, description, settings, style_references, preview_asset_id, preview_asset_ids, reference_image, edit_image): Save a private draft SpriteCook preset for the authenticated user.
- **`update_asset_label`**(asset_id*, label*): Rename one of your SpriteCook assets.
- **`report_integration_error`**(agent_name*, platform_os*, client_surface*, surface*, endpoint_or_tool*, description*, operation, status_code, error_code, spritecook_user_id, request_id, app_version, os_version): Report a short SpriteCook integration failure for debugging.

`*` = required.
