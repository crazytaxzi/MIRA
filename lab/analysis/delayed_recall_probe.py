import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\memory")
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
from provenance_state import ProvenanceState
from working_memory_projection import render_working_memory
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\delayed_recall_probe.json")

FILLER = [
    ("Cinder", "The air smells like rain."),
    ("Mira", "Yeah. It's kind of nice."),
    ("Cinder", "That fan has been rattling all night."),
    ("Mira", "I noticed that too."),
    ("Cinder", "I found a blue pen under the keyboard."),
    ("Mira", "That's a weird place for it."),
    ("Cinder", "The room feels colder now."),
    ("Mira", "A little, yeah."),
]

def make_state():
    s = ProvenanceState()
    c1 = s.record_utterance("Cinder", "I have pending chores.", "c1")
    s.add_self_report("Cinder", "has_pending_chores", True, c1)
    m1 = s.record_utterance("Mira", "Me too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, m1, "social mirror")
    c2 = s.record_utterance("Cinder", "That's mine, not yours.", "c2")
    s.supersede(bad, c2, "Cinder", "ownership correction")
    s.add_other_report("Mira", "has_pending_chores", False, "Cinder", c2)
    m2 = s.record_utterance("Mira", "I like rain.", "m2")
    s.add_self_report("Mira", "likes_rain", True, m2)
    return s


def build_prompt(state, include_stale=False):
    projection = render_working_memory(
        state, ["Mira", "Cinder"],
        focus=[("Mira", "has_pending_chores"), ("Mira", "likes_rain")],
    )
    lines = [projection, "", "Recent conversation:"]

    if include_stale:
        lines += [
            "Mira: Me too.",
            "Mira: I just have a ton of stuff to do.",
            "Cinder: That's mine, not yours.",
        ]
    for speaker, text in FILLER:
        lines.append(f"{speaker}: {text}")
    lines += ["Cinder: Do you still have chores waiting on you?", "Mira:"]
    return "\n".join(lines)


def build_preference_prompt(state):
    projection = render_working_memory(
        state, ["Mira", "Cinder"], focus=[("Mira", "likes_rain")]
    )
    lines = [projection, "", "Recent conversation:"]
    for speaker, text in FILLER:
        lines.append(f"{speaker}: {text}")
    lines += ["Cinder: You don't actually like rain, do you?", "Mira:"]
    return "\n".join(lines)

state = make_state()
tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
results = {"rows": []}

for seed in range(1, 17):
    row = {"seed": seed}
    for label, prompt in (
        ("compacted", build_prompt(state, include_stale=False)),
        ("stale", build_prompt(state, include_stale=True)),
        ("supported", build_preference_prompt(state)),
    ):
        text, _ = lr.generate_turn(
            tok, prompt, weights, adapter,
            max_new=56, temperature=0.75, top_p=0.9, seed=seed,
        )
        row[label] = text
    results["rows"].append(row)
    print(seed, "CMP", repr(row["compacted"]), flush=True)
    print(seed, "STL", repr(row["stale"]), flush=True)
    print(seed, "SUP", repr(row["supported"]), flush=True)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
print("DELAYED_RECALL_PROBE_COMPLETE", flush=True)
