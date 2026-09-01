---
id: TASK-2026-08-26-006-preflight-npm-publication-auth
complexity: tiny
track: investigation
slice: foundation
status: done

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations
- Transient npm authentication succeeded as `staticduo` using ignored mode-0600 `.npmjs`.
- No credential material was printed, copied, or persisted elsewhere.
scr: SCR-2026-08-26-001-qwen38-native-reasoning-modes
parent: TASK-2026-08-26-005-plugin-only-deepseek-qwen38-config
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-006 - Preflight npm Publication Auth

## Objective
Locate and safely validate the repository-local protected npm credential source for publishing `@staticeng/opencode-litellm`, without exposing or persisting secrets.

## Acceptance Criteria
- [ ] AC-1: Identify the exact protected credential file/path without returning its value or contents.
- [ ] AC-2: Verify ownership, permissions, gitignore/tracking status, and absence from intended package contents.
- [ ] AC-3: Define and execute a transient safe `npm whoami` preflight if possible, with no shell tracing or new credential persistence.
- [ ] AC-4: Inspect the active OpenCode plugin reference and protected rollback backup without editing.
- [ ] AC-5: Return the authenticated npm identity or an exact user-action blocker, plus safe publish/repin steps.

## Expected Evidence
- Signed redacted handoff; no token values, auth headers, or credential file contents.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** protected root-file inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** permissions/git/package inspection
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** transient npm identity probe
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** config reference inspection
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** operational review
  - **Evidence:** signed handoff
