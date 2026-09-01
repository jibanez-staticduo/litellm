# DeepSeek Policy Image Staging

## Summary

Built and published one content-addressed image from the reviewed source patch, deployed it only to the stopped NAS staging service, and rolled staging back after the mandatory health gate failed. The new image itself started and completed database migration, but the staging startup wrapper blocked on a pre-existing expired ChatGPT refresh token and never opened port 4000. Production, Fedora, client configuration, staging data services, credentials, and model records were not changed

## Work Performed

- Captured source, patch, image, Compose/config checksum, service-state, dependency, and rollback baselines without secret values
- Built from a clean `git archive` of revision `b3f60643b8a1f9d5becc2b39f15f67f7638c5375` with only the five reviewed runtime source files applied from patch SHA-256 `ffef2b5158f997fb030a04ab796ee4384af95ee36c529daddfa44b40da277783`
- Published `docker.staticduo.com/litellm@sha256:a8cf0e9d64be4f6fec1ab517c560b7619f8c6a8df60adcc52f48ccfb5d1d288e`; its amd64 image config digest is `sha256:8ebdb64e04450219e564626b987c14e1fc229940a2d36054cf6d41f5214efd72`
- Recreated only `litellm-staging` with `--no-deps`; staging PostgreSQL and Redis retained container identity, start time, healthy state, and zero restarts
- Observed successful Prisma migration with no pending migrations, followed by startup blocking on expired ChatGPT authentication; readiness and liveliness remained unavailable and the container health check stayed `starting`
- Restored the exact prior staging Compose file from its owner-only backup, recreated the prior image, and returned `litellm-staging` to its required stopped state

## Acceptance Criteria Coverage

- **AC-1: PASS**. Logs record source and patch identities, production/staging image digests, config checksums, service state, dependency identities, and exact rollback commands. No secret values are present
- **AC-2: PASS**. The registry digest, image config digest, labels, clean build context, and reviewed runtime-file checksums identify one immutable image containing the intended source patch
- **AC-3: PASS**. Only NAS staging was recreated. Production remained healthy on its prior digest. Staging PostgreSQL and Redis were not recreated, and no database, model, credential, Fedora, production, or client configuration was edited
- **AC-4: FAIL**. Staging did not become healthy, so model identity, inventory, and restart persistence could not be verified
- **AC-5: NOT RUN**. The canonical direct vLLM and public Chat/Responses matrices were halted after the mandatory staging health gate failed
- **AC-6: NOT RUN**. Request-scoped rejected-value and DG1 no-forwarding correlation requires a healthy staging proxy
- **AC-7: NOT RUN**. The unrelated hosted-vLLM live non-regression probe requires a healthy staging proxy
- **AC-8: PASS**. This packet records the failed gate, complete rollback, residual risk, and explicit production recommendation

## Documentation Impact

No steady-state product or architecture documentation changed. This is a failed staging rollout with a boundary-local rollback; the task and evidence packet are the operational record

## Open Risks

- Staging cannot currently pass startup because its mounted startup/auth path attempts ChatGPT token refresh and enters device authentication after a 401
- The candidate has not passed live policy behavior, no-forwarding, unrelated-model, or restart-persistence verification
- The image was built from uncommitted reviewed source because the task explicitly prohibited committing; provenance therefore relies on the recorded base revision, patch digest, per-file checksums, and immutable image labels
- `staticeng_validate` remains blocked by inherited repository-wide missing CodeMaps. The required repair dry-run proposed unrelated Markdown normalization and could not resolve the missing module-boundary decisions, so no broad repair was applied

## Recommended Next Step

Do not promote this image to production. PMA should route a staging-auth repair or reauthentication task, then reopen this task and rerun deployment plus the complete canonical and staging matrices from the original stopped-state baseline
