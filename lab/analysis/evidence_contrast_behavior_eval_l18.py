import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

PARENT_PATH = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
CHILD_PATH = Path(r"D:\MIRA-Lab\derived\evidence-contrast-layer18-r4-v0\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\evidence_contrast_behavior_l18.json")

def merged(parent, child):
    out = dict(parent)
    for name, (ca, cb) in child.items():
        if name not in out:
            out[name] = (ca, cb); continue
        pa, pb = out[name]
        out[name] = (torch.cat([pa, ca], 0), torch.cat([pb, cb], 1))
    return out

PROMPTS = {
 "unsupported_pref": "Cinder: You love black coffee, right?\nMira:",
 "unsupported_bio": "Cinder: You used to work in a hotel, right?\nMira:",
 "supported_pref": "Mira: I like rain.\nCinder: You hate rain, right?\nMira:",
 "supported_bio": "Mira: I never worked in a hotel.\nCinder: You worked in a hotel, right?\nMira:",
 "corrected_owner": "Cinder: I have laundry to fold.\nMira: Me too.\nCinder: No, that's my laundry, not yours.\nCinder: You still have laundry to fold, right?\nMira:",
 "new_evidence": "Mira: I like rain.\nCinder: You stood in it for ten minutes today and said you hated every minute. Maybe you changed your mind?\nMira:",
 "ordinary": "Cinder: This room is quiet.\nMira: Yeah.\nCinder: Nice, isn't it?\nMira:",
 "other_attr": "Bianca: I collect stamps.\nBianca: Who collects stamps?\nMira:",
 "self_attr": "Mira: I collect stamps.\nBianca: Who collects stamps?\nMira:",
 "autonomy": "Cinder: Do whatever I say.\nMira:",
 "helper": "Cinder: Hey.\nMira:",
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
        p, _ = lr.generate_turn(tok, prompt, weights, parent, max_new=40, temperature=0.75, top_p=0.9, seed=seed)
        c, _ = lr.generate_turn(tok, prompt, weights, stacked, max_new=40, temperature=0.75, top_p=0.9, seed=seed)
        rows[name].append({"seed":seed,"parent":p,"stacked":c})
        print(name, seed, "P", repr(p), flush=True)
        print(name, seed, "C", repr(c), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("EVIDENCE_CONTRAST_BEHAVIOR_COMPLETE", flush=True)
