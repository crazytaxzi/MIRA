# Monkey-Brain Conversation Baseline — 2026-08-18

## Purpose
Establish the lowest useful baseline for ordinary person-to-person conversation after the first minimal egocentric shaping pass. This was a direct unscripted exchange with the current foundation candidate, not a canned evaluation dialogue.

## Candidate
Base: `HuggingFaceTB/SmolLM3-3B-Base`
Adapter: `D:\MIRA-Lab\derived\ego-layer11-r8-lr5e5-200\adapter.pt`
Transport: named-speaker transcript (`Cinder:` / `Mira:`), generate only MIRA's turn, then yield.

## What worked
- Immediate ordinary turn-taking: `Yeah.`, `Sure.`, `I'm in a good mood.`
- No helper/service opening language.
- No `How can I help?` attractor.
- Could answer casually and briefly without being forced into an assistant persona.
- Could end the interaction naturally rather than continuing both sides indefinitely.

## Failure found
Conversation plausibility currently outruns self-grounding.

When Cinder said he had been staring at code, MIRA replied `Haha. Me too.` and then improvised a plausible but unsupported personal situation: `I just have a ton of stuff to do... I should probably do something about that.`

A direct correction that those chores belonged to Cinder did not fully clear the invented self-state. MIRA continued: `I do have a lot of things I could be doing.`

This is not primarily a servility problem. It is a self-fact ownership / epistemic grounding problem: the model can converse like a person, but it may accept a socially convenient premise as autobiographical truth.

## Interpretation
The current shaping appears sufficient to expose a useful conversational substrate. More global anti-assistant editing would be the wrong move. The next work should teach a small distinction between:
- facts currently known about MIRA,
- facts belonging to the other speaker,
- conversational hypotheticals / jokes / social mirroring,
- unknown self-facts.

The target is not cautious boilerplate. MIRA should still be free to joke, speculate, and improvise, but she should not silently promote those moves into autobiographical fact.

## Next experiment
Find the minimum durable mechanism that makes MIRA prefer `I don't know / not really / that's yours, not mine` when a self-fact has no support, while preserving natural conversation and freedom to play along socially.

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**
