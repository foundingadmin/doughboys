"""The First Batch finish step, 4K render in, track cover master out.

  1. isolate device and dough from the backdrop (rembg u2net + isnet, holes filled)
  2. recolor the render's backdrop only: shift lightness so the glow behind the device (Josh's Deluge
     check ellipse, real render pixels) lands on the swatch, keep the render's own light shape, pull
     chroma almost flat to the swatch and ease hue drift toward it. Device and dough stay untouched
  3. place the render at 1:1 in the center of a square canvas (6704 by default, Deluge v1's size)
  4. extend the backdrop with the falloff template from Deluge v1 (pipeline/backdrop_template.npz),
     colored to the swatch. Near the render the render's own backdrop wins, fading into the template
     with distance, so every cover falls off like Deluge. Film grain and mottle are synthesized from
     the render's own backdrop
  5. one paper, lit unevenly: every backdrop pixel keeps its OKLab lightness and takes hue and chroma
     from the swatch, like Deluge v1, so the backdrop holds one green (or blue) and only light, shadow
     and grain vary
  6. export a max quality 4:4:4 JPG, about 12 to 14 MB at 6704 square

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
HUE_KEEP = 0.5     # share of the render's own hue drift kept after the recolor
FADE = 0.04        # canvas fraction over which the render's edge detail fades out past its border
BROAD = 0.05       # blur, as a canvas fraction, that splits broad light from shadows and mottle
HANDOVER = (0.45, 1.05)  # radial distance from the glow (0.5 = canvas edge) where broad light goes from render to template


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

    alpha = device_mask(R)
    edge_fg = max(alpha[:24].max(), alpha[-24:].max(), alpha[:, :24].max(), alpha[:, -24:].max())
    rep['device_touches_edge'] = bool(edge_fg > 0.5)

    # ---- glow behind the device, real render pixels inside Josh's ellipse ----
    hs, ws = H // LOW, W // LOW
    Rs = cv2.cvtColor(cv2.resize(R, (ws, hs), interpolation=cv2.INTER_AREA).astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
    As = cv2.resize(alpha, (ws, hs), interpolation=cv2.INTER_AREA)
    fg = cv2.dilate((As > 0.02).astype(np.uint8), np.ones((5, 5)))
    known = (fg == 0).astype(np.float32)
    gy, gx = np.mgrid[0:hs, 0:ws].astype(np.float32)
    gx = (gx * LOW + ox) / S; gy = (gy * LOW + oy) / S
    ecx, ecy, erx, ery = ELLIPSE
    ell = (((gx - ecx) / erx) ** 2 + ((gy - ecy) / ery) ** 2 <= 1) & (cv2.dilate(fg, np.ones((11, 11))) == 0)
    ell[:4] = ell[-4:] = False; ell[:, :4] = ell[:, -4:] = False
    g = np.median(Rs[ell], axis=0)   # median per Lab channel, never per hue angle (it wraps at 180)
    Lg, Cg, hg = [float(v) for v in lch(g)]
    t = hex_lab(a.hex)
    Lt, Ct, ht = [float(v) for v in lch(t)]
    dLs = Lt - Lg
    rep.update(glow_before_lab=[round(Lg, 2), round(Cg, 2), round(float(np.degrees(hg)), 2)], target_lab=t.round(2).tolist(),
               L_shift=round(dLs, 2), chroma_before=round(Cg, 2), chroma_target=round(Ct, 2))

    def recolor(lab):
        L, C, h = lch(lab)
        L2 = np.clip(L + dLs, 0, 100)
        C2 = Ct * np.power(np.maximum(C, 1e-3) / max(Cg, 1e-3), 0.12)
        h2 = ht + HUE_KEEP * wrap(h - hg)
        return np.stack([L2, C2 * np.cos(h2), C2 * np.sin(h2)], -1).astype(np.float32)

    # ---- recolor the render's backdrop, device untouched ----
    step = 1024
    Rr = np.empty((H, W, 3), np.float32)
    for y in range(0, H, step):
        lab = cv2.cvtColor(R[y:y + step].astype(np.float32) / 255., cv2.COLOR_RGB2LAB)
        rgb2 = np.clip(cv2.cvtColor(recolor(lab), cv2.COLOR_LAB2RGB), 0, 1) * 255.
        al = alpha[y:y + step, :, None]
        Rr[y:y + step] = rgb2 * (1 - al) + R[y:y + step].astype(np.float32) * al
    del R

    # ---- backdrop, low res Lab over the whole canvas ----
    # broad light hands over from the render (near the device) to the Deluge template (toward the edges)
    # on a smooth radial weight, inside the render too, so there is no box at the render's border.
    # Shadows, mottle and grain stay the render's own.
    n = S // LOW
    oys, oxs = oy // LOW, ox // LOW
    Rs = recolor(Rs)
    Rb = np.where(known[..., None] > 0, Rs, push_pull(Rs, known))      # backdrop only, device filled
    Rb = cv2.GaussianBlur(Rb, (0, 0), 1.5)
    tp = np.load(TEMPLATE)
    TL = Lt + a.falloff * cv2.resize(tp['dL'], (n, n), interpolation=cv2.INTER_CUBIC)
    Th = ht + cv2.resize(tp['dh'], (n, n), interpolation=cv2.INTER_CUBIC)
    T = np.stack([TL, Ct * np.cos(Th), Ct * np.sin(Th)], -1).astype(np.float32)
    rep['template'] = str(tp['source'])
    inside = np.zeros((n, n), np.float32); inside[oys:oys + hs, oxs:oxs + ws] = 1
    placed = np.zeros((n, n, 3), np.float32); placed[oys:oys + hs, oxs:oxs + ws] = Rb
    broad = cv2.GaussianBlur(push_pull(placed, inside), (0, 0), n * BROAD)   # render's broad light, carried outward smoothly
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    rr = np.hypot((xx / n - ecx) / 0.5, (yy / n - ecy) / 0.5)
    r0, r1 = HANDOVER
    u = np.clip((rr - r0) / (r1 - r0), 0, 1); wgt = (u * u * (3 - 2 * u))[..., None]
    corr = wgt * (T - broad)                                             # added to the render backdrop and the extension alike
    # outside the render: broad light plus the render's edge detail fading out, plus the handover
    detail = cv2.copyMakeBorder(Rb - broad[oys:oys + hs, oxs:oxs + ws], oys, n - hs - oys, oxs, n - ws - oxs, cv2.BORDER_REPLICATE)
    d_top = np.clip(oys - yy, 0, None); d_bot = np.clip(yy - (oys + hs - 1), 0, None)
    d_lft = np.clip(oxs - xx, 0, None); d_rgt = np.clip(xx - (oxs + ws - 1), 0, None)
    dist = np.hypot(np.maximum(d_top, d_bot), np.maximum(d_lft, d_rgt))
    k = (1 - np.exp(-dist / (n * 0.03)))[..., None]
    detail = detail * (1 - k) + cv2.GaussianBlur(detail, (0, 0), n * 0.03) * k
    ext = broad + detail * np.exp(-dist / (n * FADE))[..., None] + corr
    del yy, xx, T, placed, detail, k, broad
    # the handover inside the render, at full res, backdrop only
    corr_r = cv2.resize(corr[oys:oys + hs, oxs:oxs + ws], (W, H), interpolation=cv2.INTER_CUBIC)
    del corr
    for y in range(0, H, step):
        lab = cv2.cvtColor(Rr[y:y + step] / 255., cv2.COLOR_RGB2LAB) + corr_r[y:y + step]
        rgb2 = np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB), 0, 1) * 255.
        al = alpha[y:y + step, :, None]
        Rr[y:y + step] = rgb2 * (1 - al) + Rr[y:y + step] * al
    del corr_r

    # ---- full res: smooth extension + matched texture, then the render on top ----
    Rr_lab = np.empty((H, W, 3), np.float32)
    for y in range(0, H, step):
        Rr_lab[y:y + step] = cv2.cvtColor(Rr[y:y + step] / 255., cv2.COLOR_RGB2LAB)
    amp, npatch = texture_spectra(Rr_lab, alpha)
    rep['texture_patches'] = npatch
    del Rr_lab
    canvas_lab = cv2.resize(ext, (S, S), interpolation=cv2.INTER_CUBIC)
    del ext
    if amp is not None:
        canvas_lab += synth_texture((S, S), amp, np.random.default_rng(7))
    canvas = np.empty((S, S, 3), np.float32)
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
    canvas[oy:oy + H, ox:ox + W] = Rr * ramp[..., None] + sub * (1 - ramp[..., None])
    del sub, ramp, Rr
    A = np.zeros((S, S), np.float32); A[oy:oy + H, ox:ox + W] = alpha

    # ---- one paper: backdrop hue and chroma come only from the swatch ----
    sw_ok = oklab(srgb_to_lin(np.array([int(a.hex.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.))
    # keep a few pixels around the device as they are, so soft mask edges carrying device light do not turn into a bright rim
    P = np.zeros((S, S), np.float32)
    P[oy:oy + H, ox:ox + W] = cv2.GaussianBlur(cv2.dilate((alpha > 0.05).astype(np.uint8), np.ones((9, 9))).astype(np.float32), (0, 0), 2.5)
    P = np.maximum(P, A)
    for y in range(0, S, step):
        al = P[y:y + step, :, None]
        canvas[y:y + step] = one_paper(canvas[y:y + step], sw_ok) * (1 - al) + canvas[y:y + step] * al
    del P

    # ---- check: glow vs swatch, corners vs the template ----
    m = S // LOW
    cs = cv2.resize(canvas, (m, m), interpolation=cv2.INTER_AREA) / 255.
    As_c = cv2.resize(A, (m, m), interpolation=cv2.INTER_AREA)
    gy, gx = np.mgrid[0:m, 0:m] / m
    ellc = ((gx - ecx) / erx) ** 2 + ((gy - ecy) / ery) ** 2 <= 1
    real = np.zeros((m, m), bool); real[oy // LOW + 4:(oy + H) // LOW - 4, ox // LOW + 4:(ox + W) // LOW - 4] = True
    bgm = ellc & real & (cv2.dilate((As_c > 0.02).astype(np.uint8), np.ones((15, 15))) == 0)
    lab_c = cv2.cvtColor(cs.astype(np.float32), cv2.COLOR_RGB2LAB)
    g2 = np.median(lab_c[bgm], axis=0)
    rep['glow_after_rgb'] = np.median(cs[bgm] * 255, axis=0).round(1).tolist()
    rep['deltaE_glow_vs_swatch'] = round(float(np.linalg.norm(g2 - t)), 2)
    def ok_hue(rgb):
        lab = oklab(srgb_to_lin(rgb))
        return np.degrees(np.arctan2(lab[..., 2], lab[..., 1]))
    bgall = cv2.dilate((As_c > 0.02).astype(np.uint8), np.ones((7, 7))) == 0
    hb = ok_hue(cs.astype(np.float32))[bgall]
    rep['backdrop_hue_spread_deg'] = round(float(np.percentile(hb, 95) - np.percentile(hb, 5)), 2)
    c = m // 16
    rep['corner_L_minus_glow'] = [round(float(np.median(lab_c[sl][..., 0]) - g2[0]), 1) for sl in
                                  ((slice(0, c), slice(0, c)), (slice(0, c), slice(m - c, m)), (slice(m - c, m), slice(0, c)), (slice(m - c, m), slice(m - c, m)))]

    Image.fromarray(np.round(canvas).astype(np.uint8)).save(a.out, quality=a.quality, subsampling=0, optimize=True, dpi=(72, 72))
    rep['out_bytes'] = os.path.getsize(a.out)
    np.save(os.path.splitext(a.out)[0] + '_alpha_small.npy', cv2.resize(A, (S // 4, S // 4), interpolation=cv2.INTER_AREA))
    if a.report:
        json.dump(rep, open(a.report, 'w'), indent=1)
    print(json.dumps(rep))


if __name__ == '__main__':
    main()
