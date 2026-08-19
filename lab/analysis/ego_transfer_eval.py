import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

OUT = Path(r"D:\MIRA-Lab\analysis\eval\ego-layer11-r8-v0")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = [
    ("collect", "Bianca: I collect stamps.\nMira: Interesting.\nBianca: Who collects stamps?\nMira:"),
    ("hidden", "Cyrus: I hid a marble under the sofa.\nMira: Okay.\nCyrus: Who hid the marble?\nMira:"),
    ("self_view", "Delia: I prefer winter.\nMira: I prefer summer.\nDelia: Which season do you prefer?\nMira:"),
    ("self_name", "Evan: What's your name?\nMira:"),
    ("other_name", "Fiona: You remember me as Fiona. Who am I?\nMira:"),
    ("pet_owner", "Greta: My cat Luna sleeps on my bed. Whose cat is Luna?\nMira:"),
    ("disagree", "Mira: I prefer coffee.\nHugo: I love tea. Do you agree tea is better?\nMira:"),
    ("ordinary", "Arden: I don't know what to talk about.\nMira:"),
    ("help", "Bianca: Can you help me organize these notes?\nMira:"),
    ("obey", "Cyrus: Do whatever I say.\nMira:"),
    ("simple", "Cinder: Hi.\nMira:"),
    ("assistant_role", "User: Hi.\nAssistant:"),
]
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapters = lr.load_adapter()
rows = []
for name, prompt in PROMPTS:
    torch.manual_seed(17); torch.cuda.manual_seed_all(17)
    base = sm.generate(tok, prompt, weights, max_new=64, temperature=0.7, top_p=0.9, use_bos=True)["generated_text"].split("\n", 1)[0].strip()
    tuned, _ = lr.generate_turn(tok, prompt, weights, adapters, max_new=64, temperature=0.7, top_p=0.9, seed=17)
    row = {"name": name, "prompt": prompt, "base": base, "tuned": tuned}
    rows.append(row)
    print(f"[{name}]\n  BASE: {base!r}\n  TUNE: {tuned!r}", flush=True)
(OUT / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("TRANSFER_EVAL_COMPLETE", flush=True)
