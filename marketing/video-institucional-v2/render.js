// usage: node render.js preview <query> t1 t2 ...  |  node render.js video <query> out.mp4 [fps]
// <query> e.g. "theme=tv"
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

(async () => {
  const [mode, query, ...args] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'index.html') + '?' + query);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  await page.evaluate(async () => {
    await Promise.all([...document.fonts].map(f => f.load()));
    window.fitAll && window.fitAll();
  });

  if (mode === 'preview') {
    const tag = query.replace(/[^a-z0-9]+/gi, '_');
    for (const t of args) {
      await page.evaluate(t => window.render(t), Number(t));
      await page.screenshot({ path: path.join(__dirname, `pv_${tag}_${t}.png`) });
    }
  } else if (mode === 'cues') {
    fs.writeFileSync(args[0], JSON.stringify(await page.evaluate(() => ({ duration: window.DURATION, bpm: window.BPM, music: window.MUSIC, cues: window.cues() }))));
  } else {
    const out = args[0], fps = Number(args[1] || 30);
    const duration = await page.evaluate(() => window.DURATION);
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '16', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'ignore', 'inherit'] });
    const total = Math.round(duration * fps);
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
