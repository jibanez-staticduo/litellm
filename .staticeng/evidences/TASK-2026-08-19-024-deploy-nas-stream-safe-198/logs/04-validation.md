# Validation

- Fresh just-in-time T0 gate: PASS on all three attempts
- Exact candidate manifest pull and selector: PASS
- Only NAS LiteLLM recreation: PASS
- Candidate final acceptance: FAIL, rolled back
- NAS rollback digest and 1.92.0 recovery: PASS
- NAS health/readiness/liveliness/restart/OOM: PASS
- Exact 32-model and 16-rule routing preservation: PASS
- Default/account2 topology and account3 quarantine: PASS
- Dependency identity and health preservation: PASS
- Protected wrapper/Compose rollback restoration: PASS
- Sanitized rollback logs: PASS, zero release-blocking matches
- Strict post-T0 credential metadata equality: FAIL, one salted lock path had recurring ctime-only drift
- Candidate Responses/Codex/LazyMCP gates: NOT RUN after mandatory stop
- Fedora candidate preservation: FAIL by design after aborted release; reverse rollback to pre-release digest PASS
- Stable mutation: PASS, none performed; inherited stable lookup remains not found
- `staticeng_validate`: FAIL on pre-existing broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps
- `staticeng_repair` dry run: reviewed but not applied because it proposed broad unrelated Markdown and CodeMap changes

Final decision: **REJECT CROSS-HOST PROMOTION**
