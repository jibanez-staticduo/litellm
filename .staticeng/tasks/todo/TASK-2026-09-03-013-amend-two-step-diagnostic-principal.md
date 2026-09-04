---
id: TASK-2026-09-03-013-amend-two-step-diagnostic-principal
complexity: tiny
track: spec
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Amend two-step diagnostic principal

## Objective

Authorize a fail-closed two-step supported API transaction because `/user/new` cannot atomically accept a password.

## Acceptance Criteria

- [x] AC-1: `/user/new` creates only the least-privilege non-login temporary principal.
- [x] AC-2: `/user/update` immediately sets only its generated password before any login/grant/use.
- [x] AC-3: An independent cleanup worker deletes the principal if the update or any intervening gate fails.
- [x] AC-4: No login, grant, key, membership, DCR, or request may occur between create and verified password update.
- [x] AC-5: Existing deletion, expiry, baseline-restoration, secret, rollback, and NAS boundaries remain unchanged.

## Handoff

[Agent Message] From: product_manager To: business_analyst

PMA selects Tech Lead option 1: amend the SCR for a strictly verified two-step supported API transaction. `/user/new` creates only the least-privilege non-login principal; `/user/update` immediately sets only its password. Arm independent cleanup before creation. Any gap/update/verification failure deletes the principal and stops before login/grant/use. Preserve all TASK-012 boundaries. Update SCR/task and return signed handoff; no runtime mutation.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved upstream integration SCR to replace TASK-012's unsupported atomic password creation assumption with one strict supported `/user/new` then immediate `/user/update` password-only transaction. The principal remains unusable until the complete two-step gate passes, and any gap, failure, mutation mismatch, or verification failure requires deletion and stop

### Work Performed

Required the independent cleanup worker to be proven and armed before creation with the generated task user ID and deletion inputs. Defined `/user/new` as creation of only the complete least-privilege non-login principal, followed by `/user/update` as the next API request with password as its only mutable field. Prohibited every intervening login, grant mutation, key, membership, DCR operation, diagnostic use, and other API request. Preserved TASK-012's secret handling, expiry, cleanup, baseline-restoration, rollback, Fedora, and NAS boundaries. No runtime, host, database, source, service, registry, Fedora, or NAS mutation was performed

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR requires `/user/new` to create only the generated task identity with the complete existing `internal_user_viewer`, model-denial, no-key, no-membership, and exact-toolset least-privilege shape
- **AC-2: PASS.** The next API request must be `/user/update` for the same user ID, with the generated password as its only mutable field and no role, model, key, membership, grant, or permission repair
- **AC-3: PASS.** Cleanup is armed before creation, does not depend on the main client progressing, and must clear the grant, delete the user, prove restoration, and stop on any transaction or verification failure
- **AC-4: PASS.** The SCR expressly prohibits login, grant mutation, key creation, membership change, DCR, diagnostic use, and any other API request between successful creation and successful password update
- **AC-5: PASS.** Existing TASK-012 deletion, expiry, credential security, cleanup, evidence, rollback, incident, Fedora-only, and NAS-isolation requirements remain mandatory and unchanged

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth. The SCR registry remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this amendment changes a one-run maintenance transaction and adds no steady-state product behavior

### Open Risks

The execution task must retain non-secret proof that `/user/update` accepted the password-only request, read-back preserved the least-privilege shape, and the first permitted login authenticated with that password. If any proof fails, creation cleanup is mandatory and the investigation remains stopped. Supported API availability remains a cleanup dependency, with TASK-012's rollback-service fallback and critical incident rule unchanged

### Recommended Next Step

PMA should accept this amendment and reopen `TASK-2026-09-03-006-diagnose-fedora-candidate-live` for Tech Lead only with the strict two-step gate incorporated into the execution runbook. The execution must arm cleanup first and stop without login, DCR, or diagnostic use if any transaction check fails

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-013 PASS. SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes one strict supported two-step principal transaction. Arm and prove the independent cleanup worker before creation. `/user/new` creates only the complete least-privilege non-login task principal, then the immediately following `/user/update` sets only its generated password. No login, grant change, key, membership, DCR operation, diagnostic use, or other request may occur in that gap. Verify the update and unchanged least-privilege state before login. Any gap, endpoint failure, unexpected mutation, or verification failure requires immediate grant clearing, principal deletion, baseline-restoration proof, and stop without retry or repair. All TASK-012 secret, expiry, cleanup, evidence, rollback, incident, Fedora, and NAS boundaries remain unchanged. No runtime mutation occurred
