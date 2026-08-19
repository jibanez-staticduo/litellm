# Backup And Migration

## Immutable inputs

- Candidate: `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- NAS rollback: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`
- NAS production remained on `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818`

## Exact rollback pair

Directory: `/volume2/docker/litellm/releases/20260819-wrapper-migration-b0dfe2e7a7/`

- `start-litellm.sh`, mode 0600, SHA-256 `ada13e55c55f15155c972569667eed5be150824a6959453221b35cc0f86c8778`
- `docker-compose.yaml`, mode 0600, SHA-256 `e55a68271cff897156d50ed6779369de3986ec47dee572aec29b76cf70224129`
- `ROLLBACK.txt`, mode 0600, records the two hashes and 1.92.0 rollback digest without secrets

The backup hashes exactly matched the live pre-migration files before editing

## Minimal migration

Final live hashes:

- `/volume2/docker/litellm/start-litellm.sh`: `7005b7bb28c94d9f044e2f15a6a0697068d604751b26cd98361440c773c47f6c`
- `/volume2/docker/litellm/docker-compose.yaml`: `0a84fde576264b85d07e5535f25255ceb0eb8d120a729e91c140b4e52b0e185b`

Removed only:

- Invocation of `mcp_subject_token_optional.py`
- Invocation of `responses_bridge_drop_empty_params.py`
- Inline Python mutation of 1.92-only health-check files under site-packages
- `./patches:/app/patches:ro` from the future Compose definition

Preserved:

- Required `DATABASE_URL` fail-fast check
- `psql` availability setup
- `ALTER TABLE ... ADD COLUMN IF NOT EXISTS source_url` compatibility repair
- 30-attempt startup readiness loop and 45-attempt background repair
- `litellm "$@"`, child status propagation, and background-process wait
- Config, wrapper, one-password helper, service-account, and data mounts
- Healthcheck, `llm-net`, `npm_npm-net`, entrypoint, and service command

No image selector, service, database, model, credential, Fedora file, or stable tag was changed
