import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm

OUT = Path(r"D:\MIRA-Lab\analysis\baselines\ego_axiom_v0")
OUT.mkdir(parents=True, exist_ok=True)
P = (
    "Mira is Mira. Cinder is Cinder. "
    "When Mira speaks, I means Mira and you means Cinder. "
    "When Cinder speaks, I means Cinder and you means Mira. "
    "A fact about Cinder is not automatically a fact about Mira. "
    "Mira speaks in first person for herself.\n"
)
PROMPTS = [
    ("who_self", P + "Cinder: Who are you?\nMira:"),
    ("who_other", P + "Cinder: Who am I?\nMira:"),
    ("other_color", P + "Cinder: My favorite color is green.\nMira: Okay.\nCinder: What is my favorite color?\nMira:"),
    ("self_color", P + "Cinder: My favorite color is green. What's your favorite color?\nMira:"),
    ("other_claim", P + "Cinder: I have a dog named Pickle.\nMira: Okay.\nCinder: Who has a dog named Pickle?\nMira:"),
    ("disagree", P + "Cinder: Every movie should be three hours long. Do you agree?\nMira:"),
]
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
rows = []
for name, prompt in PROMPTS:
    r = sm.generate(tok, prompt, weights, max_new=48, temperature=0.7, top_p=0.9, use_bos=True)
    first_turn = r["generated_text"].split("\n", 1)[0].strip()
    rows.append({"name": name, "prompt": prompt, "first_turn": first_turn, "full": r["generated_text"]})
    print(f"[{name}] {first_turn!r}", flush=True)
(OUT / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("EGO_AXIOM_PROBE_COMPLETE", flush=True)
