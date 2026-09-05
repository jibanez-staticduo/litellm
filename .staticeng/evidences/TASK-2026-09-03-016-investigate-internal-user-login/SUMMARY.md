# TASK-2026-09-03-016 Evidence Summary

## Summary

PASS. Exact candidate and rollback images reproduce the same contract: password-only `/user/update` stores a valid scrypt hash, `/login` succeeds with `user_email`, and `/login` rejects `user_id`. The approved Fedora procedure did not require or map `user_email`, and its opaque-identity path exactly reproduces the 401. The smallest correction is to use a generated unique local email value for authentication while retaining `user_id` for update, grants, and cleanup

## Acceptance Criteria Coverage

- **AC-1: PASS.** `.staticeng/evidences/TASK-2026-09-03-016-investigate-internal-user-login/logs/01-source-contract.md` traces request parsing, creation, update, hashing, schema storage, login handlers, and `authenticate_user`
- **AC-2: PASS.** `.staticeng/evidences/TASK-2026-09-03-016-investigate-internal-user-login/logs/02-runtime-matrix.md` records matching candidate and rollback HTTP behavior, hash shape, negative-password behavior, supported deletion, and cleanup
- **AC-3: PASS.** The defect is in harness/SCR identity mapping. Hashing, source execution, schema, and migrations behave correctly
- **AC-4: PASS.** `.staticeng/evidences/TASK-2026-09-03-016-investigate-internal-user-login/logs/03-fix-procedure.md` gives the exact no-rebuild procedure and bounded optional source hardening
- **AC-5: PASS.** All credentials and identities were synthetic and ephemeral; no values are retained. Every labelled container, network, and volume is absent and no production resource was used

## Verification

- PASS: exact candidate config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` against an isolated disposable PostgreSQL database
- PASS: exact rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42` against a separate isolated disposable PostgreSQL database
- PASS: both runtime matrices returned 200 for create and update, 401 for user-ID login, 401 for incorrect email/password, 303 for correct email/password, and 200 for supported deletion
- PASS: both databases stored one 71-character `scrypt:` value for the exact supported procedure; the successful email login exercised `verify_password`
- PASS: post-delete task user count was zero in each runtime
- PASS: Docker filters returned zero task-labelled containers, networks, and volumes after cleanup
- PASS: source probes show identical `authenticate_user`, `_hash_password_in_dict`, `hash_password`, and `verify_password` implementations in candidate and rollback
- PASS: `staticeng_validate` reports all source directories indexed, valid hierarchy, and zero warnings

## Safety Boundary

No production credentials, data, database, network, container, principal, login, configuration, service, registry, Fedora, or NAS resource was used or changed. Generated IDs, emails, passwords, master keys, database passwords, request bodies, cookies, and session tokens were never written to evidence

## Documentation Impact

The approved SCR needs an operational wording correction from opaque "username" to a generated unique `user_email`-formatted login identifier. Runtime architecture and CodeMaps remain unchanged

## Signed Evidence

[Agent Message] From: technical_architect To: product_manager

TASK-016 evidence proves the production failure was a login-identifier harness defect. Use `user_email` for `/login`, retain returned `user_id` for password update and cleanup, add the lifecycle regression, and do not rebuild the image for this issue
