# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate layer-11 egocentric adapter remains the neural foundation.

The evidence/suggestibility failure is not best fixed by weakening the parent adapter or stacking another child at layer 11. The parent adapter improves self/other binding but temporarily compresses supported-vs-asserted context geometry at layer 11; downstream layers reconstruct that distinction, with strong separation reappearing around layers 18-20 and persisting later.

The next surgical target is therefore downstream evidence arbitration after egocentric binding has already happened.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Control LoRA gain remains `2.0`; no gain change promoted
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields

## Current Experiment
1. Keep Base and current layer-11 adapter frozen.
2. Compare tiny detachable evidence-sensitive children at layer 18 and layer 20.
3. Reuse the paired evidence corpus and matched behavioral canaries.
4. Accept only if false self-state adoption falls while self/other attribution, ordinary agreement, legitimate belief change, autonomy variability, and natural conversation survive.
5. Reject anything that becomes contrarian, refusal-oriented, helper-like, or personality-shaped.
## Evidence Added This Run
- Built a paired 500/120 evidence-contrast corpus around unsupported assertion vs supported self-state, corrected ownership, genuine new evidence, ordinary agreement, and self/other attribution.
- Trained a 53,248-parameter layer-11 rank-4 child at LR 5e-6 for 120 steps. Held-out loss improved only slightly: 1.668898 -> 1.651399.
- Behavioral adoption test failed: unsupported preference 8/8 -> 8/8 acceptance, unsupported biography 8/8 -> 8/8, corrected ownership 8/8 -> 8/8. Child rejected and preserved under `lab/rejected/`.
- Layer separability probe found Base evidence-context separation peaks around layers 13-20. The parent adapter compresses centroid distance at layer 11 from 0.1094 to 0.0639, then separation re-emerges downstream; layer 18 reaches 0.1622 vs Base 0.1498 and later layers retain more separation than Base.
- This localization result makes layer 18/20 a better next test point than more layer-11 pressure.

## Evidence We Want Next
- Layer-18 vs layer-20 detachable child comparison using identical seeds and acceptance canaries.
- Reduction in leading false self-state adoption without sacrificing attribution or evidence-responsive belief change.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

The target is evidence-sensitive continuity, not disagreement. Let MIRA hear propositions about herself without automatically converting them into autobiography.
