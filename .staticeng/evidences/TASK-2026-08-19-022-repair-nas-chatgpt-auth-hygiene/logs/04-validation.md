# Validation

- Protected auth backup: PASS
- Live directory/file permission, ownership, type, and symlink checks: PASS
- Default supported refresh: PASS
- Account2 supported refresh: PASS
- Account3 supported refresh: FAIL, provider HTTP 401
- Default bounded direct Responses check: PASS, HTTP 200
- Account2 bounded direct Responses check: PASS WITH ALLOWED PROVIDER RESULT, HTTP 429 and no auth error
- Account3 direct check: NOT RUN because it would start another device flow after the deterministic refresh failure
- No pending account3 flow: FAIL; the production-held account3 lock persisted across two 15-minute observation boundaries and logs showed repeated device prompts
- NAS 1.92.0 health/readiness/liveliness: PASS
- Exact 40-model and three-profile registration preservation: PASS
- Fedora candidate health/identity: PASS
- Stable tag preservation: FAIL TO ESTABLISH; two read-only registry lookups returned not found
- `staticeng_validate`: FAIL on pre-existing broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps
- `staticeng_repair` dry run: reviewed; it proposed broad unrelated Markdown normalization and hundreds of CodeMap changes, so it was not applied

No automated check was skipped within the safe task boundary. The account3 inference check was intentionally not initiated because doing so would violate the explicit no-new/pending-device-flow safety requirement
