# Explore prompt · series lock

Every explore prompt is the template below, word for word, with only the bracketed parts rewritten per item. Lock the style line once with the approver at the start of the project, then never drift from it: consistency across the series comes from these words, not from reference images. `heroshot prompt ID` fills `{SUBJECT}`, `{SHAPE}`, `{GROUND}` and `{GROUND_HEX}` from heroshot.json, then Claude rewrites the brackets as plain prose.

## Template

```
A real studio product photograph for a printed catalog, shot on medium format film with an 80mm lens, fine film grain, muted print color. [SUBJECT · {SUBJECT}: name it part by part, with its buttons, labels as plain shapes, materials and finishes, and a small glowing light where a real one would sit.] [REAL PROPORTIONS: state the size relationship that makes it believable, for example the body is only slightly larger than a standard audio cassette.]

[ARRANGEMENT · {SHAPE}: describe this item's own silhouette and what sits with the subject, where the weight goes and how it meets the floor.]

Camera straight on at the subject's own height, squared up to its front. The subject fills about half the frame height. Every object sits inside the frame with clear backdrop at every edge. Nothing cropped.

Seamless {GROUND} paper sweep, no horizon line, no seams, no studio equipment. Soft diffused light from the upper left, from a source well outside the frame, soft contact shadow only. A brighter glow behind the subject and on the floor, falling to a deeper {GROUND} in the top corners.

No people, no hands, no logos, no brand names, no readable text.
```

## Rules that came from failures

- Never name a softbox or any light fixture. Naming it puts the light in frame. Describe the light without the word.
- A subject that must show its top (a turntable platter, a keyboard) gets a front view raised about 25 degrees, still squared up to the front.
- Say real proportions. Without them the generator draws toy sized parts.
- Every item gets its own silhouette. If every arrangement ends in the same shape, the set starts to rhyme.
- Exploration says no readable text. The hi res prompt supplies the exact words later.
- Watch for faces. Two round parts side by side read as eyes, something poking out of an opening reads as a tongue. Say "nothing pokes out like a tongue" and break up pairs.
- Iconic objects must look exactly like the real one or the cultural link breaks. Name the year and model features, keep logos off.
- To change one thing on a picked frame, pass it with `--ref` and open "Keep this exact photograph and replace only the <thing>". Everything else holds.
