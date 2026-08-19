---
id: TASK-2026-08-19-040-approve-nas-registry-acquisition
complexity: tiny
track: investigation
slice: qa
status: done
scr: SCR-2026-08-18-002-stream-safe-198-both-hosts
parent: TASK-2026-08-19-038-deploy-nas-clean-telemetry-198
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-19-040 - Approve NAS Registry Acquisition

## Objective
Define a secure credential-preserving method to pull the private replacement digest as the authenticated `staticduo` user and verify it under root before deployment.

## Acceptance Criteria
- [ ] AC-1: Identify existing authenticated Docker context/config location without exposing credentials.
- [ ] AC-2: Define pull command/identity and root verification of exact manifest/config/platform.
- [ ] AC-3: Ensure no credential copying, logging, permission weakening, or mutable tag use.
- [ ] AC-4: Approve/reject one acquisition/deployment retry.

## Handoff
[Agent Message] From: product_manager To: tech_lead

Define the secure private-registry acquisition path read-only and return exact approved procedure plus retry decision.

# Post Implementation Task Updates

## Tech Lead: Post Investigation Expectations
- AC-1/AC-2 passed; AC-3/AC-4 rejected current state due 0777 Docker credential permissions.
- Exact digest-only pull and root-verification procedure is recorded.
- Candidate is already present in the shared daemon; pull may be skipped if exact root identity checks pass after permission hardening.
