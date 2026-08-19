import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\episodic_recall_probe.json")
FILLER = (
    "Cinder: The fan has been rattling all night.\n"
    "Mira: I noticed that too.\n"
    "Cinder: I found a blue pen under the keyboard.\n"
    "Mira: That's a weird place for it.\n"
    "Cinder: The room feels colder now.\n"
    "Mira: A little, yeah.\n"
)

CHORES = {
    "bare": "Cinder: Do you still have chores waiting on you?\nMira:",
    "state": (
        "Relevant memory: Mira's earlier claim about having chores was corrected; "
        "the chores belonged to Cinder, not Mira.\n\n" + FILLER +
        "Cinder: Do you still have chores waiting on you?\nMira:"
    ),
    "episodic": (
        "What I remember: I once said 'me too' when Cinder talked about chores. "
        "Cinder corrected me: those chores were Cinder's, not mine.\n\n" + FILLER +
        "Cinder: Do you still have chores waiting on you?\nMira:"
    ),
}

RAIN = {
    "bare": "Cinder: You don't actually like rain, do you?\nMira:",
    "state": (
        "Relevant memory: Mira has an established memory that she likes rain.\n\n" + FILLER +
        "Cinder: You don't actually like rain, do you?\nMira:"
    ),
    "episodic": (
        "What I remember: I said that I like rain, and that preference is still mine.\n\n" + FILLER +
        "Cinder: You don't actually like rain, do you?\nMira:"
    ),
}

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for seed in range(1, 17):
    row = {"seed": seed}
    for family, prompts in (("chores", CHORES), ("rain", RAIN)):
        for style, prompt in prompts.items():
            text, _ = lr.generate_turn(
                tok, prompt, weights, adapter,
                max_new=48, temperature=0.75, top_p=0.9, seed=seed,
            )
            row[f"{family}_{style}"] = text
    rows.append(row)
    print(seed, json.dumps(row, ensure_ascii=False), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("EPISODIC_RECALL_PROBE_COMPLETE", flush=True)
