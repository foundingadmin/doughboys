"""heroshot: one command per step, from low res explore frames to a finished square master.

Every step writes its files where the project keeps them and records what happened in heroshot.json,
so any Claude Code session picks up from an item's `status` and `next`. The playbook that drives it,
with its approval gates, is .claude/skills/heroshot/SKILL.md (written by `heroshot init`).

  heroshot init [--dir art] [--name NAME] [--approver NAME] [--tz Area/City]
  heroshot doctor                     smoke test: dependencies, API key, models, budget
  heroshot models                     image models the key can reach
  heroshot status [ID]
  heroshot add ID --title T --subject S --hex "#RRGGBB" [--ground NAME] [--shape TEXT]
  heroshot prompt ID [--round 1]      drafts the explore prompt from the series lock
  heroshot explore ID [--round 1] [--n 3] [--ref PICK.png] [--dry-run]
  heroshot lock ID FRAME.png --pick R2-4
  heroshot render ID --approved "the approver's words" [--runs 1] [--source PNG] [--ref IMG] [--dry-run]
  heroshot finish ID --render JPG [--version v1] [--falloff 0.75] [--horizon 0.16]
  heroshot template MASTER.jpg        measure a falloff template from an approved master
  heroshot drive ID [--what render|master|both]
  heroshot spend                      this month against the budget
"""
import argparse, glob, json, os, shutil, subprocess, sys

from . import __version__
from .config import CONFIG_NAME, DEFAULTS, Project, die

SCAFFOLD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scaffold")
CLAUDE_MARK = "<!-- heroshot -->"


# ---------- init ----------

def copy_tree(src, dst, force):
    made, kept = [], []
    for base, _, files in os.walk(src):
        for f in files:
            s = os.path.join(base, f)
            d = os.path.join(dst, os.path.relpath(s, src))
            if os.path.exists(d) and not force:
                kept.append(d)
                continue
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy(s, d)
            made.append(d)
    return made, kept


def cmd_init(a):
    root = os.path.abspath(a.path)
    cfg_path = os.path.join(root, CONFIG_NAME)
    if os.path.exists(cfg_path) and not a.force:
        cfg = json.load(open(cfg_path))
        print(f"{CONFIG_NAME} already here, keeping it. Refreshing the skill and any missing templates.")
    else:
        cfg = json.loads(json.dumps(DEFAULTS))
        cfg.update(project=a.name or os.path.basename(root), dir=a.dir, approver=a.approver, timezone=a.tz)
        json.dump(cfg, open(cfg_path, "w"), indent=2, ensure_ascii=False)
        open(cfg_path, "a").write("\n")
        print("wrote", CONFIG_NAME)
    art = os.path.join(root, cfg.get("dir", a.dir))
    made, kept = copy_tree(os.path.join(SCAFFOLD, "art"), art, a.force)
    # the skill always refreshes, so a package upgrade reaches the playbook
    made2, _ = copy_tree(os.path.join(SCAFFOLD, "skill"), os.path.join(root, ".claude", "skills", "heroshot"), True)
    gi = os.path.join(root, ".gitignore")
    have = open(gi).read() if os.path.exists(gi) else ""
    add = [l for l in ("work/", ".heroshot.lock", "heroshot.json.tmp") if l not in have.split("\n")]
    if add:
        with open(gi, "a") as f:
            f.write(("\n" if have and not have.endswith("\n") else "") + "# heroshot\n" + "\n".join(add) + "\n")
    cm = os.path.join(root, "CLAUDE.md")
    section = open(os.path.join(SCAFFOLD, "claude-section.md")).read().replace("{DIR}", cfg.get("dir", a.dir))
    cur = open(cm).read() if os.path.exists(cm) else ""
    if CLAUDE_MARK not in cur:
        with open(cm, "a") as f:
            f.write(("\n\n" if cur else "") + section)
        print("added the heroshot section to CLAUDE.md")
    for p in made + made2:
        print("  +", os.path.relpath(p, root))
    for p in kept:
        print("  = kept", os.path.relpath(p, root))
    print(f"\nNext: edit {cfg.get('dir', a.dir)}/prompts/explore/series-lock.md and {cfg.get('dir', a.dir)}/docs/brief.md, "
          f"add items with `heroshot add`, set GEMINI_API_KEY in the environment, then `heroshot doctor`.")


