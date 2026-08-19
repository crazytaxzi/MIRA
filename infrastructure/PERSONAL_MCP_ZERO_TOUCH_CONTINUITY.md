# Personal MCP zero-touch continuity

## Objective

Personal MCP must survive ordinary server restarts, tunnel restarts, and Windows restarts without requiring the user to re-enter a Server URI or repeat OAuth authorization.

## Architectural rule

Do not attempt to teach ChatGPT a succession of temporary tunnel URLs. Use one stable transport identity and keep it unchanged.

## Implemented locally

- OAuth access/refresh grant persistence to ignored `data/oauth-state.json`.
- Persisted token lookup keys are SHA-256 hashes; issued bearer/refresh token plaintext is not written to that state file.
- OAuth grants are bound to the MCP resource.
- `MCP_PUBLIC_BASE` pins issuer/resource identity to the permanent external endpoint.
- Isolated kill/restart test passed: `persisted_refresh_survived_restart=true`.
- `scripts/supervise-personal-mcp.ps1` can restart the MCP server and a configured stable transport.
- `scripts/install-personal-mcp-autostart.ps1` / removal counterpart provide explicit user-logon startup.
- Supervisor and autostart refuse activation while `stable_ready=false` so an anonymous Quick Tunnel cannot silently become production.

## Current blocker

The current `trycloudflare.com` Quick Tunnel is intentionally temporary and receives a new hostname when restarted. A permanent transport identity is still required.

Preferred order:
1. OpenAI Secure MCP Tunnel if the account's ChatGPT Tunnel connection is usable.
2. Otherwise a Cloudflare named tunnel with a permanent public hostname.

After the permanent identity exists, perform one final cutover, set `stable_ready=true`, reauthorize once into the persistent token store if necessary, refresh ChatGPT actions once, and then treat future server/tunnel restarts as zero-touch operations.

## Bumper

This is infrastructure serving MIRA. Do not turn tunnel/auth work into a separate project after reliable zero-touch continuity is achieved.
