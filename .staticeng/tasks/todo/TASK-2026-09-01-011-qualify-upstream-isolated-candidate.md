---
id: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
complexity: complex
track: implementation
slice: qa
status: todo
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-010-integrate-upstream-main
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: Qualify isolated upstream candidate

## Objective

Build and comprehensively validate a clean immutable Docker candidate in an isolated environment separate from Fedora and NAS, retaining exact builder/final identities and all promotion evidence.

## Acceptance Criteria

- [ ] AC-1: Candidate and exact builder derive from clean reviewed commits and are retained by immutable identity.
- [ ] AC-2: Isolated DB/config/catalog permits real model, Responses, MCP, LazyMCP discovery/challenge/DCR/audience, initialize, and registered-tool tests.
- [ ] AC-3: Health, migrations, permissions, upstream auth, model inventory, logs, reconnect, and preservation gates pass.
- [ ] AC-4: Exact builder/final SBOMs, same-database scans, signatures/attestations/provenance, and independent Critical/High disposition pass.
- [ ] AC-5: No Fedora/NAS mutation occurs; candidate Evidence Packet is complete and secret-free.

## Handoff

[Agent Message] From: product_manager To: qa_engineer

Do not begin until integration commit is independently approved. Use isolated containers/networks/volumes under `/tmp/opencode`, no production DB/credentials/mounts. Do not deploy, push fork main, or change Fedora/NAS.
