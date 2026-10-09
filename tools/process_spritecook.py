#!/usr/bin/env python3
"""Turns raw SpriteCook downloads into Street Kit files and updates manifest.json.

Usage:
  python3 tools/process_spritecook.py <raw_dir>          # process every output whose raw PNG is present
  python3 tools/process_spritecook.py --derive           # rebuild only the outputs made from other kit files
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
An output can instead be made from another kit file, with no SpriteCook download:
  "from":  the kit file it is made from, e.g. art/textures/lane_tarmac.png
  "mode":  plain_texture  the texture with its painted patches lifted out ("remove": list of
                          {"box": [x, y, w, h], "threshold": t}; boxes may cross the edge, it wraps)
           cutout         one patch from the texture as a decal on transparency ("box", "threshold")
Derived outputs are rebuilt after every raw run, so they follow their source.
Outputs are written deterministically, and "size" and "sha12" are filled in.
Needs Pillow and numpy.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

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


def _wrap_blur(x: np.ndarray, radius: float) -> np.ndarray:
    """Gaussian blur done in the frequency domain, so it wraps and a tiling texture still tiles."""
    h, w = x.shape[:2]
    k = np.exp(-2 * (np.pi * radius) ** 2 * (np.fft.fftfreq(h)[:, None] ** 2 + np.fft.fftfreq(w)[None, :] ** 2))
    if x.ndim == 3:
        k = k[..., None]
    return np.real(np.fft.ifft2(np.fft.fft2(x, axes=(0, 1)) * k, axes=(0, 1)))


def _grow(mask: np.ndarray, px: int) -> np.ndarray:
    """Dilates a 0..1 mask by [px], wrapping round the edges."""
    pad = np.pad(mask, px + 1, mode="wrap")
    out = Image.fromarray((pad * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * px + 1))
    return (np.asarray(out) / 255.0)[px + 1:-px - 1, px + 1:-px - 1]


def _shrink(mask: np.ndarray, px: int) -> np.ndarray:
    return 1.0 - _grow(1.0 - mask, px)


def _patch_mask(rgb: np.ndarray, box: list, threshold: float) -> np.ndarray:
    """Pixels inside [box] whose colour stands out from the texture's usual colour: a painted
    patch, darker, lighter or warmer than the ground around it."""
    h, w = rgb.shape[:2]
    soft = _wrap_blur(rgb, 3)
    usual = np.median(rgb.reshape(-1, 3), axis=0)
    score = np.maximum(np.abs((soft - usual).mean(2)) / 14,
                       ((soft[..., 0] - soft[..., 2]) - (usual[0] - usual[2])) / 12)
    x, y, bw, bh = box
    inside = np.zeros((h, w))
    inside[np.ix_(np.arange(y, y + bh) % h, np.arange(x, x + bw) % w)] = 1
    return _shrink(_grow((score > threshold) * inside, 6), 6)


def plain_texture(im: Image.Image, removes: list) -> Image.Image:
    """Lifts painted patches out of a tiling texture. Each one is filled with clean ground
    copied from elsewhere in the same texture, shifted to match the slow colour drift around
    the hole and feathered in, so grain and brushwork carry on through."""
    a = np.asarray(im.convert("RGBA")).astype(np.float64)
    rgb = a[..., :3]
    masks = [_patch_mask(rgb, r["box"], r["threshold"]) for r in removes]
    everything = np.clip(sum(masks), 0, 1)
    avoid = _grow(everything, 24)
    keep = 1.0 - _grow(everything, 10)
    drift = _wrap_blur(rgb * keep[..., None], 40) / np.maximum(_wrap_blur(keep, 40), 1e-3)[..., None]
    h, w = rgb.shape[:2]
    for mask in masks:
        hole = _grow(mask, 14)
        feather = np.maximum(np.clip(_wrap_blur(hole, 5), 0, 1), _grow(mask, 7))
        best = None
        for dy in range(-h // 2, h // 2 + 1, 16):
            for dx in range(-w // 2, w // 2 + 1, 16):
                if abs(dx) < 120 and abs(dy) < 120:
                    continue
                cost = (np.roll(avoid, (-dy, -dx), (0, 1)) * hole).sum()
                if best is None or cost < best[0]:
                    best = (cost, dx, dy)
        _, dx, dy = best
        fill = np.roll(a, (-dy, -dx), (0, 1))
        fill[..., :3] += drift - np.roll(drift, (-dy, -dx), (0, 1))
        a = a * (1 - feather[..., None]) + fill * feather[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA")


def cutout(im: Image.Image, box: list, threshold: float) -> Image.Image:
    """One painted patch from a texture, with a soft edge, on transparency."""
    a = np.asarray(im.convert("RGBA")).astype(np.float64)
    alpha = np.clip(_wrap_blur(_grow(_patch_mask(a[..., :3], box, threshold), 3), 1.5), 0, 1)
    a[..., 3] = alpha * 255
    # roll the patch away from the edges so it is in one piece, then trim
    x, y, bw, bh = box
    a = np.roll(a, (a.shape[0] // 2 - (y + bh // 2), a.shape[1] // 2 - (x + bw // 2)), (0, 1))
    return trim(Image.fromarray(a.clip(0, 255).astype(np.uint8), "RGBA"))


def derive() -> int:
    """Rebuilds every output made from another kit file. Returns how many were written."""
    m = json.loads(MANIFEST.read_text())
    done = 0
    for asset in m["assets"]:
        for out in asset.get("outputs", []):
            if not out.get("from"):
                continue
            im = Image.open(ROOT / out["from"]).convert("RGBA")
            if out["mode"] == "plain_texture":
                res = plain_texture(im, out["remove"])
            elif out["mode"] == "cutout":
                res = cutout(im, out["box"], out["threshold"])
            else:
                sys.exit(f"{asset['id']}: unknown derived mode {out['mode']!r}")
            dest = ROOT / out["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            res.save(dest, optimize=True)
            out["size"] = [res.width, res.height]
            out["sha12"] = sha12(dest)
            print(f"{out['path']}  {res.width}x{res.height}  {out['sha12']}  (from {out['from']})")
            done += 1
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    return done


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
    done += derive()
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
    elif sys.argv[1:] == ["--derive"]:
        print(f"{derive()} derived file(s) written; manifest.json updated.")
    elif len(sys.argv) == 2:
        process(Path(sys.argv[1]))
    else:
        sys.exit(__doc__)
