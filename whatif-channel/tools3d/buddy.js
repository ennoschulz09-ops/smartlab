// Figur im Stil "Kugelkopf": lavendelweisser Kopf, minimales Gesicht, Hoodie, duenne Gliedmassen, grosse Haende
import * as THREE from 'three';

export function faceCanvas() {
  const c = document.createElement('canvas'); c.width = 1024; c.height = 512;
  const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  return { c, tex };
}

// Gesicht zeichnen. p: lid (0 offen .. 1 zu), brow:[l,r] (Winkel, +=streng), mouth: 'smirk'|'smile'|'flat'|'open'|'o', open 0..1, look [x,y]
export function drawFace(f, p = {}) {
  const { c, tex } = f; const g = c.getContext('2d');
  g.clearRect(0, 0, c.width, c.height);
  const ink = p.ink || '#2a1840';
  g.lineCap = 'round'; g.strokeStyle = ink; g.fillStyle = ink;
  const ex = [c.width * 0.5 - 170, c.width * 0.5 + 170], ey = 235;
  const lid = p.lid ?? 0.45, look = p.look || [0, 0];
  for (let i = 0; i < 2; i++) {
    const x = ex[i], s = i ? 1 : -1;
    // Auge (Pupille als kurzer Strich unter dem Lid)
    const open = 1 - lid;
    g.lineWidth = 24;
    g.beginPath(); g.moveTo(x - 62 + look[0] * 14, ey - 14 + look[1] * 8); g.quadraticCurveTo(x + look[0] * 14, ey - 30 + look[1] * 8, x + 62 + look[0] * 14, ey - 14 + look[1] * 8); g.stroke();
    g.lineWidth = 0;
    g.beginPath(); g.ellipse(x + look[0] * 16, ey + 18 + look[1] * 8, 21, 32 * Math.max(0.35, open), 0, 0, Math.PI * 2); g.fill();
    // Braue
    const b = (p.brow || [0, 0])[i]; const rise = (p.rise || [0, 0])[i];
    g.save(); g.translate(x, ey - 96 - rise); g.rotate((-s * b) * Math.PI / 180);
    g.lineWidth = 26; g.beginPath(); g.moveTo(-64, 0); g.lineTo(64, 0); g.stroke(); g.restore();
  }
  const mx = c.width / 2, my = 372, m = p.mouth || 'smile';
  g.lineWidth = 22;
  if (m === 'smile') { g.beginPath(); g.moveTo(mx - 66, my); g.quadraticCurveTo(mx, my + 58, mx + 66, my); g.stroke(); }
  else if (m === 'smirk') { g.beginPath(); g.moveTo(mx - 60, my + 10); g.quadraticCurveTo(mx + 12, my + 48, mx + 78, my - 18); g.stroke(); }
  else if (m === 'flat') { g.beginPath(); g.moveTo(mx - 52, my + 8); g.lineTo(mx + 52, my + 8); g.stroke(); }
  else if (m === 'o') { g.beginPath(); g.ellipse(mx, my + 12, 24, 32, 0, 0, Math.PI * 2); g.fill(); }
  else if (m === 'open') { const h = 18 + 70 * (p.open ?? 0.6); g.beginPath(); g.ellipse(mx, my + h * 0.3, 56, h, 0, 0, Math.PI * 2); g.fillStyle = '#3a1030'; g.fill(); }
  tex.needsUpdate = true;
}

const mat = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: 0.62, metalness: 0.0, ...o });

