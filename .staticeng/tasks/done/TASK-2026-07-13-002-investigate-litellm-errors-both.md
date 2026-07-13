---
id: TASK-2026-07-13-002-investigate-litellm-errors-both
complexity: standard
track: investigation
slice: qa
status: done
scr: null
parent: null
assigned_to: qa_engineer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-13-002 - Investigate LiteLLM Errors on NAS and Fedora

## Classification
- **complexity:** standard
- **track:** investigation
- **slice:** qa

## Objective
Analyze recent LiteLLM errors on local/NAS and Fedora, quantify dominant error classes, identify affected models/routes and root causes, and determine whether `gpt-5.6-sol` is currently operational.

## Scope
- Read recent container logs and sanitized spend/error metadata on both instances.
- Compare error rates/classes over a bounded recent window.
- Identify routing/fallback behavior, rate limits, auth errors, provider errors, code exceptions, health issues, and client disconnects.
- Check current image/status/health and minimally smoke regular/account2 Sol where safe.
- Do not expose prompts, responses, users, IPs, keys, tokens, headers, account IDs, auth files, device codes, DB URLs, or session IDs.
- Do not modify config/code/models/credentials or restart services.
- Investigation comes first. After root cause is confirmed, PMA will create implementation/release tasks.
- If a code fix/new image is required, first update the fork from current `upstream/main` using the established replay/rebase strategy that preserves upstream history, then implement/reconcile the fix, test, build, and deploy both instances.

## Acceptance Criteria
- [x] AC-1: NAS recent errors are categorized and counted.
- [x] AC-2: Fedora recent errors are categorized and counted.
- [x] AC-3: Dominant root causes and affected models are identified.
- [x] AC-4: Current status of regular/account2 GPT-5.6 Sol is reported for each applicable instance.
- [x] AC-5: Recommendations distinguish transient provider/client errors from actionable LiteLLM/config/code issues.
- [x] AC-6: Evidence is secret-safe.

## Handoff
[Agent Message] From: product_manager To: qa_engineer

Investigate recent NAS and Fedora LiteLLM errors read-only. Use bounded logs and sanitized spend/error fields. Categorize/count errors, identify affected models and routing/fallback outcomes, and run at most one harmless smoke per relevant Sol model if needed. Never persist prompts/responses/secrets/identities. Do not change or restart anything.

## Release Decision Extension
[Agent Message] From: product_manager To: qa_engineer

The user requires fixing the confirmed errors. If fixes require a new image, PMA will first sync/replay the fork onto current upstream main, then implement and deploy. Your investigation must identify whether each dominant error is transient, config/DB, or code/image, and list exact upstream/code areas likely affected.

# Investigation Findings

## Root Causes
- Local/NAS: provider availability/quota pressure caused 429/503/507 responses; retries/fallbacks multiplied log volume but no loop or profile leak was found.
- Fedora: invalid/unavailable requested model names caused all 19 HTTP 400 responses.
- Additional noise: NAS LazyMCP 500/discovery 404 and Fedora MCP upstream auth/cancellation patterns require targeted client/config attribution.
- No DB, Redis/cache, router-profile, Responses parsing, restart, OOM, or current Sol outage was found.

## Current Sol Status
- Regular and account2 Sol returned HTTP 200 on both instances, one request each, without device auth.

## PMA Decision
- No emergency upstream sync/image release is justified yet.
- Follow-up operational/config investigation must identify invalid model names, MCP callers, 507 class, and safe retry/cooldown tuning. If a reproducible code defect remains, sync/replay onto `upstream/main` before implementation/release.
