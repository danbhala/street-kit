#!/usr/bin/env python3
"""Print a Markdown table of the assets a branch adds or changes, for a PR body.

Usage (from the repo root, after pushing the branch):
    python3 .claude/skills/open-pr/asset_table.py [--base origin/main] [--ref HEAD]

Previews link to https://github.com/<owner>/<repo>/blob/<sha>/<path>?raw=true.
That is the only image URL that renders in a PR description on a private repo:
GitHub fetches it with the reviewer's own login. raw.githubusercontent.com
links (and relative paths) show as broken images on private repos. Pinning
the commit sha keeps the images working after the branch is deleted.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys

IMAGES = (".png", ".gif", ".jpg", ".jpeg", ".webp", ".svg")
ASSETS = IMAGES + (".ogg", ".wav", ".mp3", ".mp4", ".webm", ".ttf", ".otf", ".woff2")
SKIP = ("screenshots/", "docs/", "tests/", "addons/", ".github/", "assets/_original/")


def git(*args: str, binary: bool = False):
    out = subprocess.run(["git", *args], check=True, capture_output=True).stdout
    return out if binary else out.decode().strip()


def repo_slug() -> str:
    url = git("remote", "get-url", "origin")
    match = re.search(r"github\.com[:/](.+?/[^/]+?)(?:\.git)?/?$", url)
    if not match:
        sys.exit(f"origin is not a GitHub remote: {url}")
    return match.group(1).split("/git/")[-1]


def dimensions(data: bytes, path: str) -> tuple[int, int, int]:
    """Width, height and frame count, or zeros when unknown."""
    if path.endswith(".svg"):
        return 0, 0, 1
    try:
        from PIL import Image

        with Image.open(io.BytesIO(data)) as image:
            return image.width, image.height, getattr(image, "n_frames", 1)
    except ImportError:
        if data[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(data[16:20], "big"), int.from_bytes(data[20:24], "big"), 1
        return 0, 0, 1


def human(size: int) -> str:
    return f"{size / 1024:.0f} KB" if size < 1024 * 1024 else f"{size / 1048576:.1f} MB"


def known_details(ref: str) -> dict[str, str]:
    """Labels and SpriteCook ids from the repo's asset records, keyed by path."""
    details: dict[str, str] = {}
    for record in ("art/spritecook-assets.json", "manifest.json"):
        try:
            data = json.loads(git("show", f"{ref}:{record}"))
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            continue
        for asset in data.get("assets", []):
            sc = asset.get("spritecook") or {}
            asset_id = asset.get("asset_id") or sc.get("asset_id")
            label = asset.get("label") or asset.get("name") or ""
            for output in asset.get("outputs", []):
                if isinstance(output, str):  # Tip the Can: paths under art/
                    path, out_id = f"art/{output}", asset_id
                else:  # Street Kit manifest
                    path = output.get("path", "")
                    out_id = (output.get("spritecook") or {}).get("asset_id") or asset_id
                bits = [label] if label else []
                if out_id:
                    bits.append(f"SpriteCook `{out_id[:8]}`")
                details[path] = ", ".join(bits)
    return details


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument("--width", type=int, default=160, help="preview width in px")
    args = parser.parse_args()

    sha = git("rev-parse", args.ref)
    if not git("branch", "-r", "--contains", sha):
        sys.exit("Push the branch first: the previews link to the pushed commit.")
    slug = repo_slug()
    details = known_details(args.ref)

    rows = []
    changes = git("diff", "--name-status", "--no-renames", f"{args.base}...{args.ref}")
    for line in changes.splitlines():
        status, path = line.split("\t", 1)
        if status not in "AM" or not path.lower().endswith(ASSETS) or path.startswith(SKIP):
            continue
        data = git("show", f"{sha}:{path}", binary=True)
        url = f"https://github.com/{slug}/blob/{sha}/{path}"
        preview, size = "—", "—"
        if path.lower().endswith(IMAGES):
            w, h, frames = dimensions(data, path)
            # Strips and spritesheets get three times the room so frames stay readable.
            width = args.width * 3 if h and w / h > 2 else args.width
            preview = f'<a href="{url}"><img src="{url}?raw=true" width="{width}"></a>'
            size = f"{w}×{h}" if w else ("vector" if path.endswith(".svg") else "?")
            if frames > 1:
                size += f", {frames} frames"
        name = path.rsplit("/", 1)[-1]
        if status == "M":
            name += " (changed)"
        rows.append(
            f"| {preview} | **{name}** | `{path}` | {size} | {human(len(data))} | {details.get(path, '')} |"
        )

    if not rows:
        print("No new or changed assets.", file=sys.stderr)
        return
    print("| Preview | Asset | Path | Pixels | File size | Details |")
    print("| --- | --- | --- | --- | --- | --- |")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
