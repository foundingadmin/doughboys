// Review page layout (Josh, Nov 8 2026): one Figma section per stage of development, left to right
// Exploration, 4K, Complete. Inside each section, one column per track in album order, rounds stacked
// oldest at the top. Boards are named "CBDB NN ...". Fill STAGE from tracks.json before running:
//   placed in Figma -> Complete; source approved, 4K rendered, master finished -> 4K; everything else -> Exploration.
// figma_review_board.js runs this same pass after adding a board.
const STAGE = { "01": "Complete", "02": "Complete", "03": "Complete", "04": "Exploration", "05": "Complete", "06": "Complete", "07": "4K", "08": "4K", "09": "Exploration" };

async function layoutReview(page) {
  await figma.loadFontAsync({ family: "Anton", style: "Regular" });
  await figma.loadFontAsync({ family: "Archivo", style: "Regular" });
  const ORDER = ["Exploration", "4K", "Complete"];
  const NOTE = { "Exploration": "Low res explore rounds on Flash. Josh picks a frame.", "4K": "Approved source, 4K render and check, finish and master review.", "Complete": "Master approved and placed on Cover, Post and Canvas." };
  const GAP = 400, PAD = 600, HEAD = 1600;
  const boards = page.findAll(n => n.type === "FRAME" && /^CBDB \d\d/.test(n.name) && (n.parent.type === "PAGE" || n.parent.type === "SECTION"));
  const sections = {};
  for (const n of page.children) if (n.type === "SECTION" && ORDER.includes(n.name)) sections[n.name] = n;
  for (const b of boards) { const ax = b.absoluteTransform[0][2], ay = b.absoluteTransform[1][2]; page.appendChild(b); b.x = ax; b.y = ay; }
  const num = id => id.split(":").map(Number);
  let sx = 0; const out = {};
  for (const stage of ORDER) {
    let sec = sections[stage];
    if (!sec) { sec = figma.createSection(); sec.name = stage; page.appendChild(sec); }
    for (const c of [...sec.children]) c.remove();
    const cols = {};
    for (const b of boards) { const k = b.name.slice(5, 7); if ((STAGE[k] || "Exploration") === stage) (cols[k] ||= []).push(b); }
    const title = figma.createText(); title.fontName = { family: "Anton", style: "Regular" }; title.fontSize = 900; title.characters = stage.toUpperCase();
    const note = figma.createText(); note.fontName = { family: "Archivo", style: "Regular" }; note.fontSize = 160; note.characters = Object.keys(cols).length ? NOTE[stage] : NOTE[stage] + " No track here right now.";
    sec.appendChild(title); sec.appendChild(note);
    title.x = PAD; title.y = PAD - 200; note.x = PAD; note.y = PAD + 950;
    let cx = PAD, maxH = 0;
    for (const k of Object.keys(cols).sort()) {
      let y = PAD + HEAD, w = 0;
      for (const b of cols[k].sort((a, b) => { const [a1, a2] = num(a.id), [b1, b2] = num(b.id); return a1 - b1 || a2 - b2; })) {
        sec.appendChild(b); b.x = cx; b.y = y; y += b.height + GAP; w = Math.max(w, b.width);
      }
      maxH = Math.max(maxH, y - GAP); cx += w + GAP;
    }
    const W = Math.max(cx - GAP + PAD, title.width + 2 * PAD, note.width + 2 * PAD), H = Math.max(maxH + PAD, PAD + HEAD + PAD);
    sec.x = sx; sec.y = 0; sec.resizeWithoutConstraints(W, H);
    out[stage] = Object.keys(cols).sort();
    sx += W + 2000;
  }
  return out;
}
