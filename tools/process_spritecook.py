#!/usr/bin/env python3
"""Turns raw SpriteCook downloads into Street Kit files and updates manifest.json.

Usage:
  python3 tools/process_spritecook.py <raw_dir>          # process every output whose raw PNG is present
  python3 tools/process_spritecook.py --check            # verify every shipped file matches its sha12

Each output in manifest.json that should be processed carries:
  "raw":   file name (without .png) of the download in <raw_dir>
  "path":  where the processed file goes, e.g. art/elevations/terrace_row_brick.png
  "mode":  how to process it:
           fit_width     trim, then scale to "width" (elevations: houses, lamps, vans, trees)
           strip         trim, keep the middle, cross-fade the ends so it tiles left to right, scale to "width"
           texture       square, cross-faded on both axes so it tiles, scale to "width"
           slice         the raw is a row of "count" items; this output takes item "index" (0-based), then fit_width
  "width": target width in px
Outputs are written deterministically, and "size" and "sha12" are filled in.
Needs Pillow and numpy.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"


def trim(im: Image.Image) -> Image.Image:
    box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(box) if box else im


def scale_to_width(im: Image.Image, width: int) -> Image.Image:
    return im.resize((width, max(1, round(im.height * width / im.width))), Image.LANCZOS)


def fit_width(im: Image.Image, width: int) -> Image.Image:
    return scale_to_width(trim(im), width)


def _crossfade_x(a: np.ndarray, blend: float) -> np.ndarray:
    n = max(1, int(a.shape[1] * blend))
    ramp = np.linspace(0.0, 1.0, n)[None, :, None]
    head = a[:, :n] * ramp + a[:, -n:] * (1.0 - ramp)
    return np.concatenate([head, a[:, n:-n]], axis=1)


def strip(im: Image.Image, width: int, blend: float = 0.12) -> Image.Image:
    """Tiles left to right: keeps the middle 80% (generated ends are often rounded off),
    then cross-fades the last [blend] into the first so the seam disappears."""
    im = trim(im)
    inset = int(im.width * 0.1)
    im = im.crop((inset, 0, im.width - inset, im.height))
    out = _crossfade_x(np.asarray(im).astype(np.float32), blend)
    return scale_to_width(Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA"), width)


def texture(im: Image.Image, width: int, blend: float = 0.12) -> Image.Image:
    im = im.convert("RGBA")
    side = min(im.size)
    im = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width + side) // 2, (im.height + side) // 2))
    a = _crossfade_x(np.asarray(im).astype(np.float32), blend)
    a = _crossfade_x(a.transpose(1, 0, 2), blend).transpose(1, 0, 2)
    out = Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")
    return out.resize((width, width), Image.LANCZOS)


def slice_row(im: Image.Image, count: int, index: int) -> Image.Image:
    """Splits a sheet of [count] items laid out in a row, using the transparent gaps
    between them; falls back to equal columns."""
    im = trim(im)
    alpha = np.asarray(im.getchannel("A")) > 8
    cols = alpha.any(axis=0)
    runs, start = [], None
    for x, filled in enumerate(cols):
        if filled and start is None:
            start = x
        elif not filled and start is not None:
            runs.append((start, x))
            start = None
    if start is not None:
        runs.append((start, len(cols)))
    # merge tiny gaps until we have [count] runs
    while len(runs) > count:
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = gaps.index(min(gaps))
        runs[i:i + 2] = [(runs[i][0], runs[i + 1][1])]
    if len(runs) != count:
        w = im.width / count
        runs = [(round(i * w), round((i + 1) * w)) for i in range(count)]
    x0, x1 = runs[index]
    return trim(im.crop((x0, 0, x1, im.height)))


def sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def process(raw_dir: Path) -> None:
    m = json.loads(MANIFEST.read_text())
    done = 0
    for asset in m["assets"]:
        for out in asset.get("outputs", []):
            raw = out.get("raw")
            if not raw or not out.get("mode"):
                continue
            src = raw_dir / f"{raw}.png"
            if not src.exists():
                continue
            im = Image.open(src).convert("RGBA")
            mode, width = out["mode"], int(out.get("width", 512))
            if mode == "fit_width":
                res = fit_width(im, width)
            elif mode == "strip":
                res = strip(im, width)
            elif mode == "texture":
                res = texture(im, width)
            elif mode == "slice":
                res = fit_width(slice_row(im, int(out["count"]), int(out["index"])), width)
            else:
                sys.exit(f"{asset['id']}: unknown mode {mode!r}")
            dest = ROOT / out["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            res.save(dest, optimize=True)
            out["size"] = [res.width, res.height]
            out["sha12"] = sha12(dest)
            print(f"{out['path']}  {res.width}x{res.height}  {out['sha12']}")
            done += 1
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(f"{done} file(s) written; manifest.json updated.")


def check() -> None:
    m = json.loads(MANIFEST.read_text())
    bad = 0
    for asset in m["assets"]:
        if asset.get("status") != "shipped":
            continue
        for out in asset.get("outputs", []):
            if not out.get("sha12"):
                continue  # a variant that hasn't been painted yet
            p = ROOT / out["path"]
            if not p.exists():
                print(f"MISSING {out['path']}")
                bad += 1
            elif out.get("sha12") and sha12(p) != out["sha12"]:
                print(f"CHANGED {out['path']} ({sha12(p)} != {out['sha12']})")
                bad += 1
    print("All shipped files match." if not bad else f"{bad} problem(s).")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    if sys.argv[1:] == ["--check"]:
        check()
    elif len(sys.argv) == 2:
        process(Path(sys.argv[1]))
    else:
        sys.exit(__doc__)
