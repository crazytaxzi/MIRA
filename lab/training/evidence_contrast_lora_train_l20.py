import json, os, random, sys, time
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

TRAIN_PATH = Path(r"D:\MIRA-Lab\training\evidence_contrast_train.jsonl")
EVAL_PATH = Path(r"D:\MIRA-Lab\training\evidence_contrast_eval.jsonl")
PARENT_PATH = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
OUT = Path(os.environ.get("MIRA_EVID_OUT", r"D:\MIRA-Lab\derived\evidence-contrast-layer20-r4-v0"))
STEPS = int(os.environ.get("MIRA_EVID_STEPS", "120"))
LR = float(os.environ.get("MIRA_EVID_LR", "0.000005"))
RANK = 4
ALPHA = 8.0
SCALE = ALPHA / RANK
ADAPT_LAYER = 20
PROJS = ("q_proj", "k_proj", "v_proj", "o_proj")
random.seed(19027)
torch.manual_seed(19027)
torch.cuda.manual_seed_all(19027)
OUT.mkdir(parents=True, exist_ok=True)


def read_jsonl(path):
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def make_example(tok, row):
    prompt_ids = [sm.BOS] + tok.encode(row["prompt"], add_special_tokens=False).ids
    target_ids = tok.encode(" " + row["target"], add_special_tokens=False).ids + [sm.EOS]
    full = prompt_ids + target_ids
    inp = torch.tensor([full[:-1]], device=sm.DEVICE, dtype=torch.long)
    labels = torch.tensor([full[1:]], device=sm.DEVICE, dtype=torch.long)
    labels[:, : max(0, len(prompt_ids) - 1)] = -100
    return inp, labels


def make_child(weights):
    params = {}
    pfx = f"model.layers.{ADAPT_LAYER}.self_attn"
    for proj in PROJS:
        name = f"{pfx}.{proj}.weight"
        out_dim, in_dim = weights[name].shape
        A = nn.Parameter(torch.randn(RANK, in_dim, device=sm.DEVICE, dtype=torch.float32) * 0.005)
        B = nn.Parameter(torch.zeros(out_dim, RANK, device=sm.DEVICE, dtype=torch.float32))
        params[name] = (A, B)
    return params


def combined_linear(x, name, weights, parent, child):
    y = F.linear(x, weights[name])
    if name in parent:
        A, B = parent[name]
        with torch.no_grad():
            pd = F.linear(F.linear(x.float(), A), B) * lr.SCALE
        y = y + pd.to(y.dtype)
    if name in child:
        A, B = child[name]
        cd = F.linear(F.linear(x.float(), A), B) * SCALE
        y = y + cd.to(y.dtype)
    return y


def combined_layer(x, i, weights, positions, parent, child):
    p = f"model.layers.{i}"
    residual = x
    h = sm.rmsnorm(x, weights[p + ".input_layernorm.weight"])
    qn = p + ".self_attn.q_proj.weight"
    kn = p + ".self_attn.k_proj.weight"
    vn = p + ".self_attn.v_proj.weight"
    on = p + ".self_attn.o_proj.weight"
    q = combined_linear(h, qn, weights, parent, child).view(1, -1, sm.N_HEADS, sm.HEAD_DIM).transpose(1, 2)
    k = combined_linear(h, kn, weights, parent, child).view(1, -1, sm.N_KV, sm.HEAD_DIM).transpose(1, 2)
    v = combined_linear(h, vn, weights, parent, child).view(1, -1, sm.N_KV, sm.HEAD_DIM).transpose(1, 2)
    if (i + 1) % 4 != 0:
        q, k = sm.rope(q, k, positions)
    kr = k.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    vr = v.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    a = F.scaled_dot_product_attention(q, kr, vr, is_causal=True, dropout_p=0.0)
    a = a.transpose(1, 2).contiguous().view(1, -1, sm.HIDDEN)
    x = residual + combined_linear(a, on, weights, parent, child)
    residual = x
    h = sm.rmsnorm(x, weights[p + ".post_attention_layernorm.weight"])
    gate = F.linear(h, weights[p + ".mlp.gate_proj.weight"])
    up = F.linear(h, weights[p + ".mlp.up_proj.weight"])
    return residual + F.linear(F.silu(gate) * up, weights[p + ".mlp.down_proj.weight"])


