# Reopen 2 Build, Stop, And Cleanup Ledger

## Source Gate

Requested source:

```text
HEAD 9374aae27c93d509a12f167c6bb1f83815ed3db1
parent 0573332425de92ad8f17f6eb3196fce0d3ce7f22
worktree status: clean
worktree mode: detached
location: /tmp/opencode/task-011-r2-src-9374aae
```

The requested commit's root Dockerfile SHA-256 was `e7e669bfd09b5beb9ec27fc1a976bf90232adf7144fda5def7a761e2ddbcad11`. Its build and runtime default were the same immutable Wolfi digest, and Python runtime/development packages were pinned to `3.13.15-r4`

## Exact Builder Attempt

The task-owned BuildKit instance used Docker Buildx 0.32.1 and BuildKit 0.13.1. The exact command shape was:

```text
docker buildx build --builder task011r2-builder --platform linux/amd64 --target builder \
  --label staticeng.task=TASK-2026-09-01-011-r2 \
  --label org.opencontainers.image.revision=9374aae27c93d509a12f167c6bb1f83815ed3db1 \
  --tag task011r2-builder:9374aae --load --progress=plain .
```

Relevant exact build output:

```text
(50/53) Installing python-3.13-base (3.13.15-r4)
(51/53) Installing python-3.13 (3.13.15-r4)
(52/53) Installing python-3.13-base-dev (3.13.15-r4)
(53/53) Installing python-3.13-dev (3.13.15-r4)
Using CPython from /usr/bin/python3.13
ImportError: /usr/lib/libm.so.6: version `GLIBC_2.44' not found
  (required by /usr/lib/python3.13/lib-dynload/math.cpython-313-x86_64-linux-gnu.so)
ERROR: failed to build: builder step 12/19 exited with code 2
```

No builder image was emitted. The final target was not attempted because the exact builder is mandatory and its failure is a governing stop condition

## Causality Probe

A separate disposable diagnostic build retained exact source and all other arguments but replaced only `LITELLM_BUILD_IMAGE` with the previously reviewed Wolfi digest that embeds glibc 2.44. This was not a release candidate. It selected the same Python `3.13.15-r4`, completed both frozen syncs, built the Rust extension, generated Prisma, and emitted temporary builder image ID `sha256:88fb0130547d559b761e6121c6671818cf0159f75fc70c2cd4b1a04bdd7edce3`

The diagnostic builder image and BuildKit state were deleted. This proves the committed default base, rather than source or lock content, is the discriminating failed input. An argument override cannot qualify exact commit defaults and was not retained

## Production Preservation

Only these Reopen 2 allowlisted commands were used against production:

```text
docker ps --no-trunc --filter name=^/litellm$ --format '{{.ID}} {{.Image}} {{.Status}}'
docker inspect --format '{{.Id}} {{.Image}} {{.State.Status}} {{if .State.Health}}{{.State.Health.Status}}{{end}} {{.RestartCount}} {{.State.OOMKilled}}' litellm
```

The before and after values matched exactly:

```text
container identity: unchanged
image selector: unchanged
state: running
health: healthy
restart count: 0 before, 0 after
OOM killed: false before, false after
```

No broad inspection, `.Config` inspection, production Compose/env/config/mount read, production network attachment, restart, replacement, or mutation occurred

## Cleanup Proof

Post-cleanup checks returned no task or probe resources:

```text
containers with task label: 0
networks with task label: 0
volumes with task label: 0
images with task/probe labels: 0
task BuildKit instances: 0
task BuildKit containers: 0
task detached worktrees: 0
temporary metadata files: 0
```

The default Docker builder remained present and unchanged. No candidate, builder, or mutable release tag was retained because the exact build emitted none

## StaticEng Validation

```text
PASS: All source directories indexed. Hierarchy validated.
Warnings: 0
```
