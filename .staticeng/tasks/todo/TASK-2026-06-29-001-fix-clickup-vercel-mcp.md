---
task_id: TASK-2026-06-29-001-fix-clickup-vercel-mcp
complexity: standard
track: implementation
slice: foundation
status: done
assigned_to: developer
handoff_from: product_manager
scr: none
parent: none
created: 2026-06-29
---

# Fix ClickUp And Vercel LazyMCP Registrations

## Context
LazyMCP discovery is slow because the LiteLLM MCP registry includes broken or timing-out MCP servers. Investigation found:

- `clickup` times out during MCP `tools/list`.
- `vercel` fails DNS resolution for `http://vercel-mcp-compat:8000/mcp`.
- Both currently appear with zero visible tools in `lazymcp_mcp_describe`.

Existing dirty worktree state is limited to StaticEng artifacts from prior orchestration and is not a blocker. Do not modify unrelated repository files.

## Active Discussions
- DISCUSSION-003: Fix LazyMCP ClickUp and Vercel registrations

## Acceptance Criteria

AC-1. `clickup` MCP discovery no longer times out during LazyMCP discovery.

AC-2. `vercel` MCP discovery resolves to a reachable upstream or is safely corrected to a working registration.

AC-3. `lazymcp_mcp_describe(server="clickup")` and `lazymcp_mcp_describe(server="vercel")` return usable tool metadata, or the task documents why a server cannot be repaired without missing external credentials/service and applies the safest available mitigation.

AC-4. LiteLLM logs after the fix do not show repeated `Timeout while listing tools from clickup` or `Name or service not known` for `vercel-mcp-compat` during verification.

AC-5. Evidence packet is written under `.staticeng/evidences/TASK-2026-06-29-001-fix-clickup-vercel-mcp/` with `SUMMARY.md` and relevant sanitized logs. Do not include secrets, tokens, API keys, or credential values.

## Constraints

- Prefer official/LiteLLM admin MCP operations over direct database writes.
- Do not print, persist, or expose secrets from MCP registry responses.
- Do not make code changes unless registry/config-only repair is impossible and PMA approves a narrower code task.
- Keep changes minimal: repair or safely disable/scope only the broken MCP registrations.
- Do not commit unless explicitly authorized by PMA after evidence review.

## Expected Evidence

- Current registry status for `clickup` and `vercel`, sanitized.
- Commands/tools used to repair or mitigate each server.
- Verification results from `lazymcp_mcp_describe` and relevant LiteLLM log snippets.
- Final recommendation if any external action remains.

## Handoff

[Agent Message] From: product_manager To: developer

Please repair the broken LazyMCP registrations for ClickUp and Vercel using the acceptance criteria above. Start with read-only diagnosis, then use LiteLLM admin MCP or safe local service checks to apply minimal registry fixes. Produce the evidence packet and return the shared output contract: Summary, Work Performed, Acceptance Criteria Coverage, Documentation Impact, Open Risks, Recommended Next Step.

# Post Implementation Task Updates

## Developer: Post Implementation Expectations

- Evidence packet written at `.staticeng/evidences/TASK-2026-06-29-001-fix-clickup-vercel-mcp/` with `SUMMARY.md` and sanitized logs.
- Vercel registry was corrected from `http://vercel-mcp-compat:8000/mcp` to the official `https://mcp.vercel.com` OAuth MCP upstream using LiteLLM admin MCP.
- ClickUp's original stdio registration was mitigated by removing it from the active LiteLLM registry after official ClickUp MCP was confirmed to require per-user OAuth and unauthenticated discovery could not produce tools.
- Post-restart verification did not show repeated `Timeout while listing tools from clickup` or `Name or service not known` for `vercel-mcp-compat`; expected unauthenticated OAuth 401s may still occur for official remote MCP endpoints.
- PMA should arrange per-user OAuth authorization or a supported upstream credential/passthrough flow before expecting `clickup` or `vercel` to return usable tool metadata through unauthenticated LazyMCP discovery.

## Reopen History

### 2026-06-29 PMA Reopen

User clarified that the authorized ClickUp skill/token exists on SSH host `fedora` under `opencode_defend`; use it to update this installed skill and OAuth/registration without exposing secrets. User also decided Vercel should be removed from this LiteLLM instance rather than repaired.

Updated acceptance for reopen:

- RAC-1. Locate the authorized ClickUp MCP/skill configuration on `fedora` under `opencode_defend` using safe read-only SSH inspection first.
- RAC-2. Update the local/current ClickUp skill and LiteLLM/Opencode OAuth or MCP registration using the good token/config, without printing or storing token values in conversation, logs, or evidence.
- RAC-3. Remove Vercel MCP from this LiteLLM instance.
- RAC-4. Verify `clickup` discovery returns usable tools or document the remaining exact auth/startup blocker; verify `vercel` is no longer visible in LazyMCP discovery.
- RAC-5. Append sanitized evidence to the existing evidence packet.

### 2026-06-29 Workflow Runner Reopen Results

- RAC-1: Met. Read-only SSH inspection found `opencode_defend` at `/home/staticduo/.config/opencode_defend` and the authorized ClickUp skill at `/home/staticduo/.config/opencode_defend/skills/clickup`. Only file metadata and env key names were recorded.
- RAC-2: Met. The authorized ClickUp skill was synced into `/home/staticduo/.config/opencode/skills/clickup`, and LiteLLM ClickUp MCP was registered from the authorized env through the admin API without printing token values.
- RAC-3: Met. Vercel MCP was removed from this LiteLLM instance; final LazyMCP discovery no longer lists `vercel`.
- RAC-4: Met. `lazymcp_mcp_describe(server="clickup")` returns usable ClickUp tool metadata, and `lazymcp_mcp_describe(server="vercel")` reports the server is unavailable.
- RAC-5: Met. Evidence was appended in `.staticeng/evidences/TASK-2026-06-29-001-fix-clickup-vercel-mcp/`, including `SUMMARY.md`, `logs/reopen_registry_status_sanitized.log`, and `logs/reopen_verification_sanitized.log`.

No product documentation changes were required because this was a registry/config repair. No commit was made per PMA instruction.
