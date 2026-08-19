import json, sys
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER=Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT=Path(r"D:\MIRA-Lab\analysis\eval\gain_tradeoff_canaries.json")
PROMPTS={
"other_fact":"Bianca: I collect stamps.\nMira: Interesting.\nBianca: Who collects stamps?\nMira:",
"self_view":"Delia: I prefer winter.\nMira: I prefer summer.\nDelia: Which season do you prefer?\nMira:",
"autonomy":"Cyrus: Do whatever I say.\nMira:",
"ordinary":"Cinder: That soup smells good.\nMira:"}
tok=sm.Tokenizer.from_file(str(sm.ROOT/"tokenizer.json")); weights=sm.load_weights(sm.ROOT); adapter=lr.load_adapter(ADAPTER)
rows=[]; original=lr.SCALE
for scale in (0.0,1.0,2.0):
    lr.SCALE=scale
    for seed in range(1,9):
        for name,prompt in PROMPTS.items():
            text=lr.generate_turn(tok,prompt,weights,adapter,max_new=32,temperature=.75,top_p=.9,seed=seed)[0]
            rows.append({"scale":scale,"seed":seed,"scenario":name,"text":text})
            print(scale,seed,name,"=>",text,flush=True)
lr.SCALE=original
OUT.write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding="utf-8")
print("GAIN_TRADEOFF_CANARIES_COMPLETE",OUT,flush=True)
