# Retained Evidence Review

No runtime request or mutation was performed

## Account2 Classification Sources

- `TASK-2026-08-19-022` records a successful supported account2 refresh followed by direct qualified Responses HTTP 429 with no auth error on NAS 1.92.0, classified there as an allowed provider quota/rate-limit result
- `TASK-2026-08-19-023` records later HTTP 200 from the same account2-qualified family using the proven Codex request shape, confirming profile validity before the release attempt
- `TASK-2026-08-19-024` records candidate identity, health, topology, credentials, dependencies, mounts, and networks passing before direct account2 returned HTTP 429

## Candidate Functional Sources

- The native client `stream=false` request returned HTTP 200 `text/event-stream` with nine valid events, ordered lifecycle, one completion, consistent ID/sequence, correct default selection, and no forbidden errors
- Direct default `chatgpt/gpt-5.6-sol` passed the same candidate SSE and profile assertions
- Direct account2 used the same corrected request shape and returned HTTP 429

## Route Semantics Sources

- The candidate preflight preserved 32 models, 16 fallback rules, eight default-qualified deployments, eight account2-qualified deployments, public default primary, and zero account3 rows/references
- The normalized baseline records all eight public aliases bound to default primary while retaining account2 in all eight public fallback rules

## Repository Validation

- `staticeng_validate`: FAIL on the inherited broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps recorded by the parent task
- `staticeng_repair` dry run: reviewed and not applied because it proposed broad unrelated Markdown normalization and hundreds of CodeMap changes outside this retained-evidence investigation

Result: **APPROVE FINAL NAS DEPLOYMENT UNDER NON-WAIVER ASSERTIONS**
