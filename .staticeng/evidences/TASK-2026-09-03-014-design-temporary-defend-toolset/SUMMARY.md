# TASK-2026-09-03-014 Evidence Summary

## Summary

PASS. Reopen 1 used the existing Fedora administrator credential only from its owner-owned mode-0600 host-local source and only for the two authorized supported GETs. The joined responses resolve exactly one active alias `defend_memory` server, ID `54a0ad17239e9f184882cf47e3ac277c`, exposing exactly one canonical upstream tool `find`. The credential remained in process memory and was discarded without printing, hashing, copying, exporting, command-argument use, or evidence retention

Toolset rows store the upstream tool name, not the prefixed gateway wire name. The only valid member is therefore:

```json
{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}
```

The public OAuth resource is fixed at `https://litellm.defend.tech/toolset/defend_memory/lazymcp`, so the temporary toolset must be named exactly `defend_memory`. A task-unique suffix in `toolset_name` would produce a different resource and violate the approved exact-audience contract. Temporary ownership is instead bound by an execution correlation value, the create response's unpredictable `toolset_id`, the description, and before/after proof

## Supported Read Mapping

The execution preflight must use the candidate's supported administrative APIs with the already approved administrator credential handling. It must retain only allowlisted non-secret fields and status classes

1. On Fedora, `GET /v1/mcp/server` resolved exactly one active row with `alias=defend_memory`, `server_name=defend_memory`, `transport=http`, `auth_type=none`, `approval_status=active`, and no server-level `allowed_tools` restriction; its exact ID is `54a0ad17239e9f184882cf47e3ac277c`
2. On Fedora, `GET /mcp-rest/tools/list?server_id=54a0ad17239e9f184882cf47e3ac277c` resolved exactly one tool named `find` whose metadata carried the same server ID and alias `defend_memory`. Description, `inputSchema`, arguments, response content, and all other tool payload fields were not retained
3. The Fedora gateway wire name is `defend_memory-find`, formed from alias `defend_memory`, default separator `-`, and upstream name `find`. The toolset member remains `find`; never store the wire name
4. `GET /v1/mcp/toolset` must return no `toolset_name=defend_memory`. The most recent governed Fedora read returned HTTP 200 and zero total toolsets, but execution must take a fresh baseline. Any name match is a collision. Do not adopt, update, delete, or reuse it

The task also inspected the supported source contract at `litellm/types/mcp_server/mcp_toolset.py`, `litellm/proxy/management_endpoints/mcp_management_endpoints.py`, `litellm/proxy/_experimental/mcp_server/toolset_db.py`, `litellm/proxy/_experimental/mcp_server/mcp_server_manager.py`, and `litellm/proxy/_experimental/mcp_server/rest_endpoints.py`

## Exact CRUD Contract

All requests use `Authorization: Bearer <approved-admin-credential>`, `Content-Type: application/json` when a body is present, and a non-secret `litellm-changed-by` task correlation header where supported. Credential values, complete responses, tool schemas, and tool payloads must never enter evidence

### Create

```http
POST /v1/mcp/toolset
```

```json
{
  "toolset_name": "defend_memory",
  "description": "Temporary TASK-2026-09-03-014 Fedora diagnostic toolset",
  "tools": [
    {
      "server_id": "54a0ad17239e9f184882cf47e3ac277c",
      "tool_name": "find"
    }
  ]
}
```

Require HTTP 201. Capture only returned `toolset_id`, `toolset_name`, description equality, member count, normalized member fields, and canonical digest. Reject 409 as a collision and reject every response containing a mismatched name, more or fewer than one member, another server ID, or another tool name. Never retry create after an ambiguous timeout. Re-list by name; adopt for cleanup only if one row exactly matches this task's description, expected one-member digest, and the create response ID if that ID was received. Otherwise stop and escalate without deleting an unproven row

### Read

```http
GET /v1/mcp/toolset
GET /v1/mcp/toolset/<returned-toolset-id>
```

The list response is an array of toolsets. The ID response is one toolset or HTTP 404. Before grant and again immediately before use, both reads must show exactly one task row with exact name, description, returned ID, one-member shape, and digest. The list must show no second `defend_memory` row. Any drift triggers cleanup without DCR or tool invocation

### Update

No normal update is permitted. Creation must already return the exact final shape. The supported full replacement contract, reserved only to restore the task-owned row after a verified task-client serialization defect and before any grant, is:

```http
PUT /v1/mcp/toolset
```

```json
{
  "toolset_id": "<returned-toolset-id>",
  "toolset_name": "defend_memory",
  "description": "Temporary TASK-2026-09-03-014 Fedora diagnostic toolset",
  "tools": [
    {
      "server_id": "54a0ad17239e9f184882cf47e3ac277c",
      "tool_name": "find"
    }
  ]
}
```

