# NAS GPT Alias Primary Account Evidence

## Summary

Changed only the eight NAS public ChatGPT Responses aliases so their primary deployments use the default `chatgpt` account. The unrelated `gpt-4o-mini-tts` OpenAI speech route was explicitly excluded and preserved

The eight account2 deployments, eight account3 deployments, eight qualified default deployments, all 32 unaffected model rows, and the exact 40-model public inventory remain present. Two bounded stateless Responses smokes returned HTTP 200 and selected the expected public default-profile deployments

## Work Performed

- Inventoried and safely classified the eight scoped aliases, all of which used account2 before the change
- Created a mode-0600 exact eight-row rollback transaction on NAS before mutation
- Removed only `chatgpt_auth_profile` from the eight scoped public deployment rows in one checked transaction, selecting the provider's default `auth.json` account
- Triggered the supported model-update reload path and verified DB plus API readback
- Preserved credentials, auth files, qualified deployments, unrelated rows, inventory, container identity, and Fedora

## Acceptance Criteria Coverage

- **AC-1: PASS**. `logs/01-inventory-before-sanitized.log` identifies all eight scoped ChatGPT Responses aliases as account2 before mutation and records the explicit `gpt-4o-mini-tts` exclusion without secrets
- **AC-2: PASS**. `logs/02-backup-and-update-sanitized.log` records the protected exact-row backup, SHA-256, checked rollback transaction, and reload plus revalidation procedure
- **AC-3: PASS**. `logs/03-readback-validation-sanitized.log` proves all eight public primary deployments resolve through the default profile after readback
- **AC-4: PASS**. The same log records eight account2 and eight account3 qualified deployments, an unchanged 40-model inventory, an unchanged hash for all 32 unaffected rows, the preserved excluded speech route, and retained fallback targets
- **AC-5: PASS**. `logs/04-routing-smokes-sanitized.log` records HTTP 200 for representative `gpt-5.5` and `gpt-5.6-sol` requests; each response deployment header matched the expected default-profile public deployment
- **AC-6: PASS**. `logs/05-health-fedora-sanitized.log` records NAS readiness and liveliness HTTP 200, unchanged healthy container identity, zero restarts, `OOM=false`, and byte-identical Fedora runtime identity fields before and after
- **AC-7: PASS**. This packet maps every AC to sanitized evidence. No steady-state product or architecture documentation update is required because this is an operational DB-backed routing selection change

## Documentation Impact

No product documentation update is required. The approved SCR, task update, and this evidence packet are the durable operational record

## Open Risks

The protected rollback transaction is intentionally stored only on NAS because it contains exact encrypted database row values. Repository evidence records only its path, mode, hash, row count, and secret-free execution procedure

`staticeng_validate` remains blocked by pre-existing repository-wide CodeMap gaps and broken `.staticeng/codemap.yml` links. The required repair dry run proposed hundreds of unrelated changes, so it was not applied in this atomic NAS routing task. See `logs/06-staticeng-validation.log`
