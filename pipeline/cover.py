"""Build a track cover, one command per step. Each step writes its files where the repo keeps them
and records what happened in the-first-batch/tracks.json, so any session can pick up where the last
one stopped. The playbook that drives it is .claude/skills/build-track-cover/SKILL.md.

  python3 pipeline/cover.py status [NN]
  python3 pipeline/cover.py prompt NN [--round 1]
      drafts the explore prompt from the series lock and the track's device, silhouette and ground
      into the-first-batch/prompts/explore/NN-track-round-R.md. Claude finishes the bracketed parts.
  python3 pipeline/cover.py explore NN [--round 1] [--n 6]
      low res frames from that prompt into work/NN-track/round-R, contact sheet into the repo
  python3 pipeline/cover.py lock NN FRAME_PNG --pick R2-4
      copies Josh's pick to the-first-batch/assets/photos/NN-track/NN-track-source-<pick>.png
  python3 pipeline/cover.py render NN --approved "Josh's words" [--runs 1] [--source PNG]
      needs Josh's written yes, given after he was pointed to the explore frame in Figma this session
      tight crop, then 4K runs with prompts/4k/NN-track.md, renders saved as .jpg in the repo,
      a 3 x 2 grid of native check crops per render in work/NN-track/check
  python3 pipeline/cover.py finish NN --render JPG [--version v1]
      finish.py at the track's swatch, check crops, Post and Canvas framing, a 4096 copy for Figma
  python3 pipeline/cover.py drive NN [--what render|master|both]
      saves the picked 4K render and the master into the track's Masters folder on Drive
"""
import argparse, datetime, glob, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TFB = os.path.join(ROOT, 'the-first-batch')
TRACKS = os.path.join(TFB, 'tracks.json')
PY = sys.executable


def load():
    return json.load(open(TRACKS))


def save(d):
    d['updated'] = datetime.date.today().isoformat()
    json.dump(d, open(TRACKS, 'w'), indent=1, ensure_ascii=False)
    open(TRACKS, 'a').write('\n')


def get(d, n):
    for t in d['tracks']:
        if t['n'] == str(n).zfill(2):
            return t
    sys.exit(f'no track {n}')


def rel(p):
    return os.path.relpath(p, ROOT)


def run(*args):
    print('$', ' '.join(args), flush=True)
    r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    sys.stdout.write(r.stdout[-4000:])
    if r.returncode:
        sys.stderr.write(r.stderr[-4000:])
        sys.exit(f'step failed: {args[1]}')
    return r.stdout


def today():
    return datetime.date.today().isoformat()


def photos(t):
    p = os.path.join(TFB, 'assets', 'photos', t['slug'])
    os.makedirs(p, exist_ok=True)
    return p


def work(t, *sub):
    p = os.path.join(ROOT, 'work', t['slug'], *sub)
    os.makedirs(p, exist_ok=True)
    return p


def cmd_status(a):
    d = load()
    for t in d['tracks']:
        if a.n and t['n'] != a.n.zfill(2):
            continue
        print(f"{t['catalog']} {t['title']:<18} {t['status']}")
        if a.n:
            print('  next:', t.get('next', ''))
            for k in ('source', 'renders_4k', 'master', 'review_boards'):
                if k in t:
                    print(f'  {k}:', json.dumps(t[k])[:400])


def cmd_prompt(a):
    d = load(); t = get(d, a.n)
    lock = open(os.path.join(TFB, 'prompts', 'explore', 'series-lock.md')).read()
    template = lock.split('```')[1].strip()
    firm = lock.split('**Firm')[1].split('```')[1].strip()
    ground = t['ground'].capitalize()
    body = (template
            .replace('[DEVICE, named part by part, with its analog knobs and buttons and a small glowing red power light where a real one would sit.]',
                     f"[DEVICE · {t['device']}: name it part by part, with its analog knobs and buttons and a small glowing red power light where a real one would sit.]")
            .replace('[DOUGH: the firm block below, plus this track\'s own silhouette from tracks.json, for example a brick shaped like a VHS tape half in the slot.]',
                     firm + f"\n\n[SILHOUETTE · {t['silhouette']}: describe this exact shape.]")
            .replace('[GROUND NAME]', ground))
    out = os.path.join(TFB, 'prompts', 'explore', f"{t['slug']}-round-{a.round}.md")
    if os.path.exists(out) and not a.force:
        sys.exit(f'{rel(out)} exists, pass --force to redraft')
    open(out, 'w').write(body + '\n')
    print(rel(out))
    print('Replace every [BRACKETED] part with plain prose before running explore. No bracket may remain.')


