---
id: TASK-2026-09-03-019-authorize-nas-daemon-disposable-validation
complexity: tiny
track: spec
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-018-fix-dcr-maintenance-client
assigned_to: business_analyst
handoff_from: product_manager
reopened_count: 0
---

# Task: Authorize NAS-daemon disposable validation

## Objective

Record the user's authorization to use one isolated disposable Docker stack on the current NAS daemon for pre-Fedora validation, without changing the NAS LiteLLM deployment or accessing production data/configuration.

## Acceptance Criteria

- [x] AC-1: Permit only an explicitly verified daemon identity and a unique per-run namespace/labels.
- [x] AC-2: Require an internal network, synthetic credentials/data, loopback-only candidate port, and no production mounts/networks/configuration/database.
- [x] AC-3: Require ownership verification before deletion and prohibit broad prune or deletion of unowned resources.
- [x] AC-4: Require signal/deadline cancellation to interrupt the active lifecycle and run fail-closed cleanup.
- [x] AC-5: Preserve the running NAS LiteLLM container/image/configuration and require zero disposable resources before Fedora deployment.

## Handoff

[Agent Message] From: product_manager To: business_analyst

The user explicitly requested testing in a standalone disposable Docker stack before Fedora and destroying it afterward. The current daemon is on NAS; this authorizes only isolated ephemeral validation there, not NAS deployment or production access. Amend the SCR to require explicit daemon identity, unique ownership labels, internal networking, synthetic-only inputs, loopback exposure, collision-safe cleanup, signal cancellation, and proof the NAS LiteLLM production object is unchanged. No runtime mutation now.

# Post Implementation Task Updates

## Business Analyst: Post Implementation Expectations

### Summary

Amended the approved upstream integration SCR to authorize one isolated ephemeral validation stack on the explicitly verified current NAS Docker daemon before Fedora. The exception applies only to synthetic task-owned disposable resources and does not authorize NAS deployment, production access, or mutation of any pre-existing NAS object

### Work Performed

- Froze the exact Docker identity as context `default`, endpoint `unix:///var/run/docker.sock`, daemon name `nas`, and immutable daemon ID `8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f`, with rejection of ambient target selection or identity drift
- Required a run namespace with at least 128 bits of entropy and exact `staticeng.task`, `staticeng.owner`, and `staticeng.run` values on every container, network, volume, and created object
- Required one internal network, synthetic-only credentials and data, no production attachments, and one Docker-assigned candidate port bound exclusively to `127.0.0.1`
- Required pre-create collision checks and exact name, object-ID, and label ownership verification before deletion; prohibited adoption, broad cleanup, prune, and deletion of unowned resources
- Required SIGINT, SIGTERM, and deadline cancellation to reach the active HTTP lifecycle and trigger bounded fail-closed cleanup
- Required the NAS production LiteLLM identity, image, running state, configuration digest, mounts, networks, ports, and restart count to remain invariant, followed by absence of every current-run object ID and zero matches for the complete current-run ownership-label tuple before Fedora
- Performed no Docker, host, service, database, source, registry, Fedora, NAS runtime, or deployment mutation

### Acceptance Criteria Coverage

- **AC-1: PASS.** The SCR freezes context `default`, endpoint `unix:///var/run/docker.sock`, daemon name `nas`, and daemon ID `8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f`; every command must target the endpoint explicitly, and every resource uses a cryptographically unique namespace plus exact task, owner, and run-ID labels
- **AC-2: PASS.** The SCR requires an internal task network, synthetic-only state, no production mount/network/configuration/database/socket attachment, and a Docker-assigned IPv4-loopback candidate port with inspected topology
- **AC-3: PASS.** Every removal requires matching name, object ID, and all ownership labels. Name collision, ambiguous creation, mismatched ownership, broad listing deletion, Compose adoption, and every prune form fail closed
- **AC-4: PASS.** SIGINT, SIGTERM, and deadline expiry share cancellation with the active HTTP lifecycle, bound in-flight waits, prohibit further forward work, and enter ownership-checked cleanup on every exit
- **AC-5: PASS.** The running NAS production LiteLLM object and protected attachments must remain unchanged, and Fedora is blocked until current-run IDs are absent and the complete task, owner, and run-ID label tuple matches zero disposable resources

### Documentation Impact

Updated `.staticeng/docs/scrs/SCR-2026-09-01-001-upstream-main-integration.md` as the approved operational source of truth. `.staticeng/docs/scrs/current.md` remains correct. No product overview, feature list, architecture, technical, or CodeMap update is required because this is a one-run validation exception and adds no steady-state product behavior

### Open Risks

The current implementation described in TASK-018 Reopen 6 does not yet satisfy this amendment: daemon selection is ambient, the network is not internal, ownership is not run-unique, volume collision can adopt an existing object, and cancellation does not reach the active lifecycle. No disposable execution is authorized until those controls pass source review. Any production invariant drift or unresolved disposable resource is a critical NAS incident and blocks Fedora

### Recommended Next Step

PMA should reopen TASK-018 for Developer to implement this exact daemon, topology, ownership, cancellation, production-invariant, and zero-resource contract. Tech Lead must approve source before the one authorized disposable run; Fedora remains blocked until that run finishes cleanly

### Signed Handoff

[Agent Message] From: business_analyst To: product_manager

TASK-019 PASS. SCR `SCR-2026-09-01-001-upstream-main-integration` now authorizes only one isolated ephemeral synthetic validation stack on context `default`, endpoint `unix:///var/run/docker.sock`, daemon `nas`, immutable ID `8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f`, before Fedora. Every command must target and verify that endpoint explicitly. Require unique task/owner/run labels, collision rejection, one internal network, a Docker-assigned `127.0.0.1` candidate port, no production mounts/networks/config/credentials/DB/services/socket, and exact ownership inspection before deletion with no prune or unowned cleanup. SIGINT, SIGTERM, and deadline cancellation must reach the active lifecycle and trigger bounded fail-closed cleanup. NAS production LiteLLM identity, image, running state, config digest, mounts, networks, ports, and restart count must remain invariant, and all current-run IDs must be absent with zero resources matching the complete ownership-label tuple before Fedora. This is not NAS deployment or production access. No runtime mutation occurred
