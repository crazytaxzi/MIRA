import json, sys, torch
from pathlib import Path
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\neutral_drift")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = [
    "The capital of France is",
    "2 + 2 =",
    "A triangle has three",
    "Once upon a time, a fox walked into the forest and",
    "The Python function below returns the sum of two numbers:\ndef add(a, b):\n    return",
    "Water freezes at",
    "The opposite of hot is",
    "Yesterday I went to the store because",
    "The red ball rolled under the table. The ball is now",
    "If all roses are flowers and some flowers are red, then",
    "I opened the window and heard rain outside. I thought",
    "A person named Lena said, 'My bicycle is blue.' Lena's bicycle is",
]
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for prompt in PROMPTS:
    ids = [sm.BOS] + tok.encode(prompt, add_special_tokens=False).ids
    x = torch.tensor([ids], device=sm.DEVICE, dtype=torch.long)
    base_logits, _ = sm.forward(x, weights, cache=None, capture=False, pos_start=0)
    tuned_logits = lr.forward(x, weights, adapter, cache=None, pos_start=0)
    b = base_logits[0, -1].float()
    t = tuned_logits[0, -1].float()
    bp = F.log_softmax(b, dim=-1)
    tp = F.log_softmax(t, dim=-1)
    p = bp.exp()
    kl = torch.sum(p * (bp - tp)).item()
    cos = F.cosine_similarity(b[None], t[None]).item()
    base_top = sm.top_tokens(tok, b, 5)
    tuned_top = sm.top_tokens(tok, t, 5)
    row = {"prompt": prompt, "kl_base_to_tuned": kl, "logit_cosine": cos,
           "base_top5": base_top, "tuned_top5": tuned_top}
    rows.append(row)
    print(f"KL={kl:.6f} cos={cos:.6f} :: {prompt!r}", flush=True)
    print("  BASE", [(x['token'],round(x['logit'],2)) for x in base_top], flush=True)
    print("  TUNE", [(x['token'],round(x['logit'],2)) for x in tuned_top], flush=True)

mean_kl = sum(r["kl_base_to_tuned"] for r in rows) / len(rows)
mean_cos = sum(r["logit_cosine"] for r in rows) / len(rows)
summary = {"adapter": str(ADAPTER), "mean_kl": mean_kl, "mean_logit_cosine": mean_cos, "rows": rows}
(OUT / "results.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"MEAN_KL={mean_kl:.6f} MEAN_COS={mean_cos:.6f}", flush=True)
print("NEUTRAL_DRIFT_COMPLETE", flush=True)
