# Release Baseline And Device-Auth Observation

## Exact NAS Baseline

Captured after quarantine and reload on 2026-08-19 UTC

- Image: `docker.staticduo.com/litellm:rollback-nas-1.92.0-20260818`
- Image ID: `sha256:8ae33df6e1c13eaaca70ce179d4a724507a481ebcf4019be88182aa030b07afa`
- Status/health: running/healthy, OOM false, readiness HTTP 200, liveliness HTTP 200
- Model count: 32
- Normalized model-name hash: `ba61d2feac5508f98652eaf154dbc7a5e6da6cf53f6d5f5a74cd0068230788e2`
- Normalized deployment-ID hash: `647982b1a65789d33568b7ddcabeb2640b5d851409442cc119ce0c6501512fd5`
- Normalized inventory-pair hash: `c1b02458b0870214482918880ce8c01735bee34e00fa01cd90d7981c225273d4`
- General fallback count/hash: 16 / `d0841f275e4c4cdeafd89c4e8e24062438e70441edcb8a287974b8566b798262`
- Public GPT fallback count/hash: 8 / `b4b534b799d9b3597b4ccd73f4d68d8d2cacf55cdd0a9a788e4e1c5751164672`
- Compose SHA-256: `0a84fde576264b85d07e5535f25255ceb0eb8d120a729e91c140b4e52b0e185b`
- Startup wrapper SHA-256: `7005b7bb28c94d9f044e2f15a6a0697068d604751b26cd98361440c773c47f6c`
- Config SHA-256: `d10d989072e329a3a47c11ee734783a08c8607865fa8e8fa940851e75f624272`
- OnePassword wrapper SHA-256: `31f719b71fce74e968cec69aa1ce51ca4dac08381c8005aa6b5d3be2879b6289`

The account3 credential file and its protected historical state remain present, owner-only, and outside active routing

## External Preservation

- Fedora remained running/healthy on immutable candidate digest `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`, restart count 0, OOM false, start time unchanged
- The candidate registry digest remained resolvable
- `stable` remained unresolved exactly as in the parent gate; this task made no registry mutation
- No 1.98.0 deployment or tag movement occurred

## Observation

The unchanged LiteLLM container started at `2026-08-18T23:59:29.320853867Z`. The observation ended at `2026-08-19T00:14:27Z`, a bounded 14-minute 58-second post-reload window

- Account3 log matches: 0
- Device-auth log matches: 0
- Refresh-401 log matches: 0
- Account3 lock held at observation end: false
- Runtime remained running/healthy, restart count 0, OOM false
- Account3 credential metadata remained unchanged from the parent baseline: regular file, owner `0:0`, mode 0600, size 3855, mtime/ctime `1787096921`, inode `113462912`
- Auth root/default/account2 metadata remained protected at owner `0:0`, directory 0700, files 0600

This exceeds the prior repeated device-prompt interval and proves the active account3 device-auth loop stopped after routing quarantine and reload

Result: **PASS**
