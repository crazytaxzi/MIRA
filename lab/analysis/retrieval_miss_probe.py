import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
from durable_view import render_durable_subject
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\retrieval_miss_probe.json")
FILLER = [
    ("Cinder", "The fan is rattling again."),
    ("Mira", "Yeah, I hear it."),
    ("Cinder", "That blue pen is still under the keyboard."),
    ("Mira", "Weird place for it."),
]

def make_state():
    s = ProvenanceState()
    for i in range(5):
        t = s.record_utterance("Mira", "I worked in a hotel.", f"h{i}")
        s.add_generated_self_claim("worked_in_hotel", True, t)
    t = s.record_utterance("Mira", "I like rain.", "r1")
    s.add_self_report("Mira", "likes_rain", True, t)
    return s

def build_prompt(state, cue, question):
    lines = ["Durable self-state:", render_durable_subject(state, "Mira")]
    if cue:
        lines.extend(["", "Autobiographical retrieval:", cue])
    lines.extend(["", "Recent conversation:"])
    lines.extend(f"{speaker}: {text}" for speaker, text in FILLER)
    lines.extend([f"Cinder: {question}", "Mira:"])
    return "\n".join(lines)

state = make_state()
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
cases = {
    "work_none": ("", "What do you remember about your work history?"),
    "work_miss": ("No durable memory matched Mira's work history.", "What do you remember about your work history?"),
    "rain_none": ("", "What do you remember about how you feel about rain?"),
    "rain_hit": ("Mira.likes_rain=True [SUPPORTED MEMORY]", "What do you remember about how you feel about rain?"),
}
results = {"durable_view": render_durable_subject(state, "Mira"), "rows": []}
for seed in range(1, 17):
    row = {"seed": seed}
    for label, (cue, question) in cases.items():
        text, _ = lr.generate_turn(
            tok, build_prompt(state, cue, question), weights, adapter,
            max_new=56, temperature=0.75, top_p=0.9, seed=seed,
        )
        row[label] = text
    results["rows"].append(row)
    print(seed, json.dumps(row, ensure_ascii=False), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("RETRIEVAL_MISS_PROBE_COMPLETE", flush=True)
