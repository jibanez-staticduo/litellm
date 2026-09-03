# TASK-2026-09-03-001 Evidence Summary

## Summary

PASS for implementation and qualification. Root dependency policy and the generated lock now require Tornado 6.5.8, with no unrelated package upgrade. Exact new amd64 builder `sha256:313f117cf6b3334b403d5f77208400d16c2baa6069de7a82e4f4166226a9dd86` and final `sha256:9c5e9fdaae73e7c4efadf9ef1c9b19045827912195da8f3505f2313b946af8ab` pass runtime checks and same-current-frozen-Grype-DB scans with zero Critical and zero High

## Work Performed

- Inspected the current Tornado advisory, fixed release, PyPI artifacts and upstream LiteLLM correction before editing
- Raised only the root uv Tornado constraint from 6.5.6 to 6.5.8 and regenerated only Tornado lock records
- Passed lock/frozen sync, 300 proxy HTTP/SSE/WebSocket tests, full repository checks, UI gates and pinned Rust gates
- Built exact clean amd64 builder/final targets, verified Tornado 6.5.8 plus native/Prisma imports, and exercised direct HTTP, streaming, WebSocket and form-limit behavior in the final image
- Generated exact SPDX and CycloneDX SBOMs and scanned both subjects against one frozen Grype 0.118.0 database
- Removed disposable build/scanner objects, retained only exact local images and durable evidence, and proved production unchanged

## Acceptance Criteria Coverage

- **AC-1: PASS.** The sole root declaration and lock manifest now require Tornado >=6.5.8, the lock resolves exactly 6.5.8, transitive users were mapped, and no unrelated package version changed
- **AC-2: PASS.** Lock/source, proxy HTTP/SSE/WebSocket, UI, Rust, full repository and exact-image runtime gates pass
- **AC-3: PASS.** Exact builder/final SBOMs use one frozen Grype DB and each reports zero Critical, zero High and zero fixable High
- **AC-4: PASS.** Evidence/checksums, rollback scope, disposable cleanup, StaticEng validation and credential-safe production invariants pass
- **AC-5: PENDING TECH LEAD.** No commit, push, signing, publication, deployment, Fedora mutation or NAS mutation occurred, per the developer handoff boundary

## Documentation Impact

Product, architecture and CodeMap documentation are not changed because this dependency/lock-only remediation changes no application behavior, API, route, schema, module boundary or maintained verification command. The task and evidence record the security and operational result

## Open Risks

- The exact retained images are local image IDs, unsigned and unpublished by explicit scope
- Two Rust live-provider tests remain repository-defined ignored tests; all 244 executable Rust tests passed
- The targeted Python suite and UI emitted existing non-failing warnings, with no warning introduced by the two dependency files
- Parent TASK-011 still requires PMA-controlled full candidate qualification and separate signing approval before any release

## Recommended Next Step

PMA should reopen parent TASK-011 against the exact pushed fork-main commit for complete candidate and signing qualification. Do not deploy

## Signed Handoff

[Agent Message] From: developer To: product_manager

PASS for TASK-2026-09-03-001 implementation. Tornado is minimally raised to 6.5.8 in root dependency policy and the generated lock with no unrelated package upgrade. Lock/source, 300 proxy HTTP/SSE/WebSocket tests, UI, Rust, full repository and exact-image runtime gates pass. Exact amd64 builder `sha256:313f117cf6b3334b403d5f77208400d16c2baa6069de7a82e4f4166226a9dd86` and final `sha256:9c5e9fdaae73e7c4efadf9ef1c9b19045827912195da8f3505f2313b946af8ab` each have zero Critical, zero High and zero fixable High under one frozen Grype database. Evidence and cleanup are complete, production is unchanged, and no commit, push, signing, publication, deployment, Fedora mutation or NAS mutation occurred

## Tech Lead Review

### Summary

PASS. No blocking findings. Independent review confirms that the dependency and lock diff is limited to Tornado 6.5.8, the advisory and upstream fix agree on that patched floor, the retained exact builder/final subjects contain Tornado 6.5.8, and both exact scans report zero Critical and zero High under one frozen database

### Work Performed

- Compared the working diff with fork-main source `082a2e09dea2063a7239af3aaa06a862a5056f17` and upstream remediation `1eea8e283157d3c92be36749b2713607aebc9786`
- Rechecked GitHub advisory `GHSA-mpf4-983q-p7j4`, current PyPI 6.5.8 metadata and all lock artifact hashes
- Parsed old/new locks and proved that Tornado 6.5.7 to 6.5.8 is the only package-version change across 453 locked packages
- Independently reran exact pinned uv 0.11.26 lock validation, image identity/platform/label checks, Tornado imports, evidence checksum verification and StaticEng validation
- Parsed both machine-readable scans and four SBOMs, confirming Tornado 6.5.8, identical Grype DB identity, builder 0 Critical/0 High and final 0 Critical/0 High
- Rechecked task-labelled container/network/volume cleanup and the allowlisted production identity, health, restart and OOM invariants

### Acceptance Criteria Coverage

- **AC-1: PASS.** The sole root policy changes from Tornado >=6.5.6 to >=6.5.8; the lock changes only its manifest constraint and exact Tornado package artifacts
- **AC-2: PASS.** Developer evidence records lock/source, 300 proxy HTTP/SSE/WebSocket tests, UI, Rust and full repository gates; independent lock and retained-image checks pass
- **AC-3: PASS.** Exact builder `sha256:313f117cf6b3334b403d5f77208400d16c2baa6069de7a82e4f4166226a9dd86` and final `sha256:9c5e9fdaae73e7c4efadf9ef1c9b19045827912195da8f3505f2313b946af8ab` have zero Critical and zero High under Grype DB v6.1.9 built `2026-09-03T06:30:55Z`
- **AC-4: PASS.** All seven artifact checksums verify, disposable resources are absent, rollback is the two-file dependency/lock commit, StaticEng passes and production remains unchanged
- **AC-5: PASS.** Tech Lead approved closure; the reviewed commit and non-force fork-main push are recorded in the task handoff, with no signing, publication or deployment

### Documentation Impact

No product, architecture or CodeMap update is required because this dependency/lock-only security correction changes no application behavior, API, schema, route, source boundary or maintained verification command

### Open Risks

The exact retained images remain local, unsigned and unpublished. Parent TASK-011 must rebuild and rerun complete candidate qualification and satisfy its separate signing gate before release

### Recommended Next Step

PMA should reopen TASK-011 against the exact pushed fork-main commit. Keep signing, publication, deployment, Fedora and NAS blocked until separately qualified and authorized

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. TASK-2026-09-03-001 meets AC-1 through AC-5 after independent advisory, upstream, lock, exact-image, SBOM/scan, checksum, cleanup and production-invariant review. The reviewed source and evidence are committed and pushed non-force to fork `main`; the exact local/remote SHA is supplied in the final handoff. No image was signed or published and no deployment, Fedora or NAS mutation occurred
