"""Image generation through the Gemini API (key in GEMINI_API_KEY).

  python3 pipeline/gen.py models
      lists image capable models, the first thing to run in a new session

  python3 pipeline/gen.py explore --prompt-file P.md --n 6 --out DIR [--aspect 1:1] [--size 1K] [--model M]
      low res samples plus a numbered contact sheet (DIR/contact-sheet.jpg)

  python3 pipeline/gen.py crop --source S.png --out C.png [--aspect auto|16:9|3:2|4:3|1:1|3:4|4:5] [--margin 0.025]
      tight crop around the device (rembg) at the closest supported aspect, before a 4K pass

  python3 pipeline/gen.py render4k --source C.png --prompt-file P.md --out R.png [--aspect 3:2] [--model M]
      edits the approved frame at 4K ("keep this exact photograph" prompts)

Model ids change. Defaults below are what we used in Oct 2026; confirm with `models` and pass --model if they moved.
"""
import argparse, base64, json, math, os, sys, time, urllib.request, urllib.error

API = "https://generativelanguage.googleapis.com/v1beta"
EXPLORE_MODEL = os.environ.get("TFB_EXPLORE_MODEL", "gemini-3-pro-image-preview")
RENDER_MODEL = os.environ.get("TFB_RENDER_MODEL", "gemini-3-pro-image-preview")
ASPECTS = {"1:1": 1.0, "4:5": 0.8, "3:4": 0.75, "2:3": 2 / 3, "9:16": 9 / 16, "5:4": 1.25, "4:3": 4 / 3, "3:2": 1.5, "16:9": 16 / 9, "21:9": 21 / 9}


def key():
    k = os.environ.get("GEMINI_API_KEY")
    if not k:
        sys.exit("GEMINI_API_KEY is not set in this environment")
    return k


def call(path, body=None, method="POST"):
    url = f"{API}/{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json", "x-goog-api-key": key()})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:800]
            if e.code in (429, 500, 503) and attempt < 3:
                time.sleep(8 * (attempt + 1)); continue
            sys.exit(f"Gemini API error {e.code}: {msg}")
        except urllib.error.URLError as e:
            sys.exit(f"Cannot reach the Gemini API ({e.reason}). Check the environment's network allowlist for generativelanguage.googleapis.com")


def img_part(path):
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(open(path, "rb").read()).decode()}}


def generate(model, prompt, images=(), aspect=None, size=None):
    parts = [{"text": prompt}] + [img_part(p) for p in images]
    cfg = {"responseModalities": ["IMAGE"]}
    ic = {}
    if aspect: ic["aspectRatio"] = aspect
    if size: ic["imageSize"] = size
    if ic: cfg["imageConfig"] = ic
    out = call(f"models/{model}:generateContent", {"contents": [{"role": "user", "parts": parts}], "generationConfig": cfg})
    for c in out.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            d = p.get("inline_data") or p.get("inlineData")
            if d:
                return base64.b64decode(d["data"])
    sys.exit("No image in the response: " + json.dumps(out)[:600])


def save(data, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    open(path, "wb").write(data)
    from PIL import Image
    w, h = Image.open(path).size
    print(f"saved {path} {w}x{h}")


def contact_sheet(paths, out):
    from PIL import Image, ImageDraw, ImageFont
    ims = [Image.open(p).convert("RGB") for p in paths]
    cell = 512
    cols = 3 if len(ims) > 4 else len(ims)
    rows = math.ceil(len(ims) / cols)
    sheet = Image.new("RGB", (cols * cell + (cols + 1) * 16, rows * cell + (rows + 1) * 16), (245, 238, 220))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 44)
    except Exception:
        font = ImageFont.load_default()
    for i, im in enumerate(ims):
        im.thumbnail((cell, cell))
        x = 16 + (i % cols) * (cell + 16); y = 16 + (i // cols) * (cell + 16)
        sheet.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        d.rectangle([x, y, x + 64, y + 60], fill=(42, 37, 34))
        d.text((x + 14, y + 6), str(i + 1), fill=(245, 238, 220), font=font)
    sheet.save(out, quality=90)
    print(f"contact sheet {out}")


def tight_crop(src, out, aspect="auto", margin=0.025):
    from PIL import Image
    import numpy as np
    from rembg import remove, new_session
    im = Image.open(src).convert("RGB"); W, H = im.size
    m = np.maximum(*[np.array(remove(im, session=new_session(n), only_mask=True)) for n in ("u2net", "isnet-general-use")]) > 100
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    pad = margin * max(W, H)
    bw, bh = (x1 - x0) + 2 * pad, (y1 - y0) + 2 * pad * 1.3  # a little more below for contact shadows
    ratio = bw / bh
    if aspect == "auto":
        aspect = min(ASPECTS, key=lambda k: abs(math.log(ASPECTS[k] / ratio)))
    r = ASPECTS[aspect]
    if bw / bh < r: bw = bh * r
    else: bh = bw / r
    if bw > W: bw = W; bh = bw / r
    if bh > H: bh = H; bw = bh * r
    cx = (x0 + x1) / 2; cy = (y0 + y1) / 2 + pad * 0.15
    left = min(max(cx - bw / 2, 0), W - bw); top = min(max(cy - bh / 2, 0), H - bh)
    box = tuple(int(round(v)) for v in (left, top, left + bw, top + bh))
    im.crop(box).save(out)
    print(json.dumps({"crop": out, "box": box, "aspect": aspect, "device_bbox": [int(x0), int(y0), int(x1), int(y1)]}))
    return aspect


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("models")
    e = sub.add_parser("explore"); e.add_argument("--prompt-file", required=True); e.add_argument("--n", type=int, default=6); e.add_argument("--out", required=True)
    e.add_argument("--aspect", default="1:1"); e.add_argument("--size", default="1K"); e.add_argument("--model", default=EXPLORE_MODEL); e.add_argument("--ref", action="append", default=[])
    c = sub.add_parser("crop"); c.add_argument("--source", required=True); c.add_argument("--out", required=True); c.add_argument("--aspect", default="auto"); c.add_argument("--margin", type=float, default=0.025)
    r = sub.add_parser("render4k"); r.add_argument("--source", required=True); r.add_argument("--prompt-file", required=True); r.add_argument("--out", required=True)
    r.add_argument("--aspect", default=None); r.add_argument("--model", default=RENDER_MODEL); r.add_argument("--size", default="4K")
    a = ap.parse_args()
    if a.cmd == "models":
        res = call("models?pageSize=200", method="GET")
        for m in res.get("models", []):
            name = m.get("name", "")
            if "image" in name or "imagen" in name:
                print(name, "·", m.get("displayName", ""))
        return
    if a.cmd == "explore":
        prompt = open(a.prompt_file).read()
        paths = []
        for i in range(a.n):
            p = os.path.join(a.out, f"{i + 1:02d}.png")
            save(generate(a.model, prompt, a.ref, a.aspect, a.size), p); paths.append(p)
        contact_sheet(paths, os.path.join(a.out, "contact-sheet.jpg"))
        return
    if a.cmd == "crop":
        tight_crop(a.source, a.out, a.aspect, a.margin); return
    if a.cmd == "render4k":
        from PIL import Image
        aspect = a.aspect
        if not aspect:
            w, h = Image.open(a.source).size
            aspect = min(ASPECTS, key=lambda k: abs(math.log(ASPECTS[k] / (w / h))))
        save(generate(a.model, open(a.prompt_file).read(), [a.source], aspect, a.size), a.out)


if __name__ == "__main__":
    main()
