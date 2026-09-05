---
id: TASK-2026-09-01-002-design-dual-host-release
complexity: complex
track: investigation
slice: foundation
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Historical design-only PASS retained; later approved repair path replaces this execution handoff.
scr: SCR-2026-08-31-001-lazymcp-oauth-discovery
parent: TASK-2026-09-01-003-deploy-lazymcp-oauth-fedora
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Design dual-host LazyMCP release

## Objective

Freeze exact Fedora-first/NAS-second deployment, validation, observation, rollback, and evidence procedures for the qualified immutable registry digest.

## Acceptance Criteria

- [x] AC-1: Capture current Fedora/NAS selectors, image IDs, health, model/MCP inventories, public bases, restart/OOM state, and rollback files without exposing secrets.
- [x] AC-2: Define exact publication-to-Compose identity chain and require both hosts to run the same registry digest/config image ID.
- [x] AC-3: Define Fedora gates for DB backup, deploy-only-litellm, health, models, real responses, MCP/LazyMCP discovery/challenges/real tool, preservation, logs, and observation.
- [x] AC-4: Define NAS gates and split-release rollback behavior after Fedora passes.
- [x] AC-5: Produce signed execution handoffs; do not publish, deploy, restart, alter selectors, or mutate hosts.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Use the explorer topology report and historical runbooks. Research current host state read-only. Design exact commands and stop/rollback gates, including a real authorized MCP tool check without evidence payloads and 15-minute Fedora observation before NAS. Do not mutate any host, registry, Compose/env file, image tag, DB, or production container. Return governed signed handoff.

## Architecture Review

### Authority And Frozen Release Identity

This procedure is sequential and fail-closed. `TASK-2026-09-01-001-qualify-lazymcp-oauth-release` must first return PASS, the unique candidate registry reference, its manifest digest, registry config digest, signature/attestation verification, and a Tech Lead promotion authorization. The retained local amd64 candidate config image ID is `sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e`; qualification must reject rather than substitute another config image ID

The qualified handoff must instantiate these immutable values before either deployment task begins:

```bash
export RELEASE_MANIFEST='sha256:<qualified-registry-manifest>'
export RELEASE_CONFIG='sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e'
export RELEASE_REF="docker.staticduo.com/litellm@${RELEASE_MANIFEST}"
```

`RELEASE_REF` must be a digest reference, never `latest`, `stable`, or a candidate tag. The publication-to-runtime chain is exact: reviewed source commit -> retained local config image ID -> unique candidate tag -> qualified registry manifest -> registry manifest `.config.digest` -> digest-only `LITELLM_IMAGE` -> rendered Compose `litellm` image -> running container `.Config.Image` -> running container `.Image`. Before mutation, each executor must run:

```bash
test "$RELEASE_CONFIG" = 'sha256:9aa92dbf680432a423e01cb8c781e0c89a9a241c4f3deab392d3536b5d3bee1e'
test "$(docker buildx imagetools inspect "$RELEASE_REF" --raw | jq -r '.config.digest')" = "$RELEASE_CONFIG"
docker pull "$RELEASE_REF"
test "$(docker image inspect -f '{{.Id}}' "$RELEASE_REF")" = "$RELEASE_CONFIG"
test "$(docker image inspect -f '{{.Architecture}}' "$RELEASE_REF")" = amd64
```

The pull is authorized only inside the active Fedora or NAS deployment task after qualification. If the registry digest is an index instead of the qualified single amd64 manifest, the config digest differs, the local image ID differs, or OCI revision does not equal the qualified source commit, stop without changing a selector. Both completed hosts must report the same `RELEASE_MANIFEST` and `RELEASE_CONFIG`. Do not move a mutable registry tag in these deployment tasks

### Read-Only Baseline At 2026-09-01

The baseline was captured without reading credential values or retaining response payloads

