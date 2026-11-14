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
           strip         trim, keep the middle, join the ends along a matching cut so it tiles left to right, scale to "width"
           texture       square, cross-faded on both axes so it tiles, scale to "width"
           seamless      square, scale to "width"; for a raw SpriteCook already made seamless
                         (mode="texture"), where a cross-fade would double up regular joints
           slice         the raw is a row of "count" items; this output takes item "index" (0-based), then fit_width
  "width": target width in px
  "same_size_as": optional path of another output (processed earlier in the manifest); this one is
           then scaled to exactly that size, for a variant that SpriteCook painted a little taller
           or wider than its twin (the lit lamp post), so the two swap without a jump
An output can instead be made from another kit file, with no SpriteCook download:
  "from":  the kit file it is made from, e.g. art/textures/lane_tarmac.png
  "mode":  plain_texture  the texture with its painted patches lifted out ("remove": list of
                          {"box": [x, y, w, h], "threshold": t}; boxes may cross the edge, it wraps)
           cutout         one patch from the texture as a decal on transparency ("box", "threshold")
Derived outputs are rebuilt only by --derive. A raw run that rewrites a source lists them, because
their boxes are tied to that exact painting and must be checked first.
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


def _seam_path(cost: np.ndarray) -> tuple:
    """The cheapest top-to-bottom path through [cost], one column per row, moving at most one
    column between rows (dynamic programming). Returns (total cost, column for each row)."""
    h, n = cost.shape
    acc = cost.copy()
    step = np.zeros((h, n), dtype=np.int64)
    for y in range(1, h):
        prev = np.stack([np.r_[1e18, acc[y - 1, :-1]], acc[y - 1], np.r_[acc[y - 1, 1:], 1e18]])
        step[y] = prev.argmin(0) - 1
        acc[y] += prev.min(0)
    seam = np.empty(h, dtype=np.int64)
    seam[-1] = int(acc[-1].argmin())
    for y in range(h - 1, 0, -1):
        seam[y - 1] = seam[y] + step[y, seam[y]]
    return float(acc[-1].min()), seam


def _seam_cost(tail: np.ndarray, head: np.ndarray) -> np.ndarray:
    n = tail.shape[1]
    alpha = np.maximum(tail[..., 3:], head[..., 3:]) / 255.0
    cost = (np.abs(tail[..., :3] - head[..., :3]) * alpha).sum(2) + np.abs(tail[..., 3] - head[..., 3])
    lo, hi = int(n * 0.2), int(n * 0.8)  # keep the cut away from the tile edges
    cost[:, :lo] = cost[:, hi:] = 1e9
    return cost


def _seam_x(a: np.ndarray, blend: float, feather: int = 3) -> np.ndarray:
    """Like _crossfade_x, but instead of fading the two ends through each other (which leaves
    a see-through ghost of both wherever they differ, such as two windows or chimneys), it cuts
    from one to the other along the path where they already match best, softened over
    [feather] px either side. A broad tone difference across the cut (say one roof a shade
    darker than the other) is eased out over the overlap so it doesn't show as a step."""
    n = max(1, int(a.shape[1] * blend))
    tail, head = a[:, -n:], a[:, :n]
    _, seam = _seam_path(_seam_cost(tail, head))
    x = np.arange(n)[None, :]
    w = np.clip((x - seam[:, None] + feather) / (2.0 * feather + 1), 0.0, 1.0)[..., None]
    # tone: the slow part of head - tail where both are painted, split half each side of the
    # cut and faded to nothing at the overlap's outer edges, which must stay as painted
    both = (np.minimum(tail[..., 3], head[..., 3]) > 200).astype(np.float64)
    diff = (head[..., :3] - tail[..., :3]) * both[..., None]
    soft = _blur(diff, 12) / np.maximum(_blur(both, 12), 1e-3)[..., None]
    soft *= (_blur(both, 12) > 0.5)[..., None]
    toward = np.clip(x / np.maximum(seam[:, None], 1), 0, 1)
    away = np.clip((n - 1 - x) / np.maximum(n - 1 - seam[:, None], 1), 0, 1)
    tail_fix, head_fix = tail.copy(), head.copy()
    tail_fix[..., :3] += soft * (0.5 * toward)[..., None]
    head_fix[..., :3] -= soft * (0.5 * away)[..., None]
    joined = tail_fix * (1.0 - w) + head_fix * w
    return np.concatenate([joined, a[:, n:-n]], axis=1)


