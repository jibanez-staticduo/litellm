---
id: TASK-2026-08-27-003-verify-spark-provider-model
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-08-26-002-client-model-contracts-020
parent: TASK-2026-08-26-019-retire-obsolete-model-routes
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-27-003 - Verify Spark Provider Model

## Objective
Determine whether GPT-5.3 Codex Spark remains a valid upstream model for the current ChatGPT/Codex provider and, if so, identify the exact supported provider model identifier without mutating routes or accounts.

## Acceptance Criteria
- [x] AC-1: Compare current official OpenAI/Codex model documentation, current Codex 0.149.1 model catalog/cache, LiteLLM ChatGPT provider mapping, and live route records.
- [x] AC-2: Determine whether the provider-level `model` rejection means retirement, stale alias spelling, profile entitlement, or transformation error.
- [x] AC-3: If a supported exact identifier is discoverable without mutation, prove it with one safe direct/provider status-only request outside router fallback and no retained content.
- [x] AC-4: Recommend either a separate route-correction SCR/task or an approved scope change retiring Spark too; do not modify production.
- [x] AC-5: Define the exact safe unblock condition for Task 019.

## Expected Evidence
- Signed read-only handoff with official URLs, redacted catalog/model identifiers, and no credentials/prompts/responses.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

- The exact upstream identifier remains `gpt-5.3-codex-spark`; official documentation identifies it as a ChatGPT Pro-only research preview and not an API model
- The provider-level rejection is caused by the Codex Responses Lite transport selected by the local custom catalog, not by an identifier rename; entitlement remains an independent deployment prerequisite
- One direct standard Codex-backend request bypassed router fallback and returned HTTP 400 without a retained body, so functional support on a currently registered profile was not proven
- Recommend a new SCR/task to correct Spark client metadata and validate entitlement, with retirement as the fallback if no registered profile passes the direct standard-backend gate
- Evidence: `.staticeng/evidences/TASK-2026-08-27-003-verify-spark-provider-model/`
