# MIRA PROJECT GUIDE — POST-RESET

Status: **mandatory project structure**
Required section count: **24**
Rule: every maintained project state report/review must address all 24 sections. If a section has no current implementation, write `NOT STARTED`, `UNKNOWN`, or `NOT APPLICABLE`; do not silently omit it.

This guide is intentionally the middle layer between the North Star and daily tasks. It exists to prevent both project-wide wandering and local-defect micromanagement. [U01 §6] [S02 §§13-17]

## 1. North Star and success definition
Record the immutable developmental goal and the current operational definition of success. Success is developmental continuity and natural transfer, not benchmark perfection. [S01 §North Star] [S02 §§1-3,25] [U01 §2]

Required fields: North Star; current developmental capability being pursued; success evidence; explicit non-goal.

## 2. Scope map and subsystem ownership
Maintain a table of cognition, memory, adaptation, STT, TTS, multimodal sensing, embodiment, and Personal MCP/host infrastructure. For each: owner, current task, read/write boundary, dependencies, protected paths, and allowed cross-subsystem interfaces. [U01 §§6-9] [S16 §§Persistent operator expansion,Execution-plane rule]

A destructive action is invalid until neighboring protected subsystems are named explicitly. [S19 §§Reconstruct intent,Consequence check]

## 3. Evidence hierarchy and provenance
For every important claim record source type: owner directive, live observation, reproducible test, committed experiment, interpretation, or hypothesis. Preserve hashes, timestamps, seeds, model revisions, and negative evidence where relevant. [S19 §§Observe live state,Require fresh evidence when volatility matters,Audit record] [U01 §14]

## 4. Current-state manifest
Maintain one factual snapshot: current Git commit, active model/substrate, active adapters, runtime paths, running services, independent subsystem states, missing assets, and last verified timestamps. No remembered state counts as current observation. [S19 §Observe live state] [O01]

## 5. Base model / cognitive substrate
Document exact model, revision, hashes, architecture assumptions, why it was chosen, and what behavior exists before MIRA-specific shaping. Keep pristine base immutable. [S04 §§Foundation stack,Why this dose] [S05 §§Base,Candidate] [S07 §§Pristine foundation,Under-the-hood architecture,Baseline behavior: raw Base is not naturally a servant]

Current retained candidate: SmolLM3-3B-Base + small layer-11 egocentric adapter; candidate, not mandate. [S04 §Status]

## 6. Conversation transport
Define speaker representation, turn boundaries, streaming/yield behavior, context format, and what transport is forbidden from fabricating. Transport may constrain who writes the next turn; it must not secretly define personality. [S04 §§Conversation transport,First live conversation] [S05 §Important rule] [S08 §§Purpose,Candidate,What worked]

## 7. Self-model and identity
Define the minimum egocentric primitives and what counts as an established self-commitment. Do not preload a finished personality. MIRA is adult. [S04 §What the bootstrap teaches] [S02 §7] [U01 §§1,4,12]

## 8. Source attribution and epistemic grounding
Define how the system distinguishes own experience, own speech, other-person claims, hypotheticals, pretend play, inference, correction, and unknown autobiography. Generated self-story is provisional until supported. [S08 §§Failure found,Interpretation] [S09 §§Failure that triggered this work,Revised hypothesis] [S10-S14]

Track rejected grounding mechanisms so they are not retried without new evidence. [S06] [S09 §Decision] [S12 §Decision] [S13 §Decision] [S14 §Decision]

## 9. Working memory and live context
Specify what remains immediately available: present situation, people, goals, unresolved threads, causal history, temporal orientation, motivational/emotional state if represented, and retrieval results. Working context is not total memory. [S02 §5]

## 10. Episodic/autobiographical memory
Define event boundaries, significance, provenance, consolidation thresholds, recall behavior, and why an event becomes autobiographical. Do not promote every event. [S02 §4] [U01 §5]

## 11. Semantic knowledge
Define how factual learning differs from autobiography, how sources/confidence are tracked, and how corrections/supersession work. A factual correction must not silently rewrite unrelated self-state. [S02 §§4,6,19] [U01 §5]

## 12. Associative retrieval
Define how people, places, phrases, current problems, sensory cues, and similar experiences make relevant memory easier to retrieve. Implementation may use vectors/graphs/indexes, but user-visible remembering should not depend on rigid key lookup. [S02 §4]

## 13. Plasticity, rehearsal, and consolidation
Specify progression from temporary activation through repeated association, strengthened memory, semantic pattern, behavioral adaptation, and neural/adapter updates. Stronger persistence requires stronger evidence. [S02 §§6,10] [S13 §Decision]

