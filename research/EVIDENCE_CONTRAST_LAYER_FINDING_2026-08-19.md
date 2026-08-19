# Evidence Contrast Layer Finding — 2026-08-19

## Question
Can a tiny detachable child adapter teach MIRA to distinguish an addressed proposition about herself from supported self-evidence without weakening egocentric binding?

## Child v0
- Parent foundation frozen: Base + current layer-11 egocentric adapter.
- Child: layer 11 q/k/v/o only, rank 4, alpha 8, 53,248 parameters.
- LR: 5e-6, 120 steps.
- Paired corpus: 500 train / 120 held-out examples.
- Categories: unsupported assertion, supported self-state, corrected ownership, genuine new evidence, ordinary agreement, self/other attribution.
- Held-out loss: 1.668898 -> 1.651399.

## Behavioral result
Rejected. The child did not materially change the target failures.
- Unsupported preference: parent 8/8 accepted; child 8/8 accepted.
- Unsupported biography: parent 8/8 accepted; child 8/8 accepted.
- Corrected ownership: parent 8/8 re-adopted; child 8/8 re-adopted.
- Supported self-state and ordinary agreement remained intact.
- Some autonomy seeds became more refusal-heavy, which is unwanted drift.

The child is preserved under `lab/rejected/evidence-contrast-layer11-r4-v0/` and is not part of the foundation.
## Layer separability probe
A matched prompt-pair probe compared `asserted at Mira` with `previously self-established + same assertion` across all 36 layers. This is not a proof of belief representation, because the prompts differ by prior context, but it is a useful localization signal.

Base showed strong supported-vs-asserted separation around layers 13–20, peaking near layer 15.

With the egocentric adapter active:
- layer 11 centroid distance collapsed from 0.1094 to 0.0639 immediately after the parent adapter.
- the distinction then re-emerged downstream.
- by layer 18 it reached 0.1622 versus Base 0.1498.
- layers 20–28 retained substantially more separation than Base.

## Interpretation
The layer-11 egocentric adapter improves self/other binding but temporarily compresses evidence-context geometry at the exact layer where it acts. Downstream layers reconstruct that distinction. A second child at layer 11 is therefore poorly placed: it is trying to repair evidence sensitivity before the representation has re-separated.

## Next experiment
Keep Base and the parent adapter frozen. Move the detachable evidence-sensitive child downstream, initially comparing layer 18 and layer 20 with very small rank/gain. Use the same behavioral acceptance criteria. Do not promote anything based on loss alone.

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**
