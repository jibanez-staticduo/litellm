---
id: TASK-2026-08-31-005-review-lazymcp-oauth-security
complexity: complex
track: investigation
slice: qa
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 7
---

# Task: Review LazyMCP OAuth security boundary

## Objective

Review the implementation for OAuth resource confusion, audience widening, route collisions, reverse-proxy injection, credential leakage, and behavior regressions before candidate construction.

## Acceptance Criteria

- [ ] AC-1: Review parser canonicalization and all accepted/rejected URL forms.
- [ ] AC-2: Review code/access/refresh binding and admission ordering for fail-closed exact audience enforcement.
- [ ] AC-3: Review metadata genericity, challenges, route ordering, split-component ownership, and preservation boundaries.
- [ ] AC-4: Review tests for meaningful regression and mutation sensitivity.
- [ ] AC-5: Return ordered findings with file/line references and pass/reject verdict.

## Expected Evidence

- Signed review in task file or `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`.
- No runtime/test edits unless PMA reopens the implementation task.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Perform a security-focused code review of the approved SCR implementation. Do not implement fixes directly. Findings first, ordered by severity, with exact file/line references. Confirm whether a clean isolated Docker candidate can be assembled from the task-owned diff while excluding unrelated dirty source changes. Return the shared output contract and explicit authorization or rejection for candidate build.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

Completed the security-focused review without editing implementation or tests. Verdict: REJECT; candidate construction is not authorized

The review found two high-severity defects: malformed case-variant LazyMCP resources can fall into the legacy unscoped grant flow, and the canonical URL owner does not enforce trusted authority plus production HTTPS/loopback-only HTTP. It also found incomplete LazyMCP 401 challenge conversion and material mutation-sensitive test gaps around proxy/root handling, DCR negatives, challenge matrices, and route-owner original-path preservation

All acceptance criteria and the clean-worktree isolation procedure are recorded in `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`

## Tech Lead Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen the implementation task and route the ordered findings to Developer and QA. Do not build a candidate until fixes pass re-review. A later candidate can be isolated in a clean detached worktree at a recorded base by applying only a reviewed task-owned patch manifest and verifying the resulting path list before build

## Reopen History

### Reopen 1 - Security re-review after implementation fixes

Re-reviewed on 2026-08-31 after the implementation added malformed-resource rejection, trusted-base enforcement, complete LazyMCP challenges, expanded security matrices, and route-owner original-path regressions

Verdict remains REJECT and candidate construction remains unauthorized. The malformed-resource, challenge, matrix, and original-path findings are resolved, but trusted-authority enforcement still has two bypasses: an invalid non-empty `PROXY_BASE_URL` is treated as configured after the shared resolver ignores it, and an untrusted remote request can select a loopback authority with its Host header. The broadened candidate classifier also rejects legacy `/mcp` resources whenever `lazymcp` appears anywhere else in the URL, violating the `/mcp` preservation boundary

Reopen findings, independent probes, acceptance-criteria coverage, and the candidate decision are appended to `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`

## Tech Lead Reopen Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen re-review rejects candidate construction. Route the remaining trusted-authority bypasses and overbroad legacy-resource classification regression back through the original implementation task, then request another bounded security review

### Reopen 2 - Bounded security re-review

Re-reviewed on 2026-08-31 against implementation evidence logs 13 through 16 and the exact trusted-base/classifier changes

Verdict remains REJECT and candidate construction remains unauthorized. The invalid configured-base fallback and remote loopback-Host bypasses are resolved. The legacy preservation fix is incomplete: a supported slash-containing per-server resource such as `/mcp/team/lazymcp` is still classified as a malformed LazyMCP candidate and rejected with `invalid_target`. The new regressions cover a hostname containing `lazymcp` and a hyphenated server segment, but not the exact `lazymcp` segment in a multi-segment legacy server identifier

The bounded finding, independent verification, AC coverage, and candidate decision are appended to `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`

## Tech Lead Reopen 2 Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen 2 remains rejected. Preserve every same-origin path beginning with the legacy `/mcp` family, including slash-containing server identifiers, while retaining malformed LazyMCP fail-closed behavior; add the exact DCR regression and request one more bounded review

### Reopen 3 - Final bounded security re-review

Re-reviewed on 2026-08-31 against implementation evidence logs 17 through 20 and the exact legacy `/mcp/team/lazymcp` classifier/DCR regressions

Verdict remains REJECT and candidate construction remains unauthorized. The exact root-mounted `/mcp/team/lazymcp` legacy case is fixed, and the prior trusted-authority and audience controls remain intact. However, the classifier's unconditional rule that any preceding `mcp` segment makes a candidate legacy creates a root-path bypass: when the trusted external base itself ends in `/mcp`, malformed case-varied LazyMCP resources such as `https://gateway.example/mcp/LazyMCP` are not classified as LazyMCP candidates and fall back into the unscoped legacy authorization flow. This violates the approved non-empty-root and malformed-resource fail-closed boundary

The finding, independent root-path probe, AC coverage, and candidate decision are appended to `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`

## Tech Lead Reopen 3 Handoff

[Agent Message] From: tech_lead To: product_manager

Reopen 3 remains rejected. The final classifier decision must be request/root-aware so `/mcp/team/lazymcp` remains legacy while `{trusted-root}/LazyMCP` still fails closed when the configured root is `/mcp`; add that authorization regression before candidate approval

