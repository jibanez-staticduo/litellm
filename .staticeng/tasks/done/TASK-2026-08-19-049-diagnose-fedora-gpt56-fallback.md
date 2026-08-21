---
id: TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback
complexity: standard
track: investigation
slice: logic
status: done
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-049 - Diagnose Fedora GPT-5.6 fallback

## Objective
Determine why Fedora's unqualified `gpt-5.6-sol` route returns the account1 quota failure instead of falling back to the working account2 route.

## Product Intent
- `chatgpt/gpt-5.6-sol` explicitly targets account1.
- `chatgpt-account2/gpt-5.6-sol` explicitly targets account2.
- Unqualified `gpt-5.6-sol` uses account1 first and account2 when account1 fails, including provider rate limit.
- Equivalent unqualified ChatGPT model aliases should follow the same account1-primary/account2-fallback policy.

## Safety And Existing State
- Investigation is read-only over `ssh fedora`; do not change routing, cooldowns, credentials, deployments, source, containers, or clients.
- Do not trigger login or expose secrets, prompts, responses, identities, account IDs, or raw auth/config values.
- At most three bounded stateless `store=false`, no-retry Responses probes are authorized: qualified account1, qualified account2, and unqualified `gpt-5.6-sol`. Use the same provider-valid request shape and retain only sanitized status/routing/error-class evidence.
- Preserve unrelated active StaticEng tasks and existing runtime state.

## Acceptance Criteria
- [x] AC-1: Read back the live Fedora model deployments and general fallback rules for all unqualified ChatGPT aliases, with IDs and secrets sanitized.
- [x] AC-2: Confirm with logs and bounded probes that qualified account1 rate-limits, qualified account2 works, and unqualified `gpt-5.6-sol` fails to advance, or document fresh contradictory behavior.
- [x] AC-3: Identify the narrowest root cause, including whether the issue is missing/wrong fallback configuration, router exception classification, cooldown behavior, request shape, or deployment health.
- [x] AC-4: Define the minimal supported repair for `gpt-5.6-sol` and identify every equivalent alias affected by the same defect.
- [x] AC-5: Produce a sanitized evidence packet under `.staticeng/evidences/TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback/` with `SUMMARY.md` and logs, tracing all ACs.

## Handoff
[Agent Message] From: product_manager To: developer

Perform the bounded read-only Fedora diagnosis. Read live state before probes. Use the exact same valid Codex-compatible body for the three probes and correlate deployment selection from logs. Stop after proving the fault boundary. Do not repair or commit. Return the shared output contract with numbered AC evidence.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1: Read back the healthy live Fedora service, six public ChatGPT aliases, their qualified default/account2 deployments, and general fallback rules with secrets removed and deployment IDs represented only by hashes.
- AC-2: Used exactly three provider-valid, stateless, no-retry probes. Direct account2, qualified account1, and public `gpt-5.6-sol` all returned HTTP 200 with one completion; the latter two terminated on account2, contradicting the reported failure to advance.
- AC-3: Excluded current Sol fallback configuration, exception classification, request shape, cooldown traversal, and account2 health as causes. The historical symptom is not currently reproducible and is most narrowly classified as transient or stale state.
- AC-4: No current Sol repair is justified. A separate minimal configuration repair may normalize all six public aliases to explicit account1-primary/account2-secondary rules; `gpt-5.6-luna` is the only inspected public alias with no live general fallback rule.
- AC-5: Produced sanitized evidence in `.staticeng/evidences/TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback/`, including `SUMMARY.md` and two bounded logs.
- Safety: Made no runtime, config, source, database, credential, deployment, cooldown, container, or client mutation. Sent no more than the three authorized probes and retained no content or secret values.
- Recommended next action: PMA should close the Sol incident as currently non-reproducible or authorize a separate configuration task to normalize public alias policy.

## Business Analyst Closure Review

- The investigation is complete with all five acceptance criteria satisfied
- The fresh contradiction is preserved: the reported Sol failure was not reproducible, while the investigation identified inconsistent equivalent-alias configuration and the missing Luna fallback rule
- TASK-051 subsequently implemented and independently verified the separately authorized six-alias normalization policy
