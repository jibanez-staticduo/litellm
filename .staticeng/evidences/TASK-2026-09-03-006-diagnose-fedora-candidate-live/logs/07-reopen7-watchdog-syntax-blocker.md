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
