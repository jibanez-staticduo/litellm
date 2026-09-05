# Reopen 9: Actual Preflight Result

## Outcome

Stopped before deployment and before the diagnostic request. This is a dependency projection failure, not a LiteLLM functional failure.

The maintained controller and generator from approved commit `2b3123c667b13ff0765ed6cc26d00eb6743d2458` were copied to the owner-only Fedora attempt `/home/staticduo/docker/litellm/releases/TASK-006-r9-live`. Generation reported five scripts and successful Bash syntax validation. No inline deployment controller was used.

A fresh 464,634,225-byte PostgreSQL backup, checksum, and listing were created. The first isolated restore encountered a connection error; the disposable resources were removed. A second isolated restore of that same fresh backup using TCP readiness completed and verified 161 completed migrations. Its container, network, and volume were removed. No production database restore occurred.

## Exact Failure

Phase: dependency baseline, before isolated watchdog proof or maintained controller invocation.

The approved dependency Docker projection contains `{{if .State.Health}}`. Docker returned:

```text
template parsing error: template: :1:90: executing "" at <.State.Health>: map has no entry for key "Health"
```

Status-only checks with the SCR's fixed container projection passed for PostgreSQL, Redis, Defend MCP, Defend gateway, Defend PostgreSQL, and Defend Neo4j. The same projection failed for `defend-memory-qdrant`. No broad inspection or alternate whole-object projection was used.

The maintained collector uses this same missing-field-sensitive health access. Its complete dependency baseline and subsequent samples cannot be established on this host without a governed correction. The failed pipeline's partial dependency digest must not be treated as a valid baseline.

## Verification And Scope

- AC-1: Partial; fresh backup/restore and generated-script syntax passed, dependency baseline failed. Fresh signature verification, proof, and deployment were not reached.
- AC-2: Not run; zero diagnostic requests and zero diagnostic credential consumption.
- AC-3: Preflight failure localized to the Qdrant dependency's missing Health field. Product memory-failure root cause remains unresolved.
- AC-4: No patch or alternate projection was applied.
- AC-5: Not run; no candidate deployment, functional matrix, or soak.
- AC-6: Fedora remained on exact rollback digest, running healthy, restart 0, OOM false, readiness/liveliness 200. No rollback was needed. NAS was untouched.
- AC-7: This record reports the actual failed phase; it does not claim completed functional or full cleanup gates.

The active attempt pointer was removed. Protected backup and non-secret control artifacts remain in the owner-only attempt. No temporary principal, toolset, UI key, DCR, or auth workspace was created. Known unrelated StaticEng normalizations were preserved.

## Recommended Correction

PMA should route a narrow correction to make the fixed dependency health projection tolerate an absent Health key (for example, a reviewed `index`-based lookup) and add a Docker-template test with Health absent. Apply it to both baseline and maintained collector under the SCR. Do not describe this run as a product failure or successful deployment.