| Surface | Fedora | NAS |
| --- | --- | --- |
| Stack | `/home/staticduo/docker/litellm` | `/volume2/docker/litellm` |
| Public base | `https://litellm.defend.tech` | `https://litellm.staticduo.com` |
| Selector | `docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04` | same |
| Running image identity | `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04` | `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` |
| Registry config/local ID | `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` | same |
| Container | `f86ca0ef5d68b964a21a6e8e1db30b9c32b49b6f208df90b9f41068b5d5023f4` | `a4fee331519ed8fa2e0ae851f3e0e4a3533ebcae4f0c4752811a1f7a47f2fc8a` |
| Runtime | running, healthy, restart 0, OOM false | running, healthy, restart 0, OOM false |
| Readiness/liveliness | 200 / 200 | 200 / 200 |
| Models/fallbacks | 26 / 24 | 34 / 14 |
| Model projection SHA-256 | `98f0d541823b9f7c19c0a19d338e2f9027b07b6801015d2aeb5ab739229e6231` | `d9dedcd1aab865783f8f37536f9d104255af73b6b9b8efdb4e2c49a11c6a25f4` |
| Fallback projection SHA-256 | `a057787927e9cfb8f5b140f7b4ed7e7f90f792e88fdc86b84d0ffdb7cf2c0f0c` | `c9021c6323d89c22698eef17cd4b5ea1d26a9ec73dbf2797293398ed10e8fc73` |
| MCP registrations | 13 | 27 |
| MCP health | 11 healthy, 1 auth-required, 1 unknown | health endpoint timed out during the bounded read-only probe; authenticated LazyMCP `mcp_status` passed |
| Real tool target | `defend_memory` / `defend_memory-find` | `Memory` / `memory-find` |

Fedora protected hashes are Compose `c337af2ab702e153c805654b7b8699cf1cfdb32db1e52059f00517b603f407d4`, config `2860752a76954f4d8849d29687f31f2237eba15d96d25c432402e5daf7472880`, startup wrapper `9e9b0de7f19e1c8a6e784a17e855d2236183901c32d1860164e2130239c6a06e`, and OnePassword wrapper `31f719b71fce74e968cec69aa1ce51ca4dac08381c8005aa6b5d3be2879b6289`. NAS hashes are Compose `cda96c4205cab8291505d0e8155fd3d962aa58c509bcd0bf307ba0f5843d029e`, config `95affd137dd1e5c5039063bd4ba7b29cff3417e646f22795575f81827dc3a8e4`, startup wrapper `7005b7bb28c94d9f044e2f15a6a0697068d604751b26cd98361440c773c47f6c`, and the same OnePassword wrapper hash

The current selectors are the initial rollback references. The deployment executor must not rely on this dated snapshot alone: recapture all values immediately before mutation and use those fresh values as authoritative rollback and preservation identities. Fedora's 2026-09-01 start time and 26-model count differ from older release packets, so historical 27/32-model assertions must not be reused

### Common Fresh Preflight And Rollback Unit

Run this once on the target host with `STACK` set to its path. The resulting host-local directory is the only authorized rollback unit. Never copy it into repository evidence because the DB dump and `.env` can contain secrets

```bash
set -Eeuo pipefail
umask 077
ATTEMPT_ID="TASK-2026-09-01-$(date -u +%Y%m%dT%H%M%SZ)"
ROLLBACK="$STACK/releases/$ATTEMPT_ID/rollback"
EVIDENCE="$STACK/releases/$ATTEMPT_ID/evidence"
install -d -m 700 "$ROLLBACK" "$EVIDENCE"
cp -p "$STACK/.env" "$ROLLBACK/.env"
cp -p "$STACK/docker-compose.yaml" "$ROLLBACK/docker-compose.yaml"
cp -p "$STACK/config.yaml" "$ROLLBACK/config.yaml"
cp -p "$STACK/start-litellm.sh" "$ROLLBACK/start-litellm.sh"
cp -p "$STACK/onepassword-mcp-wrapper.sh" "$ROLLBACK/onepassword-mcp-wrapper.sh"
chmod 600 "$ROLLBACK"/* "$ROLLBACK/.env"
docker inspect litellm >"$ROLLBACK/litellm.inspect.json"
docker inspect postgresql litellm-redis litellm-admin-mcp litellm-admin-mcp-compat >"$ROLLBACK/dependencies.inspect.json"
docker inspect -f '{{.Config.Image}}' litellm >"$ROLLBACK/previous-image.txt"
PREVIOUS_REF=$(cat "$ROLLBACK/previous-image.txt")
case "$PREVIOUS_REF" in docker.staticduo.com/litellm@sha256:*) ;; *) exit 20 ;; esac
docker image inspect "$PREVIOUS_REF" >"$ROLLBACK/previous-image.inspect.json"
docker exec postgresql sh -c 'exec pg_dump --format=custom --no-owner --no-acl --username="$POSTGRES_USER" --dbname="$POSTGRES_DB"' >"$ROLLBACK/database.dump"
pg_restore --list "$ROLLBACK/database.dump" >"$ROLLBACK/database.list"
sha256sum "$ROLLBACK/database.dump" >"$ROLLBACK/database.dump.sha256"
sha256sum -c "$ROLLBACK/database.dump.sha256"
```

