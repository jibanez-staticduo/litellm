# Reviewed Manual Sequential Gate

## Immutable inputs

- Candidate tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260818-stream-safe-b0dfe2e7a7`
- Deployment reference: `docker.staticduo.com/litellm@sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- Fedora rollback: `docker.staticduo.com/litellm@sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`
- NAS rollback: `docker.staticduo.com/litellm@sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018`

## Global stop rules

Do not move stable/latest until both hosts pass every gate. Stop and roll back on digest, version, revision, architecture, health, restart, OOM, inventory, routing, protected-file, account topology, dependency, native Responses, Codex, LazyMCP, profile-isolation, or clean-log failure. Never recreate dependencies, restore databases, mutate models, read credentials, or deploy both hosts concurrently

## Gate 1: Fedora canary

1. Re-capture and compare all values in `03-fedora-preflight.log`
2. Confirm the Fedora rollback digest is available locally and registry-resolvable
3. Set only Fedora `LITELLM_IMAGE` to the immutable deployment reference, then run `docker compose ... pull litellm` and `docker compose ... up -d --no-deps litellm`
4. Verify container image digest, OCI revision/version, package 1.98.0, `linux/amd64`, readiness/liveliness 200, healthy status, no restart growth, and `OOM=false` over the observation interval
5. Prove exact public/deployment inventory and router hashes, regular/account2 topology, bidirectional fallbacks, cross-profile policy, protected files, mounts, networks, dependency IDs, and unrelated services match preflight
6. Run bounded no-retry native Responses, Codex, LazyMCP list/describe/tool, and regular/account2 profile-isolation probes. Record only sanitized status, deployment identity, and event/error class
7. Reject on startup patch, migration, schema, traceback, authentication prompt, `Stream must be set to true`, or release-blocking log matches
8. On any failure, restore the Fedora rollback digest with `up -d --no-deps litellm`, prove the complete Fedora baseline, and leave NAS untouched

## Gate 2: NAS wrapper and application

Proceed only after Fedora passes. Before any NAS mutation, create a mode-0600 timestamped rollback pair for the current wrapper and Compose file and verify hashes match `02-nas-preflight.log`

1. Remove only obsolete patch invocations and the patch bind mount per the architecture task. Preserve database fail-fast/readiness, guarded `source_url` repair, retry bounds, background behavior, `litellm "$@"`, mounts, healthcheck, networks, and service command
2. Require `sh -n`, rendered Compose, no obsolete runtime mutation references, target-image entrypoint/binary checks, and isolated wrapper dry-run success before production recreation
3. Set only NAS `LITELLM_IMAGE` to the same immutable deployment reference, then run `docker compose ... pull litellm` and `docker compose ... up -d --no-deps litellm`
4. Verify digest/revision/version/architecture, health stability, exact 40-row inventories, router hash, eight default plus eight account2 plus eight account3 qualified deployments, nine public GPT rows including unchanged TTS, fallbacks, protected files, mounts, networks, dependency IDs, and unrelated services
5. Run the same bounded native Responses, Codex, LazyMCP, profile routing, and clean-log matrix, including public aliases selecting default-profile deployments while account2/account3 remain fallback-registered
6. On any NAS failure, restore the NAS image plus wrapper/Compose pair as one unit and verify the full 1.92.0 baseline. Then restore Fedora to its captured digest so the aborted release cannot leave split image state

## Promotion handoff

After independent cross-host QA proves both running containers use the candidate manifest digest and all preservation/functional gates remain green, Tech Lead may authorize one stable-tag promotion. Re-resolve stable and require it to equal the candidate digest. This build task performed no deployment or promotion
