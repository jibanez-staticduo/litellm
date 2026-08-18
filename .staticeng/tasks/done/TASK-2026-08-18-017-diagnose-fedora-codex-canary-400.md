---
id: TASK-2026-08-18-017-diagnose-fedora-codex-canary-400
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-016-deploy-fedora-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-18-017 - Diagnose Fedora Codex Canary HTTP 400

## Objective
Establish the exact reason the candidate's Codex-compatible canary probe returned HTTP 400, determine whether the candidate is defective or the probe was invalid, and define a known-valid Codex gate for retry.

## Safety
- Investigation only; Fedora remains on its restored digest and NAS/stable remain untouched.
- Prefer existing sanitized logs, source, Codex session/client behavior, and isolated/offline validation.
- At most one bounded live request may be used if necessary, with secrets sourced in place and response content sanitized to error category/detail only.
- Do not deploy, edit config/database/models, restart services, or move tags.

## Acceptance Criteria
- [ ] AC-1: Recover the exact sanitized request shape and HTTP 400 error category/detail from correlated client/LiteLLM logs without exposing content.
- [ ] AC-2: Compare the probe with a real Codex `/v1/responses` request and historical known-valid canary evidence.
- [ ] AC-3: Determine whether the failure is candidate code, model/routing, provider state, or invalid probe construction.
- [ ] AC-4: Define a deterministic known-valid Codex-compatible request and success assertions for canary retry.
- [ ] AC-5: Approve or reject reactivation of the original Fedora deployment task.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Diagnose the failed HTTP 400 gate read-only. Preserve restored Fedora, NAS, and stable. Return an explicit root cause and approve/reject decision for resuming the original deployment task.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1 through AC-5 passed.
- HTTP 400 was an invalid canary model selection: `gpt-5.3-codex` is unsupported for Codex with a ChatGPT account.
- Candidate code and provider health were not causal.
- Parent reactivation approved with the recorded `gpt-5.6-sol` native-streaming gate.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1 through AC-5 pass with sanitized evidence under `.staticeng/evidences/TASK-2026-08-18-017-diagnose-fedora-codex-canary-400/`
- The failed probe selected `chatgpt/gpt-5.3-codex`, which the ChatGPT account-backed Codex provider deterministically rejects as unsupported
- Candidate stream behavior was not causal; the earlier native Responses lifecycle passed and isolated transformation forced the required provider fields
- Real Codex session evidence uses `gpt-5.6-sol`; the retry gate is defined for qualified regular and account2 `gpt-5.6-sol` deployments
- Exactly one bounded live request was used to recover the sanitized provider detail; no deployment, restart, configuration/model edit, tag movement, or other host mutation occurred
- **APPROVE** reactivation of the parent Fedora canary task only with the corrected gate and all remaining mandatory checks
- No product, architecture, or CodeMap documentation update is required
