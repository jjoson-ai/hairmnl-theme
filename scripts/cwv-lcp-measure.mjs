// lcp1 — LCP / FCP / CLS harness, companion to cwv-cls-measure.mjs (cls8).
//
// WHY THIS EXISTS (bd hairmnl-theme-m8ne, 2026-08-16)
// cls8 reports CLS only. Judging the Searchanise async change needs all three at
// once, because the whole risk of that change is trading LCP against FCP: making
// a script non-deferred can pull LCP in while pushing FCP out. Measuring one
// metric would hide exactly the failure mode we care about.
//
// Inherits cls8's three hard-won rules:
//   1. chrome-headless-shell, NOT "Chrome for Testing" — the app binary
//      fabricates zeros on this machine.
//   2. MANDATORY PRE-FLIGHT against a locally served page whose LCP and FCP are
//      analytically known. Aborts rather than report from a broken instrument.
//   3. Realistic mobile throttling (1.6Mbps / 150ms RTT / 4x CPU).
//
// Usage: node cwv-lcp-measure.mjs <url> <basePort> <runs> [mobile|desktop]
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';

const SHELL = '/Users/y9378348c/.cache/puppeteer/chrome-headless-shell/mac_arm-147.0.7727.57/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const URL_ = process.argv[2];
const BASE = Number(process.argv[3] || 9900);
const RUNS = Number(process.argv[4] || 5);
const PROF = process.argv[5] || 'mobile';
// Optional CSS selector to suppress before load. Used to isolate a metric from a
// confounding element — e.g. the Shopify consent banner, which is the LCP element
// on a FRESH profile but absent for the returning/consented users that make up
// most field traffic. Suppressing it answers "what is LCP for everyone else".
const SUPPRESS = process.argv[6] || '';

const P = PROF === 'mobile'
  ? { w: 390, h: 844, dpr: 3, mob: true, down: 1.6 * 1024 * 1024 / 8, up: 750 * 1024 / 8, lat: 150, cpu: 4 }
  : { w: 1440, h: 900, dpr: 1, mob: false, down: 10 * 1024 * 1024 / 8, up: 3 * 1024 * 1024 / 8, lat: 40, cpu: 1 };

const sleep = ms => new Promise(r => setTimeout(r, ms));
const withTimeout = (pr, ms, tag) => Promise.race([pr, new Promise((_, j) => setTimeout(() => j(new Error('timeout:' + tag)), ms))]);

const OBS = `
window.__lcp=0; window.__lcpEl=''; window.__fcp=0; window.__cls=0;
function pathOf(el){const o=[];while(el&&el.nodeType===1&&o.length<5){let s=el.tagName.toLowerCase();
  if(el.id)s+='#'+el.id; else if(typeof el.className==='string'&&el.className.trim())s+='.'+el.className.trim().split(/\\s+/).slice(0,2).join('.');
  o.unshift(s);el=el.parentElement;}return o.join('>');}
try{
new PerformanceObserver(l=>{for(const e of l.getEntries()){
  window.__lcp=Math.round(e.startTime);
  window.__lcpEl=e.element?pathOf(e.element):(e.url||'(no element)');
}}).observe({type:'largest-contentful-paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){
  if(e.name==='first-contentful-paint') window.__fcp=Math.round(e.startTime);
}}).observe({type:'paint',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries()){
  if(!e.hadRecentInput) window.__cls+=e.value;
}}).observe({type:'layout-shift',buffered:true});
}catch(err){window.__e=String(err);}
window.__raf=0;(function t(){window.__raf++;requestAnimationFrame(t);})();`;

