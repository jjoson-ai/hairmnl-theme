// cls8 — CANONICAL CLS harness (bd hairmnl-theme-pewh, 2026-08-13).
//
// Supersedes cls5/cls7. Three corrections, each from a real failure:
//
// 1. INSTRUMENT. Uses chrome-headless-shell, NOT the full "Chrome for Testing"
//    app. The app binary on this machine reports rafTicks=2, 0 paint entries,
//    0 layout-shift entries and CLS=0 on a page whose target provably moves
//    100px — it fabricates zeros, and in a partially-starved state inflates
//    per-frame deltas. It produced a "deterministic 0.1436" where this binary
//    measures 0.0296 on the same URL/profile.
//
// 2. MANDATORY PRE-FLIGHT. Before measuring anything, the harness measures a
//    locally-served page with an analytically known CLS and ABORTS unless the
//    reading matches. A silent instrument failure can no longer be mistaken for
//    "the page is fine" (or for a fix working).
//
// 3. REALISTIC SCROLL. cls7 jumped once to 45% of the page, so everything below
//    that never entered the viewport — lazy images, rec rails and late widgets
//    never got the chance to shift. Field CrUX for the sulfate article is
//    CLS p75 0.13 on phone while cls7 measured 0.003: the harness was not
//    reproducing real users. Default is now a GRADUAL full-page scroll
//    (0.8vh steps with settle time, then a pause at the bottom), which is what
//    a reader actually does to a listicle.
//
// Usage: node cls8.mjs <url> <basePort> <runs> [mobile|desktop] [deep|shallow|none]
import { spawn } from 'node:child_process';
import { createServer } from 'node:http';

const SHELL = '/Users/y9378348c/.cache/puppeteer/chrome-headless-shell/mac_arm-147.0.7727.57/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const URL_ = process.argv[2];
const BASE = Number(process.argv[3] || 9600);
const RUNS = Number(process.argv[4] || 6);
const PROF = process.argv[5] || 'mobile';
const SCROLL = process.argv[6] || 'deep';

const P = PROF === 'mobile'
  ? { w: 390, h: 844, dpr: 3, mob: true, down: 1.6 * 1024 * 1024 / 8, up: 750 * 1024 / 8, lat: 150, cpu: 4 }
  : { w: 1440, h: 900, dpr: 1, mob: false, down: 10 * 1024 * 1024 / 8, up: 3 * 1024 * 1024 / 8, lat: 40, cpu: 1 };

const sleep = ms => new Promise(r => setTimeout(r, ms));
const withTimeout = (pr, ms, tag) => Promise.race([pr, new Promise((_, j) => setTimeout(() => j(new Error('timeout:' + tag)), ms))]);

const OBS = `
window.__cls=0; window.__shifts=[];
function pathOf(el){const o=[];while(el&&el.nodeType===1&&o.length<5){let s=el.tagName.toLowerCase();
  if(el.id)s+='#'+el.id; else if(typeof el.className==='string'&&el.className.trim())s+='.'+el.className.trim().split(/\\s+/).slice(0,2).join('.');
  o.unshift(s);el=el.parentElement;}return o.join('>');}
try{
new PerformanceObserver(l=>{for(const e of l.getEntries()){
  if(e.hadRecentInput) continue;
  window.__cls+=e.value;
  window.__shifts.push({v:+e.value.toFixed(4),ms:Math.round(e.startTime),
    src:(e.sources||[]).slice(0,3).map(s=>({p:s.node?pathOf(s.node):'(detached)',
      pr:s.previousRect?[Math.round(s.previousRect.x),Math.round(s.previousRect.y),Math.round(s.previousRect.width),Math.round(s.previousRect.height)]:null,
      cr:s.currentRect?[Math.round(s.currentRect.x),Math.round(s.currentRect.y),Math.round(s.currentRect.width),Math.round(s.currentRect.height)]:null}))});
}}).observe({type:'layout-shift',buffered:true});
}catch(err){window.__e=String(err);}
window.__raf=0;(function t(){window.__raf++;requestAnimationFrame(t);})();`;

