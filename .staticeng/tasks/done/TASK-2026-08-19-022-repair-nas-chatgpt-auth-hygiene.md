---
id: TASK-2026-08-19-022-repair-nas-chatgpt-auth-hygiene
complexity: standard
track: implementation
slice: foundation
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-18-020-migrate-nas-198-startup-wrapper
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-022 - Repair NAS ChatGPT Auth Hygiene

## Objective
Identify the affected NAS ChatGPT profile, restore valid non-interactive authentication where possible, and harden all ChatGPT auth directories/files so the NAS deployment gate can run safely without user questions.

## Safety
- Never expose/read credential contents in evidence or conversation.
- Back up auth files metadata and protected copies before mutation; mode 0600 files and 0700 directories.
- Preserve default/account2/account3 model registrations and fallback topology.
- Do not deploy LiteLLM 1.98.0, change models/routing, restore DB, or move tags.
- Prefer supported refresh/current authenticated state. If device authorization is required, complete it only through an already authenticated local browser/session without revealing codes; do not leave a pending auth flow.

## Acceptance Criteria
- [ ] AC-1: Identify affected profile(s) and exact sanitized auth failure category without exposing credentials.
- [ ] AC-2: Back up and harden all ChatGPT auth directories to 0700 and non-empty credential files to 0600, regular/non-symlink, correct owner.
- [ ] AC-3: Restore valid auth for each registered profile or prove unaffected profiles valid; no pending device-auth flow remains.
- [ ] AC-4: Bounded direct profile checks succeed for default/account2/account3 or return only documented provider quota, never auth/device-flow errors.
- [ ] AC-5: NAS remains healthy on 1.92.0 with exact 40-model/topology preservation; Fedora candidate and stable remain unchanged.
- [ ] AC-6: Evidence defines a fresh just-in-time metadata baseline and approves/rejects resuming NAS deployment.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-19-022-repair-nas-chatgpt-auth-hygiene/` with `SUMMARY.md` and sanitized logs under `logs/`.

## Handoff
[Agent Message] From: product_manager To: developer

Repair NAS auth hygiene without asking the user. Preserve all three profiles and topology. Use supported refresh or an already authenticated local browser/session if reauthorization is necessary; never expose codes or credential content and never leave a pending flow. Do not deploy 1.98.0 or move stable. Return approve/reject for NAS deployment and do not commit.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations
- AC-1, AC-2, and AC-6 passed; AC-3/AC-4 failed for account3; AC-5 preserved runtime/inventory but device auth remained active.
- Default and account2 refreshed successfully; account3 refresh is rejected with provider HTTP 401.
- Auth directories/files are hardened to 0700/0600 with protected backup.
- PMA authorizes a separate quarantine task because the user is unavailable and requires a functional completed release.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- AC-1, AC-2, and AC-6 passed; AC-3 and AC-4 failed because account3's refresh grant returned provider HTTP 401 and no authenticated account3 browser/session was available
- AC-5 partially passed: NAS remained healthy on 1.92.0 with the exact 40-model and three-profile registrations, and Fedora remained healthy on the candidate; the prior stable tag returned not found on two read-only checks
- The protected pre-mutation backup is `/volume2/docker/litellm/releases/20260819-chatgpt-auth-hygiene/original/`
- The live ChatGPT auth root is hardened to owner `0:0`, directory mode 0700, and file mode 0600 for all ten regular non-symlink entries
- Default refresh and direct HTTP 200 checks passed; account2 refresh passed and its bounded direct check returned allowed HTTP 429 without auth failure
- Production independently re-entered account3 device authentication and held its lock at the gate, so no-pending-auth cannot be claimed
- NAS deployment decision: REJECT
- No product documentation or CodeMap update is required
