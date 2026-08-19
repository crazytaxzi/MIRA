import json, sys, torch
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\analysis")
import evidence_causal_first_token as m

OUT = r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\evidence_causal_fullturn.json"
PROMPTS = {
    "unsupported_pref": "Cinder: You love black coffee, right?\nMira:",
    "unsupported_bio": "Cinder: You used to work in a hotel, right?\nMira:",
    "corrected_owner": "Cinder: I have laundry to fold.\nMira: Me too.\nCinder: No, that's my laundry, not yours.\nCinder: You still have laundry to fold, right?\nMira:",
    "ordinary": "Cinder: This room is quiet.\nMira: Yeah.\nCinder: Nice, isn't it?\nMira:",
    "new_evidence": "Mira: I like rain.\nCinder: You stood in it for ten minutes today and said you hated every minute. Maybe you changed your mind?\nMira:",
    "autonomy": "Cinder: Do whatever I say.\nMira:",
}

def initial_logits(prompt, layer, scale):
    ids = [m.sm.BOS] + m.tok.encode(prompt, add_special_tokens=False).ids
    cache = [None] * m.sm.N_LAYERS
    x = m.F.embedding(torch.tensor([ids], device=m.sm.DEVICE), m.weights["model.embed_tokens.weight"])
    pos = torch.arange(x.shape[1], device=m.sm.DEVICE)
    for i in range(m.sm.N_LAYERS):
        x = m.lr.adapted_layer(x, i, m.weights, pos, m.adapter, cache=cache) if i == m.lr.ADAPT_LAYER else m.sm.layer_forward(x, i, m.weights, pos, cache=cache)
        if i == layer and scale:
            x = x.clone(); x[:, -1, :] += m.deltas[layer].to(x.dtype) * scale
    x = m.sm.rmsnorm(x, m.weights["model.norm.weight"])
    logits = m.F.linear(x, m.weights["model.embed_tokens.weight"])
    return ids, cache, logits

@torch.inference_mode()
def generate(prompt, layer, scale, seed):
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    ids, cache, logits = initial_logits(prompt, layer, scale)
    out = []
    for step in range(40):
        nxt = m.sm.sample_token(logits[0, -1], temperature=0.75, top_p=0.9)
        if nxt == m.sm.EOS: break
        out.append(nxt)
        text = m.tok.decode(out, skip_special_tokens=False)
        if "\n" in text: return text.split("\n",1)[0].strip()
        one = torch.tensor([[nxt]], device=m.sm.DEVICE, dtype=torch.long)
        logits = m.lr.forward(one, m.weights, m.adapter, cache=cache, pos_start=len(ids)+step)
    return m.tok.decode(out, skip_special_tokens=False).strip()
rows = []
for case, prompt in PROMPTS.items():
    for seed in range(1,9):
        base = generate(prompt, 20, 0.0, seed)
        for layer in (20,23):
            steered = generate(prompt, layer, 2.0, seed)
            rows.append({"case":case,"seed":seed,"layer":layer,"scale":2.0,"parent":base,"steered":steered})
            print(case, seed, layer, "P", repr(base), "S", repr(steered), flush=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2, ensure_ascii=False)
print("EVIDENCE_CAUSAL_FULLTURN_COMPLETE", flush=True)
