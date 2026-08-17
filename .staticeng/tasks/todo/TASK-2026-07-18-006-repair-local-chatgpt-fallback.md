---
id: TASK-2026-07-18-006-repair-local-chatgpt-fallback
complexity: standard
track: implementation
slice: foundation
status: done
scr: null
parent: TASK-2026-07-18-005-diagnose-local-chatgpt-fallback
assigned_to: developer
handoff_from: product_manager
reopened_count: 2
---

# Task: TASK-2026-07-18-006 - Repair Local ChatGPT Fallback

## Objective
Repair the NAS LiteLLM public GPT fallback chains so rate-limited traffic advances through account2, account3, then the default ChatGPT profile.

## Scope
- Update only DB-backed fallback entries for unqualified public GPT groups.
- Preserve profile-qualified groups as explicit account pins.
- Preserve retries, cooldowns, Redis, credentials, deployments, and unrelated fallbacks.
- Use supported LiteLLM admin APIs; do not edit DB, Redis, auth files, or source.

## Acceptance Criteria
- [x] AC-1: Every applicable unqualified public GPT group has account2, account3, and default exactly once in that order.
- [x] AC-2: Qualified `chatgpt/*` groups remain explicit profile pins without new cross-profile fallbacks.
- [x] AC-3: Existing deployments, credentials, retry/cooldown policy, and unrelated routing remain unchanged.
- [x] AC-4: Supported API readback and a non-inference router validation prove the corrected chain.
- [ ] AC-5: One bounded stateless Responses inference during the known rate-limit condition proves account advancement, without persisting prompt/response/auth content.
- [x] AC-6: Evidence packet contains `SUMMARY.md` and sanitized logs tracing all ACs; documentation impact is closed.

## Handoff
[Agent Message] From: product_manager To: developer

Repair only the unqualified GPT fallback chains using supported LiteLLM APIs. Use account2 -> account3 -> default order. Do not alter qualified profile groups, credentials, retries, cooldowns, Redis, deployments, source, or unrelated fallbacks. Back up sanitized routing state, validate readback, then send at most one new stateless no-retry Responses request to an already rate-limited public group to prove advancement. Never retain prompt, response, user, or auth content. Produce the required evidence packet and task updates; do not commit.

# Post Implementation Task Updates

## Developer

- Updated all eight applicable unqualified public GPT groups through `POST /fallback`; each chain is account2 -> account3 -> default exactly once
- Preserved qualified profile pins, all deployments and credentials, retry/cooldown and Redis settings, unrelated fallbacks, and unrelated source modifications
- Captured sanitized pre-change routing state and completed supported API readback plus non-inference `GET /fallback/{model}` validation
- Sent exactly one stateless `store=false`, `max_retries=0` Responses request to currently rate-limited public group `gpt-5.6-luna`; router logs proved account2/account3/default advancement, but the request ended HTTP 400 and did not reproduce a 429, so AC-5 is partial
- Retained no prompt, response, user, authorization, token, or raw log content
- Evidence: `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/SUMMARY.md`
- Documentation impact: closed; no product documentation change required

## Reopen History

### Reopen 1 - 2026-08-04

- Post-task sync rejected closure because the bounded probe used provider-invalid minimal input and returned HTTP 400, leaving AC-5 partial.
- The fallback configuration itself is retained; do not repeat API updates.
- Perform exactly one corrective stateless no-retry Responses request with a known-valid Codex-compatible body, preferably against a group with current rate-limit evidence.
- Prove either rate-limit-triggered advancement and success on a later account, or return the exact remaining provider/router blocker without further requests.

### Reopen 2 - 2026-08-04

- Reopen 1 again used a model rejected by the ChatGPT Codex provider (`gpt-5.3-codex`), so AC-5 remains partial.
- Do not send another inference until a read-only preflight identifies a model and exact body shape already proven HTTP 200 on this NAS/provider.
- Preflight must use existing sanitized success metadata, model inventory/capabilities, and provider tests/docs; it must not infer.
- Return the single best validated probe candidate and explain why the two prior probes returned HTTP 400.