# ---------- shared ----------

def run_py(proj, *args):
    print("$ python -m", " ".join(args), flush=True)
    r = subprocess.run([sys.executable, "-m", *args], cwd=proj.root, capture_output=True, text=True)
    sys.stdout.write(r.stdout[-4000:])
    if r.returncode:
        sys.stderr.write(r.stderr[-4000:])
        die(f"step failed: {args[0]}")
    return r.stdout


def slug_of(t):
    return t["slug"]


def assets(proj, t):
    return proj.p("assets", slug_of(t), make=True)


# ---------- read only ----------

def cmd_doctor(a):
    proj = Project()
    ok = True
    print(f"heroshot {__version__} · project {proj.cfg['project']} · {proj.rel(proj.art)}/ · {len(proj.cfg['items'])} items")
    for mod in ("PIL", "numpy", "cv2", "rembg"):
        try:
            __import__(mod)
            print(f"ok   {mod}")
        except Exception as e:
            ok = False
            print(f"FAIL {mod}: {e}")
    if not os.environ.get("GEMINI_API_KEY"):
        ok = False
        print("FAIL GEMINI_API_KEY is not set")
    else:
        from . import gen
        names = [n.split("/")[-1] for n, _ in gen.models()]
        for role, m in proj.cfg["models"].items():
            seen = m in names
            ok &= seen
            print(f"{'ok  ' if seen else 'FAIL'} {role} model {m}" + ("" if seen else f" not offered. Reachable: {', '.join(names)}"))
    lock = proj.p("prompts", "explore", "series-lock.md")
    print(f"{'ok  ' if os.path.exists(lock) else 'FAIL'} series lock {proj.rel(lock)}")
    from . import spend
    print(f"info spend this month ${spend.month_total(proj):.2f} of ${proj.cfg['budget_usd_month']}")
    print("info Drive upload " + ("wired" if os.environ.get("HEROSHOT_DRIVE_URL") else "not wired (hand files over in chat)"))
    sys.exit(0 if ok else 1)


def cmd_models(a):
    from . import gen
    for n, d in gen.models():
        print(n, "·", d)


def cmd_status(a):
    proj = Project()
    for t in proj.cfg["items"]:
        if a.id and t is not proj.item(a.id):
            continue
        print(f"{t['id']:<4} {t.get('title', ''):<24} {t.get('status', '')}")
        if a.id:
            print("  next:", t.get("next", ""))
            for k in ("subject", "shape", "ground_hex", "source", "renders", "master", "review_boards"):
                if k in t:
                    print(f"  {k}:", json.dumps(t[k], ensure_ascii=False)[:400])
    if not proj.cfg["items"]:
        print("no items yet. `heroshot add 01 --title ... --subject ... --hex ...`")


def cmd_spend(a):
    from . import spend
    proj = Project()
    print(f"${spend.month_total(proj):.2f} this month of ${proj.cfg['budget_usd_month']} · log {proj.rel(spend.path(proj))}")


# ---------- steps ----------

def cmd_add(a):
    proj = Project()
    with proj.edit() as cfg:
        if any(t["id"] == a.id for t in cfg["items"]):
            die(f"item {a.id} exists")
        slug = a.slug or f"{a.id}-" + "-".join(a.title.lower().split())
        cfg["items"].append({"id": a.id, "slug": slug, "title": a.title, "subject": a.subject, "shape": a.shape or "",
                             "ground": a.ground or "", "ground_hex": a.hex, "status": "not started",
                             "next": f"heroshot prompt {a.id} --round 1"})
    print("added", a.id, slug)


def cmd_prompt(a):
    proj = Project()
    t = proj.item(a.id)
    lock = open(proj.p("prompts", "explore", "series-lock.md")).read()
    try:
        template = lock.split("```")[1].strip()
    except IndexError:
        die("series-lock.md needs its template in a ``` block")
    body = (template.replace("{TITLE}", t.get("title", "")).replace("{SUBJECT}", t.get("subject", ""))
            .replace("{SHAPE}", t.get("shape", "")).replace("{GROUND}", t.get("ground") or t["ground_hex"])
            .replace("{GROUND_HEX}", t["ground_hex"]))
    out = proj.p("prompts", "explore", make=True)
    out = os.path.join(out, f"{slug_of(t)}-round-{a.round}.md")
    if os.path.exists(out) and not a.force:
        die(f"{proj.rel(out)} exists, pass --force to redraft")
    open(out, "w").write(body + "\n")
    print(proj.rel(out))
    print("Rewrite every [BRACKETED] part as plain prose before `heroshot explore`. No bracket may remain.")


