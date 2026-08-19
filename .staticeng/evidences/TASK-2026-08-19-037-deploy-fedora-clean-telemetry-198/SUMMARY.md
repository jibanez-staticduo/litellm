# Fedora Clean-Telemetry 1.98.0 Deployment Evidence

## Summary

Fedora now runs immutable LiteLLM 1.98.0 manifest `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3` with config digest `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`. Every corrected functional, topology, LazyMCP, preservation, ten-minute telemetry, and cache-log gate passed. Rollback remains ready. NAS and stable remained unchanged

The candidate is **APPROVED FOR NAS DEPLOYMENT**, subject to PMA authorization and the existing sequential NAS gate

## Work Performed

- Captured a fresh Fedora rollback, runtime, topology, protected-file, credential-metadata, dependency, NAS, and stable baseline
- Created a protected Fedora rollback unit and changed only `LITELLM_IMAGE`
- Pulled the immutable candidate and recreated only Fedora LiteLLM with `--no-deps`
- Proved manifest/config, architecture, version, revision, health, readiness/liveliness, zero restarts/OOM, exact topology, and unrelated-service preservation
- Ran native `stream=false`, qualified regular, direct account2, public fallback, profile isolation, and full LazyMCP probes
- Observed the same container for 629 seconds with zero telemetry, callback, usage-cache, cache-poller, stream, auth, migration, schema, patch, response-failure, or traceback findings
- Rechecked Fedora preservation, NAS isolation, stable hold, and rollback resolution

## Acceptance Criteria Coverage

- **AC-1: PASS**. Fresh baseline and protected rollback were captured. Only Fedora LiteLLM was recreated on manifest `35fc5209...f2d3`; registry config is `9975f878...c9a3a`
- **AC-2: PASS**. Identity, health, readiness/liveliness, restart/OOM, exact 27-model projection, 24 fallback rules, two-account 7/7 topology, dependencies, protected state, and unrelated services passed
- **AC-3: PASS**. Native Responses forced SSE despite client `stream=false`; corrected qualified/direct account2 and public fallback probes returned HTTP 200 with one completion, zero blocked errors, and exact account2 selection. LazyMCP status/describe/list/call passed
- **AC-4: PASS**. A 629-second observation spanning approximately 62 poll intervals had zero standard-logging, success-callback, `resolved_usage_cache`, cache-poller, or other release-blocking errors and zero generic tracebacks
- **AC-5: PASS**. NAS retained exact container/start/image/protected state and healthy HTTP 200 probes. Stable remained `b52c094...3e0`; Fedora rollback `42d36549...115b` remains ready
- **AC-6: PASS**. Complete sanitized evidence approves NAS deployment as the next sequential stage

## Documentation Impact

No product, architecture, or CodeMap update is required. This task changed only Fedora runtime image selection and created operational evidence

## Open Risks

- NAS has not yet received this replacement image
- Stable/latest remains intentionally held pending NAS deployment and cross-host QA
- `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps. The repair dry-run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA should authorize the controlled NAS deployment of this same immutable manifest, then assign independent cross-host QA before any stable promotion
