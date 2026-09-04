---
id: TASK-2026-09-03-021-investigate-redis-image-availability
complexity: tiny
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-018-fix-dcr-maintenance-client
assigned_to: tool-specialist
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate Redis image availability

## Objective

Determine why exact approved Redis linux/amd64 manifest cannot be acquired and freeze one available immutable equivalent for the replacement disposable run.

## Acceptance Criteria

- [x] AC-1: Inspect exact registry reference, manifest/index/platform/config availability without task resource creation.
- [x] AC-2: Determine whether digest was child versus index, removed, architecture-mismatched, or registry acquisition failure.
- [x] AC-3: Freeze an available Redis 7.4.11 linux/amd64 manifest/config with provenance and functional equivalence.
- [x] AC-4: Define cache/pre-pull verification and one-run reauthorization impact.
- [x] AC-5: No container/network/volume/deploy/Fedora/NAS production mutation.

## Handoff

[Agent Message] From: product_manager To: tool-specialist

Research exact Redis reference from TASK-020 using manifest inspection/pull diagnostics only; do not create task resources or retry lifecycle. Resolve child/index/reference error and freeze an available equivalent exact linux/amd64 manifest/config/version. Cached image pulls are allowed only if no containers/networks/volumes are created and production remains invariant. Update task/evidence and return signed recommendation.

# Post Implementation Task Updates

## Tool Specialist: Investigation Result

### Summary

PASS. The TASK-020 Redis subject is available and was already the correct official Redis 7.4.11 Alpine `linux/amd64` child manifest. The failed TASK-018 preflight was not caused by removal, wrong architecture, or child/index confusion. A diagnostic pull completed and exposed a local reference-normalization defect: Docker stores the canonical RepoDigest as `redis@sha256:...`, while the runner requires the literal input `docker.io/library/redis@sha256:...`

### Frozen Identity And Provenance

```text
source repository: docker.io/library/redis
source tags: 7-alpine and 7.4.11-alpine
OCI index: sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf
linux/amd64 child manifest: sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c
OCI config and local image ID: sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb
version: 7.4.11
variant: Alpine 3.21
upstream revision: 74654c612ee06275377d483dc4e134e57b463e9e
source: https://github.com/redis/docker-library-redis.git#74654c612ee06275377d483dc4e134e57b463e9e:alpine
created: 2026-08-18T16:55:58Z
entrypoint/cmd: docker-entrypoint.sh / redis-server
port: 6379/tcp
```

The immutable child reference remains `docker.io/library/redis@sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c`. No equivalent replacement digest is necessary because both official tags resolve to this same child and config. The index is provenance only, not the runtime reference

### Failure Determination

The exact child manifest resolves as OCI manifest media type, declares `linux/amd64`, points to the frozen config, and pulled successfully on the exact authorized daemon. After pull, Docker reports RepoDigests `redis@sha256:1db42...` and `redis@sha256:ff02...`. The runner compares these values to its fully qualified input string at `tests/e2e/maintenance/disposable_runner.py:581`, so the exact child identity fails only because the registry host and `library/` namespace are normalized away locally

The prior status-only evidence cannot distinguish whether its pull failed transiently or pull succeeded and this verification rejected the normalized RepoDigest. Current reproducible evidence proves availability and proves the verification defect. It does not support classifying the immutable subject as removed, architecture-mismatched, or an index mistaken for a child

### Cache And Authorization Disposition

The approved PostgreSQL and Redis child/config pairs are now cached on the exact NAS daemon. Before any future task-resource creation, source must compare canonical repository name plus digest rather than literal display spelling, then inspect both cached references for exact image/config ID, `linux`, `amd64`, and version environment. Container creation must retain `--pull never --platform linux/amd64`

No additional image acquisition is needed if that cache preflight passes. This investigation did not execute TASK-018 and did not cross its first-resource boundary, but TASK-020 requires PMA direction after any pull/preflight failure and prohibits retry. PMA must explicitly reauthorize the replacement lifecycle after the canonical RepoDigest correction receives source/test approval. An identity amendment is unnecessary because the frozen pair is unchanged

### Boundaries

Only official registry manifest inspection, exact-daemon image inspection, and authorized cached-image pulls occurred. No container, network, volume, service, database, configuration, deployment, or Fedora action occurred. Complete TASK-018 label queries remain empty. NAS production LiteLLM remains exactly one healthy running container with unchanged identity/config and restart count zero. Cached dependency images remain as permitted and were not retagged, removed, or pruned

### Signed Handoff

[Agent Message] From: tool-specialist To: product_manager

TASK-021 PASS. Redis was not removed or architecture-mismatched: TASK-020 already froze the available official 7.4.11 Alpine linux/amd64 child `sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c`, config `sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb`, under index `sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf`. Diagnostic pull and local inspection pass. The runner rejects Docker's canonical local RepoDigest `redis@sha256:...` because it compares it literally with `docker.io/library/redis@sha256:...`. Keep the same frozen identity, correct and test canonical repository-digest comparison, verify both cached dependencies before resources, and retain `--pull never`. PMA must explicitly reauthorize the lifecycle because TASK-020 requires return after the earlier preflight failure; no identity amendment is needed. Zero task resources, unchanged healthy NAS production, no deployment, and no Fedora mutation are confirmed
