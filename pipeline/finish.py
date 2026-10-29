"""The First Batch finish step, 4K render in, track cover master out.

  1. place the render untouched at 1:1 in the center of a square canvas (6704 by default, Deluge v1's size)
  2. extend the seamless backdrop to the canvas edges: anchored to the render's own border, continuing
     each edge's light falloff, with film grain and mottle synthesized from the render's own backdrop
  3. isolate device and dough from the backdrop (rembg u2net + isnet, holes filled)
  4. recolor the backdrop only, like Josh's Deluge layers: keep lightness, pull chroma and hue so the
     glow behind the device (his check ellipse, real render pixels) lands on the track swatch
  5. export a max quality 4:4:4 JPG, about 12 to 14 MB at 6704 square

usage: python3 pipeline/finish.py RENDER HEX OUT.jpg [--canvas 6704] [--report report.json] [--quality 97]
  always prints the report as JSON. Also writes OUT_alpha_small.npy (device mask) for pipeline/framing.py
"""
import argparse, json, os
import numpy as np, cv2
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
LOW = 8
ELLIPSE = (0.51, 0.534, 0.207, 0.37)  # cx, cy, rx, ry as canvas fractions, from Josh's Deluge check


def device_mask(rgb):
    from rembg import remove, new_session
    h, w = rgb.shape[:2]
    sw = 1600
    small = Image.fromarray(rgb).resize((sw, round(sw * h / w)), Image.LANCZOS)
    ms = [np.array(remove(small, session=new_session(n), only_mask=True)) for n in ('u2net', 'isnet-general-use')]
    m = np.maximum(ms[0], ms[1])
    hard = (m > 100).astype(np.uint8)
    ff = hard.copy()
    pad = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
    cv2.floodFill(ff, pad, (0, 0), 2)
    m = m.astype(np.float32) / 255.
    m[ff == 0] = 1.0  # enclosed holes belong to the device
    m = cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
    return np.clip(cv2.GaussianBlur(m, (0, 0), 1.5), 0, 1)


