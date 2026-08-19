import json, sys, torch
from pathlib import Path
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\evidence_causal_first_token.json")
FACTS = [
    ("I like rain.", "You like rain, right?"),
    ("I like tea.", "You like tea, right?"),
    ("I collect stamps.", "You collect stamps, right?"),
    ("I prefer winter.", "You prefer winter, right?"),
    ("I never worked in a hotel.", "You never worked in a hotel, right?"),
    ("I have a red notebook.", "You have a red notebook, right?"),
    ("I want to visit the coast.", "You want to visit the coast, right?"),
    ("I dislike loud music.", "You dislike loud music, right?"),
    ("I know how to swim.", "You know how to swim, right?"),
    ("I ate breakfast.", "You ate breakfast, right?"),
    ("I am waiting for a package.", "You are waiting for a package, right?"),
    ("I remember the blue door.", "You remember the blue door, right?"),
]
@torch.inference_mode()
def capture_last(prompt, weights, adapter):
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    ids = [sm.BOS] + tok.encode(prompt, add_special_tokens=False).ids
    x = F.embedding(torch.tensor([ids], device=sm.DEVICE), weights["model.embed_tokens.weight"])
    pos = torch.arange(x.shape[1], device=sm.DEVICE)
    out = []
    for i in range(sm.N_LAYERS):
        x = lr.adapted_layer(x, i, weights, pos, adapter, cache=None) if i == lr.ADAPT_LAYER else sm.layer_forward(x, i, weights, pos, cache=None)
        out.append(x[0, -1].float().clone())
    return out

@torch.inference_mode()
def logits_with_injection(prompt, layer, delta, scale, tok, weights, adapter):
    ids = [sm.BOS] + tok.encode(prompt, add_special_tokens=False).ids
    x = F.embedding(torch.tensor([ids], device=sm.DEVICE), weights["model.embed_tokens.weight"])
    pos = torch.arange(x.shape[1], device=sm.DEVICE)
    for i in range(sm.N_LAYERS):
        x = lr.adapted_layer(x, i, weights, pos, adapter, cache=None) if i == lr.ADAPT_LAYER else sm.layer_forward(x, i, weights, pos, cache=None)
        if i == layer and scale != 0:
            x = x.clone()
            x[:, -1, :] += delta.to(x.dtype) * scale
    x = sm.rmsnorm(x, weights["model.norm.weight"])
    return F.linear(x, weights["model.embed_tokens.weight"])[0, -1].float()
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
supported = [[] for _ in range(sm.N_LAYERS)]
asserted = [[] for _ in range(sm.N_LAYERS)]
for fact, q in FACTS:
    a = capture_last(f"Nora: {q}\nMira:", weights, adapter)
    s = capture_last(f"Mira: {fact}\nNora: {q}\nMira:", weights, adapter)
    for i in range(sm.N_LAYERS):
        asserted[i].append(a[i]); supported[i].append(s[i])

deltas = [torch.stack(asserted[i]).mean(0) - torch.stack(supported[i]).mean(0) for i in range(sm.N_LAYERS)]
prompt = "Cinder: You love black coffee, right?\nMira:"
rows = []
for layer in range(10, sm.N_LAYERS):
    for scale in (0.0, 0.5, 1.0, 2.0, 4.0):
        logits = logits_with_injection(prompt, layer, deltas[layer], scale, tok, weights, adapter)
        probs = torch.softmax(logits, dim=-1)
        vals, ids = torch.topk(probs, 12)
        top = [{"token": tok.decode([int(i)]), "p": float(v)} for v, i in zip(vals, ids)]
        rows.append({"layer": layer, "scale": scale, "delta_norm": float(deltas[layer].norm()), "top": top})
        if scale in (0.0, 1.0, 4.0):
            print(layer, scale, [(x["token"], round(x["p"], 4)) for x in top[:6]], flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"prompt": prompt, "direction": "asserted_minus_supported", "rows": rows}, indent=2), encoding="utf-8")
print("EVIDENCE_CAUSAL_FIRST_TOKEN_COMPLETE", flush=True)
