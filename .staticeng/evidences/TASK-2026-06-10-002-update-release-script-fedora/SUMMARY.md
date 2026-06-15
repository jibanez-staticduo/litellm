# TASK-2026-06-10-002 Evidence Summary

## Work Summary

Updated `/home/staticduo/git/release-litellm.sh` to preserve the existing local NAS deploy and add an optional Fedora deploy path.

## Acceptance Criteria Coverage

- AC-1: PASS. Added configurable `FEDORA_HOST` and `FEDORA_STACK_DIR` defaults: `fedora` and `/home/staticduo/docker/litellm`.
- AC-2: PASS. Deploy-enabled path still updates the local NAS `.env` and now calls the Fedora deploy path, which updates remote `.env` `LITELLM_IMAGE`.
- AC-3: PASS. Fedora deploy runs over SSH and uses `docker compose -f "$compose_file" --env-file "$env_file" pull litellm` plus `up -d litellm` in the remote stack directory.
- AC-4: PASS. Fedora deploy can be disabled with `FEDORA_DEPLOY=0` or `--no-fedora-deploy`.
- AC-5: PASS. `--build-only` still sets `DEPLOY=0`, so local and Fedora deploy blocks are skipped.
- AC-6: PASS. Shell syntax and safe command-path review were recorded. Live release was intentionally not run.

## Verification Logs

- `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/logs/bash-n.log`: `bash -n /home/staticduo/git/release-litellm.sh`; passed with no output.
- `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/logs/help.log`: safe help output showing the new CLI flag and environment variables.
- `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/logs/command-path-review.log`: static command-path checks for defaults, opt-outs, SSH argument passing, remote env update, and compose commands.

## Live Release Evidence

PMA ran `/home/staticduo/git/release-litellm.sh` with `TAG=staticduo-gpt-lazymcp-main-20260610-mcp-delete-cleanup`.

Result:
- Upstream merge initially conflicted and was resolved in `/home/staticduo/git/litellm-production-main`.
- Merge commit: `218bd20690 merge: update staticduo production main from upstream`.
- Built and pushed `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260610-mcp-delete-cleanup`.
- Pushed stable tag `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-latest`.
- Created rollback tag `docker.staticduo.com/litellm:rollback-20260610-172427`.
- NAS `/volume2/docker/litellm` and Fedora `/home/staticduo/docker/litellm` both run the new image and report healthy.

Live log: `.staticeng/evidences/TASK-2026-06-10-002-update-release-script-fedora/logs/live-release.log`.
