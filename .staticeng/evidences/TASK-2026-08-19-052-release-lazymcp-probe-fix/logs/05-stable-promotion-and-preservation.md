# Stable Promotion And Final Preservation

- Stable before: `sha256:35fc520902eb72f5ea91ececccf221883dd5fd78b1d47c78150dfd66eb04f2d3`
- Promotion method: locally tag the already digest-pinned candidate as `stable`, then push
- Stable after: `sha256:f44690e5203983e00a0d01016d65440bf1c4b83a941a490d22d4e7eea443b42a`
- Media type: `application/vnd.docker.distribution.manifest.v2+json`
- Platform: `linux/amd64`
- Config digest: `sha256:84dd79e310f6c5804c50e304fb36479ed6c019ffbff6a64b5b5c91b6b4c4ceed`
- OCI version/revision: 1.98.0 / `8589869e1c745ae5c66d96e5475aa816496bc060`

Post-promotion host state:

| Host | Container | Started | Restarts | OOM | Health |
|---|---|---|---:|---|---|
| Fedora | `1ce74be6f465...` | `2026-08-19T09:51:35.209256106Z` | 0 | false | healthy |
| NAS | `122510897d18...` | `2026-08-19T09:55:49.867042351Z` | 0 | false | healthy |

Both host container identities and start times matched their pre-promotion values exactly

Result: **PASS**
