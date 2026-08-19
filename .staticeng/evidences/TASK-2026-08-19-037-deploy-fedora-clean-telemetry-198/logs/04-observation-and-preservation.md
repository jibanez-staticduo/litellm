# Ten-Minute Observation And Preservation

- Candidate start: `2026-08-19T04:04:43.818876713Z`
- Final observation: `2026-08-19T04:15:12Z`
- Observed duration: 629 seconds
- The window spans approximately 62 ten-second background configuration/cache poll intervals
- Container identity and start time remained unchanged
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Redis: running / healthy

Sanitized candidate-log counts over the complete window:

- Missing/invalid `standard_logging_object` or `StandardLoggingPayload`: 0
- Success callback or success handler tracebacks: 0
- `resolved_usage_cache` or usage-cache NameErrors: 0
- Cache-settings poller errors: 0
- `Stream must be set to true`: 0
- Authentication/device-flow errors: 0
- Migration/schema/patch errors: 0
- `response.failed`: 0
- Generic Python tracebacks: 0

Final preservation:

- Model rows/projection: 27 / exact preflight match
- Default-qualified/account2-qualified rows: 7 / 7
- Router projection/fallback count/cross-profile policy: exact preflight match / 24 / true
- Five-file credential metadata projection: exact preflight match
- Non-image environment projection and all protected hashes: exact preflight match
- Unrelated services, dependency identities, 47-container count, mounts, and networks: exact preflight match
- Rollback manifest remained locally resolvable

Result: **PASS**
