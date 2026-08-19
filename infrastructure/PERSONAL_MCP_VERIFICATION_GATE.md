# Personal MCP mandatory verification gate

Date: 2026-08-19
Status: canonical enforcement contract

## Purpose

Prevent Personal MCP from confidently acting on stale model knowledge, stale local state, duplicated work, ambiguous execution results, or technically valid actions that do not match the user's actual intent.

This is server-side execution policy. It is not merely a prompt, recommendation, or UI warning.

## Core rule

Every tool call is classified before dispatch.

The classifier considers:

- operation class A/B/C/D;
- read/write/destructive/idempotent/open-world behavior;
- target and scope;
- whether the action is externally visible;
- whether the action is security-sensitive;
- whether the action is `high_consequence`;
- whether facts required to justify the action are volatile;
- whether a standing authority rule covers it;
- whether the action can be independently verified afterward.

MCP annotations are emitted truthfully for client UX, but annotations never replace server-side enforcement.

## Verification levels

### Level 0 — observation

Typical Class A closed-world read.

Requirements:

- inspect current state;
- timestamp the observation;
- no verification ticket required.

### Level 1 — routine reversible change

Typical Class B write with bounded scope and reliable rollback/idempotency.

Requirements:

- reconstruct intent;
- observe live target state;
- deduplicate/pending-operation check;
- expected-result definition;
- postflight readback;
- standing authority if running unattended.

A lightweight automatically generated verification record is sufficient.

### Level 2 — consequential change

Class C, open-world write, security-sensitive write, externally visible change, or other materially consequential action.

Requires a sealed verification ticket matching the exact action arguments.

### Level 3 — high consequence

Class D or `high_consequence=true`, including financial movement, account/security authority changes, new payment/transfer destinations, credential changes, machine lifecycle actions with material risk, or similarly costly/irreversible effects.

Requires the full gate, fresh evidence for volatile assumptions, three distinct checks, short ticket expiry, exact argument binding, independent postflight verification, and an explicit recovery/ambiguity policy.

Standing authority may remove unnecessary per-action user interruption. It does not remove Level 3 verification.

## Mandatory preflight sequence

### 1. Reconstruct intent

Capture:

- requested outcome;
- exact target;
- constraints;
- standing permissions that apply;
- prohibited outcomes;
- expected user-visible result.

Reject an action that is merely technically convenient but materially different from the requested outcome.

### 2. Observe live state

Read the current local or remote state required to safely act.

Do not rely on remembered values when a current observation is available.

Record:

- observation timestamp;
- source/tool;
- normalized observation digest;
- relevant identifiers and pending states.

### 3. Identify volatile assumptions

A volatile assumption is any material fact that may have changed since model training, since a prior conversation, since the last recorded observation, or since the workflow was configured.

Examples include:

- policies and terms;
- fees and limits;
- supported product features;
- software/API behavior;
- laws/regulations;
- service schedules/status;
- account workflow requirements;
- payment/transfer rules;
- authentication/security requirements;
- current recipients/account destinations;
- current balances/pending transactions;
- current application UI state.

### 4. Require fresh evidence when volatility matters

For a Level 2/3 action whose safety or validity depends on volatile external information, the ticket must contain current evidence.

Evidence priority:

1. live authenticated service state;
2. current first-party/official documentation;
3. current authoritative external source when no suitable first-party source exists.

Each evidence item records:

- claim being supported;
- source URL or local source identifier;
- source kind;
- checked timestamp;
- publication/update timestamp when available;
- extracted fact or digest;
- freshness limit.

The model's own remembered knowledge is never accepted as freshness evidence.

If the required evidence cannot be obtained, the action is rejected or escalated rather than guessed.

### 5. Triple-check the proposed action

Three distinct checks are mandatory at Level 2/3.

#### Intent check

Does the exact proposed action accomplish the user's requested outcome within standing authority?

#### State check

Is the action valid against the live state observed immediately before execution?

#### Consequence check

Are target, destination, amount/scope, timing, side effects, dependencies, security impact, and reversibility acceptable?

The same reasoning repeated three times does not satisfy this requirement.

### 6. Deduplicate and detect races

Before any create/send/transfer/delete/schedule/publish/change action, check whether an equivalent operation is:

- completed;
- pending;
- already scheduled;
- being performed by another worker/process;
- expected to execute automatically.

Use a stable idempotency key when the destination/workflow supports one.

Loss of acknowledgement is never sufficient reason to replay a consequential write.

### 7. Define result and stop conditions

Before dispatch record:

- expected observable result;
- acceptable variance;
- failure signals;
- ambiguity signals;
- safe rollback/recovery path;
- conditions that require user involvement.

If the outcome cannot be meaningfully verified, Level 3 unattended execution is denied by default.

### 8. Bind the ticket to the exact action

A sealed ticket contains an immutable digest of:

- tool name;
- normalized arguments;
- target identifiers;
- standing-rule id when used;
- preflight-state digest;
- evidence digest;
- verification level;
- issue and expiry timestamps.

Changing a material argument invalidates the ticket.

Tickets are single-purpose. A ticket for one destination, amount, command, file, or account cannot authorize another.

## Ticket state machine

`DRAFT -> SEALED -> CONSUMED -> POSTFLIGHT_VERIFIED`

Exceptional terminal states:

- `REJECTED`
- `EXPIRED`
- `MISMATCHED`
- `FAILED`
- `AMBIGUOUS`

A consumed Level 2/3 ticket cannot be reused for a second consequential write unless the operation is explicitly modeled as a multi-step transaction and the ticket defines every permitted step.

