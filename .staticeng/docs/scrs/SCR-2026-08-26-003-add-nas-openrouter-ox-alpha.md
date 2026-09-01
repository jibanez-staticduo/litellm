---
id: SCR-2026-08-26-003-add-nas-openrouter-ox-alpha
status: implemented
requested_by: user
approved_by: user
date: 2026-08-26
---

# SCR: Add NAS OpenRouter ox-alpha

## Requested Behavior
- Register OpenRouter model `stealth/ox-alpha` in the NAS LiteLLM PostgreSQL-backed registry under public alias `ox-alpha`.
- Store the OpenRouter API key as a named LiteLLM credential sourced from the 1Password item `openroute` without exposing or persisting the secret outside supported secret storage.
- Make the model discoverable to OpenCode only through the existing `LiteLLM` provider as `LiteLLM/ox-alpha`.

## Constraints
- NAS only; do not change Fedora.
- Use LazyMCP `litellm_admin` and the 1Password MCP rather than direct database or deployment-file edits.
- Do not modify LiteLLM, OpenCode, or repository configuration unless dynamic OpenCode discovery is proven insufficient.
- Do not execute inference requests.
- Stop on an existing conflicting credential, alias, duplicate deployment, unsupported API contract, or inability to retrieve the secret safely.

## Numbered Acceptance Criteria
- **AC-1:** LiteLLM health remains healthy with PostgreSQL connected.
- **AC-2:** Exactly one named OpenRouter credential is present and its returned secret is redacted.
- **AC-3:** Exactly one `ox-alpha` deployment points to `openrouter/stealth/ox-alpha` and references the named OpenRouter credential.
- **AC-4:** No unrelated model, alias, fallback, credential, or MCP registration changes.
- **AC-5:** A fresh OpenCode process discovers `LiteLLM/ox-alpha` without direct OpenRouter configuration or inference.
- **AC-6:** Evidence maps AC-1 through AC-5, contains no secret values or authorization material, and records rollback identifiers.

## Approval
Approved by the user on 2026-08-26 through the approved execution plan.

## Implementation Status
Implemented and independently approved on 2026-08-26. Exactly one named `openrouter` credential and one DB-backed `ox-alpha` deployment were created, and fresh OpenCode discovery exposed `LiteLLM/ox-alpha` without inference

The implementation task was reopened twice before completion. The first reopen followed confirmation that the 1Password item was accessible; execution reblocked when two populated concealed fields made the API-key source ambiguous. The second reopen followed confirmation that the API key was in the concealed custom field titled exactly `key:`. These historical blocked outcomes remain recorded in the task reopen history
