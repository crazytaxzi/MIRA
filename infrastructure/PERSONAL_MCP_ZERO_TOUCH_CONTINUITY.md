# Personal MCP zero-touch continuity

## Objective

Personal MCP must survive ordinary server restarts, tunnel restarts, and Windows restarts without requiring the user to re-enter a Server URI or repeat OAuth authorization.

## Architectural rule

Do not attempt to teach ChatGPT a succession of temporary tunnel URLs. Use one stable transport identity and keep it unchanged.

## Live state — 2026-08-19

- Current public MCP URL remains `https://controlled-bare-erp-williams.trycloudflare.com/mcp`.
- Cloudflare Quick Tunnel PID `6392` was preserved during the server cutover.
- Old Node MCP PID `7988` was replaced behind the same tunnel by Node PID `7060` on `127.0.0.1:8788`.
- Public `/health` stayed reachable after cutover.
- OAuth discovery now advertises `mcp:tools`, `personal-mcp:full`, and `offline_access`.
- Live MCP smoke test passes and advertises `ping`, `echo`, and `mcp.capabilities`.
- `ping` and `echo` now include output schemas and truthful read-only/non-destructive/idempotent/closed-world annotations.

## Restart continuity now implemented

- OAuth access/refresh grant persistence to ignored `data/oauth-state.json`.
- Persisted token lookup keys are SHA-256 hashes; issued bearer/refresh token plaintext is not written to that state file.
- OAuth grants are bound to the MCP resource.
- `MCP_PUBLIC_BASE` pins issuer/resource identity to the external endpoint.
- Isolated kill/restart test passed: `persisted_refresh_survived_restart=true`.
- `scripts/supervise-personal-mcp.ps1` can restart the MCP server and a configured stable transport.
- `scripts/install-personal-mcp-autostart.ps1` / removal counterpart provide explicit user-logon startup.

## One-time cutover caveat

The original live OAuth grants were created before persistence existed and were held only in PID `7988` RAM. A local-inspector migration was prepared, but execution was blocked by the remote safety layer. Therefore the existing ChatGPT connection may require one final reauthorization after this hot-swap. Any grant issued by the new server will then persist across ordinary server restarts.

## Remaining blocker

The current `trycloudflare.com` Quick Tunnel is intentionally temporary and receives a new hostname when restarted. Do not auto-restart it and silently create a different hostname.

Preferred permanent transport order:
1. OpenAI Secure MCP Tunnel if the account's ChatGPT Tunnel connection is usable.
2. Otherwise a Cloudflare named tunnel with a permanent public hostname.

After the permanent identity exists, set `stable_ready=true`, enable the supervisor/autostart path, refresh ChatGPT actions once, and treat future server/tunnel restarts as zero-touch operations.

## Bumper

This is infrastructure serving MIRA. Do not turn tunnel/auth work into a separate project after reliable zero-touch continuity is achieved.
