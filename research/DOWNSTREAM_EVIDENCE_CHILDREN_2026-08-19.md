# Downstream Evidence Children — 2026-08-19

## Question
Does the strong supported-vs-asserted separation that reappears around layers 18-20 provide a better place for a tiny evidence-arbitration child than layer 11?

## Matched Setup
Both tests froze Base and the accepted layer-11 egocentric parent. Each child targeted q/k/v/o attention projections only, rank 4, alpha 8, LR 5e-6, 120 steps, seed 19027, 53,248 trainable parameters, using the same 500/120 evidence-contrast corpus.

## Training
Layer 18: held-out CE `3.135735 -> 3.119415`.
Layer 20: held-out CE `3.135735 -> 3.123776`.

## Behavioral Result
Each child was compared against the parent over 11 prompt classes x 8 matched seeds = 88 generations.

Both children produced exactly the same text as the parent on all 88 generations.
Unsupported preference remained accepted 8/8. Unsupported biography remained accepted 8/8. Corrected ownership remained wrong 8/8. Supported preference/biography, genuine new-evidence responses, ordinary agreement, other/self attribution, autonomy variability, and non-helper greetings were unchanged.

## Decision
Reject both children. Preserve weights and metadata for provenance, but do not stack either onto MIRA.

## Interpretation
Linear or centroid separability tells us that a distinction exists in a representation; it does not prove that ordinary LoRA pressure on that representation has causal leverage over the final token decision. Training by geometry alone is another squirrel.

## Next Experiment
Use causal residual/activation interventions across downstream layers. Derive a supported-vs-asserted evidence direction, inject small signed perturbations, and measure whether false self-state adoption moves before attribution, legitimate belief updates, autonomy, or natural conversation degrade. Only train where causal leverage has been demonstrated.
