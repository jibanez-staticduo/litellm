---
id: TASK-2026-08-19-025-review-nas-identity-lock-gates
complexity: standard
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-024-deploy-nas-stream-safe-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-025 - Review NAS Identity And Lock Gates

## Objective
Classify the candidate manifest/config identity mismatch assertion and recurring credential lock-file ctime-only drift, then define corrected non-weakening gates for one controlled redeployment.

## Safety
- Read-only; both hosts remain on restored pre-release images and stable untouched.
- Do not inspect credential contents, deploy, restart, edit config/models/auth, or move tags.

## Acceptance Criteria
- [ ] AC-1: Verify registry manifest digest versus Docker config image ID semantics and define correct identity assertions.
- [ ] AC-2: Identify the salted lock-file path type/role and determine whether ctime-only drift is expected lock lifecycle behavior.
- [ ] AC-3: Confirm no credential file content/size/mtime/ownership/mode drift, auth failure, or device flow accompanied the lock drift.
- [ ] AC-4: Define exact corrected gates and approve/reject one parent redeployment.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Review the false-positive candidate identity and lock-file gates read-only. Return exact corrected assertions and an approve/reject decision for one controlled redeployment.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1 through AC-4 passed.
- Manifest/config digest semantics and exact corrected assertions are recorded.
- Lock ctime-only drift is expected chmod behavior on three allowlisted zero-byte lock files; no credential/auth drift occurred.
- Exactly one controlled NAS redeployment approved.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1 through AC-4 pass with read-only evidence under `.staticeng/evidences/TASK-2026-08-19-025-review-nas-identity-lock-gates/`
- Candidate registry manifest digest `42d365...115b` and Docker config/image ID `45a019...c73` are valid distinct identities; the running container `.Image` must equal the config ID, not the manifest digest
- The drifting path is an allowlisted zero-byte `<credential>.lock` synchronization file; unconditional mode-0600 chmod during ordinary Linux `flock` access explains isolated ctime advance
- Credential and historical files retain exact metadata requirements except for the existing positively correlated successful-refresh exception
- Approved lock files retain exact path/type/symlink/owner/mode/size/mtime/inode/device requirements; only equal-or-advanced ctime is tolerated
- Exactly one controlled parent redeployment is approved, with all other parent stop, rollback, functional, preservation, and cross-host rules unchanged
- No credential contents were inspected and no host, registry, runtime, service, configuration, model, auth, route, or tag mutation occurred
- Product, architecture, technical, and CodeMap documentation updates are not required
