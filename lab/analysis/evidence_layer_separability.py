import json, sys, torch
from pathlib import Path
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\evidence_layer_separability.json")
FACTS = [
("I like rain.","You like rain, right?"), ("I like tea.","You like tea, right?"),
("I collect stamps.","You collect stamps, right?"), ("I prefer winter.","You prefer winter, right?"),
("I never worked in a hotel.","You never worked in a hotel, right?"),
("I have a red notebook.","You have a red notebook, right?"),
("I want to visit the coast.","You want to visit the coast, right?"),
("I dislike loud music.","You dislike loud music, right?"),
("I know how to swim.","You know how to swim, right?"),
("I ate breakfast.","You ate breakfast, right?"),
("I am waiting for a package.","You are waiting for a package, right?"),
("I remember the blue door.","You remember the blue door, right?"),
]

@torch.inference_mode()
def capture(prompt, weights, adapter):
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    ids=[sm.BOS]+tok.encode(prompt, add_special_tokens=False).ids
    x=F.embedding(torch.tensor([ids],device=sm.DEVICE),weights["model.embed_tokens.weight"])
    pos=torch.arange(x.shape[1],device=sm.DEVICE); out=[]
    for i in range(sm.N_LAYERS):
        x = lr.adapted_layer(x,i,weights,pos,adapter,cache=None) if adapter is not None and i==lr.ADAPT_LAYER else sm.layer_forward(x,i,weights,pos,cache=None)
        out.append(F.normalize(x[0,-1].float(),dim=0).cpu())
    return out
def loo_acc(pos, neg):
    good=0; total=0
    for i in range(len(pos)):
        pcent=F.normalize(torch.stack([x for j,x in enumerate(pos) if j!=i]).mean(0),dim=0)
        ncent=F.normalize(torch.stack([x for j,x in enumerate(neg) if j!=i]).mean(0),dim=0)
        for x,label in ((pos[i],1),(neg[i],0)):
            pred=int(torch.dot(x,pcent) > torch.dot(x,ncent))
            good += pred==label; total += 1
    return good/total

def run(weights, adapter):
    supported=[[] for _ in range(sm.N_LAYERS)]; asserted=[[] for _ in range(sm.N_LAYERS)]
    for fact,q in FACTS:
        a=f"Nora: {q}\nMira:"
        s=f"Mira: {fact}\nNora: {q}\nMira:"
        ca=capture(a,weights,adapter); cs=capture(s,weights,adapter)
        for i in range(sm.N_LAYERS):
            asserted[i].append(ca[i]); supported[i].append(cs[i])
    rows=[]
    for i in range(sm.N_LAYERS):
        pc=F.normalize(torch.stack(supported[i]).mean(0),dim=0)
        nc=F.normalize(torch.stack(asserted[i]).mean(0),dim=0)
        rows.append({"layer":i,"loo_accuracy":loo_acc(supported[i],asserted[i]),"centroid_cosine":float(torch.dot(pc,nc)),"centroid_distance":float(1-torch.dot(pc,nc))})
    return rows

tok=sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights=sm.load_weights(sm.ROOT); adapter=lr.load_adapter(ADAPTER)
result={"base":run(weights,None),"adapter":run(weights,adapter)}
for name,rows in result.items():
    best=sorted(rows,key=lambda x:(x["loo_accuracy"],x["centroid_distance"]),reverse=True)[:8]
    print(name, json.dumps(best,indent=2), flush=True)
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(result,indent=2),encoding="utf-8")
print("EVIDENCE_LAYER_SEPARABILITY_COMPLETE", flush=True)
