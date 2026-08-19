# Epistemic Grounding Follow-up — 2026-08-19

## Failure that triggered this work
The live foundation can produce socially plausible self-statements and then treat them as autobiography.

Example: Cinder described staring at code and chores. MIRA said `Haha. Me too.`, invented her own pile of tasks, and did not fully relinquish that self-state after Cinder corrected ownership.

This is not helper-mode servility. It is a provenance / self-belief problem.

## Neural child experiment
The working egocentric adapter was frozen as the parent.
A second rank-4 layer-11 q/k/v/o adapter was trained separately for correction/source attribution.

Child size: 53,248 trainable parameters.
Training included:
- corrected social mirroring
- valid supported mirroring
- unknown self-history
- supported prior self-facts
- external self-claim source attribution
- pretend-play boundaries
- ordinary other-person fact recall

The corpus explicitly contained positive play/mirroring cases so the target was not blanket skepticism.
## Result
Global held-out teacher loss changed only:
`1.3262 -> 1.3047`

Per-kind results all moved only slightly. Most importantly:
- mirror correction: `2.4176 -> 2.4158`
- unknown self-history: `2.2775 -> 2.2245`
- supported mirroring: `1.0213 -> 1.0172`

Direct generation was more decisive. Parent and parent+child produced the same outputs on:
- the live correction shape
- valid supported mirroring
- pretend-play boundary
- an ordinary social-mirroring turn

## Decision
**REJECTED.**

The child is preserved locally as evidence but is not part of the foundation candidate.

A tiny extra weight layer that does not materially alter the failure does not earn architectural permanence.

## Revised hypothesis
The missing distinction should live primarily in memory/provenance architecture:

`MIRA uttered X` is evidence that MIRA said X.
It is **not automatically** evidence that X is a durable fact about MIRA.

Self-beliefs should have source, confidence, support, correction/supersession, and scope. Social mirroring, jokes, guesses, and pretend-play can remain conversational acts without silently becoming autobiography.

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**