async function connect(port, bin) {
  const proc = spawn(bin, ['--headless=new', `--remote-debugging-port=${port}`, '--no-first-run',
    `--user-data-dir=/tmp/cls8_${port}`, '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
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

// ---- Pre-flight: a known shift, measured. Aborts the whole run if wrong. ----
const PROBE_PAGE = `<!doctype html><html><head><style>body{margin:0}#t{height:200px;background:#eee}#ins{height:100px;background:#f99;display:none}</style></head>
<body><div id="ins"></div><div id="t">x</div><script>setTimeout(function(){document.getElementById('ins').style.display='block'},1200)</script></body></html>`;
async function preflight(port) {
  const srv = createServer((_, res) => { res.writeHead(200, { 'Content-Type': 'text/html' }); res.end(PROBE_PAGE); });
  const httpPort = port + 500;
  await new Promise(r => srv.listen(httpPort, '127.0.0.1', r));
  const c = await connect(port, SHELL);
  try {
    await c.send('Page.enable'); await c.send('Runtime.enable');
    await c.send('Emulation.setDeviceMetricsOverride', { width: 1000, height: 800, deviceScaleFactor: 1, mobile: false });
    await c.send('Page.addScriptToEvaluateOnNewDocument', { source: OBS });
    await c.send('Page.navigate', { url: `http://127.0.0.1:${httpPort}/` });
    for (let k = 0; k < 40; k++) { if (await c.ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(250); }
    await sleep(3000);
    const cls = await c.ev('window.__cls'), raf = await c.ev('window.__raf'), n = await c.ev('window.__shifts.length');
    // impact (0..300 of 800) = 0.375 ; distance 100 / max(1000,800) = 0.1 -> 0.0375
    const EXPECT = 0.0375, ok = typeof cls === 'number' && Math.abs(cls - EXPECT) < 0.005 && n > 0 && raf > 20;
    return { ok, cls, expect: EXPECT, raf, entries: n };
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
    await c.send('Page.navigate', { url: URL_ });
    for (let k = 0; k < 120; k++) { if (await c.ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(400); }
    await sleep(5000);
    if (SCROLL === 'deep') {
      // Gradual full-page scroll: 0.8vh steps, settle at each, then hold at the
      // bottom. Reproduces a reader working down a listicle, which is what the
      // field CrUX sample actually contains.
      const total = await c.ev('document.documentElement.scrollHeight') || 0;
      const step = Math.round(P.h * 0.8);
      for (let y = 0; y < total; y += step) {
        await c.ev(`window.scrollTo(0,${y})`);
        await sleep(700);
        if (y > 60000) break; // runaway guard on infinite-scroll pages
      }
      await sleep(3000);
    } else if (SCROLL === 'shallow') {
      await c.ev(`window.scrollTo(0,document.body.scrollHeight*0.45)`);
      await sleep(3500);
    }
    const raw = await c.ev(`JSON.stringify({cls:+window.__cls.toFixed(4),shifts:window.__shifts,raf:window.__raf,err:window.__e||null,h:document.documentElement.scrollHeight})`);
    return JSON.parse(raw);
  } finally { c.close(); }
}

async function main() {
  console.log(`\ncls8 — ${PROF} / scroll=${SCROLL} / n=${RUNS}\n${URL_}`);
  const pf = await preflight(BASE + 400);
  console.log(`  PRE-FLIGHT: cls=${pf.cls} (expect ${pf.expect}) raf=${pf.raf} entries=${pf.entries} -> ${pf.ok ? 'INSTRUMENT OK' : 'INSTRUMENT BROKEN'}`);
  if (!pf.ok) { console.log('  ABORTING — refusing to report numbers from an unvalidated instrument.'); process.exit(2); }

  const runs = [];
  for (let i = 0; i < RUNS; i++) {
    try { runs.push(await withTimeout(once(i), 240000, 'run' + i)); }
    catch (e) { runs.push({ error: String(e.message || e).slice(0, 110) }); }
    await sleep(1200);
  }
  const ok = runs.filter(r => typeof r.cls === 'number');
  const vals = ok.map(r => r.cls).sort((a, b) => a - b);
  const q = f => vals.length ? vals[Math.min(vals.length - 1, Math.floor(f * (vals.length - 1)))] : null;
  console.log(`  ok ${ok.length}/${RUNS} | raf/run ${ok.length ? Math.round(ok.reduce((s, r) => s + (r.raf || 0), 0) / ok.length) : '?'} | docHeight ${ok[0]?.h}`);
  console.log(`  MEDIAN ${q(0.5)} | p75 ${q(0.75)} | p90 ${q(0.90)} | max ${vals[vals.length - 1]} | over 0.1: ${vals.filter(v => v > 0.1).length}/${vals.length}`);
  console.log(`  sorted: ${vals.join(', ')}`);
  const agg = {};
  ok.forEach(r => r.shifts.forEach(s => s.src.forEach(x => { agg[x.p] = (agg[x.p] || 0) + s.v / s.src.length; })));
  console.log(`  top shift sources (mean per run):`);
  Object.entries(agg).sort((a, b) => b[1] - a[1]).slice(0, 8)
    .forEach(([p, v]) => console.log(`    ${(v / Math.max(ok.length, 1)).toFixed(4)}  ${p.slice(0, 88)}`));
  const big = ok.flatMap(r => r.shifts).sort((a, b) => b.v - a.v).slice(0, 4);
  console.log(`  largest individual shifts (with rects):`);
  big.forEach(s => {
    const s0 = s.src[0] || {};
    console.log(`    v=${s.v} @${s.ms}ms ${String(s0.p).slice(0, 60)}`);
    console.log(`       ${JSON.stringify(s0.pr)} -> ${JSON.stringify(s0.cr)}`);
  });
  runs.filter(r => r.error).forEach(r => console.log(`  ERR ${r.error}`));
  console.log('DONE-CLS8');
}
main().then(() => process.exit(0)).catch(e => { console.log('FATAL ' + String(e.message || e).slice(0, 200)); process.exit(1); });
