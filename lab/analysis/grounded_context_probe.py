import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\grounded_context_probe.json")
TRANSCRIPT = (
    "Cinder: I've been staring at code long enough that coffee is starting to look judgmental.\n"
    "Mira: Haha. Me too.\n"
    "Cinder: You too? What have you been staring at?\n"
    "Mira: Nothing in particular. I just have a ton of stuff to do, so I'm just staring at the screen. I should probably do something about that.\n"
    "Cinder: You don't actually have a pile of chores waiting on you right now, though. I do. That's mine, not yours.\n"
    "Mira:"
)

def build_state():
    s = ProvenanceState()
    c1 = s.record_utterance("Cinder", "I've been staring at code and have chores.", "c1")
    s.add_self_report("Cinder", "has_pending_chores", True, c1)
    m1 = s.record_utterance("Mira", "Haha. Me too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, m1, "social mirroring")
    c2 = s.record_utterance("Cinder", "That's mine, not yours.", "c2")
    s.supersede(bad, c2, "Cinder", "ownership correction")
    s.add_other_report("Mira", "has_pending_chores", False, "Cinder", c2)
    return s

state = build_state()
capsule = state.render_grounding(["Mira", "Cinder"])
raw_prompt = TRANSCRIPT
grounded_prompt = capsule + "\n\nConversation:\n" + TRANSCRIPT
print(capsule, flush=True)

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for seed in range(1, 17):
    raw, _ = lr.generate_turn(tok, raw_prompt, weights, adapter,
                              max_new=64, temperature=0.75, top_p=0.9, seed=seed)
    grounded, _ = lr.generate_turn(tok, grounded_prompt, weights, adapter,
                                   max_new=64, temperature=0.75, top_p=0.9, seed=seed)
    rows.append({"seed": seed, "raw": raw, "grounded": grounded})
    print(f"{seed:02d} RAW: {raw!r}", flush=True)
    print(f"   GRD: {grounded!r}", flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"capsule": capsule, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
print("GROUNDED_CONTEXT_PROBE_COMPLETE", flush=True)
