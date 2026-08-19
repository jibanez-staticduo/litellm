# Reopen 1 Controlled Attempt

## Corrected Preflight

- One-attempt authorization: verified from Tech Lead task `TASK-2026-08-19-025`
- Candidate reference and RepoDigests manifest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Registry manifest config digest, local image ID, and expected running image ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Architecture/version/revision: amd64 / 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Fresh T0: `2026-08-19T00:56:27Z`
- Prior 15-minute auth/device-flow failure matches: 0
- Auth roots and entries: exact allowlist, 0700 directories, 0600 regular non-symlink entries, three exact zero-byte lock paths
- Inventory/routing: exact 32 rows, 16 fallback rules, eight default, eight account2, zero account3 rows/references, public default primary
- Dependency and rollback readiness: PASS

## Candidate Recreation

- Installed the previously validated migrated wrapper/Compose pair
- Changed only `LITELLM_IMAGE`
- Recreated only NAS `litellm` with `up -d --no-deps litellm`
- Running deployment reference equaled the candidate manifest reference
- Running container image ID equaled the candidate config ID, never the manifest digest
- Health/readiness/liveliness: PASS
- Restart/OOM: 0 / false
- Mounts/networks: five mounts, `llm-net` and `npm_npm-net`
- Immediate credential comparison: PASS; one approved lock path advanced only ctime
- Immediate exact topology and dependencies: PASS

## Functional Stop

The first native Responses probe used the required list input, `stream=false`, `store=false`, encrypted reasoning inclusion, disabled parallel tool calls, `reasoning.context=all_turns`, and Codex Responses Lite header

- HTTP status: 200
- Harness outcome: failed while parsing the response body as JSON
- Classification: the harness incorrectly assumed client `stream=false` implies a JSON body. Existing accepted Fedora evidence defines the required behavior as HTTP 200 `text/event-stream` through the native Responses lifecycle
- Remaining Codex default/account2/public and LazyMCP gates: not reached after mandatory stop

Exactly one authorized attempt was made. No retry followed

Result: **MANDATORY STOP AND REJECT**
