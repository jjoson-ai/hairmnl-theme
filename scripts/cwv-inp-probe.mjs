// cwv-inp-probe — measure real interaction latency on a chosen target, and
// attribute it to script vs render (bd 958r, 2026-08-13).
//
// GA4 RUM ranks poor-INP events by debug_target; this reproduces one of those
// interactions in the lab and reports the Event Timing breakdown plus the long
// tasks that overlap it, so a fix can be aimed at the actual cost rather than
// guessed at.
//
// Event Timing gives: startTime -> processingStart (input delay),
// processingStart -> processingEnd (handler time), processingEnd -> next paint
// (presentation delay). INP is the whole span.
//
// Usage: node cwv-inp-probe.mjs <url> <port> [mobile|desktop] [selector]
import { spawn } from 'node:child_process';
const SHELL = '/Users/y9378348c/.cache/puppeteer/chrome-headless-shell/mac_arm-147.0.7727.57/chrome-headless-shell-mac-arm64/chrome-headless-shell';
const URL_ = process.argv[2];
const PORT = Number(process.argv[3] || 9940);
const PROF = process.argv[4] || 'mobile';
const SEL = process.argv[5] || '.product__media img, .flickity-slider img';
const P = PROF === 'mobile'
  ? { w: 390, h: 844, dpr: 3, mob: true, down: 1.6 * 1024 * 1024 / 8, lat: 150, cpu: 4 }
  : { w: 1440, h: 900, dpr: 1, mob: false, down: 10 * 1024 * 1024 / 8, lat: 40, cpu: 1 };
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function main() {
  const proc = spawn(SHELL, ['--headless=new', `--remote-debugging-port=${PORT}`, '--no-first-run',
    `--user-data-dir=/tmp/inp${PORT}`, '--disable-gpu', 'about:blank'], { stdio: 'ignore' });
  let ws = null;
  try {
    let u = null;
    for (let k = 0; k < 40 && !u; k++) {
      try { const t = (await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json()).find(x => x.type === 'page'); u = t?.webSocketDebuggerUrl || null; } catch {}
      if (!u) await sleep(250);
    }
    if (!u) throw new Error('no cdp');
    ws = new WebSocket(u);
    await new Promise((r, j) => { ws.onopen = r; ws.onerror = () => j(new Error('ws')); });
    let id = 0; const pend = new Map();
    ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
    const send = (m, q = {}) => new Promise(r => { const n = ++id; pend.set(n, r); ws.send(JSON.stringify({ id: n, method: m, params: q })); });
    const ev = async x => (await send('Runtime.evaluate', { expression: x, awaitPromise: true, returnByValue: true }))?.result?.result?.value;
    await send('Page.enable'); await send('Runtime.enable'); await send('Network.enable');
    await send('Emulation.setDeviceMetricsOverride', { width: P.w, height: P.h, deviceScaleFactor: P.dpr, mobile: P.mob });
    await send('Network.emulateNetworkConditions', { offline: false, downloadThroughput: P.down, uploadThroughput: P.down / 4, latency: P.lat });
    if (P.cpu > 1) await send('Emulation.setCPUThrottlingRate', { rate: P.cpu });
    await send('Page.addScriptToEvaluateOnNewDocument', { source: `
      window.__ev=[]; window.__lt=[];
      try{ new PerformanceObserver(l=>{for(const e of l.getEntries()){
        window.__ev.push({name:e.name,start:Math.round(e.startTime),dur:Math.round(e.duration),
          inputDelay:Math.round(e.processingStart-e.startTime),
          handler:Math.round(e.processingEnd-e.processingStart),
          presentation:Math.round(e.startTime+e.duration-e.processingEnd)});
      }}).observe({type:'event',durationThreshold:16,buffered:true}); }catch(e){}
      try{ new PerformanceObserver(l=>{for(const e of l.getEntries()){
        window.__lt.push({start:Math.round(e.startTime),dur:Math.round(e.duration),
          attr:(e.attribution||[]).map(a=>(a.name||'')+':'+(a.containerSrc||a.containerName||'')).join(',').slice(0,120)});
      }}).observe({type:'longtask',buffered:true}); }catch(e){}` });
    await send('Page.navigate', { url: URL_ });
    if (!Number(process.env.EARLY_MS || 0)) {
      for (let k = 0; k < 120; k++) { if (await ev(`document.readyState==='complete'`).catch(() => false)) break; await sleep(400); }
    }
    // EARLY_MS taps while the page is still loading — the condition real users
    // are in when they produce poor INP. Waiting for a settled page measures the
    // best case and hides the problem (88ms settled vs the field's >500ms).
    const EARLY = Number(process.env.EARLY_MS || 0);
    await sleep(EARLY > 0 ? EARLY : 8000);

    const box = await ev(`(function(){
      var el=document.querySelector(${JSON.stringify(SEL)});
      if(!el) return null;
      el.scrollIntoView({block:'center'});
      var r=el.getBoundingClientRect();
      return JSON.stringify({x:Math.round(r.x+r.width/2),y:Math.round(r.y+r.height/2),
        w:Math.round(r.width),h:Math.round(r.height),tag:el.tagName+'.'+(el.className||'').slice(0,50)});
    })()`);
    if (!box) { console.log('target not found: ' + SEL); return; }
    const b = JSON.parse(box);
    await sleep(800);
    await ev(`window.__mark=performance.now(); window.__evBefore=window.__ev.length; window.__ltBefore=window.__lt.length;`);

    // A real tap: touchStart/touchEnd at the element centre.
    for (const type of ['touchStart', 'touchEnd']) {
      await send('Input.dispatchTouchEvent', {
        type, touchPoints: type === 'touchStart' ? [{ x: b.x, y: b.y }] : [],
      });
      await sleep(60);
    }
    await sleep(4000);

    const out = await ev(`JSON.stringify({
      target: ${JSON.stringify(b.tag)},
      eventsAfterTap: window.__ev.slice(window.__evBefore),
      longTasksAfterTap: window.__lt.slice(window.__ltBefore),
      worstEvent: window.__ev.slice(window.__evBefore).sort((a,b)=>b.dur-a.dur)[0]||null
    })`);
    const r = JSON.parse(out);
    console.log(`\nINP probe — ${PROF} — ${URL_}`);
    console.log(`  target: ${r.target} (${b.w}x${b.h} at ${b.x},${b.y})`);
    console.log(`  worst interaction: ${r.worstEvent ? `${r.worstEvent.name} ${r.worstEvent.dur}ms  [input delay ${r.worstEvent.inputDelay} | handlers ${r.worstEvent.handler} | presentation ${r.worstEvent.presentation}]` : 'none over 16ms'}`);
    console.log(`  all events over 16ms after the tap:`);
    (r.eventsAfterTap || []).sort((a, b2) => b2.dur - a.dur).slice(0, 8)
      .forEach(e => console.log(`    ${String(e.name).padEnd(12)} ${String(e.dur).padStart(5)}ms  delay=${e.inputDelay} handler=${e.handler} paint=${e.presentation}`));
    console.log(`  long tasks after the tap: ${(r.longTasksAfterTap || []).length}`);
    (r.longTasksAfterTap || []).slice(0, 6).forEach(t => console.log(`    ${String(t.dur).padStart(5)}ms  ${t.attr || '(no attribution)'}`));
    console.log('DONE-INP');
  } finally { try { ws && ws.close(); } catch {} try { proc.kill('SIGKILL'); } catch {} }
}
main().then(() => process.exit(0)).catch(e => { console.log('FATAL ' + String(e.message || e).slice(0, 200)); process.exit(1); });
