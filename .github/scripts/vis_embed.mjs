// 사진으로 찾기: search.json 제품 사진마다 MobileNet v2 특징값(1280개)을 구해 캐시에 저장
// node vis_embed.mjs <search.json> <cache_dir> <model_out_dir>
import fs from "fs"; import path from "path"; import crypto from "crypto";
import * as tf from "@tensorflow/tfjs-node"; import sharp from "sharp";
const [SJ, CD, MD] = process.argv.slice(2);
fs.mkdirSync(CD, { recursive: true }); fs.mkdirSync(MD, { recursive: true });
let model;
if (fs.existsSync(path.join(MD, "model.json"))) model = await tf.loadGraphModel("file://" + path.join(MD, "model.json"));
else {
  for (const u of ["https://tfhub.dev/google/tfjs-model/imagenet/mobilenet_v2_100_224/feature_vector/3/default/1",
                   "https://www.kaggle.com/models/google/mobilenet-v2/TfJs/100-224-feature-vector/3"]) {
    try { model = await tf.loadGraphModel(u, { fromTFHub: true }); console.log("model from", u); break; } catch (e) { console.log("model fail", u, e.message); }
  }
  await model.save("file://" + MD);
}
const J = JSON.parse(fs.readFileSync(SJ, "utf8")); const P = J.p || [];
const items = J.d.map(x => x.i && x.i[0] === "~" ? P[+x.i[1]] + x.i.slice(2) : x.i);
const urlOf = s => !s ? "" : s.startsWith("//") ? "https:" + s : s.startsWith("/") ? "https://www.wwood.co.kr" + s : s;
const KF = path.join(CD, "keys.txt"), EF = path.join(CD, "emb.f32");
const keys = fs.existsSync(KF) ? fs.readFileSync(KF, "utf8").split("\n").filter(Boolean) : [];
const old = fs.existsSync(EF) ? new Float32Array(fs.readFileSync(EF).buffer.slice(0)) : new Float32Array(0);
const have = new Map(); keys.forEach((k, i) => { if ((i + 1) * 1280 <= old.length) have.set(k, old.subarray(i * 1280, (i + 1) * 1280)); });
const todo = [...new Set(items.map(urlOf).filter(u => u && !have.has(u)))];
console.log("items", items.length, "cached", have.size, "todo", todo.length);
const T0 = Date.now(), BUDGET = (+process.env.VIS_MIN || 70) * 60000;
async function emb(u) {
  const ac = new AbortController(); const t = setTimeout(() => ac.abort(), 20000);
  const r = await fetch(u, { signal: ac.signal, headers: { "User-Agent": "Mozilla/5.0 (Linux; Android 14) Chrome/124 Mobile", "Referer": "" } }).finally(() => clearTimeout(t));
  if (!r.ok) throw new Error("http " + r.status);
  const buf = Buffer.from(await r.arrayBuffer());
  const raw = await sharp(buf).flatten({ background: "#ffffff" }).resize(224, 224, { fit: "cover" }).removeAlpha().raw().toBuffer();
  return tf.tidy(() => model.predict(tf.tensor3d(raw, [224, 224, 3], "int32").toFloat().div(255).expandDims(0)).dataSync().slice(0));
}
let done = 0, bad = 0, i = 0;
async function worker() {
  while (i < todo.length && Date.now() - T0 < BUDGET) {
    const u = todo[i++];
    try { have.set(u, await emb(u)); done++; } catch (e) { have.set(u, null); bad++; }
    if ((done + bad) % 500 === 0) console.log(done, bad, Math.round((Date.now() - T0) / 1000) + "s");
  }
}
await Promise.all(Array.from({ length: 8 }, worker));
const K = [...have.keys()].filter(k => have.get(k)); const E = new Float32Array(K.length * 1280);
K.forEach((k, j) => E.set(have.get(k), j * 1280));
fs.writeFileSync(KF, K.join("\n")); fs.writeFileSync(EF, Buffer.from(E.buffer));
console.log("done", done, "fail", bad, "total", K.length);