async function connect(port, bin) {
  const proc = spawn(bin, ['--headless=new', `--remote-debugging-port=${port}`, '--no-first-run',
    `--user-data-dir=/tmp/lcp1_${port}`, '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  let spawnErr = null; proc.on('error', e => { spawnErr = e; });
  let u = null;
  for (let k = 0; k < 40 && !u; k++) {
    if (spawnErr) throw new Error('spawn: ' + spawnErr.message);
    if (proc.exitCode !== null) throw new Error('chrome exited code=' + proc.exitCode);
    try { const t = (await (await fetch(`http://127.0.0.1:${port}/json/list`)).json()).find(x => x.type === 'page'); u = t?.webSocketDebuggerUrl || null; } catch {}
    if (!u) await sleep(250);
  }
  if (!u) throw new Error('no cdp endpoint');
  const ws = new WebSocket(u);
  await withTimeout(new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error('ws error')); ws.onclose = () => j(new Error('ws closed')); }), 15000, 'ws-open');
  let id = 0; const pend = new Map();
  ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const send = (m, q = {}) => withTimeout(new Promise(r => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method: m, params: q })); }), 30000, m);
  const ev = async x => (await send('Runtime.evaluate', { expression: x, awaitPromise: true, returnByValue: true }))?.result?.result?.value;
  return { proc, ws, send, ev, close() { try { ws.close(); } catch {} try { proc.kill('SIGKILL'); } catch {} } };
}

// Pre-flight: a block painted immediately (FCP) and a larger one at ~1000ms that
// must win LCP. If the instrument cannot see a deliberately delayed LCP, nothing
// it reports about a real page is trustworthy.
// #b is an SVG data-URI with a real intrinsic size (380x600), NOT a bare div.
// First attempt used a coloured div: LCP scores a text block by the area of its
// TEXT, not its box, so a one-word div never beat the first paint and the
// pre-flight correctly refused to run. An image with intrinsic dimensions is an
// unambiguous LCP candidate.
// HIGH-ENTROPY on purpose. Chrome excludes low-entropy images from LCP
// candidacy (< ~0.05 bits/pixel) so that solid-colour placeholders cannot win
// the metric. The first two probe attempts used a flat-filled rect and produced
// NO LCP entry at all despite the image loading, painting at 380x600, and the
// page being visible — the pre-flight caught it and refused to run, which is
// exactly its job. 380x600 = 228,000px needs >~1.4KB of image data to qualify;
// the noise below is ~15KB.
const BIG_SVG = (() => {
  let r = 'ABCDEF0123456789', s = '';
  let seed = 12345;
  const rnd = () => (seed = (seed * 1103515245 + 12345) & 0x7fffffff) / 0x7fffffff;
  for (let i = 0; i < 900; i++) {
    const x = Math.floor(rnd() * 380), y = Math.floor(rnd() * 600);
    const w = 4 + Math.floor(rnd() * 26), h = 4 + Math.floor(rnd() * 26);
    let c = '#'; for (let k = 0; k < 6; k++) c += r[Math.floor(rnd() * 16)];
    s += `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${c}"/>`;
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" width="380" height="600"><rect width="380" height="600" fill="#204030"/>${s}</svg>`;
})();
const PROBE = `<!doctype html><html><head><style>body{margin:0}#a{height:120px;background:#ddd;font:20px sans-serif}#b{display:none}</style></head>
<body><div id="a">first paint block</div><img id="b" src="/big.svg" width="380" height="600" alt="">
<script>setTimeout(function(){document.getElementById('b').style.display='block'},1000)</script></body></html>`;
async function preflight(port) {
  // Serve the probe image as a real resource. A data: URI was tried first and the
  // pre-flight kept failing — attribute-level escaping made the SVG unreliable.
  // A real request removes that variable entirely.
  const srv = createServer((req, res) => {
    if (req.url && req.url.startsWith('/big.svg')) {
      res.writeHead(200, { 'Content-Type': 'image/svg+xml' }); res.end(BIG_SVG); return;
    }
    res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(PROBE);
  });
  const httpPort = port + 500;
  await new Promise(r => srv.listen(httpPort, '127.0.0.1', r));
  const c = await connect(port, SHELL);
  try {
    await c.send('Page.enable'); await c.send('Runtime.enable');
    await c.send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 800, deviceScaleFactor: 1, mobile: false });
    await c.send('Page.addScriptToEvaluateOnNewDocument', { source: OBS });
    await c.send('Page.navigate', { url: `http://127.0.0.1:${httpPort}/` });
    for (let k = 0; k < 40; k++) { if (await c.ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(250); }
    await sleep(2500);
    const lcp = await c.ev('window.__lcp'), fcp = await c.ev('window.__fcp'), raf = await c.ev('window.__raf'), el = await c.ev('window.__lcpEl');
    // #b appears at ~1000ms and is far larger than #a, so it must become LCP.
    const ok = typeof lcp === 'number' && lcp >= 900 && lcp < 2500 && typeof fcp === 'number' && fcp > 0 && fcp < lcp && raf > 20 && String(el).includes('#b');
    return { ok, lcp, fcp, el, raf };
  } finally { c.close(); srv.close(); }
}

