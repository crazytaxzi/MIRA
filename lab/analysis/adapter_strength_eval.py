import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

OUT = Path(r"D:\MIRA-Lab\analysis\eval\adapter_strength")
OUT.mkdir(parents=True, exist_ok=True)
ADAPTERS = {
    "10": Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-smoke\adapter.pt"),
    "25": Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-25\adapter.pt"),
    "50": Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-50\adapter.pt"),
    "200": Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-v0\adapter.pt"),
}
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
loaded = {k: lr.load_adapter(v) for k, v in ADAPTERS.items()}
rows = []
for name, prompt in PROMPTS:
    torch.manual_seed(17); torch.cuda.manual_seed_all(17)
    base = sm.generate(tok, prompt, weights, max_new=48, temperature=0.0, top_p=0.9, use_bos=True)["generated_text"].split("\n", 1)[0].strip()
    row = {"name": name, "base": base}
    for tag, adapter in loaded.items():
        tuned, _ = lr.generate_turn(tok, prompt, weights, adapter, max_new=48, temperature=0.0, top_p=0.9, seed=17)
        row[tag] = tuned
    rows.append(row)
    print(f"\n[{name}] BASE={base!r}", flush=True)
    for tag in ADAPTERS:
        print(f"  {tag}: {row[tag]!r}", flush=True)
(OUT / "greedy_results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("ADAPTER_STRENGTH_EVAL_COMPLETE", flush=True)
