# Read-Only OAuth Mtime Disposition

## Inputs

- Approved preflight: `TASK-2026-08-18-014-build-stream-safe-198-candidate/logs/02-nas-preflight.log`
- Wrapper migration postflight: `TASK-2026-08-18-020-migrate-nas-198-startup-wrapper/logs/03-preservation-and-decision.md`
- Runtime writer contract: `litellm/llms/chatgpt/authenticator.py`
- Inspection boundary: presence, file type, owner, mode, size, mtime/ctime/inode, file count, and sanitized log event classes only
- Credential contents read: no

## Metadata Findings

At inspection, NAS LiteLLM remained healthy in the same container

- ChatGPT directory: present, directory, non-symlink, owner `0:0`, mode `0777`, 10 regular non-symlink files
- Nine ChatGPT file mode/size/mtime tuples exactly matched preflight
- The sole drifted tuple remained owner `0:0`, mode `0600`, size 3855, regular, and non-symlink; mtime and ctime were both `1787094212` (`2026-08-18T23:03:32Z`)
- Anthropic directory: present, owner `0:0`, mode `0777`, one regular non-symlink file; its mode `0600`, size 383, and mtime `1778479050` exactly matched preflight
- Service-account mount source: present as the same empty directory mount, owner `0:0`, mode `0755`, mtime `1781105194`
- Two unchanged non-empty ChatGPT entries retain pre-existing mode `0777`; no permission widened during TASK-020 or this investigation

The 1.98.0 authenticator writes credentials through a mode-0600 temporary file and atomic `os.replace` at lines 194-215. Successful refresh writes at lines 411-450. Device-code initiation records `device_code_requested_at` through the same writer at lines 266-285 and 480-483

## Sanitized Log Correlation

For `2026-08-18T23:03:00Z` onward, server-side classification returned:

- Failed refresh: first `2026-08-18T23:03:32.160967398Z`, two duplicate-rendered matches
- Device-auth prompt: first `2026-08-18T23:03:32.338134084Z`, three prompt-line matches
- Interactive-auth failure trace rendering: first `2026-08-18T23:03:31.957485730Z`
- Auth-file write failure: zero
- Invalid-auth-file warning: zero

The credential mtime second equals the failed-refresh and device-code initiation second. The matching size, owner, mode, regular-file type, non-symlink status, ctime, and reviewed atomic writer make an unexplained external replacement unlikely. The observed device-auth prompt proves this was not an ordinary successful refresh

## Decision

**REJECT NAS DEPLOYMENT**

The current state fails the no-auth-flow requirement and does not establish that the affected profile retained usable authorization. Existing permissive modes also prevent a complete safe-permission finding

## Exact Just-In-Time Metadata Gate

Run this gate without reading credential contents and without invoking a ChatGPT model

1. **T0 timing:** within 60 seconds before deployment, record UTC time and a sanitized log cursor. Require no refresh failure, device-code prompt, interactive-auth failure, invalid-auth-file warning, auth-write failure, or provider-auth 401 in the preceding 15 minutes
2. **Allowlist snapshot:** for each approved ChatGPT and Anthropic entry, record a salted path hash, file type, symlink flag, UID, GID, mode, size, mtime, ctime, inode, and device ID. Record directory metadata and exact file count. Record only type/owner/mode/mtime/count for the service-account directory mount
3. **Pre-deploy hard failures:** reject on a missing or added path, file-count change, symlink, non-regular credential entry, owner drift, zero size for a previously non-empty credential, nonzero size for an approved lock file, or mode other than `0600` for a non-empty credential. Auth directories must be owner-only, mode `0700`, before approval
4. **Deployment boundary:** deploy only the digest-pinned LiteLLM service. Do not invoke auth, models, database changes, dependency recreation, or stable-tag movement as part of this gate
5. **T1 comparison:** immediately after health/readiness and again after a 10-minute observation, repeat the exact metadata snapshot and classify logs from T0. All unaffected entries must match T0 exactly for presence, type, symlink flag, owner, mode, size, mtime, ctime, inode, and device ID
6. **Permitted refresh exception:** one or more allowlisted non-empty credential files may change size, mtime, ctime, and inode only when each change is correlated within two seconds to a positively observed OAuth refresh HTTP 2xx for that profile. The replacement must remain regular, non-symlink, owner-identical, mode `0600`, and non-empty. Directory mtime may advance for the same atomic replacement
7. **Mandatory rejection events:** reject on an unexplained credential write, failed refresh, device-code/login prompt, interactive-auth failure, provider-auth 401, invalid file, write failure, missing account path, permission/owner drift, unexpected file-count change, or a credential change without positive refresh-success evidence. Absence of an error log alone is not sufficient
8. **Authorization condition:** NAS deployment is approved only if both T1 comparisons pass, the running image equals the candidate digest, health remains green, and every auth event since T0 satisfies the permitted refresh exception

This exception permits expected atomic token rotation without treating mtime equality as immutable, while positive success correlation and structural checks prevent account loss or permission drift from being masked