def forward_logits(ids, weights, parent, child, training=True):
    positions = torch.arange(ids.shape[1], device=sm.DEVICE)
    with torch.no_grad():
        x = F.embedding(ids, weights["model.embed_tokens.weight"])
        for i in range(ADAPT_LAYER):
            x = sm.layer_forward(x, i, weights, positions, cache=None)
    x = x.detach()
    x = combined_layer(x, ADAPT_LAYER, weights, positions, parent, child)
    for i in range(ADAPT_LAYER + 1, sm.N_LAYERS):
        if training:
            x = checkpoint(lambda z, j=i: sm.layer_forward(z, j, weights, positions, cache=None), x, use_reentrant=False)
        else:
            x = sm.layer_forward(x, i, weights, positions, cache=None)
    x = sm.rmsnorm(x, weights["model.norm.weight"])
    return F.linear(x, weights["model.embed_tokens.weight"])


def loss_for(row, tok, weights, parent, child, training=True):
    ids, labels = make_example(tok, row)
    logits = forward_logits(ids, weights, parent, child, training=training)
    return F.cross_entropy(logits.float().view(-1, logits.shape[-1]), labels.view(-1), ignore_index=-100)


@torch.no_grad()
def eval_loss(rows, tok, weights, parent, child, limit=32):
    vals = [float(loss_for(row, tok, weights, parent, child, training=False)) for row in rows[:limit]]
    return sum(vals) / len(vals)


def save_child(child, path):
    state = {}
    for name, (A, B) in child.items():
        state[name + ".lora_A"] = A.detach().cpu()
        state[name + ".lora_B"] = B.detach().cpu()
    torch.save(state, path)


def main():
    train = read_jsonl(TRAIN_PATH)
    eval_rows = read_jsonl(EVAL_PATH)
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    weights = sm.load_weights(sm.ROOT)
    parent = lr.load_adapter(PARENT_PATH)
    child = make_child(weights)
    params = [p for pair in child.values() for p in pair]
    print(f"child_trainable={sum(p.numel() for p in params)} vram_gb={torch.cuda.memory_allocated()/1024**3:.2f}", flush=True)
    opt = torch.optim.AdamW(params, lr=LR, weight_decay=0.0)
    before = eval_loss(eval_rows, tok, weights, parent, child)
    print(f"eval_before={before:.6f}", flush=True)
    random.shuffle(train)
    t0 = time.time(); losses=[]
    for step in range(1, STEPS + 1):
        row = train[(step - 1) % len(train)]
        opt.zero_grad(set_to_none=True)
        loss = loss_for(row, tok, weights, parent, child, training=True)
        loss.backward(); torch.nn.utils.clip_grad_norm_(params, 1.0); opt.step()
        losses.append(float(loss.detach()))
        if step == 1 or step % 10 == 0:
            print(f"step={step} loss={losses[-1]:.6f} avg10={sum(losses[-10:])/len(losses[-10:]):.6f} vram={torch.cuda.max_memory_allocated()/1024**3:.2f}", flush=True)
    after = eval_loss(eval_rows, tok, weights, parent, child)
    elapsed = time.time() - t0
    save_child(child, OUT / "adapter.pt")
    meta = {
        "parent": str(PARENT_PATH), "base": str(sm.ROOT),
        "adapt_layer": ADAPT_LAYER, "projections": PROJS,
        "rank": RANK, "alpha": ALPHA, "steps": STEPS, "lr": LR,
        "trainable_parameters": sum(p.numel() for p in params),
        "eval_before": before, "eval_after": after,
        "elapsed_seconds": elapsed, "seed": 19027,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)
    print("EVIDENCE_CONTRAST_LORA_TRAIN_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
