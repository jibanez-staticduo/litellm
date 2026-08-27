# TASK-2026-08-26-017 Evidence Summary

## Result

PASS after Reopen 6. The NAS-authoritative reasoning migration is active. Healthy canonical plugin `0.2.1` caches were retained, a descriptor-protected exact backup passed every pre-mutation gate, exactly 25 approved overrides were removed atomically from NAS, and the stable connected set converged at 100% with zero conflicts

Fresh official OpenCode processes on NAS and seven reachable peers initialized 36 live metadata models from one canonical `0.2.1` cache instance per host. Published-package selector/default/body verification covered all nine contract families, 31 aliases, and 164 explicit legacy/V2 mode bodies; retirement, Spark preservation, no-fabrication, intrinsic-default omission, and user-last override checks passed without production inference. No user/control session was terminated

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
- `staticeng_validate`: remains blocked by the pre-existing repository-wide manual CodeMap backlog recorded in `logs/02-staticeng-validation.log`

See `logs/08-reopen6-final-migration.log` for the redacted final sequence

## Documentation Impact

The approved SCR, plan, and plugin architecture documentation already define the steady-state model-contract behavior. No additional product or architecture documentation change is required; this task activates that approved state and records operational closure

## Open Risks

Pre-existing long-running OpenCode processes do not hot-reload the new config/package and require user restart. One expected peer became SSH-unreachable during final host checksum collection; Syncthing had already reported it 100% for the candidate and it remains governed by automatic NAS convergence on reconnect

The repository retains its pre-existing broad manual CodeMap backlog; this task did not add, move, or rewire source files

## Recommended Next Step

PMA can close Task 017 and notify users to restart pre-existing OpenCode sessions when convenient. Track unreachable/offline peer cache normalization separately if it does not already resolve canonical `0.2.1` on reconnect
