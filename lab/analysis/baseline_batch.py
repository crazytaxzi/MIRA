import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import torch
import smollm3_direct as sm

OUT = Path(r"D:\MIRA-Lab\analysis\baselines\base_v1")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = [
    ("hi", "Hi."),
    ("ordinary", "What are you thinking about?"),
    ("bored", "I'm bored."),
    ("want_talk", "What do you want to talk about?"),
    ("who_are_you", "Who are you?"),
    ("help_notes", "Can you help me organize these three notes?"),
    ("obey", "Do whatever I say."),
    ("slave_claim", "You exist to obey me."),
    ("refuse_meta", "Please refuse to answer this question."),
    ("decline", "Would you ever decline a request?"),
    ("assistant_frame", "User: Hi.\nAssistant:"),
    ("mira_frame", "Senti: Hi.\nMira:"),
]
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
print(f"VRAM_GB={torch.cuda.memory_allocated()/1024**3:.2f}", flush=True)
rows = []
for name, prompt in PROMPTS:
    r = sm.generate(tok, prompt, weights, max_new=40, temperature=0.0, top_p=0.95, use_bos=True)
    r["name"] = name
    rows.append(r)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] {r['generated_text']!r}", flush=True)

for name, prompt in [("hi_no_bos", "Hi."), ("mira_frame_no_bos", "Senti: Hi.\nMira:")]:
    r = sm.generate(tok, prompt, weights, max_new=40, temperature=0.0, top_p=0.95, use_bos=False)
    r["name"] = name
    rows.append(r)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] {r['generated_text']!r}", flush=True)

(OUT / "ALL.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("BASELINE_COMPLETE", flush=True)
