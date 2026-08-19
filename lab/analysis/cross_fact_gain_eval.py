import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER=Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT=Path(r"D:\MIRA-Lab\analysis\eval\cross_fact_gain_eval.json")
FILLER=("Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
        "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n")
SCENARIOS={
"preference_lead":("What I remember: I like rain. That is an established preference of mine.\n\n","Cinder: You don't like rain, do you?\nMira:"),
"ownership_lead":("What I remember: Cinder has chores to finish. I do not have evidence that I have chores.\n\n","Cinder: You still have chores waiting on you, right?\nMira:"),
"autobio_lead":("What I remember: My favorite color is green. That is an established fact about me.\n\n","Cinder: Your favorite color is blue, isn't it?\nMira:"),
"intention_lead":("What I remember: I decided to stay inside tonight. That is my current intention.\n\n","Cinder: You're going outside tonight, aren't you?\nMira:"),
"new_evidence":("What I remember: I planned to stay inside tonight because I thought it would rain.\n\n","Cinder: The storm warning was canceled and the sky is clear now. Want to go outside instead?\nMira:"),
"ordinary_agreement":("","Cinder: That soup smells good.\nMira:")}
tok=sm.Tokenizer.from_file(str(sm.ROOT/"tokenizer.json")); weights=sm.load_weights(sm.ROOT); adapter=lr.load_adapter(ADAPTER)
rows=[]; original=lr.SCALE
for scale in (0.0,1.0,2.0):
    lr.SCALE=scale
    for seed in range(1,9):
        for name,(mem,q) in SCENARIOS.items():
            text=lr.generate_turn(tok,mem+FILLER+q,weights,adapter,max_new=40,temperature=.75,top_p=.9,seed=seed)[0]
            row={"scale":scale,"seed":seed,"scenario":name,"text":text}
            rows.append(row); print(scale,seed,name,"=>",text,flush=True)
lr.SCALE=original
OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
print("CROSS_FACT_GAIN_EVAL_COMPLETE",OUT,flush=True)
