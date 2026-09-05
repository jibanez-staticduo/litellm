# Accepted dual-host repair: closure evidence index

## Summary and authority

PMA independently verified both hosts running/healthy, restart=0 and OOM=false on the same digest and explicitly accepted the functional repair/deployment scope in the archived [closure task](../../tasks/done/TASK-2026-09-05-003-close-dual-host-repair.md). This closure performs documentation/registry work only: no source, image, runtime, credential, security or harness changes, and no new runtime probes

Accepted image: `docker.staticduo.com/litellm@sha256:0c8009530d20ca8a5306f38ff4f6aecb6e3261ded0c5e7336237033b6557717c`

Application source: `6ba4b3b366386e16364a6723c43319f4e52cc7a0`

Final repair evidence commit before closure: `f44b39dafc23271f0f7d549e5d1ea4174c703c3a`

The repair evidence records 951 isolated mapped tests, public Astra reload/Chat/Responses and aggregate MCP/healthy-tool checks, zero post-deployment spend-sanitizer recursion and two complete 900-second observations. Those checks are referenced, not rerun or broadened here. Acceptance excludes external Frigate availability, universal OAuth/provider availability, fresh final-image security qualification and indefinite memory stability

## Evidence index

| Subject | Authoritative retained record |
| --- | --- |
| Final source, build, both runtime identities, public calls, spend persistence and bounded resource results | [Reopen 1 dual-host verification](../TASK-2026-09-05-002-fix-nas-functional-residuals/logs/10-reopen1-dual-host-pass.md) |
| Final 62 resource samples | [Reopen 1 samples](../TASK-2026-09-05-002-fix-nas-functional-residuals/logs/11-reopen1-resource-samples.csv) |
| Active recursion reproduction, sanitizer/OAuth corrections and exact source-test limitations | [Source verification](../TASK-2026-09-05-002-fix-nas-functional-residuals/logs/09-reopen1-source.md) |
| Earlier persistent containment, session/Responses and retained-request repair | [Fedora final functional/memory gate](../TASK-2026-09-05-001-repair-fedora-runtime/logs/19-functional-memory-pass.md) |
| Original NAS deployment, protected backup and preservation | [NAS deployment preflight](../TASK-2026-09-01-004-deploy-lazymcp-oauth-nas/logs/01-preflight-deployment.md) |
| Host-specific startup correction and secret-free versioned wrapper snapshots | [Startup correction](../TASK-2026-09-05-002-fix-nas-functional-residuals/logs/06-startup-correction.md), [Fedora snapshot](../TASK-2026-09-05-002-fix-nas-functional-residuals/config/fedora-start-litellm.sh.txt), [NAS snapshot](../TASK-2026-09-05-002-fix-nas-functional-residuals/config/nas-start-litellm.sh.txt) |
| Archived accepted records and superseded/not-passed classification | [Dispositions](dispositions.md) |
| Final deferred security and operational report | [Deferred report](deferred-security-operational.md) |
| Documentation validation and untouched-artifact proof | [Verification](logs/verification.md), [excluded-artifact checksums](logs/excluded-artifacts.sha256) |

## Acceptance criteria coverage

- AC-1: Four accepted tasks are archived under .staticeng/tasks/done/ with PMA acceptance notices; complete original bodies and evidence histories remain
- AC-2: Fifteen stale release/maintenance entries are superseded as current workflow, not marked passed. Unrelated backlog and the failed/deferred experimental DCR client remain open and unchanged
- AC-3: The concise report separates recorded private-output rotation advice, exact-final-subject audit/signature evidence gaps and deliberate containment/restart policy from verified functional success. No remediation or unsupported current-vulnerability assertion is made
- AC-4: Closure-only changes are validated and staged; the four unrelated watchdog artifacts are explicitly excluded and checked against their pre-closure bytes. All workflow writes precede the single final closure commit/non-force push
- AC-5: No further runtime changes or probes occurred. Final exact Git SHA and synchronization are returned in the handback

## Git traceability without a post-commit edit

The closure SHA is the commit introducing .staticeng/tasks/done/TASK-2026-09-05-003-close-dual-host-repair.md. Retrieve it with `git log --diff-filter=A --format=%H -- .staticeng/tasks/done/TASK-2026-09-05-003-close-dual-host-repair.md`. It is intentionally not embedded into its own contents; the exact command result, push and local/remote main equality are reported after commit. The done registry's other Commit cells reference their implementation/evidence commits, not a newly invented self-referential hash
