"""Image generation through the Gemini API. The key lives only in the environment: GEMINI_API_KEY.

Explore runs on the fast cheap model at 1K. The 4K pass is an edit of the approved frame
("keep this exact photograph") on the pro model. Model ids move: `heroshot models` lists what
the key can reach, and heroshot.json "models" picks them.
"""
import base64, json, math, os, sys, time, urllib.error, urllib.request

API = "https://generativelanguage.googleapis.com/v1beta"
ASPECTS = {"1:1": 1.0, "4:5": 0.8, "3:4": 0.75, "2:3": 2 / 3, "9:16": 9 / 16, "5:4": 1.25, "4:3": 4 / 3, "3:2": 1.5, "16:9": 16 / 9, "21:9": 21 / 9}


def key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        sys.exit("heroshot: GEMINI_API_KEY is not set. Add it to the environment, never to a file or commit.")
    return k


def call(path, body=None, method="POST"):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}/{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key()})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:800]
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(8 * (attempt + 1))
                continue
            sys.exit(f"heroshot: Gemini API error {e.code}: {msg}")
        except urllib.error.URLError as e:
            sys.exit(f"heroshot: cannot reach the Gemini API ({e.reason}). Allow generativelanguage.googleapis.com on the network.")


def models():
    res = call("models?pageSize=200", method="GET")
    return [(m.get("name", ""), m.get("displayName", "")) for m in res.get("models", [])
            if "image" in m.get("name", "") or "imagen" in m.get("name", "")]


def _part(path):
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}}


def generate(model, prompt, images=(), aspect=None, size=None):
    parts = [{"text": prompt}] + [_part(p) for p in images]
    cfg = {"responseModalities": ["IMAGE"]}
    ic = {}
    if aspect:
        ic["aspectRatio"] = aspect
    if size:
        ic["imageSize"] = size
    if ic:
        cfg["imageConfig"] = ic
    out = call(f"models/{model}:generateContent", {"contents": [{"role": "user", "parts": parts}], "generationConfig": cfg})
    for c in out.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inline_data") or p.get("inlineData")
            if d:
                return base64.b64decode(d["data"])
    sys.exit("heroshot: no image in the response: " + json.dumps(out)[:600])


def save(data, path):
    """Gemini returns JPEG bytes whatever the name, so callers save renders as .jpg."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, "wb").write(data)
    from PIL import Image
    w, h = Image.open(path).size
    print(f"saved {path} {w}x{h}")


def contact_sheet(paths, out, start=1):
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(p).convert("RGB") for p in paths]
    cell, gap = 512, 16
    cols = 3 if len(ims) > 4 else len(ims)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * cell + (cols + 1) * gap, rows * cell + (rows + 1) * gap), (245, 242, 236))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(ims):
        im.thumbnail((cell, cell))
        x = gap + (i % cols) * (cell + gap)
        y = gap + (i // cols) * (cell + gap)
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.rectangle([x, y, x + 64, y + 60], fill=(34, 34, 34))
        d.text((x + 14, y + 6), str(start + i), fill=(245, 242, 236), font=font)
    sheet.save(out, quality=90)
    print(f"contact sheet {out}")


def closest_aspect(ratio):
    return min(ASPECTS, key=lambda k: abs(math.log(ASPECTS[k] / ratio)))


def tight_crop(src, out, aspect="auto", margin=0.025):
    """Crop to the subject with a thin strip of backdrop, at the closest aspect the generator supports.
    Every pixel of empty backdrop sent to the 4K pass is subject detail thrown away."""
    from PIL import Image
    import numpy as np
    from rembg import remove, new_session
    im = Image.open(src).convert("RGB")
    W, H = im.size
    m = np.maximum(*[np.array(remove(im, session=new_session(n), only_mask=True)) for n in ("u2net", "isnet-general-use")]) > 100
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = margin * max(W, H)
    bw, bh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad * 1.3   # a little more below for contact shadows
    if aspect == "auto":
        aspect = closest_aspect(bw / bh)
    r = ASPECTS[aspect]
    if bw / bh < r:
        bw = bh * r
    else:
        bh = bw / r
    if bw > W:
        bw = W; bh = bw / r
    if bh > H:
        bh = H; bw = bh * r
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2 + pad * 0.15
    left = min(max(cx - bw / 2, 0), W - bw)
    top = min(max(cy - bh / 2, 0), H - bh)
    box = tuple(int(round(v)) for v in (left, top, left + bw, top + bh))
    im.crop(box).save(out)
    return {"crop": out, "box": box, "aspect": aspect, "subject_bbox": [int(x0), int(y0), int(x1), int(y1)]}
