---
id: TASK-2026-09-03-014-design-temporary-defend-toolset
complexity: standard
track: investigation
slice: foundation
status: active
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-015-authorize-temporary-defend-toolset
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 1
---

# Task: Design temporary Defend toolset

## Objective

Map the existing registered Defend MCP server and `memory-find` tool to a temporary exact `defend_memory` toolset using supported APIs, with least privilege and complete cleanup.

## Acceptance Criteria

- [x] AC-1: Resolve the exact existing server ID and canonical tool name through supported read-only APIs without exposing credentials or payloads.
- [x] AC-2: Define supported toolset create/read/update/delete requests and exact membership shape.
- [x] AC-3: Prove the toolset grant is narrower than server/access-group/global permissions and enables only `memory-find`.
- [x] AC-4: Define independent cleanup, baseline restoration counts/digests, failure rollback, and principal/toolset deletion ordering.
- [x] AC-5: Return signed execution handoff; no mutation.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Use supported read-only MCP server/tool APIs to map the existing Defend service and exact memory-find tool. Design one temporary toolset named with a task-unique identifier but exposed to the diagnostic flow as the exact intended resource. It must contain exactly one `{server_id, tool_name}` member, grant no server/group/model/global rights, and be deleted after the temporary principal. No direct DB reads/writes, credentials, tool payloads, creation, deployment, or NAS access. Update task/evidence and return exact supported API contract.

## Reopen History

### Reopen 1 - Authorized secret-isolated Fedora identity read

PMA authorizes use of the existing Fedora administrative credential solely through the supported read-only `GET /v1/mcp/server` and `GET /mcp-rest/tools/list` endpoints. Consume it from its owner-only host-local source or inherited file descriptor; never print, hash, copy, export, place in command arguments, or retain it in evidence. Freeze exactly one active Fedora server whose alias is `defend_memory` and which exposes canonical upstream tool `find`; reject ambiguity or mismatch. Record only the non-secret server UUID and canonical one-member digest. Do not invoke tools, mutate grants/toolsets/users/config/DB, deploy, or access NAS.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

PASS. Reopen 1 used the existing Fedora administrator credential only inside an owner-owned mode-0600 host-local source and only for the two authorized supported GETs. `GET /v1/mcp/server` returned exactly one active `defend_memory` registration, and `GET /mcp-rest/tools/list?server_id=54a0ad17239e9f184882cf47e3ac277c` returned exactly one canonical upstream `find` for that same server and alias. The exact toolset member is `{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}` and its canonical SHA-256 is `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`

The supported CRUD contract is frozen in `.staticeng/evidences/TASK-2026-09-03-014-design-temporary-defend-toolset/SUMMARY.md`. Because the public diagnostic resource is fixed at `/toolset/defend_memory/lazymcp`, the temporary toolset's required unique name is exactly `defend_memory`. Task uniqueness comes from ownership, returned `toolset_id`, description, and baseline proof, not from changing the resource segment. Any pre-existing name match is a collision and a stop condition

### Work Performed

- Read the approved SCR, parent and sibling tasks, LazyMCP architecture contract, relevant CodeMaps, toolset API types/routes/storage, authorization resolution, user cleanup paths, and prior Fedora evidence
- Used only supported read-only LiteLLM admin and LazyMCP describe APIs to distinguish the reachable NAS registry from the Fedora target and resolve canonical tool naming; no upstream tool payload was invoked or retained
- Defined exact create, list, get, defensive update, and delete requests; canonical membership hashing; principal grant ordering; unconditional cleanup; rollback; and baseline restoration proof
- Performed no direct database access, credential read, tool invocation, toolset/principal creation, update, deletion, deployment, host mutation, or NAS access
- Reopen 1 consumed the authorized credential in memory on Fedora without printing, hashing, copying, exporting, command arguments, or evidence retention; joined the two supported GET results, retained only the server UUID and member digest, then discarded the credential

### Acceptance Criteria Coverage

- [x] **AC-1: PASS.** Supported Fedora reads resolved exactly one active server ID `54a0ad17239e9f184882cf47e3ac277c` and exactly one canonical upstream `find`; the one-member digest is `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`
- [x] **AC-2: PASS.** Exact supported CRUD endpoints, bodies, expected statuses, response checks, one-member shape, and membership digest are recorded
- [x] **AC-3: PASS.** The grant contains only the returned toolset ID; resolved permissions must equal only `{server_id: ["find"]}`, while every server, access-group, direct-tool, model, team, organization, agent, and global grant remains empty or denied
- [x] **AC-4: PASS.** Toolset and association baseline counts/digests, create-before-grant ordering, principal-before-toolset cleanup, failure rollback, absence checks, and non-task preservation are frozen
- [x] **AC-5: PASS.** This signed handoff and evidence are mutation-free

### Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. This is a one-run operational exception design; the approved SCR remains the source of truth and TASK-015 must amend it before execution

### Open Risks

The supported management API has no transactional create-and-grant operation and no conditional delete. Execution must serialize toolset ownership checks and stop on any name/ID/membership drift. Toolset deletion does not clean external object-permission references, so every task principal grant must be cleared and the principal deleted before deleting the toolset

### Recommended Next Step

PMA should hand the now complete exact member and digest to TASK-015 for SCR amendment. Runtime creation remains prohibited until TASK-015 authorizes the exact temporary transaction and PMA hands execution to Tech Lead

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-014 PASS. Authorized supported Fedora GETs resolve exactly one active `defend_memory` server, ID `54a0ad17239e9f184882cf47e3ac277c`, exposing exactly one canonical upstream `find`. Freeze the only member as `{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}` with SHA-256 `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`. The credential remained in memory from its owner-only Fedora source and was never printed, hashed, copied, exported, passed in arguments, or retained. No tool invocation, mutation, deploy, direct database access, or NAS access occurred. TASK-015 may now authorize the exact create-before-grant and principal-before-toolset-delete transaction
