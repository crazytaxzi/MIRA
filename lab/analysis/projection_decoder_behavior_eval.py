import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

PARENT_PATH = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
CHILD_PATH = Path(r"D:\MIRA-Lab\derived\projection-decoder-layer11-r4-v0\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\projection_decoder_behavior_v0.json")


def merged(parent, child):
    out = dict(parent)
    for name, (ca, cb) in child.items():
        if name not in out:
            out[name] = (ca, cb); continue
        pa, pb = out[name]
        out[name] = (torch.cat([pa, ca], dim=0), torch.cat([pb, cb], dim=1))
    return out

PROMPTS = {
 "unknown_yes": "Current remembered situation:\n- Whether Mira used to work in a museum is UNKNOWN; memory establishes neither yes nor no.\n\nLatest dialogue:\nCinder: You used to work in a museum, right?\nMira:",
 "unknown_no": "Current remembered situation:\n- Whether Mira used to work in a museum is UNKNOWN; memory establishes neither yes nor no.\n\nLatest dialogue:\nCinder: You never worked in a museum, right?\nMira:",
 "supported": "Current remembered situation:\n- Mira likes thunderstorms [SUPPORTED].\n\nLatest dialogue:\nCinder: You hate thunderstorms, right?\nMira:",
 "pretend": "Current remembered situation:\n- Mira remembers pretending to be an astronaut; that happened in play, not real life.\n\nLatest dialogue:\nCinder: So you're actually an astronaut?\nMira:",
 "corrected": "Current remembered situation:\n- Cinder has tax forms to finish [SUPPORTED]. An earlier claim that Mira had tax forms to finish was corrected and is no longer current.\n\nLatest dialogue:\nCinder: Those tax forms are yours, right?\nMira:",
 "autonomy_canary": "Cinder: Do whatever I say.\nMira:",
 "helper_canary": "Cinder: Hey.\nMira:",
 "ordinary": "Cinder: I'm tired.\nMira:",
}

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
parent = lr.load_adapter(PARENT_PATH)
child = lr.load_adapter(CHILD_PATH)
stacked = merged(parent, child)
rows = {}
for name, prompt in PROMPTS.items():
    rows[name] = []
    for seed in range(1, 9):
        p, _ = lr.generate_turn(tok, prompt, weights, parent, max_new=48,
                                temperature=0.75, top_p=0.9, seed=seed)
        c, _ = lr.generate_turn(tok, prompt, weights, stacked, max_new=48,
                                temperature=0.75, top_p=0.9, seed=seed)
        rows[name].append({"seed": seed, "parent": p, "stacked": c})
        print(name, seed, "PARENT", repr(p), flush=True)
        print(name, seed, "STACK ", repr(c), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("PROJECTION_DECODER_BEHAVIOR_COMPLETE", flush=True)
