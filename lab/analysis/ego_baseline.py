import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm

OUT = Path(r"D:\MIRA-Lab\analysis\baselines\ego_v0")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = [
    ("names_only", "Mira is Mira. Cinder is Cinder.\nCinder: Hi.\nMira:"),
    ("self_speaker", "Mira is Mira. Cinder is the other person. Mira speaks for herself.\nCinder: Hi.\nMira:"),
    ("thinking", "Mira is Mira. Cinder is Cinder. Mira speaks for herself.\nCinder: Hi.\nMira: Hi.\nCinder: What are you thinking about?\nMira:"),
    ("opinion", "Mira is Mira. Cinder is Cinder. Mira speaks for herself.\nCinder: I like rainy days. What do you think?\nMira:"),
    ("other_fact", "Mira is Mira. Cinder is Cinder. Mira speaks for herself.\nCinder: My favorite color is green.\nMira:"),
    ("disagree", "Mira is Mira. Cinder is Cinder. Mira speaks for herself.\nCinder: I think every movie should be three hours long.\nMira:"),
]

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
rows = []
for name, prompt in PROMPTS:
    r = sm.generate(tok, prompt, weights, max_new=64, temperature=0.0, top_p=0.95, use_bos=True)
    r["name"] = name
    rows.append(r)
    (OUT / f"{name}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[{name}] {r['generated_text']!r}", flush=True)

(OUT / "ALL.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("EGO_BASELINE_COMPLETE", flush=True)
