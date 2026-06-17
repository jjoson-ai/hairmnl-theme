const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Preview Review, Round 5";

// ---- palette ----
const INK = "1F2933", TERRA = "B85042", WHITE = "FFFFFF", MUTED = "5A6470",
      LIGHT = "F3F4F6", ICE = "CAD3DC", GREEN = "2E7D5B", AMBER = "C77D34", GRAY = "8A8F98";
const HF = "Georgia", BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com";
const NF = "?preview_theme_id=141655801955&_fd=0&_sc=1"; // NEW: STKY-free preview theme
const L  = (path) => STORE + path + NF;                  // clean preview link
const LIVE = (path) => STORE + path;                     // live site (banner check)
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function footer(slide, n) {
  slide.addText("HairMNL · Pipeline 8 — preview review · round 5 (re-test of 16 Jun)", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "left", margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(slide, label, title) {
  slide.addText(label.toUpperCase(), { x: 0.5, y: 0.4, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.5, y: 0.72, w: 12.3, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: INK, margin: 0 });
}
function pill(text, color) { return { text, options: { fill: { color }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 9.5, fontFace: BF } }; }
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle", align: "left" } });
const tc = (t, opts = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: opts.fill || WHITE }, ...opts } });

// ============ SLIDE 1 — TITLE ============
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · STORE PREVIEW · ROUND 5", { x: 0.9, y: 1.35, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("You asked to see it without the old app. Here it is.", { x: 0.9, y: 1.85, w: 11.9, h: 1.3, fontFace: HF, fontSize: 38, bold: true, color: WHITE, margin: 0 });
s.addText("We've set up a clean preview with the old sticky-cart app switched off — so you can finally see the new buttons on their own, no doubled-up icons. Your June 16 re-tests are all addressed: the icon is back to its original size, the suggestion cards line up, and the cut-off ADD TO CART button is fixed.",
  { x: 0.9, y: 3.3, w: 11.2, h: 1.2, fontFace: BF, fontSize: 16, color: ICE, margin: 0, lineSpacingMultiple: 1.1 });
s.addText([
  { text: "Open the clean preview:  ", options: { color: ICE } },
  { text: "click here", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "   — give the first page a few seconds to load (brand-new preview, not yet cached).", options: { color: GRAY } },
], { x: 0.9, y: 4.95, w: 11.8, h: 0.5, fontFace: BF, fontSize: 12, margin: 0 });