### Reopen 4 - Final bounded security approval

Re-reviewed on 2026-08-31 against implementation evidence logs 21 through 24, the request/trusted-root-aware classifier, its call site, and exact parser/authorization regressions

Verdict: PASS. No blocking findings remain in the bounded security review. Trusted-root malformed LazyMCP requests fail closed, root-mounted `/mcp/team/lazymcp` remains legacy, trusted-authority and HTTPS controls remain intact, every reviewed LazyMCP challenge remains exact, and code/access/refresh plus pre-reload admission remain exact-audience bound

Candidate construction is authorized only from base revision `9af49e5b34e25cdc9ad40f9bb50a178f40320417` in a clean detached worktree, applying the exact seven-path runtime manifest recorded in `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`. The shared dirty worktree itself remains prohibited as a Docker context

## Tech Lead Reopen 4 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Security review authorizes isolated candidate construction from the recorded base and exact runtime manifest. Build and smoke remain required before promotion; this approval does not authorize replacing or mutating the running production container

### Reopen 5 - TASK-015 test-only and retained-image review

Re-reviewed on 2026-08-31 against TASK-015, TASK-003 Reopen 5 test additions, evidence logs 25 through 28, retained-image provenance, and the frozen runtime fingerprints

Verdict: PASS. No blocking findings. Reopen 5 changes only tests/evidence; the authorized application patch, parser, Dockerfile, and retained image are unchanged. The tests meaningfully pin all six discovery aliases to generic fail-closed 404 for an untrusted Docker-style peer and exact configured success under reserved HTTPS `PROXY_BASE_URL=https://candidate.invalid`. Aggregate, scoped, and toolset challenge tests prove no Host-derived challenge without trust and exact configured challenges with trust

Read-only re-smoke of retained image `sha256:0ade7608d10588994a73d45ffb1bb66e994966fe71edd640a9599ffca754fcdf` is authorized without rebuild, using only the isolated smoke environment and reserved HTTPS public-base value documented in the review evidence. Production replacement/restart/configuration/database/credential mutation remains unauthorized

## Tech Lead Reopen 5 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Authorize TASK-006 retained-image re-smoke without rebuild using `PROXY_BASE_URL=https://candidate.invalid`. Require exact discovery/challenge assertions, retained image-ID verification, full prior preservation/reconnect gates, production invariants, and cleanup; deployment remains unauthorized

### Reopen 6 - TASK-016 admission-order security review

Re-reviewed on 2026-08-31 against TASK-016, TASK-003 Reopen 6 runtime/tests/docs, evidence logs 29 through 32, and the exact `proxy_server.py`/`server.py` changes

Verdict: REJECT. Candidate freezing/build is not authorized. Missing and invalid credentials now receive exact catalog-free toolset challenges before database lookup, and authenticated DB-down/unknown/permitted ordering is correct. However, an intentionally anonymous admission returns `user_api_key_auth=None`; both the new name-to-ID lookup and `_apply_toolset_scope()` are conditional on non-None auth, so the request bypasses database existence and toolset permission resolution entirely. This contradicts TASK-016's explicit anonymous-admission contract and can widen an explicit toolset endpoint into unscoped LazyMCP behavior

The review also identifies missing mutation-sensitive lifecycle coverage: the new ContextVar reset is asserted only after a successful route call, not after handler failure or across concurrent toolset requests as TASK-016 required. Detailed findings and verification are appended to `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`

## Tech Lead Reopen 6 Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT. Route anonymous admission through the same post-admission database/name/scope boundary rather than using non-None auth as the signal that admission completed; preserve explicit anonymous policy while preventing unscoped toolset fallback. Add anonymous, exception-reset, and concurrent-context regressions, then request bounded re-review before freezing a new server.py-inclusive candidate

### Reopen 7 - Anonymous/toolset closure and candidate freeze

Re-reviewed on 2026-08-31 against TASK-003 Reopen 7 runtime/tests/docs, evidence logs 33 through 36, and the exact admission/context/toolset changes

Verdict: PASS. No blocking findings remain. Anonymous successful admission now reaches DB/name resolution and terminates as 503, 404, or explicit 403; it cannot fall through to aggregate LazyMCP. Authenticated unauthorized/permitted behavior remains 403/scoped success. Challenge-before-lookup, non-enumeration, double-binding fail-closed behavior, success/exception reset, and concurrent name isolation are mutation-sensitive and passing

New isolated `linux/amd64` candidate construction is authorized from base `9af49e5b34e25cdc9ad40f9bb50a178f40320417` using the frozen nine-path manifest, checksums, OCI provenance, and build/smoke constraints recorded in `.staticeng/evidences/TASK-2026-08-31-005-review-lazymcp-oauth-security/SUMMARY.md`. The manifest includes `server.py`; the retained prior image is not valid for this correction. Deployment, promotion, production mutation, and arm64 remain unauthorized

## Tech Lead Reopen 7 Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Freeze and build a new isolated amd64 candidate only from the exact nine-path manifest and current pinned OCI/toolchain inputs in review evidence. Require reserved HTTPS smoke identity, complete TASK-006 gates, immutable image evidence, production invariants, and cleanup. Promotion/deployment remain blocked pending independent supply-chain gates and final review

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-005 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
