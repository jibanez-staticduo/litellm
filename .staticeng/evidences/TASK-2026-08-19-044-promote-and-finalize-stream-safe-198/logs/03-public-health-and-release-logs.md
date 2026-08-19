# Public, Health, And Release-Log Verification

## NAS

```json
{"check":"/health/readiness","status":200}
{"check":"/health/liveliness","status":200}
{"blocked_markers":[],"check":"public_gpt_5_6_sol","content_type":"text/event-stream","response_completed":1,"selected_header_present":true,"status":200}
{"auth_device":0,"migration_schema_patch":0,"standard_logging":0,"stream":0,"traceback":0,"usage_cache":0}
```

## Fedora

```json
{"check":"/health/readiness","status":200}
{"check":"/health/liveliness","status":200}
{"blocked_markers":[],"check":"public_gpt_5_6_sol","content_type":"text/event-stream","response_completed":1,"selected_header_present":true,"status":200}
{"auth_device":0,"migration_schema_patch":0,"standard_logging":0,"stream":0,"traceback":0,"usage_cache":0}
```

Each public request was bounded to one no-retry request with a 180-second timeout. Logs were scanned from `2026-08-19T06:30:00Z` after the final public checks
