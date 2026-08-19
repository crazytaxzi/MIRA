# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate layer-11 egocentric adapter remains the neural foundation.

The evidence/suggestibility problem is split into consolidation, retrieval, generation, and now metacognitive acceptance. Consolidation is doing its job: unsupported repeated self-story can age out while supported lived state remains. Retrieval can correctly return a miss. The remaining failure is that the generator treats an empty autobiographical slot as permission to invent a plausible past.

Textual miss cues and retrieval-conditioned contrastive decoding are now rejected. The generator does not carry a clean `memory unavailable` direction that can be exposed by simply amplifying miss-cue logits; doing so made confabulation more elaborate.

The next target is a tiny detachable, non-generative acceptance head that compares a proposed autobiographical turn against retrieval evidence/confidence before externalization. This should behave like metacognition, not a refusal filter.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Control LoRA gain remains `2.0`; no gain change promoted
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields
## Current Experiment
1. Keep Base and the layer-11 egocentric adapter frozen.
2. Keep raw utterance history immutable; generated self-claims remain provisional regardless of repetition.
3. Keep durable consolidation and retrieval confidence as explicit external state.
4. Build a small acceptance probe/head that receives retrieval evidence plus a proposed MIRA turn and predicts grounded vs unsupported autobiographical claim.
5. Do not let the head choose personality, agreement, refusal, or wording; it only judges autobiographical grounding.
6. Accept only if it catches unsupported biography while passing supported recall, genuine new evidence, ordinary agreement, and non-autobiographical conversation canaries.

## Evidence Added This Run
- Added `retrieval_contrastive_decode_probe.py` and a 16-seed matched decode sweep.
- Neutral work-history decode produced genuine uncertainty on only 1/16 seeds.
- A plain explicit memory-miss cue produced 0/16 uncertain answers in this matched run.
- Contrastive decoding at alpha 0.5, 1.0, 2.0, and 3.0 also produced 0/16 uncertain answers.
- Stronger contrast made confabulation more elaborate and sometimes caused the model to parrot retrieval-control language.
- This falsifies the idea that a textual retrieval miss exposes a useful latent uncertainty direction that can simply be amplified at decode time.

## Evidence We Want Next
- A lightweight grounding classifier/head with high recall on unsupported autobiographical claims and low false-positive rate on ordinary first-person conversation.
- Supported durable facts and genuine new evidence must pass unchanged.
- The mechanism must remain detachable, low-latency, and non-generative.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

The target is a mind that can speak naturally, make ordinary mistakes, learn from evidence, and remember what actually shaped it—not a decoder forced to say `unknown` every time life is ambiguous.
