# Fedora Final Stream-Safe 1.98.0 Deployment Evidence

## Summary

Fedora is healthy on the same immutable LiteLLM 1.98.0 candidate running on NAS. The exact 27-model, 24-fallback-rule, two-account topology, protected files, credential metadata, dependencies, mounts, networks, and unrelated service count remain preserved. Native client `stream=false`, corrected Codex account2, qualified regular, public fallback, and full LazyMCP gates passed. A ten-minute observation passed with zero restarts/OOM and no concrete stream, auth, device-flow, migration, schema, patch, or response failure logs. NAS remained healthy and byte-for-byte unchanged on the candidate, and stable remained held at its inherited digest

## Work Performed

- Captured fresh Fedora image, health, inventory, routing, protected-file, credential-metadata, dependency, service-count, mount, network, registry, and rollback baselines
- Backed up the exact Fedora `.env` under a protected host release directory before mutation
- Changed only `LITELLM_IMAGE`, pulled the exact candidate digest, and recreated only `litellm` with `--no-deps`
- Corrected an initial deployment-harness identity assumption after Fedora proved that its local image ID equals the manifest digest, unlike NAS Docker's config-ID representation. The harness had already restored the tested rollback image; rollback health passed before the corrected deployment
- Verified candidate manifest, local identity, architecture, LiteLLM version, OCI revision/version, readiness, liveliness, restart, OOM, and rollback readiness
- Used the corrected Codex Lite payload with list input, `reasoning.context=all_turns`, effort `high`, summary `detailed`, native streaming, `store=false`, encrypted reasoning inclusion, disabled parallel tool calls, and the Codex Responses Lite header
- Completed native `stream=false`, qualified regular, direct account2, public fallback, LazyMCP status/describe/tool-list, and harmless `defend_memory-find` smoke checks
- Completed a ten-minute observation and repeated full preservation, health, topology, credential, dependency, log, NAS-isolation, and stable-tag checks

## Acceptance Criteria Coverage

- **AC-1: PASS**. Fresh baseline matched the preserved state: rollback image resolved locally and in the registry; Fedora was healthy with zero restarts/OOM; exact 27-model/two-account topology, 24 fallback rules, protected hashes, credential metadata, dependencies, five mounts, two networks, and 47 running services were captured
- **AC-2: PASS**. Fedora runs `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, LiteLLM 1.98.0, revision `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`. Only the LiteLLM image selector changed and only LiteLLM was recreated with `--no-deps`
- **AC-3: PASS**. Readiness/liveliness are HTTP 200, health is healthy, restarts remain zero, `OOM=false`, and the ten-minute observation passed. Concrete release-blocking log categories are zero. Two disclosed generic tracebacks are non-blocking success-telemetry callback errors, not request, stream, auth, schema, migration, patch, or candidate failures
- **AC-4: PASS**. Post-deploy projections match preflight exactly: 27 public rows, 27 deployment rows, 24 fallback rules, seven default-qualified and seven account2-qualified deployments, bidirectional cross-profile policy, protected hashes, five exact credential metadata records, three exact dependency identities, five mounts, two networks, and 47 running services
- **AC-5: PASS**. Native client `stream=false` completed HTTP 200 SSE with nine ordered events and one `response.completed`. Qualified regular completed valid HTTP 200 SSE through its configured account2 fallback after the inherited primary quota disposition. Direct account2 and public fallback each completed HTTP 200 SSE with nine ordered events, one terminal completion, exact account2 deployment selection, and no stream/auth/device/payload/model errors
- **AC-6: PASS**. LazyMCP protocol `2025-11-25`, exact gateway tool list (`mcp_status`, `mcp_describe`, `mcp_call`), status, `defend_memory-find` describe, and harmless tool smoke passed
- **AC-7: PASS**. NAS retained container `1fc657b5b51b...`, start time `2026-08-19T02:09:29.869606517Z`, candidate manifest/config identity, healthy state, zero restarts/OOM, five mounts, and HTTP 200 readiness/liveliness. Stable remained held at `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- **AC-8: PASS, APPROVE CROSS-HOST QA**. Both hosts now run the exact candidate manifest and pass the required functional, topology, LazyMCP, observation, preservation, and isolation gates. Stable was not promoted

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. No application source or steady-state behavior changed; this task and evidence packet record operational deployment truth

## Open Risks

- The default Fedora ChatGPT profile retains its documented external provider quota condition. During this run, qualified regular and public requests completed through the preserved account2 fallback
- Candidate logs contain two generic tracebacks from non-blocking cost/Prometheus success-telemetry callbacks caused by a missing standard logging object. All requests completed successfully and every concrete release-blocking category remained zero
- The first deployment harness reused NAS's config-ID expectation on Fedora and automatically restored rollback despite no candidate failure. The corrected host-specific identity gate then passed and Fedora completed the full release matrix
- `staticeng_validate` remains subject to inherited repository-wide broken links and missing CodeMaps

## Recommended Next Step

PMA should hand this packet to cross-host QA. Stable should remain held until independent QA and Tech Lead promotion authorization
