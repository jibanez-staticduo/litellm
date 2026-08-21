---
id: TASK-2026-08-19-051-implement-fedora-chatgpt-alias-fallbacks
complexity: standard
track: implementation
slice: logic
status: done
scr: SCR-2026-08-19-001-fedora-chatgpt-alias-fallbacks
parent: TASK-2026-08-19-050-spec-fedora-chatgpt-alias-fallbacks
assigned_to: developer
handoff_from: product_manager
reopened_count: 2
---

# Task: TASK-2026-08-19-051 - Implement Fedora ChatGPT Alias Fallbacks

## Objective
Normalize Fedora's six unqualified ChatGPT aliases so each uses account1 first and the matching account2 route when account1 fails or rate-limits, while preserving both qualified account routes as explicit, unchanged identities.

## Exact Scope
- Fedora LiteLLM persistent routing configuration only
- Exactly these six unqualified aliases:
  - `gpt-5.4`
  - `gpt-5.4-mini`
  - `gpt-5.5`
  - `gpt-5.6-luna`
  - `gpt-5.6-sol`
  - `gpt-5.6-terra`
- For each alias, account1 is the primary route and its matching account2 route is the fallback
- In one narrowly bounded Fedora database transaction, clear only `chatgpt_auth_profile` on the five identified unqualified public deployment records for `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, and `gpt-5.6-terra`
- Preserve `gpt-5.6-sol` unchanged because its public deployment already expresses account1 through an absent profile field
- Only after the database repair and assertions pass, issue exactly six supported fallback admin API writes, one for each in-scope public alias
- Preserve `chatgpt/<model>` as the explicit account1 route and `chatgpt-account2/<model>` as the explicit account2 route
- Correct the missing public `gpt-5.6-luna` fallback definition and normalize the other five definitions to the same policy

## Preconditions
- Read SCR-2026-08-19-001 and TASK-049's task file and complete evidence packet before mutation
- Capture a sanitized protected backup of the exact persistent routing settings that may change
- Read back current persistent and live routing state for all six aliases and their twelve qualified account routes
- Reconfirm the protected identity of exactly the five target public records and derive exact-row predicates that bind each expected record identity, public alias, and current non-null `chatgpt_auth_profile` state
- Compute protected pre-transaction fingerprints for all target rows, all non-target fields on those rows, `gpt-5.6-sol`, all twelve qualified deployments, and the broader deployment inventory required to prove preservation
- Prepare owner-only rollback SQL and exact protected before-data that can restore only the five target `chatgpt_auth_profile` values
- If the guarantee requires changing any field except the five target `chatgpt_auth_profile` values and the six public fallback definitions, or requires adding, removing, renaming, or repurposing a deployment, stop before mutation and escalate the conflict to PMA

## Safety And Preservation
- Do not expose or retain credentials, auth-profile values, identities, account IDs, raw deployment IDs, prompts, or response content
- Do not trigger login or device authentication
- Do not add, remove, rename, or repurpose model deployments
- The only permitted deployment mutation is one direct Fedora database transaction that clears `chatgpt_auth_profile` on exactly the five identified public records; do not mutate `gpt-5.6-sol`, the twelve qualified deployment/profile associations, or any other field or record
- Do not change credentials, auth-profile contents, auth files, retries, cooldowns, routing strategy, source code, image, containers, clients, or unrelated fallback rules
- Do not touch NAS or any non-Fedora environment
- Direct database access is authorized only for the five-field-clear transaction because TASK-051 Reopen 1 verified both supported admin APIs cannot clear a stored non-null association. Use supported admin APIs for all six fallback writes
- Use exact-row predicates and pre/post assertions inside the transaction. Roll back without fallback writes if the expected target count is not exactly five, any target identity or before-value differs, the updated count is not exactly five, any target field is not cleared, or any protected non-target fingerprint changes
- Do not build, deploy, or change source or image. Do not reload or restart unless strictly required for the supported fallback settings or verified live-state refresh
- Bound verification to stateless `store=false`, client-no-retry Responses probes using the same provider-valid request shape; do not induce failures through configuration or credential mutation

## Rollback
- Preserve owner-only rollback SQL plus exact protected before-data for the five target `chatgpt_auth_profile` values, and a secret-safe snapshot of all six public fallback definitions and ordering
- Keep database rollback material protected and outside sanitized evidence; sanitized evidence may record only its path, ownership/mode, integrity fingerprint, and successful restore-readiness check
- On any in-transaction count, identity, value, or fingerprint mismatch, roll back the transaction and issue zero fallback writes
- If post-commit database validation fails, transactionally restore only the five original field values using exact-row predicates and assertions. If a fallback write or later validation fails, use supported admin APIs to restore only changed fallback settings and restore the five database values when needed to return to the complete before-state
- Do not roll back by changing qualified deployments, auth-profile contents, credentials, source, image, retries, cooldowns, or unrelated settings
- Record whether rollback was required and the final persistent/live state in the evidence packet

## Acceptance Criteria
- [x] AC-1: Persistent and live Fedora readback show all six in-scope public deployments express account1 through an absent `chatgpt_auth_profile` field and have one consistent matching-account2 fallback policy, including a defined rule for `gpt-5.6-luna`.
- [x] AC-2: Readback proves all twelve qualified routes retain their explicit identities: `chatgpt/<model>` identifies account1 and `chatgpt-account2/<model>` identifies account2 for each in-scope model.
- [x] AC-3: Transaction assertions and before/after fingerprints prove only `chatgpt_auth_profile` on the five exact target public records and the six public fallback definitions changed; `gpt-5.6-sol`, every other field, all twelve qualified associations, model inventory, auth-profile contents, credentials, retries, cooldowns, routing strategy, unrelated fallback rules, source, image, containers, clients, and non-Fedora state are unchanged.
- [x] AC-4: Bounded stateless no-retry verification, correlated with sanitized routing logs, proves an in-scope unqualified request attempts account1 and advances to matching account2 when account1 rate-limits or otherwise fails, without induced failure mutation.
- [x] AC-5: No reload or restart occurs unless strictly required; if one is required, evidence states why and proves exact persistent/live equality for all six rules plus passing Fedora health/readiness afterward.
- [x] AC-6: Owner-only rollback SQL/data is sufficient to transactionally restore only the five original field values, supported-API rollback material restores only the six fallback definitions, and evidence records rollback execution or confirms it was not required.
- [x] AC-7: A sanitized evidence packet exists at `.staticeng/evidences/TASK-2026-08-19-051-implement-fedora-chatgpt-alias-fallbacks/` with `SUMMARY.md` and `logs/`, tracing AC-1 through AC-6 and recording commands, bounded probe count, safety, preservation, and final state.
- [x] AC-8: The task file contains `# Post Implementation Task Updates` and `## Developer: Post Implementation Expectations`, and documentation impact is explicitly closed.

