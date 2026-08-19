# Reopen 2 Validation

- Exactly one final authorized deployment attempt: PASS
- Fresh T0 and corrected credential gate: PASS
- Manifest/config/local/running identity gates: PASS
- Candidate health/topology/dependencies/mounts/networks: PASS
- Native client `stream=false` Content-Type-driven SSE lifecycle: PASS
- Direct default Codex SSE lifecycle/profile gate: PASS
- Direct account2 Codex gate: FAIL, HTTP 429 instead of HTTP 200
- Public Codex gate: NOT RUN after mandatory stop
- LazyMCP status/describe/list/harmless tool: NOT RUN after mandatory stop
- Candidate 10-minute observation: NOT RUN after mandatory stop
- Automatic NAS rollback: PASS
- Rollback 10-minute observation and corrected credential gate: PASS
- Fedora isolation: PASS
- Stable mutation: PASS, none performed
- Cross-host promotion: REJECT

No source tests were applicable because no application source changed. `staticeng_validate` remains blocked by inherited broken links and repository-wide missing CodeMaps; broad repair remains outside this task
