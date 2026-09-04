# Reopen 6 Client Artifact Blocker

## Outcome

Reopen 6 stopped after successful corrected email login but before watchdog activation, candidate deployment, DCR, or diagnostic execution. The maintenance client failed while attempting to serialize Python's in-memory `CookieJar` into the owner-only tmpfs workspace: `CookieJar` contains an `RLock` and is not pickleable

All security-sensitive server operations before that client-only failure passed:

- Fresh protected backup, checksum/list, isolated exact-image restore, and rollback unit passed
- Exact candidate identity, signature, SPDX, CycloneDX, and SLSA attestations passed
- Exact Defend server/tool baseline and zero-collision toolset baseline passed
- Exact one-tool task-owned `defend_memory` toolset creation/read-back passed
- Independent cleanup deadline was armed before principal creation
- `/user/new` created one least-privilege non-login viewer with unique email and opaque ID
- The immediately following request was password-only `/user/update`
- Least-privilege read-back passed
- First `/login` using the generated email succeeded
- The separately addressable UI key was extracted into an owner-only artifact for explicit cleanup

The serialization failure occurred before DCR and before candidate deployment. No login retry, alternate identity, second principal, consent, token exchange, audience check, MCP request, ad-hoc patch, or NAS operation occurred

## Cleanup Proof

The already armed supported-API cleanup ran immediately. It explicitly requested deletion of the separately addressable UI key, then cleared the principal grant, deleted the principal, deleted the task-owned toolset last, and destroyed the complete tmpfs workspace

```text
task principal count: 0
toolset count restored: 0
UI key deletion: explicitly requested before principal deletion
task auth workspace: absent
active attempt pointer: absent
candidate deployed: no
diagnostic requests: 0
```

Fedora remains on exact rollback digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, healthy with liveness/readiness 200. No rollback ran because the selector never changed. NAS was untouched

## Root Cause And Exact Governed Fix

Classification: maintenance-client implementation defect, not product authentication. Correct email login is proven. The task-local client incorrectly attempted to pickle `http.cookiejar.CookieJar`; its internal `_thread.RLock` cannot be serialized

The smallest governed fix is to keep one HTTP session process alive through login and DCR, or serialize only cookie name/value/domain/path/secure/expiry fields into an owner-only Mozilla/LWP cookie jar. Validate this harness in a disposable environment before another production reopen. Do not patch LiteLLM, repeat login in this attempt, or retain the UI key as a workaround
