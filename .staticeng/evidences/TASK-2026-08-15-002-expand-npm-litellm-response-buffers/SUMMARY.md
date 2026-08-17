# Evidence Summary

## Current Status

Both public LiteLLM proxy hosts are healthy with the Technical Architect-approved complete buffer set. Host 109 passed the complete canary sequence before host 62 was changed. Each hostname received exactly one bounded authenticated stateless Responses probe after its update; both returned HTTP 200 with response bodies discarded.

## Acceptance Criteria Coverage

- AC-1: Measured the successful Fedora-local response header block at 4,452 bytes total, with a largest field line of 445 bytes; no values or content retained
- AC-2: Established a 4,096-byte effective old host limit from the absence of host-specific directives and the NPM/OpenResty host memory page size
- AC-3: Passed. Both hosts use `proxy_buffer_size 32k`, `proxy_buffers 4 32k`, and `proxy_busy_buffers_size 64k`; host 62 retains all comments and 600-second timeouts, and host 109 retains its otherwise empty prior advanced configuration
- AC-4: Passed. Nginx configuration tests succeeded after each update, both generated host files and server blocks remain active, and both public readiness routes return HTTP 200
- AC-5: Passed. Exactly one bounded authenticated stateless `/v1/responses` probe per public hostname returned HTTP 200; both unauthenticated routing probes returned HTTP 401 and no new oversized-header errors appeared
- AC-6: Passed. Sanitized measurement, backup, effective-config inspection, outage/recovery, canary, rollout, and final verification evidence is present; no product documentation update is required

## Sensitive Data Handling

No API keys, authorization headers, cookies, response-header values, prompts, or response content were retained.
