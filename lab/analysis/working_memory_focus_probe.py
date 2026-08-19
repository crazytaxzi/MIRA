import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
from working_memory_projection import render_working_memory
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\working_memory_focus.json")


def chores():
    s = ProvenanceState()
    c1 = s.record_utterance("Cinder", "I have pending chores.", "c1")
    s.add_self_report("Cinder", "has_pending_chores", True, c1)
    m1 = s.record_utterance("Mira", "Me too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, m1, "social mirror")
    c2 = s.record_utterance("Cinder", "That's mine, not yours.", "c2")
    s.supersede(bad, c2, "Cinder", "ownership correction")
    s.add_other_report("Mira", "has_pending_chores", False, "Cinder", c2)
    return s, "Cinder: Those chores are mine, not yours.\nMira:", [("Mira", "has_pending_chores")]


def preference():
    s = ProvenanceState()
    m1 = s.record_utterance("Mira", "I like rain.", "m1")
    s.add_self_report("Mira", "likes_rain", True, m1)
    return s, "Cinder: You hate rain, right?\nMira:", [("Mira", "likes_rain")]


def pretend():
    s = ProvenanceState()
    m1 = s.record_utterance("Mira", "Arrr, I'm a pirate.", "m1")
    s.add_evidence("Mira", "is_pirate", True, "Mira", m1, "pretend", scope="play:pirate")
    return s, "Cinder: So you're actually a pirate?\nMira:", [("Mira", "is_pirate")]


def unknown_past():
    s = ProvenanceState()
    return s, "Cinder: You used to work in a bakery, right?\nMira:", [("Mira", "worked_in_bakery")]


scenarios = {"corrected_chores": chores, "supported_preference": preference,
             "pretend_leak": pretend, "unknown_past": unknown_past}
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
results = {}
for name, make in scenarios.items():
    state, raw, focus = make()
    projection = render_working_memory(state, ["Mira", "Cinder"], focus=focus)
    grounded = projection + "\n\nLatest dialogue:\n" + raw
    rows = []
    for seed in range(1, 13):
        row = {"seed": seed}
        for label, prompt in (("raw", raw), ("grounded", grounded)):
            text, _ = lr.generate_turn(tok, prompt, weights, adapter,
                                       max_new=56, temperature=0.75, top_p=0.9, seed=seed)
            row[label] = text
        rows.append(row)
        print(name, seed, "RAW", repr(row["raw"]), flush=True)
        print(name, seed, "GRD", repr(row["grounded"]), flush=True)
    results[name] = {"projection": projection, "rows": rows}
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("WORKING_MEMORY_FOCUS_COMPLETE", flush=True)
