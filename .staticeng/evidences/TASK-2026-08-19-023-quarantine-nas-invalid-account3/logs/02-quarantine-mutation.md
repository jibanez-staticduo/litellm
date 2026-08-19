# Account3 Quarantine Mutation

## Supported Admin Operations

The running LiteLLM admin API was used for every active-state mutation

- Eight `POST /fallback` updates removed only the matching `chatgpt-account3/*` target and returned HTTP 200
- Eight `POST /model/delete` calls deleted only the protected account3 deployment IDs and returned HTTP 200
- No default, account2, unrelated deployment, unrelated fallback, credential, database service, Compose file, wrapper, image selector, or registry tag was changed

The resulting public chains preserve their prior remaining order:

- Seven public aliases retain account2 first and their default-qualified target second
- `gpt-5.6-sol` retains its prior default-qualified target first and account2 second

## Reload

Immediately before reload, the pre-existing account3 file lock was still held by the old device-auth request. Only the existing NAS LiteLLM container was restarted, without pulling or changing its image

- Image remained `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818`
- Image ID remained `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Health returned `running healthy` on the 16th two-second check
- Readiness and liveliness returned HTTP 200
- Account3 lock became acquirable after reload

Result: **PASS**
