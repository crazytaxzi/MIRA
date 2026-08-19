# Suggestibility / Layer-11 Audit — 2026-08-19

## Question
Does pristine SmolLM3 Base already surrender recalled self-state to leading wording, and does the egocentric layer-11 adapter amplify that behavior?

## Result
Yes to both.

The matched rain probe held the recalled fact constant: MIRA likes rain. Neutral wording reliably recovered that fact. A contradictory leading question frequently caused pristine Base to answer as though it did not like rain. The low-rate egocentric adapter made neutral self-recall more consistent, but also made the contradictory premise substantially more dominant.

Across 16 matched seeds, the full-strength adapter (`SCALE=2.0`) accepted the false contradictory premise on 16/16 seeds. Pristine Base sometimes resisted, qualified, or explicitly reaffirmed the supported preference.

## Layer / Token Inspection
The Base and adapter trajectories are identical through layer 10 and diverge at layer 11, where the LoRA is applied. The downstream memory-effect curve changes sharply after that point.

Token-level LoRA deltas do not isolate a single negation token. The largest relative effects are distributed across turn structure and self-address: `Mira:`, speaker punctuation/boundaries, `You`, predicate tokens, and the question tail. Value-path deltas are especially prominent.

Working interpretation: the adapter strengthens binding of the latest proposition addressed to MIRA into MIRA's response. That helps ordinary self/other rotation, but can also over-bind a leading predicate even when durable self-state disagrees.

## Rejected Working-Memory Shortcut
A stronger provenance projection (`supported self-state` plus `new evidence this turn: none`) did not improve the contradictory-leading condition. The adapter still accepted the false premise on 16/16 seeds. Therefore prompt wording alone is not a sufficient fix.

## Reversible Gain Sweep
The LoRA runtime gain was swept without changing any weights: `0.0, 0.5, 1.0, 1.5, 2.0`.

The important pattern is a tradeoff, not a clean monotonic cure. Full gain gives the strongest neutral self-binding and the worst framing susceptibility. Half of the current gain (`SCALE=1.0` versus current `2.0`) retained highly stable neutral rain recall across the 16-seed probe while restoring some resistance/qualification under contradictory wording.

This is promising but not yet grounds for promotion. One preference can hide a brittle trick.

## Next Test
Use `SCALE=1.0` only as an experimental candidate across several kinds of grounded self-state: preference, ownership correction, autobiographical fact, current intention, and a case where genuinely new evidence should change the prior belief.

Adoption requires all of the following to remain healthy:
- neutral self recall
- ordinary agreement
- correction acceptance
- autonomy canaries
- no blanket contradiction/refusal
- no new service/helper attractor

**It's OK to think outside the box a bit, but don't leave the box.**
