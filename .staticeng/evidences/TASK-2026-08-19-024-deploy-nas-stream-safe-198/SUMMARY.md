# NAS Stream-Safe 1.98.0 Deployment Evidence

## Summary

The NAS release is **REJECTED AND ROLLED BACK**. Three bounded deployment attempts were stopped by verification-harness assertions before candidate functional testing. Every attempt restored NAS to the protected 1.92.0 digest and exact wrapper/Compose rollback pair. After the first failed attempt, Fedora was restored to its pre-release digest as required to avoid a split release. Stable remained in its inherited unresolved state and was not mutated

The final NAS rollback is healthy with the exact 32-model default/account2 topology, account3 quarantine, protected routing hashes, dependencies, volumes, and networks. The strict credential gate also detected recurring ctime-only drift on one salted lock-file path without size, mtime, inode, owner, mode, or log-event changes. Because the Tech Lead gate requires exact ctime equality for unaffected entries, this is independently release-blocking and requires Tech Lead disposition before another attempt

## Work Performed

- Captured three fresh T0 gates within 60 seconds of each attempted recreation; each had safe 0700/0600 auth permissions, zero preceding 15-minute auth/device-flow failure matches, exact 32-model/routing hashes, unchanged dependency IDs, and tested rollback artifacts
- Pulled and selected only immutable candidate manifest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, then recreated only NAS `litellm` with `--no-deps`
- Applied the mandatory rollback after each failed assertion, restoring NAS digest `sha256:264774f4a3bb1d01a393b844270f7e71629da996a182295c77675fe2793c6018` plus wrapper/Compose hashes `ada13e55...c8778` and `e55a6827...4129`
- Restored Fedora to pre-release digest `sha256:2e947963eddbd9385e618d5bd3e122f41a5677a05b843b5add29cef3d52991e9` after the first failed NAS release attempt
- Stopped after three attempts and requested Tech Lead help through PMA as required

## Acceptance Criteria Coverage

- **AC-1: FAIL STRICT GATE**. T0 pre-deploy checks passed, but one salted lock-file path showed recurring ctime-only drift after rollback without a permitted successful-refresh correlation
- **AC-2: FAIL**. The candidate was selected by exact digest and only LiteLLM was recreated, but the deployment was rolled back before acceptance; NAS does not remain on 1.98.0
- **AC-3: NOT COMPLETED**. Candidate health was reached during attempts, but the mandatory assertion stop prevented the candidate 10-minute observation and full startup/log acceptance matrix
- **AC-4: PASS AFTER ROLLBACK**. The exact 32-model inventory, 16-rule routing hash, default/account2 topology, zero account3 rows/references, dependencies, protected files, volumes, and networks are preserved on restored 1.92.0
- **AC-5: NOT RUN AFTER STOP**. Native Responses and corrected Codex gates were not invoked after the mandatory deployment assertion failure
- **AC-6: NOT RUN AFTER STOP**. LazyMCP status, describe, tool-list, and harmless tool smoke were not invoked after the mandatory deployment assertion failure
- **AC-7: FAIL ORIGINAL PRESERVATION, PASS ABORT SAFETY**. Fedora could not remain on the candidate after release failure; it was restored to its pre-release digest by the explicit reverse-rollback rule. Stable was not changed
- **AC-8: PASS REJECTION EVIDENCE**. Logs record T0 approval, all attempts, exact rollback state, preservation, rejection, and escalation

## Documentation Impact

No product, architecture, technical, or CodeMap update is required. No application source changed; this evidence records operational deployment and rollback truth

## Open Risks

- The NAS release remains incomplete and both hosts are now on their pre-release images
- The candidate manifest digest and NAS-local config ID are distinct (`42d365...` manifest, `45a019...` config); the next harness must validate both fields against their correct identities
- One protected lock-file ctime changes repeatedly while every other captured field and sanitized log gate remains stable; the current strict gate rejects this and needs Tech Lead classification
- Stable remains unresolved exactly as inherited from the preceding tasks
- `staticeng_validate` remains blocked by pre-existing broken links and repository-wide missing CodeMaps; repair dry-run proposed broad unrelated changes and was not applied

## Recommended Next Step

PMA should route this evidence to Tech Lead. Tech Lead should correct the manifest-versus-config identity assertion, disposition the lock-file ctime behavior without weakening credential-file checks, then reopen this task for one controlled redeployment from the verified rollback state
