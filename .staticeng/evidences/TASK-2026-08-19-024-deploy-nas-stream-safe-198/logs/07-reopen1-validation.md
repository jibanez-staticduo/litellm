# Reopen 1 Validation

- Exactly one authorized controlled attempt: PASS
- Correct manifest/RepoDigests/config/local/running identity assertions: PASS
- Fresh T0 timing and sanitized auth-log gate: PASS
- Corrected three-lock ctime exception: PASS
- Candidate health/readiness/liveliness/restart/OOM: PASS
- Exact 32-model/routing/default/account2/account3-quarantine preservation: PASS
- Dependency, mount, and network preservation: PASS
- Native Responses request HTTP status: PASS, 200
- Native Responses body-format assertion: FAIL, harness expected JSON instead of the accepted native event lifecycle
- Remaining Codex and LazyMCP gates: NOT RUN after mandatory stop
- Automatic NAS rollback: PASS
- Ten-minute rollback observation and credential gate: PASS
- Fedora reopen baseline preservation: PASS
- Stable mutation: PASS, none performed
- Cross-host promotion decision: REJECT

No source tests were applicable because no application source changed. Repository StaticEng validation remains subject to the inherited broken links and missing CodeMaps recorded in the original evidence