def cmd_explore(a):
    d = load(); t = get(d, a.n)
    pf = os.path.join(TFB, 'prompts', 'explore', f"{t['slug']}-round-{a.round}.md")
    if not os.path.exists(pf):
        sys.exit(f'write {rel(pf)} first (cover.py prompt {a.n})')
    if '[' in open(pf).read():
        sys.exit(f'{rel(pf)} still has [bracketed] parts')
    out = work(t, f'round-{a.round}')
    run(PY, 'pipeline/gen.py', 'explore', '--prompt-file', pf, '--n', str(a.n_frames), '--out', out)
    dst = os.path.join(TFB, 'explore', t['slug'], f'round-{a.round}')
    os.makedirs(dst, exist_ok=True)
    shutil.copy(os.path.join(out, 'contact-sheet.jpg'), dst)
    t['status'] = f'exploring, round {a.round} ready for Josh'
    t['next'] = f'Josh picks a frame from round {a.round} on its Figma Review board, then cover.py lock {t["n"]} <frame> --pick R{a.round}-<number>'
    t.setdefault('explore_rounds', []).append({'round': a.round, 'date': today(), 'prompt': rel(pf), 'frames': rel(out), 'contact_sheet': rel(os.path.join(dst, 'contact-sheet.jpg'))})
    save(d)
    for f in sorted(glob.glob(os.path.join(out, '[0-9][0-9].png'))):
        print(rel(f))


def cmd_lock(a):
    d = load(); t = get(d, a.n)
    dst = os.path.join(photos(t), f"{t['slug']}-source-{a.pick.lower()}.png")
    from PIL import Image
    Image.open(a.frame).convert('RGB').save(dst)
    t['source'] = {'pick': a.pick, 'approved': today(), 'repo': rel(dst), 'from': a.frame}
    t['status'] = 'source approved, 4K prompt next'
    t['next'] = f"Write the-first-batch/prompts/4k/{t['slug']}.md, show Josh, then cover.py render {t['n']}"
    save(d)
    print(rel(dst))


