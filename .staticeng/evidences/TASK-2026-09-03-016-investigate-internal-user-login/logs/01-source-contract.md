# Source Contract Trace

## Request And Persistence Path

`NewUserRequest` defines `user_email` and `user_id` but no password. `/user/new` validates duplicate IDs/emails, normalizes requested internal-user fields, and calls `generate_key_helper_fn`. With `auto_create_key=false`, the helper inserts only `LiteLLM_UserTable`; its `user_data` preserves `user_id` and nullable `user_email`

`UpdateUserRequest` defines `password` and requires either `user_id` or `user_email`. `_update_single_user_helper` serializes only explicitly supplied fields, runs `_hash_password_in_dict`, finds the target row, checks authorization, then writes through `prisma_client.update_data`. The approved password-only payload targeted by `user_id` therefore writes no identity, role, model, membership, or grant field

`_hash_password_in_dict` calls `hash_password`, which uses scrypt with a random 16-byte salt and emits `scrypt:` plus base64 salt and derived key. `LiteLLM_UserTable.password` is nullable `String` in the Prisma schema. `verify_password` parses the scrypt value and compares derived keys in constant time; legacy lowercase SHA-256 hashes remain supported

## Login Path

`POST /login`, `/v2/login`, and `/v3/login` all pass their `username` input unchanged to `authenticate_user`. Before checking the password, `authenticate_user` performs one database lookup:

```text
where={"user_email": {"equals": username, "mode": "insensitive"}}
```

It does not query `user_id`, `user_alias`, or `sso_user_id`. If no email row is found, the non-admin path returns 401 without reading the stored password. If a row is found, correct credentials pass `verify_password` and mint the bounded UI key/session; incorrect credentials return 401

The function documentation consistently says database login uses email/password and the invite-link `user_email`/password pair. The HTML form field name `username` is only an input label and is not a second database identity contract

## Candidate And Rollback Comparison

Both exact images report:

```text
NewUserRequest password field: false
UpdateUserRequest password field: true
_hash_password_in_dict SHA-256: f0380ecfeb192f163733ca6ac647029562bd466034595e3630c9ea0aac657016
authenticate_user SHA-256: 5382245b66d578d0fa7e4f1ad57079482f0eb91de313b402ad49a9628a7caad9
hash_password SHA-256: 0fffe6a3c97836d4e25868364f71269a497dd386aca6f288e05bdbba73ae9670
verify_password SHA-256: a0c0351488978c3ea7a7932b4e2079e8d38d6321aaf36eaca03ad2fbbb581572
```

The candidate source commit and rollback source commit contain byte-identical `login_utils.py`. The candidate has unrelated `/user/update` evolution, but the exact runtime matrix proves no behavioral difference at this boundary

## Existing Test Gap

Mapped unit tests cover case-insensitive email lookup, correct and incorrect password behavior, and password helper properties. They do not compose supported `/user/new`, password-only `/user/update`, and `/login` against a real database, and they do not make the intended user-ID rejection explicit. That gap allowed the operational harness to treat the form field name `username` as opaque `user_id`
