# NAS Invalid Account3 Quarantine

## Summary

Created an exact protected transactional backup, removed only account3 from eight active deployments and eight public fallback chains through supported admin APIs, and reloaded the unchanged NAS 1.92.0 container. Default, account2, public aliases, unrelated routing, credentials, Fedora, and registry state were preserved

The account3 lock released after reload. A 14-minute 58-second post-reload observation found zero account3, device-auth, or refresh-401 log matches. Final default, account2, and public checks all completed HTTP 200 without auth/device-flow errors. The normalized 32-model release baseline is recorded in `.staticeng/evidences/TASK-2026-08-19-023-quarantine-nas-invalid-account3/logs/04-release-baseline-and-observation.md`

## Work Performed

- Captured all eight account3 rows and the exact router-settings row in a protected owner-only backup with verified hashes and one atomic restore transaction
- Removed one account3 target from each affected public fallback chain while preserving every remaining target and its order
- Deleted only the eight account3 deployment IDs through `POST /model/delete`
- Restarted only the unchanged LiteLLM container to terminate the already-running device-auth request and load persistent state cleanly
- Verified zero account3 deployments/references, preserved default/account2 topology, three successful bounded Responses checks, health, and external candidate/registry preservation

## Acceptance Criteria Coverage

- **AC-1: PASS**. `.staticeng/evidences/TASK-2026-08-19-023-quarantine-nas-invalid-account3/logs/01-protected-backup.md` records the exact affected IDs, fallback scope, protected files, hashes, and atomic restoration procedure
- **AC-2: PASS**. All eight fallback updates and eight deployment deletes returned HTTP 200; live and persistent readback show zero account3 deployments and zero account3 fallback references
- **AC-3: PASS**. All eight public aliases retain their public default primary plus default/account2 qualified targets; eight default and eight account2 qualified deployments remain intact
- **AC-4: PASS**. The pre-existing account3 lock released on reload; 14 minutes 58 seconds of observation recorded zero account3/device-auth/refresh-401 activity
- **AC-5: PASS**. Default-qualified, account2-qualified, and public `gpt-5.6-sol` each returned HTTP 200 through exactly one `response.completed`, with no auth/device-flow error
- **AC-6: PASS**. NAS is healthy on unchanged 1.92.0; the normalized 32-model/routing baseline is captured; Fedora candidate and registry candidate are unchanged, and no tag was moved

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. This task changes NAS operational database routing only; task evidence is the steady operational record

## Open Risks

- Account3 remains provider-invalid and must not be restored to active routing before a separate user-assisted reauthorization succeeds
- The pre-existing missing `stable` registry tag remains unresolved and was not changed by this task
- Repository-wide StaticEng validation has pre-existing broken CodeMap links and missing maps outside this host-only task

## Recommended Next Step

PMA may use this exact 32-model baseline for the next NAS release gate. Keep account3 quarantined until a separately approved user-assisted reauthorization and restoration task passes
