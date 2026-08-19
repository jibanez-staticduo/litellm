# Sequential Fedora-Then-NAS Deployment Gate

## Immutable inputs

- Candidate: `docker.staticduo.com/litellm@sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Candidate config: `sha256:9975f878bd5080e95ba6df47f36422b291bcf2123f32b00a81e69ca5bf7c9a3a`
- Expected version/revision/platform: 1.98.0 / `177c66ef727710a455f058b99f653df9b3e4c0a4` / `linux/amd64`
- Both-host immediate rollback: `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`

## Global stop rules

Do not move stable/latest. Deploy only one host at a time and recreate only LiteLLM with `--no-deps`. Stop and restore the captured host rollback on any identity, health, restart, OOM, protected-file, model/routing, account topology, native Responses, telemetry callback, Redis usage-cache, cache poller, LazyMCP, dependency, or clean-log failure

## Gate 1: Fedora

1. Re-capture and compare every Fedora identity and preservation value in `02-both-host-baselines.md`
2. Confirm candidate and rollback resolve locally and in the registry
3. Back up the exact Fedora image selector, set only `LITELLM_IMAGE` to the immutable candidate, pull, and run `up -d --no-deps litellm`
4. Require exact manifest, version, revision, architecture, readiness/liveliness 200, healthy state, no restart growth, and `OOM=false`
5. Require exact 27-row model projection, preserved two-account routing/topology, protected hashes, credentials metadata, mounts, networks, dependencies, and unrelated-service count
6. Run bounded native `stream=false`, direct profiles, public fallback, and LazyMCP status/describe/list/tool probes
7. Observe for at least ten minutes. Require no `StandardLoggingPayload is None`, missing standard logging object, `resolved_usage_cache` NameError, cache-settings poller exception, `Stream must be set to true`, auth/device-flow, migration, schema, patch, or release-blocking traceback
8. On failure, restore the captured rollback with `up -d --no-deps litellm`, prove the complete Fedora baseline, and leave NAS untouched

## Gate 2: NAS

Proceed only after Fedora passes and PMA authorizes NAS

1. Re-capture and compare every NAS identity and preservation value in `02-both-host-baselines.md`
2. Create a protected exact rollback copy of the current image selector, wrapper, and Compose files before mutation
3. Confirm candidate and rollback resolve locally and in the registry
4. Set only `LITELLM_IMAGE` to the same immutable candidate, pull, and run `up -d --no-deps litellm`
5. Require exact manifest/config, version, revision, architecture, readiness/liveliness 200, healthy state, no restart growth, and `OOM=false`
6. Require exact 32-row model projection, eight default/eight account2 and zero account3 topology, preserved routing/protected hashes/credential metadata, mounts, networks, dependencies, and unrelated-service count
7. Run native `stream=false`, direct default, allowed account2 quota disposition, public default-primary, and full LazyMCP probes
8. Observe for at least ten minutes with the same telemetry, cache poller, stream, auth, migration, schema, patch, and traceback exclusions used on Fedora
9. On failure, restore the NAS image selector plus wrapper/Compose rollback unit and prove the complete NAS baseline. Escalate split-host disposition to PMA

## Promotion hold

Stable/latest remains held after both deployments. Independent cross-host QA and explicit Tech Lead promotion authorization are required before any tag move