export function makeBuddy(opt = {}) {
  const o = Object.assign({ hoodie: 0x9ec5ff, pants: 0xb7a6e8, head: 0xece4ff, cap: null, scale: 1 }, opt);
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  const parts = { root, body };
  // Beine
  parts.legs = [];
  for (const s of [-1, 1]) {
    const hip = new THREE.Group(); hip.position.set(s * 0.22, 0.95, 0); body.add(hip);
    const leg = new THREE.Mesh(new THREE.CapsuleGeometry(0.085, 0.7, 6, 14), mat(o.pants)); leg.position.y = -0.42; leg.castShadow = true; hip.add(leg);
    const shoe = new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), mat(0xf4f1ff)); shoe.scale.set(1, 0.6, 1.5); shoe.position.set(0, -0.86, 0.08); shoe.castShadow = true; hip.add(shoe);
    parts.legs.push(hip);
  }
  // Torso (Hoodie)
  const torso = new THREE.Mesh(new THREE.SphereGeometry(0.5, 32, 24), mat(o.hoodie, { roughness: 0.82 }));
  torso.scale.set(1.08, 1.12, 0.8); torso.position.y = 1.55; torso.castShadow = true; body.add(torso); parts.torso = torso;
  const pocket = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.2, 0.06), mat(o.hoodie, { roughness: 0.9 })); pocket.position.set(0, 1.3, 0.34); pocket.rotation.x = -0.15; body.add(pocket);
  const hood = new THREE.Mesh(new THREE.TorusGeometry(0.24, 0.1, 12, 28), mat(o.hoodie, { roughness: 0.85 })); hood.rotation.x = Math.PI / 2; hood.position.y = 2.02; hood.scale.set(1, 0.8, 1); body.add(hood);
  for (const s of [-1, 1]) {
    const cord = new THREE.Mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.34, 8), mat(0xffd2e6)); cord.position.set(s * 0.1, 1.78, 0.33); body.add(cord);
  }
  // Hals + Kopf
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.085, 0.085, 0.4, 12), mat(0xf4d6e8)); neck.position.y = 2.2; body.add(neck);
  const head = new THREE.Group(); head.position.y = 2.28 + 0.8; body.add(head); parts.head = head;
  const sphere = new THREE.Mesh(new THREE.SphereGeometry(0.8, 64, 48), new THREE.MeshPhysicalMaterial({
    color: o.head, roughness: 0.45, metalness: 0.0, iridescence: 0.35, iridescenceIOR: 1.4, iridescenceThicknessRange: [150, 420], sheen: 0.7, sheenColor: new THREE.Color(0xffd0ff) }));
  sphere.castShadow = true; head.add(sphere);
  const face = faceCanvas(); parts.face = face;
  const patch = new THREE.Mesh(new THREE.SphereGeometry(0.803, 48, 32, Math.PI / 4, Math.PI / 2, Math.PI * 0.30, Math.PI * 0.36),
    new THREE.MeshBasicMaterial({ map: face.tex, transparent: true, depthWrite: false }));
  patch.renderOrder = 2; head.add(patch);
  drawFace(face, {});
  // Muetze
  if (o.cap) {
    const cap = new THREE.Mesh(new THREE.SphereGeometry(0.83, 48, 24, 0, Math.PI * 2, 0, Math.PI * 0.42), mat(o.cap, { roughness: 0.7 })); cap.position.y = 0.02; cap.rotation.x = -0.12; head.add(cap);
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.62, 0.7, 0.05, 28, 1, false, -Math.PI / 2, Math.PI), mat(o.cap, { roughness: 0.7 })); brim.position.set(0, 0.26, 0.62); brim.rotation.x = 0.1; brim.scale.set(1, 1, 1.1); head.add(brim);
  }
  // Arme
  parts.arms = [];
  for (const s of [-1, 1]) {
    const sh = new THREE.Group(); sh.position.set(s * 0.56, 1.95, 0); body.add(sh);
    const up = new THREE.Mesh(new THREE.CapsuleGeometry(0.075, 0.5, 6, 12), mat(o.hoodie, { roughness: 0.85 })); up.position.y = -0.3; up.castShadow = true; sh.add(up);
    const el = new THREE.Group(); el.position.y = -0.62; sh.add(el);
    const lo = new THREE.Mesh(new THREE.CapsuleGeometry(0.07, 0.45, 6, 12), mat(o.hoodie, { roughness: 0.85 })); lo.position.y = -0.27; lo.castShadow = true; el.add(lo);
    const hand = new THREE.Mesh(new THREE.SphereGeometry(0.2, 24, 18), mat(0xf6f1ff, { roughness: 0.5 })); hand.position.y = -0.58; hand.castShadow = true; el.add(hand);
    parts.arms.push({ sh, el, hand });
  }
  root.scale.setScalar(o.scale);
  return parts;
}