Require HTTP 200 and exact read-back. Never use update to repair a collision, alter a pre-existing row, add tools, rename the resource, or continue after an ambiguous create. If exact create read-back fails, the safer default is delete the proven task row and stop

### Delete

```http
DELETE /v1/mcp/toolset/<returned-toolset-id>
```

Require HTTP 202, then require `GET /v1/mcp/toolset/<returned-toolset-id>` to return 404 and the collection baseline to be restored. A delete retry is allowed only after a read proves the same task-owned ID still exists with the exact task description and membership digest. HTTP 404 is acceptable only as postcondition evidence when fresh list/get reads also prove no task row and all baseline counts/digests are restored

## Canonical Membership And Digests

Normalize a toolset membership by projecting only `server_id` and `tool_name`, sorting keys lexicographically, sorting members by `(server_id, tool_name)`, and serializing UTF-8 JSON with no insignificant whitespace using `ensure_ascii=true` and separators `(',', ':')`. Reject duplicate members before hashing

The canonical membership bytes are:

```text
[{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}]
```

Every create/read/cleanup projection must match this SHA-256:

```text
e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd
```

For the non-task toolset digest, project every other row to `toolset_id`, `toolset_name`, `description` with null preserved, and normalized `tools`; sort by `toolset_id`; serialize and hash with the same rules. Timestamps and audit actors are excluded because they are not authorization state. The final count and digest must equal baseline

## Least-Privilege Proof

The toolset is a selection, not a direct server, access-group, model, or global grant. Runtime resolves its only member to this permission map:

```json
{"54a0ad17239e9f184882cf47e3ac277c":["find"]}
```

The one temporary `internal_user_viewer` must retain `models=["no-default-models"]`, `auto_create_key=false`, no teams or organizations, and an object permission whose only non-empty authorization collection is `mcp_toolsets=["<returned-toolset-id>"]`. Explicitly require `mcp_servers=[]`, `mcp_access_groups=[]`, `mcp_tool_permissions={}`, `blocked_tools=[]`, `vector_stores=[]`, `agents=[]`, `agent_access_groups=[]`, `models=[]`, `search_tools=[]`, and `mcp_tool_search_enabled=false` inside object permission. Null versus empty may vary on read, but no field other than `mcp_toolsets` may be effective or non-empty

Read the principal back through `GET /user/info?user_id=<task-user-id>` and require those exact effective conditions before login. Then use `GET /mcp-rest/tools/list?toolset_name=defend_memory` under the task UI session and retain metadata only: exactly one tool, `name=find`, matching `mcp_info.server_id`, and no second server/tool. This is the positive resolution proof. The existing negative audience checks remain mandatory. Do not call the upstream tool during this proof; TASK-006 owns the one authorized diagnostic call

The grant is narrower than alternatives because the principal receives no `mcp_servers` entry, no `mcp_access_groups` entry, no direct `mcp_tool_permissions`, no `all-proxy-mcpservers`, no model access, and no global or administrative role. A server grant would expose every server-allowed tool, an access-group grant could expose multiple servers, and a direct/global grant would bypass the one temporary named-resource lifecycle. Any such field is a stop condition

## Baseline And Restoration Proof

Before create, collect only supported-API projections and record:

- `toolset_total`, `defend_memory_name_count=0`, and the non-task toolset count/digest
- server projection count/digest from `GET /v1/mcp/server`, excluding credentials and volatile health/UI annotations; separately pin the exact Defend server ID, alias, server name, transport, auth type, empty server-level allowlist, access-group names, and allow-all/tool-filter booleans
- exact canonical Fedora member and freshly computed expected digest above
- global local-user count from paginated `GET /user/list`, generated task-user count zero, and non-task user-to-toolset association count/digest
- effective assignments of this task's not-yet-created toolset ID zero, task-owned key count zero, team/organization membership count zero, and no task artifact path

The non-task user-to-toolset association digest projects each non-task user to `user_id` plus a sorted unique `mcp_toolsets` array obtained from supported user reads, sorts by `user_id`, and hashes canonical JSON. Do not retain email, password, token, spend, metadata, or key values. Pagination must run to `total_pages`; partial scans are invalid

After create but before grant, require `toolset_total=baseline+1`, one exact task row, unchanged non-task toolset digest, unchanged server digest, task user absent, and zero assignments to returned toolset ID. After principal creation/grant, require exactly one task user and exactly one effective user association to the returned ID, with zero task memberships and only the unavoidable bounded UI session key after login

