"""The First Batch finish step, 4K render in, track cover master out.

  The backdrop is rebuilt, never kept: a smooth gradation of the track swatch, shaped like Josh's
  Deluge v1 Photoshop backdrop (pipeline/backdrop_template.npz), one hue and chroma edge to edge.
  From the render it takes only three things: the device and dough (untouched, edges cleaned of the
  old backdrop color), the contact shadows where they meet the floor, and the film grain.
  Every other light or dark patch the generator painted into its backdrop is dropped.

  1. isolate device and dough (rembg u2net + isnet, holes filled)
  2. backdrop lightness = swatch lightness + falloff x the Deluge template, on a 6704 square
  3. contact shadows: the render's own darkening (never its brightening) at the floor line under each
     part of the device and in a narrow band hugging it, so gaps between parts stay in shade
  4. grain synthesized from the render's own backdrop, lightness only
  5. one paper: OKLab lightness kept, hue and chroma from the swatch
  6. the render placed at 1:1 in the center, device composited with its edge pixels decontaminated
  7. export a max quality 4:4:4 JPG

usage: python3 pipeline/finish.py RENDER HEX OUT.jpg [--falloff 1.0] [--canvas 6704] [--report report.json] [--quality 97]
  always prints the report as JSON. Also writes OUT_alpha_small.npy (device mask) for pipeline/framing.py
"""
import argparse, json, os
import numpy as np, cv2
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
LOW = 8
ELLIPSE = (0.51, 0.534, 0.207, 0.37)  # cx, cy, rx, ry as canvas fractions, from Josh's Deluge check
TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backdrop_template.npz')
SHADOW_REF = 0.02  # canvas fraction: blur that defines the local floor brightness a contact shadow is measured against
SHADOW_ZONE = (0.035, 0.06)  # canvas fraction above and below each column's floor line where shadows are kept
SHADOW_HUG = (0.006, 0.012)  # canvas fraction: shade kept fully this close to the device, fading out by the second value (gaps, occlusion)


def srgb_to_lin(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lin_to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)


M1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]], np.float32)
M2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]], np.float32)
M2i, M1i = np.linalg.inv(M2).astype(np.float32), np.linalg.inv(M1).astype(np.float32)


def oklab(lin):
    return np.cbrt(lin @ M1.T) @ M2.T


def oklab_to_lin(lab):
    return (lab @ M2i.T) ** 3 @ M1i.T


