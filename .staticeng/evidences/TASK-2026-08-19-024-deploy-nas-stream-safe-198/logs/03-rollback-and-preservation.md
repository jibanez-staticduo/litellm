# Rollback And Preservation

## NAS Final State

- Running reference: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Image ID: `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Container: `62ce7fd232c7ef04fb8edfbdaf20a4b03602e719c47da7cd55a2d7c37af17500`
- Started: `2026-08-19T00:29:33.455352346Z`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Release-blocking log matches: 0
- Networks: `llm-net`, `npm_npm-net`; mount count: 6, including the restored rollback patch mount
- Wrapper/Compose hashes: `ada13e55c55f15155c972569667eed5be150824a6959453221b35cc0f86c8778` / `e55a68271cff897156d50ed6779369de3986ec47dee572aec29b76cf70224129`
- Config/OnePassword wrapper hashes: `d10d9890...4272` / `31f719b7...6289`

The 32-model inventory, inventory-pair hash, 16-rule fallback hash, eight default-qualified deployments, eight account2 deployments, and zero account3 deployments/references all match the approved quarantine baseline

All four dependency container IDs remained exact and healthy:

- PostgreSQL: `f33022571374136db12c778d88f130f13d21669d2a3897b80cd64957fa6b1a85`
- Redis: `8339623433c3ad44ad98968a2db02c6394f8d7b2203d583033f64c51d7c86f60`
- Admin MCP: `4849d7a2d77668ee3d0564461b4dec480902f763e7c4bd7d696d19bc46228959`
- Compatibility MCP: `75fa06bc3ef3a38467279b40cdc2b6639bfda2358e637610b71fc99aa1a77326`

## Credential Metadata Observation

Path sets, type, symlink flag, owner, mode, size, mtime, inode, and device remained exact. One salted lock-file path, `a18e6b...9213`, changed only ctime between T0, immediate rollback, and the 10-minute observation. No successful refresh or error event correlated with those changes. Under the exact Tech Lead gate this is a mandatory rejection, even though credential files remained non-empty and all modes stayed 0600

## Fedora Reverse Rollback

- Fedora runs pre-release digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Inventory remains 27 rows with 24 fallback rules
- Compose, config, wrapper, and OnePassword wrapper hashes match the pre-release baseline
- Auth/device-flow failure matches: 0

The candidate digest remains registry-resolvable. Stable remains unresolved and no registry tag was moved

Result: **ROLLBACK HEALTH PASS; RELEASE PRESERVATION GATE FAIL DUE REQUIRED FEDORA REVERSE ROLLBACK AND LOCK CTIME DRIFT**
