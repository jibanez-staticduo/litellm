# Reopen 8 Deployment Controller Failure

## Outcome

Reopen 8 passed its fresh backup/restore, exact rollback, signed identity, and approved isolated watchdog proof. The exact candidate deployment was then attempted, but the deployment controller hit a shell syntax error in its startup failure branch before it could arm the real watcher. Exact rollback ran immediately. The administrator credential was not consumed and no LazyMCP request was sent

## Passed Gates

- Fresh owner-only PostgreSQL backup, checksum, and restore listing
- Isolated restore using the exact PostgreSQL image with 161 completed migrations
- Exact rollback unit and image-only Compose delta
- Exact candidate manifest/config/source/platform identity
- Fresh signature, SPDX, CycloneDX, and SLSA verification
- TASK-004 allowlisted Docker-read boundary
- Reviewed TASK-002/003 generator and `bash -n` for all five generated scripts
- Approved isolated proof wrapper with proof-owned state, no-op rollback, 31 samples, and unchanged production pointer

## Failure And Rollback

The deployment controller used another compact `||{...}` branch around startup failure handling. Bash rejected that controller command before the real watcher started. Because selector mutation had begun, the exact rollback unit was invoked immediately

```text
candidate deployment attempted: yes
real watchdog started: no
administrator credential consumed: no
aggregate LazyMCP requests: 0
diagnostic requests: 0
exact rollback: pass
task containers/networks/volumes: 0/0/0
active attempt pointer: absent
```

Fedora is restored to exact digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, running healthy with restart zero, OOM false, and liveness/readiness 200. NAS was untouched

## Root Cause And Exact Governed Fix

Classification: deployment-controller shell syntax defect, outside the reviewed watchdog scripts. The watcher itself and isolated proof passed; the surrounding one-off SSH controller did not undergo `bash -n`

The exact fix is to place the complete deployment controller in a file, validate it with `bash -n`, and test its startup-timeout branch against an isolated/non-mutating fixture before another authorization. Every compound fallback must use valid `|| { ...; }` syntax. No LiteLLM source or production configuration correction is indicated by this attempt