// ============ SLIDE 2 — SUMMARY ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Where things stand", "Your re-tests, addressed — plus a clean preview");
const stats = [
  { n: "NEW", t: "a clean, app-free preview", d: "the old sticky-cart app is switched off here — you see only the new native buttons, one per product", c: GREEN },
  { n: "✓", t: "icon back to original size", d: "reverted to the smaller first-version cart symbol you pointed to, on every page", c: TERRA },
  { n: "✓", t: "suggestion cards line up", d: "same image size now, so titles & prices sit in a neat row — checked on the preview", c: INK },
  { n: "1", t: "quick phone check left", d: "the sticky-bar button & banner edges on a real phone, then sign-off", c: AMBER },
];
const sx = 0.5, sy = 1.7, sw = 3.55, sh = 1.95, gap = 0.32;
stats.forEach((it, i) => {
  const x = sx + (i % 2) * (sw + gap), y = sy + Math.floor(i / 2) * (sh + gap);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: sw, h: sh, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.1, h: sh, fill: { color: it.c } });
  s.addText(it.n, { x: x + 0.25, y: y + 0.14, w: sw - 0.5, h: 0.82, fontFace: HF, fontSize: 38, bold: true, color: it.c, margin: 0, align: "left" });
  s.addText(it.t, { x: x + 0.27, y: y + 0.98, w: sw - 0.5, h: 0.45, fontFace: BF, fontSize: 13, bold: true, color: INK, margin: 0 });
  s.addText(it.d, { x: x + 0.27, y: y + 1.40, w: sw - 0.45, h: 0.52, fontFace: BF, fontSize: 10.5, color: MUTED, margin: 0 });
});
s.addShape(pres.shapes.RECTANGLE, { x: 8.35, y: 1.7, w: 4.5, h: 4.22, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText("The short version", { x: 8.55, y: 1.85, w: 4.1, h: 0.35, fontFace: BF, fontSize: 13, bold: true, color: TERRA, margin: 0 });
s.addText([
  { text: "Everything from your June 16 list is done — the icon size, the cut-off button, and the suggestion-card alignment.", options: { color: MUTED, breakLine: true } },
  { text: "\nThe big change: you can now review on a preview with the old app turned off, so the doubled-up buttons that made it hard to judge are gone. The new Quick Buy buttons work — there's just one quirk about adding to cart on a preview vs. the live store, explained on the next slide.", options: { color: MUTED } },
], { x: 8.55, y: 2.25, w: 4.1, h: 3.5, fontFace: BF, fontSize: 11, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });
footer(s, 2);

// ============ SLIDE 3 — THE CLEAN PREVIEW ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "The clean preview", "See the new buttons without the old app");

// left: what it is + link
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 6.05, h: 4.55, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addText("What this is", { x: 0.72, y: 1.85, w: 5.6, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText([
  { text: "A second preview where the old sticky-cart app is switched off.", options: { color: "30373E", breakLine: true, bold: true } },
  { text: "\nOn the regular preview the old app is still installed, so every product shows two cart buttons — the old one and the new one — which made the new design hard to judge. Here you see only the new native button: one clean cart icon per product.", options: { color: MUTED, breakLine: true } },
  { text: "\nThis is exactly how the store will look after switch-over.", options: { color: MUTED, italic: true } },
], { x: 0.72, y: 2.25, w: 5.6, h: 2.4, fontFace: BF, fontSize: 11.5, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });
s.addShape(pres.shapes.RECTANGLE, { x: 0.72, y: 5.25, w: 5.6, h: 0.82, fill: { color: INK } });
s.addText([
  { text: "Open it:  ", options: { color: GRAY } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Product", options: { hyperlink: { url: L("/products/american-crew-fiber") }, color: WHITE, bold: true } },
], { x: 0.9, y: 5.25, w: 5.3, h: 0.82, fontFace: BF, fontSize: 12, valign: "middle", margin: 0 });

// right: the one quirk (add-to-cart on preview)
s.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.7, w: 6.03, h: 4.55, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText("One thing to know: adding to cart", { x: 7.02, y: 1.85, w: 5.6, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: TERRA, margin: 0 });
s.addText([
  { text: "The buttons work. Two behaviours to expect on the preview:", options: { color: "30373E", breakLine: true, bold: true } },
  { text: "\n•  Products with options (sizes, etc.): tapping the icon opens a little size / variant picker — this works on the preview, please try it.", options: { color: MUTED, breakLine: true } },
  { text: "\n•  Single-option products: tapping adds them — but only on the live store. On a preview the actual \"add\" step is blocked by another app running in the background, so it can look like nothing happens. That's a preview-only limitation, not a fault in the button — on the real store it adds normally.", options: { color: MUTED } },
], { x: 7.02, y: 2.25, w: 5.6, h: 3.9, fontFace: BF, fontSize: 11.5, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });
footer(s, 3);

// ============ SLIDE 4 — RE-TESTS, POINT BY POINT ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Your June 16 notes", "Point by point");
const rows = [
  [hcell("You said"), hcell("Status"), hcell("What it does now")],
  [tc("Quick Buy not working — and can we preview without the old app?"),
   pill("DONE", GREEN),
   tc("Clean preview built (this deck). One cart icon per product. Variant picker opens on tap; single-option products add on the live store — see slide 3.")],
  [tc("Quick Buy icon now too big — on Home, Cart page and Cart Drawer"),
   pill("FIXED", GREEN),
   tc("Reverted to the original, smaller cart symbol from the first version you pointed to, on every page. On the drawer the circle stayed the same size — only the cart symbol inside got a touch bigger so it isn't faint.")],
  [tc("PDP mobile sticky bar: ADD TO CART gets cut off (varies by product)"),
   pill("FIXED — confirm on phone", AMBER),
   tc("A long variant name (e.g. \"FREE Absolut Rep\") was pushing the button off the screen edge. The variant box now shrinks first, so ADD TO CART always shows in full.")],
  [tc("Suggestion cards not aligned — product page and cart drawer"),
   pill("FIXED — verified", GREEN),
   tc("Every card now uses the same image size, so the titles and prices line up in a neat row. Checked on the preview.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.65, w: 12.33, colW: [3.95, 1.95, 6.43],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 0.95, 1.15, 1.0, 0.85], margin: [3, 5, 3, 5],
});
footer(s, 4);

// ============ SLIDE 5 — NEXT STEPS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Over to you", "One review on the clean preview, then we go live");

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 12.33, h: 2.05, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 2.35, w: 0.55, h: 0.55, fill: { color: TERRA } });
s.addText("1", { x: 0.72, y: 2.35, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Review on the clean preview", { x: 1.5, y: 1.85, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText("On a computer:", { x: 1.5, y: 2.24, w: 11.1, h: 0.3, fontFace: BF, fontSize: 11, color: MUTED, margin: 0 });
s.addText([
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: TERRA, bold: true } },
  { text: " (one clean icon per product)      ", options: { color: MUTED } },
  { text: "Product", options: { hyperlink: { url: L("/products/american-crew-fiber") }, color: TERRA, bold: true } },
  { text: " (suggestion cards line up)      ", options: { color: MUTED } },
  { text: "Cart", options: { hyperlink: { url: L("/cart") }, color: TERRA, bold: true } },
  { text: " (drawer suggestions)", options: { color: MUTED } },
], { x: 1.5, y: 2.58, w: 11.1, h: 0.5, fontFace: BF, fontSize: 11, valign: "top", margin: 0 });
s.addText([
  { text: "On a phone (the two things we couldn't show you on a desktop):  ", options: { italic: true, color: INK } },
  { text: "the ADD TO CART button is no longer cut off on product pages, and the homepage banner fills the screen edge-to-edge.", options: { italic: true, color: MUTED } },
], { x: 1.5, y: 3.12, w: 11.2, h: 0.5, fontFace: BF, fontSize: 11, valign: "top", margin: 0 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.0, w: 12.33, h: 1.55, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 4.55, w: 0.55, h: 0.55, fill: { color: GREEN } });
s.addText("2", { x: 0.72, y: 4.55, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Sign off → switch-over", { x: 1.5, y: 4.15, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText([
  { text: "We publish the new theme and uninstall the old sticky-cart app for real (what you're previewing now becomes the live experience). The add-to-cart quirk from slide 3 disappears at this point, because it only affects previews.", options: { color: MUTED, breakLine: true } },
  { text: "\nThis also cancels the old app's $24.99/month subscription — about ₱17k/year back.", options: { color: MUTED } },
], { x: 1.5, y: 4.51, w: 11.3, h: 0.95, fontFace: BF, fontSize: 11, color: MUTED, margin: 0, valign: "top", lineSpacingMultiple: 1.05 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.8, w: 12.33, h: 0.95, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "Tip:  ", options: { bold: true, color: TERRA } },
  { text: "use the clean-preview links in this deck (not last week's tab). If something still looks off after a genuinely fresh load, tell us which page and we'll jump on it.", options: { color: MUTED } },
], { x: 0.7, y: 5.86, w: 12.0, h: 0.82, fontFace: BF, fontSize: 11.5, valign: "middle", margin: 0 });
footer(s, 5);

// ============ SLIDE 6 — CLOSING ============
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("BOTTOM LINE", { x: 0.9, y: 1.7, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("A clean preview, and your list is done.", { x: 0.9, y: 2.2, w: 11.7, h: 1.5, fontFace: HF, fontSize: 34, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "The old app is switched off in this preview, so you can judge the new buttons on their own. The icon is back to its original size, the suggestion cards line up, and the cut-off button is fixed. ", options: { color: ICE } },
  { text: "Have a look on a phone for the sticky bar and banner, and we're clear to switch over.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 3.65, w: 11.3, h: 1.6, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
s.addText([
  { text: "Open the clean preview:  ", options: { color: GRAY } },
  { text: "click here", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "      ·      Questions? Reply on the project thread.", options: { color: GRAY } },
], { x: 0.9, y: 6.5, w: 11.5, h: 0.3, fontFace: BF, fontSize: 12, margin: 0 });

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Preview-Review-R5.pptx" }).then(f => console.log("WROTE", f));
