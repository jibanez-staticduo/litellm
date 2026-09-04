# Reopen 7 Watchdog Syntax Blocker

## Outcome

Reopen 7 stopped before candidate deployment or credential use because the task-local one-second watchdog failed shell parsing during its required pre-deployment proving period

Fresh protected backup/isolated restore, exact rollback, Compose image-only delta, candidate identity, signature, SPDX, CycloneDX, and SLSA attestations passed. The watchdog process exited immediately with a syntax error in the compact failure branch (`||{...}`), so required observability and automatic rollback control were not armed. Per the direct-probe authorization, this is an immediate stop and the candidate must not deploy

## Safe Outcome

```text
watchdog syntax/proving: fail
candidate deployed: no
administrator credential consumed: no
aggregate LazyMCP requests: 0
diagnostic requests: 0
rollback needed: no
task containers/networks/volumes: 0/0/0
active attempt pointer: absent
```

Fedora remained on exact rollback digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, healthy with restart zero, OOM false, and liveness/readiness 200. NAS was untouched

## Root Cause And Exact Fix

Classification: maintenance-control implementation defect. The generated shell used `||{` without the required separating whitespace before the compound command. Because `bash -n` was not run after this generated watchdog write, the error surfaced only when the background process started

The exact governed fix is to validate every generated watcher with `bash -n` before launching it, use `|| { ...; }` with valid shell token separation, and prove at least 30 one-second samples plus a live process before selector mutation. Validate that harness outside production before another authorized reopen. No production source or runtime patch is required

## Authorized Direct-Probe Retry

After TASK-2026-09-04-002 supplied the reviewed watcher and PMA explicitly authorized the direct probe retry, a new fresh 205,610,345-byte protected database backup was created, isolated-restored with 161 migrations, and paired with an exact rollback unit and fresh signature/attestation verification

The reviewed watcher was generated and all three scripts passed `bash -n`. Its required 31-sample rollback proof then invoked the reviewed rollback script at proof completion. That script completed successfully and removed the active-attempt pointer before any candidate selector mutation, credential consumption, or diagnostic request. The next command therefore failed closed when it could no longer resolve the active attempt

```text
reviewed watcher generated: yes
bash -n: pass
rollback proof samples: 31
proof rollback action: completed
candidate deployed: no
administrator credential consumed: no
diagnostic requests: 0
Fedora exact rollback healthy: yes
```

This is a reviewed-harness proof-mode contract mismatch: `PROOF_SAMPLE_LIMIT=31` exits the watcher loop, but the proof environment still uses the production rollback script and active pointer. The required fix is to run the reviewed harness's dedicated proof wrapper or inject a no-op proof rollback and proof-owned active pointer, as TASK-002 tests do. Do not run the production rollback action as part of a pre-deployment watcher proof
