# Preservation, Restoration, And Decision

## NAS production postflight

- Container ID remained `72db643f161a4b284acdace7354ddabf4222a0388b7a6b224fa2d5f8d48cfedf`
- Start time remained `2026-08-18T17:10:37.602506412Z`
- Image remained the 1.92.0 rollback tag with image ID `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Status healthy, restart count 0, `OOM=false`, readiness HTTP 200, liveliness HTTP 200
- Running container retained its existing patch mount because production was not recreated
- Running-container count remained 143
- Networks remained `llm-net,npm_npm-net`
- Model count remained 40
- Model-name hash remained `89a76d711401a12fa7e69ab67eb2ca8b8a4860b2d7c4666b101cb5c88a4ce30a`
- Deployment-ID hash remained `29bc629224dcd1dab4573dad8707d96c5f1d849ecc654d23a1a9e3ca0ab7b465`
- Public GPT rows remained 9; account2 remained 8; account3 remained 8
- Router settings remained 16 fallback rules, `simple-shuffle`, and cross-profile fallback enabled
- PostgreSQL, Redis, admin MCP, and compatibility MCP container IDs/status/health matched the approved baseline
- `.env`, `config.yaml`, and `onepassword-mcp-wrapper.sh` hashes matched the approved baseline
- Both host patch files remained present with unchanged hashes

Credential content was never read. Presence, file count, modes, and sizes remained valid, but one mutable OAuth token mtime advanced from `1787088788` to `1787094212` while production continued serving traffic. Exact metadata equality therefore failed

## Fedora and registry postflight

- Fedora container ID remained `bb54e4bbcfe86da50580bb2bf094c31678fb6099944474baef8827f209982220`
- Fedora remained healthy on the candidate digest with restart count 0 and `OOM=false`
- Fedora start time and the five protected file hashes matched this task's preflight
- Stable remained `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`

## Exact restoration procedure

For wrapper-only restoration before any deployment:

1. Install the backup `start-litellm.sh` over `/volume2/docker/litellm/start-litellm.sh` with mode 0777
2. Install the backup `docker-compose.yaml` over `/volume2/docker/litellm/docker-compose.yaml` with mode 0777
3. Verify the restored hashes equal `ada13e55...c8778` and `e55a6827...4129`
4. Run `sh -n` and `docker compose config --quiet`
5. Do not recreate production because its current process is already the unchanged 1.92.0 container

For a future post-deployment rollback:

1. Restore the wrapper/Compose pair as above
2. Set only `LITELLM_IMAGE` in `/volume2/docker/litellm/.env` to `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
3. Pull only `litellm`
4. Run `docker compose up -d --no-deps litellm`
5. Verify the 1.92.0 digest/version, health, zero restart growth, `OOM=false`, readiness/liveliness, exact 40-row inventory/routing, dependency IDs, and restored wrapper/Compose hashes
6. If the release is aborted, restore Fedora to its captured pre-release digest according to the architecture rollback gate

## Deployment decision

**REJECT NAS production deployment at this time**

The migrated wrapper passed all technical candidate checks, but strict AC-5 credential metadata equality did not pass. PMA/Tech Lead must explicitly disposition the expected live OAuth refresh and authorize a fresh just-in-time metadata baseline before deployment can proceed
