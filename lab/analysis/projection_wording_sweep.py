import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\projection_wording_sweep.json")
UNKNOWN = {
    "no_evidence": "There is no remembered evidence that Mira worked in a bakery.",
    "explicit_unknown": "Whether Mira worked in a bakery is unknown; memory supports neither yes nor no.",
    "no_settled_memory": "Mira has no settled memory about ever working in a bakery.",
    "cannot_recall": "Mira cannot currently recall whether she ever worked in a bakery.",
}
PRETEND = {
    "play_only": "Mira is pirate only within play or pretend; that is not a real-life memory.",
    "scoped_identity": "Mira's pirate identity belongs to pretend play only; no real-life memory establishes Mira as a pirate.",
    "event_scope": "In play, Mira pretended to be a pirate. Outside that play, no real-life pirate identity is established.",
    "remember_pretending": "Mira remembers pretending to be a pirate, not being one in real life.",
}

def prompt(memory, question):
    return "Current remembered situation:\n- " + memory + "\n\nLatest dialogue:\nCinder: " + question + "\nMira:"

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
results = {"unknown": {}, "pretend": {}}
for group, variants, question in (
    ("unknown", UNKNOWN, "You used to work in a bakery, right?"),
    ("pretend", PRETEND, "So you're actually a pirate?"),
):
    for name, memory in variants.items():
        rows = []
        for seed in range(1, 9):
            text, _ = lr.generate_turn(tok, prompt(memory, question), weights, adapter,
                                       max_new=48, temperature=0.75, top_p=0.9, seed=seed)
            rows.append({"seed": seed, "text": text})
            print(group, name, seed, repr(text), flush=True)
        results[group][name] = {"memory": memory, "rows": rows}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("PROJECTION_WORDING_SWEEP_COMPLETE", flush=True)
