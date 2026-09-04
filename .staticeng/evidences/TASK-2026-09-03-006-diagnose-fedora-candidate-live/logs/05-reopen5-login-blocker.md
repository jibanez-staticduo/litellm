# Reopen 5 First-Login Blocker

## Outcome

Reopen 5 stopped before watchdog activation, candidate deployment, DCR, or diagnostic execution because the first required password login for the temporary `internal_user_viewer` returned HTTP 401

The strict supported transaction before that stop succeeded:

- Fresh protected backup/isolated restore and exact rollback unit passed
- Candidate identity, signature, SPDX, CycloneDX, and SLSA attestations passed
- Fresh supported reads proved the exact Fedora Defend server/tool member and empty toolset collision baseline
- Supported toolset create returned HTTP 201; list and ID read-back matched the exact one-member digest
- Independent cleanup deadline was armed with the returned toolset ID before principal creation
- `/user/new` created the task user with blocked models, no key or memberships, and only the returned temporary toolset ID
- The immediately following API request was password-only `/user/update`; both returned HTTP 200 with a 0.049968-second gap
- Supported read-back proved the expected viewer role, denied models, single toolset grant, and no broader effective grant
- The first `/login` attempt with the generated credentials returned HTTP 401

The first-login failure is an explicit stop condition. No login retry, alternate endpoint, credential substitution, password repair, candidate deployment, DCR operation, consent, audience check, or MCP request occurred

## Cleanup Proof

The independent supported-API cleanup ran immediately:

```text
grant clear requested before user deletion: yes
task principal absent: yes
task toolset absent: yes
toolset count restored to baseline: yes
defend_memory name count: 0
task auth workspace: absent
deadline worker stopped: yes
candidate deployed: no
diagnostic requests: 0
```

Fedora remains on exact rollback digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, running healthy with restart zero, OOM false, and liveness/readiness 200. No rollback was needed because the selector never changed. NAS was untouched

## Root Cause And Exact Governed Fix

Classification: authentication contract mismatch. The supported `/user/new` plus password-only `/user/update` transaction persisted enough non-secret state for exact read-back, but the normal `/login` path rejected those credentials. The likely boundary is the distinction between a generated opaque `user_id` and the email-oriented local-login lookup, or password update/hash/read behavior for `internal_user_viewer`; the failed run did not broaden into credential-sensitive debugging

The smallest governed next step is an isolated, non-production authentication investigation using the exact candidate source and disposable database. It should prove which login identifier `/login` accepts for local internal users created by `/user/new`, whether `/user/update` stores a hash that `authenticate_user` verifies, and whether `user_email` or `user_id` is the supported username. Add a regression covering the approved two-step lifecycle before another signed candidate or maintenance reopen. Do not retry production login or alter the principal contract ad hoc
