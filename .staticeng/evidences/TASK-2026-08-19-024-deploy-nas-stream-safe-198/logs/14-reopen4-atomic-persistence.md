# Reopen 4 Atomic Evidence Persistence

## Contract

Before deployment, the harness created root-protected attempt directory:

`/volume2/docker/litellm/releases/20260819-stream-safe-198-deploy/attempts/reopen4-20260819T020916Z`

Each sub-gate writes a supporting artifact and result through same-directory temporary creation, file fsync, atomic replacement, and parent-directory fsync. Each result contains:

- attempt ID and gate name
- expected and actual values
- PASS/FAIL and classification
- candidate container identity
- supporting artifact path and SHA-256
- persisted UTC timestamp

Failure handling captures a sanitized candidate-log category summary before rollback and persists the aggregate as either `SUB_GATE_FAILED` or `EVIDENCE_INCOMPLETE`. Success requires all mandatory result records present and PASS before the canonical aggregate is written

## Final Chain Verification

- Attempt ID: `reopen4-20260819T020916Z`
- Canonical aggregate: PASS / PASS
- Result records: 19
- Supporting artifact hashes independently verified: 19 of 19
- Missing mandatory sub-gates: 0
- Failed mandatory sub-gates: 0
- Candidate-log summary: persisted and sanitized

Sanitized candidate-log category counts:

- stream errors: 0
- auth failures: 0
- device-flow markers: 0
- migration failures: 0
- schema failures: 0
- patch failures: 0
- accepted quota/rate markers: 22
- generic traceback lines: 53, retained for audit but not itself a concrete blocking category under the approved account2-quota contract

Result: **ATOMIC EVIDENCE CONTRACT PASS**
