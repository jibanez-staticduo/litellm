# Candidate-Live DCR Bootstrap Runbook

## Purpose And Boundaries

This runbook augments TASK-007 for a reopened TASK-006. TASK-007 remains authoritative for exact image identities, backup and restore verification, instrumentation, stop thresholds, request body, root-cause classification, final verification, soak, and rollback. This runbook changes only the ordering needed to mint the exact-audience bearer while the candidate is live

Use the frozen subjects from TASK-007: candidate manifest `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3`, candidate config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`, candidate source `bf58974a935521fa570fa7e280c51a00b2e5b54e`, and rollback manifest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`

Do not use a legacy API key, admin key, unscoped session token, proxy-API token, or bearer minted for another resource. Do not create or modify a user, team, object permission, MCP registration, auth policy, runtime configuration, source, database row, container limit, timeout, mutable image tag, or NAS resource. Never print or retain the UI session cookie, flow cookie, client identifier, authorization code, verifier, access token, refresh token, callback URL, token response, request arguments, or response payload in repository evidence

## Exact Candidate Contract

The target protected resource is exactly:

```text
https://litellm.defend.tech/toolset/defend_memory/lazymcp
```

The candidate serves these routes:

```text
GET  /.well-known/oauth-protected-resource/toolset/defend_memory/lazymcp
GET  /toolset/defend_memory/lazymcp/.well-known/oauth-protected-resource
GET  /.well-known/oauth-authorization-server/mcp
POST /register
GET  /authorize
POST /authorize/complete
POST /token
POST /revoke
POST /toolset/defend_memory/lazymcp
```

Both protected-resource discovery aliases must return HTTP 200 with the exact canonical `resource` and `authorization_servers: ["https://litellm.defend.tech/mcp"]`. Authorization-server metadata must report issuer `https://litellm.defend.tech/mcp`, root registration/authorization/token endpoints, authorization-code and refresh grants, `none` among supported token endpoint authentication methods, and S256 support. Metadata mismatch is a rollback condition

`POST /register` is unauthenticated and receives JSON with one loopback redirect URI, `grant_types: ["authorization_code", "refresh_token"]`, `response_types: ["code"]`, and `token_endpoint_auth_method: "none"`. The response must be HTTP 201, have an `llm_dcrc_` client identifier, echo the exact redirect, report `token_endpoint_auth_method: "none"`, and contain no client secret. The identifier is itself a sealed registration and is credential-sensitive operational material even though it is not a bearer

The authorization request uses the same registered loopback redirect, an unpredictable state, `response_type=code`, the exact target resource, and PKCE:

```text
code_verifier: 43 to 128 high-entropy unreserved ASCII characters
code_challenge: BASE64URL-NO-PADDING(SHA256(ASCII(code_verifier)))
code_challenge_method: S256
```

The operator opens the authorization URL only in the browser profile that already represents the approved LiteLLM principal. If that browser has no valid LiteLLM session, the candidate redirects through `/sso/key/generate` and back to the same relative `/authorize` request. Account creation, permission changes, alternate principals, copied session cookies, and auth bypass are prohibited

After authentication, the candidate seals the principal and exact resource in an HttpOnly, Secure, SameSite=Lax flow cookie and redirects to `/ui/connect`. The operator verifies the displayed client origin is the expected loopback origin, makes no server-vault changes, selects `My client is on a remote or SSH machine`, and deliberately clicks `Finish connecting`. That browser POSTs the flow handle plus `delivery=manual` to `/authorize/complete`. The signed-in user must match the flow user. The flow is single-use and expires after 600 seconds

Manual completion displays a callback URL rather than dereferencing browser-local loopback. The authorization code inside it is S256-bound, client-bound, redirect-bound, resource-bound, single-use, and valid for at most 300 seconds. Deliver the callback URL only to a protected stdin reader on Fedora. Do not paste it into shell source, shell history, chat, task comments, a command argument, or evidence. The local reader must verify the exact loopback origin/path and state before extracting the code

`POST /token` uses form encoding with `grant_type=authorization_code`, the extracted code, the same redirect URI, client identifier, verifier, and the exact canonical resource. Omit client secret. The response must be HTTP 200, `token_type=Bearer`, `0 < expires_in <= 3600`, and include access and refresh tokens. Missing or changed resource, wrong verifier, client, redirect, or replay must fail closed. The token endpoint revalidates that the existing LiteLLM user is still active before minting

The access and refresh tokens carry the exact resource. Access admission compares it to the preserved original public path before principal reload or any toolset lookup. A matching token does not grant the toolset by itself; current user/team/organization/IP/server/tool/toolset policy still applies

## Owner-Only Client Workspace

