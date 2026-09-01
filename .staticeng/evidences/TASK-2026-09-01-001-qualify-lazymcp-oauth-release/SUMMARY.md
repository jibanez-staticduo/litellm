# LazyMCP OAuth Release Qualification

## Summary

**REJECT FOR PROMOTION AND DEPLOYMENT.** Exact final candidate `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e` was published to one unique candidate tag with registry config identity proven. Supply-chain tooling, aggregate SBOMs, one-database scans, Wolfi verification, and a real registered LazyMCP tool call were completed where safe. Release qualification fails because the final image contains one fixable High vulnerability, the exact R6 builder is unavailable, uv/Rust/UI identity-policy verification is incomplete, no approved signing identity exists, and candidate-bound real-tool execution remains environment-blocked

## Work Performed

- Downloaded checksum-pinned Syft 1.51.1, Grype 0.118.0, and Cosign 3.1.3 into owner-only `/tmp/opencode`; no system installation occurred
- Generated Syft JSON, SPDX JSON, and CycloneDX JSON for old/new bases, retained builder, and exact final candidate; owner-only full artifacts remain under `/tmp/opencode/lazymcp-release-qualification`
- Updated Grype once, froze database v6.1.9 and its checksum, and scanned every available comparative subject with auto-update disabled
- Verified the exact Wolfi signature plus SPDX, SLSA v1, and apko attestations; inspected uv, Rust, and UI immutable provenance and signature availability
- Published only `docker.staticduo.com/litellm:lazymcp-oauth-candidate-20260901-9aa92dbf6804`; registry config digest equals the exact local image ID
- Invoked one real registered LazyMCP tool without retaining payload content, then verified production remained healthy and unchanged

## Acceptance Criteria Coverage

- **AC-1: PASS.** Official checksums, versions, amd64 platforms, owner-only modes, and no system installation are recorded
- **AC-2: PARTIAL.** Exact final and all available comparative subjects have three aggregate SBOM formats and checksums. The retained builder is R4; exact R6 builder is unavailable
- **AC-3: PARTIAL.** One frozen database scanned old base, new base, retained builder, and exact final. Exact R6 builder could not be scanned because it was not retained and was not safely reconstructible without a fresh rolling-APK build
- **AC-4: FAIL.** Exact final has fixable High `GHSA-ffg3-p8fm-mjx2` in `restrictedpython 8.1`, fixed in 8.3. No time-bounded exception exists. Retained builder also has eight fixable High matches
- **AC-5: PARTIAL.** Wolfi signature/attestations pass. uv has digest/source/revision plus SPDX/SLSA attestation-manifest but no verifiable Cosign identity. Rust/UI publisher Cosign signatures are unavailable and no explicit exception exists
- **AC-6: PASS.** Unique candidate tag published; registry manifest digest is `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619`; config digest exactly equals local image ID
- **AC-7: BLOCKED.** No approved keyless/KMS identity was available. The digest remains unsigned/unattested; no identity was invented
- **AC-8: BLOCKED FOR THE CANDIDATE.** A real registered LazyMCP tool call passed through the existing gateway, but no isolated candidate-bound DB/config clone was available and deployment was prohibited
- **AC-9: PASS FOR EVIDENCE/PRESERVATION; REJECT OVERALL.** Production stayed healthy and unchanged, evidence is secret-free, and no deployment, restart, DB/config mutation, Git commit, or Git push occurred

## Documentation Impact

Product and architecture documentation are not required because no product behavior or source structure changed. The task and release evidence record the operational qualification result

## Open Risks

- The final candidate cannot be promoted with a fixable High under the stated policy
- Exact R6 builder SBOM/scan evidence is missing; the retained R4 builder is not a substitute
- Candidate digest lacks approved signature and attestation
- Candidate-bound real registered tool behavior remains unverified
- Global `staticeng_validate` remains red on pre-existing repository-wide missing CodeMaps

## Recommended Next Step

PMA should reject this digest for release. Route a governed dependency correction for `restrictedpython`, then produce a newly frozen candidate and retain its exact builder. Separately establish an approved keyless/KMS signing policy and an isolated candidate-bound MCP catalog/database clone before repeating all qualification gates

## Signed Handoff

[Agent Message] From: qa_engineer To: product_manager

REJECT. Exact candidate publication and identity, aggregate SBOMs, same-database scans, Wolfi verification, and production preservation pass, but the final image contains one fixable High, exact R6 builder evidence is absent, signing identity is unavailable, and candidate-bound real-tool execution is blocked. Do not promote or deploy digest `sha256:9f642cc38083d1600e62cfb473799a7d52ba89f6c8ff0c4a00940cddc386e619`
