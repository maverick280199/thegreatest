// node events.js <reelDir> <stage>  -> writes <reelDir>/events.json : every animation cue with its absolute time
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const D = path.resolve(process.argv[2]); const rd = f => JSON.parse(fs.readFileSync(path.join(D, f)));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, process.argv[3] || 'stage_case.html'));
  await p.evaluate(([a, t, m, d]) => window.init(a, t, m, d), [rd('scenes.json'), rd('timing.json'), rd('amp.json'), D]);
  const ev = await p.evaluate(() => {
    const T = window.__T || null; return null; });
  const out = await p.evaluate((T) => {
    const res = []; const scs = [...document.querySelectorAll('#stage .sc')];
    scs.forEach((e, k) => {
      const sc = T.scenes[k]; if (!sc) return; res.push({ t: sc.start, kind: 'scene' });
      e.querySelectorAll('[data-in],[data-s]').forEach(c => {
        const d = c.dataset.s !== undefined ? T.sentences[+c.dataset.s].start - sc.start + (+c.dataset.d || 0) : (+c.dataset.in || 0);
        const fx = c.dataset.fx || 'up', cls = (c.getAttribute('class') || '') + ' ' + c.tagName.toLowerCase();
        let kind = c.dataset.sfx || null;
        if (!kind) {
          if (fx === 'stamp') kind = 'stamp';
          else if (fx === 'type') kind = 'type';
          else if (fx === 'hl') kind = 'marker';
          else if (fx === 'draw') kind = (c.getAttribute('stroke') || '').toUpperCase() === '#C8322A' && (+c.dataset.dur || 0) > 1 ? 'crack' : 'thread';
          else if (fx === 'pop') kind = /note/.test(cls) ? 'paper' : 'pop';
          else if (/doc|pol|note/.test(cls)) kind = 'paper';
          else if (/kin|big/.test(cls)) kind = 'whoosh';
        }
        if (kind) res.push({ t: sc.start + d, kind, n: kind === 'type' ? (c.dataset.full || '').length : 0 });
        if (c.dataset.count !== undefined) res.push({ t: sc.start + d + 0.1, kind: 'ticks' });
      });
      e.querySelectorAll('[data-count]').forEach(c => { if (!c.dataset.in && !c.dataset.s) res.push({ t: sc.start + 0.1, kind: 'ticks' }); });
    });
    return res.sort((a, b) => a.t - b.t);
  }, rd('timing.json'));
  fs.writeFileSync(path.join(D, 'events.json'), JSON.stringify(out, null, 1)); console.log(out.length + ' cues'); await b.close();
})();
