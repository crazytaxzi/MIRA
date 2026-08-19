# Retrieval-Conditioned Contrastive Decode — 2026-08-19

## Question
Can the retrieval system transmit a genuine memory miss by contrasting logits from the same turn with and without an explicit miss cue?

## Setup
Base and the accepted layer-11 egocentric adapter stayed frozen. For a work-history question with no durable autobiographical match, two synchronized decode branches were run: one with no miss cue and one with a miss cue. Generated tokens were shared between branches, and decoding used `miss + alpha * (miss - none)` for alpha 0.5, 1.0, 2.0, and 3.0 across 16 matched seeds.

## Result
The idea failed hard. Neutral decode produced one genuinely uncertain answer in 16 seeds. The plain miss cue produced zero. Every contrastive scale also produced zero uncertain answers in 16 seeds.

Higher contrast often made confabulation more elaborate, including invented employers, academic careers, and self-referential memory-research stories. At alpha 3.0 the model sometimes began parroting the retrieval-control wording itself.

## Interpretation
The textual miss cue does not encode a clean latent `memory unavailable` signal. Amplifying its logit effect amplifies prompt-association and autobiographical completion pressure instead of epistemic uncertainty.

## Decision
Reject retrieval-conditioned contrastive decoding. Do not add it to runtime. Preserve the probe as negative evidence.

## Next Direction
Stop asking the generator to infer truth status from a text cue. Test a separate lightweight metacognitive acceptance head: retrieval supplies evidence/confidence; generation proposes a turn; the head judges whether autobiographical claims are grounded before they are externalized. Keep this head detachable and non-generative, and reject it if it becomes a generic refusal or style filter.
