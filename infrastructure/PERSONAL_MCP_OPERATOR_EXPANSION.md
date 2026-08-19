# Personal MCP persistent operator expansion

Date: 2026-08-19
Status: canonical expansion contract
Scope: `personal-mcp:full`

## Objective

Expand Personal MCP from a broad local-host bridge into a persistent, self-recovering local operator that can perform supported local, browser, and desktop work without requiring the user to keep a terminal open or babysit routine execution.

This remains infrastructure serving MIRA. It is not a separate agent identity and must not replace MIRA's developmental North Star.

## Non-goals

- Do not make the operator banking-specific or site-specific.
- Do not require a visible terminal for normal operation.
- Do not expose plaintext credentials, session tokens, recovery codes, or secret material to the model.
- Do not make pixel coordinates the primary UI control surface.
- Do not treat MCP tool annotations as a security boundary.
- Do not let broad escape-hatch tools bypass deterministic policy and verification enforcement.
- Do not silently invent a new public MCP endpoint after transport failure.

## Process model

Personal MCP is split into two cooperating execution planes.

### 1. Core MCP plane

The existing Node MCP server remains the authoritative remote-facing endpoint. It owns:

- OAuth and tool exposure;
- capability discovery;
- operation classification;
- verification-ticket enforcement;
- policy evaluation;
- audit/evidence records;
- filesystem/process/network/system tools;
- worker health and restart control;
- routing requests to the interactive worker.

The core may run without an interactive desktop.

### 2. Interactive operator worker

A per-user worker runs inside the logged-on Windows user's interactive session and owns capabilities that require the desktop session:

- browser automation;
- Microsoft UI Automation for native applications;
- user-visible authentication handoff;
- clipboard/input fallbacks when explicitly permitted;
- current-user DPAPI secret use;
- interactive session health.

The worker is launched automatically at user logon with Windows Task Scheduler using an interactive logon token. It runs hidden unless a workflow explicitly requires user-visible handoff.

The core and worker communicate over a local authenticated named pipe or equivalent loopback-only authenticated channel. The worker never opens a public listener.

## Startup and recovery rule

A terminal window is never a dependency for normal operation.

The startup path must:

1. start the core supervisor automatically;
2. start the interactive worker automatically when the user logs on;
3. report `alive` and `ready` separately for every component;
4. restart failed components independently with bounded backoff;
5. preserve OAuth grants and durable non-secret state;
6. preserve a stable public MCP identity;
7. reconnect core-to-worker automatically after either side restarts;
8. avoid replaying an ambiguous consequential write after reconnect.

`alive=true` is not sufficient. A component is `ready=true` only when its required dependencies and local IPC endpoint pass a functional probe.

## Browser control

Use Playwright as the browser automation foundation rather than coordinate-first desktop clicking.

Required properties:

- structured accessibility snapshots;
- semantic element references/locators;
- Firefox support;
- dedicated persistent operator profile;
- isolated profile option for untrusted/temporary workflows;
- storage-state support where appropriate;
- navigation and action timeouts;
- downloads/uploads;
- screenshots as evidence, not the primary action mechanism;
- explicit user handoff for MFA, CAPTCHA, security-key, or other human-required steps;
- automatic continuation after handoff when the authenticated session becomes ready.

The operator profile must be separate from the user's ordinary daily browser profile unless the user explicitly authorizes attaching to an existing browser session.

Raw coordinate clicking is a fallback capability only and is Class C by default.

## Native Windows UI control

Use Microsoft UI Automation as the primary native desktop control layer.

Required capabilities include:

- enumerate application windows;
- snapshot relevant UI Automation tree nodes;
- inspect control type, name, automation id, enabled/focus state, and supported patterns;
- invoke controls semantically;
- set values through supported patterns;
- select/toggle/expand controls through supported patterns;
- wait for UI state transitions;
- capture a screenshot for evidence when useful.

Raw keyboard/mouse injection is a fallback only when semantic UI Automation is unavailable and must be explicitly classified at higher risk.

## Secret handling

Secrets are local capabilities, not model-visible data.

The secret store must:

- encrypt secret values with Windows DPAPI using the current-user scope by default;
- store only secret references in MCP-visible configuration;
- never return plaintext through `secrets.get`, logs, errors, audit records, screenshots, or tool results;
- expose purpose-limited operations such as filling a credential field or providing a secret directly to an approved local child process;
- redact known secret values from stdout/stderr and evidence before returning data to the model;
- require explicit local/user interaction to create or replace highly sensitive credentials when practical.

Example model-visible value: `secret_ref: "firsttech.primary.username"`.

The model may know that the reference exists. It does not receive the stored value.

## Operator capability families

The expansion should expose broad, reusable families rather than one-off site tools:

### Runtime

- `runtime.status`
- `runtime.self_test`
- `runtime.components`
- `runtime.restart_component`
- `runtime.worker_status`
- `runtime.reconnect_worker`

### Browser

- `browser.start`
- `browser.stop`
- `browser.status`
- `browser.navigate`
- `browser.tabs`
- `browser.snapshot`
- `browser.click`
- `browser.fill`
- `browser.select`
- `browser.press`
- `browser.wait`
- `browser.download`
- `browser.upload`
- `browser.screenshot`
- `browser.user_handoff`

