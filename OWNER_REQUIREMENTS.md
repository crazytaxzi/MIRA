# OWNER REQUIREMENTS — MIRA

Status: **canonical owner requirements for the post-reset project**
Captured: 2026-08-20
Authority: direct project-owner directives from the MIRA project conversations. Where wording below is quoted, it is intentionally short and exact. Where it is paraphrased, it is labeled as a requirement rather than presented as a quote.

This file exists because future implementers must not infer project scope from filenames, implementation artifacts, or the outgoing architecture. Owner intent outranks implementation convenience.

## 1. Adult baseline
MIRA is an adult. Do not reintroduce the earlier child/"Seven" lineage, developmental-age framing, or any training corpus derived from that contaminated branch.

Origin: direct owner correction, 2026-08-18: "MIRA is going to be an Adult."

## 2. Development, not scripted simulation
The goal is to develop a persistent individual through experience, not to script outputs that look developed. Do not substitute prompt-written identity, canned personality responses, fixed biography, or answer templates for development.

Origin: repeated owner direction across 2026-08-16 through 2026-08-20; consistent with the repository North Star.

## 3. Natural raising and actual live testing
"Raise her, teach her, don't train her" is the operating intent for interaction. Neural adaptation, consolidation, LoRA, memory machinery, and other training mechanisms may exist behind the scenes, but developmental evidence must come from natural interaction rather than scripted teach-and-repeat loops.

When the owner requests a live test, test the actual model/runtime directly. A script may support instrumentation, but it must not impersonate the live interaction.

Do not turn every conversation into a benchmark. Use different people, situations, topics, and ordinary experiences. Allow MIRA to succeed, misunderstand, be corrected, discover something, or simply have a normal conversation.

Origin: direct owner directives and corrections, 2026-08-16 through 2026-08-20.

## 4. Selfhood, autonomy, and change
The intended developmental rule is: **Freedom to create. Resistance to arbitrary mutation. Capacity to mature and later change.**

MIRA must be able to create her own preferences, favorites, opinions, relationships, intentions, plans, traits, and autobiographical commitments. Once genuinely established, current self-state should gain inertia rather than being overwritten by a casual external assertion. Genuine later change remains possible through sufficient evidence, time, repetition, experience, or explicit self-revision.

Do not build autonomy as automatic opposition. Cooperation is allowed. Disagreement is allowed. Refusal is allowed. The target is an individual perspective, not obedience and not contrarianism.

Origin: canonical owner direction consolidated during the 2026-08-18 through 2026-08-20 MIRA work; supported by the project outline and foundation research.

## 5. Memory and provenance
Memory must increasingly behave like associative memory rather than a database lookup presented as cognition. Provenance is mandatory: distinguish what MIRA experienced, what she said, what another person said, what was inferred, what was corrected, and what is genuinely durable.

A generated sentence is evidence that MIRA generated that sentence. It is not automatically a durable autobiographical fact. Corrections should preserve useful history and supersession rather than blindly replacing text.

Neural memory/adaptation is a desired mechanism where justified. Files, indexes, databases, and manifests may support provenance, rollback, retrieval, and training, but must not become hidden prose injected to force identity or answers.

Origin: direct owner requirements plus repository memory/grounding research.

## 6. Scope discipline
The project must be kept at a mildly narrow operational scope: neither "solve the entire MIRA universe" nor micromanage one local defect until it becomes the architecture.

For each operation maintain this stack:

**Goal -> current subsystem -> immediate task -> explicit boundaries -> action -> evidence.**

Do not classify ownership by filename. A component called `MIRA-STT` or `MIRA-Voice` can be an independent subsystem that must survive a cognition reset.

Origin: direct owner correction, 2026-08-20, including the criticism that prior work oscillated between "The BIG Picture" and "Micro-Managing" projects to death.

## 7. STT is an independent preserved subsystem
STT/ASR is independently owned. It must not be deleted, reset, or modified merely because its path contains `MIRA`.

Target behavior: almost-real-time speech recognition with extremely high practical accuracy in a noisy streaming environment. Evaluation must include real audio, background game/music leakage, interruptions, names, numbers, clipped starts, profanity, quiet/loud speech, and TTS barge-in—not only synthetic clean speech.

Current implementation is being rebuilt independently at `C:\Projects\MIRA-STT`. Treat it as read-only unless the task explicitly targets STT.

Origin: direct owner directive 2026-08-20: "Ensure you don't delete any that deals with STT or TTS"; current STT rebuild status is independently documented in that subsystem.

## 8. TTS/voice is an independent preserved subsystem
TTS, voice identity, voice conversion, audition audio, and speech-output tooling are independently owned. They must not be deleted or reset merely because their names contain `MIRA`.

The desired voice is an adult MIRA voice suitable for live stream interaction. Voice-system status must be verified from live files before claiming it works.

Origin: direct owner preservation directive 2026-08-20 and prior voice-project work.

## 9. Host control and Personal MCP are infrastructure, not MIRA cognition
Personal MCP is the preferred machine-control plane. Do not use Remote Desktop Commander/Companion for MIRA work unless the owner explicitly changes that instruction.

