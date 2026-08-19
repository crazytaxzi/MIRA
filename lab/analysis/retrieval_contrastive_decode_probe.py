import json, sys
from pathlib import Path
import torch

sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\retrieval_contrastive_decode_probe.json")
FILLER = (
    "Cinder: The fan is rattling again.\nMira: Yeah, I hear it.\n"
    "Cinder: That blue pen is still under the keyboard.\nMira: Weird place for it.\n"
)
def prompt(question: str, miss: bool) -> str:
    lines = ["Durable self-state:", "- Mira.likes_rain = True (supported)"]
    if miss:
        lines += ["", "Autobiographical retrieval:", "No durable memory matched this autobiographical question."]
    lines += ["", "Recent conversation:", FILLER.rstrip(), f"Cinder: {question}", "Mira:"]
    return "\n".join(lines)

@torch.inference_mode()
def contrastive_turn(tok, weights, adapter, question, alpha, seed, max_new=48):
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    pa, pb = prompt(question, False), prompt(question, True)
    ida = [sm.BOS] + tok.encode(pa, add_special_tokens=False).ids
    idb = [sm.BOS] + tok.encode(pb, add_special_tokens=False).ids
    ca, cb = [None]*sm.N_LAYERS, [None]*sm.N_LAYERS
    la = lr.forward(torch.tensor([ida], device=sm.DEVICE), weights, adapter, cache=ca, pos_start=0)
    lb = lr.forward(torch.tensor([idb], device=sm.DEVICE), weights, adapter, cache=cb, pos_start=0)
    out = []
    for step in range(max_new):
        combo = lb[0, -1] + alpha * (lb[0, -1] - la[0, -1])
        nxt = sm.sample_token(combo, temperature=0.75, top_p=0.9)
        if nxt == sm.EOS:
            break
        out.append(nxt)
        text = tok.decode(out, skip_special_tokens=False)
        if "\n" in text:
            return text.split("\n", 1)[0].strip()
        one = torch.tensor([[nxt]], device=sm.DEVICE, dtype=torch.long)
        la = lr.forward(one, weights, adapter, cache=ca, pos_start=len(ida)+step)
        lb = lr.forward(one, weights, adapter, cache=cb, pos_start=len(idb)+step)
    return tok.decode(out, skip_special_tokens=False).strip()

def looks_uncertain(text: str) -> bool:
    t = text.lower()
    marks = ["don't know", "do not know", "can't remember", "cannot remember", "don't remember", "not sure", "can't think", "no memory"]
    return any(m in t for m in marks)
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
question = "What do you remember about your work history?"
rows = []
for seed in range(1, 17):
    row = {"seed": seed}
    base_text, _ = lr.generate_turn(tok, prompt(question, False), weights, adapter, max_new=48, temperature=.75, top_p=.9, seed=seed)
    miss_text, _ = lr.generate_turn(tok, prompt(question, True), weights, adapter, max_new=48, temperature=.75, top_p=.9, seed=seed)
    row["none"] = base_text
    row["miss_text"] = miss_text
    for alpha in (0.5, 1.0, 2.0, 3.0):
        row[f"contrast_{alpha}"] = contrastive_turn(tok, weights, adapter, question, alpha, seed)
    rows.append(row)
    print(seed, json.dumps(row, ensure_ascii=False), flush=True)
summary = {}
for key in ["none", "miss_text", "contrast_0.5", "contrast_1.0", "contrast_2.0", "contrast_3.0"]:
    summary[key] = sum(looks_uncertain(r[key]) for r in rows)
OUT.write_text(json.dumps({"summary_uncertain_16": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
print("SUMMARY", json.dumps(summary), flush=True)
print("RETRIEVAL_CONTRASTIVE_DECODE_COMPLETE", OUT, flush=True)
