# Clean-Telemetry 1.98.0 Candidate Evidence

## Summary

Built and pushed exactly one immutable `linux/amd64` LiteLLM 1.98.0 replacement candidate from clean commit `177c66ef727710a455f058b99f653df9b3e4c0a4`. No host was deployed and no stable/latest tag was moved

Candidate deployment reference: `docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`

Config digest/image ID: `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`

Candidate deployment is **APPROVED FOR INDEPENDENT IMAGE QA AND SEQUENTIAL FEDORA-THEN-NAS DEPLOYMENT**, subject to the gate in `logs/05-sequential-deployment-gate.md`

## Work Performed

- Verified synchronized `main` and `origin/main`, then created a clean detached worktree at the exact required commit
- Ran focused stream, telemetry, terminal logging, Redis usage/auth cache, and cache-settings suites with 350 passes and no failures or skips
- Captured sanitized current NAS and Fedora runtime, rollback, topology projection, protected-file, dependency, and health baselines
- Built once with explicit `linux/amd64`, OCI revision, version, and source labels
- Pushed only one unique candidate tag and resolved its registry manifest plus config digests
- Imported the installed image package and proved both stream guards, both logging-state updates, the ChatGPT fake-stream bypass, and the restored `_init_cache` contract
- Rechecked both running hosts and stable after the push; all remained unchanged

## Acceptance Criteria Coverage

- **AC-1: PASS**. `logs/01-source-and-tests.log` and `logs/03-build-and-image-verification.log` prove synchronized clean source at the exact commit, package 1.98.0, one `linux/amd64` build, and expected OCI revision/version labels
- **AC-2: PASS**. Only `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260819-clean-telemetry-177c66ef72` was pushed. Manifest and config digests resolved, and stable remained `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- **AC-3: PASS**. Bounded installed-package introspection proved sync/async stream guards, sync/async logging-state synchronization, fake-stream bypass, and `_init_cache` resolution/attachment/return behavior. See `logs/03-build-and-image-verification.log`
- **AC-4: PASS**. Focused source suites passed 350 tests with no failures/skips, and image imports/introspection passed. See `logs/01-source-and-tests.log` and `logs/03-build-and-image-verification.log`
- **AC-5: PASS**. Current both-host rollback/identity baselines and the mandatory Fedora-then-NAS gate are recorded in `logs/02-both-host-baselines.md` and `logs/05-sequential-deployment-gate.md`
- **AC-6: PASS**. This evidence contains no credentials, tokens, raw model records, environment contents, or private request payloads. The candidate is approved for the next controlled stage, not deployed or promoted

## Documentation Impact

No product, architecture, or CodeMap update is required. This task created a release artifact and operational evidence without changing source or steady-state behavior

## Open Risks

- The replacement has not received independent image QA or runtime validation on either host
- The current production digest remains the exact rollback for both hosts until each sequential deployment passes
- `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps. The required repair dry-run proposed hundreds of unrelated changes and was not applied under this exact-scope task

## Recommended Next Step

PMA should assign independent image QA against the immutable manifest, then authorize Fedora deployment first. NAS must remain unchanged until Fedora passes the full telemetry, cache, functional, preservation, and observation gate