def _blur(x: np.ndarray, radius: float) -> np.ndarray:
    """Gaussian blur (sigma [radius]) along both axes, edges clamped."""
    r = int(3 * radius)
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / radius) ** 2)
    k /= k.sum()
    out = x.astype(np.float64)
    for axis in (0, 1):
        pad = [(0, 0)] * out.ndim
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        out = sum(k[i] * np.take(p, np.arange(i, i + out.shape[axis]), axis=axis) for i in range(2 * r + 1))
    return out


def strip(im: Image.Image, width: int, blend: float = 0.12) -> Image.Image:
    """Tiles left to right: keeps about the middle 80% (generated ends are often rounded off),
    then joins the last [blend] onto the first along a cut where they match (see _seam_x).
    The window slides left or right and stretches by up to 4% to where the two ends match
    best, so the cut falls between doors and windows rather than through them and repeating
    things (garage doors, fence panels) keep their spacing across the join. The output size
    is always that of the plain middle 80%, so a better join never changes the file's size."""
    im = trim(im)
    inset = int(im.width * 0.1)
    keep0 = im.width - 2 * inset
    height = max(1, round(im.height * width / (keep0 - int(keep0 * blend))))
    a = np.asarray(im).astype(np.float32)
    best = None
    for keep in range(int(keep0 * 0.96), min(im.width, int(keep0 * 1.04)) + 1, max(1, keep0 // 100)):
        n = max(1, int(keep * blend))
        for x0 in range(0, im.width - keep + 1, max(1, inset // 16)):
            win = a[:, x0:x0 + keep]
            cost, _ = _seam_path(_seam_cost(win[:, -n:], win[:, :n]))
            if best is None or cost < best[0]:
                best = (cost, x0, keep)
    _, x0, keep = best
    out = _seam_x(a[:, x0:x0 + keep], blend)
    return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA").resize((width, height), Image.LANCZOS)


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


def _score(rgb: np.ndarray) -> np.ndarray:
    """How far each pixel stands out from the texture's usual colour: a painted patch is
    darker, lighter or warmer than the ground around it."""
    soft = _wrap_blur(rgb, 3)
    usual = np.median(rgb.reshape(-1, 3), axis=0)
    return np.maximum(np.abs((soft - usual).mean(2)) / 14,
                      ((soft[..., 0] - soft[..., 2]) - (usual[0] - usual[2])) / 12)


def _largest_part(mask: np.ndarray) -> np.ndarray:
    """Keeps only the biggest connected blob of a mask (wrapping), dropping stray specks."""
    h, w = mask.shape
    on = mask > 0.5
    seen = np.zeros_like(on)
    best: list = []
    for y0, x0 in zip(*np.nonzero(on)):
        if seen[y0, x0]:
            continue
        part, todo = [], [(y0, x0)]
        seen[y0, x0] = True
        while todo:
            y, x = todo.pop()
            part.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                ny, nx = ny % h, nx % w
                if on[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    todo.append((ny, nx))
        if len(part) > len(best):
            best = part
    out = np.zeros_like(mask)
    if best:
        ys, xs = zip(*best)
        out[list(ys), list(xs)] = 1
    return out


def _patch_mask(score: np.ndarray, box: list, threshold: float, what: str) -> np.ndarray:
    """The patch inside [box]: pixels scoring above [threshold], with small gaps closed."""
    h, w = score.shape
    x, y, bw, bh = box
    inside = np.zeros((h, w))
    inside[np.ix_(np.arange(y, y + bh) % h, np.arange(x, x + bw) % w)] = 1
    mask = _shrink(_grow((score > threshold) * inside, 6), 6)
    if mask.sum() < 400:
        sys.exit(f"{what}: no painted patch found in box {box}. If the source was repainted, "
                 "find the new patches and update the boxes in manifest.json.")
    return mask


def plain_texture(im: Image.Image, removes: list, what: str) -> Image.Image:
    """Lifts painted patches out of a tiling texture. Each one is filled with clean ground
    copied from elsewhere in the same texture, shifted to match the slow colour drift around
    the hole and feathered in, so grain and brushwork carry on through."""
    a = np.asarray(im.convert("RGBA")).astype(np.float64)
    rgb = a[..., :3]
    score = _score(rgb)
    masks = [_patch_mask(score, r["box"], r["threshold"], what) for r in removes]
    everything = np.clip(sum(masks), 0, 1)
    avoid = _grow(everything, 24)
    keep = 1.0 - _grow(everything, 10)
    drift = _wrap_blur(rgb * keep[..., None], 40) / np.maximum(_wrap_blur(keep, 40), 1e-3)[..., None]
    h, w = rgb.shape[:2]
    for mask in masks:
        hole = _grow(mask, 14)
        feather = np.maximum(np.clip(_wrap_blur(hole, 5), 0, 1), _grow(mask, 7))
        # How much patch a copy shifted by (dy, dx) would bring into the hole, for every
        # shift at once: a circular cross-correlation.
        overlap = np.real(np.fft.ifft2(np.fft.fft2(avoid) * np.conj(np.fft.fft2(hole))))
        best = None
        for dy in range(-h // 2, h // 2 + 1, 16):
            for dx in range(-w // 2, w // 2 + 1, 16):
                if abs(dx) < 120 and abs(dy) < 120:
                    continue
                cost = round(float(overlap[dy % h, dx % w]), 3)
                if best is None or cost < best[0]:
                    best = (cost, dx, dy)
        _, dx, dy = best
        fill = np.roll(a, (-dy, -dx), (0, 1))
        fill[..., :3] += drift - np.roll(drift, (-dy, -dx), (0, 1))
        a = a * (1 - feather[..., None]) + fill * feather[..., None]
    return Image.fromarray(np.rint(a).clip(0, 255).astype(np.uint8), "RGBA")


def cutout(im: Image.Image, box: list, threshold: float, what: str) -> Image.Image:
    """One painted patch from a texture, with a soft edge, on transparency."""
    a = np.asarray(im.convert("RGBA")).astype(np.float64)
    mask = _largest_part(_patch_mask(_score(a[..., :3]), box, threshold, what))
    alpha = np.clip(_wrap_blur(_grow(mask, 3), 1.5), 0, 1)
    a[..., 3] = alpha * 255
    # roll the patch away from the edges so it is in one piece, then trim
    x, y, bw, bh = box
    a = np.roll(a, (a.shape[0] // 2 - (y + bh // 2), a.shape[1] // 2 - (x + bw // 2)), (0, 1))
    return trim(Image.fromarray(np.rint(a).clip(0, 255).astype(np.uint8), "RGBA"))


def derive() -> int:
    """Rebuilds every output made from another kit file. Returns how many were written."""
    m = json.loads(MANIFEST.read_text())
    done = 0
    sources: dict = {}
    for asset in m["assets"]:
        for out in asset.get("outputs", []):
            if not out.get("from"):
                continue
            if out["from"] not in sources:
                sources[out["from"]] = Image.open(ROOT / out["from"]).convert("RGBA")
            im = sources[out["from"]]
            what = f"{asset['id']} ({out['path']})"
            if out["mode"] == "plain_texture":
                res = plain_texture(im, out["remove"], what)
            elif out["mode"] == "cutout":
                res = cutout(im, out["box"], out["threshold"], what)
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
            elif mode == "seamless":
                side = min(im.size)
                res = im.crop(((im.width - side) // 2, (im.height - side) // 2, (im.width + side) // 2,
                               (im.height + side) // 2)).resize((width, width), Image.LANCZOS)
            elif mode == "slice":
                res = fit_width(slice_row(im, int(out["count"]), int(out["index"])), width)
            else:
                sys.exit(f"{asset['id']}: unknown mode {mode!r}")
            if out.get("same_size_as"):
                twin = next(o for a in m["assets"] for o in a.get("outputs", []) if o["path"] == out["same_size_as"])
                res = res.resize(tuple(twin["size"]), Image.LANCZOS)
            dest = ROOT / out["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            res.save(dest, optimize=True)
            out["size"] = [res.width, res.height]
            out["sha12"] = sha12(dest)
            print(f"{out['path']}  {res.width}x{res.height}  {out['sha12']}")
            done += 1
    MANIFEST.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
    print(f"{done} file(s) written; manifest.json updated.")
    written = {out["path"] for a in m["assets"] for out in a.get("outputs", [])
               if out.get("raw") and (raw_dir / f"{out['raw']}.png").exists()}
    stale = sorted({out["path"] for a in m["assets"] for out in a.get("outputs", []) if out.get("from") in written})
    if stale:
        print("These are made from a file you just rewrote. Check their boxes still sit on the new "
              "painting, then run --derive:\n  " + "\n  ".join(stale))


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
