# Exact Correction Procedure

## Required Operational Correction

No source correction or rebuilt image is needed for the temporary diagnostic principal

1. Generate two distinct values: an opaque `user_id` with the existing entropy requirement, and a unique synthetic email-format login value with equivalent entropy in its local part. For the Fedora diagnostic, use a task-owned non-routable domain so no invitation or email is sent
2. Send both values in `/user/new` together with the already approved least-privilege role, denied models, no-key setting, and exact temporary toolset grant
3. Use the returned `user_id` as the target of the immediately following `/user/update`; send password as its only mutable field
4. Verify unchanged least-privilege state through the existing supported read-back
5. Send the generated `user_email`, not `user_id`, in `/login` form field `username`
6. Retain `user_id` as the authoritative key for grants, session-key cleanup where addressable, `/user/delete`, deadline-worker state, and baseline-restoration proof
7. Preserve every existing no-gap, one-login, one-request, secret handling, cleanup, rollback, deadline, Fedora-only, and NAS exclusion condition

The generated email is an authentication credential component and must follow the existing owner-only handling rule. Evidence may retain only status classes and non-reversible correlation fingerprints, never the email itself

## Regression Contract

TASK-017 should add one focused database-backed lifecycle regression, preferably in the existing mapped auth/management test modules, which proves:

```text
/user/new(user_id, user_email, internal_user_viewer, denied models, no key)
/user/update(user_id, password only)
/login(username=user_id, correct password) -> 401
/login(username=user_email, wrong password) -> 401
/login(username=user_email, correct password) -> success
stored password is scrypt, not plaintext
role/models/permissions/memberships remain unchanged
supported cleanup removes generated key/session, principal, and grants
```

This test must fail if the harness substitutes `user_id` for email, password hashing is removed, incorrect passwords authenticate, update broadens the principal, or cleanup leaves task state

## Optional Product Hardening

If product requirements later demand database login by opaque `user_id`, change only the repository lookup in `authenticate_user` to an explicit OR over exact `user_id` and case-insensitive `user_email`, then define and test collision precedence. That is a broader authentication contract and is not recommended for the current diagnostic. It would require security review because accepting another identifier changes account enumeration and ambiguity behavior

The smaller usability hardening is to rename user-facing login copy to "Email" and improve the invalid-credentials message while keeping one generic 401 response. That also is not required to unblock TASK-006

## Rollback

For the recommended procedural correction, rollback is simply to stop before login/use, clear the grant, delete the principal by `user_id`, delete the temporary toolset in the existing order, and prove baseline restoration. There is no image, source, schema, migration, or configuration rollback
