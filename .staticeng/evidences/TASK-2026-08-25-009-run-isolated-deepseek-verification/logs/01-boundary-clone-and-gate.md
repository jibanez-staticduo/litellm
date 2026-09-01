# Boundary, Clone, And Inventory Gate

## Protected Baseline

- Production image remained `docker.staticduo.com/litellm@sha256:85349c2990080596f7e6281c4ca13344506ded9460eba388286024044a766f0c`, running healthy with zero restarts and OOM false
- Production Compose/config SHA-256 remained `cda96c4205cab8291505d0e8155fd3d962aa58c509bcd0bf307ba0f5843d029e` and `bb2eb16811e76053f94fec1f42fd09d63b1f325e736802622f62aa2ca8ee39f2`
- Original staging Compose/config SHA-256 remained `5d6a6b030ed2272cf96ec5ff562eee1c52c9f28afd69e79c8a925264f0a14600` and `d10d989072e329a3a47c11ee734783a08c8607865fa8e8fa940851e75f624272`
- Original staging PostgreSQL and Redis retained IDs `25a7ab4c0c4a03acb24e0f44eb73277f82057f0a0b3eb989e16696048e0c339a` and `e69e7ef095b0dadb0be8e30a6da086e99ebcd9913cd20d4e6cb8d69e8457d72e`, healthy with zero restarts and OOM false
- Production and staging `.env` files remained mode `0600`; secret values were not captured

## Isolation And Clone

- Temporary boundary directories were mode `0700`; all key and encrypted-dump artifacts were mode `0600`
- The staging database was streamed through `pg_dump --format=custom --no-owner --no-acl` and AES-256-CBC/PBKDF2 encryption without a plaintext dump on disk
- Isolated data services used a task-private internal network and dedicated volumes. The proxy additionally used a private egress bridge solely for required upstream provider calls
- The proxy exposed only `127.0.0.1:41401`; it had zero mounts and was not connected to `npm_npm-net`, `llm-net`, or any production/staging network
- Clone pruning retained exactly `deepseek-v4-flash-fp8-mtp`, `deepseek-v4-flash-fp8-mtp-norefusal`, and `qwen3.8-27b-refusal-dial`
- Post-prune assertions: model rows `3`, ChatGPT references `0`, credential rows `0`; encrypted dump, checksum, and passphrase were shredded immediately afterward

## Candidate Gate

- Candidate reference: `docker.staticduo.com/litellm@sha256:a8cf0e9d64be4f6fec1ab517c560b7619f8c6a8df60adcc52f48ccfb5d1d288e`
- Loopback readiness and liveliness both returned HTTP 200
- Candidate inspection showed the exact digest, loopback-only port binding, zero mounts, zero restarts, and OOM false
- Router initialization rejected all three retained deployments because cloned `litellm_params` remained encrypted and no staging encryption context was supplied
- The loaded model inventory was therefore not exactly three. This was a mandatory stop condition, so no direct/staged requests or upstream correlation probes were sent
- No encrypted values, keys, environment values, prompts, completion content, authorization headers, or full request bodies are included in evidence
