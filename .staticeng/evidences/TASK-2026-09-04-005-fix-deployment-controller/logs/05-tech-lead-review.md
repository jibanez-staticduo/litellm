# Tech Lead Review 1

## Verification

```text
bash -n controller: pass
bash -n isolated test: pass
ShellCheck controller and isolated test: pass
isolated startup-failure behavior: pass
git diff --check: pass
staticeng_validate: pass, warnings 0
```

## Verdict

REJECT for functional and rollback risk

The production watcher rejects any candidate sample whose health is not `healthy` or whose liveness/readiness status is not 200. The controller launches that watcher before entering its bounded startup poll. Normal startup can therefore invoke exact rollback before the startup allowance can operate

The controller checks watcher liveness only at the start of a polling iteration. A watcher trip during container inspection or either health request can be followed by `candidate-ready`, `handoff_complete=1`, and a zero exit without another watcher or rollback-state gate

The selector is atomically replaced before `mutation_started=1`. A signal handled between those commands sees mutation as unarmed and exits without rollback

No Fedora/NAS access, deployment, credential use, diagnostic request, commit, or push occurred. TASK-006 Reopen 9 remains unauthorized