def check_grid(render, outdir, tag):
    """Six native pixel crops on a 3 x 2 grid over the render, for a first look at every region."""
    from PIL import Image
    im = Image.open(render); W, H = im.size
    paths = []
    for r in range(2):
        for c in range(3):
            box = (c * W // 3, r * H // 2, (c + 1) * W // 3, (r + 1) * H // 2)
            p = os.path.join(outdir, f'{tag}-tile{r * 3 + c + 1}.jpg')
            im.crop(box).save(p, quality=93)
            paths.append(p)
    return paths


def cmd_render(a):
    d = load(); t = get(d, a.n)
    src = a.source or (t.get('source') or {}).get('repo')
    if not src:
        sys.exit('no locked source, run cover.py lock first')
    pf = os.path.join(TFB, 'prompts', '4k', f"{t['slug']}.md")
    if not os.path.exists(pf):
        sys.exit(f'write {rel(pf)} first and show it to Josh')
    crop = os.path.join(photos(t), f"{t['slug']}-crop.png")
    info = json.loads(run(PY, 'pipeline/gen.py', 'crop', '--source', os.path.join(ROOT, src), '--out', crop).strip().splitlines()[-1])
    have = [os.path.basename(p) for p in glob.glob(os.path.join(photos(t), f"{t['slug']}-4k-render-*.jpg"))]
    letters = [chr(c) for c in range(ord('a'), ord('z') + 1) if not any(h.endswith(f'-{chr(c)}.jpg') for h in have)]
    t.setdefault('renders_4k', [])
    chk = work(t, 'check')
    for i in range(a.runs):
        L = letters[i]
        tmp = os.path.join(work(t), f'render-{L}.bin')
        run(PY, 'pipeline/gen.py', 'render4k', '--source', crop, '--prompt-file', pf, '--out', tmp, '--approved', a.approved, *[x for r in a.ref for x in ('--ref', r)])
        out = os.path.join(photos(t), f"{t['slug']}-4k-render-{info['aspect'].replace(':', 'x')}-{L}.jpg")
        shutil.move(tmp, out)          # Gemini returns JPEG bytes whatever the name
        tiles = check_grid(out, chk, L)
        t['renders_4k'].append({'file': rel(out), 'letter': L, 'aspect': info['aspect'], 'date': today(), 'prompt': rel(pf), 'crop': rel(crop), 'check_tiles': [rel(p) for p in tiles], 'josh_approval': a.approved})
        print(rel(out))
    t['crop'] = {'file': rel(crop), 'aspect': info['aspect'], 'box': info['box']}
    t['status'] = '4K rendered, check and Josh pick next'
    t['next'] = 'Check every render in crops, build the Review board, Josh picks, then cover.py finish ' + t['n'] + ' --render <file>'
    save(d)


def cmd_finish(a):
    d = load(); t = get(d, a.n)
    out = os.path.join(photos(t), f"{t['slug']}-final-{a.version}.jpg")
    rep = os.path.join(work(t), f'finish-{a.version}.json')
    extra = ['--glass-box', a.glass_box] if a.glass_box else []
    run(PY, 'pipeline/finish.py', a.render, t['ground_hex'], out, '--report', rep, *extra)
    if a.glass_box: t['finish_glass_box'] = a.glass_box
    r = json.load(open(rep))
    run(PY, 'pipeline/check.py', out, '--ox', str(r['offset'][0]), '--oy', str(r['offset'][1]), '--w', str(r['render'][0]), '--h', str(r['render'][1]), '--name', os.path.join(work(t), f'check-{a.version}'))
    fr = json.loads(run(PY, 'pipeline/framing.py', os.path.splitext(out)[0] + '_alpha_small.npy').strip().splitlines()[-1])
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    fig = os.path.join(work(t), f"{t['slug']}-final-{a.version}-figma4096.jpg")
    Image.open(out).resize((4096, 4096), Image.LANCZOS).save(fig, quality=95, subsampling=0)
    t['master'] = rel(out)
    t['render_pick'] = rel(a.render) if os.path.isabs(a.render) else a.render
    t['finish_report'] = {k: r[k] for k in ('falloff', 'horizon', 'holes_opened', 'glass_share_of_device', 'deltaE_glow_vs_swatch', 'backdrop_hue_spread_deg', 'corner_L_minus_glow', 'device_touches_edge', 'offset', 'render') if k in r}
    t['figma']['post_transform'] = fr['post']; t['figma']['canvas_transform'] = fr['canvas']
    t['status'] = f'master {a.version} finished, Josh yes then place'
    t['next'] = 'Put the master next to Deluge v1 on a Review board, on Josh\'s yes place it in the Photo slots and cover.py drive ' + t['n']
    save(d)
    flags = []
    if r['deltaE_glow_vs_swatch'] >= 3: flags.append('glow off the swatch')
    if r['device_touches_edge']: flags.append('device touches the render edge, crop again')
    if r.get('backdrop_hue_spread_deg', 0) > 2: flags.append('backdrop hue spread')
    print(json.dumps({'master': rel(out), 'figma_copy': rel(fig), 'post': fr['post'], 'canvas': fr['canvas'], 'flags': flags}))


def cmd_drive(a):
    d = load(); t = get(d, a.n)
    files = []
    if a.what in ('render', 'both') and t.get('render_pick'):
        files.append(os.path.join(ROOT, t['render_pick']))
    if a.what in ('master', 'both') and t.get('master'):
        files.append(os.path.join(ROOT, t['master']))
    if not files:
        sys.exit('nothing to upload yet')
    for f in files:
        run(PY, 'pipeline/drive.py', 'put', f, '--track', t['n'])


def main():
    ap = argparse.ArgumentParser()
    s = ap.add_subparsers(dest='cmd', required=True)
    p = s.add_parser('status'); p.add_argument('n', nargs='?')
    p = s.add_parser('prompt'); p.add_argument('n'); p.add_argument('--round', default='1'); p.add_argument('--force', action='store_true')
    p = s.add_parser('explore'); p.add_argument('n'); p.add_argument('--round', default='1'); p.add_argument('--n', dest='n_frames', type=int, default=3)
    p = s.add_parser('lock'); p.add_argument('n'); p.add_argument('frame'); p.add_argument('--pick', required=True)
    p = s.add_parser('render'); p.add_argument('n'); p.add_argument('--runs', type=int, default=1); p.add_argument('--source'); p.add_argument('--ref', action='append', default=[], help='extra detail reference images'); p.add_argument('--approved', required=True, help="Josh's written yes, quoted, given after Claude pointed him to the explore frame in Figma this session")
    p = s.add_parser('finish'); p.add_argument('n'); p.add_argument('--render', required=True); p.add_argument('--version', default='v1'); p.add_argument('--glass-box', help='x0,y0,x1,y1 render fractions around a clear part, see finish.py')
    p = s.add_parser('drive'); p.add_argument('n'); p.add_argument('--what', default='both', choices=['render', 'master', 'both'])
    a = ap.parse_args()
    globals()['cmd_' + a.cmd](a)


if __name__ == '__main__':
    main()
