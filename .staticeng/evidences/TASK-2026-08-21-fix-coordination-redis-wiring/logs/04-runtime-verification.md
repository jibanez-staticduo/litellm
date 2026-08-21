# Runtime Verification

- `GET /health/readiness`: HTTP 200
- Authorized `GET /cache/ping`: HTTP 200; Redis reported healthy
- Authorized `GET /coordination_redis/settings`: HTTP 200; source `cache_backend`; password, sentinel password, and URL values not exposed
- Unauthenticated `GET /coordination_redis/settings`: HTTP 401
- Representative existing route: `POST /v1/responses` using `gpt-5.5`, stateless request; HTTP 200 with response body
- Post-deploy startup logs: no `NameError` involving `get_persisted_coordination_redis_settings`
- Post-deploy startup logs: no `Could not read coordination_redis from the database` warning
- Post-deploy startup logs: no persisted coordination target initialization error
- No credentials, request output, response content, authorization headers, or secret values retained
