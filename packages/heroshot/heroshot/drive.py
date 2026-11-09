"""Save big files to Google Drive through a tiny Apps Script web app (scaffold: drive_drop.gs).
Chat connectors pass file contents through the conversation and cannot carry a 13 MB master.
Needs HEROSHOT_DRIVE_URL and HEROSHOT_DRIVE_KEY in the environment, never in a file."""
import base64, json, os, sys, urllib.request


def env():
    url, key = os.environ.get("HEROSHOT_DRIVE_URL"), os.environ.get("HEROSHOT_DRIVE_KEY")
    if not url or not key:
        sys.exit("heroshot: HEROSHOT_DRIVE_URL and HEROSHOT_DRIVE_KEY are not set, Drive upload is not wired. "
                 "See .claude/skills/heroshot/reference/drive.md. Fallback: hand the files over in chat.")
    return url, key


def call(body):
    url, key = env()
    req = urllib.request.Request(url, data=json.dumps(dict(body, key=key)).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:   # Apps Script redirects the POST, urllib follows it
        raw = r.read().decode()
    try:
        res = json.loads(raw)
    except ValueError:
        sys.exit("heroshot: Drive drop did not answer JSON. Deploy it as a web app, execute as you, access Anyone. First bytes: " + raw[:300])
    if not res.get("ok"):
        sys.exit("heroshot: Drive drop refused: " + str(res.get("error")))
    return res


def put(path, folder, name=None, replace=True):
    name = name or os.path.basename(path)
    mime = "image/png" if name.lower().endswith(".png") else "image/jpeg"
    data = base64.b64encode(open(path, "rb").read()).decode()
    res = call({"action": "put", "folderId": folder, "name": name, "mimeType": mime, "data": data, "replace": replace})
    return {k: res.get(k) for k in ("id", "name", "bytes", "folder", "url")}


def listing(folder):
    return call({"action": "list", "folderId": folder})
