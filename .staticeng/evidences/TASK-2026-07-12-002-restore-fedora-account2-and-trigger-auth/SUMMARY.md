# Fedora Account2 Restoration Evidence

## Summary

Restored seven Fedora LiteLLM `chatgpt-account2/*` deployments from their current regular counterparts and restored seven matching Fedora OpenCode plugin overrides. All pre-existing deployments and unrelated OpenCode settings were preserved.

## Work Performed

- Captured sanitized pre-change LiteLLM and OpenCode inventories
- Created missing deployments idempotently through `POST /model/new`
- Retained each regular deployment's physical provider model and full non-secret settings/pricing while adding `chatgpt_auth_profile: account2`
- Backed up the Fedora OpenCode config with mode `0600`
- Performed an atomic structured JSON edit that cloned each matching regular override and adapted only schema-level `id` and `name` fields
- Validated deployment preservation, profile/settings/pricing parity, endpoint health, JSON parsing, and resolved OpenCode config
- Kept the auth trigger and transient device-auth URL/code out of repository evidence
- Verified the completed authorization through one minimal Fedora-local account2 request without exposing credentials or auth-file contents
- Ran a no-retry QA dual-account smoke with one distinct harmless request per Sol deployment; account2 passed, while the regular account returned a sanitized rate-limit response

## Acceptance Criteria Coverage

- AC-1: PASS; seven account2 deployments exist, use profile `account2`, and match current regular physical models/settings/pricing
- AC-2: PASS; seven matching plugin overrides exist and all unrelated config is preserved
- AC-3: PASS; all 12 pre-existing deployments remain unchanged and health/model endpoints return HTTP 200
- AC-4: PASS; JSON parsing and `opencode debug config` succeed
- AC-5: PASS; post-authorization smoke returned HTTP 200 with the exact harmless sentinel and produced no new device-code prompt
- AC-6: PASS; authorization was completed by the user and no auth payload or secret was persisted in this packet
- AC-7: PASS; this setup/validation-only evidence packet exists at the required path

## Evidence

- `inventory-before.log`
- `setup.log`
- `validation.log`

## Documentation Impact

No product documentation changes are required.

## Open Risks

Existing long-running OpenCode processes retain startup-time configuration until restarted by their owner. No restart was performed because resolved config validation passed and this task did not request process disruption. The selected deployment was visible in request-scoped logs, but the selected auth profile was not emitted in available structured response headers or logs; profile selection remains supported by the earlier sanitized deployment configuration validation.

The final QA request to `chatgpt/gpt-5.6-sol` returned HTTP 429 due to rate limiting, so its exact sentinel could not be validated. It was not retried because QA was limited to exactly one request per account. The paired `chatgpt-account2/gpt-5.6-sol` request returned HTTP 200 with its exact sentinel, and neither request produced a new device-code prompt.

## Recommended Next Step

Close the task after PMA reviews the sanitized post-auth evidence.
