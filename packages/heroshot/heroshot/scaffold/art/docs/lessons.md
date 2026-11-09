# Lessons

Add a dated line whenever a tool, model or step fails or surprises you. If it changes how prompts are written, fold it into the series lock too.

## Carried in from earlier projects

- Upscaling a low res render does not work: upscalers invent detail. Detail has to come from a 4K generation edit of the approved frame.
- The 4K pass spends about the same pixels on any aspect. Crop tight to the subject first, at the closest supported aspect, or the detail goes to empty backdrop.
- 4K edits turn small screens and UI into fake text. Name every screen and strip in the hi res prompt and say exactly what it shows, or that it is plain.
- Gemini returns JPEG bytes whatever the file name. Renders are stored as .jpg, untouched.
- Rebuild the backdrop, never extend or blend the generator's own. Its hotspots, bands and drifting hue show up as soon as the image is enlarged. Keep only the subject, contact shadows and grain.
- One paper: keep each backdrop pixel's OKLab lightness and take hue and chroma from the swatch. Scaling chroma blows the gamut in the corners.
- Never take a median of hue angles, they wrap. Take the median of Lab a and b, then the angle.
- deltaE alone does not pass a finish. Look at the full frame next to the last approved master.
- Run no more than three finish jobs at once on a 16 GB container.
- Two steps that write the state file at the same moment used to drop each other's records. heroshot locks the file now, but still run paid steps one after another so the approver sees them in order.
- The cheapest way to change one thing on a picked frame is an explore with the pick as `--ref` and a "keep this exact photograph" prompt. The rest held frame for frame on the fast model.

## This project
