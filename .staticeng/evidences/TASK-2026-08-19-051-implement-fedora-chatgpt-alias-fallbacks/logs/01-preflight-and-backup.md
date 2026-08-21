# Preflight And Protected Backup

## Baseline

- Fedora service: healthy; readiness and liveliness HTTP 200; zero restarts
- Inventory: 27 deployment records
- Public associations: five account2-associated targets and account1-associated `gpt-5.6-sol`
- Qualified routes: six account1 absent-profile records and six distinct account2 profile-associated records
- Persistent/live public fallbacks: five existing inconsistent rules; public Luna missing
- Protected router policy: retries 3, allowed failures 1, cooldown 30.0, strategy `simple-shuffle`, cross-profile policy enabled

## Exact Transaction Predicates

The transaction selected only records whose `model_name` was exactly one of `gpt-5.4`, `gpt-5.4-mini`, `gpt-5.5`, `gpt-5.6-luna`, or `gpt-5.6-terra` and whose JSON parameters contained `chatgpt_auth_profile`. A temporary protected target set bound each selected database row identity, public alias, and exact before-value. The update joined on all three values

Preconditions asserted exactly five rows and five distinct aliases, exactly one absent-profile public Sol record, six absent-profile qualified account1 records, and six profile-associated qualified account2 records

## Protected Rollback

- Exact-value SQL: `/home/staticduo/docker/litellm/backups/TASK-2026-08-19-051/rollback-profile-values.sql`
- SQL mode: `0600`; rows: 5; SHA-256: `26efbe869ba5cd55a1d7b9ae057602a992da184709e6ec0a525f42bcae9561fd`
- Exact fallback snapshot: `/home/staticduo/docker/litellm/backups/TASK-2026-08-19-051/router-settings-before.json`
- Fallback snapshot mode: `0600`; SHA-256: `4a75be69f03567f3e68cf9aa02fe5ee73b02b01c24bae87d63c41bfc996324e0`
- Parent directory mode: `0700`
- Protected material remains on Fedora and outside repository evidence because it contains exact encrypted before-values and row identities

No credential, raw profile value, account identity, deployment ID, prompt, or response content is retained here
