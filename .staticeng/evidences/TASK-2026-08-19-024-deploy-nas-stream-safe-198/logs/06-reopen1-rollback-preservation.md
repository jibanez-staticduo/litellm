# Reopen 1 Rollback And Preservation

## NAS Automatic Rollback

- Rollback container: `cd8aac034d11381c0837b722cb5ffd9fc0c2af68edc3791ccc17bd0ac13ce481`
- Deployment reference: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Image ID: `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Started: `2026-08-19T00:58:11.110732293Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Restored wrapper/Compose hashes: `ada13e55...c8778` / `e55a6827...4129`
- Operational file owner/modes: `1000:10` / 0777
- Config and OnePassword wrapper hashes: unchanged
- Dependency IDs and health: exact match
- Networks/mounts: rollback baseline restored, including six mounts

## Ten-Minute Observation

- Started: `2026-08-19T01:00:12Z`
- Ended: `2026-08-19T01:10:14Z`
- Health/readiness/liveliness/restart/OOM: PASS
- Exact 32-model/16-rule topology and account3 quarantine: PASS
- Credential metadata under corrected gate: PASS at immediate and final boundaries
- Approved lock ctime advances: one; every other lock field and every credential/historical field exact
- Auth/device-flow failure matches: 0

## Fedora And Registry

Fedora remained unchanged throughout Reopen 1:

- Container ID: `c64c3f7556eb3d1c3a3e430a4d46393a4ee9f64f2b7e91d4fec25a193c520c98`
- Image/digest: `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Start time: `2026-08-19T00:25:17.007636761Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Protected hashes and four dependency IDs: exact pre/post match
- Auth/device-flow failure matches: 0

The candidate manifest remains resolvable. Stable remained not found before and after; no tag was moved

Result: **ROLLBACK AND REOPEN-BASELINE PRESERVATION PASS**
