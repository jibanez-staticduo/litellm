---
id: TASK-2026-09-03-008-prepare-fedora-dcr-credential
complexity: standard
track: implementation
slice: qa
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Failed credential preparation remains a failed historical attempt; later approved direct probes replaced this prerequisite.
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-006-diagnose-fedora-candidate-live
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: Prepare Fedora exact-audience DCR credential

## Objective

Complete the existing DCR authorization-code flow for exact resource `https://litellm.defend.tech/toolset/defend_memory/lazymcp`, store a short-lived bearer securely outside repository and Syncthing, and prove its audience isolation before the next maintenance deployment.

## Acceptance Criteria

- [ ] AC-1: Use only supported DCR endpoints and an existing authorized Fedora principal; do not weaken auth or create broad credentials.
- [ ] AC-2: Bind the token exactly to the toolset LazyMCP resource and record only non-secret identifiers, expiry, audience, and checksums.
- [ ] AC-3: Store bearer owner-only outside repository/Syncthing/evidence and define secure revocation/destruction after use.
- [ ] AC-4: Prove rejection against aggregate, other scope, and `/mcp` audiences without exposing token or payloads.
- [ ] AC-5: Keep Fedora on rollback image, make no schema/config/source changes, and leave NAS untouched.

## Handoff

[Agent Message] From: product_manager To: tech_lead

Prepare the exact-audience credential before candidate deployment using the supported flow and an existing authorized principal. Never print/log/store token, authorization code, verifier, client secret, cookie, or credential-bearing URL. Use owner-only temporary storage outside repo and Syncthing; retain only expiry/audience/non-secret proof. Prove cross-audience rejection safely. Fedora must remain on the healthy rollback image; no candidate deployment, config/auth weakening, DB edit, mutable tag, or NAS access. Return signed pass/reject and exact secure handoff for TASK-006 retry.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

### Summary

REJECT. Fedora remains healthy on the exact rollback digest, but that image returns HTTP 404 for both supported exact-toolset discovery forms and for `/toolset/defend_memory/lazymcp`. The supported DCR flow cannot mint a provably exact-audience bearer from this runtime

### Work Performed

- Verified exact rollback identity, health, readiness, restart, and OOM state
- Ran status-only, body-discarded public discovery and transport probes
- Stopped before registration or authorization because the exact resource prerequisite failed
- Defined secure owner-only tmpfs handoff, one-hour expiry, negative-audience proof, and destruction/revocation requirements for a future compatible runtime
- Preserved Fedora and made no NAS access

### Acceptance Criteria Coverage

- **AC-1: REJECT.** No supported exact-resource DCR flow was available; no unsupported or broad credential was used
- **AC-2: REJECT.** No bearer was minted. The exact audience and its non-secret checksum are recorded in task evidence
- **AC-3: NOT CREATED.** No secret exists. The future owner-only non-Syncthing storage and destruction contract is documented
- **AC-4: BLOCKED.** Cross-audience rejection requires the exact bearer that could not be minted
- **AC-5: PASS.** Fedora is unchanged and healthy on rollback; no schema/config/source/auth/database change or NAS access occurred

### Documentation Impact

No product, architecture, technical, or CodeMap update is required because no supported behavior or maintained source changed

### Open Risks

TASK-006 remains blocked. Deploying the approved but unqualified candidate only to mint the prerequisite credential is outside this task and would violate the no-candidate boundary

### Recommended Next Step

PMA should route the smallest governed prerequisite that exposes the approved exact-resource DCR surface without relying on an unqualified production candidate, then reopen this task

### Signed Handoff

[Agent Message] From: tech_lead To: product_manager

REJECT CREDENTIAL PREPARATION; FEDORA ROLLBACK HEALTH PASS. The exact rollback image is healthy, but both supported RFC 9728 discovery forms and the exact toolset transport return 404. No supported exact-audience bearer can be minted or audience-tested from this runtime. No authorization flow or secret material was created, no broader credential was substituted, Fedora remained unchanged, and NAS was untouched. Keep TASK-006 blocked and route a governed compatible-runtime prerequisite before reopening TASK-008
