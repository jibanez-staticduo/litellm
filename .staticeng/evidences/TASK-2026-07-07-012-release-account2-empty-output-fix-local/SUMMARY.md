# Evidence Summary: TASK-2026-07-07-012

## Release
- Release scope: local/NAS LiteLLM only; Fedora deploy skipped
- Source commit: `fe302bf88d1864570b0aeb24d45951aee2a2e225`
- Release tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`
- Release digest: `docker.staticduo.com/litellm@sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316`
- Release image ID: `sha256:39defe25157c950455a83922942be5f55e428691bcf3d2b4261ce993f34e068c`

## Rollback
- Previous deployed image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-20260708`
- Previous digest: `docker.staticduo.com/litellm@sha256:a9bb7c0865dd3b65c1065c87061c3ca6bbfc7d50033aeba28ad43b7b6bdd895f`
- Rollback tag: `docker.staticduo.com/litellm:rollback-account2-emptyoutputfix-20260708`
- Rollback image ID: `sha256:aa2f2b22013e834d96c5ddf436613dc92eee18e83d4f582c916e635cdfd15be6`

## Health Verification
- Docker container image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`
- Docker health: `healthy`
- Docker status: `running`
- Readiness: HTTP 200
- Liveliness: HTTP 200

## Live Responses Smokes
All smokes used `/v1/responses` with sanitized output only.

- `chatgpt/gpt-5.5`: HTTP 200, sanitized preview `pong`
- `chatgpt-account2/gpt-5.5`: HTTP 200, sanitized preview `pong`
- `chatgpt-account2/gpt-5.4`: HTTP 200, sanitized preview `pong`

## Logs
- `logs/00-preflight.txt`
- `logs/10-release.log`
- `logs/20-post-deploy-health.txt`
- `logs/30-readiness-liveliness.txt`
- `logs/40-live-responses-smokes.txt`
- `logs/41-responses-format-probe.txt`
- `logs/42-responses-complex-input-format-probe.txt`
- `logs/50-compose-ps.txt`

## Notes
- The release was run from a temporary detached clean worktree under `/tmp/opencode/litellm-release-account2-empty-output-fix` to preserve unrelated changes in the main repository worktree; the temporary worktree was removed after release.
- No Fedora deployment was performed.
- No raw provider response bodies or secrets were written to the evidence packet.
