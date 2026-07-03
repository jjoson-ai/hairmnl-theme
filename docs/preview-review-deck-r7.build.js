const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Round 7 Fix Review";

// ---- palette (house style, matches R5/R6) ----
const INK = "1F2933", TERRA = "B85042", WHITE = "FFFFFF", MUTED = "5A6470",
      ICE = "CAD3DC", GREEN = "2E7D5B", GRAY = "8A8F98";
const HF = "Georgia", BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com";
const NF = "?preview_theme_id=141168312419&_fd=0&_sc=1";
const L = (path) => STORE + path + NF;
const PDP = "/products/kerastase-genesis-anti-hair-fall-fortifying-conditioner-200ml";

function footer(slide, n) {
  slide.addText("HairMNL · Pipeline 8 — round 7 (fixes for the 25 Jun notes)", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, align: "left", margin: 0 });
  slide.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(slide, label, title) {
  slide.addText(label.toUpperCase(), { x: 0.5, y: 0.38, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  slide.addText(title, { x: 0.5, y: 0.70, w: 12.3, h: 0.7, fontFace: HF, fontSize: 28, bold: true, color: INK, margin: 0 });
}
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle", align: "left" } });
const tc = (t, opts = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: WHITE }, ...opts } });
const wasCell = (t) => ({ text: t, options: { fontSize: 10, fontFace: BF, italic: true, color: TERRA, valign: "middle", fill: { color: "FBF3F1" } } });

// ============ SLIDE 1 — TITLE ============
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · ROUND 7", { x: 0.9, y: 0.9, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Everything from the June 25 notes is fixed", { x: 0.9, y: 1.4, w: 11.8, h: 1.0, fontFace: HF, fontSize: 36, bold: true, color: WHITE, margin: 0 });
s.addText("Covers the iOS deck comments AND the Android list: the variant picker behaviour, the badges on the recommendation sliders, and the cart-page items. Each one has been re-tested on the preview before this deck — the pages below show exactly what you should now see.",
  { x: 0.9, y: 2.55, w: 11.4, h: 1.05, fontFace: BF, fontSize: 15, color: ICE, margin: 0, lineSpacingMultiple: 1.12 });
s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 3.85, w: 11.5, h: 1.5, fill: { color: "3A2E2C" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "📱 Open each link directly ", options: { bold: true, color: WHITE } },
  { text: "(tap it / paste it fresh — clicking through pages bounces you to the live site).\n", options: { color: ICE } },
  { text: "🛒 Cart page is special: ", options: { bold: true, color: WHITE } },
  { text: "the link trick doesn't hold there — it always jumps to the live site. To review the CART PAGE, use the theme's \"Share preview\" link from Shopify admin (the shopifypreview.com one).", options: { color: ICE } },
], { x: 1.15, y: 3.98, w: 11.0, h: 1.25, fontFace: BF, fontSize: 13, valign: "middle", margin: 0, lineSpacingMultiple: 1.15 });
s.addText("The pages:", { x: 0.9, y: 5.6, w: 11, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: GRAY, margin: 0 });
s.addText([
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Product page (Genesis Conditioner)", options: { hyperlink: { url: L(PDP) }, color: WHITE, bold: true } },
], { x: 0.9, y: 5.95, w: 11.6, h: 0.5, fontFace: BF, fontSize: 14, margin: 0 });

// ============ SLIDE 2 — VARIANT PICKER ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Variant picker (Quick Buy)", "It now behaves exactly as you specified:");
let rows = [
  [hcell("What to check"), hcell("What you should see now"), hcell("⚠ Was buggy before")],
  [tc("Stays on its product card", { bold: true }),
   tc("Open the picker, then scroll — it moves WITH the card (scrolls off-screen with it, comes back with it). No more floating box chasing you down the page."),
   wasCell("Floated in place over other products while scrolling.")],
  [tc("Stays open", { bold: true }),
   tc("Scroll away and back — it's still open when you return to the card. It only closes when you tap somewhere else, switch pages, or add to cart."),
   wasCell("Disappeared on its own while scrolling (iOS + Android).")],
  [tc("Sits behind the bars", { bold: true }),
   tc("Scroll so the card passes under the header / search / filter bar — the picker slides UNDER them (and under any pop-up banner), never on top."),
   wasCell("Covered the header and pop-ups.")],
  [tc("Long variant names", { bold: true }),
   tc("Box is the same width as the product card; long names (e.g. \"FREE Absolut Repair Molecular Masque 75ml | 30ml\") wrap onto multiple lines with the price intact on the right — never cut, never covering the price."),
   wasCell("Names cut off / ran over the price.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.55, w: 12.33, colW: [2.9, 6.0, 3.43],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.05, 1.0, 1.0, 1.15], margin: [4, 6, 4, 6],
});
s.addText([
  { text: "Try it: ", options: { color: MUTED } },
  { text: "Home → Best Sellers", options: { hyperlink: { url: L("/") }, color: TERRA, bold: true } },
  { text: "  (the L'Oréal Serioxyl card has the long free-gift names)   ·   ", options: { color: MUTED } },
  { text: "Product page → Complete Your Routine", options: { hyperlink: { url: L(PDP) }, color: TERRA, bold: true } },
], { x: 0.5, y: 6.6, w: 12.3, h: 0.35, fontFace: BF, fontSize: 12, margin: 0 });
footer(s, 2);

// ============ SLIDE 3 — BADGES + SLIDERS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Recommendation sliders", "Badges & alignment — now consistent everywhere:");
rows = [
  [hcell("What to check"), hcell("What you should see now"), hcell("⚠ Was buggy before")],
  [tc("Badges on the Vertex sliders", { bold: true }),
   tc("\"Complete Your Routine\" (product page) and \"Complete Your Cart / Order\" (cart drawer + cart page): the badge is the same grey pill overlay as everywhere else — FREE GIFTS in caps, top-left, on the image."),
   wasCell("Plain lowercase \"free gifts\" text pushing the card content down. (Badge styling wasn't loading on product & cart pages — now it loads on every page.)")],
  [tc("Slider card alignment", { bold: true }),
   tc("All sliders (home, product page, Recently Viewed, cart): uniform image boxes, products shown in full (no zoom/crop), full titles, prices lined up."),
   wasCell("Zoomed/cropped images, cards at different heights.")],
];
s.addTable(rows, {
  x: 0.5, y: 1.55, w: 12.33, colW: [2.9, 5.6, 3.83],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 1.35, 1.05], margin: [4, 6, 4, 6],
});
s.addText([
  { text: "Best spot to check: ", options: { color: MUTED } },
  { text: "the Genesis Conditioner product page", options: { hyperlink: { url: L(PDP) }, color: TERRA, bold: true } },
  { text: " — its \"Complete Your Routine\" row has the exact card from your screenshot (Genesis 500ml, FREE GIFTS pill).", options: { color: MUTED } },
], { x: 0.5, y: 4.55, w: 12.3, h: 0.55, fontFace: BF, fontSize: 12, margin: 0, lineSpacingMultiple: 1.1 });
footer(s, 3);

