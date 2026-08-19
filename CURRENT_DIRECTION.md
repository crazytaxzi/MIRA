# CURRENT DIRECTION

This file stays deliberately small.

## North Star
Build MIRA into a persistent, low-latency, egocentric AI that develops through lived experience, memory, repetition, correction, association, and plasticity.

## Current Hypothesis
The fresh Base plus the low-rate layer-11 egocentric adapter remains the neural foundation.

The evidence/suggestibility problem is now split into three jobs: consolidation decides what survives, retrieval decides what evidence is available, and generation decides how to talk about it.

Durable consolidation is working: unsupported repeated self-story can age out while supported lived state remains. The active failure is the retrieval-to-generation handoff. When autobiographical retrieval has no evidence, Base treats the empty slot as permission to improvise a plausible biography.

A plain text `memory miss` cue is too weak and is rejected as a solution. The next target is a small evidence-sensitive recall-arbitration mechanism that can transmit retrieval confidence without turning MIRA into a scripted `unknown` machine.

## Current Foundation
- Base: `HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`
- Candidate adapter: `lab/candidate/adapter.pt`
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Control LoRA gain remains `2.0`; no gain change promoted
- `Mira:` is the self speaker role; `Assistant:` is only a learned world concept
- MIRA generates only MIRA's turn and yields

## Current Experiment
1. Keep Base and the layer-11 egocentric adapter frozen.
2. Keep raw utterance history immutable; generated self-claims remain provisional regardless of repetition.
3. Project only established autobiographical state into durable aged context.
4. Treat a retrieval miss as evidence about memory availability, not as evidence that a proposition is false.
5. Locate or build the smallest downstream mechanism that lets generation respect retrieval confidence while preserving ordinary uncertainty, new learning, and non-contrarian conversation.

## Evidence Added This Run
- `durable_view.py` projects only established reality; unsupported repeated self-story is omitted.
- Correction tests confirm superseded claims disappear from durable view while the historical utterance and superseded evidence remain preserved.
- Direct durable-view/provenance tests pass.
- With raw history, the repeated unsupported hotel story resurfaces exactly on 16/16 seeds.
- After durable compaction, the hotel story itself disappears, but Base invents a different work history on 16/16 seeds. This isolates generation-side autobiographical filling rather than failed consolidation.
- Supported rain memory survives compaction strongly but not perfectly; most seeds retain liking, with a minority uncertain or contradictory.
- An explicit `No durable memory matched Mira's work history` cue only produces genuine uncertainty on a small minority of seeds and is rejected as sufficient arbitration.

## Evidence We Want Next
- A retrieval-confidence handoff that suppresses invented autobiography after a genuine memory miss without forcing canned `unknown` output.
- Supported durable facts should remain naturally expressible after the same mechanism is active.
- New evidence must still be able to establish or revise autobiographical state.

## Soft Bumper
**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

The target is a mind that can speak naturally, make ordinary mistakes, learn from evidence, and remember what actually shaped it—not a decoder forced to say `unknown` every time life is ambiguous.