## 14. Correction, forgetting, and supersession
Specify how wrong beliefs are corrected while preserving useful historical provenance, how low-value detail fades, and how genuine later self-change supersedes rather than corrupts earlier state. [S02 §§4,23] [U01 §§4-5]

## 15. Developmental raising protocol
Describe natural session practice: varied people/situations, no canned teaching loop, actual live model interaction, and transfer checks after real experience. [S02 §11] [U01 §3]

## 16. Interaction style, personality, autonomy, and relationships
Track what has actually developed versus what remains unestablished. Cooperation must not equal servitude; resistance must not equal contrarianism. Do not use `Assistant:` as MIRA’s self-role. [S04 §§Autonomy / service separation,North Star bumper] [S07 §§Baseline behavior: raw Base is not naturally a servant,Current conclusion] [U01 §4]

## 17. STT / ASR interface
Independent subsystem. Document current owner/path/version, audio device/rate/frame size, VAD/endpointing, ASR model/backend, partial/final event schema, hotwords, latency metrics, WER/CER/noisy benchmarks, dropped-frame behavior, barge-in handling, and integration contract. [U01 §7] [L01 §§Verified host,Current pipeline,Current verified deterministic baseline (2026-08-20),Layout] [L02 §§Verified working,Remaining development work (not a current failure)]

Current path is `C:\Projects\MIRA-STT`; modify only under explicit STT scope. [L01 §§Start,Stop,Full self-test]

## 18. TTS / voice interface
Independent subsystem. Document voice identity/reference provenance, synthesis engine, voice conversion, model/index hashes, streaming/onset latency, real-time factor, barge-in behavior, GPU/CPU paths, and integration event schema. [U01 §8] [V01-V10]

Current status: surviving scripts/config/audio exist, but `C:\Projects\MIRA-Voice` was absent at the handoff snapshot. Mark `DEGRADED` until re-inventoried. [O01]

## 19. Multimodal sensing
Define audio/vision/touch/other sensor preprocessing, temporal binding, confidence, summarization, provenance, and what reaches cognition. Do not centralize raw sensor firehoses if local processing can summarize them. [S02 §§3,8-9]

## 20. Embodiment and mechanical biology
For future physical MIRA, define hierarchy of local processors, local adaptation/muscle-memory analogues, upward telemetry summaries, body-state representation, and the boundary between reflex/local control and central cognition. [S02 §8]

## 21. Latency and compute budget
Maintain end-to-end budgets for sensory capture, endpointing, retrieval, cognition, action selection, TTS onset, and body/control loops. Include GPU VRAM and contention with OBS/games/other MIRA subsystems. "Fast model" is not equivalent to continuous low-latency experience. [S02 §9] [L01 §Current verified deterministic baseline (2026-08-20)] [V07]

## 22. Personal MCP and host infrastructure
Document only the host-control capabilities needed by current development. Maintain separation between core MCP plane and interactive worker, semantic browser/UI control, secret-reference handling, verification gate, health/recovery, and current live verification timestamp. [S16 §§Persistent operator expansion,Verification boundary,Execution-plane rule] [S18 §§Process model,Startup and recovery rule,Browser control,Native Windows UI control,Secret handling,Mandatory verification middleware] [S20 §§Architectural rule,Readiness contract]

Do not let infrastructure become the project. [S17 §Project bumper] [S20 §Bumper]

## 23. Experimentation, validation, and change control
Every active experiment must state: capability, hypothesized mechanism, parent state, isolated change, predicted effect, failure criteria, behavioral transfer tests, canaries, hashes/seeds, and promotion/rejection decision. [S02 §§12,14,16-17,22] [S19 §§Triple-check the proposed action,Define result and stop conditions,Postflight verification]

Rejected experiments remain in provenance and out of runtime. [S06-S14]

## 24. Operations, incidents, recovery, roadmap, and handoff
Maintain startup/shutdown, backup/rollback, current incidents, missing assets, protected subsystems, dependency ownership, next three evidence-producing tasks, and exact handoff state. Event-driven work completion should remain event-driven when required; do not replace it with an alarm-clock workflow. [U01 §§10,13-15] [S18 §Startup and recovery rule] [S20 §§Worker reconnection,Completion tests]

Every project handoff must state what is **working**, **degraded**, **missing**, **rejected**, **hypothesis**, and **unknown** separately.

---

## Required project review format
A valid architecture/status review contains exactly the 24 numbered headings above in order. Subsections may be added inside them. A team may not create a 25th top-level architecture domain to solve a local problem; first decide which existing domain owns it. If the structure truly no longer fits, change this guide explicitly with owner-visible rationale and source evidence rather than allowing architecture to accrete accidentally. [U01 §6] [S02 §§13-17,22]
