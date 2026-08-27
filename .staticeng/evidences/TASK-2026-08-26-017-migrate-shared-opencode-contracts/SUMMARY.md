# TASK-2026-08-26-017 Evidence Summary

## Result

ROLLED BACK after Reopen 5 because the fresh NAS configuration backup initially inherited mode `0777` from the ACL/default-create environment instead of the required `0600`. The backup was immediately corrected to `0600`, the exact prior configuration was restored atomically, and the migration stopped before Syncthing candidate propagation or functional matrix execution

The requested duplicate-cache cleanup succeeded and remains active because package `0.2.1` is healthy. On NAS and seven reachable stable connected hosts, every cache tree whose package identity was exactly `@staticeng/opencode-litellm` was inventoried and protected, stale/duplicate trees were removed, and fresh official OpenCode processes built exactly one current `@latest` cache tree resolving spec/version `0.2.1`. Linux hosts ran official OpenCode `1.18.23`; ProArt ran its installed official `1.18.4`. All returned model discovery success, package-lock integrity matched live npm metadata, and unrelated caches were untouched

## Acceptance Criteria Coverage

- **T3-AC-1: FAIL/ROLLED BACK.** The exact candidate cleanup and unrelated-structure comparison passed, but the fresh backup mode gate initially failed (`0777`). Backup mode was corrected and exact rollback completed before candidate propagation
- **T3-AC-2: CANDIDATE PASS/ROLLED BACK.** Candidate parsed, retained exact unversioned `@staticeng/opencode-litellm`, had zero `file://` references, and mode `0600`; prior configuration was restored due backup protection failure
- **T3-AC-3: PASS for preflight and rollback.** NAS was authoritative/idle/error-free; eight connected expected peers were 100% complete with no need. Post-rollback NAS is idle/error-free and no peer was directly edited
- **T3-AC-4: PASS for corrective `0.2.1` scope.** NAS and seven reachable peers each retain exactly one current cache tree, spec/version `0.2.1`, integrity matching live npm metadata, and successful fresh official OpenCode model initialization
- **T3-AC-5: PASS for safety.** No rollout-control or unrelated OpenCode process was terminated. Pre-existing long-running OpenCode processes were recorded and require user restart after a future successful configuration migration
- **T3-AC-6: BLOCKED.** Selector/retirement/Spark matrix did not run after the mandatory backup mode failure
- **T3-AC-7: BLOCKED.** Default/wire/override matrix did not run after the mandatory backup mode failure
- **T3-AC-8: PASS.** Evidence contains no credentials, prompts, responses, raw configuration, device IDs, addresses, protected checksums, or backup locations

## Verification

- Npm live metadata: latest `0.2.1`; integrity and shasum present
- Preflight: NAS send-only/idle/error-free; eight connected expected peers at 100% with zero need
- Reachable stable set: NAS plus seven peers; one connected peer was not SSH-reachable and was left untouched for follow-up
- Cache inventory: exact package identity/spec/path/version only; no contents recorded
- Cache deletion: exact identity trees only; unrelated package/provider/language-server caches preserved
- Cache result: one `opencode-litellm@latest` tree per reachable host; manifest spec `0.2.1`; installed package `0.2.1`; package-lock integrity matched live npm
- Fresh initialization: official OpenCode model discovery succeeded on all eight reachable hosts
- Process safety: no user OpenCode process terminated; one failed cleanup helper process on ProArt was terminated after timeout, not an OpenCode/user session
- Candidate config: exact 25 approved keys removed, five unrelated overrides preserved, whole-object restoration comparison passed, atomic file and directory fsync, mode `0600`
- Failure: newly created exact backup initially reported mode `0777`
- Response: backup changed to `0600`; exact prior config restored atomically with file/directory fsync and mode `0600`; NAS scan returned idle/error-free
- Candidate propagation: not initiated before rollback
- Functional matrix: not run
- Codex/LiteLLM route edit count: zero
- `staticeng_validate`: remains blocked by the pre-existing repository-wide manual CodeMap backlog recorded in `logs/02-staticeng-validation.log`

See `logs/07-reopen5-cache-success-config-rollback.log` for the redacted sequence

## Documentation Impact

No product or architecture steady-state update is required because the reasoning configuration candidate was rolled back. Operational evidence records successful `0.2.1` cache normalization and the backup-mode blocker

## Open Risks

The shared filesystem's default ACL/create behavior can yield a newly created backup with permissive mode despite passing `0600` to `os.open`. A subsequent migration must enforce and verify `fchmod(0600)` before writing backup content and before any production config mutation

One connected expected peer was not reachable over SSH, so its package cache was not changed; it remains explicit follow-up. Offline peers remain automatic configuration convergence recipients

## Recommended Next Step

Reopen the original task with a corrected backup procedure that calls `fchmod(0600)` on the open backup descriptor before writing and verifies mode before touching `opencode.json`. Reuse the healthy canonical `0.2.1` caches; then complete the NAS edit, convergence, and full official matrix