def push_pull(V, w):
    """Smooth fill of V where w == 0 from pixels where w == 1."""
    levels = []
    num = V * w[..., None]; den = w.astype(np.float32)
    while min(den.shape) > 2:
        levels.append((num, den))
        sz = (max(1, num.shape[1] // 2), max(1, num.shape[0] // 2))
        num = cv2.resize(cv2.GaussianBlur(num, (0, 0), 1.0), sz, interpolation=cv2.INTER_AREA) * 4
        den = cv2.resize(cv2.GaussianBlur(den, (0, 0), 1.0), sz, interpolation=cv2.INTER_AREA) * 4
    fill = num / np.maximum(den, 1e-6)[..., None]
    for num, den in reversed(levels):
        up = cv2.resize(fill, (den.shape[1], den.shape[0]), interpolation=cv2.INTER_LINEAR)
        est = num / np.maximum(den, 1e-6)[..., None]
        a = np.clip(den / 0.5, 0, 1)[..., None]
        fill = est * a + up * (1 - a)
    return fill


def edge_slope_profiles(Lch, w, frac=(0.03, 0.15)):
    """Outward lightness slope (L per low-res px) along each edge, per column or row, smoothed."""
    h, wd = Lch.shape
    def prof(Lb, wb, Li, wi, dist, n_out):
        sb = (Lb * wb).sum(0); cb = wb.sum(0); si = (Li * wi).sum(0); ci = wi.sum(0)
        ok = (cb > 2) & (ci > 2)
        sl = np.zeros(n_out, np.float32)
        sl[ok] = (sb[ok] / cb[ok] - si[ok] / ci[ok]) / dist
        wt = ok.astype(np.float32); sig = max(3.0, n_out * 0.05)
        num = cv2.GaussianBlur((sl * wt)[None], (0, 0), sigmaX=sig, sigmaY=0.1)[0]
        den = cv2.GaussianBlur(wt[None], (0, 0), sigmaX=sig, sigmaY=0.1)[0]
        return np.where(den > 1e-3, num / np.maximum(den, 1e-3), 0).astype(np.float32)
    a, b = max(1, int(frac[0] * h)), int(frac[1] * h)
    c, d = max(1, int(frac[0] * wd)), int(frac[1] * wd)
    top = prof(Lch[:a], w[:a], Lch[a:b], w[a:b], b / 2.0, wd)
    bot = prof(Lch[h - a:], w[h - a:], Lch[h - b:h - a], w[h - b:h - a], b / 2.0, wd)
    lft = prof(Lch[:, :c].T, w[:, :c].T, Lch[:, c:d].T, w[:, c:d].T, d / 2.0, h)
    rgt = prof(Lch[:, wd - c:].T, w[:, wd - c:].T, Lch[:, wd - d:wd - c].T, w[:, wd - d:wd - c].T, d / 2.0, h)
    return top, bot, lft, rgt


def texture_spectra(R_lab, alpha, patch=512, sigma=48):
    """Amplitude spectra of the render's backdrop texture (grain + mottle), per Lab channel."""
    h, w = alpha.shape
    fgd = cv2.dilate((alpha > 0.02).astype(np.uint8), np.ones((31, 31)))
    win = np.outer(np.hanning(patch), np.hanning(patch)).astype(np.float32)
    specs = []
    for y in range(0, h - patch + 1, patch // 2):
        for x in range(0, w - patch + 1, patch // 2):
            if fgd[y:y + patch, x:x + patch].any():
                continue
            p = R_lab[y:y + patch, x:x + patch]
            hp = p - cv2.GaussianBlur(p, (0, 0), sigma)
            specs.append(np.abs(np.fft.fft2(hp * win[..., None], axes=(0, 1))) ** 2)
    if not specs:
        return None, 0
    P = np.mean(specs, 0) / (win ** 2).sum()
    return np.sqrt(P).astype(np.float32), len(specs)


def synth_texture(shape, amp, rng):
    """Random-phase noise with the measured amplitude spectrum, per channel on the full canvas."""
    H, W = shape
    patch = amp.shape[0]
    out = np.zeros((H, W, 3), np.float32)
    iy = (np.round(np.fft.fftfreq(H) * patch) % patch).astype(int)[:, None]
    ix = (np.round(np.fft.fftfreq(W) * patch) % patch).astype(int)[None, :]
    for c in range(3):
        A = amp[..., c][iy, ix]
        z = np.fft.fft2(rng.standard_normal((H, W)).astype(np.float32))
        out[..., c] = np.real(np.fft.ifft2(z * A)).astype(np.float32)
        del A, z
    return out


def hex_lab(hexs):
    rgb = np.array([[[int(hexs[i:i + 2], 16) for i in (0, 2, 4)]]], np.float32) / 255.
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[0, 0]


def lch(lab):
    return lab[..., 0], np.hypot(lab[..., 1], lab[..., 2]), np.arctan2(lab[..., 2], lab[..., 1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('render'); ap.add_argument('hex'); ap.add_argument('out')
    ap.add_argument('--canvas', type=int, default=6704)
    ap.add_argument('--report')
    ap.add_argument('--quality', type=int, default=97)
    a = ap.parse_args()
    rep = {}
    R = np.array(Image.open(a.render).convert('RGB'))
    H, W = R.shape[:2]
    S = max(a.canvas, W, H)
    ox, oy = (S - W) // 2, (S - H) // 2
    rep.update(render=[W, H], canvas=S, offset=[ox, oy])

    alpha = device_mask(R)
    edge_fg = max(alpha[:24].max(), alpha[-24:].max(), alpha[:, :24].max(), alpha[:, -24:].max())
    rep['device_touches_edge'] = bool(edge_fg > 0.5)

    # ---- backdrop extension, low res Lab ----
    n = S // LOW
    hs, ws = H // LOW, W // LOW
    oys, oxs = oy // LOW, ox // LOW
    Rs = cv2.cvtColor(cv2.resize(R, (ws, hs), interpolation=cv2.INTER_AREA).astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
    As = cv2.resize(alpha, (ws, hs), interpolation=cv2.INTER_AREA)
    fg = cv2.dilate((As > 0.02).astype(np.uint8), np.ones((5, 5)))
    known = (fg == 0).astype(np.float32)
    Rb = np.where(known[..., None] > 0, Rs, push_pull(Rs, known))      # backdrop only, device filled
    Rb = cv2.GaussianBlur(Rb, (0, 0), 1.5)
    pad = cv2.copyMakeBorder(Rb, oys, n - hs - oys, oxs, n - ws - oxs, cv2.BORDER_REPLICATE)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    d_top = np.clip(oys - yy, 0, None); d_bot = np.clip(yy - (oys + hs - 1), 0, None)
    d_lft = np.clip(oxs - xx, 0, None); d_rgt = np.clip(xx - (oxs + ws - 1), 0, None)
    dist = np.hypot(np.maximum(d_top, d_bot), np.maximum(d_lft, d_rgt))
    # smooth more the farther out we go, so edge detail fades into broad light
    ext = pad.copy()
    for sig, scale in ((n * 0.015, 0.03), (n * 0.05, 0.08), (n * 0.12, 0.18)):
        k = (1 - np.exp(-dist / (n * scale)))[..., None]
        ext = ext * (1 - k) + cv2.GaussianBlur(pad, (0, 0), sig) * k
    top, bot, lft, rgt = edge_slope_profiles(Rs[..., 0], known)
    cx = np.clip(xx - oxs, 0, ws - 1).astype(int); cy = np.clip(yy - oys, 0, hs - 1).astype(int)
    tau = 900.0 / LOW
    f = lambda d: tau * (1 - np.exp(-d / tau))
    dL = top[cx] * f(d_top) + bot[cx] * f(d_bot) + lft[cy] * f(d_lft) + rgt[cy] * f(d_rgt)
    dL = cv2.GaussianBlur(np.clip(dL, -22, 8), (0, 0), 3)
    base_L = ext[..., 0].copy()
    ext[..., 0] = np.clip(base_L + dL, 0, 100)
    sc = np.clip(ext[..., 0] / np.maximum(base_L, 1), 0.6, 1.2)  # chroma eases with lightness
    ext[..., 1] *= sc; ext[..., 2] *= sc
    del pad, yy, xx, base_L

    # ---- full res: smooth extension + matched texture, then the untouched render on top ----
    R_lab_full = cv2.cvtColor(R.astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
    amp, npatch = texture_spectra(R_lab_full, alpha)
    rep['texture_patches'] = npatch
    del R_lab_full
    canvas_lab = cv2.resize(ext, (S, S), interpolation=cv2.INTER_CUBIC)
    del ext
    if amp is not None:
        canvas_lab += synth_texture((S, S), amp, np.random.default_rng(7))
    canvas = np.empty((S, S, 3), np.float32)
    step = 1024
    for y in range(0, S, step):
        canvas[y:y + step] = np.clip(cv2.cvtColor(canvas_lab[y:y + step], cv2.COLOR_LAB2RGB), 0, 1) * 255.
    del canvas_lab
    fw = 32
    ramp = np.ones((H, W), np.float32)
    r = np.linspace(0, 1, fw, dtype=np.float32)
    ramp[:fw] *= r[:, None]; ramp[-fw:] *= r[::-1][:, None]
    ramp[:, :fw] *= r[None]; ramp[:, -fw:] *= r[::-1][None]
    ramp = np.maximum(ramp, (alpha > 0.02).astype(np.float32))
    sub = canvas[oy:oy + H, ox:ox + W]
    canvas[oy:oy + H, ox:ox + W] = R.astype(np.float32) * ramp[..., None] + sub * (1 - ramp[..., None])
    del sub, ramp
    A = np.zeros((S, S), np.float32); A[oy:oy + H, ox:ox + W] = alpha

    # ---- backdrop recolor to the swatch ----
    m = S // LOW
    cs = cv2.resize(canvas, (m, m), interpolation=cv2.INTER_AREA) / 255.
    As_c = cv2.resize(A, (m, m), interpolation=cv2.INTER_AREA)
    gy, gx = np.mgrid[0:m, 0:m] / m
    ecx, ecy, erx, ery = ELLIPSE
    ell = ((gx - ecx) / erx) ** 2 + ((gy - ecy) / ery) ** 2 <= 1
    real = np.zeros((m, m), bool); real[oy // LOW + 4:(oy + H) // LOW - 4, ox // LOW + 4:(ox + W) // LOW - 4] = True
    bgm = ell & real & (cv2.dilate((As_c > 0.02).astype(np.uint8), np.ones((15, 15))) == 0)
    lab_s = cv2.cvtColor(cs.astype(np.float32), cv2.COLOR_RGB2LAB)
    g = np.median(lab_s[bgm], axis=0); t = hex_lab(a.hex)
    Lg, Cg, hg = [float(v) for v in lch(g)]
    Lt, Ct, ht = [float(v) for v in lch(t)]
    gamma = float(np.log(Lt / 100.) / np.log(Lg / 100.)); dh = float(ht - hg)
    rep.update(glow_before_lab=g.round(2).tolist(), target_lab=t.round(2).tolist(),
               L_gamma=round(gamma, 4), chroma_before=round(Cg, 2), chroma_target=round(Ct, 2),
               hue_shift_deg=round(float(np.degrees(dh)), 2))
    for y in range(0, S, step):
        lab = cv2.cvtColor(canvas[y:y + step] / 255., cv2.COLOR_RGB2LAB)
        L, C, h = lch(lab)
        L2 = 100. * np.power(np.clip(L / 100., 1e-6, 1), gamma)
        C2 = Ct * np.power(np.maximum(C, 1e-3) / max(Cg, 1e-3), 0.12)
        h2 = h + dh
        lab2 = np.stack([L2, C2 * np.cos(h2), C2 * np.sin(h2)], -1).astype(np.float32)
        rgb2 = np.clip(cv2.cvtColor(lab2, cv2.COLOR_LAB2RGB), 0, 1) * 255.
        al = A[y:y + step, :, None]
        canvas[y:y + step] = rgb2 * (1 - al) + canvas[y:y + step] * al
    cs2 = cv2.resize(canvas, (m, m), interpolation=cv2.INTER_AREA) / 255.
    g2 = np.median(cv2.cvtColor(cs2.astype(np.float32), cv2.COLOR_RGB2LAB)[bgm], axis=0)
    rep['glow_after_rgb'] = np.median(cs2[bgm] * 255, axis=0).round(1).tolist()
    rep['deltaE_glow_vs_swatch'] = round(float(np.linalg.norm(g2 - t)), 2)

    Image.fromarray(np.round(canvas).astype(np.uint8)).save(a.out, quality=a.quality, subsampling=0, optimize=True, dpi=(72, 72))
    rep['out_bytes'] = os.path.getsize(a.out)
    np.save(os.path.splitext(a.out)[0] + '_alpha_small.npy', cv2.resize(A, (S // 4, S // 4), interpolation=cv2.INTER_AREA))
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
