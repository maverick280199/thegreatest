// node preview.js <reelDir> <stage> <mode> <out.png> t1 t2 ...  -> one contact sheet of stills
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
(async () => {
  const [dir, stage, mode, out, ...ts] = process.argv.slice(2); const D = path.resolve(dir);
  const rd = f => JSON.parse(fs.readFileSync(path.join(D, f)));
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, stage));
  const sc = rd('scenes.json'); sc.avatar = mode;
  await p.evaluate(([a, t, m, d]) => window.init(a, t, m, d), [sc, rd('timing.json'), rd('amp.json'), D]);
  await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(400);
  const shots = [];
  for (const t of ts) { await p.evaluate(x => window.renderAt(x), +t); shots.push(await p.screenshot({ type: 'png' })); }
  await p.setViewportSize({ width: 360 * ts.length, height: 640 });
  await p.setContent('<body style="margin:0;display:flex">' + shots.map(s => `<img width=360 src="data:image/png;base64,${s.toString('base64')}">`).join('') + '</body>');
  await p.waitForTimeout(200); await p.screenshot({ path: out }); await b.close();
})();
