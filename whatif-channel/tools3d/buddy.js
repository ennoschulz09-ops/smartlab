// Figur im Stil "Kugelkopf": heller Kopf, minimales Gesicht, Hoodie, duenne Gliedmassen, grosse Haende
import * as THREE from 'three';

// Gesichtsflaeche: 130 Grad Breite x 85 Grad Hoehe der Kugel. Alle Masse in Grad, damit sie zur Kopfgroesse passen
// (gemessen am Vorbild: Augen sitzen weit auseinander, Lider lang, Mund nahe am Kinn).
const CW = 1024, CH = 670, PPD = CW / 130;
export function faceCanvas() {
  const c = document.createElement('canvas'); c.width = CW; c.height = CH;
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  return { c, tex };
}
const ay = (theta) => (theta - 55) / 85 * CH; // Polarwinkel -> Canvas-y

// p: lid 0..1, brow [l,r] (Winkel, + = streng), rise [l,r] (Grad), mouth smile|smirk|flat|open|o|grit|frown, open 0..1, look [x,y], sweat 0..1
export function drawFace(f, p = {}) {
  const { c, tex } = f; const g = c.getContext('2d');
  g.clearRect(0, 0, CW, CH);
  const ink = p.ink || '#2a1840';
  g.lineCap = 'round'; g.lineJoin = 'round'; g.strokeStyle = ink; g.fillStyle = ink;
  const lid = p.lid ?? 0.45, look = p.look || [0, 0];
  const exs = [CW / 2 - 26 * PPD, CW / 2 + 26 * PPD], ey = ay(97);
  for (let i = 0; i < 2; i++) {
    const x = exs[i], s = i ? 1 : -1; const open = 1 - lid;
    const lx = look[0] * 3 * PPD, ly = look[1] * 2 * PPD;
    g.lineWidth = 3.2 * PPD;
    g.beginPath(); g.moveTo(x - 13 * PPD + lx, ey - 1.5 * PPD + ly); g.quadraticCurveTo(x + lx, ey - 5 * PPD + ly, x + 13 * PPD + lx, ey - 1.5 * PPD + ly); g.stroke();
    g.beginPath(); g.ellipse(x + lx * 1.2, ey + 4 * PPD + ly, 4.2 * PPD, 6.5 * PPD * Math.max(0.3, open), 0, 0, Math.PI * 2); g.fill();
    const b = (p.brow || [0, 0])[i]; const rise = (p.rise || [0, 0])[i];
    g.save(); g.translate(x, ey - 15 * PPD - rise * PPD); g.rotate((-s * b) * Math.PI / 180);
    g.lineWidth = 3.6 * PPD; g.beginPath(); g.moveTo(-12.5 * PPD, 0); g.lineTo(12.5 * PPD, 0); g.stroke(); g.restore();
  }
  const mx = CW / 2, my = ay(128), m = p.mouth || 'smile', w = 11.5 * PPD;
  g.lineWidth = 3 * PPD;
  if (m === 'smile') { g.beginPath(); g.moveTo(mx - w, my); g.quadraticCurveTo(mx, my + 9 * PPD, mx + w, my); g.stroke(); }
  else if (m === 'smirk') { g.beginPath(); g.moveTo(mx - w, my + 1.5 * PPD); g.quadraticCurveTo(mx + 2 * PPD, my + 7 * PPD, mx + w * 1.2, my - 3 * PPD); g.stroke(); }
  else if (m === 'flat') { g.beginPath(); g.moveTo(mx - w * 0.8, my + PPD); g.lineTo(mx + w * 0.8, my + PPD); g.stroke(); }
  else if (m === 'frown') { g.beginPath(); g.moveTo(mx - w, my + 4 * PPD); g.quadraticCurveTo(mx, my - 4 * PPD, mx + w, my + 4 * PPD); g.stroke(); }
  else if (m === 'o') { g.beginPath(); g.ellipse(mx, my + 2 * PPD, 3.6 * PPD, 5 * PPD, 0, 0, Math.PI * 2); g.fill(); }
  else if (m === 'open') { const h = 2.5 * PPD + 9 * PPD * (p.open ?? 0.6); g.beginPath(); g.ellipse(mx, my + h * 0.4, 7 * PPD + 3 * PPD * (p.open ?? 0.6), h, 0, 0, Math.PI * 2); g.fillStyle = '#3a1030'; g.fill(); }
  else if (m === 'grit') {
    g.fillStyle = '#fffaf5'; g.lineWidth = 1.8 * PPD; g.beginPath(); g.roundRect(mx - 10 * PPD, my - 2 * PPD, 20 * PPD, 8 * PPD, 3 * PPD); g.fill(); g.stroke();
    g.lineWidth = PPD; for (let k = -1; k <= 1; k++) { g.beginPath(); g.moveTo(mx + k * 5 * PPD, my - 2 * PPD); g.lineTo(mx + k * 5 * PPD, my + 6 * PPD); g.stroke(); }
  }
  if (p.sweat > 0) {
    [[CW / 2 - 52 * PPD, ay(84)], [CW / 2 + 55 * PPD, ay(80)], [CW / 2 - 56 * PPD, ay(112)]].forEach(([xx, y0], i) => { const yy = y0 + p.sweat * (4 + i * 5) * PPD;
      g.fillStyle = 'rgba(150,205,255,0.95)'; g.beginPath(); g.moveTo(xx, yy - 7 * PPD); g.quadraticCurveTo(xx + 4.6 * PPD, yy + PPD, xx, yy + 4 * PPD); g.quadraticCurveTo(xx - 4.6 * PPD, yy + PPD, xx, yy - 7 * PPD); g.fill(); });
  }
  tex.needsUpdate = true;
}

const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.0, ...o });

