---
id: TASK-2026-08-19-029-deploy-fedora-final-stream-safe-198
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-010-design-stream-safe-198-release
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-029 - Deploy Fedora Final Stream-Safe 1.98.0

## Objective
Restore Fedora to the same verified immutable 1.98.0 candidate now running on NAS and execute the already-proven corrected functional/preservation gates.

## Safety
- NAS must remain healthy and unchanged on the candidate; stable remains held.
- Re-capture Fedora baseline/rollback and recreate only LiteLLM by digest with `--no-deps`.
- Preserve Fedora two-account topology, database, credentials, dependencies, clients, and unrelated services.
- Use corrected Codex payload including `reasoning.context=all_turns`.
- Qualified regular may return documented provider quota HTTP 429; direct account2 and public fallback must complete HTTP 200 SSE.
- Roll back Fedora on any non-quota, health, preservation, LazyMCP, observation, or log failure.

## Acceptance Criteria
- [ ] AC-1: Fresh Fedora baseline and rollback readiness match prior preserved state.
- [ ] AC-2: Fedora runs the exact candidate manifest/config/version/revision with only LiteLLM recreated.
- [ ] AC-3: Health/readiness/liveliness, restart/OOM, 10-minute observation, and clean-log gates pass.
- [ ] AC-4: Exact 27-model/two-account topology, fallbacks/isolation, protected hashes, credentials metadata, dependencies, and unrelated services are preserved.
- [ ] AC-5: Native stream=false passes; qualified regular returns only documented quota 429; direct account2 and public fallback complete valid HTTP 200 SSE with correct profile selection and no stream/auth/device errors.
- [ ] AC-6: LazyMCP status/describe/tool-list and harmless tool smoke pass.
- [ ] AC-7: NAS remains healthy and unchanged on the same candidate; stable remains held.
- [ ] AC-8: Evidence packet approves/rejects cross-host QA and stable promotion.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-029-deploy-fedora-final-stream-safe-198/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Deploy Fedora by the exact candidate digest using all corrected, previously proven gates. Preserve NAS and stable. Complete full functional, LazyMCP, observation, and preservation validation. Roll back only on genuine failure. Do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1 through AC-8 passed.
- Fedora runs the same immutable 1.98.0 candidate as NAS with zero restarts/OOM.
- Corrected Codex SSE, public account2 fallback, LazyMCP, exact topology/preservation, clean logs, and ten-minute observation passed.
- Default profile remains provider-quota-bound; account2 fallback provides public availability.
- Stable remains held pending independent cross-host QA.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1 through AC-8 passed and complete evidence is under `.staticeng/evidences/TASK-2026-08-19-029-deploy-fedora-final-stream-safe-198/`
- Fedora runs the exact immutable candidate manifest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, LiteLLM 1.98.0, revision `b0dfe2e7a7`
- Only `LITELLM_IMAGE` changed and only LiteLLM was recreated with `--no-deps`; dependencies and 47-service runtime scope remain preserved
- Native `stream=false`, qualified regular through configured quota fallback, direct account2, and public fallback completed valid HTTP 200 SSE with correct account2 selection and no stream/auth/device/payload/model errors
- LazyMCP status, exact three-tool list, Fedora `defend_memory-find` describe, and harmless tool smoke passed
- Exact 27-model, 24-rule, two-account topology, protected hashes, credential metadata, dependencies, mounts, networks, health, and ten-minute observation passed
- Concrete release-blocking log categories are zero; two disclosed generic tracebacks are non-blocking success-telemetry callback errors after successful requests
- NAS remained exact and healthy on the same candidate; stable remained held at its inherited digest
- Cross-host QA is approved by developer evidence; stable promotion remains a separate QA/Tech Lead decision
- No product, architecture, technical, or CodeMap update is required and no commit was created
