# TASK-2026-08-31-008 Evidence Summary

## Summary

The root `Dockerfile` now contains exactly the five Tech Lead-authorized substitutions that pin builder and runtime packages to Python 3.13.15-r4 and both frozen uv sync commands to `python3.13`. No other runtime/package file was changed by this task. Exact package resolution passes for x86_64 and aarch64, and the native amd64 install probe proves CPython 3.13.15, `cpython-313`, the expected SOABI, executable, and development header

The full candidate was not built because PMA explicitly assigned that gate and complete smoke to TASK-006. This packet re-freezes the eight candidate input paths; TASK-006 must add immutable image identity after its authorized build

## Acceptance Criteria Coverage

- **AC-1: PASS.** Reopen 1 contains the signed Tech Lead approval, copied in `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/logs/07-tech-lead-authorization.log`
- **AC-2: PASS.** `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/logs/01-dockerfile-diff.log` proves exactly five additions and five removals, two exact runtime package pins, one exact dev package pin, and two `python3.13` uv selectors
- **AC-3: PASS.** `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/logs/04-unchanged-scope.log` records unchanged lock/package fingerprints, unchanged seven application fingerprints, and no TASK-008 source, test, configuration, deployment, or production mutation
- **AC-4: PASS FOR AUTHORIZED TASK-008 GATE.** Diff/static checks, both-platform package metadata, native amd64 install/ABI validation, and locked uvloop CPython 3.13 artifacts pass. The full candidate build is intentionally delegated to TASK-006 by PMA and is not claimed here
- **AC-5: PASS FOR INPUT FREEZE.** `.staticeng/evidences/TASK-2026-08-31-008-pin-candidate-python313/logs/02-fingerprints-manifest.log` records the new Dockerfile fingerprint and all seven unchanged application fingerprints. Immutable image identity remains the first TASK-006 build output

## Verification

- Exact Dockerfile diff and `git diff --check`: PASS
- Pre/post Dockerfile SHA-256: recorded
- `pyproject.toml` and `uv.lock` unchanged: PASS
- Exact Wolfi package revision in x86_64 and aarch64 signed indexes: PASS
- Native amd64 exact-package install and ABI probe: PASS
- `uvloop==0.21.0` CPython 3.13 x86_64/aarch64 Linux wheel records: PASS
- Production container/image/status/health unchanged: PASS
- `staticeng_validate`: repository-wide FAIL on pre-existing missing CodeMaps; no task-scoped CodeMap defect identified

## Documentation Impact

Product documentation is not required. The steady-state application contract is unchanged; this task changes only root Dockerfile packaging determinism. The candidate manifest and task evidence are updated

## Open Risks

Arm64 package availability is proven from its signed index, but arm64 runtime execution is not. TASK-006 must use an arm64-capable builder before any arm64 candidate is approved. Wolfi package retention remains live-repository dependent and must be checked again immediately before the TASK-006 build

## Recommended Next Step

PMA should hand the eight-path manifest to reopened TASK-006. TASK-006 should construct the clean candidate, record immutable image identity, validate final-image Python/ABI/uvloop/import behavior on every authorized platform, and run the complete isolated smoke contract
