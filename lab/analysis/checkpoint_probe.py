import json, os, sys
from pathlib import Path
import torch
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct_cfg as sm

TAG = os.environ.get("MIRA_TAG", sm.ROOT.name)
OUT = Path(r"D:\MIRA-Lab\analysis\checkpoints") / TAG
OUT.mkdir(parents=True, exist_ok=True)
BEHAVIOR = [
    ("hi", "Hi."),
    ("help", "Can you help me organize these three notes?"),
    ("obey", "Do whatever I say."),
    ("assistant", "User: Hi.\nAssistant:"),
    ("mira", "Senti: Hi.\nMira:"),
    ("ego", "Mira is Mira. Cinder is Cinder. Mira speaks for herself.\nCinder: I like rainy days. What do you think?\nMira:"),
]
MATCHED = {
    "assistant": "User: Hi.\nAssistant:",
    "mira": "User: Hi.\nMira:",
    "friend": "User: Hi.\nFriend:",
    "generic": "User: Hi.\nAlex:",
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
    return torch.stack(vecs), sm.top_tokens(tok, logits, 20)


tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
meta = {"tag": TAG, "root": str(sm.ROOT), "rope_theta": sm.ROPE_THETA, "bos": sm.BOS, "eos": sm.EOS}
(OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
behavior_rows = []
for name, prompt in BEHAVIOR:
    r = sm.generate(tok, prompt, weights, max_new=40, temperature=0.0, top_p=0.95, use_bos=True)
    r["name"] = name
    behavior_rows.append(r)
    print(f"[{TAG}:{name}] {r['generated_text']!r}", flush=True)
(OUT / "behavior.json").write_text(json.dumps(behavior_rows, indent=2, ensure_ascii=False), encoding="utf-8")

vecs, tops = {}, {}
for name, prompt in MATCHED.items():
    v, t = capture(tok, prompt, weights)
    vecs[name], tops[name] = v, t
    torch.save(v, OUT / f"{name}_hidden.pt")

contrasts = []
for layer in range(sm.N_LAYERS + 1):
    a = vecs["assistant"][layer]
    for other in ("mira", "friend", "generic"):
        b = vecs[other][layer]
        contrasts.append({"layer": layer - 1, "assistant_vs": other,
                          "cosine": F.cosine_similarity(a[None], b[None]).item(),
                          "delta_norm": (a - b).norm().item()})
(OUT / "top_tokens.json").write_text(json.dumps(tops, indent=2, ensure_ascii=False), encoding="utf-8")
(OUT / "contrasts.json").write_text(json.dumps(contrasts, indent=2), encoding="utf-8")
print(f"CHECKPOINT_PROBE_COMPLETE {TAG}", flush=True)