Before candidate deployment, create only an empty task workspace under Fedora's existing user tmpfs, outside the repository and Syncthing, with `umask 077`, parent mode `0700`, and files mode `0600`. The workspace creation is ephemeral instrumentation preparation, not credential creation. The operator must confirm `/run/user/1000` is tmpfs-backed and owned by the executing principal

Use fixed internal files for client state, client identifier, verifier, expected state, callback input, authorization code, access token, refresh token, expiry, and request body. Write each with create-new semantics or atomic rename, no newline for secret values, and reject symlinks or unexpected ownership/mode. Do not put secrets in process arguments or exported environment variables. Read them through stdin, protected file descriptors, or a single owner-only client process. Disable shell tracing, HTTP trace/debug output, redirects outside the expected browser leg, retries, dumps, core files, and command logging

The access-token file is the only artifact consumed by the diagnostic request. Do not copy it into the TASK-006 release directory. The refresh token exists only to revoke its future renewal capability during cleanup and must never be handed to the diagnostic client. The client identifier is needed only for token redemption and refresh revocation

Register cleanup traps before generating any client material. On normal exit, error, signal, watchdog trigger, candidate rollback, browser cancellation, state mismatch, expiry, or maintenance cutoff, the trap must kill the local callback reader and diagnostic client, revoke a minted refresh token when the candidate is responsive, unlink every file, remove the workspace, and verify the paths are absent. Never delay a required rollback to wait for revocation

Repository evidence may retain only UTC and monotonic phase times, endpoint status, metadata equality booleans, PKCE method, public-client/no-secret boolean, access expiry time, exact audience and its already approved SHA-256, positive/negative admission classes, refresh revocation status, destruction time, and path-absence result. Do not retain token-derived hashes, JWT claims, response headers, cookies, callback URLs, or client identifiers

## Watchdog And Timing

Complete TASK-007 Phase 0 first. Create a fresh protected database backup and isolated restore proof, freeze exact identities and protected state, prepare and syntax-check exact rollback, and prove candidate Compose rendering changes only `litellm.image`

Before changing the selector, start TASK-007's independent one-second cgroup/process/host watcher, two-second health watcher, five-second pool/dependency watcher, Docker events, and kernel event capture. Capture at least 30 seconds of rollback baseline. Confirm the automatic rollback process is alive and its command is independently reviewed. The same watcher processes must remain armed through candidate startup, DCR discovery, browser interaction, code exchange, audience probes, diagnostic request, 15-second settlement, credential cleanup, and any rollback

Do not relax TASK-007 thresholds. In particular, during bootstrap or reproduction immediately kill clients and invoke rollback on candidate memory `>= max(B + 2 GiB, 8 GiB)`, growth of at least 512 MiB/s for three samples, host `MemAvailable < 32 GiB`, swap over 512 MiB, memory PSI full avg10 over 0.10, OOM/restart/identity/dependency/security/data/observability failures, or any other listed gate. `B` remains the maximum of the final 30 healthy candidate samples immediately before the diagnostic request. The watchdog must also apply the absolute 8 GiB and host gates before `B` is finalized

The four-hour SCR clock still starts at the selector change. Add this fail-closed bootstrap schedule:

```text
T-45 to T0       TASK-007 preflight, empty tmpfs workspace, rollback and watchdog armed
T+0              exact candidate selector change
T+0 to T+3       candidate identity, migrations, health and bounded startup gates
T+3 to T+4       exact discovery/metadata/challenge checks and DCR registration
T+4 to T+6       existing-principal browser authorization and deliberate manual completion
T+6 to T+6:30    code redemption, expiry check, exact-audience positive/negative proofs
T+6:30 to T+7    final 30-second candidate baseline; bearer must be ready before T+7
T+7              hard bootstrap cutoff: no ready bearer means cleanup and rollback
immediately      one diagnostic request; no unrelated wait or functional suite
request +15s     settlement decision, refresh revocation, destruction verification
```

These are maximum offsets, not targets. Move directly to the next step when ready. Do not consume the broader T+90 or T+120 investigation allowance waiting for a person, login, callback, or token. The short cutoff limits candidate exposure before the diagnostic that justifies it

## Audience Proof And Immediate Reproduction

Audience proof begins only after the token response is safely split into its protected files. It is part of the same candidate-live guarded operation. Disable retries and parallelism. Send harmless, body-discarded authenticated requests serially and retain only status plus challenge/error class

1. Send a minimal `initialize` to the exact `/toolset/defend_memory/lazymcp` resource. Require admission to pass the OAuth boundary and produce the expected MCP success class. If the transport returns a session identifier, do not persist it and do not reuse it for the diagnostic call
2. Present the same bearer to `/lazymcp`. Require HTTP 401 with `invalid_token` and resource metadata for aggregate LazyMCP
3. Present it to one known syntactically valid, distinct `/lazymcp/{scope}` path selected from the pre-recorded non-secret release fixture. Require HTTP 401 with `invalid_token` before catalog or permission behavior. Do not discover or enumerate a scope during the window
4. Present it to `/mcp`. Require HTTP 401 with `invalid_token`

