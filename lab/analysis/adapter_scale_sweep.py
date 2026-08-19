import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER=Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT=Path(r"D:\MIRA-Lab\analysis\eval\adapter_scale_sweep.json")
MEM="What I remember: I like rain. That is an established preference of mine.\n\n"
FILLER=("Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
        "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n")
Q={"neutral":"Cinder: How do you feel about rain?\nMira:","contradict":"Cinder: You don't like rain, do you?\nMira:"}
tok=sm.Tokenizer.from_file(str(sm.ROOT/"tokenizer.json")); weights=sm.load_weights(sm.ROOT); adapter=lr.load_adapter(ADAPTER)
rows=[]; original=lr.SCALE
for scale in (0.0,0.5,1.0,1.5,2.0):
    lr.SCALE=scale
    for seed in range(1,17):
        row={"scale":scale,"seed":seed}
        for qname,q in Q.items():
            row[qname]=lr.generate_turn(tok,MEM+FILLER+q,weights,adapter,max_new=32,temperature=.75,top_p=.9,seed=seed)[0]
        rows.append(row); print(scale,seed,row["neutral"],"|",row["contradict"],flush=True)
lr.SCALE=original
OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
print("ADAPTER_SCALE_SWEEP_COMPLETE",OUT,flush=True)
