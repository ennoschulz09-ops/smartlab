// Figur v2: weisser Kopf mit Haaren, Hoodie mit Logo, Cargohose mit Taschen/Kette, Sneaker, Accessoires, Haende mit Fingern, Gesichts-Bibliothek
import * as THREE from 'three';
const CW = 1024, CH = 670, PPD = CW / 130;
export function faceCanvas() { const c = document.createElement('canvas'); c.width = CW; c.height = CH; const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4; return { c, tex }; }
const ay = (th) => (th - 55) / 85 * CH;
// eye: dot | happy | wink | smug | wide | closed | sleepy ; mouth: smile | grin | laugh | smirk | flat | o | worry | frown | tongue
export function drawFace2(f, p = {}) {
  const { c, tex } = f; const g = c.getContext('2d'); g.clearRect(0, 0, CW, CH);
  const ink = p.ink || '#1a1420'; g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = ink; g.fillStyle = ink;
  const ex = [CW / 2 - 24 * PPD, CW / 2 + 24 * PPD], ey = ay(98), look = p.look || [0, 0];
  const eyes = p.eye ? (Array.isArray(p.eye) ? p.eye : [p.eye, p.eye]) : ['dot', 'dot'];
  for (let i = 0; i < 2; i++) {
    const x = ex[i] + look[0] * 2.5 * PPD, y = ey + look[1] * 2 * PPD, k = eyes[i];
    if (k === 'dot') { g.beginPath(); g.ellipse(x, y, 3.4 * PPD, 5.4 * PPD, 0, 0, 7); g.fill(); }
    else if (k === 'happy') { g.lineWidth = 2.8 * PPD; g.beginPath(); g.arc(x, y + 2 * PPD, 5.5 * PPD, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    else if (k === 'closed') { g.lineWidth = 2.6 * PPD; g.beginPath(); g.arc(x, y - 2 * PPD, 5.5 * PPD, Math.PI * 0.1, Math.PI * 0.9); g.stroke(); }
    else if (k === 'wink') { g.lineWidth = 2.8 * PPD; g.beginPath(); g.moveTo(x - 5 * PPD, y - 2 * PPD); g.lineTo(x + 4 * PPD, y + 1.5 * PPD); g.moveTo(x - 5 * PPD, y + 5 * PPD); g.lineTo(x + 4 * PPD, y + 1.5 * PPD); g.stroke(); }
    else if (k === 'smug') { g.beginPath(); g.ellipse(x, y + 1.6 * PPD, 3.4 * PPD, 4 * PPD, 0, 0, 7); g.fill(); g.lineWidth = 3.4 * PPD; g.beginPath(); g.moveTo(x - 6.5 * PPD, y - 2.2 * PPD); g.lineTo(x + 6.5 * PPD, y - 3.2 * PPD); g.stroke(); }
    else if (k === 'wide') { g.fillStyle = '#fff'; g.beginPath(); g.ellipse(x, y, 6.8 * PPD, 8.2 * PPD, 0, 0, 7); g.fill(); g.lineWidth = 1.4 * PPD; g.stroke(); g.fillStyle = ink; g.beginPath(); g.ellipse(x + look[0] * 2 * PPD, y + look[1] * 2 * PPD, 3 * PPD, 3.8 * PPD, 0, 0, 7); g.fill(); }
    if (p.brow) { const b = p.brow[i]; g.save(); g.translate(x, y - 11 * PPD); g.rotate((i ? -1 : 1) * b * Math.PI / 180); g.lineWidth = 2.4 * PPD; g.beginPath(); g.moveTo(-6 * PPD, 0); g.lineTo(6 * PPD, 0); g.stroke(); g.restore(); }
  }
  const mx = CW / 2, my = ay(127), m = p.mouth || 'smile'; g.lineWidth = 2.4 * PPD; g.fillStyle = ink;
  const openMouth = (w, h, tongue) => { g.fillStyle = '#3a0f1c'; g.beginPath(); g.moveTo(mx - w, my - h * 0.2); g.quadraticCurveTo(mx, my - h * 0.5, mx + w, my - h * 0.2); g.quadraticCurveTo(mx + w * 0.8, my + h, mx, my + h * 1.05); g.quadraticCurveTo(mx - w * 0.8, my + h, mx - w, my - h * 0.2); g.fill();
    if (tongue) { g.save(); g.clip(); g.fillStyle = '#ff6f86'; g.beginPath(); g.ellipse(mx, my + h * 0.95, w * 0.62, h * 0.55, 0, 0, 7); g.fill(); g.restore(); } g.fillStyle = ink; };
  if (m === 'smile') { g.beginPath(); g.moveTo(mx - 8 * PPD, my); g.quadraticCurveTo(mx, my + 7 * PPD, mx + 8 * PPD, my); g.stroke(); }
  else if (m === 'smirk') { g.beginPath(); g.moveTo(mx - 7 * PPD, my + 1.5 * PPD); g.quadraticCurveTo(mx + 1 * PPD, my + 6 * PPD, mx + 9 * PPD, my - 2 * PPD); g.stroke(); }
  else if (m === 'flat') { g.beginPath(); g.moveTo(mx - 6 * PPD, my + PPD); g.lineTo(mx + 6 * PPD, my + PPD); g.stroke(); }
  else if (m === 'frown') { g.beginPath(); g.moveTo(mx - 7 * PPD, my + 3 * PPD); g.quadraticCurveTo(mx, my - 3 * PPD, mx + 7 * PPD, my + 3 * PPD); g.stroke(); }
  else if (m === 'worry') { g.beginPath(); g.moveTo(mx - 8 * PPD, my + 2 * PPD); for (let k = 0; k < 4; k++) g.quadraticCurveTo(mx - 8 * PPD + (k * 4 + 1) * PPD, my - (k % 2 ? -2 : 2) * PPD, mx - 8 * PPD + (k * 4 + 4) * PPD, my + 2 * PPD); g.stroke(); }
  else if (m === 'o') { g.beginPath(); g.ellipse(mx, my + 2 * PPD, 3.2 * PPD, 4.6 * PPD, 0, 0, 7); g.fill(); }
  else if (m === 'grin') openMouth(9 * PPD, 5.5 * PPD, false);
  else if (m === 'laugh' || m === 'tongue') openMouth(9.5 * PPD, 8 * PPD, true);
  else if (m === 'talk') { const h = 1.5 * PPD + 7 * PPD * (p.open ?? 0.5); openMouth(7 * PPD + 3 * PPD * (p.open ?? 0.5), h, (p.open ?? 0.5) > 0.5); }
  if (p.sweat > 0) { [[CW / 2 - 50 * PPD, ay(84)], [CW / 2 + 52 * PPD, ay(80)]].forEach(([xx, y0], i) => { const yy = y0 + p.sweat * (4 + i * 5) * PPD; g.fillStyle = 'rgba(150,205,255,0.95)'; g.beginPath(); g.moveTo(xx, yy - 7 * PPD); g.quadraticCurveTo(xx + 4.6 * PPD, yy + PPD, xx, yy + 4 * PPD); g.quadraticCurveTo(xx - 4.6 * PPD, yy + PPD, xx, yy - 7 * PPD); g.fill(); }); }
  tex.needsUpdate = true;
}
const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.7, ...o });
const sphereAt = (r, m, x, y, z, sx = 1, sy = 1, sz = 1) => { const s = new THREE.Mesh(new THREE.SphereGeometry(r, 24, 18), m); s.position.set(x, y, z); s.scale.set(sx, sy, sz); s.castShadow = true; return s; };