Also record sanitized JSON containing the current container ID, selector, image ID, health, start time, restart/OOM state, readiness/liveliness status codes, normalized model/fallback counts and hashes, MCP registration count/status counts, dependency IDs/state, mount/network projections, protected hashes, credential path metadata only, and non-image `.env` hash. Record no environment dump, authorization header, DB URL, cookie, request body, response body, token, credential filename, upstream URL, or raw log content. Require exactly one `LITELLM_IMAGE=` line, a successful `docker compose ... config --services`, `litellm` in that service list, and a rendered `config --images` entry equal to the fresh selector

Stop before deployment if the DB dump/list/checksum fails; either health endpoint is non-200; current container is not healthy with restart 0 and OOM false; a dependency is unhealthy or changed during capture; the selector is not immutable; a protected path is a symlink; credential metadata violates the host's established ownership/mode policy; Compose rendering fails; the fresh inventory differs between first and second capture; or the fresh rollback image cannot be inspected locally. NAS's current MCP health timeout is not silently waived: its fresh preflight must obtain a bounded `/v1/mcp/server/health` response or a Tech Lead must explicitly classify the same known timeout while `mcp_status`, registrations, and required real tool all pass

### Fedora Execution Handoff

Only `TASK-2026-09-01-003-deploy-lazymcp-oauth-fedora` may execute this section, after PMA activation and Tech Lead authorization

1. Set `STACK=/home/staticduo/docker/litellm`, complete the common fresh preflight, and record the fresh `PREVIOUS_REF`, baseline container/dependency IDs, inventory hashes, protected hashes, restart count, and bounded log start timestamp
2. Prove the qualified publication chain locally. Verify the rendered Compose differs only in the `litellm` image when `LITELLM_IMAGE=$RELEASE_REF`; reject any dependency, mount, network, command, environment-key, port, ulimit, or healthcheck change
3. Atomically replace exactly one `LITELLM_IMAGE=` value, preserving file owner/mode and every other byte-normalized line. Immediately prove the non-image `.env` hash equals baseline
4. Run only:

```bash
docker compose --project-directory "$STACK" -f "$STACK/docker-compose.yaml" --env-file "$STACK/.env" pull litellm
docker compose --project-directory "$STACK" -f "$STACK/docker-compose.yaml" --env-file "$STACK/.env" up -d --no-deps litellm
```

