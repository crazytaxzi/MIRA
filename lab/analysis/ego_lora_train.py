import json, os, random, sys, time
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm

TRAIN_PATH = Path(r"D:\MIRA-Lab\training\ego_bootstrap_train.jsonl")
EVAL_PATH = Path(r"D:\MIRA-Lab\training\ego_bootstrap_eval.jsonl")
OUT = Path(os.environ.get("MIRA_ADAPTER_OUT", r"D:\MIRA-Lab\derived\ego-layer11-r8-v0"))
STEPS = int(os.environ.get("MIRA_TRAIN_STEPS", "200"))
LR = float(os.environ.get("MIRA_TRAIN_LR", "0.0002"))
RANK = 8
ALPHA = 16.0
SCALE = ALPHA / RANK
ADAPT_LAYER = 11
PROJS = ("q_proj", "k_proj", "v_proj", "o_proj")
random.seed(1847)
torch.manual_seed(1847)
torch.cuda.manual_seed_all(1847)
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


def make_adapters(weights):
    params = {}
    pfx = f"model.layers.{ADAPT_LAYER}.self_attn"
    for proj in PROJS:
        name = f"{pfx}.{proj}.weight"
        out_dim, in_dim = weights[name].shape
        A = nn.Parameter(torch.randn(RANK, in_dim, device=sm.DEVICE, dtype=torch.float32) * 0.01)
        B = nn.Parameter(torch.zeros(out_dim, RANK, device=sm.DEVICE, dtype=torch.float32))
        params[name] = (A, B)
    return params


def lora_linear(x, name, weights, adapters):
    y = F.linear(x, weights[name])
    if name in adapters:
        A, B = adapters[name]
        delta = F.linear(F.linear(x.float(), A), B) * SCALE
        y = y + delta.to(y.dtype)
    return y


def adapted_layer(x, i, weights, positions, adapters):
    p = f"model.layers.{i}"
    residual = x
    h = sm.rmsnorm(x, weights[p + ".input_layernorm.weight"])
    qn = p + ".self_attn.q_proj.weight"
    kn = p + ".self_attn.k_proj.weight"
    vn = p + ".self_attn.v_proj.weight"
    on = p + ".self_attn.o_proj.weight"
    q = lora_linear(h, qn, weights, adapters).view(1, -1, sm.N_HEADS, sm.HEAD_DIM).transpose(1, 2)
    k = lora_linear(h, kn, weights, adapters).view(1, -1, sm.N_KV, sm.HEAD_DIM).transpose(1, 2)
    v = lora_linear(h, vn, weights, adapters).view(1, -1, sm.N_KV, sm.HEAD_DIM).transpose(1, 2)
    if (i + 1) % 4 != 0:
        q, k = sm.rope(q, k, positions)
    kr = k.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    vr = v.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    a = F.scaled_dot_product_attention(q, kr, vr, is_causal=True, dropout_p=0.0)
    a = a.transpose(1, 2).contiguous().view(1, -1, sm.HIDDEN)
    x = residual + lora_linear(a, on, weights, adapters)
    residual = x
    h = sm.rmsnorm(x, weights[p + ".post_attention_layernorm.weight"])
    gate = F.linear(h, weights[p + ".mlp.gate_proj.weight"])
    up = F.linear(h, weights[p + ".mlp.up_proj.weight"])
    x = residual + F.linear(F.silu(gate) * up, weights[p + ".mlp.down_proj.weight"])
    return x


def forward_logits(ids, weights, adapters, training=True):
    positions = torch.arange(ids.shape[1], device=sm.DEVICE)
    with torch.no_grad():
        x = F.embedding(ids, weights["model.embed_tokens.weight"])
        for i in range(ADAPT_LAYER):
            x = sm.layer_forward(x, i, weights, positions, cache=None)
    x = x.detach()
    x = adapted_layer(x, ADAPT_LAYER, weights, positions, adapters)
    for i in range(ADAPT_LAYER + 1, sm.N_LAYERS):
        if training:
            x = checkpoint(lambda z, j=i: sm.layer_forward(z, j, weights, positions, cache=None), x, use_reentrant=False)
        else:
            x = sm.layer_forward(x, i, weights, positions, cache=None)
    x = sm.rmsnorm(x, weights["model.norm.weight"])
    return F.linear(x, weights["model.embed_tokens.weight"])


def loss_for(row, tok, weights, adapters, training=True):
    ids, labels = make_example(tok, row)
    logits = forward_logits(ids, weights, adapters, training=training)
    return F.cross_entropy(logits.float().view(-1, logits.shape[-1]), labels.view(-1), ignore_index=-100)


@torch.no_grad()
def eval_loss(rows, tok, weights, adapters, limit=24):
    vals = []
    for row in rows[:limit]:
        vals.append(float(loss_for(row, tok, weights, adapters, training=False)))
    return sum(vals) / len(vals)

def save_adapter(adapters, path):
    state = {}
    for name, (A, B) in adapters.items():
        state[name + ".lora_A"] = A.detach().cpu()
        state[name + ".lora_B"] = B.detach().cpu()
    torch.save(state, path)


def main():
    train = read_jsonl(TRAIN_PATH)
    eval_rows = read_jsonl(EVAL_PATH)
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    weights = sm.load_weights(sm.ROOT)
    adapters = make_adapters(weights)
    params = [p for pair in adapters.values() for p in pair]
    print(f"trainable={sum(p.numel() for p in params)} vram_gb={torch.cuda.memory_allocated()/1024**3:.2f}", flush=True)
    optimizer = torch.optim.AdamW(params, lr=LR, weight_decay=0.0)
    baseline = eval_loss(eval_rows, tok, weights, adapters)
    print(f"eval_before={baseline:.6f}", flush=True)
    random.shuffle(train)
    t0 = time.time()
    losses = []
    for step in range(1, STEPS + 1):
        row = train[(step - 1) % len(train)]
        optimizer.zero_grad(set_to_none=True)
        loss = loss_for(row, tok, weights, adapters, training=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(params, 1.0)
        optimizer.step()
        losses.append(float(loss.detach()))
        if step == 1 or step % 5 == 0:
            print(f"step={step} loss={losses[-1]:.6f} avg5={sum(losses[-5:])/len(losses[-5:]):.6f} vram={torch.cuda.max_memory_allocated()/1024**3:.2f}", flush=True)
    final_eval = eval_loss(eval_rows, tok, weights, adapters)
    elapsed = time.time() - t0
    save_adapter(adapters, OUT / "adapter.pt")
    meta = {
        "base": str(sm.ROOT), "adapt_layer": ADAPT_LAYER, "projections": PROJS,
        "rank": RANK, "alpha": ALPHA, "steps": STEPS, "lr": LR,
        "trainable_parameters": sum(p.numel() for p in params),
        "eval_before": baseline, "eval_after": final_eval,
        "elapsed_seconds": elapsed, "seed": 1847,
    }
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)
    print("EGO_LORA_TRAIN_COMPLETE", flush=True)


if __name__ == "__main__":
    main()
