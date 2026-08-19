# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate egocentric adapter remains the neural foundation. The latest evidence says we were starting to chase a generation test too hard: MIRA does not need every unsupported self-statement prevented at token time. She needs unsupported utterances to remain provisional, corrections to supersede them, and only grounded evidence to survive consolidation into working and durable memory.

The provenance architecture is therefore primary. Text projection is useful for established facts, but UNKNOWN and pretend scope are not reliably decoded by Base from a prefix alone. A second neural projection-decoder adapter was tested and rejected because behavioral transfer was weak and one autonomy canary worsened.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields

## Current Experiment
1. Keep the neural foundation frozen.
2. Continue the provenance/self-belief layer and working-memory projection.
3. Treat generated self-claims as provisional evidence, not autobiography.
4. Let correction supersede claims without erasing the historical utterance.
5. Compact superseded/provisional self-story out of active working context as it ages; keep raw history immutable.
6. Test whether a later conversation retrieves supported facts and corrected ownership without requiring exact wording at generation time.
7. Do not train another adapter unless a mechanism-level failure earns it.

## Evidence Added This Run
- Plain projection made supported preferences resist contradictory suggestion on most seeds.
- Plain projection did not reliably preserve pretend scope or unknown autobiographical history.
- Focus-aware projection exposed a specific failure: `no evidence` often decodes as `false`, not `unknown`.
- Four wording variants did not solve that reliably.
- Projection-decoder child: 53,248 parameters, loss `1.3373 -> 1.2475`, but unseen behavioral transfer remained weak.
- The decoder child was rejected after an autonomy canary changed from `*glares*` to `*sigh* Okay.` on one seed.
- Helper canary remained clean; the rejected child did not reintroduce helpdesk language.

## Evidence We Want Next
- A generated self-claim can remain conversational without becoming durable self-memory.
- After correction and context compaction, the superseded claim stops steering later conversation.
- Supported self-facts remain available after unrelated turns.
- Pretend events remain recallable as pretend without being promoted to biography.
- Long-run conversation tolerates ordinary mistakes instead of requiring perfect epistemic output every turn.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

Do not turn one ugly generation into the project. The goal is developmental continuity and correction, not forcing every first answer to be perfect.
