// Rendert 3D-Bilder: node render.cjs frames.json ausgabeordner
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = __dirname; const mime = { '.js': 'text/javascript', '.html': 'text/html', '.mjs': 'text/javascript' };
const srv = http.createServer((q, s) => { const f = path.join(root, decodeURIComponent(q.url.split('?')[0])); fs.readFile(f, (e, d) => { if (e) { s.writeHead(404); s.end(); return; } s.writeHead(200, { 'Content-Type': mime[path.extname(f)] || 'application/octet-stream' }); s.end(d); }); }).listen(8124);
(async () => {
  const raw = JSON.parse(fs.readFileSync(process.argv[2])); const specs = Array.isArray(raw) ? raw : raw.frames; const meta = Array.isArray(raw) ? null : raw.meta; const out = process.argv[3]; fs.mkdirSync(out, { recursive: true });
  const PAGE = process.argv[4] || 'world.html'; const RW = +(process.env.RENDER_W || 1280), RH = +(process.env.RENDER_H || 720);
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: RW, height: RH } });
  page.on('console', m => console.log('[page]', m.text())); page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto(`http://localhost:8124/${PAGE}?w=${RW}&h=${RH}`); await page.waitForFunction('window.ready===true', null, { timeout: 120000 });
  if (meta) await page.evaluate(m => window.setMeta && window.setMeta(m), meta);
  const t0 = Date.now();
  const info = {};
  for (const s of specs) { info[s.i] = await page.evaluate(sp => window.renderFrame(sp), s); await page.screenshot({ path: path.join(out, String(s.i).padStart(5, '0') + '.jpg'), type: 'jpeg', quality: 93 }); if (s.i % 25 === 0) console.log('frame', s.i, ((Date.now() - t0) / 1000).toFixed(0) + 's'); }
  fs.writeFileSync(path.join(out, 'info.json'), JSON.stringify(info));
  await browser.close(); srv.close();
})();
