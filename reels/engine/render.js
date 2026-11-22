// Usage: node render.js <reelDir>   (reelDir has scenes.json, voice.mp3, timing.json, amp.json)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs'); const path = require('path');
(async () => {
  const dir = path.resolve(process.argv[2]);
  const timing = JSON.parse(fs.readFileSync(path.join(dir, 'timing.json')));
  const fps = 30, dur = timing.duration, n = Math.ceil(dur * fps);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, process.argv[3] || 'stage.html') );
  const rd=f=>JSON.parse(fs.readFileSync(path.join(dir,f)));
  await page.evaluate(([a,b,c,d])=>window.init(a,b,c,d),[rd('scenes.json'),rd('timing.json'),rd('amp.json'),dir]);
  await page.evaluate(()=>document.fonts.ready);
  await page.waitForTimeout(300);
  await page.waitForFunction('window.ready === true');
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
    '-i', fs.existsSync(path.join(dir, 'mix.mp3')) ? path.join(dir, 'mix.mp3') : path.join(dir, 'voice.mp3'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-crf', '18',
    '-af', 'apad', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', path.join(dir, 'reel.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.renderAt(t), i / fps);
    const buf = await page.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await browser.close(); console.log('done');
})();