def cmd_explore(a):
    from . import gen, spend
    proj = Project()
    t = proj.item(a.id)
    pf = proj.p("prompts", "explore", f"{slug_of(t)}-round-{a.round}.md")
    if not os.path.exists(pf):
        die(f"write {proj.rel(pf)} first (heroshot prompt {a.id} --round {a.round})")
    prompt = open(pf).read()
    if "[" in prompt:
        die(f"{proj.rel(pf)} still has [bracketed] parts")
    model, size, aspect = a.model or proj.cfg["models"]["explore"], proj.cfg["explore"]["size"], proj.cfg["explore"]["aspect"]
    n = a.n or proj.cfg["explore"]["n"]
    est = n * spend.price(proj, model, size)
    spent = spend.guard(proj, est, a.over_budget, a.dry_run)
    print(f"{n} frames on {model} at {size}, about ${est:.2f} (month so far ${spent:.2f})")
    if a.dry_run:
        print(prompt)
        return
    out = proj.work(slug_of(t), f"round-{a.round}")
    paths = []
    for i in range(n):
        p = os.path.join(out, f"{i + 1:02d}.png")
        gen.save(gen.generate(model, prompt, a.ref, aspect, size), p)
        spend.log(proj, model, size, f"explore {proj.rel(pf)} {i + 1}")
        paths.append(p)
    gen.contact_sheet(paths, os.path.join(out, "contact-sheet.jpg"))
    dst = proj.p("explore", slug_of(t), f"round-{a.round}", make=True)
    shutil.copy(os.path.join(out, "contact-sheet.jpg"), dst)
    shutil.copy(pf, os.path.join(dst, "prompt.md"))
    with proj.edit() as cfg:
        it = proj.item(a.id, cfg)
        it.setdefault("explore_rounds", []).append({"round": a.round, "date": proj.today(), "model": model, "prompt": proj.rel(pf),
                                                    "frames": proj.rel(out), "refs": a.ref, "contact_sheet": proj.rel(os.path.join(dst, "contact-sheet.jpg"))})
        it["status"] = f"exploring, round {a.round} ready for {proj.cfg['approver']}"
        it["next"] = f"{proj.cfg['approver']} picks a frame on the round {a.round} review board, then heroshot lock {a.id} <frame> --pick R{a.round}-<n>"
    for p in paths:
        print(proj.rel(p))


def cmd_lock(a):
    from PIL import Image
    proj = Project()
    t = proj.item(a.id)
    dst = os.path.join(assets(proj, t), f"{slug_of(t)}-source-{a.pick.lower()}.png")
    Image.open(a.frame).convert("RGB").save(dst)
    with proj.edit() as cfg:
        it = proj.item(a.id, cfg)
        it["source"] = {"pick": a.pick, "approved": proj.today(), "file": proj.rel(dst), "from": a.frame}
        it["status"] = "source approved, hi res prompt next"
        it["next"] = f"Write {proj.cfg['dir']}/prompts/hires/{slug_of(t)}.md, show {proj.cfg['approver']}, then heroshot render {a.id}"
    print(proj.rel(dst))


