# MIRA MCP Bridge

This is supporting infrastructure for MIRA. It does not redefine the North Star.

## Live state — 2026-08-19

- ChatGPT successfully connected to the OAuth-capable MCP bridge.
- Current temporary endpoint: `https://controlled-bare-erp-williams.trycloudflare.com/mcp`
- OAuth flow completed through authorization code + PKCE and `/token` exchange.
- Current tools are `ping` and `echo`.
- Source has explicit `outputSchema` plus truthful MCP annotations for both tools; those metadata changes require a deliberate server restart and ChatGPT action refresh before becoming live.

## Reliability gaps

1. Current hand-built OAuth access/refresh state lives only in process memory. Restarting Node forces manual reconnection.
2. Current shim receives the OAuth `resource` parameter but does not yet provide strong persisted audience/resource binding.
3. Post-auth MCP negotiation is not currently logged, so protocol-version/method-level diagnostics are weak.
4. Cloudflare Quick Tunnel has no uptime guarantee and its hostname changes on restart.
5. `offline_access` should be authorization-server capability, not advertised as a protected-resource requirement.

## Preferred v2 direction

Do not keep expanding the temporary OAuth shim unless required to preserve the working baseline. The already-installed Better Auth 1.7 MCP stack is the preferred reliability path: SQLite-backed OAuth state, PKCE, refresh-token handling, resource/audience-bound JWTs, JWKS verification, RFC 9728 discovery, scope challenges, and MCP 2026-07-28 CIMD support.

Stage v2 beside the live bridge, test it independently, then migrate once. Avoid repeated connection-breaking restarts.

**It's OK to think outside the box a bit, but don't leave the box.**