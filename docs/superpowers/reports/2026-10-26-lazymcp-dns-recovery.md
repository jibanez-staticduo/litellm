# LazyMCP DNS recovery

## Cause and correction

On 26 October, the NAS gateway returned `listing_failed` for SocialMedia and several other servers. The configured SocialMedia endpoint used HTTPS. Direct internal MCP requests completed in about 100 ms, while the configured HTTPS route intermittently stalled before TLS during DNS resolution. Both the SDK and LiteLLM client reproduced the delay

UDP queries to the configured resolvers intermittently received no reply. Selecting one resolver did not fix the problem. A process-only resolution control preserved the endpoint, TLS, SNI and authentication and restored complete sessions in 100-125 ms. An isolated container using TCP DNS completed three concurrent batches of 18 lookups in 14-18 ms and complete HTTPS MCP sessions in 100-219 ms. The precise upstream reason for the UDP losses remains unverified

The runtime correction adds only this setting to the NAS Compose service:

```yaml
services:
  litellm:
    dns_opt:
    - use-vc
```

Docker service discovery and both configured resolvers remain in use. This changes the DNS transport without changing permissions, credentials, MCP registrations, client timeouts or application code

## Verification

The published image remains `docker.staticduo.com/litellm@sha256:e97bb39af53404c3d0df2e8a82eb661be0ef00900d6670cc7d9eeedbb61f320d`, source revision `6a69b93bf239fed6a2107da0381185f53b9d5e19`. The existing sealed Fedora gate and current Fedora runtime were verified for that image. This gate covers the image; the isolated and NAS checks cover the DNS configuration

The NAS database backup passed `pg_dump`, `pg_restore --list` and an independent checksum comparison. The original backup remains intact. A separately identified candidate configuration snapshot was supplied to the unchanged `deploy-published-image.py` helper after the NAS registry/pull gate passed. Only LiteLLM was recreated

Run the operational regression inside the runtime, with its existing gateway credential:

```bash
docker exec -i litellm python - \
  --url http://127.0.0.1:4000/lazymcp \
  --server socialmedia \
  --tool socialmedia-social_list_accounts \
  --dns-host ss.staticduo.com < scripts/check_lazymcp_runtime.py
```

Before correction, this command exited 1 with DNS exceeding one second and a failed gateway lifecycle. After correction it exited 0: three gateway tools, 77 described upstream tools, successful metadata call, DNS in 3-4 ms and complete cleanup in 9 ms. Real LazyMCP connector describe and metadata calls also succeeded. Negative checks rejected an invalid credential and a nonexistent tool

Independent comparisons confirmed the same image, environment values, mounts, resolver list, mounted configuration and 99 model routes. Other container IDs were unchanged and LiteLLM was healthy with zero restarts after recreation. Ruff and BasedPyright passed for the checker. No application change or new image was needed, so the full application suite and external PR reviewers were not run

Private backup and sanitized acceptance artifacts are under `/home/staticduo/tmp/litellm-lazy-backup-20261026` and `/home/staticduo/tmp/litellm-lazy-evidence-20261026`. The original working checkout was preserved

## Rollback and remaining risk

Restore the original Compose bytes from the verified backup and recreate only LiteLLM with the same published digest through the deployment procedure. Keep the original backup separate from the candidate configuration snapshot

TCP port 53 must remain reachable to the configured resolvers. The underlying UDP loss remains an infrastructure follow-up. One unrelated server still had zero tools in the final global catalog; it is outside the SocialMedia acceptance scope
