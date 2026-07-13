# TASK-2026-07-11-003 Release Evidence

## Summary

Released commit `8dcccc5cd201d777aee23e3004242e73d8ed4207` to local/NAS and Fedora using one immutable registry image. Both instances are healthy and retained their exact pre-release model inventories. Local regular and account2 Sol smokes passed; Fedora regular Sol passed and no Fedora account2 request or device-auth flow was triggered.

## Image

- Tag: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-multiaccount-routingfix-20260711`
- Registry digest: `sha256:ca28db906704c63afc9b73bd40a201edadb10da30e214542fcada54748dd2497`
- Local image ID: `sha256:0fd2463546d5ff893abf90174ea433fef470bec83cac11565dddb2385ea94d52`
- Fedora image ID: `sha256:ca28db906704c63afc9b73bd40a201edadb10da30e214542fcada54748dd2497`

## Rollback

- Previous image on both instances: `docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708`
- Previous registry digest: `sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316`
- Local rollback tag: `docker.staticduo.com/litellm:rollback-multiaccount-routingfix-local-20260711`
- Fedora rollback tag: `docker.staticduo.com/litellm:rollback-multiaccount-routingfix-fedora-20260711`

## Verification

| Check | Local/NAS | Fedora |
| --- | --- | --- |
| Container | running, healthy | running, healthy |
| Readiness | HTTP 200 | HTTP 200 |
| Liveliness | HTTP 200 | HTTP 200 |
| Inventory | 26 before, 26 after, exact names and deployment IDs preserved | 19 before, 19 after, exact names and deployment IDs preserved |
| Regular Sol smoke | HTTP 200, exact sentinel | HTTP 200, exact sentinel |
| Account2 Sol smoke | HTTP 200, exact sentinel | not called |
| Regular routing proof | default, deployment prefix `11dbce7b` | default, deployment prefix `9007ab1c` |
| Account2 routing proof | account2, deployment prefix `59183bd1` | not called |

Auth verification inspected only file names, presence, modes, and mtimes. Local `auth.json` and `account2.json` remained present with their pre-existing mode `777` and unchanged mtimes. Fedora `auth.json` and `account2.json` remained present with their pre-existing mode `644` and unchanged mtimes. No auth contents were read or recorded.

## Operational Note

The first local deployment was reverted by the `updatedockers` stack. With explicit authorization, only the Compose project rooted at `/volume2/docker/updatedockers` was stopped. Local LiteLLM was redeployed from `/volume2/docker/litellm`, observed healthy on the target image, and verified. `updatedockers` was then restarted and became healthy. After an additional observation period, local LiteLLM remained healthy on the target image.

## Acceptance Criteria

- AC-1: PASS. Required commit was built and the image was pushed with a registry digest.
- AC-2: PASS. Local/NAS runs the target image healthy with exact inventory preservation.
- AC-3: PASS. Fedora runs the target image healthy with exact inventory preservation.
- AC-4: PASS. Both regular Sol smokes succeeded and selected the default profile/deployment.
- AC-5: PASS. Local account2 Sol succeeded and selected the account2 profile/deployment.
- AC-6: PASS. Fedora account2 was not called; no device-auth flow was triggered and auth-file presence/mtime remained unchanged.
- AC-7: PASS. Rollback image references were captured and pushed for both instances.
- AC-8: PASS. This packet contains the summary and sanitized logs.

## Evidence Files

- `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/logs/release-and-rollback.md`
- `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/logs/local-verification.json`
- `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/logs/fedora-verification.json`
- `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/logs/routing-smokes-and-proof.jsonl`
- `.staticeng/evidences/TASK-2026-07-11-003-release-multiaccount-routing-fix-both/logs/updatedockers-control.md`

No application code, model database/configuration, or credential content was modified. No commit was created.