export function makeBuddy(opt = {}) {
  const o = Object.assign({ hoodie: 0x9ec5ff, pants: 0xb7a6e8, head: 0xece4ff, cap: null, hair: null, beanie: null, tie: null, scale: 1 }, opt);
  const root = new THREE.Group(); const body = new THREE.Group(); root.add(body);
  const parts = { root, body };
  parts.legs = [];
  for (const s of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(s * 0.22, 0.95, 0); body.add(hip);
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.085, 0.7, 6, 14), mat(o.pants)); leg.position.y = -0.42; leg.castShadow = true; hip.add(leg);
    const shoe = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), mat(0xf4f1ff)); shoe.scale.set(1, 0.6, 1.5); shoe.position.set(0, -0.86, 0.08); shoe.castShadow = true; hip.add(shoe);
    parts.legs.push(hip);
  }
  const torso = new THREE.Mesh(new THREE.SphereGeometry(0.5, 32, 24), mat(o.hoodie, { roughness: 0.82 }));
  torso.scale.set(1.3, 1.22, 0.92); torso.position.y = 1.55; torso.castShadow = true; body.add(torso); parts.torso = torso;
  const pocket = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.06), mat(o.hoodie, { roughness: 0.9 })); pocket.position.set(0, 1.25, 0.46); pocket.rotation.x = -0.15; body.add(pocket);
  const hood = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.12, 12, 28), mat(o.hoodie, { roughness: 0.85 })); hood.rotation.x = Math.PI / 2; hood.position.y = 2.0; hood.scale.set(1, 0.8, 1); body.add(hood);
  for (const s of [-1, 1]) { const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.36, 8), mat(0xffd2e6)); cord.position.set(s * 0.12, 1.8, 0.47); body.add(cord); }
  if (o.tie) { const tie = new THREE.Mesh(new THREE.BoxGeometry(0.14, 0.52, 0.05), mat(o.tie, { roughness: 0.5 })); tie.position.set(0, 1.72, 0.5); tie.rotation.x = -0.12; body.add(tie);
    const knot = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.12, 0.07), mat(o.tie, { roughness: 0.5 })); knot.position.set(0, 1.98, 0.47); body.add(knot); }
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 0.32, 12), mat(0xf4d6e8)); neck.position.y = 2.2; body.add(neck);
  const head = new THREE.Group(); head.position.y = 2.18 + 0.8; body.add(head); parts.head = head;
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.8, 64, 48), new THREE.MeshPhysicalMaterial({
    color: o.head, roughness: 0.48, metalness: 0.0, iridescence: 0.3, iridescenceIOR: 1.4, iridescenceThicknessRange: [150, 420], sheen: 0.7, sheenColor: new THREE.Color(0xffd0ff) }));
  sphere.castShadow = true; head.add(sphere);
  const face = faceCanvas(); parts.face = face;
  const patch = new THREE.Mesh(new THREE.SphereGeometry(0.803, 72, 48, Math.PI / 2 - 65 * Math.PI / 180, 130 * Math.PI / 180, 55 * Math.PI / 180, 85 * Math.PI / 180), new THREE.MeshBasicMaterial({ map: face.tex, transparent: true, depthWrite: false }));
  patch.renderOrder = 2; head.add(patch);
  drawFace(face, {});
  if (o.cap) {
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.83, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.42), mat(o.cap, { roughness: 0.7 })); cap.position.y = 0.02; cap.rotation.x = -0.12; head.add(cap);
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.7, 0.05, 28, 1, false, -Math.PI / 2, Math.PI), mat(o.cap, { roughness: 0.7 })); brim.position.set(0, 0.26, 0.62); brim.rotation.x = 0.1; brim.scale.set(1, 1, 1.1); head.add(brim);
  }
  if (o.hair) { const hair = new THREE.Mesh(new THREE.SphereGeometry(0.84, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.36), mat(o.hair, { roughness: 0.55 })); hair.position.y = 0.04; hair.rotation.x = -0.28; head.add(hair); }
  if (o.beanie) {
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.84, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.4), mat(o.beanie, { roughness: 0.9 })); b.position.y = 0.04; b.rotation.x = -0.1; head.add(b);
    const fold = new THREE.Mesh(new THREE.TorusGeometry(0.76, 0.1, 12, 40), mat(0xf4ecff, { roughness: 0.9 })); fold.rotation.x = Math.PI / 2 - 0.1; fold.position.set(0, 0.34, 0.02); fold.scale.set(1, 1, 1); head.add(fold);
    const pom = new THREE.Mesh(new THREE.SphereGeometry(0.17, 20, 16), mat(0xf4ecff, { roughness: 0.95 })); pom.position.set(0, 0.92, 0); head.add(pom);
  }
  parts.arms = [];
  for (const s of [-1, 1]) {
    const cap0 = new THREE.Mesh(new THREE.SphereGeometry(0.15, 16, 12), mat(o.hoodie, { roughness: 0.85 })); cap0.position.set(s * 0.66, 1.9, 0); body.add(cap0);
    const sh = new THREE.Group(); sh.position.set(s * 0.66, 1.9, 0); body.add(sh);
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.1, 0.5, 6, 12), mat(o.hoodie, { roughness: 0.85 })); up.position.y = -0.3; up.castShadow = true; sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.62; sh.add(el);
    const lo = new THREE.Mesh(new THREE.CapsuleGeometry(0.09, 0.45, 6, 12), mat(o.hoodie, { roughness: 0.85 })); lo.position.y = -0.27; lo.castShadow = true; el.add(lo);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.25, 28, 20), mat(0xf6f1ff, { roughness: 0.5 })); hand.position.y = -0.58; hand.castShadow = true; el.add(hand);
    parts.arms.push({ sh, el, hand });
  }
  root.scale.setScalar(o.scale);
  return parts;
}