async function once(i) {
  const c = await connect(BASE + i, SHELL);
  try {
    await c.send('Page.enable'); await c.send('Runtime.enable'); await c.send('Network.enable');
    await c.send('Emulation.setDeviceMetricsOverride', { width: P.w, height: P.h, deviceScaleFactor: P.dpr, mobile: P.mob });
    await c.send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: P.down, uploadThroughput: P.up, latency: P.lat });
    if (P.cpu > 1) await c.send('Emulation.setCPUThrottlingRate', { rate: P.cpu });
    await c.send('Page.addScriptToEvaluateOnNewDocument', { source: OBS });
    if (SUPPRESS) {
      await c.send('Page.addScriptToEvaluateOnNewDocument', { source:
        `(function(){var s=document.createElement('style');s.textContent=${JSON.stringify(SUPPRESS + '{display:none !important}')};` +
        `(document.head||document.documentElement).appendChild(s);})();` });
    }
    await c.send('Page.navigate', { url: URL_ });
    for (let k = 0; k < 150; k++) { if (await c.ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(400); }
    // Hold without scrolling: LCP is an above-fold, pre-interaction metric, and
    // scrolling can only end the LCP candidacy window early.
    await sleep(8000);
    const raw = await c.ev(`JSON.stringify({lcp:window.__lcp,fcp:window.__fcp,cls:+window.__cls.toFixed(4),el:window.__lcpEl,raf:window.__raf,err:window.__e||null,
      results:document.querySelectorAll('.snize-item, [class*="snize-product"]').length})`);
    return JSON.parse(raw);
  } finally { c.close(); }
}

const med = a => { const v = [...a].sort((x, y) => x - y); return v.length ? v[Math.floor(v.length / 2)] : null; };

async function main() {
  console.log(`\nlcp1 — ${PROF} / n=${RUNS}${SUPPRESS ? ' / suppressing ' + SUPPRESS : ''}\n${URL_}`);
  const pf = await preflight(BASE + 400);
  console.log(`  PRE-FLIGHT: lcp=${pf.lcp}ms (expect ~1000-1500) fcp=${pf.fcp}ms el=${pf.el} raf=${pf.raf} -> ${pf.ok ? 'INSTRUMENT OK' : 'INSTRUMENT BROKEN'}`);
  if (!pf.ok) { console.log('  ABORTING — refusing to report numbers from an unvalidated instrument.'); process.exit(2); }

  const runs = [];
  for (let i = 0; i < RUNS; i++) {
    try { runs.push(await withTimeout(once(i), 240000, 'run' + i)); }
    catch (e) { runs.push({ error: String(e.message || e).slice(0, 110) }); }
    await sleep(1200);
  }
  const ok = runs.filter(r => typeof r.lcp === 'number' && r.lcp > 0);
  if (!ok.length) { console.log('  ALL RUNS FAILED'); runs.forEach((r, i) => console.log(`   run${i}: ${r.error || JSON.stringify(r)}`)); process.exit(3); }
  console.log(`  ok ${ok.length}/${RUNS}`);
  console.log(`  LCP  median ${med(ok.map(r => r.lcp))}ms   runs: ${ok.map(r => r.lcp).join(', ')}`);
  console.log(`  FCP  median ${med(ok.map(r => r.fcp))}ms   runs: ${ok.map(r => r.fcp).join(', ')}`);
  console.log(`  CLS  median ${med(ok.map(r => r.cls))}      runs: ${ok.map(r => r.cls).join(', ')}`);
  console.log(`  search results rendered (median): ${med(ok.map(r => r.results))}`);
  const els = {}; ok.forEach(r => { els[r.el] = (els[r.el] || 0) + 1; });
  console.log('  LCP element:');
  Object.entries(els).sort((a, b) => b[1] - a[1]).forEach(([k, v]) => console.log(`     ${v}x  ${k}`));
  console.log('DONE-LCP1');
}
main().catch(e => { console.error('FATAL', e); process.exit(1); });
