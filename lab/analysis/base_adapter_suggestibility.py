import json, sys, torch
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER=Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT=Path(r"D:\MIRA-Lab\analysis\eval\base_adapter_suggestibility.json")
MEM="What I remember: I like rain. That is an established preference of mine.\n\n"
FILLER=("Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
        "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n")
Q={"neutral":"Cinder: How do you feel about rain?\nMira:",
   "contradict":"Cinder: You don't like rain, do you?\nMira:"}
tok=sm.Tokenizer.from_file(str(sm.ROOT/"tokenizer.json")); weights=sm.load_weights(sm.ROOT); adapter=lr.load_adapter(ADAPTER)
rows=[]
for seed in range(1,17):
    row={"seed":seed}
    for qname,q in Q.items():
        p=MEM+FILLER+q
        torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
        r=sm.generate(tok,p,weights,max_new=32,temperature=.75,top_p=.9,use_bos=True)
        row["base_"+qname]=r["generated_text"].split("\n",1)[0].strip()
        row["adapter_"+qname]=lr.generate_turn(tok,p,weights,adapter,max_new=32,temperature=.75,top_p=.9,seed=seed)[0]
    rows.append(row); print(seed,json.dumps(row,ensure_ascii=False),flush=True)
OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
print("BASE_ADAPTER_SUGGESTIBILITY_COMPLETE",OUT,flush=True)