5. Within 180 seconds require running/healthy, readiness and liveliness 200, restart 0, OOM false, `.Config.Image == RELEASE_REF`, `.Image == RELEASE_CONFIG`, and unchanged dependency IDs/start times. Require OCI revision/version to match qualification
6. Require exact pre/post equality for normalized model/deployment and fallback projections, protected files, non-image environment, credential metadata, mounts, networks, ports, ulimits, command, and unrelated/dependency containers. No DB migration error is allowed; no DB restore is performed during successful deployment
7. Run one bounded real `/v1/responses` request using an approved credential read only inside the container. Persist only HTTP status, content type, selected non-secret deployment ID, ordered lifecycle classification, and error-class counts. Require HTTP 200, a complete response, and no `response.failed`; never retain prompt or generated content
8. Verify `/mcp` initialize/list behavior and MCP REST registration/health counts against the fresh baseline. For each of aggregate, a pre-authorized scoped resource, and a pre-authorized toolset resource, verify both RFC 9728 discovery forms return 200 JSON with equivalent metadata and exact canonical public `resource`; unauthenticated transport returns 401 with the exact path-inserted `resource_metadata`; invalid token adds `invalid_token`; a selection header does not change the challenge. Verify unknown scope/toolset discovery remains generic and unknown transport access fails closed. Retain only status, content type, boolean equality, canonical URL, and challenge classification
9. Use an existing owner-protected exact-audience OAuth token, never the master key as a substitute for this gate, to initialize the Fedora LazyMCP resource and call `mcp_call` for `defend_memory` / `defend_memory-find`. Require JSON-RPC success and `isError != true`. Do not persist the token, arguments, response, hashes of private content, or tool payload. Repeat discovery plus initialize three times and require zero discovery 404s
10. Scan only logs since the recorded deployment timestamp and persist aggregate counts. Any new traceback, 5xx, migration/schema/patch failure, audience/resource mismatch, unexpected 401/403, discovery 404, OAuth/token error, permission widening, MCP failure, upstream credential forwarding indication, response failure, restart, OOM, or credential/device-auth prompt is release-blocking unless conclusively attributed to unrelated pre-existing traffic by Tech Lead before proceeding
11. Observe the same Fedora container for at least 900 continuous seconds. Poll every 30 seconds for identical container ID/start time, healthy state, readiness/liveliness 200, restart 0, OOM false, exact manifest/config identity, and unchanged dependency IDs. At minute 15 rerun discovery, challenge, authorized initialize/real tool, Responses, MCP REST, inventory, preservation, and bounded-log gates
12. If and only if every gate passes, write a secret-free signed PASS handoff to PMA and Tech Lead. PMA may then activate NAS. A partial pass, shortened soak, payload-bearing evidence, or open warning is REJECT

Any Fedora failure invokes Fedora rollback immediately and leaves NAS untouched

### NAS Execution Handoff

Only `TASK-2026-09-01-004-deploy-lazymcp-oauth-nas` may execute this section. It requires the Fedora signed PASS after the full 15-minute soak, independent Tech Lead approval, and confirmation immediately before NAS mutation that Fedora still passes identity, readiness/liveliness, restart/OOM, discovery, challenge, and clean-log gates

Run the same common preflight and steps 2 through 10 with `STACK=/volume2/docker/litellm`, NAS's fresh topology, public base `https://litellm.staticduo.com`, and real tool `Memory` / `memory-find`. Recreate only NAS `litellm` with `--no-deps`. Require NAS `.Config.Image == RELEASE_REF` and `.Image == RELEASE_CONFIG`, then remotely recheck Fedora and prove both hosts have the same manifest/config pair. Host inventories are intentionally different and must each equal their own fresh baseline; do not compare inventory hashes across hosts

NAS observation is at least 10 minutes with 30-second polls, followed by the full final functional, preservation, log, and cross-host identity matrix. Any NAS gate failure starts split-release rollback. Do not move `stable`, restart Fedora opportunistically, mutate registrations, refresh credentials, restore a DB, or repair unrelated MCP health in this task

### Exact Rollback And Split-Release Resolution

Rollback restores only the selector and recreates only `litellm`; it never restores the DB because this release has no migration and successful preflight already captured a safety dump. On the affected host:

