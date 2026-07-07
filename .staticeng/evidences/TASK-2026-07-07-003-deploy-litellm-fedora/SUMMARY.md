# TASK-2026-07-07-003 Deploy LiteLLM To Fedora

## Summary

Deployed the known-good LiteLLM image to the Fedora stack at `/home/staticduo/docker/litellm` using SSH host `fedora`. Only the Fedora `litellm` service was pulled and recreated. The service is running healthy, readiness and liveliness pass from Fedora, no post-deploy `CacheCodec is not defined` entries were found, and LazyMCP/MCP smoke passed without printing secrets.

## Images

- Previous Fedora env image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`
- Previous Fedora running image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`
- Previous Fedora running image ID: `sha256:102158c62182f4db494be543dbb09580b4074dd69f87967a15e77ba3a5349a79`
- Final Fedora image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`
- Final Fedora digest: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`
- Final Fedora image ID: `sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`

## Acceptance Criteria Coverage

- AC-1: PASS. Previous Fedora env image, running image, image ID, and health were recorded before deployment in `logs/01-preflight.log` without printing `.env` contents.
- AC-2: PASS. Fedora stack `/home/staticduo/docker/litellm` was updated to `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`; `pull` and `up -d` targeted only `litellm`. See `logs/02-deploy.log`.
- AC-3: PASS. Final Docker status is `status=running health=healthy`. See `logs/04-wait-for-docker-health.log` and `logs/06-final-status.log`.
- AC-4: PASS. Fedora-local `http://127.0.0.1:4000/health/readiness` returned `{"status":"healthy","db":"connected"}` and liveliness returned `"I'm alive!"`. See `logs/03-health-and-log-check.log` and `logs/06-final-status.log`.
- AC-5: PASS. Docker logs since the new container start have no `CacheCodec is not defined` entries. See `logs/03-health-and-log-check.log` and `logs/06-final-status.log`.
- AC-6: PASS. LazyMCP tooling status and memory server describe passed locally, and Fedora `/v1/mcp/tools` returned HTTP 200 using an in-session key read that did not print secret values. See `logs/05-lazymcp-smoke.log`.
- AC-7: PASS. Evidence packet exists with `SUMMARY.md` and safe logs under `.staticeng/evidences/TASK-2026-07-07-003-deploy-litellm-fedora/`.
- AC-8: PASS. Task is moved to `.staticeng/tasks/done/`, and `.staticeng/tasks/current.md` is updated to no active/blocked tasks.
- AC-9: PASS. Closure artifacts were committed and pushed to `origin main` only in `6ccbc2e680`.
- AC-10: PASS. Evidence logs contain only safe status, image, digest, and endpoint metadata. No `.env` contents, master keys, API keys, tokens, cookies, private keys, or session tokens are logged.

## Rollback Path

If rollback is needed, restore the previous image on Fedora with:

```bash
ssh fedora bash -s -- /home/staticduo/docker/litellm docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session <<'EOF'
set -euo pipefail
stack_dir="$1"
image="$2"
env_file="${stack_dir}/.env"
compose_file="${stack_dir}/docker-compose.yaml"
if grep -q '^LITELLM_IMAGE=' "$env_file"; then
  sed -i "s|^LITELLM_IMAGE=.*|LITELLM_IMAGE=${image}|" "$env_file"
else
  printf '\nLITELLM_IMAGE=%s\n' "$image" >> "$env_file"
fi
docker compose -f "$compose_file" --env-file "$env_file" pull litellm
docker compose -f "$compose_file" --env-file "$env_file" up -d litellm
EOF
```

Expected service impact: one `litellm` container recreate; transient LiteLLM unavailability during container restart and health warmup.

## Logs

- `logs/01-preflight.log`
- `logs/02-deploy.log`
- `logs/03-health-and-log-check.log`
- `logs/04-wait-for-docker-health.log`
- `logs/05-lazymcp-smoke.log`
- `logs/06-final-status.log`
- `logs/07-staticeng-validate.log`
- `logs/08-pre-commit-git-status.log`
