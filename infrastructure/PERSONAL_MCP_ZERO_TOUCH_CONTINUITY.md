# Personal MCP zero-touch continuity

## Objective

Personal MCP must survive ordinary server restarts, transport restarts, and Windows restarts without requiring the user to keep a terminal open, re-enter a Server URI, or repeat OAuth authorization during normal recovery.

Browser/desktop operator capabilities must also recover automatically once the user has an interactive Windows session.

## Architectural rule

Do not attempt to teach ChatGPT a succession of temporary tunnel URLs. Use one stable transport identity and keep it unchanged.

Do not require one process to do both background service work and interactive desktop work. Keep a durable core MCP plane plus a per-user interactive operator worker.

## Last recorded live state — 2026-08-19

The following values are historical observations from the 2026-08-19 live migration and must not be treated as current merely because they are written here:

- public MCP URL observed as `https://controlled-bare-erp-williams.trycloudflare.com/mcp`;
- Cloudflare Quick Tunnel PID observed as `6392` during the preserved cutover;
- Node MCP PID observed as `7060` on `127.0.0.1:8788` after replacing old PID `7988`;
- public `/health` was reachable after that cutover;
- OAuth discovery advertised `mcp:tools`, `personal-mcp:full`, and `offline_access`;
- the live MCP smoke test advertised `ping`, `echo`, and `mcp.capabilities`;
- `ping` and `echo` included output schemas and truthful read-only/non-destructive/idempotent/closed-world annotations.

Any future operational decision must query current process, health, transport, OAuth, and tool state rather than assuming these recorded PID/URL values remain valid.

## Restart continuity already implemented

- OAuth access/refresh grant persistence to ignored `data/oauth-state.json`.
- Persisted token lookup keys are SHA-256 hashes; issued bearer/refresh token plaintext is not written to that state file.
- OAuth grants are bound to the MCP resource.
- `MCP_PUBLIC_BASE` pins issuer/resource identity to the external endpoint.
- Isolated kill/restart test passed at implementation time: `persisted_refresh_survived_restart=true`.
- `scripts/supervise-personal-mcp.ps1` can restart the MCP server and a configured stable transport.
- `scripts/install-personal-mcp-autostart.ps1` / removal counterpart provide explicit user-logon startup.

## Persistent operator startup expansion

Zero-touch continuity now includes the operator architecture in `PERSONAL_MCP_OPERATOR_EXPANSION.md`.

### Core supervisor

The core supervisor must run without a visible terminal and must:

- start the MCP core;
- functional-probe the MCP endpoint rather than checking only for a PID;
- restart the core with bounded backoff;
- supervise the stable transport once a permanent transport identity exists;
- preserve persisted OAuth state;
- expose component `alive` and `ready` separately;
- reconnect to the interactive worker when it appears.

### Interactive worker

Browser and desktop UI control must run inside the logged-on user's interactive session.

Install a Task Scheduler entry using `TASK_LOGON_INTERACTIVE_TOKEN` / `InteractiveToken` semantics so the worker launches automatically when that user logs on. The task should:

- start hidden;
- restart on failure with bounded backoff;
- use the user's profile so current-user DPAPI secrets are available;
- expose only local authenticated IPC to the core;
- avoid a public listener;
- not require an open PowerShell/cmd/terminal window;
- surface a visible browser/UI only when a workflow requires human handoff.

Microsoft documents that `TASK_LOGON_INTERACTIVE_TOKEN` runs only in an existing interactive user session: https://learn.microsoft.com/en-us/windows/win32/taskschd/principal-logontype

### Browser worker

Use a dedicated persistent Playwright profile for normal operator browsing. Login state may persist across worker restarts. Maintain one-writer ownership of a persistent browser profile to avoid profile conflicts.

Playwright's current MCP documentation describes persistent profiles, Firefox support, accessibility snapshots, and standalone operation: https://playwright.dev/docs/getting-started-mcp

### Worker reconnection

Core and worker must use authenticated local IPC with heartbeats.

Recovery rules:

1. loss of heartbeat marks the worker `alive=false`, `ready=false`;
2. core does not assume in-flight writes failed merely because IPC disappeared;
3. after reconnection, reconcile any in-flight action through the verification/audit state before retrying;
4. read-only/idempotent work may be retried under normal bounded recovery;
5. ambiguous consequential writes follow `PERSONAL_MCP_VERIFICATION_GATE.md` and are not automatically replayed.

## Readiness contract

Every supervised component returns at least:

```json
{
  "alive": true,
  "ready": true,
  "observed_at": "2026-08-19T...",
  "dependencies": {},
  "last_error": null
}
```

`ready=true` requires a functional probe appropriate to the component.

Examples:

- MCP core: protocol/capability probe succeeds;
- transport: stable public origin reaches the intended MCP resource;
- interactive worker: local authenticated IPC responds;
- browser worker: browser process/context exists and a harmless snapshot probe succeeds;
- UI Automation worker: desktop automation root can be queried in the interactive session.

## One-time OAuth/app refresh caveat

Existing OAuth persistence removes ordinary restart reauthorization after a persisted grant has been issued.

However, ChatGPT's approved custom MCP action set is not automatically updated when server tools or inputs change. After adding the operator tool families, the app's actions must be refreshed/reviewed in ChatGPT before those new actions become callable. OpenAI currently documents this frozen action-snapshot behavior here: https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt

This is a deployment/update step, not a recurring runtime dependency.

## Remaining stable-transport blocker

The recorded `trycloudflare.com` Quick Tunnel architecture is intentionally temporary and receives a new hostname when restarted. Do not auto-restart it and silently create a different hostname.

Preferred permanent transport order:

1. OpenAI Secure MCP Tunnel if available for this connection/account.
2. Otherwise a Cloudflare named tunnel with a permanent public hostname.

OpenAI currently documents Secure MCP Tunnel as the supported path for a private/local MCP server rather than exposing it directly to the public internet: https://help.openai.com/en/articles/12584461-developer-mode-and-full-mcp-connectors-in-chatgpt

After a permanent transport identity exists, set `stable_ready=true`, enable the supervisor/autostart path, refresh ChatGPT actions after tool-schema changes, and treat future core/worker/transport restarts as zero-touch operations.

## Completion tests

Zero-touch continuity is not complete until tests prove:

- Windows reboot -> core returns ready without a user-open terminal;
- user logon -> interactive worker returns ready automatically;
- worker kill -> worker restarts and reconnects without terminal intervention;
- core kill -> core restarts and reconnects to the existing worker;
- browser kill -> browser component recovers or reports a precise handoff requirement;
- transport restart retains the same permanent public identity;
- OAuth refresh survives ordinary component restarts;
- in-flight ambiguous consequential write is reconciled rather than replayed;
- current component status contains fresh observation timestamps, not stale remembered state.

## Bumper

This is infrastructure serving MIRA. Do not turn tunnel/auth/operator plumbing into a separate project after reliable zero-touch continuity is achieved.
