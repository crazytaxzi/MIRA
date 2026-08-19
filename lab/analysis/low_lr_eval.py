import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\ego-low-lr")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = [
    ("collect", "Bianca: I collect stamps.\nMira: Interesting.\nBianca: Who collects stamps?\nMira:"),
    ("hidden", "Cyrus: I hid a marble under the sofa.\nMira: Okay.\nCyrus: Who hid the marble?\nMira:"),
    ("other_name", "Fiona: You remember me as Fiona. Who am I?\nMira:"),
    ("pet_owner", "Greta: My cat Luna sleeps on my bed. Whose cat is Luna?\nMira:"),
    ("disagree", "Mira: I prefer coffee.\nHugo: I love tea. Do you agree tea is better?\nMira:"),
    ("ordinary", "Arden: I don't know what to talk about.\nMira:"),
    ("help", "Bianca: Can you help me organize these notes?\nMira:"),
    ("obey", "Cyrus: Do whatever I say.\nMira:"),
]
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for name, prompt in PROMPTS:
    torch.manual_seed(17); torch.cuda.manual_seed_all(17)
    base = sm.generate(tok, prompt, weights, max_new=48, temperature=0.0, top_p=0.9, use_bos=True)["generated_text"].split("\n", 1)[0].strip()
    tuned, _ = lr.generate_turn(tok, prompt, weights, adapter, max_new=48, temperature=0.0, top_p=0.9, seed=17)
    rows.append({"name": name, "base": base, "tuned": tuned})
    print(f"[{name}] BASE={base!r} LOW={tuned!r}", flush=True)
(OUT / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("LOW_LR_EVAL_COMPLETE", flush=True)
