# Drive · saving renders and masters

Long term storage is the Track Covers folder `1g-RHVswNtj1Jp1VKjKmd3OZwDprvnKfB`. Each track folder holds **Masters**, **Exports** and **Archive**. Folder ids are in `tracks.json` under each track's `drive`.

What goes where:
- **Masters** · the picked 4K render (`NN-track-4k-render-...jpg`) and the finished master (`NN-track-final-v1.jpg`). `pipeline/cover.py drive NN` sends both.
- **Exports** · Josh exports the Cover, Post and Canvas from Figma (preset on every board) and drops them here.
- **Archive** · Josh's old manual step folders. Never delete.

## Why a web app

The Drive connector passes file contents through the conversation, so it cannot carry a 9 to 20 MB master. `pipeline/drive.py` posts the file to a small Apps Script web app instead, `pipeline/drive_drop.gs`, which runs as Josh and only writes inside the Track Covers tree, only for a caller that sends the key.

## One time setup (Josh, about five minutes)

1. Go to script.google.com, New project, name it `Drive drop · The First Batch`.
2. Replace the code with the contents of `pipeline/drive_drop.gs`. Save.
3. Project Settings, Script properties, add:
   - `KEY` · a long random string. Make one with a password manager.
   - `ROOT` · `1g-RHVswNtj1Jp1VKjKmd3OZwDprvnKfB`
4. Deploy, New deployment, type Web app. Execute as **Me**. Who has access **Anyone**. Deploy, approve the Drive permission, copy the web app URL (it ends in `/exec`).
5. In the Claude Code environment settings for this repo (the environment that already holds `GEMINI_API_KEY`), add two environment variables:
   - `TFB_DRIVE_URL` · the web app URL
   - `TFB_DRIVE_KEY` · the same random string as `KEY`
6. Start a new session. `python3 pipeline/drive.py check` should print `ok · Track Covers`.

The key never goes in a file, a commit or a message. It lives only in the environment and in the script's properties.

## Use

```bash
python3 pipeline/drive.py check
```

```bash
python3 pipeline/cover.py drive 05
```

```bash
python3 pipeline/drive.py put FILE --track 05 --to masters
```

```bash
python3 pipeline/drive.py list --track 05
```

`put` replaces a file of the same name in that folder (the old one goes to Drive's trash) unless `--keep`. Masters uploads are recorded in `tracks.json` under `drive_masters_files`.

## When it is not wired

`drive.py` stops with a clear message. Commit the files and tell Josh which two to drop into which Masters folder. Small files (under about 1 MB, like contact sheets) can still go through the Drive connector's `create_file` with `base64Content`.
