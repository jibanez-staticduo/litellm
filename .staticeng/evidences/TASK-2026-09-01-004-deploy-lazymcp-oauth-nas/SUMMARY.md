# TASK-2026-09-01-004 Reopen 1

## Summary

NAS deployed the exact Fedora-approved image and passed representative functional, preservation, cross-host identity and 900-second resource checks. Both hosts remain healthy on that same release. Full acceptance is pending for two concrete live limitations: NAS Astra Chat deployment cooldown and unscoped standard MCP initialization timeout. The task is not marked done

## Work Performed

Verified the actual NAS host/daemon/Compose path, prepared owner-only DB/config/mounted-state recovery, checked schema compatibility and applied the exact selector with persistent 8-GiB/no-swap/restart-disabled LiteLLM containment. Recreated only LiteLLM with --no-deps. Preserved all four dependencies and NAS-specific config/environment. Ran real SDK models and read-only MCP calls, public discovery/challenges, the complete 900.46-second soak and fresh Fedora functional/identity checks

Source: 7a9ef0335303d973f3a228dcf7baadff18c82fb5. Both selectors: docker.staticduo.com/litellm@sha256:7b2368711ff10db3107772d627e03aa89319598f8897ff7431497775926b2eb9. The amd64 child is 9753f91ea752ddc7e01c03d282d8a059c08297e6ed66a9271744b89324415065, config 02a12f580ddbaddc0e27529901d629fb54d4ec571257af7afe090f9decf4850f

## Acceptance Criteria Coverage

| AC | Result | Evidence |
| --- | --- | --- |
| AC-1 | PASS: independent Fedora authorization preceded NAS mutation | logs/01-preflight-deployment.md |
| AC-2 | PASS: owner-only DB, selectors/config/wrappers and mounted state captured | logs/01-preflight-deployment.md |
| AC-3 | PASS under Reopen 1 containment amendment: only LiteLLM selector/limits/restart changed and only LiteLLM recreated | logs/01-preflight-deployment.md, logs/03-functional-final.md |
| AC-4 | PASS: exact OCI image/source parity, healthy, zero restarts/OOM; engine-specific image ID representation explained | logs/01-preflight-deployment.md, logs/03-functional-final.md |
| AC-5 | PARTIAL: SDK Responses, available-model Chat, LazyMCP, selected standard MCP and real read-only calls pass; Astra Chat 429 and aggregate MCP 504 remain open | logs/03-functional-final.md |
| AC-6 | PARTIAL: 900-second memory/health and final parity pass; no-regression/clean-log disposition remains open for live failures | logs/02-soak.jsonl, logs/03-functional-final.md |
| AC-7 | Recovery ready, not exercised; no split release or proven candidate regression, no destructive DB restore | logs/01-preflight-deployment.md, logs/03-functional-final.md |

## Documentation Impact

No product documentation change is needed. SCR records the latest explicit NAS authorization; task and registry record actual runtime state and pending acceptance. StaticEng validation passed with zero warnings. No source or UI change, so no new source build/test or screenshots are applicable

## Open Risks

Astra Chat has no currently available deployment outside cooldown even though Astra Responses and other Chat aliases pass. Unscoped /mcp initialization hits a 30-second 504 with three unhealthy Frigate registrations; selected Memory transport works. Causality versus the prior image is not established. Do not claim those failures as successful tests or an all-provider/all-MCP release PASS

Security rotation recommendations from earlier private-output handling, maintenance-tool findings and additional supply-chain review remain deferred. No new full security qualification is claimed. Backup listing/checksum and inherited isolated schema rollback evidence are not a fresh complete production-data restore rehearsal

## Recommended Next Step

PMA should disposition the two observed live limitations or route bounded same-scope diagnosis, keeping the healthy contained same-image runtimes and protected recovery available. Do not start unrelated security remediation or harness work. Final task closure remains with PMA
