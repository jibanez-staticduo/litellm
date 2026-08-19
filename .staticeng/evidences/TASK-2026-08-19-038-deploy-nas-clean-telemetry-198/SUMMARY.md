# NAS Clean-Telemetry 1.98.0 Deployment Evidence

## Summary

Reopen 3 is **APPROVED AND RUNNING** under the user's direct no-rollback override. NAS runs exact replacement manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`, config `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`, LiteLLM 1.98.0, revision `177c66ef727710a455f058b99f653df9b3e4c0a4`

All identity, health, functionality, public/default selection, account2, LazyMCP, exact topology, preservation, ten-minute telemetry/cache, Fedora isolation, stable hold, and evidence-security gates passed. Rollback artifacts remain protected but were not used

The Reopen 2 public failure was a harness expectation defect: public `gpt-5.6-sol` has its own deployment ID while its provider model is the default `chatgpt/gpt-5.6-sol`. Separate status, SSE lifecycle, blocked-error, provider-profile, and selection checks all pass. LazyMCP also passed after using the current configured server/tool identifiers `Memory` / `memory-find` instead of stale identifiers

## Work Performed

- Captured fresh rollback, NAS/Fedora/stable, topology, credential, dependency, mount/network, protected-file, and exact candidate baselines
- Verified byte-identical root/staticduo local replacement identity and skipped registry pull
- Recreated only NAS LiteLLM with `--no-deps` and left the replacement running
- Persisted separate functional status, content-type, SSE lifecycle, blocked-error, quota, provider-profile, and deployment-selection results
- Proved native client `stream=false`, direct default, direct account2, and public default-primary with HTTP 200 and complete nine-event SSE lifecycles
- Proved LazyMCP protocol, exact gateway tools, status, describe, and harmless configured memory call
- Observed the same candidate for at least 600 seconds across 21 health/cache polls
- Reverified exact 32-model/16-rule topology, eight default-qualified, eight account2-qualified, zero account3, credentials, dependencies, mounts/networks, non-image environment, and protected hashes
- Classified generic tracebacks as unrelated backend-connectivity, invalid-key, and unrelated MCP traffic; telemetry, usage-cache, stream, auth/device, migration/schema/patch release-blocking categories were zero
- Secured the complete NAS release/evidence hierarchy to root-owned 0700 directories and 0600 files and reverified its complete hash chain

## Acceptance Criteria Coverage

- **AC-1: PASS**. Fresh baseline/rollback and strict credentials passed; only NAS LiteLLM was recreated on the replacement manifest/config
- **AC-2: PASS**. Identity, health, zero restarts/OOM, exact 32-model/16-rule topology, zero account3, credentials, dependencies, mounts/networks, non-image environment, and protected hashes passed
- **AC-3: PASS**. Native/default/account2/public Responses and Codex checks passed separate HTTP 200, SSE lifecycle, blocked-error, provider-profile, and selection gates. Full LazyMCP passed
- **AC-4: PASS**. The same container completed 21 polls over at least 600 seconds with zero telemetry, usage-cache, stream, auth/device, migration/schema/patch release-blocking findings
- **AC-5: PASS**. NAS release/evidence directories are root-owned 0700, files are root-owned 0600, and the complete hash chain reverified
- **AC-6: PASS**. Fedora remained healthy and byte-identical on the same replacement manifest; stable remained unchanged/missing
- **AC-7: PASS, APPROVE**. Complete evidence approves final cross-host QA

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. This task changed only the NAS runtime image selector and operational evidence

## Open Risks

- Generic logs include unrelated backend-connectivity, invalid-key, and unrelated MCP request tracebacks; none match release-blocking telemetry/cache/stream categories
- Keycloak and Firecrawl restarted independently during the extended observation windows; scoped LiteLLM dependencies remained exact and healthy
- Stable remains intentionally held
- `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps; broad unrelated repair was not applied

## Recommended Next Step

PMA should assign final independent cross-host QA while preserving the stable hold
