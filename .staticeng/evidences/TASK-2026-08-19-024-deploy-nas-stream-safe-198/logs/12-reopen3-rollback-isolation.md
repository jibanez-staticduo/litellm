# Reopen 3 Rollback And Isolation

## NAS Automatic Rollback

- Container: `a48f5a6a164a29ab7063a55ee16c5ac85c169f7ce5b2f48cf0e6f4ed7aa7ec1f`
- Deployment reference: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Image ID: `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Started: `2026-08-19T01:49:16.032432666Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Restored wrapper/Compose/config/OnePassword wrapper hashes: exact
- Four dependency IDs: exact and healthy
- Rollback mounts/networks: restored

## Ten-Minute Rollback Observation

- Started: `2026-08-19T01:51:03Z`
- Ended: `2026-08-19T02:01:05Z`
- Health/readiness/liveliness/restart/OOM: PASS
- Exact 32-model/16-rule topology and account3 quarantine: PASS
- Credential metadata under corrected gate: PASS
- Approved lock paths with ctime-only advance: two
- Auth/device-flow failure matches: 0
- Rollback clean-log matches in the inspected window: 0

## Fedora And Stable

Fedora remained exact:

- Container: `c64c3f7556eb3d1c3a3e430a4d46393a4ee9f64f2b7e91d4fec25a193c520c98`
- Digest: `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Start time: `2026-08-19T00:25:17.007636761Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Protected hashes, mounts, and dependency IDs: exact pre/post match

Candidate manifest remains resolvable. Stable remained not found before and after; no tag moved

Result: **ROLLBACK AND ISOLATION PASS**
