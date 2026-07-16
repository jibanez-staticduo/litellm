---
id: TASK-2026-07-16-002-repair-fedora-litellm-routing-errors
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 1
---

# Task: TASK-2026-07-16-002 - Repair Fedora LiteLLM Routing Errors

## Classification
- **complexity:** standard
- **track:** implementation
- **slice:** foundation

## Objective
Stop Fedora's repeated invalid-Qwen requests and repair any currently unhealthy ChatGPT profile implicated by 401/cooldown exhaustion, preserving all unrelated models and configuration.

## Scope
- Fedora runtime plus the NAS authoritative Syncthing source for the single affected OpenCode model override only.
- Back up affected client configuration mode `0600`, then structurally remove or replace the nonexistent `qwen3.6-35b-a3b-uncensored-nvfp4` catalog/override with the intended deployed model.
- Search Fedora agent/job/config overrides for the stale literal and correct only active request sources.
- Perform secret-safe, no-retry health checks for paired ChatGPT profiles.
- If a profile still returns 401 and supported reauthentication can be completed without user interaction, use the supported workflow; never edit token files directly. If user device authorization is required, stop and return the transient authorization need to PMA without persisting it.
- Do not change generic cooldown policy or invent a same-context context fallback.
- Preserve unrelated models, defaults, credentials, services, and settings.
- Correct the NAS source of truth rather than creating a Fedora-local Syncthing exception; allow normal propagation back to Fedora.

## Acceptance Criteria
- [x] AC-1: Fedora active client catalogs/overrides no longer request the nonexistent Qwen alias and preserve unrelated entries.
- [x] AC-2: The intended deployed Qwen model is resolvable and no new invalid-alias errors appear during bounded verification.
- [x] AC-3: Each Fedora ChatGPT profile receives one no-retry secret-safe health check; current status and selected public model are recorded.
- [x] AC-4: Any remaining 401 is repaired through supported auth or reported as an explicit user-action blocker without direct token editing.
- [x] AC-5: LiteLLM readiness/admin health passes and no configured deployment is lost.
- [x] AC-6: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: developer

Implement this Fedora-only operational repair. Use backups and structured edits, avoid direct database/token edits, and do not alter cooldown/context fallback policy. Verify boundedly with no retries and secret-safe evidence. If device authorization is required, stop at the blocker and return transient details only to PMA; never persist them.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary
- Removed the stale Qwen alias from active Fedora OpenClaw using a structural JSON edit
- Removed the stale override from the NAS authoritative OpenCode configuration and excluded the invalid server-discovered model from resolved catalogs
- Allowed normal propagation to Fedora's unchanged Syncthing `receiveonly` folder; no local exception was created
- Preserved the intended deployed Qwen model and all unrelated settings
- Both Fedora ChatGPT profiles are healthy; no reauthentication was required

### Verification
- NAS and Fedora OpenCode configs and all task backups are mode `0600`; OpenClaw remains mode `0600`
- NAS and Fedora JSON/resolved OpenCode validation pass with zero stale resolved model entries and the intended model retained
- Exactly one no-retry health request per ChatGPT profile returned HTTP 200
- One no-retry request to the intended Qwen model returned HTTP 200
- Readiness, liveliness, and model-info returned HTTP 200; all 19 deployments remain
- Bounded post-restart logs contain zero stale-alias lines
- Generic retry/cooldown and context fallback policy were not changed

### Reopen 1 Resolution
- AC-1 is satisfied through the approved NAS source-of-truth update and normal Fedora propagation
- Post-propagation bounded Fedora logs contain zero stale-alias errors
- No ChatGPT or intended-Qwen inference request was repeated

### Evidence
- `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/SUMMARY.md`
- `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/logs/`

## QA Engineer: Post Implementation Expectations

### Result
- **PASS** based on complete review of the task, Reopen History, evidence summary, and all three sanitized logs
- **Closure recommendation:** close the task; AC-1 through AC-6 are traceable and supported by the evidence packet
- Validation was evidence-only; QA sent no inference/auth requests and made no runtime or configuration changes

### Acceptance Criteria Coverage
- **AC-1 PASS:** NAS-authoritative structural edit, matching exclusion, normal propagation to Fedora's unchanged `receiveonly` folder, zero stale resolved entries on both hosts, intended override retained, and no local sync exception are recorded
- **AC-2 PASS:** the single prior no-retry intended-Qwen request returned HTTP 200; the Reopen 1 bounded window records zero stale-alias lines and zero inference requests
- **AC-3 PASS:** the evidence contains one request block for each Fedora ChatGPT profile; both record `request_count=1`, `num_retries=0`, HTTP 200, and the selected public response model
- **AC-4 PASS:** both profiles record no device-authorization requirement and the configuration evidence records no auth/token-file edit
- **AC-5 PASS:** readiness, liveliness, and model-info returned HTTP 200; deployment count remains 19; container health passed; retry, cooldown, and context-fallback policies are recorded unchanged
- **AC-6 PASS:** `SUMMARY.md` and the three referenced sanitized logs exist at the required evidence path

### Preservation, Safety, and Documentation
- Preservation claims are internally consistent: expected semantic change only passed, intended entries remain, 19 deployments remain, unrelated policy is unchanged, and historical/inactive records were not modified
- NAS and Fedora current configs and all listed backups record mode `0600` after authoritative propagation
- Secret-pattern scan across all four evidence files found zero private-key, bearer-token, API-key/token assignment, or JWT matches; evidence explicitly omits raw logs, prompts, responses, headers, credentials, identifiers, and auth details
- No repeated inference occurred during Reopen 1; `reopen1_inference_requests_sent=0`
- Documentation closure is adequate; the evidence summary states no product documentation change is required and identifies PMA closure as the next step

### Targeted Validation Evidence
- `git diff --check` -> PASS with no output
- `for f in .staticeng/tasks/todo/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors.md .staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/SUMMARY.md .staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/logs/*.log; do git diff --no-index --check /dev/null "$f" >/dev/null || exit $?; done` -> PASS with no output
- Evidence-consistency script -> PASS for AC-1 through AC-6, NAS-to-Fedora propagation, no repeated Reopen 1 inference, and documentation closure after correcting a QA script block-counting issue
- Secret-pattern scan -> PASS; four files scanned and zero matches in all four sensitive-pattern classes

### Open Risks
- Historical backups, memories, and inactive model-pinned sessions retain the stale literal by design; manually resuming such a session may require selecting a current model
- QA did not independently query live hosts because the handoff prohibited inference/auth requests and runtime/config mutation; closure depends on the sanitized operational evidence supplied by the developer

## Reopen History

### Reopen 1 - 2026-07-16
- Post-task sync rejected closure because AC-1 remained blocked by Fedora's receive-only Syncthing restoration
- User instructed PMA to continue
- Approved resolution: update only the stale model override in the NAS authoritative OpenCode config, preserve unrelated configuration, and verify normal propagation to Fedora
- Reuse the original developer session and do not repeat completed ChatGPT or Qwen inference checks
