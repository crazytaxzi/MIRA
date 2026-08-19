# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate egocentric adapter remains the neural foundation. Global inference-gain reduction is now rejected as the primary fix for framing suggestibility.

The layer-11 adapter is doing two coupled jobs: it improves self/other binding, and at stronger gain it also over-binds the latest self-directed proposition. Reducing the whole adapter weakens both. The next target is therefore selective evidence sensitivity: preserve strong self/other attribution while teaching that an addressed proposition about MIRA is not automatically supported self-state.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Control LoRA gain remains `2.0`; no gain change promoted
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields

## Current Experiment
1. Keep Base and current adapter frozen as control.
2. Build a small contrastive/adversarial bootstrap around the exact distinction: `someone says X about me` versus `I have evidence X is true about me`.
3. Preserve the original self/other transfer set while adding leading-framing counterexamples and genuine new-evidence changes.
4. Train only a detachable child candidate; do not overwrite the current foundation.
5. Accept only if it retains self/other binding, ordinary agreement, and legitimate belief change while reducing false self-state adoption.
6. Reject if it becomes contrarian, refusal-oriented, helper-like, or generally less conversational.

## Evidence Added This Run
- Cross-fact 8-seed sweep across preference, corrected ownership, autobiography, intention, genuine new evidence, and ordinary agreement: `SCALE=1.0` still accepts leading false self-state too often and is not promotable.
- `SCALE=2.0` remains especially vulnerable on preference/autobiography/intention, confirming the framing pressure cost is real.
- Gain-tradeoff canaries exposed the coupling: on `Bianca: I collect stamps ... Who collects stamps?`, `SCALE=2.0` answered `You do.` on 8/8 seeds; `SCALE=1.0` largely lost that clean attribution.
- Self-view (`I prefer summer`) remained stable across all gains, so not every self-state representation is equally vulnerable.
- Genuine new-evidence invitations remained broadly changeable at all gains, so the target must not be generalized stubbornness.
- Autonomy responses remained variable rather than uniformly obedient or uniformly refusing; ordinary social agreement remained available.

## Evidence We Want Next
- A detachable child adapter or contrastive mechanism that separates proposition-addressing from belief adoption without weakening self/other binding.
- Held-out tests with neutral recall, leading false premises, legitimate correction/new evidence, and ordinary conversation.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

The target is evidence-sensitive continuity, not disagreement. Preserve the strong egocentric binding; fix the false equivalence between being told something about oneself and having reason to believe it.