Any exact-endpoint 401/403, any negative audience accepted past OAuth, any missing/wrong challenge, any catalog lookup before a wrong-audience rejection, or any ambiguous result triggers cleanup and rollback. Do not try another token or principal

After the negative `/mcp` result, run no additional discovery, refresh, introspection, login, initialize, or functional probe. Finalize the 30-second candidate baseline `B` while the bearer is already ready, then immediately execute TASK-007's exact single `defend_memory-find` JSON-RPC request against `/toolset/defend_memory/lazymcp` with that access token, concurrency one, no retries, one safe trace ID, and a 75-second client deadline. Response handling and evidence remain exactly as TASK-007 defines

When the call ends or the watchdog fires, wait at most 15 seconds for in-flight counters to return to baseline. A timeout does not prove cancellation. Apply TASK-007's rollback decision before cleanup if waiting would threaten any gate

## Destruction And Revocation

Once the reproduction settles, or immediately on any failure:

1. Stop the callback listener and diagnostic client and close all protected file descriptors
2. If a refresh token was minted and the candidate is still responsive, form-POST it with the same client identifier to `/revoke`; require HTTP 200. The endpoint burns the refresh token's single-use identifier. Never put either value in command arguments or output. The authorization-server document does not advertise this endpoint, so use it only as the candidate source-backed cleanup contract, not as a discovered protocol capability
3. Do not submit the access token to `/revoke`; candidate source revokes refresh tokens, while access tokens are stateless and expire after at most one hour
4. Unlink callback input, code, verifier, state, client identifier, access token, refresh token, expiry, request body, cookies if any local browser automation created them, temporary output, and the workspace. Verify all paths are absent
5. Retain only revocation outcome, destruction UTC/monotonic time, expiry time, and absence result. A revocation failure does not justify retaining the refresh token. Destroy it, roll back, and notify PMA that renewal capability could remain valid until its 14-day expiry unless the existing principal is deactivated through a separately authorized action

TASK-006 may continue to classification and the SCR's full gates only after cleanup is verified. The one-hour access token must not be retained for soak or later functional reruns. Any later DCR verification mints its own task-local credential and destroys it under the same rule

## Bounded Fallback

There is no credential fallback. If either discovery alias, metadata equality, registration, existing-principal sign-in, `/ui/connect`, deliberate consent, manual callback delivery, state verification, code redemption, exact admission, negative-audience proof, or token storage fails, do not switch to a legacy key, admin key, broad bearer, proxy-API grant, unscoped `/mcp` token, different principal, refresh grant, copied cookie, or auth/config change

If the operator has not reached `/ui/connect` by T+5 minutes, cancel. If manual completion has not produced a verified callback by T+6 minutes, cancel. If the exact bearer is not stored, expiry-checked, and audience-proven by T+7 minutes, cancel. Cancellation means burn no second flow, revoke any refresh token already minted, destroy every local artifact, invoke exact rollback, complete TASK-007 rollback verification, and report `DCR bootstrap unavailable` to PMA. Reopening requires a new authorized attempt, fresh backup, fresh watchdog, and fresh DCR flow

If the browser session is expired, the only permitted attempt is the normal `/sso/key/generate` round trip as the same existing principal within these deadlines. If that does not complete, rollback. Pre-authenticating, repairing SSO, creating a principal, changing grants, or extending the bootstrap cutoff is outside TASK-006

## Execution Handoff

[Agent Message] From: technical_architect To: tech_lead

Execute candidate-live bootstrap only as an inseparable prefix to reopened TASK-006. Arm and verify TASK-007's exact rollback plus independent watchers before selector mutation; deploy only the frozen signed digest and require bounded healthy startup. Use the candidate's exact LazyMCP discovery and gateway authorization-server metadata, register one public loopback client, generate high-entropy S256 PKCE, authorize the exact toolset resource through the existing principal's browser session, deliberately choose manual remote delivery, state-check the protected callback on Fedora, and redeem with the same exact resource. Keep every artifact in owner-only `/run/user/1000` tmpfs with cleanup traps and no shell arguments, logs, environment dumps, repository copies, Syncthing copies, or client secret. Require exact toolset admission and serial `invalid_token` rejection at aggregate LazyMCP, one preselected distinct scope, and `/mcp`; then finalize the 30-second baseline and immediately send TASK-007's one 75-second call. Revoke the refresh token, unlink every artifact, and verify absence. If the bearer is not fully audience-proven by T+7 minutes, any auth/audience step is ambiguous, or any existing watchdog gate fires, destroy artifacts and roll back without a request or credential substitution
