// usage: node render.js preview t1 t2 ...   |   node render.js video out.mp4 [fps]
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

(async () => {
  const [mode, ...args] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);

  if (mode === 'preview') {
    for (const t of args) {
      await page.evaluate(t => window.render(t), Number(t));
      await page.screenshot({ path: path.join(__dirname, `frame_${t}.png`) });
    }
  } else {
    const out = args[0], fps = Number(args[1] || 30);
    const duration = await page.evaluate(() => window.DURATION);
    const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-preset', 'slow', '-crf', '17', '-movflags', '+faststart', out],
      { stdio: ['pipe', 'ignore', 'inherit'] });
    const total = Math.round(duration * fps);
    for (let i = 0; i < total; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`frame ${i}/${total}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();
})();
