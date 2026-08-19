# Reopen 3 Functional And Observation Gates

## Deployment Boundary

- Fresh T0: `2026-08-19T01:36:59Z`
- Prior 15-minute auth/device-flow failure matches: 0
- Exact manifest/config/version/revision identity: PASS
- Corrected credential lock-ctime gate: PASS; one approved lock advanced only ctime immediately
- Exact 32 models, 16 rules, eight default, eight account2, zero account3, public default-primary topology: PASS
- Candidate health/readiness/liveliness/restart/OOM, dependencies, five mounts, and two networks: PASS immediately
- Only NAS `litellm` was recreated with `--no-deps`

## Exact Functional Matrix

- Native client `stream=false`: HTTP 200 `text/event-stream`, nine JSON events, ordered created/in-progress/completed, one terminal completion, consistent ID/contiguous sequence, correct default selection, PASS
- Direct default Codex: HTTP 200 `text/event-stream`, same complete SSE contract, correct default selection, PASS
- Direct account2: HTTP 429 provider quota/rate category, correct account2 selection, no auth/device/payload/stream/model/routing/candidate error, PASS under Reopen 3 disposition
- Public `gpt-5.6-sol`: HTTP 200 `text/event-stream`, same complete SSE contract, correct default-primary selection, PASS
- LazyMCP tool-list: exactly `mcp_status`, `mcp_describe`, `mcp_call`
- LazyMCP status/mode: enabled / `lazymcp`
- LazyMCP describe memory and harmless `memory-find`: PASS

## Candidate Observation

- Observation started: `2026-08-19T01:39:03Z`
- Ten-minute interval elapsed
- Final credential metadata: PASS; two approved locks advanced only ctime, every other field exact
- Final manifest/config identity: PASS
- Final 32-model/16-rule/default/account2/account3 topology: PASS
- A subsequent assertion in the remaining final health, dependency, protected-hash, patch-hash, auth-log, or clean-log aggregate failed before the final success marker

The harness emitted only `failure_stage=observation`; it did not persist the individual failed assertion or sanitized matching log category. Automatic rollback removed the candidate container and its runtime log. Therefore no narrower cause is asserted and acceptance fails closed

Result: **FUNCTIONAL PASS; FINAL OBSERVATION ACCEPTANCE FAIL**
