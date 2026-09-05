# Clean build and Fedora startup hold

## Source and build

Source commit `2dee9cd19e329d5c59eb712b8f27b8205ca0ff02` was committed and non-force pushed to origin/main. Only task-owned source, tests, documentation and evidence were staged. Pre-existing watchdog edits remain untouched

Build input was `git archive 2dee9cd19e329d5c59eb712b8f27b8205ca0ff02`, streamed to Fedora Docker with the unchanged repository Dockerfile, platform linux/amd64 and the full source revision label. No dirty working-tree files entered the build. The first local build used an abbreviated revision label; it was not deployed or pushed. A second exact-source build corrected the label before publication

Build completed successfully. UI and dependency layers were reused from Docker's matching cache; project installation built LiteLLM 1.100.0, enterprise 0.1.62 and proxy-extras 0.4.91. Prisma client generation and the runtime Prisma path check passed. Existing Prisma Wolfi distro/type-support warnings and Tornado test-directory cleanup warning were emitted, with successful build exit

Published tag: `docker.staticduo.com/litellm:task0905-residuals-2dee9cd19e`

Published OCI index: `sha256:4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258`

Linux/amd64 manifest: `sha256:a56f0dc247ad96eb6d13eb6ae6f173d267fef42e3fe0d65390d069a46047f03d`

Config: `sha256:071b0d181864f9de5fb0a146a412d758d7dd7fd942953f263ab74c82b309aaba`

Registry push returned the same OCI index. Fedora local image inspection confirms linux/amd64 and full revision `2dee9cd19e329d5c59eb712b8f27b8205ca0ff02`

## Fedora-only deployment

Git comparison against the previous deployed source confirms schema.prisma, migrations, pyproject.toml, uv.lock and Dockerfile are unchanged

Verified actual Compose root `/home/staticduo/docker/litellm` and selector. Owner-only backup directory `/home/staticduo/docker/litellm/releases/TASK-2026-09-05-002-residuals` retains byte-verified copies of existing .env, docker-compose.yaml and config.yaml when present; copies mode 0600, directory mode 0700. Existing recovery directories were not removed or overwritten. No DB/schema or host-specific credential/configuration migration was attempted

Only the exact LITELLM_IMAGE selector changed. Byte comparison reversing that selector replacement equals the original .env. Compose and wrapper contents were not changed. Persistent limits remain memory=8589934592, memory+swap=8589934592, restart=no

Command: `docker compose --project-directory /home/staticduo/docker/litellm -f /home/staticduo/docker/litellm/docker-compose.yaml --env-file /home/staticduo/docker/litellm/.env up -d --no-deps --pull never litellm`

Result: only container litellm recreated and started

Actual Fedora container: `4dba9e66fcd0b316f06c3e811c97f35b3f895b4a2987347dc8dcf605202eb26a`

Started: `2026-09-05T15:01:47.161884279Z`

Selected image: `docker.staticduo.com/litellm@sha256:4800816a96e35e7e87549e23823b0627148b6dfe2ac3cb7b55dab345dede1258`

## Failed startup gate, no NAS promotion

The first readiness probe failed with URLError; the process never reached listening port 4000. Docker reports running/unhealthy, restarts=0, OOMKilled=false. An additional bounded 120.01-second socket poll remained negative

`docker top litellm -eo pid,ppid,etimes,comm` at 361 elapsed seconds showed only the entrypoint shell and an apk child, both alive for 361 seconds. The existing mounted `/app/start-litellm.sh` maps to `/home/staticduo/docker/litellm/start-litellm.sh`; its apk installation redirects output to /dev/null. No wrapper or tooling repair was attempted. Docker log projection returned zero lines

One sample showed cgroup memory.current=91324416 bytes and low/high/max/oom/oom_kill/oom_group_kill/sock_throttled counters all zero. This is a startup containment observation, not the required 900-second soak

A separate read-only request from this container to the official Wolfi APKINDEX returned HTTP 200 in 0.52 seconds. Therefore generic Wolfi index network unavailability is not established. The reason the existing apk child has not completed remains unresolved; no claim of a LiteLLM source failure or a specific external package/network cause is made

The deployed-fix functional probes stopped at readiness. Astra after actual reload, Chat/Responses, aggregate MCP and healthy real-tool checks did not run, and no Fedora PASS or 900-second PASS is claimed. PMA was notified immediately of the startup hold. Per explicit direction there was no automatic rollback and the candidate remains selected and contained

NAS was not changed or promoted. Last fresh read-back retains container `6b6f8743c69dab2a768dc76bef046511c7486bf0627d3fc0bc0a587bd4ff314c` on `docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`, running/healthy, restarts=0, OOMKilled=false. Its Frigate TCP failures remain the separately established external limitation from log 01, not the Fedora startup cause

Final read-back at 491 elapsed seconds still shows Fedora's same shell/apk process pair and running/unhealthy status, zero restarts/OOM. The same read-back confirms NAS remains running/healthy on its unchanged container and selector

## Required continuation

PMA should route the bounded Fedora bootstrap investigation without changing Frigate, credentials or unrelated tooling. Keep the same task active. The task's three product corrections have passed mapped source verification and built successfully, but release acceptance is blocked on actual Fedora readiness and all subsequent functional/resource gates. NAS may receive this exact digest only after those gates pass
