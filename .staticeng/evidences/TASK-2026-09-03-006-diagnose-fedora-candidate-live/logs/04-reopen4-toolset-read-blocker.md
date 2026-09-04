# Reopen 4 Existing Toolset Blocker

## Outcome

Reopen 4 stopped before watchdog activation, candidate deployment, or temporary-principal creation because the supported toolset read API returned an empty collection. The transaction cannot resolve and prove the required existing `defend_memory` toolset ID or membership digest

The amended SCR prohibits principal creation until that exact existing toolset is resolved through a supported read API. Creating a toolset, inferring an ID, granting direct MCP server/tool access, reading or repairing the database, or continuing with an empty/broader grant is not authorized. The failed prerequisite therefore ended the attempt without production mutation

## Completed Safety Preparation

- Created a fresh owner-only protected attempt directory
- Captured exact rollback selector and runtime identity
- Created and syntax-checked the exact-digest rollback unit
- Proved candidate Compose rendering differs only by `services.litellm.image`
- Created a fresh 205,997,369-byte custom-format PostgreSQL backup with checksum and listing
- Restored the backup into a disposable exact-image PostgreSQL instance and verified 161 completed migrations
- Removed the isolated restore container, network, and volume
- Freshly verified the exact candidate signature plus SPDX, CycloneDX, and SLSA attestations
- Verified candidate image ID, amd64 platform, and source revision

## Stop-State Proof

```text
supported /v1/mcp/toolset HTTP status: 200
returned toolsets: 0
defend_memory matches: 0
principal created: no
candidate deployed: no
watchdog started: no
diagnostic request sent: no
task containers/networks/volumes: 0/0/0
task watchdogs: 0
task auth workspaces: 0
active attempt pointer: absent
```

Fedora remained on exact rollback digest `sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04`, running healthy with restart zero, OOM false, and liveness/readiness 200. No rollback ran because the selector never changed. NAS was untouched

## Root Cause And Governed Fix

Classification: configuration/data prerequisite mismatch. TASK-012/013 require an existing `defend_memory` toolset row, but the healthy Fedora rollback service's supported admin `GET /v1/mcp/toolset` returns no toolsets. The registered Defend MCP server/access group is not equivalent to the named toolset required by the amendment

The smallest governed fix is a separate SCR/task to create and verify the exact `defend_memory` toolset through supported APIs, including its precise `{server_id, tool_name}` membership, permissions, rollback/removal behavior, and production-preservation impact. Alternatively, amend the temporary-principal contract to use a different already-supported least-privilege grant only after architecture/security review. Do not direct-edit the database or broaden to server/access-group permissions under TASK-006