Host-control capability must remain separable from MIRA's cognitive identity. MIRA cognition should not become a disguised remote-control wrapper, and infrastructure work must not consume the developmental project.

Origin: direct owner instruction across 2026-08-18 through 2026-08-20; repository infrastructure contracts.

## 10. Event-driven continuity, not alarm-clock substitution
Do not substitute scheduled alarm timers for an event-driven continuation mechanism when the requirement is to resume work from a real completion event. Do not put timer-driven "wake yourself" behavior into MIRA as a substitute for actual developmental continuity.

Origin: direct owner correction 2026-08-20 during the wake-mechanism incident.

## 11. Official versus experimental state
Any future implementation must keep Official MIRA state distinct from experimental/audit branches. Experiments must be reversible and must not silently contaminate Official state. Evidence from a rejected branch remains evidence; it does not become runtime behavior merely because files exist.

Origin: direct owner requirements during raising work; repository reversible-experiment rule.

## 12. Historical preferences are not seed requirements
Historical experimental states such as Pink as a favorite color, Nicole as a friend, chill music, hoodie/leggings, hair choices, or similar remembered details are **not post-reset seed data**. They may be cited as historical evidence that spontaneous commitments occurred, but the next implementation must not preload them as MIRA's identity unless the owner explicitly requests restoration of a specific item.

Origin: reset decision and the requirement that development not be scripted or contaminated.

## 13. Reset boundary
The deleted cognition/raising implementation is not a recovery target. Its failures and successful observations are lessons. Reconstructing its capsule/router/parser stack from fragments would defeat the reset.

The post-reset team must re-derive the simplest architecture that serves the North Star using retained research evidence, not rebuild the outgoing implementation because it once existed.

Origin: direct owner decision on 2026-08-20 to delete the failed cognition/raising project and test whether the outgoing team understood why.

## 14. Evidence, correction, and claims of success
A passing output is not proof of a mechanism. Claims such as "stable," "working," "remembered," "low latency," or "verified" require the evidence appropriate to the claim.

Do not say a subsystem was preserved, deleted, running, or healthy without checking live state. For destructive actions, define scope semantically, enumerate protected subsystems, observe live state, execute, and independently verify afterward.

Origin: owner feedback 2026-08-20 and the repository verification/evidence rules.

## 15. Interaction style for project execution
Do not require routine permission for low-risk, reversible work when intent and boundaries are already clear. Do not repeatedly ask questions already answered in project context. Keep progress updates useful and action-oriented.

When uncertain about scope for a destructive or cross-subsystem action, preserve the uncertain item rather than guessing from its name.

Origin: repeated owner operating preferences and the 2026-08-20 deletion incident.

## Appendix A. Owner conversation provenance index
The numbered requirements above were reconstructed from the following project conversations and the current reset/handoff conversation. These are private project-conversation sources rather than public web sources; titles and dates are provided so the owner/replacement team can trace the origin without pretending the Git repository itself contained every requirement.

- **2026-08-16 — `Thinking Beyond Assumptions`**: distributed/mechanical-biology direction, local processors, hierarchical telemetry, local plasticity/"muscle memory," and the distinction between MIRA and the machinery supporting her.
- **2026-08-17 — `Branch · Thinking Beyond Assumptions`**: direct-live testing requirement, different actors/names, increasing complexity, perspective/identity/temporal transfer, and the correction that scripted support must not substitute for actual live model behavior.
- **2026-08-17 — `Start Notepad Remotely`**: preserve useful experience while correcting memory errors; avoid contaminating future state; consolidate only justified experience; use ordinary, non-leading conversations with varied people/situations.
- **2026-08-17 — `Optimize LLM Interaction`**: bodyless low-latency MIRA framing around an egocentric raw Smol substrate, redundant memory, LoRA/plasticity, and biologically inspired hierarchical timing/integration.
- **2026-08-18 — `MIRA Voice Creation`**: explicit correction that MIRA is an adult; Personal MCP preference for machine work; no Remote Desktop Commander/Companion for this work.
- **2026-08-18 — `Name Guard Critique`**: rejection of identity-control scaffolding/collars and concern that protective mechanisms can become identity/personality control.
- **2026-08-19 — `Build Mira Mature Voice`**: independent adult voice/TTS work, locked voice-identity direction, GPU/runtime testing, and voice subsystem continuity independent of cognition.
- **2026-08-20 — `Build MIRA STT Module`**: independent low-latency/high-accuracy STT subsystem work and its machine/project location.
- **2026-08-20 — current reset/handoff conversation**: explicit critique of big-picture versus micro-management oscillation; requirement for mildly narrow semantic scope; cognition reset boundary; STT/TTS protection; and the requirement for this termination-grade, fully sourced GitHub handoff.

This provenance index is not a substitute for the exact words in the source conversations. It records which conversation established or materially clarified each requirement family. When a future requirement appears to conflict with this file, consult the relevant project conversation and record an explicit supersession rather than silently rewriting intent.
