const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Preview Review, Round 4";

// ---- palette ----
const INK = "1F2933", TERRA = "B85042", WHITE = "FFFFFF", MUTED = "5A6470",
      LIGHT = "F3F4F6", ICE = "CAD3DC", GREEN = "2E7D5B", AMBER = "C77D34", GRAY = "8A8F98";
const HF = "Georgia", BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com", PID = "?preview_theme_id=141168312419";
const L = (path) => STORE + path + PID;
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 135, opacity: 0.16 });

function footer(slide, n) {
  slide.addText("HairMNL · Pipeline 8 — preview review · round 4 (16 Jun comments)", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "left", margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(slide, label, title) {
  slide.addText(label.toUpperCase(), { x: 0.5, y: 0.4, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.5, y: 0.72, w: 12.3, h: 0.7, fontFace: HF, fontSize: 30, bold: true, color: INK, margin: 0 });
}
function pill(text, color) { return { text, options: { fill: { color }, color: WHITE, bold: true, align: "center", valign: "middle", fontSize: 10, fontFace: BF } }; }
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle", align: "left" } });
const tc = (t, opts = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: opts.fill || WHITE }, ...opts } });

// ============ SLIDE 1 — TITLE ============
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · STORE PREVIEW · ROUND 4", { x: 0.9, y: 1.45, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Your June 16 comments — all addressed", { x: 0.9, y: 1.95, w: 11.8, h: 1.3, fontFace: HF, fontSize: 42, bold: true, color: WHITE, margin: 0 });
s.addText("Recommendations now skip what's already in the cart, the Quick Buy icon is bigger and bolder, the mobile bar button has its margin — and the mobile banner is fixed and live (it was a caching issue, explained inside).",
  { x: 0.9, y: 3.35, w: 11, h: 1.0, fontFace: BF, fontSize: 16, color: ICE, margin: 0 });
s.addText([
  { text: "Open the preview store:  ", options: { color: ICE } },
  { text: "click here", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "   — please use a brand-new window / hard refresh (see slide 4).", options: { color: GRAY } },
], { x: 0.9, y: 4.7, w: 11.6, h: 0.5, fontFace: BF, fontSize: 12, margin: 0 });

