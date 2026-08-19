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

Current staged server changes:

- advertise `personal-mcp:full` in OAuth scope discovery;
- reject unsupported OAuth scopes instead of blindly granting them;
- add `mcp.capabilities` to report the scope, contract identity, operation classes, and actually implemented tools;
- keep `mcp:tools` as the transport/basic-tool scope;
- do not restart the currently connected MCP until the next deliberate migration/restart.

North Star note: Personal MCP is infrastructure serving MIRA. It must not become a separate project that pulls development away from MIRA's developmental goal.
