---
id: TASK-2026-09-03-016-investigate-internal-user-login
complexity: standard
track: investigation
slice: logic
status: superseded
superseded_by: TASK-2026-09-05-003-close-dual-host-repair
supersession_note: Historical email-login investigation retained; no final-image DCR lifecycle or deferred client-harness PASS inferred.
scr: SCR-2026-09-01-001-upstream-main-integration
parent: TASK-2026-09-03-017-fix-internal-user-login
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: Investigate internal-user login

## Objective

Reproduce in an isolated disposable database why `/user/new` plus password-only `/user/update` produces a least-privilege principal whose first `/login` returns 401, and determine the supported identity field or source correction.

## Acceptance Criteria

- [x] AC-1: Trace `/user/new`, `/user/update`, password hashing/storage, `/login`, and `authenticate_user` identity lookup.
- [x] AC-2: Test opaque user ID versus local email, login by user ID versus email, and password hash verification in disposable candidate and rollback runtimes.
- [x] AC-3: Identify whether harness usage, API contract, schema migration, or source behavior is defective.
- [x] AC-4: Recommend exact smallest fix/test/rollback or corrected supported procedure.
- [x] AC-5: No production principal/login/DB/config mutation; complete disposable cleanup and signed evidence.

## Handoff

[Agent Message] From: product_manager To: technical_architect

Use isolated disposable PostgreSQL and exact candidate/rollback images, never production credentials or DB. Reproduce the two-step lifecycle and test identity variants without logging generated secrets. Inspect source/tests. Determine if the correct supported login identifier is email or user_id and whether `/user/update` hashes passwords correctly. Research may create only disposable test principals in isolated DB. Destroy all resources and return exact fix/procedure.

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations

### Summary

PASS. Exact candidate and rollback runtimes behave identically: `/user/update` correctly hashes and stores the password, and `/login` authenticates database users only by case-insensitive `user_email`. The approved Fedora harness/SCR did not require or map that field and its opaque-identity path reproduces the observed 401, so this is a harness/SCR identity-field defect rather than a hashing, schema, migration, or runtime regression

### Work Performed

Inspected the nearest auth and management CodeMaps, the API request models, `/user/new`, `/user/update`, `hash_password`, `verify_password`, all three login handlers, `authenticate_user`, the Prisma user schema, and existing mapped tests

Ran secret-free source probes in exact candidate config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` and exact rollback config `sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42`. Both expose password only on `UpdateUserRequest`, use the same scrypt hash and verification functions, and query `authenticate_user` only by case-insensitive `user_email`

Started each exact image against a separate labelled disposable PostgreSQL volume and synthetic credentials. In both runtimes, supported `/user/new` and password-only `/user/update` returned 200, a correct email/password login returned 303, the same user's ID/password login returned 401, a wrong email/password login returned 401, and all stored task passwords were 71-character `scrypt:` values. The exact approved password-only-by-user-ID update procedure also passed

Deleted every synthetic principal through `/user/delete`, proved zero task users remained, and removed every task-labelled application container, PostgreSQL container, network, and volume. No production service, principal, login, database, configuration, image, registry, Fedora, or NAS resource was touched

### Acceptance Criteria Coverage

- **AC-1: PASS.** Evidence traces creation, update, hashing, storage, `/login`, and the email-only repository lookup
- **AC-2: PASS.** Candidate and rollback matrices prove user ID login fails, email login succeeds, wrong password fails, and stored scrypt hashes verify through the successful login path
- **AC-3: PASS.** The 401 is a harness/SCR field-mapping defect. The API/source contract is internally consistent but easy to misuse because the form field is named `username`; schema and migrations are not defective
- **AC-4: PASS.** The smallest correction is procedural: generate a unique local email-format login identity, pass it as `user_email` to `/user/new`, keep password-only `/user/update` targeted by returned `user_id`, and submit that same `user_email` as `/login` `username`. No source or image rebuild is required for this diagnostic
- **AC-5: PASS.** Only isolated synthetic data was used; cleanup is proven and evidence is secret-free

### Documentation Impact

The governing SCR uses "generated opaque local username" and "generated user ID" without mapping the login identity to `user_email`. Amend that operational contract to require a generated unique `user_email`-formatted identifier for `/login` while retaining the opaque `user_id` as the management and cleanup key. No steady-state product or architecture document changes are required because runtime behavior is unchanged. No CodeMap changes are required

### Open Risks

`/login` calls its input `username` while database authentication accepts only `user_email`, and current tests mock the email lookup but do not exercise `/user/new` -> password-only `/user/update` -> `/login` against a database. A later product decision may add `user_id` login, but broadening accepted identifiers is unnecessary for this one-run diagnostic and requires duplicate/collision semantics plus a regression/security review

### Recommended Next Step

PMA should revise the SCR and TASK-017 from source-fix scope to the exact supported procedure, then have Developer add one focused regression confirming email success, user-ID rejection, incorrect-password rejection, scrypt storage, unchanged least privilege, and cleanup. Reopen TASK-006 only after that contract update; do not rebuild the candidate for this issue

### Signed Handoff

[Agent Message] From: technical_architect To: product_manager

TASK-016 PASS. Candidate and rollback both hash password-only `/user/update` values correctly as scrypt and authenticate local database users only through case-insensitive `user_email`; `user_id` login returns 401 by design. The approved opaque-identity procedure omitted the required `user_email` mapping and exactly reproduces Reopen 5, so this is a harness/SCR defect, not an API, source, schema, or migration defect. Amend the principal contract to create a unique generated `user_email`, update by returned `user_id`, and log in with that email. Add the focused lifecycle regression, clean up as already specified, and do not rebuild or broaden authentication
