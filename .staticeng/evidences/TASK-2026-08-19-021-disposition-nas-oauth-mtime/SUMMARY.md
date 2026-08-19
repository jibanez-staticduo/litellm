# NAS OAuth Mtime Drift Disposition

## Summary

Read-only metadata and sanitized log review rejects NAS deployment authorization. The changed 3855-byte ChatGPT credential file was atomically rewritten at `2026-08-18T23:03:32Z`, exactly when the running service logged a failed OAuth refresh and started device-code authentication. This is attributable to the service's credential writer rather than an unexplained replacement, but it is not a successful routine refresh and an auth-flow trigger cannot be excluded

No credential contents were read. No host file, container, service, model, credential, image tag, or configuration was changed

## Work Performed

- Compared the current ChatGPT, Anthropic, and service-account mount metadata with the approved NAS preflight and TASK-020 postflight
- Verified all credential entries are regular non-symlink files or expected directories, with current root ownership
- Correlated the changed file mtime with sanitized service-log event classes only
- Reviewed the 1.98.0 authenticator write path, which uses a mode-0600 temporary file plus atomic `os.replace` for refresh, device-code request markers, and completed login records
- Defined the required just-in-time pre/post metadata and sanitized-log gate in `.staticeng/evidences/TASK-2026-08-19-021-disposition-nas-oauth-mtime/logs/01-read-only-disposition.md`

## Acceptance Criteria Coverage

- **AC-1: FAIL**. Unauthorized replacement is not indicated, but the mtime is positively correlated with failed refresh followed by a device-code auth-flow trigger, not successful live refresh
- **AC-2: PARTIAL**. Presence, ownership, type, size, and all unaffected mtimes/modes match the baseline. Two pre-existing non-empty ChatGPT entries and both auth directories retain permissive legacy modes, so this review cannot call the complete permission state safe
- **AC-3: PASS**. The exact just-in-time gate tolerates only a positively correlated successful refresh while rejecting missing accounts, permission drift, unexplained replacement, failed refresh, and device-auth initiation
- **AC-4: REJECT**. NAS deployment remains blocked

## Documentation Impact

No product, architecture, or CodeMap update is required. This investigation records transient operational disposition and a deployment gate without changing steady-state behavior

## Open Risks

- One ChatGPT profile attempted device-code authentication after refresh failed, so that profile may require user reauthorization
- Legacy permissive auth-directory and two non-empty credential-file modes require separate PMA-authorized remediation before the metadata gate can be called secure
- The prior baseline did not capture inode identity, so attribution relies on exact timestamp correlation, preserved metadata, sanitized logs, and the reviewed atomic writer contract

## Recommended Next Step

PMA should keep NAS deployment blocked, route profile reauthorization and credential-permission hardening as separate authorized work, then rerun the just-in-time gate immediately before a digest-pinned deployment
