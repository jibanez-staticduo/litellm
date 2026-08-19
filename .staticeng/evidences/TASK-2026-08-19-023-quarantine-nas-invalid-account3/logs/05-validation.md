# Validation

- Protected backup row counts, modes, owners, and hashes: PASS
- Exact restore transaction dry run with final rollback: PASS
- Eight supported fallback updates: PASS, HTTP 200 each
- Eight supported deployment deletes: PASS, HTTP 200 each
- Persistent/live account3 rows and fallback references: PASS, 0 and 0
- Eight public default-profile primaries: PASS
- Eight default-qualified and eight account2-qualified deployments: PASS
- Final default/account2/public Responses gates: PASS, HTTP 200 and one `response.completed` each
- Post-reload device-auth observation: PASS, 14 minutes 58 seconds with zero account3/device/refresh-401 log matches and free account3 lock
- NAS health/readiness/liveliness: PASS
- Fedora candidate and candidate registry preservation: PASS
- Stable tag unchanged from parent missing state: PASS WITH CARRIED RISK
- Source tests/build: NOT APPLICABLE, no source or deployment artifact changed
- `staticeng_validate`: FAIL on pre-existing broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps
- `staticeng_repair` dry run: reviewed and not applied because it proposed broad unrelated Markdown normalization and hundreds of CodeMap changes

No safe task-scoped automated check failed or was skipped. StaticEng repository validation remains an inherited repository-wide blocker outside this host-only quarantine task
