# Read-only Comparison Log

## Scope

Subject: `sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820`

Source revision: `a826c38dc0737afd9eef00a2e9f50d2413ca92eb`

No production object, configuration, credential, source file, test, image, build cache, registry object, Git ref, or deployment was changed. Disposable `task005-*` containers were removed after each probe

## Key Observations

```text
image: sha256:eeb98cc84cd1f3b73ce1dc584ac9922e47515fc3db46beb8825283fddf6b2820 amd64 linux
entrypoint: ["docker/prod_entrypoint.sh"]
command: ["--port", "4000"]
working directory: /app
litellm: 1.100.0, non-editable file:///app
gateway component files in final image: absent
backend component files in final image: absent
SERVER_ROOT_PATH: unset
PROXY_BASE_URL: unset by image default
app root_path: ""
initial lazy_loaded: set()
discovery route indices: 559..564
lazy owners for every discovery path: ["mcp_discoverable"]
```

The exact source commit and installed image package produced identical SHA-256 values for all files in the causal path

## Live Exact-image A/B

Unchanged image with no `PROXY_BASE_URL`:

```text
404 /.well-known/oauth-protected-resource/lazymcp {"detail":"Not Found"}
404 /lazymcp/.well-known/oauth-protected-resource {"detail":"Not Found"}
404 /.well-known/oauth-protected-resource/lazymcp/team-a {"detail":"Not Found"}
404 /lazymcp/team-a/.well-known/oauth-protected-resource {"detail":"Not Found"}
404 /.well-known/oauth-protected-resource/toolset/tools-a/lazymcp {"detail":"Not Found"}
404 /toolset/tools-a/lazymcp/.well-known/oauth-protected-resource {"detail":"Not Found"}
```

Unchanged image with only `PROXY_BASE_URL=https://candidate.invalid` added:

```text
200 /.well-known/oauth-protected-resource/lazymcp {"resource":"https://candidate.invalid/lazymcp","authorization_servers":["https://candidate.invalid/mcp"]}
200 /lazymcp/.well-known/oauth-protected-resource {"resource":"https://candidate.invalid/lazymcp","authorization_servers":["https://candidate.invalid/mcp"]}
200 /.well-known/oauth-protected-resource/lazymcp/team-a {"resource":"https://candidate.invalid/lazymcp/team-a","authorization_servers":["https://candidate.invalid/mcp"]}
200 /lazymcp/team-a/.well-known/oauth-protected-resource {"resource":"https://candidate.invalid/lazymcp/team-a","authorization_servers":["https://candidate.invalid/mcp"]}
200 /.well-known/oauth-protected-resource/toolset/tools-a/lazymcp {"resource":"https://candidate.invalid/toolset/tools-a/lazymcp","authorization_servers":["https://candidate.invalid/mcp"]}
200 /toolset/tools-a/lazymcp/.well-known/oauth-protected-resource {"resource":"https://candidate.invalid/toolset/tools-a/lazymcp","authorization_servers":["https://candidate.invalid/mcp"]}
```

With `PROXY_BASE_URL=http://candidate.invalid`, all six remain HTTP 404 because non-loopback public resources require HTTPS

## OpenAPI

Both the unset and HTTPS exact-image runs advertise all six route templates in `/openapi.json`. This confirms OpenAPI is not the discriminator. Snapshot/schema generation is based on declared routes, while trusted public-origin validation executes inside the handler at request time

## Cleanup

```text
docker ps -a --filter name=task005-: zero results
```
