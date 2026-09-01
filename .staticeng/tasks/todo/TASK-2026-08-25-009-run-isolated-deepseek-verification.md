---
id: TASK-2026-08-25-009-run-isolated-deepseek-verification
complexity: complex
track: implementation
slice: qa
status: active
scr: SCR-2026-08-25-001-deepseek-v4-native-reasoning-modes
parent: TASK-2026-08-25-007-build-stage-deepseek-policy-image
assigned_to: tech_lead
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-25-009 - Run Isolated DeepSeek Verification

## Objective
Create a temporary private NAS verification boundary for the candidate image, run the complete live contract matrix, and remove all temporary resources afterward.

## Acceptance Criteria
- [ ] AC-1: Capture protected production/staging baselines and create owner-only temporary resources with no public/NPM network, production mounts, or ChatGPT credential mounts.
- [ ] AC-2: Clone staging data locally, immediately prune the clone to both DeepSeek aliases and one provider-verified unrelated hosted-vLLM control, and prove zero ChatGPT references without exposing secrets.
- [ ] AC-3: Start the exact candidate digest on a loopback-only port with isolated PostgreSQL/Redis and achieve healthy readiness/liveness with exactly three model groups.
- [ ] AC-4: Run direct canonical vLLM probes and the complete Chat/Responses matrix for `off`, `low`, `high`, `max`, `medium`, and `xhigh` against both aliases.
- [ ] AC-5: Prove rejected requests return deterministic 400 errors and make zero DG1 calls using request-scoped correlation.
- [ ] AC-6: Verify the unrelated hosted-vLLM control remains unchanged and restart persistence passes.
- [ ] AC-7: Tear down containers, networks, volumes, dump, and temporary files; confirm production and original staging identities/state/checksums remain unchanged.
- [ ] AC-8: Produce complete redacted evidence and an explicit production promotion recommendation.

## Expected Evidence
Create `.staticeng/evidences/TASK-2026-08-25-009-run-isolated-deepseek-verification/` with `SUMMARY.md` and redacted `logs/` mapping AC-1 through AC-8.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** boundary and baseline inspection
  - **Evidence:** evidence packet
- [ ] AC-2
  - **Method:** clone allowlist verification
  - **Evidence:** redacted counts and identities
- [ ] AC-3
  - **Method:** health and inventory checks
  - **Evidence:** evidence logs
- [ ] AC-4
  - **Method:** API matrix
  - **Evidence:** evidence logs
- [ ] AC-5
  - **Method:** correlated upstream audit
  - **Evidence:** evidence logs
- [ ] AC-6
  - **Method:** non-regression and restart tests
  - **Evidence:** evidence logs
- [ ] AC-7
  - **Method:** teardown and invariant checks
  - **Evidence:** evidence logs
- [ ] AC-8
  - **Method:** closure review
  - **Evidence:** SUMMARY.md

## Blocker Report

- The isolated clone was restored and immediately reduced to the two DeepSeek aliases and one provider-verified unrelated hosted-vLLM control, with zero ChatGPT references and zero credential rows
- The exact candidate digest became ready and live on loopback only, but all three retained model records failed router loading because their encrypted `litellm_params` could not be resolved without staging's encryption context
- This violated the required exactly-three-model inventory invariant, so the request matrix, correlation checks, control probe, and restart test were not attempted
- All temporary containers, networks, volumes, encrypted dump material, keys, and the owner-only boundary were removed. Production and original staging identities, checksums, health, and state remained unchanged
- Production promotion is rejected. PMA must decide whether a resumed run may receive the original staging encryption context transiently or must use a separately re-encrypted three-model fixture

## Security Authorization
- On 2026-08-25 the user explicitly authorized one-time use of the staging encryption key inside a temporary no-egress transformer.
- Authorization is limited to in-memory decryption and immediate re-encryption of the three approved cloned model rows under a disposable fixture key.
- The original key must never reach the candidate, logs, evidence, commands, committed files, or persistent storage, and all temporary resources must be destroyed after verification.

## Reopen History

### Reopen 1 - 2026-08-25
- Reopened after explicit user security authorization.
- Execute the separately re-encrypted three-model fixture design from task 010 and rerun all remaining AC-3 through AC-8 gates.

# Post Implementation Task Updates

## Tech Lead: Post Implementation Expectations

- AC-1, AC-2, AC-7 teardown/baseline scope, and AC-8 pass
- AC-3 fails at the exactly-three-loaded-model inventory gate despite readiness/liveness passing
- AC-4 through AC-6 were stopped as required after the invariant violation
- Resume this task only after PMA resolves the encryption-context boundary; do not weaken model inventory checks or expose encrypted values
