# Tech Lead continuation

The original metadata replay and initialize-probe corrections are retained. The aggregate adds a per-peer AnyIO deadline around complete setup, listing and permission filtering. Expiry is classified as timeout even if an inner client absorbs cancellation. The boundary introduces no detached task, registration change, fallback bypass or scoped-route error change

## Verification output

Command: `.venv/bin/python -m pytest tests/test_litellm/test_router_model_cost_isolation.py tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server.py -q`

Result: 295 passed, 4 warnings in 68.22s, no skips. Warnings are the existing Starlette httpx and datetime.utcnow deprecations

Command: `.venv/bin/python -m pytest tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server_manager.py::TestMCPServerManagerUpstreamInstructionsCache tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server_manager.py::TestHealthCheckInterpolatesGlobalEnvVars -q`

Result: 8 passed, 1 Starlette warning in 5.73s, no skips

Six new parameterized cases pass: headers, client creation and upstream listing each tested for deadline expiry with healthy peer success, and caller cancellation with child drain. Each checks no new pending asyncio tasks remain

Production Ruff: All checks passed for router.py, mcp_server_manager.py and server.py. Edited server test formatting: already formatted. git diff --check: PASS. staticeng_validate: PASS, warnings=0

## Baseline OAuth attribution

Clean detached checkout `/tmp/opencode/litellm-residual-baseline` at `1ac8bbeba0ff4af8392450523f6f0b6ab218757b`, using the same Python environment

Command: `/home/staticduo/git/litellm/.venv/bin/python -m pytest tests/test_litellm/proxy/_experimental/mcp_server/test_mcp_server_manager.py::TestOAuthDiscoverySSRFGuard::test_cross_origin_allowed_when_resolves_to_public_ip -q`

Result: 1 failed, 1 warning in 8.39s. Expected authorization server list, received []

Direct baseline import inspection confirms the imported manager source is inside the clean detached checkout and `hasattr(MCPServerManager, "_fetch_oauth_discovery_url")` is False. Its `_fetch_oauth_metadata_from_resource` calls that absent method and absorbs the resulting exception. This is a real pre-existing source issue, not caused by either changed manager path, the aggregate deadline, the network, or the test host's DNS. Per PMA direction no unrelated OAuth source or harness repair is included. The failing baseline assertion is not represented as a passing test

## Live identity read-back

Both exact containers remain running and healthy, restarts=0, OOMKilled=false. No deployment was performed during source verification

NAS container: `6b6f8743c69dab2a768dc76bef046511c7486bf0627d3fc0bc0a587bd4ff314c`

Fedora container: `164bab0c75f9294a3a7977420c2fda7686acb7a7bc5317af2d0768021b721264`

Both configured selectors: `docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9`. NAS engine image ID is config `sha256:02a12f580ddbaddc0e27529901d629fb54d4ec571257af7afe090f9decf4850f`; Fedora engine image ID is the selected OCI index. These retain the parent task's engine representation distinction

Git pull --ff-only reported already up to date. HEAD and origin/main both equal `1ac8bbeba0ff4af8392450523f6f0b6ab218757b` before this task's changes are committed. Unrelated watchdog source/evidence edits are preserved and not attributed to this task
