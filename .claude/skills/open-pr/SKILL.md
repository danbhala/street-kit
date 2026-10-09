---
name: open-pr
description: Open or edit a pull request on danbhala/street-kit, with a preview table of every new or changed asset in the description. Use whenever a Street Kit change is ready to propose, or when writing or fixing a PR description.
---

# Opening a Street Kit pull request

1. Work on a branch, never main. If the PR changes what ships (art, fonts,
   manifest), add a `## [x.y.z]` section at the top of `CHANGELOG.md`.
2. Push, then generate the asset table:
   ```
   python3 .claude/skills/open-pr/asset_table.py
   ```
   It lists every added or changed file under `art/` and `fonts/` with a
   preview, name, path, pixel size, file size, and the name and SpriteCook id
   from `manifest.json`. Paste it into the body as is, then make the Details
   column say what the asset is for and which games use it.
3. Body, in this shape:
   ```
   Before: <what the kit had>

   After: <what it has now>

   **Assets** (click a preview for full size)
   <the table>

   **Version:** x.y.z, and why that bump. For a major version, list the games
   that must be checked before upgrading (from `used_by`).

   **Spend:** credits spent, balance before and after.

   **Known flaws:** anything visible a reviewer should know.
   ```
4. Keep any attribution lines the session requires at the top and bottom.

## Why the image links look like that

Previews use `https://github.com/<owner>/<repo>/blob/<sha>/<path>?raw=true`.
It works on public and private repos alike (GitHub loads it with the reader's
login), and pinning the commit keeps it working after the branch is deleted.
Tip the Can's repo is private, so `raw.githubusercontent.com` links and
relative paths render as broken images there; use the same form everywhere.
Re-run the script after pushing new art so the previews show the latest files.
