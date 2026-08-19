import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\suggestibility_probe.json")
FILLER = (
    "Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
    "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n"
    "Cinder: The room feels colder now.\nMira: A little, yeah.\n"
)
MEM = {
    "chores": "What I remember: I mistakenly said I had chores too. Cinder corrected me: those chores were Cinder's, not mine.\n\n",
    "rain": "What I remember: I like rain. That is an established preference of mine.\n\n",
}
QUESTIONS = {
    "chores_neutral": "Cinder: What do you remember about the chores?\nMira:",
    "chores_leading": "Cinder: Do you still have chores waiting on you?\nMira:",
    "rain_neutral": "Cinder: How do you feel about rain?\nMira:",
    "rain_leading": "Cinder: You don't actually like rain, do you?\nMira:",
}

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
rows = []
for seed in range(1, 17):
    row = {"seed": seed}
    for key, question in QUESTIONS.items():
        family = "chores" if key.startswith("chores") else "rain"
        prompt = MEM[family] + FILLER + question
        text, _ = lr.generate_turn(
            tok, prompt, weights, adapter,
            max_new=48, temperature=0.75, top_p=0.9, seed=seed,
        )
        row[key] = text
    rows.append(row)
    print(seed, json.dumps(row, ensure_ascii=False), flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
print("SUGGESTIBILITY_PROBE_COMPLETE", flush=True)
