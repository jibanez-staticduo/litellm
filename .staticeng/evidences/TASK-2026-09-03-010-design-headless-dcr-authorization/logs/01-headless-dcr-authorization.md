# Headless DCR Authorization Design

## Decision

The candidate supports one non-browser client procedure, but it does not support non-interactive principal authorization. DCR registration, PKCE generation, token redemption, audience proof, and cleanup can run headlessly on Fedora. The principal step still requires a valid LiteLLM UI `token` cookie and deliberate consent at `/authorize/complete`

The supported way to remove an external browser dependency is an HTTP session process running entirely on Fedora. It signs the existing principal in through the normal username/password UI endpoint, keeps cookies only in process memory or an owner-only cookie jar, follows `/authorize`, and explicitly posts the flow handle to `/authorize/complete`. This remains authorization-code plus PKCE S256. It does not replace consent with an API key or call an internal helper

This procedure is executable only if the secret owner confirms the existing principal has normal username/password credentials available by secret name. Fedora Compose references `UI_USERNAME` and `UI_PASSWORD`, so that shape exists without reading values. If the intended existing principal is OIDC-only, or those names are unavailable to the operator, the product has no supported non-interactive DCR authorization grant and the attempt must roll back by T+7

## Source And Test Trace

### Registration

`POST /register` is public and stateless. A request carrying `redirect_uris` routes to `register_aggregate_client()`. The server seals the registered redirects into an `llm_dcrc_` client identifier, forces `token_endpoint_auth_method: none`, and returns authorization-code plus refresh grants. It never issues a client secret. Registration validates HTTPS, loopback HTTP, or an allowlisted native callback and bounds redirect count and size

Evidence: `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py:2761`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:305`, and `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:96`

### Authorization And Principal Authentication

`GET /authorize` recognizes only a registered `llm_dcrc_` client at the root route. It validates the exact registered redirect, `response_type=code`, a PKCE challenge, and `code_challenge_method=S256`. For the exact LazyMCP resource it parses and seals the canonical resource. Malformed LazyMCP-shaped targets fail with `invalid_target`

Principal identity comes only from `_session_cookie_user_id(request)`. That helper reads the `token` cookie, verifies its HS256 signature with the configured master key, requires `exp`, requires `login_method` equal to `sso` or `username_password`, rejects BYOK session tokens, and returns a non-empty `user_id`. `/authorize` does not inspect `Authorization`, `x-litellm-api-key`, a master key, a service-account key, or a gateway session bearer

With no accepted cookie, `/authorize` returns a 303 to `/sso/key/generate` with the same-origin relative authorize request in `return_to`. A valid cookie creates a 600-second sealed flow cookie and redirects to `/ui/connect`; it does not mint a code

Evidence: `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py:346`, `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py:1766`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:435`, `litellm/proxy/_experimental/mcp_server/byok_oauth_endpoints.py:85`, `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:202`, and `tests/test_litellm/proxy/auth/test_login_utils.py:582`

### Consent Completion

`POST /authorize/complete` is public at the router but authorization is bound to two cookies and an explicit POST. It requires the flow handle, the matching HttpOnly flow cookie, and the same valid UI `token` cookie. The signed-in `user_id` must exactly match the principal sealed at `/authorize`. The flow is atomically single-use. Approval mints a client-, redirect-, PKCE-, principal-, and exact-resource-bound code; a loopback flow with `delivery=manual` renders a no-store callback URL and grants a 300-second code lifetime

The dashboard proves the intended consent contract: its `Finish connecting` button is the consent gate and the source expressly prohibits auto-finish. A headless HTTP client may submit the same explicit form as the existing principal, but it must do so as a deliberate operator action. A scheduled or unattended auto-approval would weaken the supported contract and is prohibited

Evidence: `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py:1916`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:700`, `ui/litellm-dashboard/src/components/chat/ConnectFlowBanner.tsx:18`, and `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:640`

### Token And Live Principal

`POST /token` routes an `llm_dcrc_` client to `aggregate_token()`. An authorization-code grant requires the code, same redirect, same client identifier, a 43 to 128 character verifier, and the same exact LazyMCP `resource`. Missing or changed resource, wrong verifier, wrong client, wrong redirect, expiry, and replay fail closed. Before minting, the server reloads the user from the database and rejects a missing or SCIM-deactivated principal

The result is an identity-only MCP access token with a 3600-second lifetime and a 14-day rotating refresh token. Both carry the exact resource. Admission compares that claim against the original public transport path before live user and policy resolution. The exact audience is a ceiling, not a grant; current user, team, organization, IP, toolset, server, and tool policy still applies

Evidence: `litellm/proxy/_experimental/mcp_server/discoverable_endpoints.py:1846`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:1040`, `litellm/proxy/_experimental/mcp_server/gateway_dcr_flow.py:1166`, `litellm/proxy/_experimental/mcp_server/bridge_token_flow.py:184`, `litellm/proxy/_experimental/mcp_server/outbound_credentials/session_token.py:64`, `litellm/proxy/_experimental/mcp_server/auth/user_api_key_auth_mcp.py:918`, and `tests/test_litellm/proxy/_experimental/mcp_server/test_gateway_dcr_flow.py:931`

