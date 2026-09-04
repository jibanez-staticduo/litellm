# Reopen 3 Supported-API Contract Blocker

## Outcome

Reopen 3 stopped at the mandatory pre-creation API proof. No temporary principal was created and the candidate was not deployed

The amended SCR requires one atomic `/user/new` call containing the generated password, exact least-privilege object permission, `internal_user_viewer`, denied models, and `auto_create_key=false`. Fresh source/runtime contract checks prove `/user/new` cannot accept or retain a password:

```text
candidate NewUserRequest password field: false
candidate parsed request retains password: false
rollback NewUserRequest password field: false
rollback parsed request retains password: false
live OpenAPI /user/new password property: false
```

`/user/update` supports setting a password and clearing object permission, while `/user/delete` supports deletion. However, composing `/user/new` followed by `/user/update` would violate the amendment's required atomic password-backed creation and its prohibition on follow-up repair before use. Direct database writes, container-side application calls, alternate endpoints, and weakening the atomic gate are also prohibited

The candidate probe ran in disposable `--rm --network none` containers. No image selector, production service, database, principal, key, membership, grant, login, DCR, consent, token, request, or NAS state changed

## Orchestration Resume Check

At `2026-09-04T06:52:41Z` Fedora was already and remained on the exact rollback digest. There was no active Reopen 3 watchdog, maintenance clock, tmpfs auth workspace, candidate container, or task-owned user. The stale `.active` pointer still names the completed first attempt and does not represent a live candidate or watchdog

```text
selector/runtime: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
container: running, healthy, restart 0, OOM false
liveliness/readiness: HTTP 200/200
task-owned users: 0
task auth workspace: absent
candidate deployment in Reopen 3: no
temporary principal created: no
diagnostic request sent: no
rollback needed: no
NAS touched: no
```

## Root Cause And Exact Governed Fix

Classification: specification/API-contract mismatch. The approved temporary-principal lifecycle assumes `/user/new` accepts `password`, but the actual candidate and rollback `NewUserRequest` schemas do not define that field and Pydantic drops it. Existing endpoint prose documents password only on `/user/update`

The smallest governed fix is either:

1. Amend the SCR to explicitly authorize a two-step supported API transaction: atomically create the fully least-privilege non-login user with `/user/new`, immediately set only its password with `/user/update` before login, verify the complete returned/read-back state, and run cleanup on any gap; or
2. Implement, test, qualify, sign, and authorize a new candidate where `/user/new` accepts and hashes a password atomically

No correction was applied in production
