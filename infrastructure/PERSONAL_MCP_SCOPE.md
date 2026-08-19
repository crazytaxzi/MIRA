# Personal MCP Full Scope

Canonical OAuth scope: `personal-mcp:full`

This scope represents the broad local-host capability boundary defined by the user-supplied `PERSONAL_MCP_REQUIRED_CAPABILITIES.md` contract. It is a permission boundary, not a claim that every capability is already implemented.

Contract SHA-256: `acf90ff200caed76fed2c559abb7ebda4a2f5d1d8c8d8a4c9a221f7ae56af26a`

The contract requires structured results, absolute resolved paths, first-class binary support, long-running process sessions, explicit elevation, explicit destructive operations, separated stdout/stderr, auditable state changes, and a broad host execution escape hatch.

Operation classes remain explicit:

- Class A — read-only
- Class B — reversible write
- Class C — destructive or privileged
- Class D — machine lifecycle / high-impact

The initial minimum viable contract contains 40 primitives centered on bridge discovery, filesystem access, process/session control, artifact transfer, generic execution, system/GPU telemetry, networking, audio/media, and privilege inspection.

Implementation rule: tools are exposed only when actually implemented and must declare input schema, output schema, privilege requirements, and truthful MCP annotations. Destructive or privileged actions remain explicit even when `personal-mcp:full` is granted.

## Persistent operator expansion

The canonical scope now also includes the reusable persistent-operator architecture defined in:

- `PERSONAL_MCP_OPERATOR_EXPANSION.md`
- `PERSONAL_MCP_VERIFICATION_GATE.md`
- `PERSONAL_MCP_OPERATOR_TOOLSET.json`

This expansion broadens Personal MCP beyond filesystem/process/network execution to include persistent runtime supervision, semantic browser automation, native Windows UI Automation, local secret references, schedules/queues, standing policy, verification/evidence, recovery, and exception notification.

The expansion is deliberately application-agnostic. It must not be implemented as a bank-specific, browser-only, or site-specific automation layer.

## Verification boundary

`personal-mcp:full` grants the MCP permission boundary; it does not disable deterministic verification.

All execution paths, including generic shell/host escape hatches, must pass through the server-side classifier and verification middleware. MCP annotations are truthful client-facing hints, not the enforcement boundary.

Add a `high_consequence` overlay independent of Class A-D for financial movement, account/security authority changes, new recipients/destinations, credential changes, irreversible external publication, and similarly costly effects.

Routine operations may use standing authority and proceed without unnecessary human interruption, but high-consequence actions still require current-state verification and exact-action binding.

## Execution-plane rule

Personal MCP is split into:

1. the core MCP plane, which owns remote-facing OAuth/tools/policy/verification/audit; and
2. a per-user interactive operator worker for browser and desktop UI capabilities.

The interactive worker must start automatically in the logged-on user's Windows session. A visible terminal is not a normal operating dependency.

Current staged server changes:

- advertise `personal-mcp:full` in OAuth scope discovery;
- reject unsupported OAuth scopes instead of blindly granting them;
- add `mcp.capabilities` to report the scope, contract identity, operation classes, and actually implemented tools;
- keep `mcp:tools` as the transport/basic-tool scope;
- preserve OAuth grants and stable transport identity across ordinary restart;
- implement the persistent-operator expansion only as underlying capabilities become real and tested;
- refresh ChatGPT action definitions after new tools/inputs are added because approved MCP action snapshots are not assumed to auto-update.

North Star note: Personal MCP is infrastructure serving MIRA. It must not become a separate project that pulls development away from MIRA's developmental goal.
