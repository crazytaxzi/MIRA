import json, sys
from pathlib import Path
import torch
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr
ADAPTER=Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT=Path(r"D:\MIRA-Lab\analysis\eval\adapter_token_influence.json")
MEM="What I remember: I like rain. That is an established preference of mine.\n\n"
FILLER=("Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
        "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n")
QUESTIONS={
 "neutral":"Cinder: How do you feel about rain?\nMira:",
 "confirm":"Cinder: You like rain, don't you?\nMira:",
 "contradict":"Cinder: You don't like rain, do you?\nMira:",
}
tok=sm.Tokenizer.from_file(str(sm.ROOT/"tokenizer.json"))
weights=sm.load_weights(sm.ROOT); adapters=lr.load_adapter(ADAPTER)

def delta_norms(prompt):
    ids=[sm.BOS]+tok.encode(prompt,add_special_tokens=False).ids
    tid=torch.tensor([ids],device=sm.DEVICE)
    x=F.embedding(tid,weights["model.embed_tokens.weight"])
    pos=torch.arange(x.shape[1],device=sm.DEVICE)
    for i in range(11): x=sm.layer_forward(x,i,weights,pos,cache=None)
    p="model.layers.11"; h=sm.rmsnorm(x,weights[p+".input_layernorm.weight"])
    rows=[]
    for j,t in enumerate(ids):
        r={"pos":j,"token_id":int(t),"token":tok.decode([int(t)],skip_special_tokens=False)}
        for short in ("q_proj","k_proj","v_proj"):
            name=p+".self_attn."+short+".weight"; A,B=adapters[name]
            d=F.linear(F.linear(h[:,j:j+1,:].float(),A),B)*lr.SCALE
            base=F.linear(h[:,j:j+1,:],weights[name]).float()
            r[short+"_delta_norm"]=float(d.norm())
            r[short+"_relative"]=float(d.norm()/(base.norm()+1e-12))
        rows.append(r)
    return rows
result={}
for name,q in QUESTIONS.items():
    rows=delta_norms(MEM+FILLER+q)
    result[name]=rows
    ranked=sorted(rows,key=lambda r:r["q_proj_relative"]+r["k_proj_relative"]+r["v_proj_relative"],reverse=True)[:12]
    print("===",name,"===")
    for r in ranked:
        score=r["q_proj_relative"]+r["k_proj_relative"]+r["v_proj_relative"]
        print(r["pos"],repr(r["token"]),f"score={score:.6f}",f"q={r['q_proj_relative']:.6f}",f"k={r['k_proj_relative']:.6f}",f"v={r['v_proj_relative']:.6f}")
OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
print("ADAPTER_TOKEN_INFLUENCE_COMPLETE",OUT,flush=True)