Final restoration requires toolset total and non-task toolset digest equal baseline, `defend_memory_name_count=0`, returned toolset ID absent, server count/digest equal baseline, generated user absent, task keys and memberships absent, effective assignments to returned ID zero, global user count equal baseline, non-task user-to-toolset count/digest equal baseline, and zero task artifact paths. Any mismatch blocks maintenance closure

## Ordering And Failure Rollback

The independent cleanup worker and deadline worker must hold the generated task user ID, exact expected toolset identity/digest, and returned toolset ID as soon as create succeeds. They must be armed before principal creation. They must not infer ownership by name alone

Required forward order:

1. Capture complete fresh baseline and prove zero `defend_memory` collision
2. Create exact toolset and validate collection plus ID read-back
3. Arm independent cleanup using the returned toolset ID, then create the principal
4. Complete the already approved strict `/user/new` then immediate password-only `/user/update` transaction
5. Read back least privilege, log in, prove one-tool resolution, and perform exact-resource DCR/audience gates
6. Send the single TASK-006 diagnostic request, with no retry

Required cleanup order on every success, rejection, timeout, signal, watchdog stop, rollback, or maintenance expiry:

1. Stop all further use and revoke refresh when issued; destroy access, refresh, cookie, code, verifier, state, client, request, and response artifacts
2. Delete any separately addressable task UI session key
3. Clear the task user's object permission using password-free `POST /user/update` with `{"user_id":"<task-user-id>","object_permission":{}}`, read back zero effective grants, then delete the user with `POST /user/delete` and `{"user_ids":["<task-user-id>"]}`
4. Prove task user, key, membership, and toolset associations absent
5. Delete the toolset by its returned ID, then prove ID 404, name count zero, and every baseline count/digest restored

Toolset deletion must be last because the supported delete removes only the toolset row and does not clean object-permission references. Deleting it while the principal remains linked could leave a stale grant ID and make cleanup proof ambiguous

If principal creation fails, clear/delete any supported-API-visible task identity first, then delete the proven task-owned toolset. If grant clear or user deletion fails, do not delete the toolset, continue bounded cleanup against the healthy rollback service, reject release, and escalate the critical security incident. If toolset deletion fails after principal cleanup, keep release rejected, prove no effective grant remains, retry only after exact ownership read-back, and escalate if baseline cannot be restored. Direct DB repair is never allowed

## Acceptance Criteria Coverage

- **AC-1: PASS.** The authorized supported Fedora reads resolved exact server ID `54a0ad17239e9f184882cf47e3ac277c`, canonical upstream member `find`, and digest `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd` without credential or payload retention
- **AC-2: PASS.** Supported create/list/get/update/delete requests and exact one-member shape are defined
- **AC-3: PASS.** The runtime permission map and principal object-permission invariant prove only upstream `find` is reachable, with no server, group, direct-tool, model, admin, or global grant
- **AC-4: PASS.** Independent cleanup, forward/reverse ordering, baseline counts/digests, rollback handling, and absence proof are defined
- **AC-5: PASS.** The handoff is signed in the task file; investigation performed no runtime mutation

## Documentation Impact

No steady-state product, architecture, technical, or CodeMap update is required. This evidence defines a temporary operational transaction only. TASK-015 must amend the approved SCR before execution

## Open Risks

- CRUD and principal grant are separate supported operations without a shared API transaction, so watchers and exact read-back are mandatory
- The toolset API accepts syntactically valid members without proving the live upstream catalog at create time; preflight and principal-scoped one-tool list close that gap
- Alias drift changes the gateway wire name even though stored membership remains `find`; exact fresh read mapping must therefore pass immediately before execution
- Redis toolset permission entries expire by TTL rather than being enumerated for deletion, but create/update/delete invalidate local caches and final authorization state is established through fresh supported reads and negative admission

## Recommended Next Step

PMA should hand TASK-015 the exact `defend_memory` temporary name, frozen member and digest, create-before-grant and principal-before-toolset-delete ordering, and expanded baseline/restoration proof. Runtime creation remains prohibited until TASK-015 amends the approved SCR and PMA activates execution

## Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-014 PASS. Authorized supported Fedora GETs resolve exactly one active `defend_memory` server, ID `54a0ad17239e9f184882cf47e3ac277c`, exposing exactly one canonical upstream `find`. Freeze the only member as `{"server_id":"54a0ad17239e9f184882cf47e3ac277c","tool_name":"find"}` with SHA-256 `e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd`. The credential remained in memory from its owner-only Fedora source and was never printed, hashed, copied, exported, passed in arguments, or retained. No tool invocation, mutation, deploy, direct database access, or NAS access occurred. TASK-015 may now authorize the exact create-before-grant and principal-before-toolset-delete transaction
