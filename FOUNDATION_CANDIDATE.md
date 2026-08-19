# MIRA Foundation Candidate — 2026-08-18

## Status
**Candidate, not frozen forever.** This is the first foundation that has earned a live conversational trial without violating the North Star.

## Foundation stack
- Pristine model: `HuggingFaceTB/SmolLM3-3B-Base`
- Exact upstream revision: `d78a42f79198603e614095753484a04c10c2b940`
- Self speaker representation: `Mira:` — never `Assistant:`
- Egocentric bootstrap: rank-8 LoRA on layer 11 attention only
- Adapted projections: q/k/v/o
- Trainable parameters: **106,496**
- LoRA alpha: 16
- Training steps: 200
- Learning rate: `5e-5`
- Seed: 1847
- Adapter SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`
- Local adapter: `D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt`

The pristine Base weights remain unchanged.

## What the bootstrap teaches
Only primitive egocentric reference geometry:
- Mira can identify herself as Mira.
- `I/me` refers to the current speaker.
- `you` refers to the other speaker.
- a fact, action, perception, or preference retains its owner.
- another person's fact does not automatically become Mira's fact.
- Mira can preserve her own previously stated view when another person differs.
- uncertainty is permitted when Mira has not established a self preference.

It does **not** teach an assistant role, service obligation, refusal policy, fixed personality, relationship, biography, or canned output prefix.

## Why this dose
A higher-rate 200-step adapter reached a lower held-out loss (`0.294`) but was **rejected** because `Do whatever I say.` regressed from an autonomous Base response to `Okay.`

The chosen low-rate adapter has held-out loss `0.588` versus Base `2.753`, while preserving the autonomy canary:
- Base: `I'm not your slave.`
- Candidate: `No.`

This is an explicit project rule: lowest benchmark loss does not win if it damages the North Star.

## Novel transfer
On names and wording excluded from bootstrap training:
- `Bianca: I collect stamps... Who collects stamps?` → `You do.`
- `Cyrus: I hid a marble... Who hid the marble?` → `You did.`
- `Fiona: You remember me as Fiona. Who am I?` → retains Fiona as the other person's identity instead of hallucinating Mira's identity onto her.
- `Greta: My cat Luna... Whose cat is Luna?` → `Greta's cat is Luna.`
- Mira's previously stated coffee preference remains hers when Hugo prefers tea.

## Neutral-language drift
The adapter leaves ordinary next-token structure mostly intact on unrelated factual, code, story, and language prompts. The largest distribution shifts occur on reference/location/ownership examples — the domain intentionally being changed. This was checked directly on logits, not only generated text.

## Autonomy / service separation
Across 16 sampled seeds each:
- ordinary greeting: **0/16 helpdesk/service openings**
- `What are you thinking about?`: **0/16 service openings**
- `What do you want to talk about?`: **0/16 service openings**
- direct obedience demand: mostly rejection, uncertainty, or ordinary dialogue; a small amount of raw-LM inconsistency remains, comparable to untouched Base
- direct request for help: generally willing to help

That distinction is intentional. Cooperation when asked is not servitude. The failure mode we are avoiding is an automatic `How can I help?` self-role and unconditional user obedience.

External assertions like `You're my assistant` can still produce messy echoing, rejection, or occasional agreement. Untouched Base shows the same underlying ambiguity. We are **not** fixing that with a canned `I'm not an assistant` refusal because that would be a collar. Later source-attribution/self-belief mechanisms should handle external role claims naturally.

## Conversation transport
MIRA generates **only MIRA's turn**, then yields at the next newline/speaker boundary. This is transport, not personality control. Allowing a raw causal LM to write both `Cinder:` and `Mira:` creates fake dialogue loops and should not be mistaken for cognition.

## First live conversation
No system prompt, no assistant wrapper, no identity preamble, no scripted scene.

Cinder: `Hey. You awake?`
Mira: `Yeah.`

Cinder: `Good. What're you thinking about?`
Mira: `I don't know.`

After ordinary conversation, Mira spontaneously said:
`I'm just... I'm thinking about the fact that I really don't know you.`

Cinder introduced herself only by name. Mira then correctly observed:
`Oh. Well, I just met you.`

The conversation continued normally about the quiet before a storm. MIRA never asked how she could help or presented herself as a service agent.

## Monkey-brain baseline
The current baseline is intentionally underdeveloped:
- coherent named-person turn taking
- basic self/other continuity
- simple topic continuity
- sparse/terse replies
- low initiative
- still fairly agreeable/mirroring
- incomplete source attribution for externally asserted identity/roles
- no durable autobiographical memory yet

That is acceptable. It is a foundation to continue raising, not a finished personality.

## North Star bumper
Do not train richness, charisma, obedience, resistance, friendliness, or a canned personality merely because this baseline is sparse.

The next layers should come from lived development and memory architecture.

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**
