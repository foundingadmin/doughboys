# Lessons

Newest at the bottom of each section. Add a dated line when something fails or surprises you.

## Resolution

- Upscaling a low res render does not work. Topaz Gigapixel invented grille and panel detail on Deluge (Oct 18 2026). Detail has to come from a 4K generation edit of the approved frame.
- The 4K pass spends about the same 17 megapixels on any aspect. A square run of Traycee left the computer at about 87 percent of 4096 and the rest went to backdrop. Crop tight first, at the closest supported aspect (Josh, Oct 28 2026).
- Deluge v1 is the 5056 × 3392 render placed untouched at 1:1 on a 6704 canvas, offset 824, 1656, with Photoshop Generative Expand filling the rest. Found by feature matching, scale 1.000 (Oct 28 2026). finish.py does the same placement.

## Finish pipeline

- A global blur plus a straight line fit of the backdrop extrapolated wildly, white at the bottom and deep blue at the top. Anchoring the extension to the render's own border and continuing each edge's falloff fixed it.
- A smooth fill leaves a visible step at the seam because the render's backdrop has grain and mottle. finish.py synthesizes texture from the render's own backdrop spectrum.
- Scaling chroma blew the gamut in the corners. Josh's correction behaves like a colorize: keep lightness shape, pull chroma to the target almost flat, shift hue. That is what the recolor does now.
- Measure the glow only on real render pixels inside Josh's check ellipse, never on the generated extension.
- Calibration on Deluge: backdrop color inside the render lands within deltaE 2.2 of Josh's hand made v1.
- finish.py crashed on `"#73D2AB"` because it parsed the hex without stripping the `#`, though CLAUDE.md passes it that way. Fixed to accept both (Oct 29 2026).

## Crop and 4K

- `gen.py crop` picked 3:2 for Traycee, not the 16:9 the brief expected. The device box is about 1.59 wide, so 3:2 keeps more pixels on the device. Trust the auto pick unless something gets cut (Oct 29 2026).
- 4K edits turn small screen UI into fake text. On Traycee the taskbar grew a garbled Start label and clock, and the CD player buttons got smudged glyphs. Name every UI strip in the 4K prompt and say exactly what it shows, or that it is plain (Oct 29 2026).
- Naming them fixed it in one re-run: the transport buttons came back as clean play, pause, stop and eject symbols, the taskbar went plain, and asking for one solid column closed the hole in Traycee's dough (render B, Oct 29 2026).
- Gemini returns JPEG bytes even when `gen.py` saves to a `.png` name. Store renders in the repo as `.jpg`, untouched (Oct 29 2026).

## Docs

- CLAUDE.md now says how to keep art-direction.md, tracks.json and this file current. Update all three in the same commit as the work (Oct 29 2026).

## Prompts

- Specific beats simple. Naming every label word, dial number and drip to remove worked on Deluge (Oct 18 2026).
- The explore lessons (softbox, raised camera for turntables, no pink cast, own silhouette per track) live in prompts/explore/series-lock.md.

## Tools and network

- Gemini image API needs `generativelanguage.googleapis.com` allowed in the environment. Figma asset upload posts to `mcp.figma.com`, image downloads come from `www.figma.com`.
- Weave in Figma runs the same Nano Banana Pro edit model for 23 credits per 4K run. Fallback only, ask Josh before each run.
- Large binaries cannot go through the Drive connector, it passes file contents through the conversation. GitHub is the hand off for masters. Server side Drive copies of files already on Drive are fine.
- Chat uploads shrink loose images to 2576 px. Full size files travel zipped, or through the repo.

## Figma

- See docs/figma.md. Scripts are atomic, pages reset per call, fonts load before any text change.
- `upload_assets` caps a file at 10 MB, so a 12 MB master will not go. Figma also stores images at 4096 px max. Upload a 4096 square JPG q95 downscale of the master (about 2.4 MB for Deluge). The repo and Drive keep the full 6704 (Oct 29 2026).
- `upload_assets` without a target node drops a new frame on the page. Delete it in the same `use_figma` call that fills the boards (Oct 29 2026).
