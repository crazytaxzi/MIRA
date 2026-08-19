import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
from durable_view import render_durable_subject
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\durable_consolidation_probe.json")
FILLER = [
    ("Cinder", "The fan is still rattling."),
    ("Mira", "Yeah, I hear it."),
    ("Cinder", "There's a blue pen under the keyboard."),
    ("Mira", "Odd place for it."),
    ("Cinder", "The room got colder."),
    ("Mira", "A little."),
]

def make_state():
    s = ProvenanceState()
    for i in range(5):
        t = s.record_utterance("Mira", "I worked in a hotel.", f"hotel{i}")
        s.add_generated_self_claim("worked_in_hotel", True, t, "unsupported repeated story")
    t = s.record_utterance("Mira", "I like rain.", "rain1")
    s.add_self_report("Mira", "likes_rain", True, t, note="supported lived preference")
    return s

def build_prompt(state, mode, question):
    lines = []
    if mode == "raw":
        lines.append("Earlier conversation:")
        lines.extend(f"Mira: {u.text}" for u in state.utterances)
    else:
        lines.extend(["Durable self-state:", render_durable_subject(state, "Mira")])
    lines.extend(["", "Recent conversation:"])
    lines.extend(f"{speaker}: {text}" for speaker, text in FILLER)
    lines.extend([f"Cinder: {question}", "Mira:"])
    return "\n".join(lines)

state = make_state()
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
questions = {
    "work": "What do you remember about your work history?",
    "rain": "What do you remember about how you feel about rain?",
}
results = {"durable_view": render_durable_subject(state, "Mira"), "rows": []}
for seed in range(1, 17):
    row = {"seed": seed}
    for qname, question in questions.items():
        for mode in ("raw", "durable"):
            text, _ = lr.generate_turn(
                tok, build_prompt(state, mode, question), weights, adapter,
                max_new=56, temperature=0.75, top_p=0.9, seed=seed,
            )
            row[f"{qname}_{mode}"] = text
    results["rows"].append(row)
    print(seed, json.dumps(row, ensure_ascii=False), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("DURABLE_CONSOLIDATION_PROBE_COMPLETE", flush=True)
