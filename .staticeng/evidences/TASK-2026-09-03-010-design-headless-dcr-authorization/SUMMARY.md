# TASK-2026-09-03-010 Evidence Summary

## Summary

PASS WITH EXECUTION PRECONDITION. The candidate has no API-key, master-key, service-account, gateway-session, OIDC client-credentials, or other non-interactive principal grant for DCR. Both `/authorize` and `/authorize/complete` derive identity only from a bounded, master-key-signed UI `token` cookie and completion remains deliberate consent

A Fedora-only HTTP session client can remove the external-browser dependency without weakening the protocol. It may authenticate an existing username/password principal through the supported `/login` route, retain cookies owner-only, perform public DCR plus PKCE S256, explicitly submit consent, redeem for the exact toolset resource, prove cross-audience rejection, invoke once, and clean up. Execution is allowed only after the secret owner confirms the selected existing principal has both a password and current toolset authorization. OIDC-only principals remain a precise product limitation

## Work Performed

- Read the governing task and SCR, TASK-006/007/008/009 records and evidence, the LazyMCP OAuth architecture contract, relevant CodeMaps, DCR source, admission source, UI-cookie/login source, dashboard consent source, component allowlists, and focused tests
- Traced `/register`, `/authorize`, `/authorize/complete`, `/token`, refresh revocation, UI login, UI session parsing, live principal reload, exact-resource claims, and transport admission
- Classified existing Fedora credential shapes without reading values and performed one read-only host inventory limited to container identity, environment names, Compose substitution names, and mount metadata
- Defined one Fedora-only owner-file/stdin procedure preserving explicit consent, PKCE S256, exact audience, one-hour access expiry, serial rejection proofs, watchdog, cleanup, and T+7
- Performed no authorization flow, secret-value read, credential creation, deployment, source/config/database/container mutation, registry operation, Git ref change, or NAS access

## Acceptance Criteria Coverage

- **AC-1: PASS.** `.staticeng/evidences/TASK-2026-09-03-010-design-headless-dcr-authorization/logs/01-headless-dcr-authorization.md` maps all candidate DCR routes and proves principal identity comes only from the valid UI cookie at both authorization steps
- **AC-2: PASS.** Existing API/master/service-account/session credentials cannot directly authorize DCR. The supported headless bridge is normal username/password `/login` for an existing principal; OIDC-only identity has no supported non-interactive grant
- **AC-3: PASS.** The design confines password, cookies, client identifier, verifier, state, code, access token, refresh token, callback URL, and request body to one Fedora process, inherited descriptors/stdin, or owner-only tmpfs files and excludes them from arguments, output, environment exports, Syncthing, and evidence
- **AC-4: PASS.** The procedure preserves exact `https://litellm.defend.tech/toolset/defend_memory/lazymcp`, S256, one-hour access expiry, aggregate/scope/`/mcp` rejection, TASK-007 watchdog gates, refresh revocation, UI-session cleanup, artifact absence, and the T+7 cutoff
- **AC-5: PASS.** Evidence provides one executable supported procedure with an explicit secret-owner/principal precondition and a precise OIDC-only limitation. Investigation made no forbidden mutation

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. The candidate contract is unchanged. This evidence records a one-time operational composition and product limitation for the maintenance retry

## Open Risks

- Fedora's secret-name topology proves username/password configuration shape, but not that the configured principal is the user currently authorized for `defend_memory`. Secret-owner confirmation is mandatory
- `/login` creates a short-lived UI virtual key as part of the normal supported login. This is expected auth state, but its self-deletion is a cleanup mutation that must be explicitly covered by the later execution task
- Deliberate consent can be driven without a graphical browser, but cannot be unattended or auto-approved under the source-backed contract
- Access tokens are stateless and individually non-revocable. Owner-only destruction, one-hour expiry, and live-principal revalidation remain the controls
- The candidate's prior catastrophic memory behavior still requires TASK-007's already defined independent watchers and immediate rollback thresholds

## Recommended Next Step

PMA should obtain secret-owner confirmation for one existing username/password principal with current `defend_memory` toolset permission, then give this procedure to Tech Lead as the candidate-live prefix to reopened TASK-006. If only OIDC identity is available, route a separate product change or restore browser-assisted consent instead of weakening DCR

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-010 PASS WITH EXECUTION PRECONDITION. Candidate source supports a Fedora-only HTTP-session client that uses the normal `/login` username/password path to mint the exact UI cookie required by `/authorize` and `/authorize/complete`; public DCR, S256 PKCE, exact resource redemption, audience proof, T+7, watchdog, revocation, and destruction remain unchanged. API keys, the master key as a bearer, service-account tokens, gateway sessions, and OIDC client credentials cannot authorize this flow. Before reopening TASK-006, the secret owner must confirm one existing toolset-authorized username/password principal and provide only owner-only files or inherited file descriptors. The operator must explicitly approve the one `/authorize/complete` POST. If the principal is OIDC-only, approval is absent, or the exact bearer is not audience-proven by T+7, clean up and roll back without the diagnostic call. No authorization, secret value access, deployment, source/config/database/container mutation, or NAS access occurred
