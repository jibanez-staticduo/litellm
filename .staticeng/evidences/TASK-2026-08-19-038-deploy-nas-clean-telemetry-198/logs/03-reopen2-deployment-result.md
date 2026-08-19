# Reopen 2 Deployment Result

- Attempt: `nas-clean-20260819T044435Z`
- Root/staticduo shared-daemon identity: PASS
- Root/staticduo exact local replacement identity: PASS
- Registry pull: correctly skipped
- Fresh baseline and rollback: PASS
- Replacement manifest/config: `35fc5209...f2d3` / `9975f878...c9a3a`
- NAS-only recreation with `--no-deps`: PASS
- Candidate identity and immediate health: PASS
- Native client `stream=false`: sequential assertion passed
- Direct default: sequential assertion passed
- Approved account2 gate: sequential assertion passed
- Public `gpt-5.6-sol` default-primary: FAIL, selection-or-blocked-error predicate
- Public response retained: no
- LazyMCP: not run after mandatory stop
- Candidate ten-minute observation: not run after mandatory stop
- Automatic rollback: PASS

Result: **RELEASE REJECTED AND ROLLED BACK**
