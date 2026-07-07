---
task_id: TASK-2026-07-07-003-deploy-litellm-fedora
complexity: standard
track: implementation
slice: qa
status: done
assigned_to: developer
handoff_from: product_manager
scr: none
parent: TASK-2026-07-07-002-release-v192-replay-host
discussion: DISCUSSION-002
---

# Deploy LiteLLM CacheCodecFix Image To Fedora

## Classification

- complexity: standard
- track: implementation
- slice: qa

## Active Discussions

- DISCUSSION-002: Deploy LiteLLM cachecodecfix image to Fedora

## Context

The user asked to update LiteLLM on Fedora after confirming the local/NAS release succeeded.

Known good local image:
- Image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`
- Digest: `docker.staticduo.com/litellm@sha256:23f346521079a27dfeb9039e73dc2328c268ec50d44e11dc662c33d78a006d86`
- Local/NAS container `litellm` is running healthy on that image.

Known deploy target details from release script:
- SSH host: `fedora`
- Fedora stack dir: `/home/staticduo/docker/litellm`
- Fedora env file: `/home/staticduo/docker/litellm/.env`
- Fedora compose file: `/home/staticduo/docker/litellm/docker-compose.yaml`

Safe deploy pattern from `/home/staticduo/git/release-litellm.sh`:

```bash
ssh fedora bash -s -- /home/staticduo/docker/litellm docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707 <<'EOF'
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

Safety notes:
- Do not print or store Fedora `.env` contents or secrets.
- Do not push to `upstream`.
- If Fedora deployment fails after changing the image, either roll back to the previous Fedora image or report exact rollback command and current service impact.
- Record previous Fedora image before changing it without exposing env contents.

## Acceptance Criteria

AC-1. Fedora previous LiteLLM image is recorded safely before deployment.

AC-2. Fedora stack `/home/staticduo/docker/litellm` is updated to `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707`.

AC-3. Fedora `litellm` container is running and Docker-healthy after deploy.

AC-4. Fedora `/health/readiness` and `/health/liveliness` pass from inside the Fedora context.

AC-5. Fedora recent logs have no post-deploy `CacheCodec is not defined` entries.

AC-6. LazyMCP/MCP smoke is attempted if feasible without exposing secrets; if not feasible, explain why.

AC-7. Evidence packet exists with `SUMMARY.md` and safe logs.

AC-8. Task is moved to done and `.staticeng/tasks/current.md` has no active/blocked tasks after success.

AC-9. StaticEng evidence/closure is committed and pushed to `origin main` only.

AC-10. No secrets, `.env` contents, master keys, API keys, tokens, cookies, private keys, or session tokens are committed or logged.

## Expected Evidence

Create `.staticeng/evidences/TASK-2026-07-07-003-deploy-litellm-fedora/` with:
- `SUMMARY.md` mapping ACs to verification.
- `logs/` with safe preflight, deploy, health, log-check, and final git status outputs.

## Handoff

[Agent Message] From: product_manager To: developer
Please deploy the known-good LiteLLM image `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707` to Fedora using the stack details and safe deploy pattern in this task. Do not expose `.env` contents or secrets. Record previous Fedora image, update/pull/up only the Fedora `litellm` service, verify Docker health, readiness, liveliness, log absence of `CacheCodec is not defined`, and LazyMCP/MCP if feasible. If deployment fails, rollback or provide exact rollback command and impact. Produce evidence, move task to done on success, update current.md, commit/push only StaticEng closure artifacts to `origin main`, and return Summary, Work Performed, AC coverage, Documentation Impact, Open Risks, Recommended Next Step, previous image, final image, final health/status, rollback path.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Deployed `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-cachecodecfix-20260707` to Fedora stack `/home/staticduo/docker/litellm` using SSH host `fedora`.
- Recorded previous Fedora image before deployment: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260612-onboarding-claim-session`.
- Pulled and recreated only the Fedora `litellm` service.
- Verified final Docker status `running healthy`, readiness `{"status":"healthy","db":"connected"}`, liveliness `"I'm alive!"`, and no post-deploy `CacheCodec is not defined` log entries.
- Verified LazyMCP/MCP smoke without printing secrets: local LazyMCP status/describe passed, and Fedora `/v1/mcp/tools` returned HTTP 200 with response-shape metadata only.
- Created evidence under `.staticeng/evidences/TASK-2026-07-07-003-deploy-litellm-fedora/`.
- Product documentation changes were not required; this was an operational deployment closure.
