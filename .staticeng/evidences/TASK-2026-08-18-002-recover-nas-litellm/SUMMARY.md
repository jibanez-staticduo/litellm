# Recovery Evidence Summary

## Result

NAS LiteLLM was recovered from a restart storm by recreating only the `litellm` Compose service with `--no-deps` on `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818`

The runtime is healthy on LiteLLM 1.92.0 with zero restarts, `OOM=false`, readiness and liveliness HTTP 200, and an exact match to the saved 40-model baseline. PostgreSQL, Redis, admin MCP dependencies, bind-mounted configuration, credentials, and data retained their pre-change identities or hashes. Fedora retained its pre-change 1.98.0 digest, runtime identity, health, and configuration hashes

AC-5 is PARTIAL/DISPOSITIONED for availability recovery after Tech Lead review. The HTTP 400 used an invalid string-input payload; both 180-second client timeouts later completed server-side with HTTP 200, indicating provider/fallback latency rather than a startup or rollback regression. LazyMCP remains unverified and is carried into the separate 1.98.0 release retry. Startup-only logs contain one successful startup marker and no matched release-blocking error categories

`staticeng_validate` also fails on pre-existing repository-wide missing CodeMaps and broken root CodeMap links. The required repair dry run proposed hundreds of unrelated CodeMap creations, so applying it was unsafe for this atomic recovery task. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/06-staticeng-validation.txt`

## Acceptance Criteria Coverage

- **AC-1: PASS**. Pre-change NAS state captured the 1.98.0 digest, runtime image ID, restart count 339, unhealthy/restarting state, `OOM=false`, rollback-back digest, and validated local rollback image ID/version without secrets. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/01-pre-change-and-rollback.txt`
- **AC-2: PASS**. Compose rendered the captured rollback tag and recreated only `litellm` with `up -d --no-deps litellm`. PostgreSQL, Redis, and both admin MCP container IDs/start times are unchanged. No database restore occurred. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/02-deployment-and-preservation.txt`
- **AC-3: PASS**. NAS is healthy with readiness and liveliness HTTP 200, zero restarts, and `OOM=false`. The zero restart count remained stable throughout verification. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/03-health-version-models.txt`
- **AC-4: PASS**. Runtime reports LiteLLM 1.92.0. Authenticated inventory exactly equals the saved sorted, unique 40-model baseline with SHA-256 `89a76d711401a12fa7e69ab67eb2ca8b8a4860b2d7c4666b101cb5c88a4ce30a`. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/03-health-version-models.txt`
- **AC-5: PARTIAL/DISPOSITIONED**. Startup-only logs are clean. Tech Lead review established that the HTTP 400 used an invalid string-input shape and the two client timeouts later completed server-side with HTTP 200. LazyMCP remains unverified and is required by the 1.98.0 release retry. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/04-smoke-and-startup-logs.txt`
- **AC-6: PASS**. Fedora remains healthy with zero restarts and `OOM=false` on digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9`; image ID, start time, and protected file hashes match pre-change values. See `.staticeng/evidences/TASK-2026-08-18-002-recover-nas-litellm/logs/05-fedora-unchanged.txt`
- **AC-7: PASS WITH AC-5 DISPOSITION RECORDED**. This packet maps AC-1 through AC-6 and records documentation impact. Product documentation is not required; PMA and Tech Lead authorized availability-recovery closure while carrying valid Responses and LazyMCP checks into the 1.98.0 release retry

## Safety Notes

- No source, database, model registry, credential, volume, dependency service, image tag, registry artifact, or Fedora state was intentionally changed
- The NAS `.env` image selector was changed only from the captured 1.98.0 digest to the authorized rollback tag
- Logs contain no credentials, authorization headers, prompts, provider responses, or private content
- Repository-wide StaticEng CodeMap repair remains an unrelated follow-up