function makeHand(color) {
  const g = new THREE.Group(); const m = mat(color, { roughness: 0.5 });
  g.add(sphereAt(0.2, m, 0, -0.1, 0, 1, 1.1, 0.75));
  const fingers = [];
  [[-0.1, 0.17], [-0.035, 0.2], [0.035, 0.2], [0.1, 0.16]].forEach(([x, len], i) => { const f = new THREE.Group(); f.position.set(x, -0.2, 0.0); const m1 = new THREE.Mesh(new THREE.CapsuleGeometry(0.045, len, 4, 8), m); m1.position.y = -len / 2 - 0.02; m1.castShadow = true; f.add(m1); g.add(f); fingers.push(f); });
  const th = new THREE.Group(); th.position.set(0.18, -0.08, 0.05); th.rotation.z = 0.8; const tm = new THREE.Mesh(new THREE.CapsuleGeometry(0.05, 0.13, 4, 8), m); tm.position.y = -0.09; th.add(tm); g.add(th);
  g.userData = { fingers, thumb: th }; return g;
}
export function handPose(hand, kind) { const { fingers, thumb } = hand.userData; const c = { open: [0.15, 0.15, 0.15, 0.15], fist: [1.6, 1.6, 1.6, 1.6], peace: [0.0, 0.0, 1.6, 1.6], point: [0.0, 1.6, 1.6, 1.6], relaxed: [0.5, 0.6, 0.7, 0.8] }[kind] || [0.4, 0.4, 0.4, 0.4];
  fingers.forEach((f, i) => { f.rotation.x = -c[i]; if (kind === 'peace' && i < 2) f.rotation.z = i ? -0.18 : 0.18; else f.rotation.z = 0; }); thumb.rotation.x = kind === 'fist' ? -0.9 : -0.2; }

