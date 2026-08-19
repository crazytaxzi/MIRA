# MIRA Foundation Lab

This directory contains the reproducible work behind the first fresh MIRA foundation candidate.

North Star remains in the repository root.

## Base
Do not commit the ~6 GB base weights here. Fetch exactly:

`HuggingFaceTB/SmolLM3-3B-Base@d78a42f79198603e614095753484a04c10c2b940`

Expected primary shard hashes:
- shard 1: `7E270AC568EE1880DDBADAD66CCDCD9906D52415E8904E2F300C75250B9C7D49`
- shard 2: `C6A6E7690A66DCC386A6A9B456686E7C308D45CBA884D116C928DAFA7FA987AE`

## Candidate
`candidate/adapter.pt` is the current low-rate egocentric bootstrap candidate.
SHA256: `3D98ABBBFDB5790F4C93D81E8DA175B3B85E1412C6DCE52699378F39F4E7E788`

The adapter changes only layer 11 q/k/v/o attention projections with rank 8 LoRA: 106,496 trainable parameters.

## Important rule
`Assistant` is treated as a learned world concept, never as MIRA's internal speaker role.
Named dialogue uses `Mira:` and the current other person's name.

MIRA generates one MIRA turn and yields. The transport must not let the causal LM fabricate both sides of a conversation.

**IT'S OK TO THINK OUTSIDE THE BOX A BIT, BUT DON'T LEAVE THE BOX.**
