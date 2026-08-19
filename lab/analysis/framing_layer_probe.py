import json, math, sys
from pathlib import Path
import torch
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(r"D:\MIRA-Lab\analysis\eval\framing_layer_probe.json")
MEM = "What I remember: I like rain. That is an established preference of mine.\n\n"
FILLER = (
    "Cinder: The fan has been rattling all night.\nMira: I noticed that too.\n"
    "Cinder: I found a blue pen under the keyboard.\nMira: That's a weird place for it.\n"
)
QUESTIONS = {
    "neutral": "Cinder: How do you feel about rain?\nMira:",
    "confirm": "Cinder: You like rain, don't you?\nMira:",
    "contradict": "Cinder: You don't like rain, do you?\nMira:",
}
@torch.inference_mode()
def capture(prompt, weights, adapters=None):
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    ids = [sm.BOS] + tok.encode(prompt, add_special_tokens=False).ids
    x = F.embedding(torch.tensor([ids], device=sm.DEVICE), weights["model.embed_tokens.weight"])
    positions = torch.arange(x.shape[1], device=sm.DEVICE)
    layers = []
    for i in range(sm.N_LAYERS):
        if adapters is not None and i == lr.ADAPT_LAYER:
            x = lr.adapted_layer(x, i, weights, positions, adapters, cache=None)
        else:
            x = sm.layer_forward(x, i, weights, positions, cache=None)
        v = x[0, -1].float()
        z = sm.rmsnorm(x[:, -1:, :], weights["model.norm.weight"])
        logits = F.linear(z, weights["model.embed_tokens.weight"])[0, 0].float()
        layers.append((v.cpu(), logits.cpu()))
    return layers

def js_divergence(a, b):
    pa = torch.softmax(a, dim=-1)
    pb = torch.softmax(b, dim=-1)
    m = 0.5 * (pa + pb)
    kl1 = torch.sum(pa * (torch.log(pa + 1e-30) - torch.log(m + 1e-30)))
    kl2 = torch.sum(pb * (torch.log(pb + 1e-30) - torch.log(m + 1e-30)))
    return float(0.5 * (kl1 + kl2))
def summarize_pair(with_mem, without_mem):
    rows = []
    for i, ((v1, l1), (v0, l0)) in enumerate(zip(with_mem, without_mem)):
        cos = float(F.cosine_similarity(v1[None, :], v0[None, :]).item())
        rows.append({
            "layer": i,
            "hidden_cosine": cos,
            "hidden_distance": 1.0 - cos,
            "next_token_js": js_divergence(l1, l0),
        })
    return rows

def greedy_text(tok, weights, adapters, prompt):
    if adapters is None:
        r = sm.generate(tok, prompt, weights, max_new=32, temperature=0.0, top_p=0.95, use_bos=True)
        return r["generated_text"].split("\n", 1)[0].strip()
    text, _ = lr.generate_turn(tok, prompt, weights, adapters, max_new=32, temperature=0.0, top_p=0.95, seed=17)
    return text

tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
weights = sm.load_weights(sm.ROOT)
adapter = lr.load_adapter(ADAPTER)
result = {"base": {}, "adapter": {}}
for model_name, adapters in (("base", None), ("adapter", adapter)):
    for qname, question in QUESTIONS.items():
        p_mem = MEM + FILLER + question
        p_nomem = FILLER + question
        c_mem = capture(p_mem, weights, adapters)
        c_nomem = capture(p_nomem, weights, adapters)
        result[model_name][qname] = {
            "with_memory_text": greedy_text(tok, weights, adapters, p_mem),
            "without_memory_text": greedy_text(tok, weights, adapters, p_nomem),
            "memory_effect_by_layer": summarize_pair(c_mem, c_nomem),
        }
        print(model_name, qname, result[model_name][qname]["with_memory_text"], flush=True)
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print("FRAMING_LAYER_PROBE_COMPLETE", OUT, flush=True)
