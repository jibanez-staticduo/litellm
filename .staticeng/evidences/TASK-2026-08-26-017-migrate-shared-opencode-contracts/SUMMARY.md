# TASK-2026-08-26-017 Evidence Summary

## Result

ROLLED BACK after Reopen 3. The fresh connected-scope preflight passed and the exact NAS-only atomic cleanup was applied, but a newly connected expected peer failed the post-mutation convergence gate. The protected NAS backup was restored atomically before cache or process changes

Reopen 3 began with six connected expected peers complete, conflict-free, and checksum-aligned with the NAS send-only source. During rollout a seventh expected peer connected. It did not converge within the bounded wait, remaining one item behind, and then disconnected. Per the post-mutation stop condition, the exact mode-`0600` backup was restored from NAS, Syncthing returned the six still-connected peers to the prior checksum, and no plugin cache or process was changed

## Acceptance Criteria Coverage

- **T3-AC-1: ROLLED BACK.** A protected mode-`0600` exact backup was created. The candidate removed exactly 25 approved keys and structural restoration comparison proved every unrelated path unchanged, but the candidate was rolled back after convergence failure
- **T3-AC-2: ROLLED BACK.** Candidate JSON parsed, retained exact unversioned `@staticeng/opencode-litellm`, had no `file://` reference, and remained mode `0600`; the prior valid configuration was restored
- **T3-AC-3: FAIL/ROLLED BACK.** Six initial connected peers converged to the candidate. A seventh expected peer connected during rollout, remained one item behind through the bounded wait, and disconnected; rollback restored NAS and the six remaining connected peers to the prior checksum with no conflicts
- **T3-AC-4: NOT RUN.** No package cache was invalidated because convergence failed first
- **T3-AC-5: PASS for safety.** No control, pre-existing, or unrelated process was terminated; no fresh process was launched because the preceding gate failed
- **T3-AC-6: NOT RUN.** Runtime selector validation did not begin
- **T3-AC-7: NOT RUN.** Isolated wire and override validation did not begin
- **T3-AC-8: PASS.** Evidence contains no credentials, prompts, responses, raw configuration, device IDs, network addresses, secret hashes, or backup path

## Verification

- Initial scope: NAS plus six connected expected peers; all complete, checksum-aligned, mode `0600`, JSON-valid, and conflict-free
- Candidate backup: exact, protected mode `0600`, file-fsynced outside the synchronized tree
- Candidate mutation: NAS-only, JSON parse before rename, atomic rename, file fsync, directory fsync, mode `0600`
- Candidate cleanup: 25 approved overrides removed; 5 unrelated overrides preserved; whole-object restoration comparison passed
- Candidate plugin contract: exact unversioned package reference; zero `file://` references
- Failure: newly connected seventh expected peer stayed one item behind during bounded convergence and then disconnected
- Rollback: exact backup restored atomically from NAS with file and directory fsync; checksum and mode matched backup
- Post-rollback: six currently connected expected peers at 100%, matching prior active checksum, zero conflict files; NAS idle/error-free
- Cache invalidation count: zero
- Process change count: zero
- Codex/LiteLLM registry edit count: zero
- `staticeng_validate`: remains blocked by the pre-existing repository-wide manual CodeMap backlog recorded in `logs/02-staticeng-validation.log`

See `logs/05-reopen3-migration-rollback.log` for the redacted Reopen 3 sequence

## Documentation Impact

Product and architecture documentation are not changed because the candidate behavior was rolled back. Task and operational evidence record the attempted migration and exact restored state

## Open Risks

The newly connected expected peer is not directly reachable from this control host and disconnected before receiving the candidate or rollback version. It should automatically receive the current authoritative NAS file when it reconnects, but another migration attempt must treat it according to the then-current connected-peer scope

The repository also retains its pre-existing broad manual CodeMap backlog; this task did not add, move, or rewire source files

## Recommended Next Step

PMA should confirm the transient peer is either offline before the next fresh preflight or connected and 100% complete. Then reopen the original task and retry the same protected NAS-only migration. Do not invalidate cache or run the behavior matrix until post-mutation connected-peer convergence passes
