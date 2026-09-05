# Tech Lead Reopen 1 Review

## Verification

```text
complete generated watcher Bash syntax: pass
complete generated watcher ShellCheck: pass
complete watcher behavioral and OOM matrix: pass
complete controller Bash syntax: pass
complete controller ShellCheck: pass
controller normal startup handshake: pass
controller startup-failure rollback: pass
controller pre-ready trip rollback: pass
controller pre-selector signal rollback: pass
git diff --check: pass
staticeng_validate: pass, warnings 0
```

## Verdict

REJECT for functional/OOM/rollback risk

The watcher remains in `pre-start` until the controller completes candidate startup. The pre-start collector returns before candidate cgroup/process collection, and the watcher applies candidate absolute memory, growth, cgroup OOM, restart, and process gates only to `active` rows. The candidate is thus unprotected by those required limits during startup

Watcher trip and controller handoff do not share a lock or ownership transition. Trip removes ready and active state, then publishes its trigger. The controller separately checks those files and can set handoff complete after its final trigger check while trip is beginning. The current final-race test trips before ready publication, not at this final boundary

On the pre-selector signal path, rollback moves the prepared candidate selector into place before invoking the exact rollback action. If that action fails, the candidate selector remains installed. The current signal test exercises only successful rollback

No Fedora/NAS access, deployment, credential use, diagnostic request, commit, or push occurred. TASK-006 Reopen 9 remains unauthorized