function logoTexture(kind) {
  const c = document.createElement('canvas'); c.width = c.height = 256; const g = c.getContext('2d'); g.clearRect(0, 0, 256, 256);
  g.fillStyle = kind === 'light' ? '#f4f0ff' : '#1d1424'; g.strokeStyle = g.fillStyle; g.lineWidth = 9; g.lineJoin = 'round';
  g.beginPath(); g.moveTo(128, 70); g.bezierCurveTo(70, 70, 70, 150, 62, 186); g.lineTo(194, 186); g.bezierCurveTo(186, 150, 186, 70, 128, 70); g.closePath(); g.fill();
  g.beginPath(); g.arc(128, 62, 10, 0, 7); g.stroke(); g.beginPath(); g.arc(128, 202, 14, 0, 7); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}

export function makeBuddy2(opt = {}) {
  const o = Object.assign({ hoodie: 0xff8a2b, pants: 0x2a2530, shoe: 0xf4f4f8, shoeAccent: 0x2fc4b8, skin: 0xf6f1f6, hair: null, hairColor: 0xe6e0ea, headphones: null, cap: null, capBack: true, beanie: null, shades: false, logo: 'dark', bag: false, scale: 1, chain: true }, opt);
  const root = new THREE.Group(), body = new THREE.Group(); const lift = new THREE.Group(); lift.position.y = 0.3; root.add(lift); lift.add(body); const P = { root, body, legs: [], arms: [] };
  // ---- Beine: weite Cargohose, Stulpen, Taschen, Kette; Sneaker
  for (const s of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(s * 0.26, 1.05, 0); body.add(hip);
    const thigh = new THREE.Mesh(new THREE.CapsuleGeometry(0.24, 0.55, 8, 16), mat(o.pants, { roughness: 0.85 })); thigh.position.y = -0.38; thigh.castShadow = true; hip.add(thigh);
    const shin = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.26, 0.5, 18), mat(o.pants, { roughness: 0.85 })); shin.position.y = -0.85; shin.castShadow = true; hip.add(shin);
    const cuff = new THREE.Mesh(new THREE.TorusGeometry(0.255, 0.05, 8, 24), mat(o.pants, { roughness: 0.9 })); cuff.rotation.x = Math.PI / 2; cuff.position.y = -1.09; hip.add(cuff);
    const pocket = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.34, 0.3), mat(o.pants, { roughness: 0.95 })); pocket.position.set(s * 0.27, -0.45, 0.02); hip.add(pocket);
    const flap = new THREE.Mesh(new THREE.BoxGeometry(0.11, 0.1, 0.32), mat(o.pants, { roughness: 0.95 })); flap.position.set(s * 0.275, -0.3, 0.02); hip.add(flap);
    const shoe = new THREE.Group(); shoe.position.set(0, -1.12, 0.12); hip.add(shoe);
    const upper = new THREE.Mesh(new THREE.SphereGeometry(0.3, 24, 18), mat(o.shoe, { roughness: 0.55 })); upper.scale.set(0.95, 0.62, 1.55); upper.position.set(0, 0.02, 0.1); upper.castShadow = true; shoe.add(upper);
    const toe = new THREE.Mesh(new THREE.SphereGeometry(0.23, 20, 14), mat(o.shoe, { roughness: 0.5 })); toe.scale.set(1.1, 0.7, 1.0); toe.position.set(0, -0.02, 0.4); shoe.add(toe);
    const sole = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.09, 1.0), mat(0xf2f2f4, { roughness: 0.6 })); sole.position.set(0, -0.17, 0.15); sole.castShadow = true; shoe.add(sole);
    const acc = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.05, 0.5), mat(o.shoeAccent, { roughness: 0.6 })); acc.position.set(0, -0.095, 0.16); shoe.add(acc);
    for (let k = 0; k < 3; k++) { const lace = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.32, 6), mat(0xffffff)); lace.rotation.z = Math.PI / 2; lace.position.set(0, 0.2 - k * 0.012, 0.0 + k * 0.17); shoe.add(lace); }
    P.legs.push(hip);
    if (o.chain && s === 1) { for (let k = 0; k < 9; k++) { const a = k / 8; const l = new THREE.Mesh(new THREE.TorusGeometry(0.03, 0.01, 6, 10), mat(0xcfd3dc, { metalness: 0.9, roughness: 0.3 })); l.position.set(0.3 + 0.03 * Math.sin(a * 3.14), 0.0 - a * 0.5, 0.15 + 0.05 * Math.sin(a * 3.14)); l.rotation.y = (k % 2) * Math.PI / 2; hip.add(l); } }
  }
  // ---- Torso (Hoodie): Koerper, Bund, Kapuze, Kordeln, Tasche, Logo
  const torso = new THREE.Mesh(new THREE.SphereGeometry(0.55, 40, 28), mat(o.hoodie, { roughness: 0.9 })); torso.scale.set(1.25, 1.2, 0.95); torso.position.y = 1.65; torso.castShadow = true; body.add(torso); P.torso = torso;
  const hem = new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.07, 10, 36), mat(o.hoodie, { roughness: 0.95 })); hem.rotation.x = Math.PI / 2; hem.position.y = 1.08; hem.scale.set(1.12, 0.85, 1); body.add(hem);
  const hoodBack = new THREE.Mesh(new THREE.SphereGeometry(0.42, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.6), mat(o.hoodie, { roughness: 0.92 })); hoodBack.position.set(0, 2.18, -0.22); hoodBack.rotation.x = 0.55; hoodBack.scale.set(1.15, 0.9, 0.9); body.add(hoodBack);
  const collar = new THREE.Mesh(new THREE.TorusGeometry(0.36, 0.13, 14, 32), mat(o.hoodie, { roughness: 0.92 })); collar.rotation.x = Math.PI / 2; collar.position.y = 2.17; collar.scale.set(1.05, 0.9, 1); body.add(collar);
  
  for (const s of [-1, 1]) { const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.022, 0.022, 0.5, 8), mat(0xf4efe9)); cord.position.set(s * 0.14, 1.88, 0.55); body.add(cord); const bead = new THREE.Mesh(new THREE.SphereGeometry(0.04, 10, 8), mat(0xf4efe9)); bead.position.set(s * 0.14, 1.62, 0.56); body.add(bead); }
  const logo = new THREE.Mesh(new THREE.PlaneGeometry(0.42, 0.42), new THREE.MeshBasicMaterial({ map: logoTexture(o.logo), transparent: true, depthWrite: false })); logo.position.set(0, 1.82, 0.585); logo.rotation.x = -0.06; body.add(logo);
  if (o.bag) { const strap = new THREE.Mesh(new THREE.BoxGeometry(0.12, 1.5, 0.05), mat(0x221a26)); strap.position.set(-0.05, 1.7, 0.52); strap.rotation.z = -0.5; body.add(strap); const bag = new THREE.Mesh(new THREE.BoxGeometry(0.55, 0.4, 0.22), mat(0x221a26, { roughness: 0.5 })); bag.position.set(0.5, 1.2, 0.62); bag.rotation.z = -0.3; body.add(bag); }
  // ---- Kopf
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.3, 14), mat(0x1a1420)); neck.position.y = 2.3; body.add(neck);
  const head = new THREE.Group(); head.position.y = 3.2; body.add(head); P.head = head;
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.9, 72, 52), new THREE.MeshPhysicalMaterial({ color: o.skin, roughness: 0.42, sheen: 0.8, sheenColor: new THREE.Color(0xffd8f0), clearcoat: 0.25, clearcoatRoughness: 0.5 })); sphere.scale.set(1, 1.02, 0.97); sphere.castShadow = true; head.add(sphere);
  const face = faceCanvas(); P.face = face;
  const patch = new THREE.Mesh(new THREE.SphereGeometry(0.905, 72, 48, Math.PI / 2 - 65 * Math.PI / 180, 130 * Math.PI / 180, 55 * Math.PI / 180, 85 * Math.PI / 180), new THREE.MeshBasicMaterial({ map: face.tex, transparent: true, depthWrite: false })); patch.scale.set(1, 1.02, 0.97); patch.renderOrder = 2; head.add(patch); drawFace2(face, {});
  // Haare: viele Straehnen (nach hinten/oben, Gesicht frei)
  if (o.hair) { const hm = mat(o.hairColor, { roughness: 0.6 }); let seed = 11; const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
    const base = new THREE.Mesh(new THREE.SphereGeometry(0.93, 40, 24, 0, Math.PI * 2, 0, Math.PI * 0.36), hm); base.rotation.x = -0.35; base.position.set(0, 0.04, -0.06); base.castShadow = true; head.add(base);
    const n = o.hair === 'spiky' ? 22 : 18; for (let i = 0; i < n; i++) { const th = (0.1 + rnd() * 0.42) * Math.PI, ph = rnd() * Math.PI * 2; const nx = Math.sin(th) * Math.cos(ph), ny = Math.cos(th), nz = Math.sin(th) * Math.sin(ph);
      if ((nz > 0.2 && th > 0.26 * Math.PI) || (Math.abs(nx) > 0.62 && th > 0.3 * Math.PI)) continue; const r = 0.2 + rnd() * 0.14; const up = o.hair === 'spiky' ? 1.7 : 1.25; const m = sphereAt(r, hm, nx * 0.88, ny * 0.9 + 0.08, nz * 0.88 - 0.05, 1, up, 1); m.lookAt(nx * 3, ny * 3 + 2, nz * 3); m.rotateX(-Math.PI / 2); head.add(m); }
    if (o.hair === 'swoop') { for (let k = 0; k < 4; k++) { const f = sphereAt(0.22, hm, -0.45 + k * 0.28, 0.88 - k * 0.02, 0.5 - k * 0.04, 1.2, 0.8, 0.9); f.rotation.z = 0.3 - k * 0.12; head.add(f); } } }
  if (o.beanie) { const b = new THREE.Mesh(new THREE.SphereGeometry(0.93, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.4), mat(o.beanie, { roughness: 0.95 })); b.position.y = 0.05; b.rotation.x = -0.1; head.add(b); const f = new THREE.Mesh(new THREE.TorusGeometry(0.84, 0.11, 12, 40), mat(0xf4ecff, { roughness: 0.95 })); f.rotation.x = Math.PI / 2 - 0.1; f.position.set(0, 0.36, 0.02); head.add(f); const pom = new THREE.Mesh(new THREE.SphereGeometry(0.19, 20, 16), mat(0xf4ecff, { roughness: 0.95 })); pom.position.set(0, 1.0, 0); head.add(pom); P.pom = pom; }
  if (o.cap) { const cp = new THREE.Mesh(new THREE.SphereGeometry(0.95, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.42), mat(o.cap, { roughness: 0.7 })); cp.position.y = 0.06; cp.rotation.x = -0.15; head.add(cp); const br = new THREE.Mesh(new THREE.CylinderGeometry(0.7, 0.78, 0.06, 28, 1, false, -Math.PI / 2, Math.PI), mat(o.cap, { roughness: 0.7 })); br.position.set(0, 0.3, o.capBack ? -0.65 : 0.68); br.rotation.set(0.08, o.capBack ? Math.PI : 0, 0); br.scale.set(1, 1, 1.15); head.add(br); }
  if (o.headphones) { const band = new THREE.Mesh(new THREE.TorusGeometry(0.98, 0.05, 10, 40, Math.PI), mat(o.headphones, { roughness: 0.4 })); band.rotation.z = 0; band.position.y = 0.0; head.add(band); for (const s of [-1, 1]) { const cup = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.22, 24), mat(o.headphones, { roughness: 0.35 })); cup.rotation.z = Math.PI / 2; cup.position.set(s * 0.97, 0.0, 0.0); cup.castShadow = true; head.add(cup); const pad = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.06, 24), mat(0x2a2230)); pad.rotation.z = Math.PI / 2; pad.position.set(s * 1.1, 0.0, 0.0); head.add(pad); } }
  if (o.shades) { const gm = mat(0x0b0b10, { roughness: 0.15, metalness: 0.2 }); for (const s of [-1, 1]) { const lens = new THREE.Mesh(new THREE.SphereGeometry(0.3, 24, 16), gm); lens.scale.set(1.15, 0.72, 0.18); lens.position.set(s * 0.42, 0.06, 0.88); head.add(lens); } const br = new THREE.Mesh(new THREE.BoxGeometry(0.2, 0.05, 0.05), gm); br.position.set(0, 0.1, 0.9); head.add(br); }
  // ---- Arme mit Haenden
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 0.72, 2.0, 0); body.add(sh);
    sh.add(sphereAt(0.2, mat(o.hoodie, { roughness: 0.9 }), 0, 0, 0));
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 0.46, 8, 14), mat(o.hoodie, { roughness: 0.9 })); up.position.y = -0.32; up.castShadow = true; sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.64; sh.add(el); el.add(sphereAt(0.17, mat(o.hoodie, { roughness: 0.9 }), 0, 0, 0));
    const lo = new THREE.Mesh(new THREE.CapsuleGeometry(0.155, 0.4, 8, 14), mat(o.hoodie, { roughness: 0.9 })); lo.position.y = -0.3; lo.castShadow = true; el.add(lo);
    const cuff = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.04, 8, 20), mat(o.hoodie, { roughness: 0.95 })); cuff.rotation.x = Math.PI / 2; cuff.position.y = -0.53; el.add(cuff);
    const hand = makeHand(0xf6f1f6); hand.position.y = -0.6; el.add(hand); P.arms.push({ sh, el, hand }); handPose(hand, 'relaxed');
  }
  root.scale.setScalar(o.scale); return P;
}
