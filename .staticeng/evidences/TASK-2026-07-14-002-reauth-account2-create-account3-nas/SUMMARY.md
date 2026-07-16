# NAS Account3 Setup Evidence

## Summary

Cloned all eight current NAS `chatgpt-account2/*` deployments to corresponding `chatgpt-account3/*` deployments and added matching OpenCode plugin overrides. All pre-existing deployments and unrelated OpenCode configuration were preserved.

## Work Performed

- Captured sanitized pre-change LiteLLM and OpenCode inventories
- Created missing account3 deployments idempotently through the LiteLLM admin API
- Retained each account2 deployment's physical provider model, settings, metadata, and pricing while selecting auth profile `account3`
- Backed up the NAS OpenCode config with mode `0600`
- Performed an atomic structured JSON edit that cloned account2 overrides and adapted only public `id` and `name` fields
- Validated deployment preservation, profile/settings/pricing parity, health endpoints, JSON parsing, and resolved OpenCode config
- Kept transient device-auth URLs and codes out of repository evidence
- Rotated the provider-invalidated account2 auth file to a timestamped mode-0600 backup after explicit authorization, then started one account2 device flow
- Did not complete either login

## Evidence

- `inventory-before.log`
- `setup.log`
- `validation.log`

## Open Risk

Account2 retained an existing non-expired local access token, but the provider had invalidated it. After explicit authorization, the invalid file was preserved as a secure same-directory backup and one account2 inference request started the requested device flow.

Account3 device authorization was started once and intentionally left incomplete. Its one inference request remained pending while the device flow awaited user authorization and was not retried.

## Post-Auth Verification

Both authorizations were subsequently completed outside the agent. Sanitized verification found both mode-0600 auth files with every required field present and non-empty. Exactly one no-retry request per account returned HTTP 200 and the distinct exact sentinel from the corresponding public Sol deployment. Account2 used its configured `account2` profile and account3 used its configured `account3` profile. No new device-code prompt appeared. Auth contents, token values, proxy credentials, account identifiers, response bodies, device URLs, and device codes were not persisted.
