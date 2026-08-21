---
id: SCR-2026-08-19-001-fedora-chatgpt-alias-fallbacks
status: implemented
requested_by: user
approved_by: user
date: 2026-08-19
---

# SCR: Fedora ChatGPT Alias Fallbacks

## Requested Behavior
Every in-scope unqualified Fedora ChatGPT model alias must route to account1 as its primary account and advance to the matching account2 route when account1 fails, including provider rate limiting.

Qualified account routes remain explicit: `chatgpt/<model>` continues to identify account1 and `chatgpt-account2/<model>` continues to identify account2. This change must not repurpose, rename, or remove either qualified route.

## Exact Scope
- Fedora LiteLLM persistent routing configuration only
- The six unqualified aliases established by TASK-049 live readback:
  - `gpt-5.4`
  - `gpt-5.4-mini`
  - `gpt-5.5`
  - `gpt-5.6-luna`
  - `gpt-5.6-sol`
  - `gpt-5.6-terra`
- One consistent account1-primary, account2-fallback policy for each alias
- A narrowly bounded transactional Fedora database repair that clears only `chatgpt_auth_profile` on the five identified unqualified public deployment records that currently select account2; `gpt-5.6-sol`, which already expresses account1 through an absent profile field, must remain unchanged
- After the database repair passes all post-transaction assertions, exactly six supported fallback admin API writes establish the matching account2 fallback for each in-scope alias
- Exact persistent and live readback after repair, including the previously missing public `gpt-5.6-luna` fallback rule

## Exclusions And Preservation
- Do not change qualified account-route identity or behavior beyond preserving the existing account1-to-account2 fallback policy
- Do not add, remove, rename, or repurpose model deployments
- Do not change credentials or auth-profile contents. This amendment permits one direct database exception only because both deployed supported model-update APIs were verified to merge non-null values and cannot clear `chatgpt_auth_profile`
- The database exception may clear only `chatgpt_auth_profile` on the identified public records for `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, and `gpt-5.6-terra`; it must use exact-row predicates and must not alter `gpt-5.6-sol` or any other field or record
- Do not change the twelve qualified deployment/profile associations, retries, cooldowns, routing strategy, source code, container image, containers, clients, or unrelated fallback rules
- Do not trigger device authentication or retain secrets, identities, account IDs, prompts, or response content
- NAS and all non-Fedora environments are out of scope

## Acceptance Intent
- A request to any of the six unqualified aliases selects the matching account1 route before account2
- An account1 failure eligible for general fallback, including rate limiting, advances to the matching account2 route
- Direct requests to either qualified route retain their explicit account identity
- Before/after readback proves that only the necessary public deployment/profile associations and the six public fallback definitions changed
- Live state and persistent state expose the same six exact public fallback definitions after reload or restart
- Verification uses bounded stateless, no-retry probes and does not induce failure by mutating credentials, auth-profile contents, retries, cooldowns, or source
- Before mutation, preserve owner-only rollback SQL and the exact protected before-data needed to restore only the five target values
- Execute the five-row repair in one transaction with pre- and post-update count, identity, and non-target-field fingerprint assertions. Roll back immediately on any row-count or fingerprint mismatch
- Do not change source or image and do not reload or restart unless the persistent-settings mechanism or verified live-state behavior strictly requires it

## Approval
Product-owner approval was given directly by the user on 2026-08-19 and relayed in the signed PMA handoff for TASK-050. The approved policy applies to every unqualified Fedora ChatGPT alias in the exact six-alias scope above.

On 2026-08-19, after TASK-051 proved that five public aliases were account2-backed and fallback-only settings could not establish account1-first behavior, the user explicitly authorized the minimum Fedora-only public deployment/auth-profile reassociation needed to implement this policy. This amendment does not authorize auth-profile content changes, credential changes, qualified-route reassociation, or any broader deployment mutation.

On 2026-08-19, TASK-051 Reopen 1 proved that both supported deployed model-update APIs merge only non-null values and therefore cannot clear the five stored `chatgpt_auth_profile` associations. The user then explicitly said `hazlo`, approving direct database repair as the verified last resort. This approval is limited to one asserted transaction clearing that single field on the five identified unqualified public records, followed by the six supported fallback admin API writes. It does not authorize any other direct database mutation.

## Basis
- Parent investigation: `TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback`
- Evidence: `.staticeng/evidences/TASK-2026-08-19-049-diagnose-fedora-gpt56-fallback/SUMMARY.md`
- Implementation task: `TASK-2026-08-19-051-implement-fedora-chatgpt-alias-fallbacks`
