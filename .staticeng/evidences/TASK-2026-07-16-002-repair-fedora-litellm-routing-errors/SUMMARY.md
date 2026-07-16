# Fedora LiteLLM Routing Repair

## Summary

Removed the stale Qwen alias from the active Fedora OpenClaw catalog and the NAS authoritative OpenCode configuration. The NAS structural edit removed the stale override and explicitly excluded that server-discovered invalid model, while preserving the intended deployed Qwen override and every unrelated setting. Normal Syncthing propagation updated Fedora without a local synchronization exception

Each Fedora ChatGPT profile received exactly one secret-safe no-retry health request. The regular and account2 Sol profiles both returned HTTP 200, so no reauthentication or token-file change was needed

## Work Performed

- Removed the exact stale override from the NAS authoritative OpenCode configuration using a parsed, fsynced, atomic JSON edit
- Added the same stale name to the LiteLLM plugin's `excludeModels` list because `/model/info` discovery would otherwise recreate it in resolved configuration after override removal
- Allowed normal Syncthing propagation to Fedora's unchanged `receiveonly` folder
- Removed only `litellm/qwen3.6-35b-a3b-uncensored-nvfp4` from the Fedora OpenClaw default model catalog
- Preserved the intended `qwen3.6-27b-aeon-ultimate-uncensored-multimodal-nvfp4-mtp` entries and all unrelated settings
- Restarted only the Fedora OpenCode, Defend OpenCode, and OpenClaw gateway user services so active processes loaded the corrected catalogs
- Searched active Fedora OpenCode, OpenClaw, Hermes, and user-systemd config/job surfaces; no active stale request source remains. Historical backups, memories, and inactive session records were not modified
- Did not alter LiteLLM deployments, authentication files, generic cooldown/retry policy, or context fallback policy

## Backups

- OpenCode: `/home/staticduo/.config/opencode/opencode.json.bak-TASK-2026-07-16-002-20260716T132505Z`
- OpenClaw: `/home/staticduo/.openclaw/openclaw.json.bak-TASK-2026-07-16-002-20260716T133311Z`
- NAS authoritative OpenCode: `/home/staticduo/.config/opencode/opencode.json.bak-TASK-2026-07-16-002-reopen1-20260716T143110Z`
- NAS intermediate resolved-catalog edit: `/home/staticduo/.config/opencode/opencode.json.bak-TASK-2026-07-16-002-reopen1-resolved-20260716T143509Z`

All backups are mode `0600`. Backup contents are not included in evidence

## Acceptance Criteria Coverage

- AC-1: PASS; NAS and Fedora resolved OpenCode catalogs have zero stale model entries, Fedora OpenClaw remains corrected, the intended override remains, and structural comparison confirms only the stale override removal and matching exclusion were added
- AC-2: PASS; the previously completed no-retry intended-Qwen request returned HTTP 200, and the post-propagation bounded verification window contains zero stale-alias log lines
- AC-3: PASS; exactly one no-retry health request per Fedora ChatGPT profile was made. `chatgpt/gpt-5.6-sol` returned HTTP 200 with response model `gpt-5.6-sol`; `chatgpt-account2/gpt-5.6-sol` returned HTTP 200 with response model `chatgpt-account2/gpt-5.6-sol`
- AC-4: PASS; neither profile returned 401 or requested device authorization, so reauthentication was unnecessary. No auth/token file was edited
- AC-5: PASS; readiness, liveliness, and model-info endpoints returned HTTP 200; all 19 deployments remain, and the container is healthy with zero restarts and no OOM
- AC-6: PASS; this summary and sanitized logs exist at the required evidence path

## Verification

- NAS and Fedora OpenCode JSON parsing and resolved `opencode debug config` validation passed
- NAS and Fedora resolved model catalogs contain zero stale Qwen model entries and retain the intended Qwen model
- Fedora remained a Syncthing `receiveonly` folder and received the authoritative change normally; no local exception was created
- OpenClaw JSON parsing and `config validate` passed
- OpenCode, Defend OpenCode, and OpenClaw gateway services are active
- Intended Qwen request: HTTP 200, one request, `num_retries: 0`
- Regular ChatGPT profile: HTTP 200, one request, `num_retries: 0`
- Account2 ChatGPT profile: HTTP 200, one request, `num_retries: 0`
- LiteLLM deployment count remains 19
- Live router policy remains `num_retries: 3`, `allowed_fails: 1`, `cooldown_time: 30`, with 19 fallback rules
- Post-propagation stale alias log lines from `2026-07-16T14:36:01Z` through `2026-07-16T14:37:13Z`: 0

## Evidence Files

- `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/logs/config-repair-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/logs/health-and-routing-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-16-002-repair-fedora-litellm-routing-errors/logs/bounded-verification-sanitized.log`

## Documentation Impact

No product documentation change is required. This evidence packet documents the Fedora repair and its approved NAS source-of-truth update

## Open Risks

Historical backups, archived memories, and inactive sessions still contain the old literal by design; they are not active request sources. A manually resumed old model-pinned session may require selecting a current model

## Recommended Next Step

PMA can close the task after reviewing the updated evidence. Do not repeat the already completed ChatGPT or intended-Qwen requests
