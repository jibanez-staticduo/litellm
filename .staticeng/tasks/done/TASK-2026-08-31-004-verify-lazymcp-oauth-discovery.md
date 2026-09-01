---
id: TASK-2026-08-31-004-verify-lazymcp-oauth-discovery
complexity: complex
track: investigation
slice: qa
status: done
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-08-31-003-implement-lazymcp-oauth-discovery
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: Independently verify LazyMCP OAuth discovery

## Objective

Independently validate implementation correctness, test quality, exact audience isolation, preservation boundaries, and Docker-candidate readiness against the approved SCR.

## Acceptance Criteria

- [ ] AC-1: Review all task-owned runtime/test diffs for SCR coverage and missing cases.
- [ ] AC-2: Independently run focused and mapped tests with no required failures or skips.
- [ ] AC-3: Independently verify lint/type gates and exact cross-resource rejection behavior.
- [ ] AC-4: Confirm `/mcp`, MCP REST, permissions, and upstream auth preservation evidence is sufficient.
- [ ] AC-5: Produce a signed pass/reject report with exact findings and evidence paths.

## Expected Evidence

- `.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/SUMMARY.md`
- Logs for independent commands, with no secrets or OAuth artifacts.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Read the approved SCR, architecture handoff, implementation task, implementation diff, and Evidence Packet. Do not modify runtime implementation unless PMA reopens the original task. You may add QA evidence and task updates only. Run independent focused checks, inspect skipped tests, and prioritize audience isolation and preservation regressions. Return the shared output contract with a clear pass/reject verdict.

# Post Implementation Task Updates

## QA Engineer: Post Implementation Expectations

Independent verification completed with a **REJECT** verdict. The focused selection passed 443 tests with no failures or skips, but required Docker candidate smoke is absent, exact audience/challenge and authorization rejection matrices are incomplete, root-path/proxy security coverage is missing, and malformed LazyMCP-shaped resources can fall into the legacy unscoped authorization path

Evidence: `.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

REJECT. Reopen the original implementation task for the exact findings recorded in the QA evidence packet, then return it for independent verification after all required automated and Docker gates pass

## Reopen 1 Review

Re-reviewed the developer's reopened implementation, Reopen History, architecture contract, updated runtime/test diffs, and implementation logs 07 through 12. Independently reran the critical parser, discovery, DCR, signed-token, exact-admission, challenge, original-path, and component-owner matrices: 493 tests passed with no failures or skips. Independent focused Ruff, basedpyright, boundary probes, and `git diff --check` also passed

All prior code-level QA findings are closed. The implementation is **PASS FOR DOCKER CANDIDATE BUILD**. Final task closure remains contingent on building one isolated immutable candidate and passing every secret-free SCR smoke and preservation check against that exact digest

Reopen evidence: `.staticeng/evidences/TASK-2026-08-31-004-verify-lazymcp-oauth-discovery/SUMMARY.md`

[Agent Message] From: qa_engineer To: product_manager

PASS FOR DOCKER CANDIDATE BUILD. All prior QA findings are closed by independent verification. Proceed with the isolated candidate, then return its exact-digest smoke evidence for final closure

## Business Analyst: Workflow Closure

Closed for source/candidate scope only. Exact retained `linux/amd64` candidate is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`. A real authorized upstream tool invocation remains explicitly blocked because the isolated environment intentionally has no production database, registered server, or credentials. This limitation is not waived and must be verified in an authorized lower-risk environment before promotion

Promotion, publication, deployment, production mutation, and arm64 remain **REJECTED / UNAUTHORIZED**. Exact Wolfi signature and attestation verification, aggregate exact-image SBOMs, comparative old-base/new-base/builder/final scans using one current vulnerability database, independent Critical/High disposition, and the real authorized tool invocation are still mandatory promotion gates

[Agent Message] From: business_analyst To: product_manager

TASK-004 is archived as done for source/candidate scope only. Archive status does not authorize promotion, publication, deployment, arm64 use, production mutation, or removal of the retained candidate image
