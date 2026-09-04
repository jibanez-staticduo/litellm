---
id: TASK-2026-09-03-010-design-headless-dcr-authorization
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design headless DCR authorization

## Objective

Replace the unavailable browser-session dependency with a supported non-interactive authorization flow using an existing authorized Fedora principal, without weakening exact-audience security or exposing credentials.

## Acceptance Criteria

- [x] AC-1: Trace candidate `/register`, `/authorize`, `/authorize/complete`, `/token`, and principal-auth requirements from source and tests.
- [x] AC-2: Determine whether an existing API key, master key, service account, or short-lived session can complete authorization headlessly through supported endpoints.
- [x] AC-3: Define secret-safe execution entirely on Fedora using owner-only files/stdin and no token, key, code, verifier, cookie, or credential URL in command arguments or evidence.
- [x] AC-4: Preserve exact toolset audience, PKCE S256, cross-audience rejection, one-hour expiry, cleanup/revocation, watchdog, and T+7 cutoff.
- [x] AC-5: Return one executable supported procedure or a precise product limitation; no mutation.

## Handoff

[Agent Message] From: product_manager To: technical_architect

The user confirms Agent Jake is not connected and no browser automation is available. Read DCR source/tests and existing Fedora auth topology by secret-name/shape only. Find a supported headless way to authorize the exact toolset resource with an existing authorized principal; do not invent endpoints, weaken auth, read/output secret values, run an auth flow, deploy, or mutate hosts/source. Update task/evidence and return signed execution handoff.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

PASS WITH EXECUTION PRECONDITION. Candidate DCR cannot accept an API key, master key, service-account credential, gateway session, or OIDC client credential as the authorizing principal. It requires a valid UI `token` cookie at `/authorize` and `/authorize/complete`, plus explicit consent

A Fedora-local HTTP session client can use the supported `/login` username/password route for one existing toolset-authorized principal, retain cookies owner-only, and complete public DCR with S256 and exact audience without an external browser. The secret owner must first confirm that such a principal and password are available. OIDC-only identity has no supported non-interactive grant

### Work Performed

- Traced DCR, login, UI-cookie, live-user, exact-audience admission, cleanup, UI consent, and focused test contracts
- Classified existing credential shapes and inspected Fedora only by container identity, environment names, Compose substitution names, and mount metadata
- Defined a Fedora-only owner-file/stdin procedure with deliberate consent, exact audience proof, T+7, watchdog, and cleanup
- Performed no auth flow, secret read, deployment, host/source/config/database/container mutation, or NAS access

### Acceptance Criteria Coverage

- **AC-1: PASS.** Evidence maps every required route and the exact cookie-only principal boundary
- **AC-2: PASS.** Only a valid UI cookie works. Supported `/login` can mint it from existing username/password credentials; all listed key/session alternatives fail the principal contract
- **AC-3: PASS.** The procedure keeps every credential and OAuth artifact in one local process, protected stdin/file descriptors, or mode-`0600` tmpfs files, with no argument or evidence leakage
- **AC-4: PASS.** Exact toolset binding, S256, serial negative audiences, one-hour expiry, refresh revocation, artifact destruction, watcher gates, and T+7 remain mandatory
- **AC-5: PASS.** One supported procedure and the OIDC-only product limitation are documented without mutation

### Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. This task changes no maintained behavior or structure

### Open Risks

- Secret-name shape does not prove that the configured username/password principal owns current `defend_memory` permission
- Normal `/login` creates bounded UI auth state that the later execution task must authorize and clean up
- Headless consent still requires a deliberate operator decision and cannot run unattended
- Stateless access-token invalidation remains destruction, one-hour expiry, and live-principal deactivation

### Recommended Next Step

PMA should obtain secret-owner confirmation for one existing username/password principal with current toolset permission, then hand the evidence procedure to Tech Lead for the candidate-live retry. If only OIDC exists, do not execute this path

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-010 PASS WITH EXECUTION PRECONDITION. Candidate source supports a Fedora-only HTTP-session client that uses the normal `/login` username/password path to mint the exact UI cookie required by `/authorize` and `/authorize/complete`; public DCR, S256 PKCE, exact resource redemption, audience proof, T+7, watchdog, revocation, and destruction remain unchanged. API keys, the master key as a bearer, service-account tokens, gateway sessions, and OIDC client credentials cannot authorize this flow. Before reopening TASK-006, the secret owner must confirm one existing toolset-authorized username/password principal and provide only owner-only files or inherited file descriptors. The operator must explicitly approve the one `/authorize/complete` POST. If the principal is OIDC-only, approval is absent, or the exact bearer is not audience-proven by T+7, clean up and roll back without the diagnostic call. No authorization, secret value access, deployment, source/config/database/container mutation, or NAS access occurred
