# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate egocentric adapter remains the neural foundation, but the current full inference gain is likely too strong.

Pristine Base is already vulnerable to leading self-directed wording. The adapter did not create that defect; it improves neutral self/other binding while also amplifying acceptance of the latest addressed proposition. Layer-11 inspection suggests broad over-binding of turn/self structure and predicate content rather than a single negation failure.

A pure working-memory wording fix failed. A reversible LoRA gain sweep is more promising: `SCALE=1.0` (half the current `2.0`) kept neutral rain recall stable across the 16-seed probe while restoring some resistance/qualification under contradictory framing. This is an experimental candidate only, not a promoted foundation.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Production/control LoRA gain remains `2.0` until broader evidence supports a change
- Experimental gain candidate: `1.0`
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields

## Current Experiment
1. Keep Base and adapter weights frozen.
2. Compare `SCALE=1.0` against Base (`0.0`) and current full gain (`2.0`) across multiple self-state types.
3. Include preference, corrected ownership, autobiographical fact, current intention, and genuine new-evidence cases.
4. Keep provenance/correction as the durable source of self-state.
5. Require legitimate belief change to remain possible.
6. Reject any setting that merely makes MIRA contrarian, stubborn, refusal-oriented, or helper-like.

## Evidence Added This Run
- Greedy matched probe: Base and adapter both flip under contradictory framing, proving the defect exists in pristine Base.
- 16-seed matched comparison: full-gain adapter accepted the false leading rain premise on 16/16 seeds; pristine Base sometimes resisted, qualified, or reaffirmed the supported preference.
- Layer-wise trajectories are identical through layer 10 and diverge at layer 11, exactly where the LoRA acts.
- Token-level LoRA influence is distributed across speaker/turn boundaries and proposition tokens, especially the value path; no single negation-specific culprit emerged.
- Stronger provenance wording alone failed: 16/16 false-premise acceptance remained.
- Gain sweep (`0.0, 0.5, 1.0, 1.5, 2.0`) exposed a tradeoff. Full gain is the worst suggestibility case. `1.0` preserved strong neutral recall while recovering some resistance.

## Evidence We Want Next
- Broader cross-fact scale comparison before changing the foundation runtime.
- A real change-of-mind case where new evidence should defeat prior self-state.
- Autonomy and ordinary-agreement canaries at reduced gain.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

The target is evidence-sensitive continuity, not disagreement. Prior supported self-state should beat mere phrasing pressure, while actual new evidence must still be able to change it.
