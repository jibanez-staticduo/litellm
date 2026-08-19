# NAS, Stable, And Validation

NAS before and after Fedora deployment:

- Container: `1fc657b5b51b7ab07b1a2ac4da13302f5e56c2123ce521481a3d82c3be36c148`
- Started: `2026-08-19T02:09:29.869606517Z`
- Image/config identity: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness from inside the container: HTTP 200 / HTTP 200
- Mounts/networks: 5 / `llm-net`, `npm_npm-net`
- Protected `.env`/Compose/config/wrapper/OnePassword-wrapper hashes: exact preflight match

Stable remained `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0` and was not moved

Verification:

- `bash -n` for both sanitized operational probes: pass
- `git diff --check`: pass
- `staticeng_validate`: inherited failure from broken `.staticeng/codemap.yml` links and repository-wide missing CodeMaps
- `staticeng_repair` dry-run proposed hundreds of unrelated Markdown and CodeMap changes, so no broad repair was applied under this exact-scope deployment task

Result: **DEPLOYMENT GATES PASS; INHERITED STATICENG VALIDATION DEBT DISCLOSED**