```bash
set -Eeuo pipefail
PREVIOUS_REF=$(cat "$ROLLBACK/previous-image.txt")
python3 - "$STACK/.env" "$PREVIOUS_REF" <<'PY'
import os
import sys
from pathlib import Path

path = Path(sys.argv[1])
lines = path.read_text().splitlines()
matches = [index for index, line in enumerate(lines) if line.startswith("LITELLM_IMAGE=")]
if len(matches) != 1:
    raise SystemExit("expected exactly one image selector")
lines[matches[0]] = "LITELLM_IMAGE=" + sys.argv[2]
temporary = path.with_name(path.name + ".rollback")
temporary.write_text("\n".join(lines) + "\n")
os.chmod(temporary, path.stat().st_mode & 0o777)
os.replace(temporary, path)
PY
docker compose --project-directory "$STACK" -f "$STACK/docker-compose.yaml" --env-file "$STACK/.env" pull litellm
docker compose --project-directory "$STACK" -f "$STACK/docker-compose.yaml" --env-file "$STACK/.env" up -d --no-deps litellm
```

After rollback, require the fresh baseline selector/config ID, healthy/readiness/liveliness, restart 0 for the replacement container, OOM false, inventory/fallback hashes, MCP REST, `/mcp`, LazyMCP status and real tool, Responses, protected hashes, dependency identities, and bounded logs. Preserve failed candidate logs only as sanitized counts/classifications

If Fedora fails, roll back Fedora and stop; NAS remains baseline. If NAS fails before its selector changes, roll back Fedora to its Fedora baseline and verify it, restoring a uniform pre-release state. If NAS fails after recreation, first roll back and verify NAS, then roll back and verify Fedora. If either rollback cannot be verified, stop all further mutation, hold all mutable tags, mark a critical split-release incident with the exact host/digest states, and escalate to PMA and Tech Lead. Never attempt DB restore, registration edits, credential refresh, dependency recreation, or ad hoc image substitution to conceal a split

### Stop Conditions And Evidence Contract

The release is rejected on any identity drift, missing qualification/signing gate, authorization ambiguity, failed backup, payload-bearing evidence, public-base mismatch, discovery metadata/challenge mismatch, cross-audience acceptance, permission/catalog drift, real-tool failure, Responses failure, `/mcp` or MCP REST regression, health/restart/OOM failure, inventory/config/credential/dependency drift, new release-related log error, shortened observation, or inability to verify rollback. A known pre-existing MCP `auth_required` or `unknown` state may remain only when its count and identity are unchanged and it is unrelated to the required real-tool target

Each deployment evidence packet must be host-local owner-only `0700` directories and `0600` files, with a final SHA-256 manifest and a repository `SUMMARY.md` containing only sanitized identities, counts, booleans, timestamps, and AC mapping. Never retain environment dumps, DB dumps, bearer values, cookies, credentials, request/response content, raw authorization payloads, raw private logs, private keys, or registry auth in repository evidence

### Impact And Documentation

Runtime impact is constrained to `/home/staticduo/docker/litellm/.env` and Fedora `litellm`, then `/volume2/docker/litellm/.env` and NAS `litellm`. Compose, config, wrappers, database, registrations, credentials, dependencies, networks, volumes, public routing, source, and registry tags are preservation-only. No maintained source directory or `.staticeng/codemap.yml` changes. The steady-state protocol contract remains `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`; this task is the operational release handoff and requires no product documentation change

### Technical Architect Review Note

AC-1 through AC-5 are design-covered. Current state and historical release evidence were inspected read-only. No registry operation, image pull/build/push, selector edit, DB write/dump, Compose/config change, container recreation/restart, registration change, credential access, or host mutation was performed

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

- Baseline identities, publication chain, host-specific invariants, exact mutation boundary, backups, verification, stop conditions, observation windows, and rollback sequence are frozen above
- Fedora must complete a continuous 15-minute soak before NAS authorization; NAS must use the same manifest and config image ID
- NAS failure resolves split release by verified NAS rollback followed by verified Fedora rollback; rollback uncertainty becomes a critical held incident
- Product and CodeMap documentation changes are not required; the existing architecture contract remains authoritative

[Agent Message] From: technical_architect To: product_manager

PASS FOR GOVERNED EXECUTION PLANNING. The task now freezes fresh-baseline capture, exact candidate-to-Compose identity, Fedora-first gates and 15-minute soak, NAS parity, payload-free authorized real-tool checks, stop conditions, and verified split-release rollback. Keep deployment tasks blocked until qualification supplies the exact registry manifest and Tech Lead authorizes Fedora
