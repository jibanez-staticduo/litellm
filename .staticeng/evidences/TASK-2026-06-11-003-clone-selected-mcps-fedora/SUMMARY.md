# TASK-2026-06-11-003 First-Pass Evidence

## Scope Completed

Registered the first-pass selected MCPs on Fedora LiteLLM using `ssh fedora` and Fedora local API `http://127.0.0.1:4000/v1/mcp/server`.

## MCPs Registered

- Notion
- ClickUp
- Exa_Web_Search
- Context7
- LiteLLM_Admin

## Verification

- Fedora endpoint used: `http://127.0.0.1:4000/v1/mcp/server`
- Fedora list count after first pass: 5
- Fedora MCP names after first pass: ClickUp, Context7, Exa_Web_Search, LiteLLM_Admin, Notion
- Registration method: POST attempted first; existing records were updated with PUT where POST returned already-exists.

## Acceptance Criteria Progress

- AC-1: Not evaluated in this first pass; Docker/local clone intentionally not started.
- AC-2: Partially covered for selected online/stdio first-pass MCPs.
- AC-3: First-pass Fedora list contains only the five first-pass selected MCPs.
- AC-4: Covered for first pass; LiteLLM_Admin points to `http://litellm-admin-mcp-compat:8000/mcp` on Fedora.
- AC-5: First-pass list verification completed; health checks deferred to later task phase unless requested for this pass.

## Evidence Logs

- `.staticeng/evidences/TASK-2026-06-11-003-clone-selected-mcps-fedora/logs/first-pass-source-inventory-redacted.json`
- `.staticeng/evidences/TASK-2026-06-11-003-clone-selected-mcps-fedora/logs/first-pass-fedora-registration-redacted.json`
- `.staticeng/evidences/TASK-2026-06-11-003-clone-selected-mcps-fedora/logs/first-pass-summary-redacted.json`
- `.staticeng/evidences/TASK-2026-06-11-003-clone-selected-mcps-fedora/logs/first-pass-fedora-registration-stderr-redacted.log`

No secrets are intentionally included in evidence.
