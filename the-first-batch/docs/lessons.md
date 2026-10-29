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