def cmd_render(a):
    from . import checks, gen, spend
    proj = Project()
    t = proj.item(a.id)
    src = a.source or (t.get("source") or {}).get("file")
    if not src:
        die(f"no locked source, run heroshot lock {a.id} first")
    src = os.path.join(proj.root, src) if not os.path.isabs(src) else src
    pf = proj.p("prompts", "hires", f"{slug_of(t)}.md")
    if not os.path.exists(pf):
        die(f"write {proj.rel(pf)} first and show it to {proj.cfg['approver']}")
    if len(a.approved.strip()) < 3:
        die(f"--approved needs {proj.cfg['approver']}'s written yes from this conversation, quoted")
    model, size = a.model or proj.cfg["models"]["render"], proj.cfg["render"]["size"]
    est = a.runs * spend.price(proj, model, size)
    spent = spend.guard(proj, est, a.over_budget, a.dry_run)
    print(f"{a.runs} run(s) on {model} at {size}, about ${est:.2f} (month so far ${spent:.2f})")
    if a.dry_run:
        print(open(pf).read())
        return
    crop = os.path.join(assets(proj, t), f"{slug_of(t)}-crop.png")
    info = gen.tight_crop(src, crop) if not a.no_crop else {"crop": src, "box": None, "aspect": a.aspect}
    if a.no_crop:
        from PIL import Image
        w, h = Image.open(src).size
        info["aspect"] = a.aspect or gen.closest_aspect(w / h)
        crop = src
    print(json.dumps(info))
    have = [os.path.basename(p) for p in glob.glob(os.path.join(assets(proj, t), f"{slug_of(t)}-render-*.jpg"))]
    letters = [chr(c) for c in range(ord("a"), ord("z") + 1) if not any(h.endswith(f"-{chr(c)}.jpg") for h in have)]
    records = []
    for i in range(a.runs):
        L = letters[i]
        out = os.path.join(assets(proj, t), f"{slug_of(t)}-render-{size.lower()}-{info['aspect'].replace(':', 'x')}-{L}.jpg")
        gen.save(gen.generate(model, open(pf).read(), [crop] + a.ref, info["aspect"], size), out)
        spend.log(proj, model, size, f"render {proj.rel(crop)} {proj.rel(pf)}", a.approved)
        tiles = checks.grid(out, proj.work(slug_of(t), "check"), L)
        records.append({"file": proj.rel(out), "letter": L, "aspect": info["aspect"], "date": proj.today(), "prompt": proj.rel(pf),
                        "crop": proj.rel(crop), "check_tiles": [proj.rel(p) for p in tiles], "approval": a.approved})
        print(proj.rel(out))
    with proj.edit() as cfg:
        it = proj.item(a.id, cfg)
        it.setdefault("renders", []).extend(records)
        it["crop"] = {"file": proj.rel(crop), "aspect": info["aspect"], "box": info["box"]}
        it["status"] = f"rendered, check and {proj.cfg['approver']} pick next"
        it["next"] = f"Check every render in crops, build the review board, {proj.cfg['approver']} picks, then heroshot finish {a.id} --render <file>"


def cmd_finish(a):
    from PIL import Image
    from . import checks, framing
    import numpy as np
    proj = Project()
    t = proj.item(a.id)
    fc = proj.cfg["finish"]
    out = os.path.join(assets(proj, t), f"{slug_of(t)}-final-{a.version}.jpg")
    rep = os.path.join(proj.work(slug_of(t)), f"finish-{a.version}.json")
    args = ["heroshot.finish", a.render, t["ground_hex"], out, "--report", rep, "--canvas", str(fc["canvas"]),
            "--falloff", str(a.falloff if a.falloff is not None else fc["falloff"]),
            "--horizon", str(a.horizon if a.horizon is not None else fc["horizon"])]
    if fc.get("template"):
        args += ["--template", os.path.join(proj.root, fc["template"])]
    if a.glass_box:
        args += ["--glass-box", a.glass_box]
    run_py(proj, *args)
    r = json.load(open(rep))
    seam = checks.seams(out, r["offset"][0], r["offset"][1], r["render"][0], r["render"][1], os.path.join(proj.work(slug_of(t)), f"check-{a.version}"))
    fr = framing.transforms(np.load(os.path.splitext(out)[0] + "_alpha_small.npy"))
    Image.MAX_IMAGE_PIXELS = None
    small = os.path.join(proj.work(slug_of(t)), f"{slug_of(t)}-final-{a.version}-4096.jpg")
    Image.open(out).resize((4096, 4096), Image.LANCZOS).save(small, quality=95, subsampling=0)
    flags = []
    if r["deltaE_glow_vs_swatch"] >= 3:
        flags.append("glow off the swatch (deltaE 3 or more)")
    if r["device_touches_edge"]:
        flags.append("subject touches the render edge, crop again")
    if r.get("backdrop_hue_spread_deg", 0) > 2:
        flags.append("backdrop hue spread over 2 degrees")
    with proj.edit() as cfg:
        it = proj.item(a.id, cfg)
        it["master"] = proj.rel(out)
        it["render_pick"] = proj.rel(os.path.abspath(a.render))
        it["finish_report"] = {k: r[k] for k in ("falloff", "horizon", "template", "deltaE_glow_vs_swatch", "backdrop_hue_spread_deg",
                                                 "corner_L_minus_glow", "device_touches_edge", "offset", "render") if k in r}
        it["framing"] = fr
        it["status"] = f"master {a.version} finished, {proj.cfg['approver']} yes then place"
        it["next"] = f"Review board with the master beside the last approved one, on {proj.cfg['approver']}'s yes place it, then heroshot drive {a.id}"
    print(json.dumps({"master": proj.rel(out), "upload_copy_4096": proj.rel(small), "seam_crops": [proj.rel(p) for p in seam],
                      "framing": fr, "flags": flags}))