def one_paper(rgb255, sw_ok):
    """One paper, lit unevenly: keep each pixel's OKLab lightness, take hue and chroma from the swatch.
    That is how Deluge v1 behaves (flat OKLab chroma, hue within 4 degrees). Where a light or dark pixel
    cannot hold the swatch chroma inside sRGB, chroma eases off instead of clipping, so hue never moves."""
    L = oklab(srgb_to_lin(rgb255 / 255.))[..., 0]
    out = np.empty(L.shape + (3,), np.float32)
    k = np.ones(L.shape, np.float32)
    for _ in range(12):
        lab = np.stack([L, sw_ok[1] * k, sw_ok[2] * k], -1)
        out = oklab_to_lin(lab)
        bad = (out.min(-1) < -1e-4) | (out.max(-1) > 1 + 1e-4)
        if not bad.any():
            break
        k = np.where(bad, k * 0.85, k)
    return lin_to_srgb(out) * 255.


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


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
    hexs = hexs.lstrip("#")
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
    ap.add_argument('--falloff', type=float, default=1.0, help='depth of the template falloff, 1.0 = Deluge v1, lower = lighter corners')
    a = ap.parse_args()
    rep = {'falloff': a.falloff}
    R = np.array(Image.open(a.render).convert('RGB'))
    H, W = R.shape[:2]
    S = max(a.canvas, W, H)
    ox, oy = (S - W) // 2, (S - H) // 2
    rep.update(render=[W, H], canvas=S, offset=[ox, oy])
    step = 1024

    alpha = device_mask(R)
    alpha = np.clip((alpha - 0.1) / 0.8, 0, 1); alpha = alpha * alpha * (3 - 2 * alpha)   # tighter soft edge, no fringe of old floor
    edge_fg = max(alpha[:24].max(), alpha[-24:].max(), alpha[:, :24].max(), alpha[:, -24:].max())
    rep['device_touches_edge'] = bool(edge_fg > 0.5)
    t = hex_lab(a.hex)
    Lt = float(t[0])
    sw_rgb = np.array([int(a.hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.
    sw_ok = oklab(srgb_to_lin(sw_rgb))

    # ---- low res: the old render backdrop with the device filled, used to clean the device's edge pixels ----
    n = S // LOW
    hs, ws = H // LOW, W // LOW
    oys, oxs = oy // LOW, ox // LOW
    Rs = cv2.resize(R, (ws, hs), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.
    As = cv2.resize(alpha, (ws, hs), interpolation=cv2.INTER_AREA)
    known = (As < 0.1).astype(np.float32)                                     # tight, so floor pixels right at the device count
    Rb = np.where(known[..., None] > 0, Rs, push_pull(Rs, known))            # old backdrop, device filled

    # ---- contact shadows at half res: darker than the local floor, only in a band at each column's floor line ----
    h2, w2 = H // 2, W // 2
    R2 = cv2.resize(R, (w2, h2), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.
    A2 = cv2.resize(alpha, (w2, h2), interpolation=cv2.INTER_AREA)
    k2 = (A2 < 0.05).astype(np.float32)
    Y2 = srgb_to_lin(R2) @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    Y2 = np.where(k2 > 0, Y2, push_pull(np.repeat(Y2[..., None], 3, -1), k2)[..., 0])
    Yref = cv2.GaussianBlur(Y2, (0, 0), (S / 2) * SHADOW_REF)
    sh2 = np.clip(Y2 / np.maximum(Yref, 1e-4), 0, 1)
    dev = A2 > 0.5
    rows = np.arange(h2, dtype=np.float32)[:, None]
    bottom = np.where(dev.any(0), (dev * rows).max(0), -1).astype(np.float32)
    span = max(1, int(S / 2 * 0.03))
    bottom = cv2.dilate(bottom[None], np.ones((1, 2 * span + 1)))[0]           # bridge small gaps between parts
    up, down = S / 2 * SHADOW_ZONE[0], S / 2 * SHADOW_ZONE[1]
    zone = ((rows >= bottom[None] - up) & (rows <= bottom[None] + down) & (bottom[None] >= 0)).astype(np.float32)
    zone = cv2.GaussianBlur(zone, (0, 0), S / 2 * 0.01)
    dist = cv2.distanceTransform((A2 < 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    h0, h1 = S / 2 * SHADOW_HUG[0], S / 2 * SHADOW_HUG[1]
    hug = np.clip((h1 - dist) / (h1 - h0), 0, 1)
    zone = np.maximum(zone, hug * hug * (3 - 2 * hug))
    sh2 = 1 - zone * (1 - sh2)
    rep['shadow_min'] = round(float(sh2.min()), 3)
    shade_r = cv2.resize(sh2, (W, H), interpolation=cv2.INTER_LINEAR)
    del R2, A2, k2, Y2, Yref, zone, sh2, dist, hug

    # ---- backdrop: smooth swatch gradation from the Deluge template ----
    tp = np.load(TEMPLATE)
    rep['template'] = str(tp['source'])
    TL = Lt + a.falloff * cv2.resize(tp['dL'], (n, n), interpolation=cv2.INTER_CUBIC)
    lab_n = np.stack([np.clip(TL, 0, 100), np.full((n, n), t[1]), np.full((n, n), t[2])], -1).astype(np.float32)

    # ---- full res: gradation + grain, contact shadows in linear light, one paper ----
    R_lab = np.empty((H, W, 3), np.float32)
    for y in range(0, H, step):
        R_lab[y:y + step] = cv2.cvtColor(R[y:y + step].astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
    amp, npatch = texture_spectra(R_lab, alpha)
    rep['texture_patches'] = npatch
    del R_lab
    canvas_lab = cv2.resize(lab_n, (S, S), interpolation=cv2.INTER_CUBIC)
    if amp is not None:
        canvas_lab[..., 0] += synth_texture((S, S), amp, np.random.default_rng(7))[..., 0]
    shade_f = np.ones((S, S), np.float32); shade_f[oy:oy + H, ox:ox + W] = shade_r
    del shade_r
    canvas = np.empty((S, S, 3), np.float32)
    for y in range(0, S, step):
        lin = srgb_to_lin(np.clip(cv2.cvtColor(canvas_lab[y:y + step], cv2.COLOR_LAB2RGB), 0, 1)) * shade_f[y:y + step, :, None]
        canvas[y:y + step] = one_paper(lin_to_srgb(lin) * 255., sw_ok)
    del canvas_lab, shade_f

    # ---- the device on top, edge pixels freed of the old backdrop color ----
    Bold = cv2.resize(Rb, (W, H), interpolation=cv2.INTER_LINEAR) * 255.
    for y in range(0, H, step):
        al = alpha[y:y + step, :, None]
        C = R[y:y + step].astype(np.float32)
        F = np.where(al > 0.98, C, np.clip((C - (1 - al) * Bold[y:y + step]) / np.maximum(al, 0.02), 0, 255))
        sub = canvas[oy + y:oy + y + al.shape[0], ox:ox + W]
        canvas[oy + y:oy + y + al.shape[0], ox:ox + W] = F * al + sub * (1 - al)
    del Bold
    A = np.zeros((S, S), np.float32); A[oy:oy + H, ox:ox + W] = alpha

    # ---- check: glow vs swatch, corners, hue spread ----
    m = S // LOW
    cs = cv2.resize(canvas, (m, m), interpolation=cv2.INTER_AREA) / 255.
    As_c = cv2.resize(A, (m, m), interpolation=cv2.INTER_AREA)
    gy, gx = np.mgrid[0:m, 0:m] / m
    ecx, ecy, erx, ery = ELLIPSE
    ellc = ((gx - ecx) / erx) ** 2 + ((gy - ecy) / ery) ** 2 <= 1
    bgall = cv2.dilate((As_c > 0.02).astype(np.uint8), np.ones((15, 15))) == 0
    lab_c = cv2.cvtColor(cs.astype(np.float32), cv2.COLOR_RGB2LAB)
    g2 = np.median(lab_c[ellc & bgall], axis=0)
    rep['glow_after_rgb'] = np.median(cs[ellc & bgall] * 255, axis=0).round(1).tolist()
    rep['deltaE_glow_vs_swatch'] = round(float(np.linalg.norm(g2 - t)), 2)
    okc = oklab(srgb_to_lin(cs.astype(np.float32)))
    hb = np.degrees(np.arctan2(okc[..., 2], okc[..., 1]))[bgall]
    rep['backdrop_hue_spread_deg'] = round(float(np.percentile(hb, 95) - np.percentile(hb, 5)), 2)
    c = m // 16
    rep['corner_L_minus_glow'] = [round(float(np.median(lab_c[sl][..., 0]) - g2[0]), 1) for sl in
                                  ((slice(0, c), slice(0, c)), (slice(0, c), slice(m - c, m)), (slice(m - c, m), slice(0, c)), (slice(m - c, m), slice(m - c, m)))]

    Image.fromarray(np.round(np.clip(canvas, 0, 255)).astype(np.uint8)).save(a.out, quality=a.quality, subsampling=0, optimize=True, dpi=(72, 72))
    rep['out_bytes'] = os.path.getsize(a.out)
    np.save(os.path.splitext(a.out)[0] + '_alpha_small.npy', cv2.resize(A, (S // 4, S // 4), interpolation=cv2.INTER_AREA))
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
