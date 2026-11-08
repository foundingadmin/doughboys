"""Save big files into the Track Covers folders on Drive, through the Drive drop web app.

The Drive connector passes file contents through the conversation, so it cannot carry a 13 MB
master. This posts the file to pipeline/drive_drop.gs, deployed once under Josh's account.
Needs TFB_DRIVE_URL and TFB_DRIVE_KEY in the environment (setup: the-first-batch/docs/drive.md).

  python3 pipeline/drive.py check
      confirms the web app answers and lists the Track Covers root
  python3 pipeline/drive.py put FILE --track 05 [--to masters|exports|archive] [--name NAME] [--keep]
      uploads FILE into that track's folder (Masters by default), replacing a file of the same name
      unless --keep, and records the Drive file id in tracks.json under drive_masters_files
  python3 pipeline/drive.py list --track 05 [--to masters]
"""
import argparse, base64, json, os, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TRACKS = os.path.join(ROOT, 'the-first-batch', 'tracks.json')


def env():
    url, key = os.environ.get('TFB_DRIVE_URL'), os.environ.get('TFB_DRIVE_KEY')
    if not url or not key:
        sys.exit('TFB_DRIVE_URL and TFB_DRIVE_KEY are not set. Drive upload is not wired in this environment, '
                 'see the-first-batch/docs/drive.md. Fallback: commit the file and tell Josh to drop it into Drive.')
    return url, key


def call(body):
    url, key = env()
    body = dict(body, key=key)
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method='POST', headers={'Content-Type': 'application/json'})
    # Apps Script answers a POST with a redirect to script.googleusercontent.com; urllib follows it as a GET
    with urllib.request.urlopen(req, timeout=600) as r:
        raw = r.read().decode()
    try:
        res = json.loads(raw)
    except ValueError:
        sys.exit('Drive drop did not answer with JSON. Check the deployment is a web app that runs as Josh with access Anyone. First bytes: ' + raw[:300])
    if not res.get('ok'):
        sys.exit('Drive drop refused: ' + str(res.get('error')))
    return res


def track(n):
    d = json.load(open(TRACKS))
    for t in d['tracks']:
        if t['n'] == n.zfill(2):
            return d, t
    sys.exit(f'no track {n} in tracks.json')


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('check')
    p = sub.add_parser('put'); p.add_argument('file'); p.add_argument('--track', required=True)
    p.add_argument('--to', default='masters', choices=['masters', 'exports', 'archive']); p.add_argument('--name'); p.add_argument('--keep', action='store_true')
    l = sub.add_parser('list'); l.add_argument('--track', required=True); l.add_argument('--to', default='masters', choices=['masters', 'exports', 'archive'])
    a = ap.parse_args()

    if a.cmd == 'check':
        d = json.load(open(TRACKS))
        res = call({'action': 'list', 'folderId': d['drive_track_covers']})
        print(f"ok · {res['folder']} · {len(res['files'])} loose files at the root")
        return
    d, t = track(a.track)
    folder = t['drive'][a.to]
    if a.cmd == 'list':
        res = call({'action': 'list', 'folderId': folder})
        for f in sorted(res['files'], key=lambda f: f['name']):
            print(f"{f['name']}  {f['bytes'] / 1e6:.1f} MB  {f['id']}")
        return
    name = a.name or os.path.basename(a.file)
    mime = 'image/png' if name.lower().endswith('.png') else 'image/jpeg'
    data = base64.b64encode(open(a.file, 'rb').read()).decode()
    res = call({'action': 'put', 'folderId': folder, 'name': name, 'mimeType': mime, 'data': data, 'replace': not a.keep})
    print(json.dumps({k: res[k] for k in ('id', 'name', 'bytes', 'folder', 'url')}))
    if a.to == 'masters':
        t.setdefault('drive_masters_files', {})[name] = res['id']
        json.dump(d, open(TRACKS, 'w'), indent=1, ensure_ascii=False); open(TRACKS, 'a').write('\n')


if __name__ == '__main__':
    main()
