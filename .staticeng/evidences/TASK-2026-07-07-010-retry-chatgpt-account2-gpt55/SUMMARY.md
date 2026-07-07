# TASK-2026-07-07-010 Evidence Summary

## Result

Attempted one minimal smoke request against `chatgpt-account2/gpt-5.5` on the local/NAS LiteLLM container. The request reached LiteLLM but failed with HTTP 500.

## Smoke request

- Target container: `litellm`
- Endpoint: `POST http://127.0.0.1:4000/v1/chat/completions` from inside the container
- Model: `chatgpt-account2/gpt-5.5`
- Prompt: `Reply with exactly: ok-account2`
- Secret handling: proxy key was read only from the container environment inside the command and was not printed

## Sanitized outcome

Failure. Sanitized non-secret reason: `litellm.APIConnectionError: APIConnectionError: ChatgptException - Unknown items in responses API response: []`. LiteLLM also reported no fallback model group for the requested model.

No device-code URL, login code, master key, API key, token, cookie, private key, auth file, refresh token, session token, or database connection string was written here.

## Acceptance Criteria

- AC-1: Passed. A request to `chatgpt-account2/gpt-5.5` was attempted.
- AC-2: Passed. The result is reported as failure with a sanitized non-secret reason.
- AC-3: Passed. This evidence file contains no secrets or raw provider response.

## Notes and risks

- This retry did not confirm a successful account2 response.
- The failure matches the prior smoke symptom: ChatGPT response parsing received an empty Responses API item list.
