---
id: TASK-2026-09-03-001-remediate-tornado-high
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: Remediate Tornado High

## Objective

Upgrade Tornado from vulnerable 6.5.7 to fixed 6.5.8 through the smallest compatible dependency/lock change, verify behavior and exact builder/final scans, then obtain Tech Lead commit/push approval.

## Acceptance Criteria

- [x] AC-1: Identify declarations/locks/transitive constraints and apply only the minimal compatible Tornado >=6.5.8 correction.
- [x] AC-2: Lock, source, proxy streaming/WebSocket/HTTP, UI, Rust and mapped regressions pass.
- [x] AC-3: Clean exact amd64 builder/final scans under one frozen DB show zero Critical and zero fixable High.
- [x] AC-4: Evidence, rollback, cleanup and production invariants pass.
- [x] AC-5: Tech Lead reviews, commits, and non-force pushes fork main; no deployment occurs.

## Handoff

[Agent Message] From: product_manager To: developer

Start from exact current fork main and inspect current upstream Tornado remediation first. Apply the smallest dependency/lock-only fix to at least 6.5.8; no unrelated upgrades. Run targeted Tornado/proxy streaming/WebSocket/HTTP tests plus complete required source gates, build new exact builder/final and same-frozen-DB scans, retain evidence and clean disposable resources. No commit/push yourself, signing, publication, Fedora/NAS mutation or deployment.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

PASS for implementation and qualification. Root dependency policy and generated lock now select Tornado 6.5.8 without unrelated package upgrades. Exact new amd64 builder/final runtime and same-frozen-DB scans pass with zero Critical and zero High

### Acceptance Criteria Coverage

- **AC-1: PASS.** Sole root declaration, lock manifest and exact Tornado package records changed; transitive users are mapped and all unrelated versions are unchanged
- **AC-2: PASS.** Lock/source, 300 proxy HTTP/SSE/WebSocket tests, UI, Rust, complete repository checks and exact-image runtime checks pass
- **AC-3: PASS.** Exact builder `sha256:313f117cf6b3334b403d5f77208400d16c2baa6069de7a82e4f4166226a9dd86` and final `sha256:9c5e9fdaae73e7c4efadf9ef1c9b19045827912195da8f3505f2313b946af8ab` each report zero Critical, zero High and zero fixable High under Grype DB v6.1.9 built `2026-09-03T06:30:55Z`
- **AC-4: PASS.** Durable SBOM/scan/checksum evidence, rollback scope, disposable cleanup, StaticEng validation and credential-safe production invariants pass
- **AC-5: PENDING TECH LEAD.** Developer performed no commit, push, signing, publication, deployment, Fedora mutation or NAS mutation

### Documentation Impact

No product, architecture or CodeMap update is required because the dependency/lock correction changes no application behavior, API, schema, route, source boundary or maintained verification command

### Open Risks

Exact retained images remain local, unsigned and unpublished. Parent TASK-011 must rerun complete candidate and signing qualification after Tech Lead approval before release

### Recommended Next Step

Route the exact diff and evidence to Tech Lead for review, commit and non-force push if approved. Keep publication and deployment blocked

### Signed Handoff

[Agent Message] From: developer To: product_manager

PASS for TASK-2026-09-03-001 implementation. Tornado is minimally raised to 6.5.8 in root dependency policy and the generated lock with no unrelated package upgrade. Lock/source, 300 proxy HTTP/SSE/WebSocket tests, UI, Rust, full repository and exact-image runtime gates pass. Exact amd64 builder `sha256:313f117cf6b3334b403d5f77208400d16c2baa6069de7a82e4f4166226a9dd86` and final `sha256:9c5e9fdaae73e7c4efadf9ef1c9b19045827912195da8f3505f2313b946af8ab` each have zero Critical, zero High and zero fixable High under one frozen Grype database. Evidence and cleanup are complete, production is unchanged, and no commit, push, signing, publication, deployment, Fedora mutation or NAS mutation occurred

## Tech Lead: Post Implementation Expectations

### Summary

PASS. No blocking findings. The exact two-file dependency/lock change selects Tornado 6.5.8 without unrelated package churn, all behavioral and repository gates are evidenced, and exact retained builder/final scans pass with zero Critical and zero High under one frozen database

### Work Performed

- Independently verified `GHSA-mpf4-983q-p7j4`, PyPI 6.5.8 metadata and upstream remediation `1eea8e283157d3c92be36749b2713607aebc9786`
- Proved Tornado 6.5.7 to 6.5.8 is the only package-version change across all 453 lock records
- Reran exact pinned uv 0.11.26 lock validation, retained-image identity/platform/version checks, evidence checksum verification and StaticEng validation
- Parsed exact builder/final SBOMs and Grype reports, confirming Tornado 6.5.8 and one frozen DB with zero Critical and zero High
- Verified disposable cleanup and unchanged allowlisted production identity, health, restart and OOM state

### Acceptance Criteria Coverage

- [x] **AC-1:** Sole root declaration and generated Tornado lock records change; no unrelated package version changes
- [x] **AC-2:** Lock/source, 300 proxy HTTP/SSE/WebSocket tests, UI, Rust, full repository and exact-image runtime gates pass
- [x] **AC-3:** Exact amd64 builder/final SBOM scans share Grype DB v6.1.9 built `2026-09-03T06:30:55Z` and each report zero Critical and zero High
- [x] **AC-4:** Evidence/checksums, rollback scope, cleanup, StaticEng and production invariants pass
- [x] **AC-5:** Tech Lead approved closure; reviewed commit and non-force fork-main push are recorded in the final handoff, with no deployment

### Documentation Impact

No product, architecture or CodeMap update is required because this dependency/lock-only correction changes no application behavior, API, schema, route, source boundary or maintained verification command

### Open Risks

The exact retained images remain local, unsigned and unpublished. Parent TASK-011 must rebuild and rerun complete candidate qualification and satisfy its separate signing gate before release

### Recommended Next Step

PMA should reopen TASK-011 against the exact pushed fork-main commit. Keep signing, publication, deployment, Fedora and NAS blocked until separately qualified and authorized

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. TASK-2026-09-03-001 meets AC-1 through AC-5 after independent advisory, upstream, lock, exact-image, SBOM/scan, checksum, cleanup and production-invariant review. The reviewed source and evidence are committed and pushed non-force to fork `main`; the exact local/remote SHA is supplied in the final handoff. No image was signed or published and no deployment, Fedora or NAS mutation occurred
