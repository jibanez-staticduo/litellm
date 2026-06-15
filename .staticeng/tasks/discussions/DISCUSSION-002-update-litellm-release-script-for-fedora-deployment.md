---
id: DISCUSSION-002
title: "Update LiteLLM release script for Fedora deployment"
status: closed
summarized_by: business_analyst
source: runtime-transcript
---

# Discussion Summary

## Topic
Update the LiteLLM release/build script so it also updates the Fedora LiteLLM deployment after building the new image.

## Purpose
The user requested committing the completed MCP stale-permission cleanup work to `staticduo-production-main`, running the existing LiteLLM update/build script with new upstream commits, resolving any merge issues, creating the image, and extending the script so Fedora is updated in addition to the NAS/local LiteLLM deployment.

## Repository Truth Relevant To This Discussion
- The working repository for the completed bug fix is `/home/staticduo/git/litellm`.
- The Fedora deployment repository/path referenced for remote work is `/home/staticduo/docker/litellm` on host `fedora`.
- The local LiteLLM MCP/admin instance for this session must not be touched through the `litellm_admin` MCP.
- The existing script already updates LiteLLM on the NAS/this computer after image creation.
- There were pre-existing local changes in `.staticeng` and `.gitignore` that the PM intended to inspect before delegation to avoid overwriting unrelated work.
- Completed bug-fix evidence exists at `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/SUMMARY.md`.

## Facts Established
- A LiteLLM MCP stale-reference cleanup fix was completed locally before this new request.
- Completed code changes include:
  - `litellm/proxy/_experimental/mcp_server/db.py`: added MCP reference cleanup for permissions and credentials.
  - `litellm/proxy/management_endpoints/mcp_management_endpoints.py`: `DELETE /v1/mcp/server/{server_id}` deletes the real server and cleans permissions/credentials; returns `202` when an ID is stale but referenced and cleanup succeeds; keeps `404` when the server ID is neither present nor referenced.
  - `litellm/proxy/management_helpers/object_permission_utils.py`: stale IDs no longer become effective or listable access.
- Tests were added in:
  - `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`
  - `tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
- Validation already completed for the bug fix:
  - `uv run python -m pytest tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
  - Result: `110 passed, 7 warnings`.
  - `uv run ruff check ...`
  - Result: `All checks passed`.
- Tech Lead review for the bug fix completed with no blocking findings.
- The bug fix had not yet been committed or deployed when the user made the new request.
- The user wants the release/update script run with new upstream commits, merge conflicts fixed if they occur, and the image created.
- The user expects the script itself to update the NAS/local LiteLLM after image creation and wants it modified to also update Fedora.

## Requirements Captured
- Commit the completed local changes to branch `staticduo-production-main`.
- Run the LiteLLM update/build script so it incorporates new upstream commits.
- Resolve merge issues caused by upstream updates if they occur.
- Create the updated LiteLLM image.
- Modify the release/update script so that, after image creation, it also updates the Fedora LiteLLM deployment.
- Preserve the existing behavior where the script updates LiteLLM on the NAS/this computer.
- Perform Fedora deployment work only through SSH to `fedora` and commands inside `/home/staticduo/docker/litellm`, or by passing context to the referenced remote/session agent if needed.

## Constraints
- Do not touch or operate the local/session MCP `litellm_admin` instance.
- Use SSH to `fedora` for Fedora work.
- Use `/home/staticduo/docker/litellm` as the Fedora deployment repository/path.
- Avoid overwriting unrelated existing changes, especially pre-existing `.staticeng` and `.gitignore` changes.
- Follow normal git safety: inspect status/diff/log before committing and stage only intended files.
- The release script change should not remove the current NAS/local update behavior.

## Non-Goals
- Do not deploy or administer through the local `litellm_admin` MCP.
- Do not optimize the MCP cleanup implementation beyond the completed bug fix unless separately requested.
- Do not redesign the whole release pipeline unless necessary to satisfy the Fedora update requirement.

## Decisions Made
- Fedora-related actions must use `ssh fedora` and the remote path `/home/staticduo/docker/litellm`.
- The local/session LiteLLM MCP admin integration is explicitly out of scope for deployment operations.
- The release/update script should be extended to update Fedora in addition to the NAS/local LiteLLM update it already performs.

## Assumptions
- `staticduo-production-main` is the target branch for committing the completed bug fix and any release-script changes.
- The existing LiteLLM release/update script is present in the repository or deployment tooling and is responsible for pulling/updating upstream, building the image, and updating the NAS/local LiteLLM instance.
- Fedora can be reached via the configured SSH alias `fedora`.
- The Fedora deployment uses the repository or compose setup located at `/home/staticduo/docker/litellm`.

## Open Questions
- Exact path/name of the LiteLLM update/build script was not specified in the transcript.
- Exact desired Fedora update command sequence after image creation was not specified.
- Whether the commit should include only the completed bug fix first, or combine the bug fix and script modification in one or multiple commits, was not explicitly stated.
- Whether the script should fail the whole release if the Fedora update fails, or report Fedora failure while preserving NAS/local update success, was not specified.
- Whether remote Fedora update requires restarting services, pulling compose changes, loading/pulling a built image, or running another deployment command was not specified.

## Risks Or Concerns
- Merge conflicts may occur when incorporating new upstream commits and must be resolved without losing the completed MCP stale-reference fix.
- The MCP cleanup fix has residual technical risks: cleanup is not wrapped in a real transaction and scans permissions in Python; accepted for the bug fix but potentially inefficient at very high volume.
- Touching the wrong LiteLLM instance through `litellm_admin` could affect the current session environment and is explicitly prohibited.
- Fedora deployment automation could break existing NAS/local update behavior if the script change is not carefully scoped.
- Pre-existing `.staticeng` and `.gitignore` changes may be unrelated and should not be accidentally committed or reverted.

## Referenced Files Or Areas
- `.staticeng/.config/runtime/discussions/DISCUSSION-002-transcript.md`
- `.staticeng/evidences/TASK-2026-06-10-001-fix-mcp-delete-stale-permissions/SUMMARY.md`
- `litellm/proxy/_experimental/mcp_server/db.py`
- `litellm/proxy/management_endpoints/mcp_management_endpoints.py`
- `litellm/proxy/management_helpers/object_permission_utils.py`
- `tests/test_litellm/proxy/management_endpoints/test_mcp_management_endpoints.py`
- `tests/test_litellm/proxy/management_helpers/test_object_permission_utils.py`
- `.staticeng`
- `.gitignore`
- Fedora host: `fedora`
- Fedora deployment path: `/home/staticduo/docker/litellm`
- Target branch: `staticduo-production-main`

## Recommended Workflow Next Step
- assigned_to: tech_lead
- why: Requires git/branch hygiene, upstream merge handling, release-script modification, image build/deployment validation, and protection against touching the prohibited local `litellm_admin` MCP instance.
