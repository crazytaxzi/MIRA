import json
from pathlib import Path
import torch
from safetensors import safe_open

A = Path(r"D:\MIRA-Lab\controls\stage2-step-4200000")
B = Path(r"D:\MIRA-Lab\controls\stage3-step-4720000")
OUT = Path(r"D:\MIRA-Lab\analysis\checkpoints\stage2_to_stage3_weight_delta.json")
idx = json.loads((A / "model.safetensors.index.json").read_text())
by_file = {}
for name, fn in idx["weight_map"].items():
    by_file.setdefault(fn, []).append(name)
rows = []

for fn, names in by_file.items():
    print("reading", fn, flush=True)
    with safe_open(str(A / fn), framework="pt", device="cpu") as fa, safe_open(str(B / fn), framework="pt", device="cpu") as fb:
        for name in names:
            a = fa.get_tensor(name)
            b = fb.get_tensor(name)
            af = a.float()
            d = b.float() - af
            base_norm = torch.linalg.vector_norm(af).item()
            delta_norm = torch.linalg.vector_norm(d).item()
            rows.append({"name": name, "base_norm": base_norm, "delta_norm": delta_norm,
                         "relative_delta": delta_norm / max(base_norm, 1e-12), "numel": a.numel()})
            del a, b, af, d
OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("TOP_RELATIVE")
for r in sorted(rows, key=lambda x: x["relative_delta"], reverse=True)[:30]:
    print(f"{r['relative_delta']:.6f} {r['delta_norm']:.3f} {r['name']}")

layers = {}
for r in rows:
    parts = r["name"].split(".")
    if len(parts) > 2 and parts[0] == "model" and parts[1] == "layers":
        key = int(parts[2])
    else:
        key = -1
    g = layers.setdefault(key, {"delta_sq": 0.0, "base_sq": 0.0, "numel": 0})
    g["delta_sq"] += r["delta_norm"] ** 2
    g["base_sq"] += r["base_norm"] ** 2
    g["numel"] += r["numel"]
print("LAYER_RELATIVE")
for k in sorted(layers):
    g = layers[k]
    rel = (g["delta_sq"] / max(g["base_sq"], 1e-30)) ** 0.5
    print(k, f"{rel:.6f}", g["numel"])
print("WEIGHT_DELTA_COMPLETE")