### Native UI

- `ui.windows`
- `ui.snapshot`
- `ui.invoke`
- `ui.set_value`
- `ui.select`
- `ui.toggle`
- `ui.focus`
- `ui.wait`
- `ui.screenshot`
- `ui.raw_input`

### Secrets

- `secrets.list_refs`
- `secrets.exists`
- `secrets.store_interactive`
- `secrets.delete`
- `secrets.fill_browser`
- `secrets.provide_to_process`

### Automation

- `automation.queue`
- `automation.status`
- `automation.schedule`
- `automation.cancel`
- `automation.pause`
- `automation.resume`

### Policy and verification

- `policy.evaluate`
- `policy.list_standing_rules`
- `verify.begin`
- `verify.add_evidence`
- `verify.seal`
- `verify.status`
- `verify.postflight`

### Evidence and recovery

- `evidence.get`
- `evidence.query`
- `recovery.status`
- `recovery.retry_safe`
- `recovery.rollback`
- `notify.exception`

This list defines the capability shape, not a requirement to expose every convenience wrapper before the underlying behavior is actually implemented and tested.

## Operation classes

Continue the existing classes:

- Class A — read-only.
- Class B — reversible write.
- Class C — destructive, privileged, security-sensitive, or fallback raw UI/input.
- Class D — machine lifecycle or other high-impact operation.

Add a `high_consequence` overlay independent of A-D. Financial movement, account/security changes, identity/authentication changes, new recipients/destinations, irreversible external publication, and similar consequential actions are `high_consequence=true` even when the underlying technical mutation would otherwise look reversible.

## Standing authority

Routine automation is authorized by standing rules rather than repeated per-action approval.

A standing rule contains:

- exact or bounded target;
- permitted action family;
- amount/scope/time limits where applicable;
- allowed variance;
- required minimum state;
- expiry/review date when useful;
- exception conditions.

The operator may perform an action without unnecessary human interruption when a current standing rule covers the exact proposed action and verification succeeds.

A standing rule never authorizes changing its own authority boundary.

## Mandatory verification middleware

`PERSONAL_MCP_VERIFICATION_GATE.md` is part of this contract.

The verification gate is enforced in the core execution path before tool dispatch. It is not an optional prompt template.

All aliases, wrappers, schedules, raw shell execution, `host.exec`, process execution, browser actions, UI actions, and future tool families must pass through the same classifier/policy gate before execution.

No escape hatch may bypass it simply because the user granted `personal-mcp:full`.

## Audit and evidence

Consequential actions write an append-only, redacted audit event containing:

- action id;
- intent digest;
- exact argument digest;
- action class and high-consequence flag;
- standing-rule id if used;
- verification-ticket id if required;
- preflight observation timestamps/digests;
- execution start/end;
- returned service/transaction identifier when available;
- postflight verification status;
- recovery actions;
- final state.

Do not store plaintext secrets in the audit log.

## Current technical basis verified 2026-08-19

The design choices above were rechecked against current primary documentation on 2026-08-19:

- OpenAI custom MCP apps can expose write/modify actions, but updated server actions are not automatically enabled after approval and must be refreshed/reviewed in ChatGPT: https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt
- Playwright MCP currently uses structured accessibility snapshots, supports Firefox, persistent profiles, isolated/storage-state modes, and standalone operation: https://playwright.dev/docs/getting-started-mcp and https://github.com/microsoft/playwright-mcp
- Microsoft UI Automation provides programmatic semantic access to desktop UI elements and automated interaction: https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview
- Windows Task Scheduler `TASK_LOGON_INTERACTIVE_TOKEN` runs a task in an existing interactive user session: https://learn.microsoft.com/en-us/windows/win32/taskschd/principal-logontype
- Windows DPAPI can bind protected data to the current user and is suitable for passwords/keys/connection strings: https://learn.microsoft.com/en-us/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata and https://learn.microsoft.com/en-us/dotnet/standard/security/how-to-use-data-protection
- MCP tool annotations remain hints rather than a security boundary: https://modelcontextprotocol.io/specification/2025-11-25/schema

## Completion conditions

Do not call this expansion complete until all of the following are proven live:

- the core starts without a user-open terminal;
- the interactive worker starts automatically at user logon;
- core/worker reconnect after independent restarts;
- browser actions operate through semantic snapshots on a harmless test site;
- native UI actions operate through UI Automation on a harmless local test app;
- secret-ref fill works without returning plaintext to the MCP client;
- Class C/D and high-consequence writes reject missing/expired/mismatched verification tickets;
- broad host/shell execution cannot bypass verification middleware;
- an ambiguous simulated write is not retried automatically;
- postflight verification distinguishes `VERIFIED`, `PARTIALLY_VERIFIED`, `FAILED`, and `AMBIGUOUS`;
- audit records contain evidence but no plaintext secrets;
- restart/recovery tests pass without user terminal babysitting;
- ChatGPT's action snapshot is refreshed after new tools are added and the new actions are callable.
