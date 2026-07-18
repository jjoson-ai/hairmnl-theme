const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
pres.author = "HairMNL";
pres.title = "Pipeline 8 — Pre-Launch Checklist";

// ---- palette (house style) ----
const INK = "1F2933", TERRA = "B85042", WHITE = "FFFFFF", MUTED = "5A6470",
      ICE = "CAD3DC", GREEN = "2E7D5B", GRAY = "8A8F98";
const HF = "Georgia", BF = "Calibri";
const STORE = "https://creations-gdc.myshopify.com";
const NF = "?preview_theme_id=141168312419&_fd=0&_sc=1";
const L = (p) => STORE + p + NF;
const PDP = "/products/kerastase-genesis-anti-hair-fall-fortifying-conditioner-200ml";

function footer(s, n) {
  s.addText("HairMNL · Pipeline 8 — pre-launch checklist (17 Jul)", { x: 0.5, y: 7.12, w: 10.5, h: 0.3, fontFace: BF, fontSize: 9, color: MUTED, margin: 0 });
  s.addText(String(n), { x: 12.4, y: 7.12, w: 0.5, h: 0.3, fontFace: BF, fontSize: 9, color: GRAY, align: "right", margin: 0 });
}
function header(s, label, title) {
  s.addText(label.toUpperCase(), { x: 0.5, y: 0.35, w: 12.3, h: 0.3, fontFace: BF, fontSize: 12, bold: true, color: TERRA, charSpacing: 3, margin: 0 });
  s.addText(title, { x: 0.5, y: 0.66, w: 12.3, h: 0.62, fontFace: HF, fontSize: 26, bold: true, color: INK, margin: 0 });
}
const hcell = (t) => ({ text: t, options: { fill: { color: INK }, color: WHITE, bold: true, fontSize: 11, fontFace: BF, valign: "middle" } });
const tc = (t, o = {}) => ({ text: t, options: { fontSize: 10.5, fontFace: BF, color: "30373E", valign: "middle", fill: { color: WHITE }, ...o } });
const box = (t, o = {}) => ({ text: "☐  " + t, options: { fontSize: 11, fontFace: BF, color: "30373E", valign: "middle", fill: { color: WHITE }, bold: true, ...o } });

