# TASK-2026-09-03-009 Evidence Summary

## Summary

PASS. The exact candidate can create its own diagnostic prerequisite after deployment without weakening authentication or asking the rollback image to support candidate-only routes. The safe sequence arms the existing rollback watchdog first, deploys and stabilizes the frozen candidate, completes the candidate's public DCR plus S256 PKCE flow with an already authorized LiteLLM principal, proves the bearer is admitted only at the exact toolset resource, then uses the same bearer for the single bounded diagnostic call

Candidate deployment is not contingent on a pre-existing bearer. Deployment is authorized by the maintenance amendment and protected by the independent watchdog. The bearer is a post-deployment diagnostic artifact, so failure to create, isolate, or prove it is a rollback condition rather than a reason to broaden credentials

## Work Performed

- Read TASK-006, TASK-007, TASK-008, the amended SCR, prior release and qualification evidence, the steady-state LazyMCP OAuth contract, relevant CodeMaps, DCR source, admission source, route source, dashboard completion UI, and focused tests
- Mapped the candidate's exact protected-resource discovery, authorization-server discovery, registration, authorization, explicit consent completion, token, refresh revocation, and exact-audience admission contracts
- Designed the owner-only tmpfs client workspace, browser-to-host manual code delivery, exact-resource positive and negative proofs, one-call handoff, unconditional cleanup, and bounded fallback
- Reconciled the bootstrap with TASK-007's one-second resource watchdog and four-hour maintenance schedule without changing its stop thresholds
- Performed no deployment, authorization flow, credential creation, host access, source/config/database/container/registry mutation, Git ref change, or NAS access

## Acceptance Criteria Coverage

- **AC-1: PASS.** `.staticeng/evidences/TASK-2026-09-03-009-design-candidate-dcr-bootstrap/logs/01-candidate-live-dcr-bootstrap.md` maps the exact endpoint chain, mandatory S256 parameters, existing UI-session principal, deliberate consent POST, manual loopback delivery, exact-resource token redemption, and live-principal revalidation without recording secrets
- **AC-2: PASS.** The runbook orders preflight, watchdog, candidate health, DCR mint, exact and cross-audience proof, immediate one-call reproduction, refresh revocation, token destruction, and exact rollback within explicit monotonic deadlines
- **AC-3: PASS.** The independent watchdog is armed before selector mutation and remains active through browser authorization, token exchange, audience proof, diagnostic request, settlement, cleanup, and rollback. Existing memory and host thresholds remain unchanged, and no bearer is a deployment prerequisite
- **AC-4: PASS.** If interactive authorization and token exchange do not finish by T+7 minutes, or any stage fails, the operator cancels the flow, revokes any minted refresh token, destroys all client artifacts, and rolls back without a reproduction or alternate credential
- **AC-5: PASS.** Task and secret-free evidence contain the signed execution handoff. Research made no runtime, auth, host, source, config, database, container, registry, Git ref, or NAS mutation

## Documentation Impact

No product, steady-state architecture, technical, or CodeMap update is required. The existing architecture contract already defines the supported OAuth behavior. This evidence only composes that behavior with the approved one-time maintenance procedure

## Open Risks

- The exact candidate remains capable of catastrophic memory growth, so it must never run outside the armed watchdog and must roll back on any bootstrap delay or threshold
- Interactive sign-in depends on the existing principal still being active, the UI session being valid, and the operator completing deliberate consent promptly. This runbook does not create or repair an account or session
- The aggregate metadata does not advertise `/revoke`, although the candidate implements it. This runbook relies on that source-backed endpoint only for cleanup, not protocol discovery; treat a non-200 result as incomplete revocation requiring immediate file destruction, rollback, and PMA notification
- The access token is stateless and cannot be individually revoked. Its practical controls are one-hour expiry, live principal revalidation, owner-only handling, immediate unlink, and no refresh-token retention
- A successful diagnostic call still does not qualify the candidate. TASK-006 must identify the prior failure's cause and complete the SCR's full verification and 900-second soak or roll back

## Recommended Next Step

PMA should send this runbook to Tech Lead as the candidate-live prerequisite for reopening TASK-006. Tech Lead should execute it only inside the still-authorized four-hour maintenance path, preserve all TASK-007 stop gates, and roll back by T+7 minutes if the DCR bearer is not already audience-proven and ready for the one bounded call

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-009 PASS. The supported bootstrap is candidate-live and fail-closed: arm TASK-007's independent watchdog and exact rollback first, deploy and stabilize only the frozen candidate, then use its public `/register`, `/authorize`, `/authorize/complete`, and `/token` flow with S256 PKCE, the exact `https://litellm.defend.tech/toolset/defend_memory/lazymcp` resource on authorization and redemption, and an existing signed-in authorized principal. Keep all client material in an owner-only Fedora tmpfs workspace, use deliberate manual loopback code delivery, retain no client secret, prove exact admission plus rejection at aggregate LazyMCP, a distinct scope, and `/mcp`, then immediately send the single 75-second diagnostic call. Revoke the refresh token, unlink access/refresh/code/verifier/client artifacts, and continue TASK-006 only after cleanup. If token readiness is not complete by T+7 minutes, any DCR/audience step fails, the principal cannot finish, or any watchdog gate fires, destroy artifacts and roll back without using a legacy key or sending the reproduction. No mutation or secret access occurred during this research
