# Reopen 2 Preflight Blocker

## Outcome

Reopen 2 stopped before backup, watcher setup, selector mutation, login, DCR, or tool execution because the only discovered owner-only username/password file does not identify an existing Fedora UI principal and does not match the configured proxy-admin credentials

The precondition was evaluated without printing either value. The file is a regular owner-owned mode `0600` file with exactly two non-empty `username=` and `password=` records. A parameterized read-only database check found zero matching `LiteLLM_UserTable` rows by case-insensitive email or user ID. A constant-time comparison performed inside the healthy rollback container found both the username and password differ from the configured UI administrator pair

The principal therefore cannot be proven existing and currently `defend_memory`-authorized. PMA's explicit stop condition applies: no principal/credential means no candidate deployment. No alternate identity, master-key fallback, OIDC flow, credential substitution, production login, DCR registration, consent POST, API key, database mutation, or second attempt was used

## Safe Checks

```text
credential file: regular, owner-only, mode 0600
credential shape: two non-empty username/password records
matching database users: 0
configured UI username match: false
configured UI password match: false
candidate deployed: no
login attempted: no
DCR artifacts created: no
authorize/complete submitted: no
diagnostic request sent: no
NAS touched: no
```

## Final Fedora State

```text
selector: exact prior digest sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
runtime image: exact prior digest
container: running, healthy, restart 0, OOM false
liveliness: HTTP 200
readiness: HTTP 200
completed migrations: 161
task auth workspace: absent
```

No rollback ran because no deployment or production mutation occurred

## Required Governed Correction

The secret owner must provide an existing Fedora username/password principal that is already authorized for the `defend_memory` toolset, through owner-only local files or inherited file descriptors. The identity must pass a pre-deployment parameterized authorization check without exposing it. Creating a user, setting/resetting a password, granting a toolset, or substituting the master/UI/API key requires separate governance and is not authorized by TASK-006
