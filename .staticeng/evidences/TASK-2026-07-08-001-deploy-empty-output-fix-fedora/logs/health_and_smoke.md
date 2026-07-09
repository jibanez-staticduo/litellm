# Health and smoke log

## Running image after deploy

```text
litellm_health=healthy
name=/litellm id=0946b3b273f674805b4a4cd27dc7ecb150b177bc292f06659a53a481676d207d image=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708 image_id=sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316 status=running health=healthy
image=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708 id=sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316 repo_digests=docker.staticduo.com/litellm@sha256:1c83fa329b7c3e5d4e04ccd03da9a345c373d24123b6a0b060de4d178f6c1316
```

## Compose image setting after deploy

```text
line=17 LITELLM_IMAGE=docker.staticduo.com/litellm:staticduo-gpt-lazymcp-v1.92-replay-chatgptprofiles-emptyoutputfix-20260708
```

## Endpoint checks

Checks were run from inside the LiteLLM container with only status, byte count, and item count recorded. Auth material was read inside the container and was not printed.

```json
[
  {
    "bytes": 12,
    "path": "/health/liveliness",
    "status": 200
  },
  {
    "bytes": 37,
    "path": "/health/readiness",
    "status": 200
  },
  {
    "error_type": "HTTPError",
    "path": "/health",
    "status": 401
  },
  {
    "bytes": 42134,
    "data_count": 9,
    "path": "/model/info",
    "status": 200
  },
  {
    "bytes": 1118,
    "data_count": 9,
    "path": "/v1/models",
    "status": 200
  }
]
```

`/health` returning 401 is expected for the authenticated health endpoint; liveliness and readiness passed. `/model/info` and `/v1/models` provided the safe admin/API validation without sending paid or private provider completion traffic
