# Album master finish (Nov 9 2026). The 4K render keeps the dough record, its contact shadow and grain;
# the pinwheel backdrop is redrawn in the exact 500 step hexes at the wedge angles measured from the render.
# python3 pipeline/finish_album.py RENDER.png OUT.jpg [--size 6704]
import sys, json, math, argparse, numpy as np
from PIL import Image
from scipy import ndimage
HEX = ["#6C8DCE", "#ECCE7B", "#C77171", "#65B8E5", "#E99CC2", "#82A967", "#8E74B7", "#DE9F65", "#73D2AB"]
NAMES = ["blueberry", "butter", "cherry", "bondi", "bubblegum", "lime", "grape", "tangerine", "mint"]
rgb = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], float)
COLS = np.stack([rgb(h) for h in HEX])
def lab(a):
    a = a / 255.0; a = np.where(a > 0.04045, ((a + 0.055) / 1.055) ** 2.4, a / 12.92)
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = a @ M.T / np.array([0.95047, 1, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("render"); ap.add_argument("out"); ap.add_argument("--size", type=int, default=6704); a = ap.parse_args()
    R = np.asarray(Image.open(a.render).convert("RGB")).astype(float); H, W, _ = R.shape; cx, cy = W / 2, H / 2
    # 1 matte: rembg u2net on a 2048 copy (color rules failed where the dough sits in its own shadow, Nov 9 2026)
    from rembg import remove, new_session
    src = Image.fromarray(R.astype(np.uint8))
    m = remove(src.resize((2048, 2048), Image.LANCZOS), session=new_session("u2net"), only_mask=True, post_process_mask=True)
    soft = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(float) / 255
    disc = soft > 0.5
    d_lab = np.linalg.norm(lab(R)[..., None, :] - lab(COLS)[None, None], axis=-1)
    near = d_lab.min(-1); cls = d_lab.argmin(-1)
    # 2 wedge boundaries from the render, sampled on rings outside the disc
    dist_out = ndimage.distance_transform_edt(~disc)
    ang = (np.degrees(np.arctan2(np.arange(H)[:, None] - cy, np.arange(W)[None, :] - cx)) + 360) % 360
    ring = (dist_out > 40) & (near < 25)
    bins = np.zeros((1440, 9))
    np.add.at(bins, ((ang[ring] * 4).astype(int) % 1440, cls[ring]), 1)
    lab_bins = bins.argmax(1); has = bins.sum(1) > 0
    # fill empty bins from neighbours
    idx = np.where(has)[0]
    lab_bins = lab_bins[idx[np.abs(np.arange(1440)[:, None] - idx[None]).argmin(1)]]
    lab_bins = ndimage.median_filter(lab_bins, size=9, mode="wrap")
    # 3 shadow multiplier: render luminance over its wedge's own flat level, near the disc only
    L = R.mean(-1)
    flat = np.zeros(9)
    far = (dist_out > 250) & (near < 25)
    for k in range(9):
        m = far & (cls == k); flat[k] = np.median(L[m]) if m.sum() > 1000 else L[cls == k].mean()
    wedge_img = lab_bins[(ang * 4).astype(int) % 1440]
    mult = np.clip(L / flat[wedge_img], 0.35, 1.0)
    w = np.clip(1 - dist_out / 220.0, 0, 1) ** 1.5; w[disc] = 0
    mult = 1 - (1 - mult) * w
    mult = ndimage.gaussian_filter(mult, 3)
    # grain: high pass of the render backdrop
    hp = R - ndimage.gaussian_filter(R, (1.6, 1.6, 0))
    gstd = hp[far].std(0)
    # 4 build at the output size
    S = a.size; k = S / W
    Ri = np.asarray(Image.fromarray(R.astype(np.uint8)).resize((S, S), Image.LANCZOS)).astype(float)
    alpha = np.asarray(Image.fromarray((soft * 255).astype(np.uint8)).resize((S, S), Image.LANCZOS)).astype(float) / 255
    alpha = np.clip((alpha - 0.15) / 0.7, 0, 1)[..., None]
    multS = np.asarray(Image.fromarray((mult * 255).astype(np.uint8)).resize((S, S), Image.BILINEAR)).astype(float)[..., None] / 255
    yy, xx = np.mgrid[0:S, 0:S]
    angS = (np.degrees(np.arctan2(yy - S / 2, xx - S / 2)) + 360) % 360
    # supersampled wedge colors: blend across the boundary using sub bin position
    b = angS * 4; i0 = b.astype(int) % 1440; i1 = (i0 + 1) % 1440; t = (b - np.floor(b))[..., None]
    base = COLS[lab_bins[i0]] * (1 - t) + COLS[lab_bins[i1]] * t
    rng = np.random.default_rng(7)
    grain = ndimage.gaussian_filter(rng.standard_normal((S, S)), 0.9 * k)
    grain = grain / grain.std() * gstd.mean()
    back = base * multS + grain[..., None]
    out = alpha * Ri + (1 - alpha) * back
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(a.out, quality=95, subsampling=0)
    # report
    O = np.asarray(Image.open(a.out).convert("RGB")).astype(float)
    rep = {"out": a.out, "size": S, "disc_frac": round(float(disc.mean()), 3), "grain_std": [round(float(x), 2) for x in gstd],
           "wedge_dE": {}, "boundaries_deg": []}
    for kk in range(9):
        m = np.where(lab_bins == kk)[0]
        if not len(m): continue
        mid = math.radians(np.median(m) / 4); r = 0.48 * S
        x, y = int(S / 2 + r * math.cos(mid)), int(S / 2 + r * math.sin(mid))
        s = O[y - 60:y + 60, x - 60:x + 60].reshape(-1, 3).mean(0)
        rep["wedge_dE"][NAMES[kk]] = round(float(np.linalg.norm(lab(s[None])[0] - lab(COLS[kk][None])[0])), 2)
    rep["boundaries_deg"] = [round(i / 4, 2) for i in range(1440) if lab_bins[i] != lab_bins[i - 1]]
    print(json.dumps(rep))
if __name__ == "__main__":
    main()
