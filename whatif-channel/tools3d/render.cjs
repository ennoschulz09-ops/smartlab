const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const root = process.cwd(); const mime={'.js':'text/javascript','.html':'text/html','.mjs':'text/javascript'};
const srv = http.createServer((q,s)=>{ const f=path.join(root,decodeURIComponent(q.url.split('?')[0])); fs.readFile(f,(e,d)=>{ if(e){s.writeHead(404);s.end();return;} s.writeHead(200,{'Content-Type':mime[path.extname(f)]||'application/octet-stream'}); s.end(d);}); }).listen(8123);
(async()=>{
const browser = await chromium.launch({ args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport:{width:1280,height:720} });
page.on('console', m=>console.log('[page]', m.text())); page.on('requestfailed', r=>console.log('[reqfail]', r.url())); page.on('pageerror', e=>console.log('[err]', e.message));
await page.goto('http://localhost:8123/'+(process.argv[2]||'spike.html')); await page.waitForFunction('window.ready===true',null,{timeout:120000});
const times=(process.argv[3]||'0,1.5').split(',').map(Number);
for (const t of times){ const t0=Date.now(); await page.evaluate(t=>window.render(t),t); await page.screenshot({path:`shot_${t}.png`}); console.log('t',t,'ms',Date.now()-t0); }
await browser.close(); srv.close();
})();