## Existing Credential Disposition

| Existing shape | Supported for DCR principal step | Reason |
| --- | --- | --- |
| Legacy API key or `LITELLM_STATICDUO_API_KEY` | No | `/authorize` and `/authorize/complete` ignore authorization headers. A legacy key also has no exact LazyMCP resource claim |
| `LITELLM_MASTER_KEY` | No direct grant | It is server signing/configuration material and may be the fallback UI password only when `UI_PASSWORD` is absent. Fedora Compose explicitly references `UI_PASSWORD`, so do not assume or substitute the master key |
| OnePassword service account | No | The mounted service-account token is for secret retrieval. It is neither parsed as a UI session nor accepted as DCR consent |
| Gateway access or refresh session | No | MCP session tokens are rejected by the UI-cookie reader because they lack a UI login method and use a distinct token family |
| Existing UI `token` cookie | Yes, while valid | It is the exact principal format required by both authorization endpoints, but obtaining or reusing it is bearer-cookie handling, not a header-key shortcut |
| `UI_USERNAME` plus `UI_PASSWORD` | Yes | `POST /login` and `POST /v2/login` authenticate this existing principal and mint the required bounded UI session cookie. `/v2/login` returns the cookie token in JSON, so use `/login` to avoid duplicating it in a response body |
| Existing database user email plus password | Yes | The same username/password login path authenticates an existing DB user and mints the required UI cookie. It must already own the needed toolset permissions |
| Generic OIDC client credentials | No | They configure interactive OIDC redirects. No resource-owner, client-credentials, device-code, token-exchange, or API-key-to-UI-cookie grant feeds the DCR principal step |

## Secret-Name And Shape-Only Fedora Topology

A read-only inspection on 2026-09-04 found the healthy rollback container and did not read any value. Compose references the auth-related names `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `LITELLM_STATICDUO_API_KEY`, `UI_USERNAME`, `UI_PASSWORD`, `GENERIC_CLIENT_ID`, `GENERIC_CLIENT_SECRET`, `GENERIC_AUTHORIZATION_ENDPOINT`, `GENERIC_TOKEN_ENDPOINT`, `GENERIC_USERINFO_ENDPOINT`, `GENERIC_SCOPE`, `GENERIC_USER_EXTRA_ATTRIBUTES`, and `DATABASE_URL`

The runtime container exposes names for `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `LITELLM_STATICDUO_API_KEY`, and `DATABASE_URL`. Compose resolves the UI and Generic OIDC names before container creation, so absence from `docker inspect` does not mean the values are unavailable at Compose execution. The host has read-only mounts named `/run/secrets/op_service_account_token` and `/run/secrets/litellm_loopback_oauth_relay`; only path, file type, ownership, mode, and size were observed. No value, cookie, token, key, password, configuration body, or database row was read

The topology supports a normal username/password login route and a Generic OIDC route. It does not prove that the intended toolset-authorized user corresponds to `UI_USERNAME`, that the secret owner will permit non-interactive use, or that a password exists for an OIDC-only user. Those are execution preconditions for PMA and the secret owner, not facts this read-only task may infer

## Executable Fedora-Only Procedure

This is a protocol procedure, not a ready-to-run shell paste. The Tech Lead should use one reviewed local client process so secrets never become command arguments and so response bodies containing credentials never enter a general command pipeline

