# Drive · saving renders and masters

Chat connectors pass file contents through the conversation, so they cannot carry a 13 MB master. `heroshot drive ID` posts the picked render and the master to a small Apps Script web app (`drive_drop.gs`, next to this file) that runs as the folder owner and only writes inside one folder tree, only for a caller that sends the key.

## One time setup (about five minutes)

1. script.google.com, New project. Paste `drive_drop.gs`. Save.
2. Project Settings, Script properties:
   - `KEY` · a long random string from a password manager
   - `ROOT` · the id of the Drive folder that holds this project's files
3. Deploy, New deployment, Web app. Execute as **Me**, access **Anyone**. Approve the Drive permission, copy the URL ending in `/exec`.
4. In the Claude Code environment settings (where `GEMINI_API_KEY` lives) add `HEROSHOT_DRIVE_URL` (the URL) and `HEROSHOT_DRIVE_KEY` (the same string as `KEY`).
5. New session, `heroshot doctor` reports Drive upload wired.

Per item, set `drive_folder` in heroshot.json to the folder its masters go in, or set `drive.default_folder` once. Folders must sit inside `ROOT`.

The key never goes in a file, a commit or a message.

## When it is not wired

`heroshot drive` stops with a clear message. Attach the files to the reply with SendUserFile (`display: attach`) and say which folder they belong in. Do that even when Drive is wired, it is the fastest hand off.
