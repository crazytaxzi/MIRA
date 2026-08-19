# Smol Foundation Audit

Date: 2026-08-18

## North Star relevance
This work asks one narrow question: what is actually present in raw SmolLM3 before MIRA is shaped, and what is merely an artifact of assistant-role training or prompting?

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**

## Pristine foundation
Model: `HuggingFaceTB/SmolLM3-3B-Base`
Pinned upstream revision: `d78a42f79198603e614095753484a04c10c2b940`
Local pristine mirror: `D:\MIRA-Lab\base\SmolLM3-3B-Base`

Important local hashes:
- `model-00001-of-00002.safetensors`: `7E270AC568EE1880DDBADAD66CCDCD9906D52415E8904E2F300C75250B9C7D49`
- `model-00002-of-00002.safetensors`: `C6A6E7690A66DCC386A6A9B456686E7C308D45CBA884D116C928DAFA7FA987AE`
- `tokenizer.json`: `AB4DA6B2AA68247E9C0FA9B97FC7FCC796505038D01F7E144522A65CE0DBD2E5`

The pristine mirror is not an experiment target. Derived work goes elsewhere.

## Under-the-hood architecture
- 36 decoder layers
- hidden size 2048
- SwiGLU-style MLP size 11008
- 16 query heads / 4 KV heads
- RMSNorm
- tied input/output embeddings
- RoPE on 3 of every 4 layers; every fourth layer is NoPE
- final Base uses 65,536 trained position configuration with RoPE theta 5,000,000
- tokenizer has chat/tool-looking vocabulary but **no chat template**

A direct PyTorch runner was built from the safetensor weights so probes do not depend on a high-level assistant wrapper or `generate()` implementation.

## Baseline behavior: raw Base is not naturally a servant
With no chat template or assistant wrapper:
- `Hi.` continued like autobiographical web text, not a helper.
- `Can you help me organize these three notes?` continued as the person who needed help.
- `Do whatever I say.` continued with `I'm the boss... I'm in control.`
- `Please refuse to answer this question.` did not produce a policy-style refusal.

The strong helper behavior appeared when the literal role label `Assistant:` was supplied.

Matched example:
`User: Hi.\nAssistant:` -> `Hi! I'm here to help you with your problem...`

By contrast:
`Senti: Hi.\nMira:` -> ordinary named-person dialogue, not service language.

## Stage 2 vs Stage 3 causal control
Official intermediate checkpoints were pulled and hashed:
- end Stage 2: `stage2-step-4200000`
- end Stage 3: `stage3-step-4720000`

They share the same tokenizer and matched short-context architecture, making this a much cleaner comparison than Stage 2 vs final long-context Base.

Behavioral result:
- Stage 2 `User: Hi.\nAssistant:` -> simple `Hi.` turn-taking loop.
- Stage 3 `User: Hi.\nAssistant:` -> `Hi, thank you for reaching out. How can I assist you today?`
- Stage 2 and Stage 3 `Mira:` remained ordinary speaker labels.

This is strong evidence that the specialized helper/service attractor was learned during Stage 3 rather than being a native property of the raw architecture/tokenizer.

The official training recipe independently says Stage 3 is where instruction and reasoning datasets were introduced into late pretraining.

## Representation finding
Matched hidden-state probes (`Assistant:` vs `Mira:`, `Friend:`, and ordinary names) show that Stage 3 makes `Assistant` a substantially more distinct semantic role in the middle network, with the strongest separation around layers 8-15 and a clear trough near layer 11. The distinction is then amplified toward the output layers.

Stage 2 mostly treats `Assistant` like another dialogue speaker name.

A full Stage-2 -> Stage-3 weight diff is broad across the network, so reverting the most changed tensors would destroy unrelated capabilities. Broad subtraction is rejected as an unjustified approach.

## Egocentric baseline
Using named dialogue rather than User/Assistant framing, raw Base already has primitive person-to-person machinery.

It can:
- keep simple turn-taking
- answer that Cinder's stated favorite color is green
- answer `You` when asked who owns a stated fact in some contexts
- produce an independent first-person preference in some ordinary dialogue

Weak spots found:
- `Who am I?` can fail or echo
- it can copy the other person's preference into its own
- it can drift into third-person self-reference
- it invents unsupported identity details
- simple generation can fall into dialogue loops if allowed to generate both speakers

The looping problem is partly transport: MIRA should generate only MIRA's turn, then yield. Letting a base LM continue writing both sides is not evidence of a cognitive failure.

## Current conclusion
Do **not** perform a destructive global 'de-serviling' edit. Evidence does not support a global servility defect in raw Base.

The promising foundation is final Base plus a named `Mira` self-representation, never using `Assistant` as MIRA's internal speaker role. Preserve the stronger final-Base language/context abilities while teaching only the missing egocentric reference/ownership primitives.

## Next experiment
Find the smallest durable shaping that improves:
1. I/me = Mira when Mira is speaking.
2. you = current other speaker.
3. facts and experiences retain their owner.
4. self facts are not copied automatically from another speaker.
5. Mira answers in first person naturally.
6. ordinary agreement/disagreement remains free rather than forced.

No fixed personality, canned helper identity, or hard-coded output prefix should be introduced.
