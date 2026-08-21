# Fedora GPT-5.6 Fallback Diagnosis

## Summary

Fresh live behavior contradicts the reported failure. During the authorized three-probe window, account2 completed directly, and both qualified account1 and unqualified `gpt-5.6-sol` completed through the account2 deployment. The account1 deployment remains quota-limited, but the router advanced to account2 instead of returning the primary error

The current `gpt-5.6-sol` route is therefore healthy. The configuration defect is narrower and affects consistency across equivalent public aliases: `gpt-5.6-luna` has no general fallback rule, while the other public aliases route either to qualified account1 or directly to account2. This does not explain a fresh Sol failure because Sol currently has a direct account2 fallback and proved it live

## Work Performed

- Read the live Fedora model inventory and router settings through authenticated localhost admin endpoints, sanitizing deployment IDs and auth-profile values
- Confirmed the service remained healthy and made no runtime, file, database, credential, container, source, client, or cooldown mutation
- Sent exactly three authorized stateless no-retry Responses probes with one provider-valid Codex-compatible request shape
- Retained only HTTP status, selected sanitized model group, completion count, and error class; no prompts, responses, identities, account IDs, credentials, or raw configuration values were retained
- Inspected the bounded container-log window; no authentication, request-shape, or routing error was emitted

## Root Cause And Minimal Repair

The originally reported Sol failure is not reproducible in current live state. Missing Sol fallback, router exception classification, request shape, account2 deployment health, and current cooldown behavior are excluded by the successful public traversal. The most precise disposition is a transient or stale observation before the current routing state, not a current Sol defect

For policy consistency, the minimal supported repair is configuration-only: define every public ChatGPT alias as account1-primary and account2-secondary in one explicit general-fallback rule per alias. Do not change router exception handling, deployments, credentials, retries, or cooldowns. The equivalent public aliases inspected were `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, `gpt-5.6-sol`, and `gpt-5.6-terra`; `gpt-5.6-luna` is the only one missing a public general-fallback rule in live readback

## Acceptance Criteria Coverage

- **AC-1: PASS**. Live deployments and all general fallback rules were read back with deployment IDs hashed and profile values reduced to `default` or `non-default`; see `.staticeng/evidences/TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback/logs/01-live-routing-readback.md`
- **AC-2: PASS WITH FRESH CONTRADICTION**. Account2 returned HTTP 200 with one completion. Qualified account1 and public Sol also returned HTTP 200 with one completion through account2. Current logs and selection prove account1 quota disposition followed by successful fallback rather than failure to advance; see `.staticeng/evidences/TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback/logs/02-probes-and-logs.md`
- **AC-3: PASS**. Current Sol fallback configuration, exception handling, provider-valid request shape, cooldown traversal, and account2 health all worked. The historical failure is not currently reproducible and cannot be narrowed beyond transient or stale state without violating the three-probe bound
- **AC-4: PASS**. No Sol runtime repair is currently justified. The minimal consistency repair is one explicit account1-primary/account2-secondary rule for each public alias; live `gpt-5.6-luna` is the only equivalent public alias missing a rule
- **AC-5: PASS**. This packet contains a sanitized summary and bounded logs tracing every acceptance criterion

## Documentation Impact

No product, architecture, technical, or CodeMap update is required because this investigation changed no steady-state behavior

## Open Risks

- Deployment-selection headers expose only the terminal selected deployment, so the account1 quota event is inferred from the known current quota disposition plus account2 terminal selection, consistent with immediately preceding retained evidence
- The three-probe limit is exhausted; no further request should be sent under this task
- Public alias fallback definitions remain structurally inconsistent until a separately authorized repair task changes them

## Recommended Next Step

PMA should close the reported Sol incident as currently non-reproducible. If uniform alias policy is required, authorize a separate configuration task to normalize the six public aliases, with special attention to the missing `gpt-5.6-luna` rule
