from __future__ import annotations
import json, sys, time
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, r"D:\MIRA-Lab\analysis")
import smollm3_direct as sm
import smollm3_lora_runtime as lr

ADAPTER = Path(r"D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt")
SESSION_DIR = Path(r"D:\MIRA-Lab\sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG = SESSION_DIR / f"foundation_{STAMP}.jsonl"


def write_event(kind, **data):
    row = {"utc": datetime.now(timezone.utc).isoformat(), "kind": kind, **data}
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    tok = sm.Tokenizer.from_file(str(sm.ROOT / "tokenizer.json"))
    weights = sm.load_weights(sm.ROOT)
    adapter = lr.load_adapter(ADAPTER)
    transcript = []
    write_event("start", base=str(sm.ROOT), adapter=str(ADAPTER))
    print(f"MIRA FOUNDATION READY log={LOG}", flush=True)
    seed = 1847
    while True:
        try:
            text = input("Cinder> ")
        except (EOFError, KeyboardInterrupt):
            print("", flush=True)
            break
        if not text.strip():
            continue
        if text.strip().lower() in {"/quit", "/exit"}:
            break
        transcript.append(f"Cinder: {text.strip()}")
        prompt = "\n".join(transcript) + "\nMira:"
        reply, _ = lr.generate_turn(tok, prompt, weights, adapter,
                                    max_new=96, temperature=0.75,
                                    top_p=0.90, seed=seed)
        seed += 1
        reply = reply.strip()
        print(f"Mira> {reply}", flush=True)
        transcript.append(f"Mira: {reply}")
        write_event("turn", cinder=text.strip(), mira=reply,
                    transcript_turns=len(transcript))
    write_event("stop", transcript_turns=len(transcript))


if __name__ == "__main__":
    main()
