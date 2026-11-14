# 특징값 1280개 → 주성분 96개로 줄이고 1바이트(int8)로 압축 → assets/vis/
import json, os, sys, numpy as np
sj, cd, out = sys.argv[1:4]
J = json.load(open(sj, encoding="utf-8")); P = J.get("p", [])
keys = open(f"{cd}/keys.txt", encoding="utf-8").read().split("\n")
E = np.fromfile(f"{cd}/emb.f32", dtype=np.float32).reshape(-1, 1280)[:len(keys)]
pos = {k: i for i, k in enumerate(keys)}
def url(s):
    if not s: return ""
    if s[0] == "~": s = P[int(s[1])] + s[2:]
    return "https:" + s if s.startswith("//") else ("https://www.wwood.co.kr" + s if s.startswith("/") else s)
rows, seen = [], set()
for x in J["d"]:
    u = url(x.get("i", ""))
    if u not in pos or (x["n"], u) in seen: continue
    seen.add((x["n"], u)); rows.append((pos[u], x))
X = E[[r[0] for r in rows]]
X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
mu = X.mean(0); D = 96
_, _, Vt = np.linalg.svd(X - mu, full_matrices=False); W = Vt[:D].T.astype(np.float32)  # 1280×96
Y = (X - mu) @ W; Y /= (np.linalg.norm(Y, axis=1, keepdims=True) + 1e-8)
Q = np.clip(np.round(Y * 127), -127, 127).astype(np.int8)
os.makedirs(out, exist_ok=True)
np.concatenate([mu.astype(np.float32), W.ravel()]).astype(np.float16).tofile(f"{out}/proj.bin")
Q.tofile(f"{out}/items.bin")
it = [{k: x[k] for k in ("n", "i", "s", "c", "l", "d", "u") if x.get(k)} for _, x in rows]
json.dump({"p": P, "dim": D, "d": it}, open(f"{out}/items.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("packed", len(rows), "items")