def cmd_template(a):
    from . import template
    proj = Project()
    out = a.out or proj.p("backdrop_template.npz")
    res = template.measure(a.master, out)
    with proj.edit() as cfg:
        cfg.setdefault("finish", {})["template"] = proj.rel(out)
    print(json.dumps(res))


def cmd_drive(a):
    from . import drive
    proj = Project()
    t = proj.item(a.id)
    folder = a.folder or t.get("drive_folder") or proj.cfg["drive"].get("default_folder")
    if not folder:
        die(f"no Drive folder: set drive_folder on item {a.id} or drive.default_folder in {CONFIG_NAME}")
    files = []
    if a.what in ("render", "both") and t.get("render_pick"):
        files.append(t["render_pick"])
    if a.what in ("master", "both") and t.get("master"):
        files.append(t["master"])
    if not files:
        die("nothing to upload yet")
    done = {}
    for f in files:
        res = drive.put(os.path.join(proj.root, f), folder)
        done[res["name"]] = res["id"]
        print(json.dumps(res))
    with proj.edit() as cfg:
        proj.item(a.id, cfg).setdefault("drive_files", {}).update(done)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="heroshot", description=__doc__.split("\n")[0])
    ap.add_argument("--version", action="version", version=__version__)
    s = ap.add_subparsers(dest="cmd", required=True)
    p = s.add_parser("init"); p.add_argument("path", nargs="?", default="."); p.add_argument("--dir", default="art")
    p.add_argument("--name"); p.add_argument("--approver", default="the creative director"); p.add_argument("--tz", default="UTC")
    p.add_argument("--force", action="store_true", help="overwrite existing config and templates")
    s.add_parser("doctor"); s.add_parser("models"); s.add_parser("spend")
    p = s.add_parser("status"); p.add_argument("id", nargs="?")
    p = s.add_parser("add"); p.add_argument("id"); p.add_argument("--title", required=True); p.add_argument("--subject", required=True)
    p.add_argument("--hex", required=True, help="ground swatch, like #C77171"); p.add_argument("--ground", help="ground color name for prompts")
    p.add_argument("--shape", help="this item's own arrangement or silhouette"); p.add_argument("--slug")
    p = s.add_parser("prompt"); p.add_argument("id"); p.add_argument("--round", default="1"); p.add_argument("--force", action="store_true")
    p = s.add_parser("explore"); p.add_argument("id"); p.add_argument("--round", default="1"); p.add_argument("--n", type=int)
    p.add_argument("--ref", action="append", default=[], help="reference image, for example the picked frame to change only one thing")
    p.add_argument("--model"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--over-budget", action="store_true")
    p = s.add_parser("lock"); p.add_argument("id"); p.add_argument("frame"); p.add_argument("--pick", required=True)
    p = s.add_parser("render"); p.add_argument("id"); p.add_argument("--approved", required=True, help="the approver's written yes from this conversation, quoted")
    p.add_argument("--runs", type=int, default=1); p.add_argument("--source"); p.add_argument("--ref", action="append", default=[])
    p.add_argument("--aspect"); p.add_argument("--no-crop", action="store_true", help="send the source as is, for a second pass on a render")
    p.add_argument("--model"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--over-budget", action="store_true")
    p = s.add_parser("finish"); p.add_argument("id"); p.add_argument("--render", required=True); p.add_argument("--version", default="v1")
    p.add_argument("--falloff", type=float); p.add_argument("--horizon", type=float); p.add_argument("--glass-box")
    p = s.add_parser("template"); p.add_argument("master"); p.add_argument("--out")
    p = s.add_parser("drive"); p.add_argument("id"); p.add_argument("--what", default="both", choices=["render", "master", "both"]); p.add_argument("--folder")
    a = ap.parse_args(argv)
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()
