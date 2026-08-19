# Reopen 2 Rollback And Preservation

## NAS Automatic Rollback

- Container: `c2ed0dfcf34e6067c5d14ece9584acb37b394b6b56b8a1bc8a1a7a7f43f07abb`
- Deployment reference: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Image ID: `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Started: `2026-08-19T01:18:26.786407507Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Restored wrapper/Compose hashes: `ada13e55...c8778` / `e55a6827...4129`
- Config, OnePassword wrapper, owner/modes, four dependency IDs, networks, and six rollback mounts: exact

## Ten-Minute Observation

- Started: `2026-08-19T01:19:35Z`
- Ended: `2026-08-19T01:29:36Z`
- Health/readiness/liveliness/restart/OOM: PASS
- Exact 32-model/16-rule topology and account3 quarantine: PASS
- Credential metadata: PASS under corrected gate at both boundaries
- Approved lock paths with ctime-only advance: two; every other lock field and every credential/historical field exact
- Auth/device-flow failure matches: 0

## Fedora And Registry Isolation

Fedora remained exact across Reopen 2:

- Container: `c64c3f7556eb3d1c3a3e430a4d46393a4ee9f64f2b7e91d4fec25a193c520c98`
- Image/digest: `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Start time: `2026-08-19T00:25:17.007636761Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Protected hashes, mounts, and four dependency IDs: exact
- Readiness/liveliness: HTTP 200 / HTTP 200
- Auth/device-flow failure matches: 0

Candidate manifest remains resolvable. Stable remained not found before and after; no tag moved

Result: **ROLLBACK AND ISOLATION PASS**
