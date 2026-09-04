# Disposable DCR maintenance runner

`disposable_runner.py` is the executable, loopback-only integration wrapper for the maintained DCR client. It targets only Docker context `default`, endpoint `unix:///var/run/docker.sock`, daemon name `nas`, and daemon ID `8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f`. It creates four uniquely named containers: isolated PostgreSQL, isolated Redis, a synthetic `find` MCP upstream, and the exact retained LiteLLM candidate. It also creates one internal network and one PostgreSQL volume.

Safety properties:

- The candidate is the only service with a published host port, and Docker assigns that port on `127.0.0.1` only.
- Ambient `DOCKER_HOST`/`DOCKER_CONTEXT` and any daemon identity drift are rejected before resource creation; every daemon operation explicitly supplies `--host unix:///var/run/docker.sock`.
- A 128-bit random run ID names the namespace, and exact task, owner, and run labels identify every object.
- Every name must be absent before creation. A successful create response is retained provisionally before ownership inspection. Inspection timeout/failure gets bounded retries; wrong or unprovable name/ID/labels preserves the exact unresolved object and escalates. Cleanup inspects name, object ID, and all three labels immediately before removing each proven object; it never adopts or removes unowned collisions.
- The exact candidate image ID and mounted config SHA-256 are checked by `DisposableCandidateInspector` before the HTTP lifecycle starts.
- Database, master-key, salt, user, and OAuth credentials are generated for the run. Docker subprocesses receive a minimal non-secret environment. Secret setup enforces umask 077, creates the owner-only `/dev/shm` directory as 0700, and creates every file atomically with `O_CREAT|O_EXCL|O_CLOEXEC` and final mode 0400 from its first instant. Writes are completed in a loop and fsynced. Descriptor ownership remains tracked until close succeeds or an `fstat`-style probe proves the descriptor is already closed; close retries are bounded, and an unresolved descriptor is retained and blocks all further secret creation. Any mkdir/open/write/fsync/close failure removes every partial path and restores umask. Files mount read-only only to exact consumers; `candidate_secret_wrapper.py` constructs `DATABASE_URL` inside the candidate, then all files and in-process values are destroyed.
- No production mount, credential, network, database, or socket is used. The only bind mounts are reviewed repository files and the current-run owner-only tmpfs secret path, all read-only and attached only to their exact consumers.
- Cleanup removes only names created by the current runner, in reverse order. It never calls Docker prune or filters broad daemon state.
- `SIGINT`, `SIGTERM`, setup failure, lifecycle failure, and deadline expiry all pass through `finally` cleanup.
- Signal and deadline cancellation is shared with the active DCR client, which checks it between bounded HTTP phases while cleanup remains independently permitted.
- Exactly one running Compose-labelled production LiteLLM container must exist; zero or multiple matches fail without a name fallback. Its ID, image, running state, Compose configuration digest, canonical mount projection (`type`, source, destination, read-only/read-write), networks, ports, and restart count must be identical before and after the run.
- Every Docker subprocess has a hard timeout bounded by the remaining lifecycle or cleanup deadline. An independent deadline timer sets the same cancellation event while the HTTP lifecycle is active.
- Every created object ID is retained through cleanup and must be unresolvable by both name and ID before the final complete-label zero-resource queries pass.
- PostgreSQL and Redis use only TASK-020's immutable `linux/amd64` child-manifest references. Both are pulled with explicit platform and verified for exact repository digest, OCI config ID, OS, architecture, and version before any task network, volume, or container is created. Docker Hub's equivalent `docker.io/library/name`, `library/name`, and bare official-image spellings normalize to one repository identity while the complete sha256 remains exact; other registries, repositories, near names, or digests fail closed. Container creation uses `--pull never`; the runner never retags or removes images.
- Standard output is one status-only JSON object; exceptions and secrets are not printed.

The runner is intentionally not part of the default test collection because it requires the retained exact candidate image and Docker. Tech Lead controls execution after source review:

```bash
python -m tests.e2e.maintenance.disposable_runner
```

Successful output contains only the allowlisted booleans, HTTP statuses, PKCE method, and cookie count returned by `MaintenanceStatus.evidence()`. A failed run emits only `{"cleanup_complete":false,"status":"failed"}` and exits non-zero after cleanup.
