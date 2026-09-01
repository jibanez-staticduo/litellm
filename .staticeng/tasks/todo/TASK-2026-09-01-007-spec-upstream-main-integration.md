---
id: TASK-2026-09-01-007-spec-upstream-main-integration
complexity: complex
track: spec
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: null
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Specify upstream main integration

## Objective

Define the approved behavior, preservation, qualification, Git, isolated-candidate, and Fedora-release contract for integrating all current LiteLLM upstream `main` into the StaticDuo fork.

## Acceptance Criteria

- [x] AC-1: Require inclusion of upstream `main` at exact reviewed commit while preserving all intentional fork behavior.
- [x] AC-2: Require resolution of all merge conflicts without dropping LazyMCP, ChatGPT/Responses, model policy, security, or operational behavior.
- [x] AC-3: Require comprehensive source tests and a fully isolated Docker candidate outside Fedora and NAS.
- [x] AC-4: Require models, Responses, MCP, LazyMCP, OAuth discovery/challenges/DCR/audience isolation, real tool behavior, logs, health, and preservation gates.
- [x] AC-5: Require complete security qualification, exact builder retention, provenance/signing/SBOM/scans, and no fixable High/Critical findings.
- [x] AC-6: Require reviewed commit(s) pushed to fork `main` only after candidate approval, followed by Fedora-only exact-digest deployment with rollback and observation.
- [x] AC-7: Keep NAS deployment out of scope unless separately authorized; preserve production until all prior gates pass.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The user explicitly approved integrating all current upstream main, resolving the merge, testing in an isolated Docker environment separate from Fedora/NAS, then updating fork main and Fedora only after complete confidence. Create an approval-ready SCR and update this task with signed AC evidence. Do not edit source/tests, Git refs, hosts, registry, images, or deployments.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Created approved SCR `SCR-2026-09-01-001-upstream-main-integration` as the fail-closed product, preservation, qualification, Git, and Fedora-only release contract. No implementation or environment mutation was performed

### Work Performed

Defined the exact upstream snapshot and ancestry requirements, exhaustive fork preservation manifest, conflict ledger, comprehensive clean-source gates, fully isolated candidate topology, real model and registered-tool checks, supply-chain policy, independent approvals, no-force fork-main push sequence, exact-digest Fedora release, rollback, observation, and NAS exclusion. Registered the SCR as approved while preserving unrelated registry content

### Acceptance Criteria Coverage

- **AC-1: PASS.** SCR sections `Exact Upstream Inclusion and Git Contract` and `Fork Preservation Contract` require one full reviewed upstream SHA, complete ancestry, attribution of every fork path and commit, and verified preservation or upstream equivalence
- **AC-2: PASS.** SCR sections `Fork Preservation Contract` and `Source Verification Contract` require a reviewed conflict ledger and mutation-sensitive regressions for LazyMCP, MCP, ChatGPT/Responses, model policy, security, authentication, permissions, migrations, logging, and operations
- **AC-3: PASS.** SCR sections `Source Verification Contract` and `Isolated Candidate Qualification` require clean focused, mapped, and repository-wide applicable gates with no required failure or skip, followed by a disposable candidate outside Fedora and NAS
- **AC-4: PASS.** SCR section `Isolated Candidate Qualification` requires candidate-bound health, migrations, model inventory, real Chat Completions and Responses, MCP/LazyMCP/OAuth/audience/permission coverage, reconnects, logs, upstream authentication, and a real registered tool using isolated test-owned state
- **AC-5: PASS.** SCR section `Supply-Chain and Security Qualification` requires exact builder retention, frozen identities, publisher provenance, signatures, attestations, durable SPDX/CycloneDX SBOMs, same-database comparative scans, zero Critical and zero fixable High findings, and independent disposition of remaining High findings
- **AC-6: PASS.** SCR section `Fork Main and Fedora Release Contract` permits a no-force fork-main push only after signed source/candidate approval, then requires the unchanged qualified digest on Fedora with baseline, migration safety, rollback, full verification, and at least 15 minutes of observation
- **AC-7: PASS.** SCR section `NAS Exclusion and Production Preservation` prohibits all NAS release mutation without a separate user-approved SCR and preserves both production environments until every prior gate passes

### Documentation Impact

Added `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` and registered it in `.staticeng/docs/scrs/current.md`. No product overview or feature inventory exists in this repository, and this maintenance integration adds no advertised capability. Any behavior change discovered during conflict resolution requires a separate SCR; implementation must update affected steady-state docs and CodeMaps

### Open Risks

The exact upstream SHA, merge-versus-replay decision, complete dirty-work attribution, conflict map, and executable command matrix remain outputs of the active read-only architecture task. They are deliberately not invented by this specification. Repository-wide StaticEng validation also remains red on established missing-CodeMap debt unrelated to these documentation-only changes

`git diff --check` passes for the three task-owned documentation paths. `staticeng_validate` fails on the established repository-wide missing-CodeMap inventory, beginning with `litellm/llms/gradient_ai`, `litellm/llms/novita`, and `litellm/llms/llamafile`. `staticeng_repair` dry-run confirms those CodeMaps require separate module-boundary decisions and proposes unrelated Markdown normalizations, so no repair was applied

### Recommended Next Step

PMA should accept and close this specification task, then require the Technical Architect to complete the exact snapshot, topology, preservation inventory, conflict map, and implementation-ready verification handoff before activating pre-merge or source work

## Signed Handoff

[Agent Message] From: business_analyst To: product_manager

SCR `SCR-2026-09-01-001-upstream-main-integration` is approved and implementation-ready at the product-contract level. AC-1 through AC-7 are satisfied by the exact-snapshot, preservation, conflict, source, isolated-candidate, security, no-force Git, Fedora rollback/observation, and NAS-exclusion sections. Architecture must now bind the contract to the reviewed upstream SHA and exact execution matrix before implementation begins