## Suggested ticket schema

```json
{
  "ticket_id": "verify_...",
  "intent": "...",
  "tool": "...",
  "normalized_args_sha256": "...",
  "target": "...",
  "operation_class": "C",
  "verification_level": 2,
  "high_consequence": false,
  "standing_rule_id": null,
  "live_state": {
    "observed_at": "...",
    "sha256": "..."
  },
  "volatile_assumptions": [],
  "evidence": [],
  "checks": {
    "intent": {"ok": true, "reason": "..."},
    "state": {"ok": true, "reason": "..."},
    "consequence": {"ok": true, "reason": "..."}
  },
  "duplicate_check": {
    "ok": true,
    "idempotency_key": "...",
    "pending_equivalent": false
  },
  "expected_result": "...",
  "rollback": "...",
  "stop_conditions": [],
  "issued_at": "...",
  "expires_at": "...",
  "status": "SEALED"
}
```

## Freshness policy

Freshness is claim-specific, not one universal timeout.

Examples:

- current DOM/UI state: seconds/minutes;
- balance or pending transaction state before a financial action: immediately before action;
- current service status: minutes;
- current product limits/policies/security workflows: rechecked when material to a consequential action unless an explicitly cached first-party record remains within its configured TTL;
- static local file hash: valid until the file changes;
- durable user standing rule: valid until its expiry/supersession/revocation.

The gate must prefer an inexpensive cached source only when the cache is still inside the configured freshness window and the underlying claim is not known to have changed.

## Postflight verification

Tool-returned `ok=true` means the call returned successfully. It does not prove the real-world outcome occurred.

After Level 1/2/3 writes, perform an independent observation whenever possible.

Examples:

- reread the modified file and hash it;
- refresh/requery the resulting service state;
- verify a new schedule appears;
- verify a transaction/payment identifier and current status;
- verify a process/service state through an independent query;
- reopen the relevant UI/page and inspect the resulting state.

Return one of:

- `VERIFIED` — independent evidence matches the expected result;
- `PARTIALLY_VERIFIED` — some expected effects are confirmed but final completion remains pending;
- `FAILED` — evidence shows the requested result did not occur;
- `AMBIGUOUS` — completion cannot currently be determined.

## Ambiguous write rule

An ambiguous consequential write is never blindly retried.

Recovery order:

1. query current state;
2. search for returned transaction/action/request identifiers;
3. search for an equivalent pending/completed action;
4. retry only when non-execution is established or an end-to-end idempotency mechanism guarantees no duplicate effect;
5. otherwise stop with `AMBIGUOUS` and escalate.

## Recovery

Safe technical recovery may be automatic:

- reconnect local IPC;
- restart a failed worker;
- reopen a browser/profile;
- restore a known authenticated session;
- refresh stale page/UI state;
- repeat idempotent reads;
- retry a write only under the ambiguity rule above.

Recovery attempts are bounded and audited.

## Human interruption policy

Do not ask the user merely because a routine operation exists.

Escalate when:

- no standing authority covers an unattended write;
- target/recipient/destination is new;
- a material value exceeds the standing boundary;
- current evidence conflicts with the standing rule;
- live state makes the outcome unsafe or ambiguous;
- MFA/CAPTCHA/security-key requires a human;
- credentials/security authority would change outside standing authority;
- the result remains ambiguous after bounded verification/recovery;
- execution would violate a legal, contractual, platform, or safety restriction.

Routine covered operations proceed without unnecessary user interaction after required verification succeeds.

## Escape-hatch enforcement

Generic tools are powerful enough to bypass naive wrapper-only safety.

Therefore the policy classifier and verification middleware must execute below the public tool wrapper layer and cover at minimum:

- raw shell;
- host execution;
- PowerShell/cmd execution;
- process starts that embed commands;
- file writes/deletes/moves;
- browser script/evaluate operations;
- native raw input;
- scheduler/task creation;
- child tools invoked by an automation queue.

A command containing an action that would require Level 2/3 verification when expressed through a dedicated tool must not become Level 0/1 merely because it is embedded in `host.exec`.

## Audit record

For Level 1/2/3 operations append a redacted event containing:

- action/ticket ids;
- timestamp;
- intent and argument digests;
- operation class/level;
- standing-rule reference;
- preflight observations;
- freshness evidence references;
- three-check results;
- execution result identifiers;
- postflight classification;
- recovery attempts;
- final state.

Never record plaintext passwords, auth tokens, cookies, recovery codes, secret answers, private keys, or other secret material.

## Current-source verification requirement

The implementation itself must periodically revalidate the external facts it depends on. As of 2026-08-19:

- OpenAI documents that MCP app action changes are not automatically enabled after approval and must be refreshed/reviewed: https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt
- The current MCP schema explicitly states tool annotations are hints and not a trusted enforcement mechanism: https://modelcontextprotocol.io/specification/2025-11-25/schema

If those platform behaviors materially change, update this contract and implementation rather than continuing from stale assumptions.

## Required tests

The gate is not complete until tests prove:

1. Class A read succeeds without a ticket.
2. Routine reversible Class B write performs pre/post observation.
3. Class C write rejects a missing ticket.
4. Level 3 write rejects stale required evidence.
5. A sealed ticket rejects changed arguments.
6. An expired ticket rejects execution.
7. Triple-check requires three separately populated checks.
8. A duplicate/pending equivalent blocks replay.
9. A raw shell equivalent of a protected action cannot bypass the gate.
10. An ambiguous write is not automatically replayed.
11. Postflight can return all four verification classifications.
12. Audit output is redacted and contains no seeded test secrets.
