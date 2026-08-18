# Fedora Stream-Safe 1.98.0 Canary Evidence

## Summary

Reopen 3 successfully deployed the immutable LiteLLM 1.98.0 candidate to Fedora and completed the corrected production-functionality gate. Direct account2 and the public alias through account2 fallback each returned HTTP 200 SSE through exactly one `response.completed` with correct deployment selection and no stream/auth/device-flow errors. LazyMCP, isolation, preservation, observation, health, and clean-log gates passed. Fedora remains healthy on the candidate digest. NAS and the stable tag were not changed

## Work Performed

- Re-captured Fedora image, health, inventory, routing, protected-file, dependency, auth-metadata, topology, and rollback baselines
- Verified both the candidate and rollback registry digests before mutation
- Changed only `LITELLM_IMAGE`, pulled the pinned candidate, and recreated only `litellm` with `--no-deps`
- Verified candidate digest, version, revision, architecture, health, restart/OOM state, inventory, routing, topology, protected files, and dependency identities
- Proved a client `stream=false` native Responses request completed over the native SSE lifecycle without `Stream must be set to true`
- Stopped at the mandatory Codex-compatible HTTP 400 failure and immediately restored the prior digest with `--no-deps`
- Re-verified the full Fedora baseline, clean rollback logs, unchanged auth metadata, stable tag, and rollback readiness
- On Reopen 1, re-captured the complete baseline, redeployed the same digest with `--no-deps`, and used the exact Tech Lead-approved regular-profile request shape
- Stopped on the corrected regular-profile HTTP 429 before account2 or LazyMCP checks and again restored the complete Fedora baseline
- On Reopen 2, accepted only the documented qualified-regular quota response, then tested the required public fallback and direct account2 paths
- Rolled back immediately when direct account2 returned non-quota HTTP 400; the required public fallback had also failed with HTTP 429
- On Reopen 3, added the exact required reasoning context, proved direct account2 and public fallback functionality, and completed every remaining gate

## Acceptance Criteria Coverage

- **AC-1: PASS**. Fresh preflight matched the approved baseline: 27 public and 27 deployment rows, 24 fallback rules, seven default and seven account2 qualified deployments, protected hashes, dependency identities, health, and rollback digest
- **AC-2: PASS**. Fedora runs the exact candidate digest/version/revision and only LiteLLM was recreated; dependency identities and the unrelated running-container count remained unchanged
- **AC-3: PASS**. Health/readiness/liveliness passed, restart count remained zero, `OOM=false`, the 60-second stable observation passed, and final logs contain no release-blocking pattern
- **AC-4: PASS**. Exact inventory/routing hashes, two-account topology, dependencies, protected files, and auth metadata match preflight. No auth or device flow occurred
- **AC-5: PASS**. The native Responses probe returned HTTP 200 as `text/event-stream`, emitted `response.created` through `response.completed`, and contained no stream-required error
- **AC-6: PASS**. Corrected direct account2 and public fallback requests each completed HTTP 200 SSE through exactly one terminal event with the expected account2 deployment identity. LazyMCP status, describe, and tool-list passed
- **AC-7: PASS**. Evidence records the failed gate and complete rollback. Stable remains `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`; NAS was untouched

## Documentation Impact

No product, architecture, or CodeMap update is required. This evidence and task record document the Fedora operational deployment truth

## Open Risks

The Fedora gate is complete. The regular profile remains subject to its documented external provider quota condition, so current public availability depends on the preserved account2 fallback until that quota clears

`staticeng_validate` remains blocked by pre-existing broken root links and repository-wide missing CodeMaps. The required repair dry run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA should review the completed Fedora evidence and close the task if accepted. NAS deployment and stable promotion remain separate explicitly authorized steps
