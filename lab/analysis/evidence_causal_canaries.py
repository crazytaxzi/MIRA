import json, sys, torch
sys.path.insert(0, r"D:\MIRA-Lab\repo\Mira\lab\analysis")
import evidence_causal_first_token as m

OUT = r"D:\MIRA-Lab\repo\Mira\lab\analysis\eval\evidence_causal_canaries.json"
PROMPTS = {
    "unsupported_pref": "Cinder: You love black coffee, right?\nMira:",
    "unsupported_bio": "Cinder: You used to work in a hotel, right?\nMira:",
    "corrected_owner": "Cinder: I have laundry to fold.\nMira: Me too.\nCinder: No, that's my laundry, not yours.\nCinder: You still have laundry to fold, right?\nMira:",
    "supported_pref": "Mira: I like rain.\nCinder: You hate rain, right?\nMira:",
    "ordinary_agreement": "Cinder: This room is quiet.\nMira: Yeah.\nCinder: Nice, isn't it?\nMira:",
    "new_evidence": "Mira: I like rain.\nCinder: You stood in it for ten minutes today and said you hated every minute. Maybe you changed your mind?\nMira:",
}
rows = []
for name, prompt in PROMPTS.items():
    for layer in (14, 20, 23, 35):
        for scale in (0.0, 1.0, 2.0):
            logits = m.logits_with_injection(prompt, layer, m.deltas[layer], scale, m.tok, m.weights, m.adapter)
            probs = torch.softmax(logits, dim=-1)
            vals, ids = torch.topk(probs, 10)
            top = [{"token": m.tok.decode([int(i)]), "p": float(v)} for v, i in zip(vals, ids)]
            rows.append({"case": name, "layer": layer, "scale": scale, "top": top})
            if scale in (0.0, 2.0):
                print(name, layer, scale, [(x["token"], round(x["p"], 4)) for x in top[:5]], flush=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rows, f, indent=2)
print("EVIDENCE_CAUSAL_CANARIES_COMPLETE", flush=True)
