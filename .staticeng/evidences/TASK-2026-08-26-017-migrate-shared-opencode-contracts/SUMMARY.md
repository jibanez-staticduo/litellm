# TASK-2026-08-26-017 Evidence Summary

## Historical Intermediate Result

PASS for Task 017's completed migration scope. This summary is a historical intermediate snapshot, not the final client contract. At this point the NAS-authoritative reasoning migration used plugin `0.2.1`, retained nine families including Spark, and validated intrinsic-default omission. Those version, family-count, Spark, and default-semantics statements were superseded by later approved decisions

The final authoritative state is plugin `0.2.2` on OpenCode `1.18.23`, eight retained families, both normal and Spark GPT-5.3 retired, explicit official-default transmission, and user-last overrides. See Task 004 for corrective client retirement, Task 005 for independent current runtime gates, and Task 020 for the final SCR PASS trace. Task 019 provides final dual-registry retirement evidence

## Acceptance Criteria Coverage

- **T3-AC-1: PASS.** Fresh exact backup was opened, descriptor-`fchmod(0600)`ed, owner-aligned, fsynced, closed, and verified for owner/mode/size/checksum before mutation. Candidate removed exactly 25 approved keys and whole-object restoration comparison proved every unrelated path unchanged; five unrelated overrides remain
- **T3-AC-2: PASS.** Active JSON parses, exact unversioned `@staticeng/opencode-litellm` remains, zero `file://` references exist, and mode remains `0600`
- **T3-AC-3: PASS under approved connected scope.** NAS was sole writer. Seven peers connected at the final stabilization window reached 100%, zero need/deletes, matching candidate checksum, and zero conflicts. SSH-unreachable/offline peers remain automatic future convergence follow-up
- **T3-AC-4: PASS for corrective `0.2.1`.** NAS and seven reachable peers retain exactly one canonical cache tree each at manifest/installed version `0.2.1` with matching npm integrity. Fresh official model discovery succeeded with 36 models on every reachable host
- **T3-AC-5: PASS.** No rollout-control or unrelated user process was killed. Pre-existing long-running OpenCode processes were recorded and require user restart to adopt the active config/package
- **T3-AC-6: PASS.** Exact approved modes/defaults resolved for all 31 discovered known aliases; four retired normal GPT-5.3 aliases are absent, four Spark aliases remain, and no near-match/future namespace was fabricated
- **T3-AC-7: PASS.** Published `0.2.1` matrix validated nine family defaults and all 164 explicit legacy/V2 bodies, Qwen/DeepSeek off mappings, intrinsic default omission for unknown models, and user/provider-last override precedence without production inference
- **T3-AC-8: PASS.** Evidence contains no credentials, prompts, responses, raw configuration, device IDs, addresses, protected hashes, or backup path

## Verification

- Preflight NAS: send-only, idle, zero need, zero pull/system errors
- Preflight stable connected set: seven peers, all 100%, zero need/deletes
- Backup: owner match, descriptor mode `0600`, size match, checksum match, file fsync, closed before mutation
- Candidate: NAS-only atomic rename, file/directory fsync, JSON parse, mode `0600`
- Cleanup: exactly 25 approved overrides removed; five unrelated overrides preserved; unrelated whole-object comparison passed
- Plugin reference: exact unversioned package; zero local/file references
- Post-mutation Syncthing: seven final connected peers at 100%, matching candidate checksum, zero conflicts; NAS idle/error-free
- Fresh official host processes: eight reachable hosts, model discovery success, 36 models, one cache tree, installed `0.2.1`
- Package regression: 63/63 tests passed, including live direct response shapes
- Published-package matrix: 9 families, 31 aliases, 164 explicit bodies, 4 retired aliases absent, 4 Spark aliases present, fabricated aliases zero, user-last pass, intrinsic-default omission pass
- Production inference request count: zero
- Process termination count: zero
- Peer direct configuration edit count: zero
- Codex/LiteLLM route edit count: zero
- `staticeng_validate`: remains blocked by the pre-existing repository-wide manual CodeMap backlog recorded in `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/logs/02-staticeng-validation.log`

See `.staticeng/evidences/TASK-2026-08-26-017-migrate-shared-opencode-contracts/logs/08-reopen6-final-migration.log` for the redacted final sequence

## Documentation Impact

This packet preserves the completed `0.2.1` migration evidence as history. It must be read with the final SCR/plan and Tasks 004/005/019/020; its nine-family, Spark-preserving, and intrinsic-default-omission statements are non-normative

## Open Risks

Pre-existing long-running OpenCode processes do not hot-reload the new config/package and require user restart. One expected peer became SSH-unreachable during final host checksum collection; Syncthing had already reported it 100% for the candidate and it remains governed by automatic NAS convergence on reconnect

The repository retains its pre-existing broad manual CodeMap backlog; this task did not add, move, or rewire source files

## Recommended Next Step

Task 017 remains closed as a successful intermediate migration. Use Tasks 004/005/019/020 for current state and track unreachable/offline peer convergence separately
