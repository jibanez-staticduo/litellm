# Candidate Compatibility Validation

Candidate digest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`

## Final checks

- `sh -n /volume2/docker/litellm/start-litellm.sh`: PASS
- `docker compose config --quiet` with candidate override: PASS
- Rendered Compose JSON assertions: PASS
- Runtime patch and source-mutation scan across the live wrapper/Compose: PASS, zero banned references
- Candidate config digest/image ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Candidate architecture: `amd64`
- Candidate OCI revision: `b0dfe2e7a7d5191871fa63224f5ed8f9544382fa`
- Candidate OCI version and package version: `1.98.0`
- Candidate configured entrypoint: `docker/prod_entrypoint.sh`
- Candidate `/bin/sh`, Python, `litellm`, and `apk` binaries: PASS
- Disposable candidate `postgresql-client` installation and `psql --version`: PASS

## Rendered LiteLLM service

- Image resolves to the immutable candidate digest
- Entrypoint remains `/bin/sh /app/start-litellm.sh`
- Command remains `--host 0.0.0.0 --port 4000 --config /app/config.yaml`
- Mount targets remain `/app/config.yaml`, `/app/data`, `/app/onepassword-mcp-wrapper.sh`, `/app/start-litellm.sh`, and `/run/secrets/op_service_account_token`
- `/app/patches` mount is absent
- Networks remain `llm-net` and `npm_npm-net`
- Healthcheck remains present

## Network-isolated wrapper run

The migrated live wrapper was bind-mounted read-only into the exact candidate image with `--network none`. Only `psql` and `sleep` were replaced by deterministic test doubles so no database or network could be reached. The real candidate `litellm --version` binary ran through the wrapper

- Wrapper exit: 0
- Actual LiteLLM version: 1.98.0
- Guarded `source_url` SQL calls: 46, one startup call plus 45 background repair calls
- Network: none
- Temporary test artifacts: removed

One initial rendered-mount assertion used the wrong expected service-account target. Inspection confirmed the architecture-preserved target is `/run/secrets/op_service_account_token`; the corrected final assertion passed