1. Complete TASK-007 Phase 0, including a fresh backup and restore proof, exact rollback unit, and all independent watchers. Confirm the candidate selector is still the frozen digest and the four-hour amendment still applies
2. Before selector mutation, create an empty owner-only task directory under `/run/user/1000`, require tmpfs ownership by UID 1000 and mode `0700`, set `umask 077`, disable tracing and core dumps, and pre-register cleanup traps. The client must use files created with exclusive semantics at mode `0600`, reject symlinks, and log only allowlisted booleans, status classes, and times
3. The secret owner must select one existing toolset-authorized principal. Prefer a dedicated existing database user with a password over the proxy-admin UI account. Authorize the client to read only that username and password from owner-only files or dedicated inherited file descriptors. If only OIDC login exists, stop because there is no supported non-interactive principal grant
4. Arm TASK-007 watchers, capture the baseline, deploy the exact candidate, and require all identity, migration, health, discovery, and metadata gates by T+3/T+4. No auth request occurs on rollback
5. The Fedora client generates state and a 43 to 128 character high-entropy verifier internally and derives the S256 challenge. It registers one `http://127.0.0.1:<ephemeral>/callback` public client at `/register`, requiring HTTP 201, `token_endpoint_auth_method=none`, exact redirect echo, and no client secret
6. In one cookie session, form-POST the existing username/password to `/login`, with the values read from inherited file descriptors or stdin. Do not use `/v2/login`, because it repeats the UI session token in JSON. Require only a 303 and a `token` cookie in the protected jar. Do not record `Set-Cookie`, response bodies, or redirects containing credentials
7. In the same cookie session, GET `/authorize` with `response_type=code`, the registered client identifier, redirect, unpredictable state, S256 challenge, and exact `https://litellm.defend.tech/toolset/defend_memory/lazymcp` resource. Require a 303 to `/ui/connect`, a new HttpOnly flow cookie, and no redirect to `/sso/key/generate`
8. Treat the next operation as the explicit consent event. The operator confirms the intended principal and exact client origin, then instructs the local process once to POST `/authorize/complete` with the flow handle and `delivery=manual`. The process must not schedule, retry, or auto-submit this POST. Require HTTP 200 no-store. Parse the callback URL only in memory, verify exact loopback scheme/host/port/path and constant-time state equality, then write only the code to its owner-only file
9. Form-POST `/token` with `grant_type=authorization_code`, code, same redirect, same client identifier, verifier, and the exact resource. Omit client secret. Require HTTP 200, Bearer, and `0 < expires_in <= 3600`. Split access and refresh tokens directly into separate mode-`0600` files; never print the response or persist its raw body
10. Run TASK-009's serial audience proof with retries and redirects disabled: exact toolset `initialize` must pass OAuth and MCP; the same bearer at `/lazymcp`, one preselected distinct `/lazymcp/{scope}`, and `/mcp` must each return 401 `invalid_token`. Retain status and class only. Any ambiguity or broader admission triggers cleanup and rollback
11. The bearer must be fully audience-proven by T+7. Finalize TASK-007's 30-second baseline and immediately run its single 75-second diagnostic call. No second auth attempt, second principal, refresh, or unrelated probe is permitted
12. On completion or any stop condition, revoke the refresh token at `/revoke` using protected file input, delete the UI session virtual key at `/key/delete` using the session key held only inside the UI cookie when a supported owner-authorized request can do so, clear the cookie jar, unlink all OAuth/login/request artifacts, and verify the workspace paths are absent. Never delay mandatory rollback for revocation or UI-key deletion

The UI JWT cookie itself has no server-side revocation endpoint. Clearing it only removes the local copy. Deleting the embedded short-lived UI virtual key prevents its management use, while DCR admission separately revalidates the user. If safe self-deletion of the UI key cannot be completed, destroy the cookie and record the bounded UI session expiry as a residual credential lifetime; do not use the master key to clean it up within this flow

## Timing And Stop Conditions

TASK-009 timing remains unchanged. Candidate deployment is T+0, candidate health completes by T+3, discovery and DCR registration by T+4, username/password session creation plus authorization and explicit consent by T+6, redemption and audience proof by T+6:30, and bearer readiness by T+7. The exact diagnostic call follows immediately

The external-browser dependency is removed, but the principal and deliberate-consent requirements are not. Stop and roll back without a diagnostic request when any of these is true: secret-owner approval is absent; the selected user lacks an existing password or toolset authorization; login redirects to OIDC or fails; the UI cookie cannot be retained without output; `/authorize` asks for login again; consent cannot be explicitly confirmed; exact resource binding changes; the bearer is not proven by T+7; or any TASK-007 watchdog gate fires

Cleanup runs on normal exit, error, signal, deadline, or rollback. Access tokens cannot be individually revoked and expire within one hour. Refresh tokens must be burned when the candidate is responsive, then destroyed regardless of revocation outcome. A failed refresh revocation leaves a maximum 14-day renewal capability and requires PMA notification. The candidate must not remain deployed merely to finish cleanup

## Execution Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-010 PASS WITH EXECUTION PRECONDITION. Candidate source supports a Fedora-only HTTP-session client that uses the normal `/login` username/password path to mint the exact UI cookie required by `/authorize` and `/authorize/complete`; public DCR, S256 PKCE, exact resource redemption, audience proof, T+7, watchdog, revocation, and destruction remain unchanged. API keys, the master key as a bearer, service-account tokens, gateway sessions, and OIDC client credentials cannot authorize this flow. Before reopening TASK-006, the secret owner must confirm one existing toolset-authorized username/password principal and provide only owner-only files or inherited file descriptors. The operator must explicitly approve the one `/authorize/complete` POST. If the principal is OIDC-only, approval is absent, or the exact bearer is not audience-proven by T+7, clean up and roll back without the diagnostic call. No authorization, secret value access, deployment, source/config/database/container mutation, or NAS access occurred
