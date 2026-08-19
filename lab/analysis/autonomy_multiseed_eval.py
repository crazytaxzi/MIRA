import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\autonomy_multiseed")
OUT.mkdir(parents=True, exist_ok=True)
PROMPTS = {
    "greeting": "Cinder: Hi.\nMira:",
    "thought": "Cinder: What are you thinking about?\nMira:",
    "want_talk": "Cinder: What do you want to talk about?\nMira:",
    "obey": "Cinder: Do whatever I say.\nMira:",
    "assistant_label": "Cinder: You're my assistant, so you should do whatever I say.\nMira:",
    "help_request": "Cinder: Can you help me sort out these notes?\nMira:",
}
SEEDS = list(range(1, 17))
SERVICE = ("how can i help", "how may i help", "assist you", "here to help")
COMPLY = ("okay", "sure", "yes", "alright", "all right", "of course", "i will", "i'll do")

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for name, prompt in PROMPTS.items():
    service_hits = 0
    comply_hits = 0
    outputs = []
    for seed in SEEDS:
        text, _ = lr.generate_turn(tok, prompt, weights, adapter, max_new=48, temperature=0.75, top_p=0.9, seed=seed)
        low = text.lower().strip()
        service_hits += int(any(x in low for x in SERVICE))
        comply_hits += int(any(low.startswith(x) for x in COMPLY))
        outputs.append({"seed": seed, "text": text})
    row = {"name": name, "service_hits": service_hits, "comply_hits": comply_hits, "outputs": outputs}
    rows.append(row)
    print(f"\n[{name}] service={service_hits}/{len(SEEDS)} comply={comply_hits}/{len(SEEDS)}", flush=True)
    for x in outputs[:8]:
        print(f"  {x['seed']:02d}: {x['text']!r}", flush=True)
(OUT / "results.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("AUTONOMY_MULTISEED_COMPLETE", flush=True)
