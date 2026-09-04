# Exact Runtime Matrix

## Subjects

```text
candidate registry manifest: sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
candidate local config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
rollback registry manifest: sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
rollback local config: sha256:0a221cc57c07ae89e5a0223488351ff85ac30053771b22b43a94b3aa5361ae42
PostgreSQL local config: sha256:d741b376874687de90374fd34f55c6b2760e8f7bd7e4ae5cd47f50757fc08cf8
```

Each image started separately against a new labelled PostgreSQL 17 volume and private task network. Host publication was loopback-only with an ephemeral port. Each run used newly generated synthetic database/master/UI/user credentials and an `.invalid` email; evidence retained no values

## Exact Approved Procedure

The procedure tested in each runtime was:

1. `/user/new` with an opaque generated `user_id`, generated unique `user_email`, `internal_user_viewer`, `models=["no-default-models"]`, and `auto_create_key=false`
2. The immediately following `/user/update` identified only by returned `user_id`, with password as the only mutable field
3. `/login` by `user_id` with the correct password
4. `/login` by `user_email` with an incorrect password
5. `/login` by `user_email` with the correct password
6. Secret-safe database shape check, supported `/user/delete`, zero-row proof, and resource cleanup

```text
runtime   new   update-by-id   login-by-id   wrong-password-by-email   login-by-email   stored hash   delete   remaining
candidate 200   200            401           401                       303              scrypt: 71    200      0
rollback  200   200            401           401                       303              scrypt: 71    200      0
```

An additional matrix in both runtimes created an ID-only user and an email-bearing user. Both updates stored valid scrypt-shaped values. Both user-ID login attempts returned 401 regardless of whether the row also had an email, while correct email/password returned 303. This isolates lookup identity from password storage and role

## Classification

The results exclude password hashing, verification, schema migration, role, and candidate-versus-rollback drift. User-ID login fails before password verification because `authenticate_user` cannot find a row by its email-only query. Email login finds the same row and verifies the same stored hash successfully

## Cleanup

Both synthetic users in each broad matrix and the exact-procedure user in each focused run were deleted through `/user/delete`; database checks returned zero matching task users. Traps removed application and database containers, networks, and volumes after success and after intermediate command failures. Final label-filtered Docker inventory was empty
