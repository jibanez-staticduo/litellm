# Staging Deploy, Health Gate, And Rollback

## Deployment

- Changed the staging Compose image reference only, from the prior immutable digest to the candidate immutable digest
- Validated Compose using the required staging database interpolation without printing the value
- Pulled the candidate and ran `docker compose ... up -d --no-deps litellm`
- Only `litellm-staging` was recreated. Production, staging PostgreSQL, and staging Redis retained identity and start times
- Candidate container identity resolved to image config `sha256:8ebdb64e04450219e564626b987c14e1fc229940a2d36054cf6d41f5214efd72`, running with zero restarts and OOM false

## Failed Health Gate

- The candidate completed `prisma migrate deploy`; 151 migrations were found and no pending migration was applied
- The startup wrapper then received HTTP 401 while refreshing an existing ChatGPT credential and entered device-authentication flow
- The application never opened port 4000. Docker health remained `starting` with repeated connection-refused checks, and loopback readiness/liveliness returned no HTTP status
- No device code, token, credential value, prompt, completion, authorization header, or environment value was captured in repository evidence
- Per the architecture stop condition, live request matrices were not attempted after the failed health gate

## Rollback Verification

- Stopped the candidate, restored and checksum-verified the prior Compose, recreated the prior image with `--no-deps`, then stopped staging
- Final staging image: `docker.staticduo.com/litellm@sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Final staging state: exited, zero restarts, OOM false
- Final staging Compose SHA-256: `5d6a6b030ed2272cf96ec5ff562eee1c52c9f28afd69e79c8a925264f0a14600`
- Final staging config SHA-256: `d10d989072e329a3a47c11ee734783a08c8607865fa8e8fa940851e75f624272`
- Staging PostgreSQL and Redis retained their exact pre-deploy IDs, start times, healthy states, and zero restart counts
- Production retained container ID `51224136611e59fb7bea7c0f19f3303f90d4ecfc1052c307602bdd8abf89c014`, prior immutable image, original start time, healthy state, zero restarts, and OOM false
