# Fedora Codex Provider Repair

## Summary

Started only the inactive `codex-optima.service` on Fedora. The service is active, its control-plane process owns `127.0.0.1:34160`, and both local health endpoints pass

Exactly one bounded client request was sent to the loopback Responses endpoint with the existing command-backed auth helper. Client retries and requested LiteLLM retries were both zero. The SSE request returned HTTP 200 and emitted a completion event; no secret, prompt, or response content was printed or retained

## Work Performed

- Confirmed the service was inactive and port `34160` had no listener
- Reviewed the existing unit and lifecycle journal without changing configuration or credentials
- Started only `codex-optima.service`
- Verified listener ownership, `/healthz`, `/readyz`, and LiteLLM readiness/liveliness
- Sent exactly one bounded no-retry request through `127.0.0.1:34160/model-provider/v1/responses`
- Confirmed the corresponding HTTP 200 `/v1/responses` access in the LiteLLM container log
- Made no configuration, credential, app-server, or container changes

## Acceptance Criteria Coverage

- AC-1: PASS; `codex-optima.service` is active and its process owns `127.0.0.1:34160`
- AC-2: PASS; provider `/healthz` and `/readyz` returned HTTP 200, LiteLLM readiness and liveliness returned HTTP 200, and the LiteLLM container remained healthy
- AC-3: PASS; exactly one bounded request used the existing auth helper with client retries disabled and `num_retries=0`; it returned an HTTP 200 SSE completion and correlates to an HTTP 200 LiteLLM `/v1/responses` access
- AC-4: PASS; the running Codex app-server and LiteLLM container were not restarted or reconfigured, and no credential or configuration file was edited
- AC-5: PASS; this summary and the sanitized logs trace AC-1 through AC-4 without request or response content, secrets, or authorization values
- AC-6: PASS; no product documentation change is required; this operational evidence records service ownership and recovery

## Verification

- Provider service: `active`, `running`, result `success`, restart count `0` after the explicit start
- Listener: one loopback listener on `127.0.0.1:34160`, owned by the service process
- Provider health: `/healthz` HTTP 200; `/readyz` HTTP 200
- LiteLLM: container `07f2bfc52cfb` remained healthy; readiness HTTP 200; liveliness HTTP 200
- Request: count `1`; client retries `0`; requested retries `0`; HTTP 200; SSE completion observed; bounded duration 3.406 seconds
- LiteLLM access: `POST /v1/responses` HTTP 200 at `2026-07-18T06:42:35.786323769Z`, within the bounded request window

## Evidence Files

- `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/logs/01-service-recovery-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/logs/02-health-and-preservation-sanitized.log`
- `.staticeng/evidences/TASK-2026-07-18-002-repair-fedora-codex-provider/logs/03-single-response-request-sanitized.log`

## Documentation Impact

No product documentation change is required. The existing runtime documentation already describes the private loopback provider; this evidence closes the operational service-recovery impact explicitly

## Open Risks

The earlier SIGTERM was a clean external stop and its initiator is not identified by the available user journal. The bounded scope did not broaden into lifecycle redesign. A separate earlier transient upstream socket termination remains outside this repair because the restarted service and end-to-end request are healthy

## Recommended Next Step

PMA can send the evidence packet to QA. Do not repeat the completed inference request
