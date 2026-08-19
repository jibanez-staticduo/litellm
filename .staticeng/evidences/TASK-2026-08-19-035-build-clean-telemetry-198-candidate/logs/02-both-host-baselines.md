# Current Both-Host Rollback And Identity Baselines

Captured on 2026-08-19 before the replacement build. No credentials, environment values, raw model records, or request payloads were retained

## Shared current rollback

- Immutable rollback manifest: `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Registry resolution: PASS
- Architecture: `amd64`
- Version/revision: 1.98.0 / `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Earlier NAS rollback remains registry-resolvable: `sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- Earlier Fedora rollback remains registry-resolvable: `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`

## NAS

- Container: `1fc657b5b51b7ab07b1a2ac4da13302f5e56c2123ce521481a3d82c3be36c148`
- Started: `2026-08-19T02:09:29.869606517Z`
- Running manifest/config: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b` / `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Mounts/networks: 5 / `llm-net`, `npm_npm-net`
- Model rows: 32
- Sanitized model identity projection SHA-256: `b76e2dc7fef25874c35786be12d8cec1e8ae4526010db38105cc494499d27d78`
- Account3 references: 0
- Protected `.env`/Compose/config/wrapper/OnePassword-wrapper SHA-256: `6bffa18f7f3a692889f7efbdcd9f8812e7992313193c1d180305586cb65b237c`, `0a84fde576264b85d07e5535f25255ceb0eb8d120a729e91c140b4e52b0e185b`, `d10d989072e329a3a47c11ee734783a08c8607865fa8e8fa940851e75f624272`, `7005b7bb28c94d9f044e2f15a6a0697068d604751b26cd98361440c773c47f6c`, `31f719b71fce74e968cec69aa1ce51ca4dac08381c8005aa6b5d3be2879b6289`
- PostgreSQL/Redis/admin MCP/compatibility MCP container IDs: `f33022571374136db12c778d88f130f13d21669d2a3897b80cd64957fa6b1a85`, `8339623433c3ad44ad98968a2db02c6394f8d7b2203d583033f64c51d7c86f60`, `4849d7a2d77668ee3d0564461b4dec480902f763e7c4bd7d696d19bc46228959`, `75fa06bc3ef3a38467279b40cdc2b6639bfda2358e637610b71fc99aa1a77326`; all running and healthy

## Fedora

- Container: `b4cff1ee704ccf7cb2d3f09d5890a467b3a77550fd7dd1f1e48ae631cf939b39`
- Started: `2026-08-19T02:32:15.989297648Z`
- Running manifest/local ID: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Mounts/networks: 5 / `llm-net`, `npm_npm-net`
- Model rows: 27
- Sanitized model identity projection SHA-256: `402856f9e84c813044caa3d212aeef1561e4c5e1d724b3635d777338e657255b`
- Protected `.env`/Compose/config/wrapper/OnePassword-wrapper SHA-256: `70fd4926ed9b237816057e5bdb8476af1112f1ed7fd12c9e2e79623795764c6a`, `af1a6462aad67872997638fcaa9400879ed039b42c3ae497705d00602efbf9d6`, `f3b83ce7ce2ec8418fdce63d16292c87933fe74d3f886b6d8510db8fee638967`, `9e9b0de7f19e1c8a6e784a17e855d2236183901c32d1860164e2130239c6a06e`, `31f719b71fce74e968cec69aa1ce51ca4dac08381c8005aa6b5d3be2879b6289`
- PostgreSQL/Redis/admin MCP/compatibility MCP container IDs: `f7b8b0c4fa916fdf34a185e58337b4bb701fdf29cf10933d9a6627bc1d66d8bc`, `e177e235b51263252d04a48c3a4931dc473e8d90da8455404747beebc4a51f0f`, `7b7cf44ab24b6e4194e3eb0d8da4768945985860468fc2b0010407aee0e13845`, `4faf5494e7a2c99e8d491af56f32ea71ef15bb4fe42cf6d3660f4f9736892991`; all running and healthy

Result: **CURRENT BOTH-HOST ROLLBACK AND IDENTITY BASELINE PASS**
