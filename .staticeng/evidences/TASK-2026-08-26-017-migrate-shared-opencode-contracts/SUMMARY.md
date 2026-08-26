# TASK-2026-08-26-017 Evidence Summary

## Result

ROLLED BACK after Reopen 4. The NAS-only candidate and final connected-set convergence passed, but the first required fresh official OpenCode package/version gate failed. The exact protected backup was restored atomically and converged to every still-connected peer

Reopen 4 used the approved stable final-connected-set rule. Six connected expected peers passed preflight and post-mutation stabilization at 100%, with matching candidate checksums and no conflicts. Stale unversioned plugin cache state was removed only on NAS and six reachable connected hosts. Fresh official OpenCode `1.18.23` then failed to load published `@staticeng/opencode-litellm@0.2.0`: plugin initialization raised `models.filter is not a function`, model discovery exited nonzero, and no resolved `0.2.0` installation remained. This is a package/runtime behavior failure and triggered required rollback before selector or wire probes

## Acceptance Criteria Coverage

- **T3-AC-1: ROLLED BACK.** Protected mode-`0600` exact backup created; candidate removed exactly 25 approved keys; whole-object restoration comparison proved unrelated paths unchanged; exact backup restored after package failure
- **T3-AC-2: ROLLED BACK.** Candidate parsed, retained exact unversioned `@staticeng/opencode-litellm`, contained no `file://` reference, and remained mode `0600`; prior valid file restored
- **T3-AC-3: PASS for candidate and rollback.** NAS was sole writer. All six peers connected at the end of each stabilization window reached 100%, matching checksum, zero need, zero errors, and zero conflicts
- **T3-AC-4: FAIL/ROLLED BACK.** Only stale unversioned plugin cache state was invalidated on seven reachable hosts. Fresh official OpenCode failed plugin initialization and did not prove installed `0.2.0`
- **T3-AC-5: PASS for safety.** No control, pre-existing, or unrelated session was terminated. Fresh short-lived official commands were isolated and exited; pre-existing processes require user restart only after a successful future rollout
- **T3-AC-6: BLOCKED.** Selector validation could not begin because the official runtime package gate failed
- **T3-AC-7: BLOCKED.** Wire/default/override matrix could not begin because the official runtime package gate failed
- **T3-AC-8: PASS.** Evidence contains no credentials, prompts, responses, raw configuration, device IDs, addresses, protected checksums, or backup path

## Verification

- Fresh preflight: NAS send-only/idle/error-free; six connected expected peers complete, checksum-aligned, mode `0600`, JSON-valid, and conflict-free
- Backup: exact, protected mode `0600`, outside synchronized tree, file-fsynced
- Candidate: NAS-only atomic rename, JSON parse, file and directory fsync, mode `0600`
- Cleanup: 25 approved overrides removed; 5 unrelated overrides preserved; full unrelated structure comparison passed
- Final connected set: six peers; all 100%, matching candidate checksum, zero conflicts/errors
- Cache scope: only stale unversioned `@staticeng/opencode-litellm` package cache directory on NAS and six reachable connected hosts
- Official runtime: OpenCode `1.18.23`; fresh model command failed with plugin initialization type error; installed `0.2.0` proof failed
- Selector/wire matrix: not executed after mandatory package gate failure
- Rollback: exact backup restored atomically from NAS; file and directory fsync; mode `0600`
- Post-rollback: NAS idle/error-free; six final connected peers 100%, matching prior checksum, zero conflicts
- Cache cleanup after rollback: no candidate cache remained
- Process termination count: zero
- Peer direct configuration edit count: zero
- Codex/LiteLLM registry edit count: zero
- `staticeng_validate`: remains blocked by the pre-existing repository-wide manual CodeMap backlog recorded in `logs/02-staticeng-validation.log`

See `logs/06-reopen4-package-failure-rollback.log` for the redacted execution sequence

## Documentation Impact

No steady-state product or architecture documentation was changed because the candidate was rolled back. Task and evidence document the runtime incompatibility requiring package remediation

## Open Risks

Published plugin `0.2.0` is not loadable in the live official OpenCode `1.18.23` environment with the production discovery response shape. The release evidence used an isolated fixture path that did not expose this runtime `models.filter` failure. Retrying configuration rollout without a corrected published package will fail again

Offline expected peers remain untouched and will automatically receive the currently restored NAS configuration when they reconnect

## Recommended Next Step

PMA should reopen the plugin implementation/release work to reproduce the official `models.filter is not a function` failure against the production discovery response shape, publish a corrected package under the approved versioning process, and verify it with fresh official OpenCode before reopening this migration
