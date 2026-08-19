# NAS ChatGPT Auth Hygiene Repair

## Summary

Backed up and hardened the complete NAS ChatGPT auth root, refreshed default and account2 successfully, and identified account3 as the sole invalid profile. Account3's stored refresh grant is rejected by the provider with HTTP 401, and no already-authenticated account3 browser/session was available to complete reauthorization safely

NAS deployment remains **REJECTED**. Production independently re-entered account3 device authentication after the failed refresh, and the stable registry tag could not be resolved. LiteLLM remains healthy on 1.92.0 with all 40 models and all three profile registrations preserved; Fedora remains healthy on the candidate

## Work Performed

- Created and verified a protected 0700/0600 backup of all ten ChatGPT auth entries before mutation
- Hardened the live ChatGPT auth directory to 0700 and every entry to 0600, regular/non-symlink, owner `0:0`
- Used the supported refresh path exactly once per profile and retained only sanitized outcomes
- Proved default valid with HTTP 200 and account2 valid up to an allowed HTTP 429 provider quota/rate result
- Checked all available local/NAS authenticated sessions and browser controls without exposing account identifiers, credentials, URLs, or device codes
- Preserved NAS 1.92.0, exact 40-model/profile inventory, fallback registration, Fedora candidate, and all deployment files/routes
- Captured a fresh metadata baseline and an explicit deployment rejection

## Acceptance Criteria Coverage

- **AC-1: PASS**. `account3` is the affected profile; the exact sanitized category is OAuth refresh-grant rejection, `RefreshAccessTokenError`, provider HTTP 401
- **AC-2: PASS**. Backup and hardening checks prove the directory is 0700 and all ten files are 0600, regular, non-symlink, owner `0:0`
- **AC-3: FAIL**. Default and account2 refresh succeeded. Account3 could not be restored from an authenticated account3 session, and production independently held an account3 interactive-auth lock at the gate
- **AC-4: FAIL**. Default returned HTTP 200 and account2 returned only allowed HTTP 429. Account3 could not be invoked without starting another device flow after its refresh returned HTTP 401
- **AC-5: PARTIAL**. NAS remains healthy on 1.92.0 with 40 models and all three profile/topology families; Fedora remains healthy on the candidate. The prior stable tag returned not found on two read-only lookups
- **AC-6: PASS**. `.staticeng/evidences/TASK-2026-08-19-022-repair-nas-chatgpt-auth-hygiene/logs/03-preservation-baseline-and-decision.md` defines the fresh metadata baseline and rejects NAS deployment

## Documentation Impact

No product, architecture, or CodeMap update is required. This task changes transient host credential permissions/auth state only; this evidence is the operational record

## Open Risks

- Account3 requires reauthorization through an authenticated account3 session before production can safely use that fallback
- Production traffic can retrigger account3 device authentication while its refresh grant remains invalid
- The stable registry tag must be restored or explicitly dispositioned before any release gate can assert it remained unchanged

## Recommended Next Step

PMA should keep NAS deployment blocked. Reauthorize account3 from an authenticated account3 browser/session, prove all three direct profile checks without auth/device errors, confirm no account3 lock or new device prompt remains, resolve the missing stable tag, then recapture metadata immediately before deployment
