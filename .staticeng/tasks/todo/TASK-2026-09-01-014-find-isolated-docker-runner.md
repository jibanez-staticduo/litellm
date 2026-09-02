---
id: TASK-2026-09-01-014-find-isolated-docker-runner
complexity: standard
track: investigation
slice: foundation
status: done
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-01-011-qualify-upstream-isolated-candidate
assigned_to: tool-specialist
handoff_from: product_manager
reopened_count: 0
---

# Task: Find isolated Docker runner

## Objective

Locate and validate an already-authorized execution target distinct from Fedora and NAS for clean candidate build and isolated runtime qualification.

## Acceptance Criteria

- [x] AC-1: Inventory available Docker contexts, SSH hosts, VMs, DGX/Spark runners, CI runners, and rootless/container alternatives without mutation.
- [x] AC-2: Prove candidate target hostname/identity is neither Fedora nor NAS and has sufficient amd64 CPU, disk, Docker/buildx, and network access.
- [x] AC-3: Verify authorization, isolation, cleanup, artifact transfer, and secret-handling boundaries.
- [x] AC-4: Recommend exact connection/build/cleanup procedure or return a precise external blocker.

## Handoff

[Agent Message] From: product_manager To: tool-specialist

Research only. The current Docker daemon identifies as NAS and cannot be used. Inspect existing Docker contexts, SSH aliases/config names without secret contents, available VM/DGX/Spark tooling, CI/self-hosted runners, and safe remote execution capabilities. Do not create directories, containers, images, networks, volumes, sessions, or mutate hosts/config. Return one proven third-host option with exact safe procedure, or state no authorized option exists.

## Investigation Result

The required third host is blocked. The two reachable DGX Spark hosts are authorized and have ample CPU, memory, disk, Docker, buildx, network, transfer, and cleanup capability, but both are ARM64, not the required AMD64. No reachable and authorized target satisfied all acceptance conditions

Observed on 2026-09-02 using read-only commands only:

- Local Docker exposes only context `default` at `unix:///var/run/docker.sock`; its server is Linux AMD64, but the parent task already proves that daemon is NAS and excludes it
- SSH config names are `arcade`, `asus`, `dg1`, `dg2`, `fedora`, `mac`, `nas`, `pi`, `pi5`, `proart`, `ut2`, `windows`, `windows-ps`, `cachyos`, `pi5-torre`, and `mac-defend`. Secret key contents were not read
- `dg1` and `dg2` accepted non-interactive public-key SSH as user `staticduo`. Both identify themselves as distinct hosts, run Ubuntu 24.04 on `aarch64`, and expose Docker 29.2.1 as ARM64 with buildx 0.31.1 and BuildKit 0.27.1. The account is in the `docker` group and has non-interactive sudo, proving execution authorization, but not AMD64 suitability
- `dg1` has 20 CPUs, about 121.6 GiB RAM, and about 155 GiB free on ext4. `dg2` has 20 CPUs, about 121.6 GiB RAM, and about 227 GiB free. Both resolve and reach `ghcr.io`; `dg1` also completed `git ls-remote` against the public upstream repository
- Both DGX hosts currently participate in active SparkRun cluster `cx7_dual`, job `811bcbb617dc5e63_497f01c831a2`. A qualification run would need namespaced Docker resources and must not stop, replace, prune, or otherwise disturb that workload
- `pi5` is reachable and authorized but ARM64 with four CPUs. `pi` is ARMv7. `asus` is ARM64 without Docker. `ut2` is ARM64 and its Docker daemon was inaccessible. Other configured non-excluded hosts were unreachable or timed out during bounded read-only SSH probes
- No local Podman, Buildah, nerdctl, Finch, Lima, Multipass, Vagrant, Incus, or LXC alternative is installed. `virsh` exists, but system access requires unavailable interactive PolicyKit authorization and therefore proves no authorized VM. No VM or machine was created
- The fork has zero registered self-hosted GitHub runners. Repository GitHub Actions are disabled at repository level. Hosted workflows name `ubuntu-latest`, including Docker image builds, but cannot be dispatched while Actions are disabled and do not implement the parent task's complete retained candidate and runtime qualification contract

## Boundaries And Exact Resume Procedure

PMA must provision or explicitly authorize one reachable Linux AMD64 runner that is neither Fedora nor NAS, then rerun the read-only preflight below before handing it to TASK-011:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <runner> '
  set -eu
  hostname
  uname -m
  id
  docker version --format "server={{.Server.Version}} os={{.Server.Os}} arch={{.Server.Arch}}"
  docker info --format "name={{.Name}} cpus={{.NCPU}} mem={{.MemTotal}} root={{.DockerRootDir}} security={{json .SecurityOptions}}"
  docker buildx version
  docker buildx ls
  df -Pk / /home | sort -u
  git ls-remote https://github.com/BerriAI/litellm.git HEAD
  curl -sSI --max-time 10 https://ghcr.io/v2/ | sed -n "1p"
'
```

Require `uname -m=x86_64`, Docker server `arch=amd64`, sufficient free disk for source plus builder/final images and evidence, successful public egress, and a host identity independently shown not to be Fedora or NAS. Transfer the exact clean commit by public immutable Git commit where possible. If an offline bundle is required, use `git bundle` or `tar` over SSH and verify a recorded SHA-256 before use. Do not forward the SSH agent and do not copy `.env`, GitHub credentials, Docker auth, production config, databases, private keys, or runtime secrets

TASK-011 must generate a unique task prefix and label for every container, image, network, volume, and builder. It may remove only resources that match both that exact prefix and label after recording image IDs, digests, SBOMs, scans, logs, and checksums. Never run host-wide `docker system prune`, `docker builder prune`, unfiltered `docker rm`, `docker rmi`, or `docker volume/network prune`. Any credential needed for the candidate-bound real-tool gate must be separately authorized, short-lived, injected without disk persistence, redacted from evidence, and revoked after use

## Acceptance Criteria Evidence

- **AC-1: PASS.** Docker contexts, SSH aliases and reachable hosts, VM tools, DGX/Spark, GitHub-hosted and self-hosted runners, and rootless/container alternatives were inventoried without runtime mutation
- **AC-2: BLOCKED EXTERNALLY.** Distinct authorized hosts were proven, but every reachable option is ARM64/ARMv7. No authorized Linux AMD64 target distinct from Fedora and NAS is available
- **AC-3: PASS FOR BOUNDARY DEFINITION.** SSH/Docker authorization and safe transfer/cleanup controls are proven or specified. Actual isolation and cleanup remain execution gates for the future runner
- **AC-4: PASS.** The precise blocker and fail-closed resume, transfer, secret, naming, and cleanup procedure are recorded

## Signed Handoff

[Agent Message] From: tool-specialist To: product_manager

BLOCKED. No authorized, reachable Linux AMD64 Docker runner distinct from Fedora and NAS exists in the inspected inventory. `dg1` and `dg2` are the strongest authorized targets, but both are ARM64 and currently run an active two-node SparkRun workload; emulation was neither proven nor authorized and cannot satisfy AC-2. Keep TASK-011 blocked until PMA supplies a third-host AMD64 runner that passes the exact read-only preflight and accepts the namespaced transfer, secret, evidence, and selective-cleanup boundaries recorded here
