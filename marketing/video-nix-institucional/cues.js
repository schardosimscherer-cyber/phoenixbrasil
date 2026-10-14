const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto('file://' + path.join(__dirname, 'index.html'));
  const c = await p.evaluate(() => ({ duration: window.DURATION, cues: window.cues() }));
  fs.writeFileSync(path.join(__dirname, 'cues.json'), JSON.stringify(c));
  console.log(c.cues.length, 'cues'); await b.close();
})();
