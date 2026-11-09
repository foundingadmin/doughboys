<!-- heroshot -->
## heroshot · series photo pipeline

This repo makes its product photos with heroshot (installed with pip, the `heroshot` command). `heroshot.json` is the config and every item's state, `{DIR}/` holds prompts, sources, renders, masters, review crops, the brief and lessons. `work/` is scratch and ignored.

Any request about exploring, rendering, finishing or placing an item means: load the `heroshot` skill (`.claude/skills/heroshot/SKILL.md`) and follow it. It stops at four approval gates. No 4K run without the approver's fresh written yes in the conversation.

Session start: `heroshot doctor`. Network needed: `generativelanguage.googleapis.com` (Gemini), `mcp.figma.com` and `www.figma.com` (Figma uploads), GitHub and PyPI.

Keep `heroshot.json`, `{DIR}/docs/brief.md` and `{DIR}/docs/lessons.md` current in the same commit as the work. Keys live only in the environment (`GEMINI_API_KEY`, `HEROSHOT_DRIVE_URL`, `HEROSHOT_DRIVE_KEY`).