## Required Evidence Packet
- `SUMMARY.md` using the shared output contract: Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step
- `logs/01-preflight-and-backup.md`: sanitized persistent/live baseline, six public associations, exact six-alias inventory, twelve qualified routes, protected-backup metadata, and precondition decision
- `logs/02-routing-change-and-readback.md`: sanitized transaction predicates and pre/post assertion outcomes, exact affected-row counts, protected fingerprints, six supported fallback API writes, before/after public associations and fallback definitions, preservation comparison, and reload/restart disposition
- `logs/03-bounded-fallback-verification.md`: probe count, stateless/no-retry controls, status and error class, sanitized account1 then account2 routing correlation, and no retained content
- `logs/04-rollback-and-validation.md`: health/readiness, persistent/live equality, rollback disposition, secret-safety review, and StaticEng validation result
- No raw API payloads, authorization material, deployment IDs, profile values, prompts, responses, or unrelated logs

## Handoff
[Agent Message] From: product_manager To: developer

Do not implement until PMA dispatches Reopen 2. On dispatch, use one asserted Fedora database transaction to clear only `chatgpt_auth_profile` on the five exact public records for `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, and `gpt-5.6-terra`; preserve public `gpt-5.6-sol` unchanged. Require exact-row predicates, exact count and fingerprint assertions, protected owner-only rollback SQL/data, and immediate rollback on any mismatch. Only after the transaction passes, perform exactly six supported fallback admin API writes. Preserve all qualified deployments and every other field and setting. Do not change source or image, and do not reload or restart unless strictly required. Complete bounded secret-safe verification and evidence, and do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

### Summary

- Stopped before mutation because fallback-only configuration cannot guarantee account1-first ordering for five of the six public aliases
- Fresh readback shows those five public deployments use account2 identity; only `gpt-5.6-sol` uses account1 identity
- Changing the public deployments or auth-profile association would be required to guarantee the approved first attempt, but both are explicitly prohibited

### Work Performed

- Read the SCR, this task, TASK-049 task file, and complete TASK-049 evidence packet
- Captured persistent and live six-alias routing state, all twelve qualified identities, health, image, restart count, inventory, and preservation fingerprints
- Created exact owner-only rollback material before the precondition decision
- Made zero `POST /fallback` writes, zero deployment/profile changes, zero reloads/restarts, and zero inference probes

### Acceptance Criteria Coverage

- AC-1: BLOCKED; no uniform six-rule state was written because it could not guarantee account1-first order within scope
- AC-2: PASS; all twelve qualified routes preserve distinct account1/account2 identities
- AC-3: PASS; no runtime, persistent, source, deployment, credential, policy, client, container, NAS, or non-Fedora mutation occurred
- AC-4: BLOCKED BY PRECONDITION; no post-change probe was appropriate because no valid change could be applied
- AC-5: NOT APPLICABLE; no reload or restart occurred, and Fedora remained healthy with zero restarts
- AC-6: PASS; protected exact rollback material exists and rollback was not required
- AC-7: PASS; complete sanitized evidence exists under `.staticeng/evidences/TASK-2026-08-19-051-implement-fedora-chatgpt-alias-fallbacks/`
- AC-8: PASS; this section records closure and documentation impact

### Documentation Impact

No product, architecture, technical, or CodeMap update is required because steady-state behavior and repository source did not change. The evidence packet is the durable blocked-implementation record

### Open Risks

- Five public aliases remain account2-first by deployment identity, and public `gpt-5.6-luna` remains without a general fallback rule
- Repository-wide StaticEng validation retains pre-existing broken links and missing CodeMaps; no task-specific validation defect was reported

### Recommended Next Step

PMA should request a revised SCR authorizing the minimum public deployment/profile correction or revise the requested ordering. Fallback-only mutation must not proceed under the current preservation constraints

## Reopen History

### Reopen 1 - 2026-08-19

- Reason: TASK-051 established that five public aliases are account2-backed, so fallback-only settings cannot satisfy the approved account1-first behavior
- Authorization: the user approved the minimum Fedora-only reassociation of the six public deployments with existing matching account1 auth profiles while preserving all twelve qualified associations and all other protected state
- Scope effect: supported admin API reassociation is now permitted only for the six public deployment/profile associations; direct database edits and broader deployment, auth-profile, or credential changes remain prohibited
- State: dispatched; execution stopped before mutation because the deployed supported model-update APIs cannot clear a stored non-null `chatgpt_auth_profile` to the existing absent-field account1 association

### Reopen 1 Developer Execution

- Revalidated that five public aliases store the account2 association, while `gpt-5.6-sol` and every account1 qualified route express account1 through an absent profile field
- Inspected both supported model-update API contracts and deployed merge behavior. Explicit null and omission both preserve a stored non-null profile; null clearing is limited to unrelated pricing fields
- Created owner-only six-association rollback material alongside the existing exact fallback snapshot
- Made zero association or fallback writes, zero qualified-route changes, zero reloads/restarts, and zero probes
- AC-1 and AC-4 remain blocked by the supported API limitation; AC-2, AC-3, AC-6, AC-7, and AC-8 pass; AC-5 is not applicable
- Documentation impact: no steady-state product, architecture, technical, or CodeMap change occurred
- Recommended next step: separately authorize a minimal source change adding explicit-null clear semantics for `chatgpt_auth_profile`, then deploy it and resume this task; alternatively authorize a narrowly bounded transactional database repair

### Reopen 2 - 2026-08-19

- Reason: Reopen 1 proved both supported deployed model-update APIs merge only non-null values and cannot clear the five stored public `chatgpt_auth_profile` associations
- Authorization: the user explicitly said `hazlo`, approving direct database repair as the verified last resort for the already approved account1-primary/account2-fallback policy
- Scope effect: one asserted transaction may clear only `chatgpt_auth_profile` on the five exact unqualified public records, followed by exactly six supported fallback API writes; all qualified deployments, all other fields, source, image, and unrelated LazyMCP work remain protected
- Safety effect: exact-row predicates, pre/post count and fingerprint assertions, protected rollback SQL/data, and rollback on any mismatch are mandatory
- State: implemented; awaiting independent QA and PMA closure

### Reopen 2 Developer Execution

- Created protected exact-value five-row rollback SQL before mutation
- Executed one asserted transaction that cleared only the five authorized public `chatgpt_auth_profile` fields; exact target/update counts were five, protected non-target fingerprint and 27-row inventory were unchanged, public Sol and all qualified associations were preserved
- Issued exactly six supported fallback API writes, all HTTP 200, establishing matching account2 targets for every in-scope public alias including Luna
- Persistent and live readback agree: six account1-associated public aliases, six exact account2 fallback rules, six qualified account1 routes, and six qualified account2 routes
- Sent exactly one stateless no-retry public Sol probe; HTTP 200 terminated on matching account2 with no failed/error event and no retained content
- No reload/restart was required; readiness/liveliness are HTTP 200, container healthy, restart count zero, image and router policy unchanged
- Rollback was not required. Exact database and fallback rollback material remains owner-protected on Fedora
- AC-1 through AC-8 pass. StaticEng validation retains only pre-existing repository-wide CodeMap defects
- Documentation impact: no product, architecture, technical, or CodeMap update is required; SCR, task, and evidence are the durable operational record
- Recommended next step: independent QA, then PMA closure

## Business Analyst Review Notes

- The amended SCR and task now resolve the prior precondition conflict without broadening the six-alias Fedora scope
- Revised AC-1, AC-3, and AC-6 make the authorized association change, preservation boundary, and rollback path observable and testable
- The prior Developer post-implementation record remains intact as evidence of the blocked first attempt
- Reopen 2 resolves the supported-API limitation through a single explicit last-resort exception without weakening the preservation boundary
- Revised preconditions, rollback rules, AC-1, AC-3, AC-5, AC-6, evidence requirements, and developer handoff make the five-row transaction and six supported fallback writes independently testable
- The task remains atomic, Fedora-only, and ready for PMA dispatch; unrelated LazyMCP records and work are unchanged

## QA Engineer: Post Implementation Expectations

### Summary

- Independent post-task QA passed all acceptance criteria using read-only, sanitized Fedora inspection and evidence audit
- No additional provider probe was needed because the implementation packet already contains the single bounded account2 traversal probe and fresh structural readback remained conclusive

### Work Performed

- Read the approved SCR, task history, implementation summary, and all four implementation logs
- Read back persistent database associations and live model inventory for the six public and twelve qualified routes
- Read back all six general fallbacks and protected router policy, then checked health, image identity, restart count, inventory count, and rollback permissions and hashes
- Performed no Fedora write, reload, restart, credential access, content inspection, or inference request

### Acceptance Criteria Coverage

- AC-1: PASS; integration readback shows six public absent-profile account1 associations and six exact live matching account2 general fallbacks, including Luna
- AC-2: PASS; integration readback shows six qualified account1 absent-profile routes and six qualified account2 profile-associated routes, matching the unchanged implementation readback
- AC-3: PASS; evidence audit verifies the asserted five-field transaction and before/after protected fingerprint, while independent readback confirms inventory 27, unchanged image, zero restarts, and preserved router policy
- AC-4: PASS; evidence audit confirms one stateless `store=false`, client-no-retry public Sol probe terminated successfully on matching account2 under natural account1 quota disposition; current structural readback independently confirms account1 primary and the sole account2 fallback
- AC-5: PASS; manual and integration checks show readiness/liveliness HTTP 200, healthy container, restart count zero, and no reload/restart requirement
- AC-6: PASS; manual filesystem verification shows rollback directory mode `0700`, both rollback files mode `0600`, expected ownership, and SHA-256 values matching preflight evidence; rollback was not required
- AC-7: PASS; evidence packet contains `SUMMARY.md`, the four required implementation logs, and the sanitized independent QA log
- AC-8: PASS; Developer and QA Engineer post-implementation sections exist and documentation impact is explicitly closed

### Documentation Impact

No product, architecture, technical, or CodeMap update is required because QA introduced no source or structure change. This task section and the QA evidence log close the verification record

### Open Risks

- Attempt-by-attempt provider logs remain unavailable; AC-4 relies on exact structural routing state plus the already bounded terminal account2 correlation, as disclosed in implementation evidence
- Repository-wide StaticEng validation has pre-existing CodeMap defects unrelated to TASK-051

### Recommended Next Step

PMA should close TASK-051. No further provider probe or Fedora mutation is warranted

## Business Analyst Closure Review

- Independent QA passed AC-1 through AC-8 and confirmed the approved six-alias policy is implemented
- All Reopen History, implementation notes, QA notes, preservation findings, and residual-risk disclosures remain part of the closure record
- Product documentation impact is closed through the implemented SCR, task history, and evidence packet; no additional steady-state documentation update is required
