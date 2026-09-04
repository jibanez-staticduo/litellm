# TASK-2026-09-03-021 Evidence Summary

## Outcome

PASS. The approved Redis 7.4.11 `linux/amd64` child manifest remains available and pulled successfully. The frozen identity is unchanged. The reproducible failure is local RepoDigest spelling normalization, not manifest removal, index/child confusion, or platform mismatch

## Exact Identity

```text
repository: docker.io/library/redis
tags: 7-alpine, 7.4.11-alpine
index: sha256:ff02b58f971e7d7d156a1267e283fcbbeee91773b6aa36c49dac28ecfe28eadf
linux/amd64 child: sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c
config/image ID: sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb
version: 7.4.11
base: alpine:3.21
revision: 74654c612ee06275377d483dc4e134e57b463e9e
created: 2026-08-18T16:55:58Z
```

## Diagnostics

Registry inspection identifies `sha256:1db42...` as an OCI image manifest for `linux/amd64`, not an index. Its config descriptor is `sha256:5509...`, and official annotations identify Redis `7.4.11-alpine`. Both `7-alpine` and `7.4.11-alpine` resolve through index `sha256:ff02...` to this child

The exact authorized pull succeeded on context `default`, endpoint `unix:///var/run/docker.sock`, daemon `nas`, ID `8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f`. Local inspection returns the exact config/image ID, `linux`, `amd64`, and `REDIS_VERSION=7.4.11`

Docker records RepoDigests as `redis@sha256:1db42...` and `redis@sha256:ff02...`. The runner's literal membership test expects `docker.io/library/redis@sha256:1db42...`, so it returns false despite identical canonical repository and digest. The previous status-only failure did not retain the inner exception; it could have been transient acquisition or this deterministic post-pull check. Current evidence rules out unavailable, removed, wrong-platform, and child/index-root causes

## Required Correction And Preflight

Keep the existing frozen child/config pair. Change source verification to parse and canonicalize repository names before comparing the expected digest, with focused tests for Docker Hub's `docker.io/library/redis`, `library/redis`, and `redis` spellings and rejection of another repository or digest. Before a reauthorized lifecycle creates any task object, inspect both cached dependency refs and require their exact config IDs, RepoDigest subjects, `linux/amd64`, and version values. Continue to create containers only with `--pull never --platform linux/amd64`

## Authorization

The diagnostic cached-image pull was allowed by TASK-021 and created no task resources. The TASK-020 replacement lifecycle remains unexecuted past its formal first-resource boundary, but its no-retry clause requires new explicit PMA direction after the earlier preflight failure. PMA should reauthorize one lifecycle only after the canonical comparison fix and Tech Lead source/test PASS. The Redis identity does not change, so no SCR identity amendment is required

## Invariants

No containers, networks, volumes, services, databases, configuration, deployment, or Fedora resources were created or changed. TASK-018 complete-label queries return zero resources. NAS production remains one healthy running LiteLLM container with unchanged container ID, image ID, Compose config hash, and restart count zero. Cached PostgreSQL and Redis images remain permitted; no image was retagged, removed, or pruned

## Signed Handoff

[Agent Message] From: tool-specialist To: product_manager

TASK-021 PASS. The exact TASK-020 Redis child/config pair is available, correct, functionally equivalent, and now cached. Failure is the runner's non-canonical RepoDigest string comparison. Preserve the pair, fix canonical repository comparison, perform cache-only exact identity preflight, then obtain explicit PMA replacement-lifecycle reauthorization. Production invariants hold, no task resources or deployment occurred, and Fedora was untouched