// ============ SLIDE 2 — SUMMARY ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Where things stand", "5 of 5 addressed — and the banner is live");
const stats = [
  { n: "5", t: "of 5 June-16 comments done", d: "every slide in your review", c: GREEN },
  { n: "✓", t: "recs skip cart items now", d: "verified: an item drops out of the suggestions the moment it's in the cart", c: TERRA },
  { n: "LIVE", t: "mobile banner deployed", d: "fixed on the live site — the earlier reports were a cached page", c: INK },
  { n: "1", t: "step left", d: "your fresh-window look, then sign-off", c: AMBER },
];
const sx = 0.5, sy = 1.7, sw = 3.55, sh = 1.95, gap = 0.32;
stats.forEach((it, i) => {
  const x = sx + (i % 2) * (sw + gap), y = sy + Math.floor(i / 2) * (sh + gap);
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: sw, h: sh, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 }, shadow: shadow() });
  s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.1, h: sh, fill: { color: it.c } });
  s.addText(it.n, { x: x + 0.25, y: y + 0.14, w: sw - 0.5, h: 0.82, fontFace: HF, fontSize: 42, bold: true, color: it.c, margin: 0, align: "left" });
  s.addText(it.t, { x: x + 0.27, y: y + 0.98, w: sw - 0.5, h: 0.45, fontFace: BF, fontSize: 13, bold: true, color: INK, margin: 0 });
  s.addText(it.d, { x: x + 0.27, y: y + 1.42, w: sw - 0.45, h: 0.5, fontFace: BF, fontSize: 10.5, color: MUTED, margin: 0 });
});
s.addShape(pres.shapes.RECTANGLE, { x: 8.35, y: 1.7, w: 4.5, h: 4.22, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText("The short version", { x: 8.55, y: 1.85, w: 4.1, h: 0.35, fontFace: BF, fontSize: 13, bold: true, color: TERRA, margin: 0 });
s.addText([
  { text: "Four of the five are quick UI tweaks — done and checked on the preview.", options: { color: MUTED, breakLine: true } },
  { text: "\nThe fifth, the mobile banner, has been the tricky one across three rounds. It turns out the fix was already correct and deployed — the store pages were just serving an older cached copy. We've confirmed the fix is now in the live page and reinforced it. Slide 4 explains how to see it.", options: { color: MUTED } },
], { x: 8.55, y: 2.25, w: 4.1, h: 3.5, fontFace: BF, fontSize: 11, valign: "top", margin: 0, lineSpacingMultiple: 1.1 });
footer(s, 2);

// ============ SLIDE 3 — THE 5 COMMENTS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Your comments", "All five, point by point");
const rows = [
  [hcell("You asked"), hcell("Status"), hcell("What it does now")],
  [tc("Cart drawer: don't recommend items already in the cart"),
   pill("FIXED", GREEN),
   tc("Suggestions now skip anything in the cart. Verified: adding a product makes it disappear from the suggestions immediately.")],
  [tc("Cart page: don't recommend items already in the cart"),
   pill("FIXED", GREEN),
   tc("Same fix applies to the cart-page suggestions.")],
  [tc("PDP mobile sticky bar: add a right margin to the ADD TO CART button"),
   pill("FIXED", GREEN),
   tc("The button now has breathing room on the right instead of touching the screen edge.")],
  [tc("Quick Buy icon: the cart symbol is faded and too small — darken & enlarge"),
   pill("FIXED", GREEN),
   tc("Redrawn bolder and larger (and again on the smaller drawer cards), keeping the light-grey circle you specified.")],
  [tc("Mobile banner margins — still showing on Pipeline 8 and the live theme"),
   pill("LIVE — see slide 4", TERRA),
   tc("The fix is correct and now confirmed in the live page. The earlier screenshots were a cached view — details next slide.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.65, w: 12.33, colW: [4.5, 1.9, 5.93],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 0.92, 0.6, 0.85, 0.95, 0.95], margin: [3, 5, 3, 5],
});
footer(s, 3);

// ============ SLIDE 4 — THE BANNER, EXPLAINED ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "The mobile banner", "Why it kept looking unfixed — and how to see it");

// left: what happened
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 6.05, h: 4.0, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addText("What was actually going on", { x: 0.72, y: 1.85, w: 5.6, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText([
  { text: "The full-bleed fix was already correct and deployed — to the preview and the live theme.", options: { color: "30373E", breakLine: true, bold: true } },
  { text: "\nStore pages are cached for speed. After we pushed the fix, the homepage kept serving its previously-saved copy for a while, so the banner still looked gapped — to us and to you — even though the underlying file was already fixed.", options: { color: MUTED, breakLine: true } },
  { text: "\nWe've now confirmed the fix is present in the live page itself (not just the file), and added an extra safeguard so the banner fills the screen edge-to-edge on mobile no matter what.", options: { color: MUTED } },
], { x: 0.72, y: 2.25, w: 5.6, h: 3.3, fontFace: BF, fontSize: 11.5, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });

// right: how to verify
s.addShape(pres.shapes.RECTANGLE, { x: 6.8, y: 1.7, w: 6.03, h: 4.0, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText("How to see the fixed banner", { x: 7.02, y: 1.85, w: 5.6, h: 0.35, fontFace: BF, fontSize: 14, bold: true, color: TERRA, margin: 0 });
s.addText([
  { text: "1.  Open a brand-new browser window (or Incognito/Private) — don't reuse the tab from last week.", options: { color: "30373E", breakLine: true } },
  { text: "\n2.  On your phone, hard-refresh (pull down to reload).", options: { color: "30373E", breakLine: true } },
  { text: "\n3.  If you opened it right after a change, give it ~30 minutes for the page cache to refresh, then reload.", options: { color: "30373E", breakLine: true } },
  { text: "\nStill see side-gaps after a genuinely fresh load?  Then the banner image file itself has white space built into it — we'd just need the artwork re-exported edge-to-edge (a quick design fix). Let us know and we'll flag it.", options: { color: MUTED } },
], { x: 7.02, y: 2.25, w: 5.6, h: 3.3, fontFace: BF, fontSize: 11.5, valign: "top", margin: 0, lineSpacingMultiple: 1.12 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.95, w: 12.33, h: 0.95, fill: { color: INK } });
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.95, w: 0.1, h: 0.95, fill: { color: TERRA } });
s.addText([
  { text: "Note:  ", options: { bold: true, color: TERRA } },
  { text: "this same caching is why a few earlier items looked \"not addressed\" when they were already fixed. A fresh window is the reliable way to review — it's worth generating a new preview link each time before checking.", options: { color: ICE } },
], { x: 0.8, y: 6.0, w: 11.8, h: 0.85, fontFace: BF, fontSize: 12, valign: "middle", margin: 0 });
footer(s, 4);

// ============ SLIDE 5 — NEXT STEPS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Over to you", "One fresh look, then we go live");

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.7, w: 12.33, h: 2.0, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 2.3, w: 0.55, h: 0.55, fill: { color: TERRA } });
s.addText("1", { x: 0.72, y: 2.3, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Final review — fresh window, hard refresh", { x: 1.5, y: 1.85, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText("Check on the preview, and the banner on the live site too:", { x: 1.5, y: 2.21, w: 11.1, h: 0.3, fontFace: BF, fontSize: 11, color: MUTED, margin: 0 });
s.addText([
  { text: "Product", options: { hyperlink: { url: L("/products/davines-purifying-shampoo-for-oily-or-dry-dandruff-100ml") }, color: TERRA, bold: true } },
  { text: " (sticky bar margin)      ", options: { color: MUTED } },
  { text: "Cart", options: { hyperlink: { url: L("/cart") }, color: TERRA, bold: true } },
  { text: " (suggestions skip cart items, bigger Quick Buy icon)      ", options: { color: MUTED } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: TERRA, bold: true } },
  { text: " (Quick Buy icon)", options: { color: MUTED } },
], { x: 1.5, y: 2.58, w: 11.1, h: 0.55, fontFace: BF, fontSize: 11, valign: "top", margin: 0 });
s.addText("Phone: sticky-bar button margin · Quick Buy icon size · banner edges (preview AND the live homepage).", { x: 1.5, y: 3.2, w: 11.1, h: 0.32, fontFace: BF, fontSize: 11, italic: true, color: MUTED, margin: 0 });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 3.95, w: 12.33, h: 1.35, fill: { color: LIGHT }, line: { color: "E4E7EB", width: 1 } });
s.addShape(pres.shapes.OVAL, { x: 0.72, y: 4.32, w: 0.55, h: 0.55, fill: { color: GREEN } });
s.addText("2", { x: 0.72, y: 4.32, w: 0.55, h: 0.55, fontFace: HF, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
s.addText("Sign off → switch-over", { x: 1.5, y: 4.12, w: 11.1, h: 0.38, fontFace: BF, fontSize: 14, bold: true, color: INK, margin: 0 });
s.addText("We publish the new theme, turn off the old sticky-cart app (the doubled-up icons disappear, Recently Viewed gets its Quick Buy), and cancel the $24.99/month subscription (≈ ₱17k/year back).", { x: 1.5, y: 4.48, w: 11.3, h: 0.7, fontFace: BF, fontSize: 11, color: MUTED, margin: 0, valign: "top" });

s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.65, w: 12.33, h: 0.95, fill: { color: "FBF3F1" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "While you review:  ", options: { bold: true, color: TERRA } },
  { text: "the old app is still installed on the preview, so you'll see two of some buttons until switch-over. Expected — not a bug.", options: { color: MUTED } },
], { x: 0.7, y: 5.72, w: 12.0, h: 0.8, fontFace: BF, fontSize: 11, valign: "middle", margin: 0 });
footer(s, 5);

// ============ SLIDE 6 — CLOSING ============
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("BOTTOM LINE", { x: 0.9, y: 1.7, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("All five in. The banner mystery solved.", { x: 0.9, y: 2.2, w: 11.7, h: 1.5, fontFace: HF, fontSize: 36, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "The four UI tweaks are done and checked; recommendations now skip cart items; and the mobile banner was correct all along — the gap was a cached page, now confirmed fixed in the live store and reinforced. ", options: { color: ICE } },
  { text: "Open a fresh window for the final look, and we're clear to switch over.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 3.7, w: 11.2, h: 1.5, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
s.addText([
  { text: "Open the preview store:  ", options: { color: GRAY } },
  { text: "click here", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "      ·      Questions? Reply on the project thread.", options: { color: GRAY } },
], { x: 0.9, y: 6.5, w: 11.5, h: 0.3, fontFace: BF, fontSize: 12, margin: 0 });

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Preview-Review.pptx" }).then(f => console.log("WROTE", f));
