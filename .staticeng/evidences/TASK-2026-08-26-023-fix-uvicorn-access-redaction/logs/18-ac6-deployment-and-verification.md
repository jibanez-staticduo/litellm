# AC-6 Deployment And Verification

## Immutable Candidate

- Source revision: `73699327dde515b915ab445606ae0e19977c93af`
- Unique tag: `docker.staticduo.com/litellm:task-20260827-uvicorn-redaction-20260827T091942Z-73699327`
- Immutable registry reference: `docker.staticduo.com/litellm@sha256:8a688990cb66fa7bd804fc8ac7423dd487dfd876d10fa7ef384096ab373ff6e5`
- Local/running image ID: `sha256:9c8dfd429d8ccc03da7496d03361fb3ec58ad6b291ca6409c9bb178e068b354a`
- Runtime patch SHA-256: `42e9630075145943278a5d92dbc7cc149c7f1d2b363d087be69671d6717f2d51`
- Reviewed `litellm/_logging.py` SHA-256: `804128adf3dae118bbac42b6f2b9bd5039f83a150f315c433c5a2579520100b5`
- The context was created from `git archive HEAD` plus tracked runtime diffs, excluding test diffs. Normal `.dockerignore` processing excluded `.git`, tests, logs, and generated artifacts from the Docker context. Untracked CodeMaps and evidence files were not copied from the shared worktree
- The built image was inspected with an entrypoint override and contains the reviewed `uvicorn.access` branch, including traceback fail-closed handling

## Deployment

- Deployed through `/volume2/docker/litellm/docker-compose.yaml`
- Updated only `LITELLM_IMAGE` to the immutable digest
- Recreated only `litellm` with `--no-deps`; unrelated services and persistent configuration were unchanged
- Final state: running, healthy, zero restarts, OOM false
- Readiness: HTTP 200 from inside the container
- Running image reference and image ID exactly match the immutable candidate

## LazyMCP And Access-Log Probe

- Connected LazyMCP `mcp_status`: enabled, mode `lazymcp`, 27 visible servers, 535 visible tools
- Bounded public `/lazymcp` probe used one unique non-sensitive key-shaped marker and received the expected HTTP 401
- The matching access log was emitted normally as `GET /lazymcp?REDACTED HTTP/1.1` with `401 Unauthorized`
- Raw marker count in the bounded candidate log window: 0
- `REDACTED` count for the probe window: 1
- The raw marker and response body were not persisted in task evidence

## Bounded Clean Window

- Window: `2026-08-27T09:27:40Z` through `2026-08-27T09:29:12Z`
- `Logging error`: 0
- `cannot unpack non-iterable NoneType object`: 0
- Raw probe marker: 0
- Matching redacted access line: 1
- End state: running, healthy, zero restarts, OOM false
- Rollback was not required