// ============ 1 — TITLE ============
let s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("PIPELINE 8 · PRE-LAUNCH", { x: 0.9, y: 1.0, w: 11, h: 0.4, fontFace: BF, fontSize: 15, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("The launch checklist", { x: 0.9, y: 1.5, w: 11.8, h: 0.95, fontFace: HF, fontSize: 40, bold: true, color: WHITE, margin: 0 });
s.addText([
  { text: "Everything from every review round is fixed and verified — including the July 17 mobile badge note. ", options: { color: ICE } },
  { text: "The full code audit passed, and the launch theme now carries every fix plus the FAQ & special product pages. ", options: { color: ICE } },
  { text: "What's left fits on three slides: your final phone pass, a few admin steps, and the launch-day sequence.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 2.7, w: 11.4, h: 1.3, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.18 });
s.addShape(pres.shapes.RECTANGLE, { x: 0.9, y: 4.35, w: 11.5, h: 1.0, fill: { color: "3A2E2C" }, line: { color: TERRA, width: 1 } });
s.addText([
  { text: "Reminder: ", options: { bold: true, color: WHITE } },
  { text: "open the links below directly (tapping through pages can bounce you to the live site). The CART PAGE only stays on Pipeline 8 via the admin \"Share preview\" link.", options: { color: ICE } },
], { x: 1.15, y: 4.45, w: 11.0, h: 0.8, fontFace: BF, fontSize: 13, valign: "middle", margin: 0, lineSpacingMultiple: 1.15 });
s.addText([
  { text: "Home", options: { hyperlink: { url: L("/") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Collection", options: { hyperlink: { url: L("/collections/all") }, color: WHITE, bold: true } },
  { text: "   ·   ", options: { color: GRAY } },
  { text: "Product page", options: { hyperlink: { url: L(PDP) }, color: WHITE, bold: true } },
  { text: "   ·   Cart page via admin Share preview", options: { color: GRAY } },
], { x: 0.9, y: 5.75, w: 11.9, h: 0.4, fontFace: BF, fontSize: 13, margin: 0 });

// ============ 2 — WEB TEAM FINAL PASS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Step 1 · Web team", "Final phone pass — 8 checks");
let rows = [
  [hcell("Check"), hcell("What you should see")],
  [box("Mobile badges — all sliders"), tc("Badges are now the SAME size on every slider (your July 17 note is fixed): compare Recommended-for-You vs Best Sellers on a phone.")],
  [box("Variant picker"), tc("Opens over its card · scrolls with the card · stays open · closes on tap-away — and tapping the little cart icon again also closes it now.")],
  [box("Brand pages — mobile FILTERS button"), tc("On any brand page (Kérastase, Davines…) below tablet width, the FILTERS button now opens the sidebar. It was dead before — please try 2-3 brands.")],
  [box("Filter + Back button"), tc("Filter any collection, tap a product, press Back — the grid matches the filters shown in the URL (no mismatched products).")],
  [box("Quick-buy add to cart"), tc("Add from any slider: the cart drawer slides open WITH the item inside, and the header cart count updates. No error flashes.")],
  [box("Cart page (Share-preview link)"), tc("\"Complete Your Order\" slider before the totals · no BUY IT WITH box · trash icon top-right of each item on mobile.")],
  [box("FAQ + special product pages"), tc("Newly added to the launch theme: hero-product FAQ pages (K18, Genesis serum, Olaplex 3…) and Backbar/promo/reward product pages render correctly.")],
];
s.addTable(rows, { x: 0.5, y: 1.5, w: 12.33, colW: [3.7, 8.63], border: { type: "solid", pt: 0.5, color: "D7DBE0" }, autoPage: false,
  rowH: [0.3, 0.62, 0.62, 0.68, 0.6, 0.6, 0.6, 0.68], margin: [3, 6, 3, 6] });
s.addText("Anything off: screenshot + page + device → same-day turnaround.", { x: 0.5, y: 6.72, w: 12.3, h: 0.3, fontFace: BF, fontSize: 11.5, italic: true, color: MUTED, margin: 0 });
footer(s, 2);

// ============ 3 — ADMIN STEPS ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Step 2 · Admin (before launch day)", "Five small admin items");
rows = [
  [hcell("Task"), hcell("Where"), hcell("Notes")],
  [box("Add the Davines hero banner"), tc("Theme editor → Pipeline 8 Working Demo → /collections/davines"), tc("The branded \"Heart of Glass\" banner from the current site isn't configured on the new theme yet — content task, no code.")],
  [box("App-embeds side-by-side check"), tc("Theme editor → App embeds panel: current live theme vs Working Demo"), tc("10-minute insurance: every embed that's ON for live (Klaviyo, Judge.me, Reamaze, LoyaltyLion…) must be ON for the Demo, so nothing silently dies at launch.")],
  [box("Sign out other Shopify sessions"), tc("Admin → Settings → Users → your account"), tc("Security housekeeping from the audit — one stored login session should be rotated.")],
  [box("Back-in-Stock switchover decision"), tc("Appikon → Klaviyo-native"), tc("The Klaviyo replacement is built; confirm the subscriber-list import (or accept the gap) so Appikon can be uninstalled at launch. Can also follow a few days after.")],
  [box("Recommendation engine — Google Cloud sign-in"), tc("Terminal (1-minute browser sign-in when prompted)"), tc("Lets us deploy the updated recommendation filters and run a fresh build, so launch-day sliders carry only in-stock, non-freebie products from the very first visit.")],
];
s.addTable(rows, { x: 0.5, y: 1.5, w: 12.33, colW: [3.4, 4.2, 4.73], border: { type: "solid", pt: 0.5, color: "D7DBE0" }, autoPage: false,
  rowH: [0.3, 0.8, 0.9, 0.62, 0.9, 0.9], margin: [3, 6, 3, 6] });
footer(s, 3);

// ============ 4 — LAUNCH DAY ============
s = pres.addSlide();
s.background = { color: WHITE };
header(s, "Step 3 · Launch day", "The sequence — about an hour end to end");
rows = [
  [hcell("#"), hcell("Action"), hcell("Who")],
  [tc("1", { bold: true, align: "center" }), tc("Recommendation engine: deploy updated filters + fresh build, verify sliders carry clean products (launch-eve, backend)"), tc("Claude")],
  [tc("2", { bold: true, align: "center" }), tc("Final content sync — snapshot the Demo's latest settings/content into version control (one command)"), tc("Jonathan + Claude")],
  [tc("3", { bold: true, align: "center" }), tc("PUBLISH \"Pipeline 8 Working Demo\" (Admin → Themes → Publish)", { bold: true }), tc("Jonathan")],
  [tc("4", { bold: true, align: "center" }), tc("Theme editor → App embeds → toggle the STKY sticky-bar embed OFF"), tc("Jonathan")],
  [tc("5", { bold: true, align: "center" }), tc("Uninstall the STKY app + cancel its subscription (the theme's own sticky bar takes over)"), tc("Jonathan")],
  [tc("6", { bold: true, align: "center" }), tc("Uninstall LimeSpot (recommendations are fully in-house now — also removes ~25 stale requests per page)"), tc("Jonathan")],
  [tc("7", { bold: true, align: "center" }), tc("15-minute live smoke test: home · product page · collection · cart · quick-buy add (drawer opens WITH the item, count updates, no errors) · sticky buy bar on scroll · badges · recommendation sliders show in-stock products only · chat bubble · reach checkout", { bold: true }), tc("Everyone")],
];
s.addTable(rows, { x: 0.5, y: 1.5, w: 12.33, colW: [0.6, 9.6, 2.13], border: { type: "solid", pt: 0.5, color: "D7DBE0" }, autoPage: false,
  rowH: [0.28, 0.55, 0.5, 0.45, 0.45, 0.5, 0.55, 1.0], margin: [3, 6, 3, 6] });
s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 6.25, w: 12.33, h: 0.62, fill: { color: "EAF3EE" }, line: { color: GREEN, width: 0.75 } });
s.addText([
  { text: "Instant rollback, any time: ", options: { bold: true, color: GREEN } },
  { text: "the current live theme stays in the admin — publishing it back reverses the launch in one click. Nothing is destructive until the old apps are uninstalled (steps 5-6), and even those only affect their own widgets.", options: { color: "30373E" } },
], { x: 0.72, y: 6.3, w: 11.9, h: 0.52, fontFace: BF, fontSize: 11.5, valign: "middle", margin: 0 });
footer(s, 4);

// ============ 5 — CLOSE ============
s = pres.addSlide();
s.background = { color: INK };
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.28, h: 7.5, fill: { color: TERRA } });
s.addText("AFTER LAUNCH", { x: 0.9, y: 2.0, w: 11, h: 0.4, fontFace: BF, fontSize: 14, bold: true, color: TERRA, charSpacing: 4, margin: 0 });
s.addText("Phone pass ✓  +  admin items ✓  →  pick the day.", { x: 0.9, y: 2.5, w: 11.7, h: 1.5, fontFace: HF, fontSize: 32, bold: true, color: WHITE, margin: 0, lineSpacingMultiple: 1.05 });
s.addText([
  { text: "We keep watching speed and stability dashboards after launch, and the remaining polish items are already scheduled. ", options: { color: ICE } },
  { text: "Anything odd in the first days: screenshot + page + device — same-day fix.", options: { color: WHITE, bold: true } },
], { x: 0.9, y: 4.2, w: 11.3, h: 1.1, fontFace: BF, fontSize: 15, margin: 0, lineSpacingMultiple: 1.2 });
footer(s, 5);

pres.writeFile({ fileName: "/tmp/p8deck/Pipeline8-Pre-Launch-Checklist.pptx" }).then(f => console.log("WROTE", f));
