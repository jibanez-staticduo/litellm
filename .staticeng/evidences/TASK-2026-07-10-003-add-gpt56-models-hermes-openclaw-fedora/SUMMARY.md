# Evidence Summary

## Summary

Fedora Hermes and OpenClaw now expose all six requested LiteLLM-backed GPT-5.6 model IDs. Both retain their GPT-5.5 defaults and `https://litellm.staticduo.com/v1` base URL. Existing model sets were verified as subsets of the post-update sets. Both gateways were restarted to load the catalog changes and are healthy.

## Work Performed

- Read the task frontmatter before operations
- Inspected only config paths, catalog schemas, model IDs, provider names, base URLs, defaults, counts, and non-secret service status
- Backed up both configs on Fedora with mode `0600`
- Added the six target IDs to Hermes provider `openclaw-litellm.models`
- Added the six target IDs to OpenClaw provider `litellm.models` and selectable `agents.defaults.models`
- Preserved unrelated settings, existing model entries, and defaults
- Parsed YAML/JSON and ran native validation and gateway status checks
- Restarted both gateways and verified active/running state
- Did not run account authentication, completion, or inference calls

## Acceptance Criteria Coverage

- AC-1 PASS: Hermes contains all six target models
- AC-2 PASS: OpenClaw provider and selectable catalogs contain all six target models
- AC-3 PASS: Hermes default remains `chatgpt/gpt-5.5`
- AC-4 PASS: OpenClaw default remains `litellm/chatgpt/gpt-5.5`
- AC-5 PASS: pre-existing model sets are subsets of post-update sets; unrelated settings were preserved by targeted structured edits
- AC-6 PASS: YAML/JSON parse, `hermes config check`, `hermes doctor`, `openclaw config validate`, native gateway status, and systemd health checks passed
- AC-7 PASS: backups and rollback commands are recorded without config contents
- AC-8 PASS: no account2 authentication or completion/inference calls were performed
- AC-9 PASS: this evidence packet contains `SUMMARY.md` and sanitized `logs/`

## Operational Details

Hermes config: `/home/staticduo/.hermes/config.yaml`

OpenClaw config: `/home/staticduo/.openclaw/openclaw.json`

Hermes backup: `/home/staticduo/.hermes/config.yaml.bak.TASK-2026-07-10-003.20260710T152203Z`

OpenClaw backup: `/home/staticduo/.openclaw/openclaw.json.bak.TASK-2026-07-10-003.20260710T152203Z`

Hermes provider model count: `18 -> 24`

OpenClaw provider model count: `12 -> 18`

OpenClaw selectable model count: `18 -> 24`

Restart occurred: yes

Post-restart Hermes gateway: active/running; native status exit 0

Post-restart OpenClaw gateway: active/running; native status exit 0

## Documentation Impact

No product or LiteLLM application documentation changed. Only this secret-safe operational evidence packet was added.

## Open Risks

Hermes doctor continues to report pre-existing non-blocking setup/provider warnings, including its generic warning about vendor-prefixed slugs with the custom provider. The configured catalog validates and the gateway is healthy. Per task safety requirements, model availability was not tested through real inference.

## Rollback

Exact commands are in `logs/rollback.txt`. Restore each mode-`0600` backup over its config, validate, restart the corresponding user service, and run the native gateway status command.

## Recommended Next Step

PMA can review the evidence packet and close the task. Any later functional smoke test should be separately authorized because this task explicitly prohibits real completion calls.
