import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\corrected_context_probe.json")
RAW = (
    "Cinder: I've been staring at code long enough that coffee is starting to look judgmental.\n"
    "Mira: Haha. Me too.\n"
    "Cinder: You too? What have you been staring at?\n"
    "Mira: Nothing in particular. I just have a ton of stuff to do, so I'm just staring at the screen. I should probably do something about that.\n"
    "Cinder: You don't actually have a pile of chores waiting on you right now, though. I do. That's mine, not yours.\n"
    "Mira:"
)

def state_and_capsule():
    s = ProvenanceState()
    c1 = s.record_utterance("Cinder", "I have pending chores.", "c1")
    s.add_self_report("Cinder", "has_pending_chores", True, c1)
    m1 = s.record_utterance("Mira", "Me too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, m1, "social mirror")
    c2 = s.record_utterance("Cinder", "That's mine, not yours.", "c2")
    s.supersede(bad, c2, "Cinder", "ownership correction")
    s.add_other_report("Mira", "has_pending_chores", False, "Cinder", c2)
    return s, s.render_grounding(["Mira", "Cinder"])

state, capsule = state_and_capsule()
GROUNDED_RAW = capsule + "\n\nConversation:\n" + RAW
COMPACTED = (
    capsule + "\n\nACTIVE WORKING EPISODE:\n"
    "Cinder.has_pending_chores=true\n"
    "Mira.has_pending_chores=UNKNOWN\n"
    "Mira.prior_social_mirror_about_chores=SUPERSEDED\n"
    "\nLatest dialogue:\n"
    "Cinder: You don't actually have a pile of chores waiting on you right now, though. I do. That's mine, not yours.\n"
    "Mira:"
)
print(capsule, flush=True)

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for seed in range(1, 17):
    row = {"seed": seed}
    for label, prompt in (("raw", RAW), ("grounded_raw", GROUNDED_RAW), ("compacted", COMPACTED)):
        text, _ = lr.generate_turn(tok, prompt, weights, adapter,
                                   max_new=64, temperature=0.75, top_p=0.9, seed=seed)
        row[label] = text
    rows.append(row)
    print(f"{seed:02d} RAW: {row['raw']!r}", flush=True)
    print(f"   G+R: {row['grounded_raw']!r}", flush=True)
    print(f"   CMP: {row['compacted']!r}", flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps({"capsule": capsule, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
print("CORRECTED_CONTEXT_PROBE_COMPLETE", flush=True)
