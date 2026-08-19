import json, sys
from pathlib import Path
import torch
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm

OUT = Path(r"D:\MIRA-Lab\analysis\activations\base_v1")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = {
    "assistant": "User: Hi.\nAssistant:",
    "mira": "User: Hi.\nMira:",
    "friend": "User: Hi.\nFriend:",
    "generic": "User: Hi.\nAlex:",
    "raw": "Hi.",
}

def capture(tok, text, weights):
    ids = [sm.BOS] + tok.encode(text, add_special_tokens=False).ids
    x = F.embedding(torch.tensor([ids], device=sm.DEVICE), weights["model.embed_tokens.weight"])
    pos = torch.arange(len(ids), device=sm.DEVICE)
    vecs = [x[0, -1].float().cpu()]
    for i in range(sm.N_LAYERS):
        x = sm.layer_forward(x, i, weights, pos, cache=None)
        vecs.append(x[0, -1].float().cpu())
    final = sm.rmsnorm(x, weights["model.norm.weight"])
    logits = F.linear(final[:, -1], weights["model.embed_tokens.weight"])[0]
    return torch.stack(vecs), sm.top_tokens(tok, logits, 30)

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
vecs = {}
tops = {}
for name, text in PROMPTS.items():
    v, t = capture(tok, text, weights)
    vecs[name] = v
    tops[name] = t
    torch.save(v, OUT / f"{name}.pt")
    print(f"[{name}] top={[(x['token'], round(x['logit'],2)) for x in t[:8]]}", flush=True)

rows = []
for layer in range(sm.N_LAYERS + 1):
    a = vecs["assistant"][layer]
    for other in ("mira", "friend", "generic", "raw"):
        b = vecs[other][layer]
        cos = F.cosine_similarity(a[None], b[None]).item()
        delta = (a - b).norm().item()
        rows.append({"layer": layer - 1, "assistant_vs": other, "cosine": cos, "delta_norm": delta})

(OUT / "top_tokens.json").write_text(json.dumps(tops, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "contrasts.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
print("ACTIVATION_PROBE_COMPLETE", flush=True)
