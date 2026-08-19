from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import torch
import torch.nn.functional as F
from safetensors import safe_open
import sys
GLOBAL310 = r'C:\Users\crazy\AppData\Local\Programs\Python\Python310\Lib\site-packages'
if GLOBAL310 not in sys.path:
    sys.path.insert(0, GLOBAL310)
from tokenizers import Tokenizer

ROOT = Path(r"D:\MIRA-Lab\base\SmolLM3-3B-Base")
DEVICE = "cuda"
DTYPE = torch.bfloat16
HIDDEN = 2048
INTER = 11008
N_LAYERS = 36
N_HEADS = 16
N_KV = 4
HEAD_DIM = 128
ROPE_THETA = 5_000_000.0
RMS_EPS = 1e-6
BOS = 128000
EOS = 128001


def rmsnorm(x, w):
    y = x.float()
    y = y * torch.rsqrt(y.pow(2).mean(-1, keepdim=True) + RMS_EPS)
    return y.to(x.dtype) * w


def rotate_half(x):
    a, b = x[..., :HEAD_DIM // 2], x[..., HEAD_DIM // 2:]
    return torch.cat((-b, a), dim=-1)


def rope(q, k, positions):
    inv = 1.0 / (ROPE_THETA ** (torch.arange(0, HEAD_DIM, 2, device=q.device, dtype=torch.float32) / HEAD_DIM))
    freqs = positions.float()[:, None] * inv[None, :]
    emb = torch.cat((freqs, freqs), dim=-1)
    cos = emb.cos().to(q.dtype)[None, None, :, :]
    sin = emb.sin().to(q.dtype)[None, None, :, :]
    return q * cos + rotate_half(q) * sin, k * cos + rotate_half(k) * sin


def load_weights(root: Path):
    idx = json.loads((root / "model.safetensors.index.json").read_text())
    by_file = {}
    for name, fn in idx["weight_map"].items():
        by_file.setdefault(fn, []).append(name)
    weights = {}
    for fn, names in by_file.items():
        print(f"loading {fn} ({len(names)} tensors)", flush=True)
        with safe_open(str(root / fn), framework="pt", device="cpu") as f:
            for name in names:
                weights[name] = f.get_tensor(name).to(device=DEVICE, dtype=DTYPE)
    return weights


def linear(x, w, weights):
    return F.linear(x, weights[w])


def layer_forward(x, i, weights, positions, cache=None):
    p = f"model.layers.{i}"
    residual = x
    h = rmsnorm(x, weights[p + ".input_layernorm.weight"])
    q = linear(h, p + ".self_attn.q_proj.weight", weights).view(1, -1, N_HEADS, HEAD_DIM).transpose(1, 2)
    k = linear(h, p + ".self_attn.k_proj.weight", weights).view(1, -1, N_KV, HEAD_DIM).transpose(1, 2)
    v = linear(h, p + ".self_attn.v_proj.weight", weights).view(1, -1, N_KV, HEAD_DIM).transpose(1, 2)
    if (i + 1) % 4 != 0:
        q, k = rope(q, k, positions)
    if cache is not None and cache[i] is not None:
        old_k, old_v = cache[i]
        k = torch.cat((old_k, k), dim=2)
        v = torch.cat((old_v, v), dim=2)
    if cache is not None:
        cache[i] = (k, v)
    kr = k.repeat_interleave(N_HEADS // N_KV, dim=1)
    vr = v.repeat_interleave(N_HEADS // N_KV, dim=1)
    causal = q.shape[2] > 1 and (cache is None or k.shape[2] == q.shape[2])
    a = F.scaled_dot_product_attention(q, kr, vr, is_causal=causal, dropout_p=0.0)
    a = a.transpose(1, 2).contiguous().view(1, -1, HIDDEN)
    x = residual + linear(a, p + ".self_attn.o_proj.weight", weights)
    residual = x
    h = rmsnorm(x, weights[p + ".post_attention_layernorm.weight"])
    gate = linear(h, p + ".mlp.gate_proj.weight", weights)
    up = linear(h, p + ".mlp.up_proj.weight", weights)
    h = F.silu(gate) * up
    x = residual + linear(h, p + ".mlp.down_proj.weight", weights)
    return x


@torch.inference_mode()
def forward(ids, weights, cache=None, capture=False, pos_start=0):
    x = F.embedding(ids, weights["model.embed_tokens.weight"])
    positions = torch.arange(pos_start, pos_start + ids.shape[1], device=DEVICE)
    captures = []
    for i in range(N_LAYERS):
        x = layer_forward(x, i, weights, positions, cache=cache)
        if capture:
            v = x[0, -1].float()
            captures.append({"layer": i, "norm": float(v.norm()), "mean": float(v.mean()), "std": float(v.std())})
    x = rmsnorm(x, weights["model.norm.weight"])
    logits = F.linear(x, weights["model.embed_tokens.weight"])
    return logits, captures


def encode(tok, text, use_bos):
    ids = tok.encode(text, add_special_tokens=False).ids
    if use_bos:
        ids = [BOS] + ids
    return ids


def sample_token(logits, temperature=0.0, top_p=0.95):
    if temperature <= 0:
        return int(torch.argmax(logits).item())
    probs = torch.softmax(logits.float() / temperature, dim=-1)
    sorted_p, sorted_i = torch.sort(probs, descending=True)
    keep = torch.cumsum(sorted_p, dim=-1) <= top_p
    keep[0] = True
    filtered = sorted_p * keep
    filtered = filtered / filtered.sum()
    choice = torch.multinomial(filtered, 1)
    return int(sorted_i[choice].item())


def top_tokens(tok, logits, k=20):
    vals, ids = torch.topk(logits.float(), k)
    return [{"id": int(i), "token": tok.decode([int(i)], skip_special_tokens=False), "logit": float(v)} for v, i in zip(vals, ids)]


@torch.inference_mode()
def generate(tok, prompt, weights, max_new=48, temperature=0.0, top_p=0.95, use_bos=True):
    ids = encode(tok, prompt, use_bos)
    x = torch.tensor([ids], device=DEVICE, dtype=torch.long)
    cache = [None] * N_LAYERS
    logits, captures = forward(x, weights, cache=cache, capture=True, pos_start=0)
    first_top = top_tokens(tok, logits[0, -1], 20)
    out = []
    t0 = time.time()
    for step in range(max_new):
        nxt = sample_token(logits[0, -1], temperature=temperature, top_p=top_p)
        out.append(nxt)
        if nxt == EOS:
            break
        one = torch.tensor([[nxt]], device=DEVICE, dtype=torch.long)
        logits, _ = forward(one, weights, cache=cache, capture=False, pos_start=len(ids) + step)
    elapsed = time.time() - t0
    return {
        "prompt": prompt,
        "use_bos": use_bos,
        "prompt_tokens": len(ids),
        "generated_ids": out,
        "generated_text": tok.decode(out, skip_special_tokens=False),
        "first_token_top20": first_top,
        "layer_last_token_stats": captures,
        "generation_seconds": elapsed,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--max-new", type=int, default=48)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--no-bos", action="store_true")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    torch.manual_seed(17)
    torch.cuda.manual_seed_all(17)
    tok = Tokenizer.from_file(str(ROOT / "tokenizer.json"))
    weights = load_weights(ROOT)
    print(f"loaded tensors={len(weights)} vram_gb={torch.cuda.memory_allocated()/1024**3:.2f}", flush=True)
    result = generate(tok, args.prompt, weights, args.max_new, args.temperature, args.top_p, not args.no_bos)
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()

