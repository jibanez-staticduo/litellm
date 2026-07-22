---
id: TASK-2026-07-18-002-repair-fedora-codex-provider
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-07-18-001-diagnose-fedora-codex-provider
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-18-002 - Repair Fedora Codex Provider

## Objective
Restore Fedora Codex inference through the existing local Codex Optima provider and verify one end-to-end Responses API stream to LiteLLM.

## Scope
- Preserve the existing running Codex app-server and healthy LiteLLM container.
- Start only `codex-optima.service`; do not edit configuration or credentials unless startup evidence proves a minimal change is necessary.
- Verify service health, listener ownership, LiteLLM readiness, and exactly one no-retry Codex-compatible inference.
- Investigate the prior SIGTERM only through available read-only logs; do not broaden into unrelated lifecycle redesign.

## Acceptance Criteria
- [x] AC-1: `codex-optima.service` is active and owns `127.0.0.1:34160`.
- [x] AC-2: Local provider health and LiteLLM readiness pass.
- [x] AC-3: Exactly one bounded no-retry Responses API request completes through the local provider and reaches LiteLLM.
- [x] AC-4: Existing Codex app-server, LiteLLM deployments, configuration, and credentials are preserved.
- [x] AC-5: Evidence packet contains `SUMMARY.md` and sanitized logs tracing AC-1 through AC-4.
- [x] AC-6: Documentation impact is closed explicitly.

## Handoff
[Agent Message] From: product_manager To: developer

Start only the stopped `codex-optima.service`, verify its health/listener and LiteLLM readiness, then send exactly one no-retry Responses API request through the local provider using existing secret-safe credential helpers. Do not print credentials, prompts, or response content. Preserve the existing Codex app-server and LiteLLM container. Create the required evidence packet and return the shared handoff contract.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Started only `codex-optima.service`; it is active and owns `127.0.0.1:34160`
- Preserved the running Codex app-server, healthy LiteLLM container, deployments, configuration, and credentials
- Reviewed the prior SIGTERM through read-only journal evidence; the available journal shows a clean external stop but not its initiator

### Verification
- Provider `/healthz` and `/readyz` returned HTTP 200
- LiteLLM readiness and liveliness returned HTTP 200; container `07f2bfc52cfb` remained healthy
- Exactly one bounded request used the existing command-backed auth helper, client retries `0`, and `num_retries=0`
- The request returned HTTP 200, completed its SSE stream in 3.406 seconds, and has a corresponding HTTP 200 LiteLLM `/v1/responses` access
- No secret, authorization value, prompt, response content, raw request body, or raw response body was printed or stored in evidence

### Acceptance Criteria
- AC-1 through AC-6 pass with traceability in the evidence summary and three sanitized logs
- No product documentation change is required; operational service ownership and recovery are recorded in the evidence packet

### Evidence
- `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/logs/`

### Open Risk
- The SIGTERM initiator is not present in the available user journal; lifecycle redesign remains outside this bounded repair

## QA: Post Implementation Expectations

[Agent Message] From: qa_engineer To: product_manager

### Verdict
- PASS; recommend closure of TASK-2026-07-18-002
- Evidence-first review validates AC-1 through AC-6, preservation, secret safety, logs, and developer task updates
- QA sent no inference or authentication request and made no Fedora runtime or configuration mutation

### Acceptance Criteria
- AC-1 PASS; recovery evidence and the 2026-07-18 08:46:50 CEST read-only live check show `codex-optima.service` active/running with restart count `0`, and its service process owns the sole `127.0.0.1:34160` listener
- AC-2 PASS; evidence records provider and LiteLLM health HTTP 200, while the QA live check independently returned HTTP 200 for provider `/healthz` and `/readyz` plus LiteLLM readiness and liveliness
- AC-3 PASS; sanitized execution evidence records exactly one bounded Responses request, client retries `0`, `num_retries=0`, HTTP 200, completed SSE, and a correlated LiteLLM `POST /v1/responses` HTTP 200; QA did not repeat it
- AC-4 PASS; before/after evidence preserves the Codex app-server and LiteLLM container, with no configuration, credential, deployment, unrelated-service, or container mutation; current container ID remains `07f2bfc52cfb`, healthy, running, and at restart count `0`
- AC-5 PASS; `SUMMARY.md` and all three referenced sanitized logs exist and provide traceability for AC-1 through AC-4
- AC-6 PASS; documentation impact is explicitly closed as evidence-only operational recovery with no product documentation change required

### Safety And Logs
- Targeted secret-pattern review found no private keys, bearer values, API keys, tokens, passwords, or client secrets in the evidence packet; only safe control labels and the credential-helper path are present
- Current service journal since the recorded start contains the start event, a Node SQLite warning, and successful non-stale model catalog synchronization for 14 models; it contains no service failure or restart
- `gitleaks` was unavailable locally, so secret safety is supported by direct evidence review and targeted pattern scanning rather than a gitleaks run
- Repository-wide `staticeng_validate` remains red on unrelated CodeMap link, locality, and missing-CodeMap findings; no task or evidence schema defect was reported

### Shared Handoff Contract
- Status: QA approved
- Evidence: `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/SUMMARY.md` and `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/logs/`
- Validation: evidence-first plus read-only, non-inference SSH checks of service state, listener ownership, provider health, LiteLLM container state, LiteLLM health, app-server presence, and current service journal
- Preservation: no QA mutation; no repeated inference/auth request; no credential, configuration, service, process, deployment, or container change
- Residual risk: the earlier clean SIGTERM initiator remains unknown from the available journal; lifecycle redesign is outside this task
- Closure recommendation: product manager may mark the task done without another inference request
