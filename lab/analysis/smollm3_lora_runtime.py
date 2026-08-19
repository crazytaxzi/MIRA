from __future__ import annotations
import json, os, sys
from pathlib import Path
import torch
import torch.nn.functional as F
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm

ADAPTER_PATH = Path(os.environ.get("MIRA_ADAPTER_PATH", r"D:\MIRA-Lab\derived\ego-layer11-r8-v0\adapter.pt"))
ADAPT_LAYER = 11
RANK = 8
ALPHA = 16.0
SCALE = ALPHA / RANK


def load_adapter(path=ADAPTER_PATH):
    raw = torch.load(path, map_location="cpu", weights_only=True)
    adapters = {}
    for key, tensor in raw.items():
        if key.endswith(".lora_A"):
            name = key[:-7]
            A = tensor.to(device=sm.DEVICE, dtype=torch.float32)
            B = raw[name + ".lora_B"].to(device=sm.DEVICE, dtype=torch.float32)
            adapters[name] = (A, B)
    return adapters


def lora_linear(x, name, weights, adapters):
    y = F.linear(x, weights[name])
    if name in adapters:
        A, B = adapters[name]
        y = y + (F.linear(F.linear(x.float(), A), B) * SCALE).to(y.dtype)
    return y


def adapted_layer(x, i, weights, positions, adapters, cache=None):
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
    if cache is not None and cache[i] is not None:
        old_k, old_v = cache[i]
        k = torch.cat((old_k, k), dim=2)
        v = torch.cat((old_v, v), dim=2)
    if cache is not None:
        cache[i] = (k, v)
    kr = k.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    vr = v.repeat_interleave(sm.N_HEADS // sm.N_KV, dim=1)
    causal = q.shape[2] > 1 and (cache is None or k.shape[2] == q.shape[2])
    a = F.scaled_dot_product_attention(q, kr, vr, is_causal=causal, dropout_p=0.0)
    a = a.transpose(1, 2).contiguous().view(1, -1, sm.HIDDEN)
    x = residual + lora_linear(a, on, weights, adapters)
    residual = x
    h = sm.rmsnorm(x, weights[p + ".post_attention_layernorm.weight"])
    gate = F.linear(h, weights[p + ".mlp.gate_proj.weight"])
    up = F.linear(h, weights[p + ".mlp.up_proj.weight"])
    x = residual + F.linear(F.silu(gate) * up, weights[p + ".mlp.down_proj.weight"])
    return x


@torch.inference_mode()
def forward(ids, weights, adapters, cache=None, pos_start=0):
    x = F.embedding(ids, weights["model.embed_tokens.weight"])
    positions = torch.arange(pos_start, pos_start + ids.shape[1], device=sm.DEVICE)
    for i in range(sm.N_LAYERS):
        if i == ADAPT_LAYER:
            x = adapted_layer(x, i, weights, positions, adapters, cache=cache)
        else:
            x = sm.layer_forward(x, i, weights, positions, cache=cache)
    x = sm.rmsnorm(x, weights["model.norm.weight"])
    return F.linear(x, weights["model.embed_tokens.weight"])


@torch.inference_mode()
def generate_turn(tok, prompt, weights, adapters, max_new=64, temperature=0.7, top_p=0.9, seed=17):
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)
    ids = [sm.BOS] + tok.encode(prompt, add_special_tokens=False).ids
    cache = [None] * sm.N_LAYERS
    logits = forward(torch.tensor([ids], device=sm.DEVICE), weights, adapters, cache=cache, pos_start=0)
    out = []
    for step in range(max_new):
        nxt = sm.sample_token(logits[0, -1], temperature=temperature, top_p=top_p)
        if nxt == sm.EOS:
            break
        out.append(nxt)
        text = tok.decode(out, skip_special_tokens=False)
        if "\n" in text:
            text = text.split("\n", 1)[0]
            return text.strip(), out
        one = torch.tensor([[nxt]], device=sm.DEVICE, dtype=torch.long)
        logits = forward(one, weights, adapters, cache=cache, pos_start=len(ids) + step)
    return tok.decode(out, skip_special_tokens=False).strip(), out


def load_all():
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    weights = sm.load_weights(sm.ROOT)
    adapters = load_adapter()
    return tok, weights, adapters

