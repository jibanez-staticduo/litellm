# Isolated DeepSeek Verification

## Summary

Created an owner-only temporary NAS boundary, restored an encrypted clone of staging into isolated PostgreSQL, immediately reduced it to the two DeepSeek aliases and one unrelated hosted-vLLM control, and removed all ChatGPT and credential references. The exact candidate digest passed readiness and liveliness on a loopback-only port, but the three retained model records did not load because their encrypted model parameters require staging's encryption context. The required exactly-three-model inventory invariant therefore failed, the live matrix was stopped, and every temporary resource was torn down

## Work Performed

- Captured production and original staging image, checksum, identity, health, restart, OOM, ownership, and permission baselines without recording secret values
- Created a mode `0700` task boundary and mode `0600` key/dump artifacts, streamed a staging `pg_dump` through AES-256-CBC/PBKDF2 encryption, and restored it into a dedicated PostgreSQL volume
- Pruned the clone transactionally to `deepseek-v4-flash-fp8-mtp`, `deepseek-v4-flash-fp8-mtp-norefusal`, and `qwen3.8-27b-refusal-dial`; verified three rows, zero ChatGPT references, and zero credential rows, then shredded the encrypted dump and its passphrase
- Started isolated PostgreSQL and Redis on an internal-only data network and the exact candidate on `127.0.0.1:41401`; no production mount, staging mount, ChatGPT credential mount, NPM network, or public bind was present
- Stopped immediately when router loading reported unresolved encrypted model parameters and the public inventory contained no loaded model groups
- Removed all task-labeled containers, networks, volumes, temporary keys/files, and the boundary directory; revalidated protected baselines

## Acceptance Criteria Coverage

- **AC-1: PASS**. Protected baselines were captured. Temporary resources were owner-only, task-labeled, isolated from NPM/public ingress, and had no protected deployment or credential mounts
- **AC-2: PASS**. The local clone was encrypted at rest, restored, immediately allowlisted to exactly three named records, verified with zero ChatGPT references and zero credential rows, and its dump material was shredded
- **AC-3: FAIL**. The exact candidate digest passed readiness/liveliness on loopback with isolated PostgreSQL and Redis, but the exactly-three-loaded-model inventory gate failed because cloned encrypted model parameters lacked their encryption context
- **AC-4: NOT RUN**. Direct and public request matrices were stopped at the AC-3 invariant failure
- **AC-5: NOT RUN**. Rejection/no-forwarding correlation was stopped at the AC-3 invariant failure
- **AC-6: NOT RUN**. The unrelated control and restart-persistence checks require a valid three-model inventory
- **AC-7: PASS**. All temporary resources and protected clone material were removed. Production and original staging identities, checksums, permissions, health, restart counts, and OOM state matched baseline
- **AC-8: PASS**. This redacted packet records the failed gate, complete teardown, residual boundary decision, and explicit promotion recommendation

## Documentation Impact

No steady-state product or architecture documentation changed. The approved contract remains correct; this run exposed an operational prerequisite for isolated database-clone verification

## Open Risks

- A resumed clone requires a deliberate encryption-context strategy. Transiently supplying staging's existing salt may preserve exact data semantics but extends secret exposure into the temporary boundary; independently re-encrypting only the three allowed records changes clone handling and needs an approved procedure
- The candidate still lacks live direct/staged matrix, no-forwarding, control-model, and restart-persistence evidence
- Repository-wide `staticeng_validate` remains blocked by inherited missing CodeMaps; deterministic repair dry-run cannot resolve the required module-boundary decisions

## Recommended Next Step

Do not promote the candidate to production. PMA should obtain an architecture decision for transient staging encryption context versus a separately re-encrypted three-model fixture, then resume this task from a clean boundary and run every remaining gate