// ============ SLIDE 4 — CART PAGE CLARIFICATION ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Cart page — please re-check with the right link", "What you screenshotted was the LIVE site, not Pipeline 8");
s.addText([
  { text: "The preview link silently jumps to hairmnl.com on the cart page ", options: { bold: true, color: INK } },
  { text: "— so the cart-page notes (missing \"Complete Your Cart\" slider, the BUY IT WITH box, the odd trash-bin placement) were all screenshots of the current live site. They're already correct on Pipeline 8:", options: { color: "30373E" } },
], { x: 0.5, y: 1.6, w: 12.3, h: 0.85, fontFace: BF, fontSize: 14, margin: 0, lineSpacingMultiple: 1.15 });
rows = [
  [hcell("On the Pipeline 8 cart page"), hcell("Status")],
  [tc("\"Complete Your Order\" recommendation slider sits after your items, BEFORE the order summary", { bold: true }), tc("✓ already built in", { color: GREEN, bold: true })],
  [tc("No Shopify \"BUY IT WITH\" box", { bold: true }), tc("✓ it doesn't exist on P8", { color: GREEN, bold: true })],
  [tc("Trash-bin icon pinned neatly top-right of each item (mobile) — same as the cart drawer", { bold: true }), tc("✓ already matches the drawer", { color: GREEN, bold: true })],
];
s.addTable(rows, {
  x: 0.5, y: 2.65, w: 12.33, colW: [9.3, 3.03],
  border: { type: "solid", pt: 0.5, color: "D7DBE0" }, align: "left", valign: "middle",
  autoPage: false, rowH: [0.3, 0.7, 0.55, 0.7], margin: [4, 6, 4, 6],
});
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.35, w: 12.33, h: 0.95, fill: { color: "F3F4F6" }, line: { color: "D7DBE0", width: 0.75 } });
s.addText([
  { text: "How to see the P8 cart page: ", options: { bold: true, color: INK } },
  { text: "Shopify admin → Online Store → Themes → \"Pipeline 8 Working Demo\" → Preview / Share preview, then add an item and open /cart from inside that preview session (the shopifypreview.com address stays on P8).", options: { color: "30373E" } },
], { x: 0.75, y: 5.45, w: 11.9, h: 0.78, fontFace: BF, fontSize: 12.5, valign: "middle", margin: 0, lineSpacingMultiple: 1.12 });
footer(s, 4);

// ============ SLIDE 5 — CLOSING ============
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("THAT'S ROUND 7", { x: 0.9, y: 1.9, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Give these a pass on your phones — if they hold, we're go for launch.", { x: 0.9, y: 2.4, w: 11.7, h: 1.6, fontFace: HF, fontSize: 32, bold: true, color: WHITE, margin: 0, lineSpacingMultiple: 1.05 });
s.addText([
  { text: "The picker + badge fixes shipped AFTER your last videos were recorded, so a fresh capture on iOS/Android would be the clean confirmation. ", options: { color: ICE } },
  { text: "Anything still off: screenshot + page + device, and we'll turn it around same-day.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 4.2, w: 11.3, h: 1.2, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
s.addText([
  { text: "Pages:  ", options: { color: GRAY } },
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "  ·  ", options: { color: GRAY } },
  { text: "Product page", options: { hyperlink: { url: L(PDP) }, color: WHITE, bold: true } },
  { text: "  ·  Cart page via admin Share preview", options: { color: GRAY } },
], { x: 0.9, y: 6.35, w: 11.9, h: 0.35, fontFace: BF, fontSize: 12, margin: 0 });

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Round7-Fix-Review.pptx" }).then(f => console.log("WROTE", f));
