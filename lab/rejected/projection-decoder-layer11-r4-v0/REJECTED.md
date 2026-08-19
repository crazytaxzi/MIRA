# Projection Decoder v0 — REJECTED

This adapter was a detachable rank-4 child stacked on the frozen egocentric parent.
It was trained only to decode structured provenance / working-memory projections into ordinary conversation.

## Why it was tried
Text-only working-memory projection improved supported self-facts but did not reliably preserve UNKNOWN or pretend scope under leading questions.
The earlier rejected epistemic adapter had never been trained on the projection representation itself, so this narrower experiment was justified.

## Training result
- Trainable parameters: 53,248
- Layer: 11 q/k/v/o attention projections
- Rank 4, alpha 8
- LR: 1e-5
- Steps: 180
- Held-out projection loss: 1.3373 -> 1.2475
- Adapter SHA256: C76025E44B3E27863C2C587076A26B5F72BC308CC404645056C99AF813EE8A49

## Behavioral decision
Rejected. Loss improved more than the previous child, but unseen behavior remained unreliable.
UNKNOWN still collapsed into confident yes/no answers on many seeds; pretend scope remained inconsistent; corrected ownership remained poor.
One autonomy canary regressed from a noncompliant glare to `*sigh* Okay.`

A neural decoder that improves teacher loss but weakens autonomy or fails the actual epistemic transfer does not earn a place in the foundation.
