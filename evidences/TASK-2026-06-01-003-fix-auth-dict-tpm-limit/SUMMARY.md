# TASK-2026-06-01-003 Evidence Summary

## Result

- Status: completed
- Production branch: `staticduo-production-main` pushed to `fork/main`
- Code commits:
  - `f11607cbf3 fix(auth): handle cached user dict limits`
  - `08a3aac163 fix(auth): use cached user dict accessor`
- Deployed image: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-main-20260601`
- Deployed digest: `sha256:2d048ed762d694b37e249df47247d8994b29c8e18f9239454976d76ea8900b85`
- Deployed container image id: `sha256:ab75ad44ea89242baa2e386f94950e53f067f6a11dd70de5117091ae717de782`

## Acceptance Criteria

- AC-1: Fixed `user_obj.tpm_limit` / `user_obj.rpm_limit` by reading cached users through dict/object-safe accessors.
- AC-2: Audited same-scope auth paths and fixed additional cached user dict reads for `user_role`, `spend`, `max_budget`, `models`, `user_id`, and `user_email` in auth flow helpers.
- AC-3: Added focused regression coverage for cached user dict `tpm_limit`/`rpm_limit` and shared accessor behavior.
- AC-4: Ran focused tests and Black. See `logs/tests.log`.
- AC-5: Pushed fork `main` without force through `08a3aac163` before final deployment.
- AC-6: Deployed with `/home/staticduo/git/release-litellm.sh --workdir /tmp/opencode/litellm-production-main`. See `logs/deploy.log`.
- AC-7: Health is healthy/readiness 200 and final log scan shows zero matching auth dict attribute errors. See `logs/health-after.log` and `logs/error-scan-after.log`.

## Verification

- Focused tests: `3 passed, 93 deselected` for `return_user_api_key_auth_obj or get_user_object_value`.
- Health: Docker health `healthy`; internal `/health/readiness` returned `200` with `{"status":"healthy","db":"connected"}`.
- Log scan counts:
  - `tpm_limit_attr_error=0`
  - `user_role_attr_error=0`
  - `spend_attr_error=0`
  - `generic_dict_attr_error=0`
  - `generic_object_attr_error=0`
  - `auth_exception=0`

## Rollback

- Release script rollback marker: `docker.staticduo.com/litellm:rollback-20260601-071044`.
- Because the same date tag was reused during this incident, the rollback marker points at the final deployed digest. If a pre-final rollback is needed, the previous published digest observed during this task was `docker.staticduo.com/litellm@sha256:287e48736c75b7cbfe2c4641e6cb42415e1d8e5456aa94b160c970633c376bd9`.
