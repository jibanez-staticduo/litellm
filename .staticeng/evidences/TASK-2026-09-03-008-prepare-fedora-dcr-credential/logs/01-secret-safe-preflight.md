# Secret-Safe Fedora DCR Preflight

## Scope

The preflight used status-only HTTP probes with response bodies discarded. It did not submit authorization, registration, token, refresh, revocation, introspection, or MCP payloads. It did not read cookies, credentials, environment values, configuration contents, database contents, or response headers

## Runtime

```text
verified_at: 2026-09-03T23:58:58Z
host: fedora
user id: 1000
rollback manifest: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
runtime image id: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
container state: running
container health: healthy
restart count: 0
OOM killed: false
readiness: HTTP 200
```

## Discovery And Transport

```text
GET /.well-known/oauth-protected-resource/toolset/defend_memory/lazymcp: HTTP 404
GET /toolset/defend_memory/lazymcp/.well-known/oauth-protected-resource: HTTP 404
GET /.well-known/oauth-protected-resource/lazymcp: HTTP 404
GET /lazymcp/.well-known/oauth-protected-resource: HTTP 404
GET /.well-known/oauth-protected-resource/lazymcp/defend_memory: HTTP 404
GET /lazymcp/defend_memory/.well-known/oauth-protected-resource: HTTP 404
GET /.well-known/oauth-authorization-server/mcp: HTTP 200
GET /toolset/defend_memory/lazymcp: HTTP 404
GET /lazymcp: HTTP 401
GET /lazymcp/defend_memory: HTTP 401
GET /mcp: HTTP 401
```

The exact toolset resource has neither supported discovery alias nor a transport route on the healthy rollback image. This is a hard prerequisite failure before principal authorization or token creation

## Non-Secret Credential Contract

```text
audience: https://litellm.defend.tech/toolset/defend_memory/lazymcp
audience sha256: 088fc4a965db7f6770e4b487f2c26dd0a591315d4fedf86d7e2491dd3e924c14
supported client type: public DCR client
token endpoint auth: none
PKCE: S256 required
access lifetime: 3600 seconds
refresh lifetime if separately retained: 1209600 seconds
refresh revocation: RFC 7009 /revoke
access revocation: expiry or authorized-principal deactivation
```

No client identifier, token identifier, token checksum, or expiry timestamp was recorded because no client was registered and no token was minted

## Storage Boundary

Fedora `/run/user/1000` is owner `staticduo`, mode `0700`, and tmpfs-backed. The configured Syncthing folder reported by the active service is `~/.config/opencode`; `/run/user/1000` is outside that folder. A future secret file must be placed only under an owner-only task directory in `/run/user/1000`, mode `0600`, and removed after the bounded consumer finishes or any stop condition fires

## Preservation

No Fedora service, file, selector, image, config, auth policy, database, registration, principal, or credential changed. No NAS command or connection was made
