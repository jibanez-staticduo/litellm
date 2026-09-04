# TASK-2026-09-03-008 Evidence Summary

## Summary

REJECT. Fedora is healthy on the exact rollback digest, but that image does not expose any canonical LazyMCP protected-resource metadata or the exact toolset transport. Both supported RFC 9728 discovery forms for `https://litellm.defend.tech/toolset/defend_memory/lazymcp` return HTTP 404, and the transport itself returns HTTP 404. A supported DCR client therefore cannot discover or obtain a bearer bound to that audience from the required healthy rollback runtime

No authorization flow was opened, no principal was asked to consent, no client registration was submitted, and no token, authorization code, verifier, client secret, cookie, or credential-bearing URL was created, read, printed, retained, or exposed. No credential file was created because there was no valid credential to store

## Work Performed

- Read the task, parent failure, diagnostic runbook, approved SCR, architecture contract, repository guidance, and relevant CodeMaps and DCR implementation
- Verified Fedora still runs exact rollback manifest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, healthy with restart count `0`, OOM false, and readiness HTTP 200
- Probed only public, unauthenticated, body-discarded status codes for the canonical toolset discovery aliases and transport
- Confirmed the aggregate authorization-server metadata endpoint exists, but did not misuse it because the required exact resource is not discoverable or routable on this image
- Defined the supported short-lived credential lifetime, safe owner-only storage location, audience checksum, and destruction/revocation procedure for a future compatible runtime without creating any secret material
- Made no candidate deployment, selector/config/auth/source/database change, credential broadening, or NAS access

## Acceptance Criteria Coverage

- **AC-1: REJECT.** The supported discovery prerequisite fails on the healthy rollback image, so no DCR authorization-code flow was started and no broader or unsupported credential was substituted
- **AC-2: REJECT.** No exact-audience bearer could be minted. The required audience is recorded verbatim with SHA-256 `088fc4a965db7f6770e4b487f2c26dd0a591315d4fedf86d7e2491dd3e924c14`; no token-derived checksum exists because no token exists
- **AC-3: NOT CREATED.** The selected future handoff location is Fedora tmpfs under `/run/user/1000/`, mode `0600`, inside an owner-only `0700` directory. It is outside the repository and configured Syncthing folder. The file must be unlinked after the bounded TASK-006 request, on expiry, rollback, cancellation, or any failed gate. If a refresh credential is ever retained separately, revoke it through the advertised RFC 7009 endpoint before unlinking. An access bearer is stateless and expires after 3600 seconds
- **AC-4: BLOCKED.** Aggregate, other-scope, and `/mcp` negative requests cannot prove cross-audience rejection without a minted exact-audience bearer. Sending any existing legacy key would test the wrong credential and weaken the gate
- **AC-5: PASS.** Fedora remained on the exact rollback image and healthy; no runtime/config/auth/schema/source/database mutation occurred, and NAS was untouched

## Safe Runtime Evidence

```text
verified_at: 2026-09-03T23:58:58Z
rollback manifest: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
runtime state: running, healthy, restart 0, OOM false
readiness: HTTP 200
toolset discovery, path-inserted: HTTP 404
toolset discovery, path-appended: HTTP 404
toolset transport: HTTP 404
aggregate authorization-server metadata: HTTP 200
aggregate transport without credential: HTTP 401
NAS access: none
```

## Secure Handoff Contract

A future credential preparation attempt may proceed only after PMA authorizes a runtime that serves both canonical discovery forms and the exact toolset transport while preserving the architecture contract. Use a public DCR client with S256 PKCE and the existing authorized Fedora principal. Bind both authorization and token redemption to the exact resource. Retain only the one-hour access bearer needed by TASK-006; do not hand off a refresh token unless PMA explicitly requires renewable access

Create an owner-only directory in Fedora tmpfs, for example `/run/user/1000/litellm-task-008-credential`, mode `0700`, and write the bearer atomically to `access-token`, mode `0600`, with no newline or metadata in the secret file. Pass only that fixed path out-of-band to TASK-006. Do not place it in a shell argument, shell history, process title, environment dump, repository, evidence, Syncthing, logs, or a credential-bearing URL

Before handoff, use the bearer exactly once per negative audience with empty or harmless body-discarded requests and no retries. Require invalid-token rejection from `https://litellm.defend.tech/lazymcp`, one different valid scope under `/lazymcp/{scope}`, and `https://litellm.defend.tech/mcp`, while the exact toolset endpoint admits the credential. Record status and challenge class only. Never retain headers, bodies, or URLs carrying authorization material

After TASK-006 consumes the bearer, or on any stop condition, unlink the access-token file and remove the directory. Access-token invalidation is expiry or authorized principal deactivation because the supported endpoint revokes refresh tokens, not stateless access tokens. If a refresh token was retained under separate authorization, submit it to `/revoke` with its DCR client identifier, require HTTP 200, then unlink both credential files and the client identifier. Record only destruction time, expiry time, audience, and non-secret outcome

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap documentation changed. The existing architecture contract already defines the required routes. This packet records an operational incompatibility of the rollback image, not a new supported behavior

## Open Risks

- TASK-006 remains blocked because no exact-audience bearer exists
- The approved candidate exposes the required DCR surface but cannot be deployed merely to mint a prerequisite credential under this task's explicit no-candidate boundary
- Cross-audience rejection remains unproven in Fedora production until a compatible authorized runtime can mint the exact bearer

## Recommended Next Step

PMA should reject reopening TASK-006 with the current rollback runtime. Route the smallest governed prerequisite that makes the approved exact LazyMCP DCR surface available without using an unqualified production candidate, then reopen this task to mint, isolate, negatively test, and hand off the one-hour bearer

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT CREDENTIAL PREPARATION; FEDORA ROLLBACK HEALTH PASS. Exact rollback manifest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04` is healthy with readiness 200, restart 0, and OOM false, but both supported RFC 9728 discovery forms and the exact `/toolset/defend_memory/lazymcp` transport return 404. The aggregate authorization server alone cannot mint a supported provable credential for a resource the running image does not expose. I did not start authorization, use a legacy key, create or expose secret material, deploy the candidate, change config/auth/source/schema/database, or access NAS. TASK-006 remains blocked. Authorize a compatible exact-resource DCR runtime through the smallest governed path, then reopen TASK-008 and use the secure handoff and destruction contract in its evidence summary
