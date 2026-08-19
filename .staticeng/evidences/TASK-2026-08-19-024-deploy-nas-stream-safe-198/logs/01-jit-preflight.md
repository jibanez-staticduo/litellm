# Just-In-Time Preflight

## Final T0

- Captured at `2026-08-19T00:28:09Z`, within 60 seconds of candidate recreation
- Preceding 15-minute sanitized auth/device-flow failure matches: 0
- ChatGPT auth root: owner `0:0`, mode 0700, ten regular non-symlink entries, every entry mode 0600
- Anthropic auth root: owner `0:0`, mode 0700, one regular non-symlink entry, mode 0600
- Service-account source: unchanged empty directory mount
- Credential contents read or retained: no

## Topology And Routing

- Model count: 32
- Model-name hash: `ba61d2feac5508f98652eaf154dbc7a5e6da6cf53f6d5f5a74cd0068230788e2`
- Inventory-pair hash: `c1b02458b0870214482918880ce8c01735bee34e00fa01cd90d7981c225273d4`
- General fallback count/hash: 16 / `d0841f275e4c4cdeafd89c4e8e24062438e70441edcb8a287974b8566b798262`
- Default-qualified deployments: 8
- Account2-qualified deployments: 8
- Account3 deployments/references: 0 / 0
- Routing strategy: `simple-shuffle`; cross-profile fallback enabled

## Rollback And Dependencies

- Candidate manifest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Candidate config ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Candidate architecture/version/revision: amd64 / 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- NAS rollback manifest: `sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Migrated wrapper/Compose hashes: `7005b7bb...7f6c` / `0a84fde5...185b`
- Protected rollback wrapper/Compose hashes: `ada13e55...c8778` / `e55a6827...4129`
- Account3 atomic restoration backup hash remained `91a02193...ffb82`
- PostgreSQL, Redis, admin MCP, and compatibility MCP identities matched the quarantine baseline and were healthy

Result: **T0 PASS**
