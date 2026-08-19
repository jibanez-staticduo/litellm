# Reopen 4 Isolation And Validation

## Fedora Isolation

Fedora remained exact before and after NAS deployment:

- Container: `c64c3f7556eb3d1c3a3e430a4d46393a4ee9f64f2b7e91d4fec25a193c520c98`
- Digest/image ID: `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Start time: `2026-08-19T00:25:17.007636761Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Five mounts, four dependency IDs, and protected file hashes: exact

## Registry And Rollback

- Candidate manifest remains registry-resolvable by exact digest
- Stable remained not found before and after; no tag moved
- Protected NAS rollback image remains locally available
- Protected rollback wrapper/Compose hashes and account3 atomic restoration backup remain exact
- Prior attempt evidence contains repeated successful automatic rollback and ten-minute rollback observations

## Validation

- Every Reopen 4 persisted mandatory sub-gate: PASS
- Canonical atomic aggregate: PASS
- Artifact hash-chain verification: PASS, 19 of 19
- `git diff --check`: PASS
- `staticeng_validate`: inherited failure on broken links and repository-wide missing CodeMaps
- `staticeng_repair` dry run: not applied because proposed changes are broad and unrelated

Final decision: **APPROVE NAS; KEEP STABLE HELD**