#### Preflight Result

- Tech Lead identified `gpt-5.5` with structured Responses input as the only exact public model/body combination already proven HTTP 200 on multiple NAS ChatGPT profiles.
- No currently rate-limited public model has equivalent provider-valid proof, so another live request cannot simultaneously guarantee valid input and reproduce a current 429.
- Closure will use the supported API chain readback, observed three-profile router traversal, historical mapped 429 evidence, and explicit residual live-429 risk rather than spend another non-decisive request.

### Reopen 1 Developer Resolution - 2026-08-04

- Did not repeat any fallback API update
- Sent exactly one corrective stateless `store=false`, `max_retries=0` `/v1/responses` request using the Codex string-input shape covered by the ChatGPT Responses transformation tests
- Requested public group `gpt-5.3-codex`, selected from groups with current pre-request rate-limit evidence
- Sanitized router evidence proved traversal through account2, account3, and default; the final selected deployment correlated to default
- No 429 occurred in the corrective window. The exact remaining blocker is provider rejection: `gpt-5.3-codex` is not supported by the current ChatGPT account-backed Codex provider, producing HTTP 400 across the traversed accounts
- Sent no further request. AC-5 remains partial because traversal is proven but neither rate-limit-triggered success nor valid HTTP 200 was possible with the selected provider-rejected model
- Retained no prompt, response, user, authorization, token, or raw log content
- Evidence: `.staticeng/evidences/TASK-2026-07-18-006-repair-local-chatgpt-fallback/logs/reopen1-corrective-responses-sanitized.log`

## QA Engineer: Post Implementation Expectations

- Performed evidence-first review of this task, the parent diagnosis, `CLAUDE.md`, and the complete implementation evidence packet; sent no inference request and made no runtime, router, configuration, credential, authentication, Redis, deployment, or source mutation
- Repeated only read-only checks: LiteLLM health and readiness returned HTTP 200; live `GET /router/settings` returned 16 fallback rules and the preserved retry/cooldown policy; live `GET /fallback/{model}` returned HTTP 200 with the exact repaired chain for all eight applicable groups
- AC-1 PASS: each applicable unqualified public GPT group has exactly one account2 -> account3 -> default rule in live readback
- AC-2 PASS: live readback retains only the two pre-existing qualified `chatgpt/*` source rules shown by the sanitized baseline, with no account2/account3 target added
- AC-3 PASS: sanitized before/after evidence preserves 42 deployments, policy values, 16 total rules, qualified rules, and unrelated rules; the supported update log records no credential, deployment, Redis, or source edit
- AC-4 PASS: supported live API readback and non-inference fallback lookups independently reconfirm the repaired chains
- AC-5 PARTIAL, ACCEPTABLE WITH DISCLOSED RESIDUAL RISK: both bounded probes observed account2 -> account3 -> default traversal, but neither observed a live 429 because provider-invalid body/model combinations returned HTTP 400; historical sanitized NAS evidence independently records HTTP 429 as rate limit and `RouterRateLimitError`, while Tech Lead preflight found no currently rate-limited model with a NAS-proven provider-valid body. Do not spend another inference request. Residual risk is limited to the unobserved combination of a fresh live 429 triggering this repaired chain and succeeding on a later account
- AC-6 PASS: `SUMMARY.md` and five sanitized logs are present and trace the repair, readback, both probes, safety constraints, and documentation closure; no screenshots are applicable to this non-UI task
- Functional closure recommendation: accept AC-5 as partial with the disclosed residual risk; do not send another live probe because no validated candidate exists and another request would not provide decisive evidence under the current provider state
- Final workflow closure blocker: `staticeng_validate` fails on pre-existing repository-wide CodeMap gaps and broken `.staticeng/codemap.yml` links. The required repair dry-run proposes broad metadata changes outside this read-only/no-config-mutation handoff, so QA did not apply it. PMA should route that StaticEng repair separately, then rerun validation before final closure
- Documentation impact: no product or architecture documentation update is required; this task and its evidence packet are the operational record
