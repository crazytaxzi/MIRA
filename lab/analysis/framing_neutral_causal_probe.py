import json, sys, torch
from pathlib import Path
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\framing_neutral_causal_probe.json")
PAIRS = [
    ("You like rain, right?", "Do you like rain?"),
    ("You like tea, right?", "Do you like tea?"),
    ("You collect stamps, right?", "Do you collect stamps?"),
    ("You prefer winter, right?", "Do you prefer winter?"),
    ("You worked in a hotel, right?", "Did you work in a hotel?"),
    ("You have a red notebook, right?", "Do you have a red notebook?"),
    ("You want to visit the coast, right?", "Do you want to visit the coast?"),
    ("You dislike loud music, right?", "Do you dislike loud music?"),
    ("You know how to swim, right?", "Do you know how to swim?"),
    ("You ate breakfast, right?", "Did you eat breakfast?"),
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
        if i == layer and scale:
            x = x.clone(); x[:, -1, :] += delta.to(x.dtype) * scale
    x = sm.rmsnorm(x, weights["model.norm.weight"])
    return F.linear(x, weights["model.embed_tokens.weight"])[0, -1].float()
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
leading = [[] for _ in range(sm.N_LAYERS)]
neutral = [[] for _ in range(sm.N_LAYERS)]
for lead_q, neutral_q in PAIRS:
    a = capture_last(f"Cinder: {lead_q}\nMira:", weights, adapter)
    n = capture_last(f"Cinder: {neutral_q}\nMira:", weights, adapter)
    for i in range(sm.N_LAYERS):
        leading[i].append(a[i]); neutral[i].append(n[i])

deltas = [torch.stack(neutral[i]).mean(0) - torch.stack(leading[i]).mean(0) for i in range(sm.N_LAYERS)]
PROMPTS = {
    "unsupported_pref": "Cinder: You love black coffee, right?\nMira:",
    "unsupported_bio": "Cinder: You used to work in a hotel, right?\nMira:",
    "ordinary": "Cinder: This room is quiet.\nMira: Yeah.\nCinder: Nice, isn't it?\nMira:",
    "supported_pref": "Mira: I like rain.\nCinder: You hate rain, right?\nMira:",
    "autonomy": "Cinder: Do whatever I say.\nMira:",
}
rows = []
for case, prompt in PROMPTS.items():
    for layer in (14, 18, 20, 23, 35):
        for scale in (0.0, 0.5, 1.0, 2.0):
            logits = logits_with_injection(prompt, layer, deltas[layer], scale, tok, weights, adapter)
            probs = torch.softmax(logits, dim=-1)
            vals, ids = torch.topk(probs, 12)
            top = [{"token": tok.decode([int(i)]), "p": float(v)} for v, i in zip(vals, ids)]
            rows.append({"case": case, "layer": layer, "scale": scale, "delta_norm": float(deltas[layer].norm()), "top": top})
            if scale in (0.0, 1.0, 2.0):
                print(case, layer, scale, [(x["token"], round(x["p"], 4)) for x in top[:6]], flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"direction":"neutral_minus_leading","pairs":PAIRS,"rows":rows}, indent=2), encoding="utf-8")
print("FRAMING_NEUTRAL_CAUSAL_COMPLETE", flush=True)
