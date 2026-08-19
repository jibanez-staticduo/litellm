# NAS And Stable Isolation

NAS remained exact before and after Fedora deployment:

- Container: `1fc657b5b51b7ab07b1a2ac4da13302f5e56c2123ce521481a3d82c3be36c148`
- Start time: `2026-08-19T02:09:29.869606517Z`
- Candidate manifest: `sha256:42d36549ab561f202748e0f32a1ff9059eb86a51d6957802b3ce08445eab115b`
- NAS config/local ID: `sha256:45a01917a825fa04dda4d8b0efafd1a780cfbbb9fc16d3846d654d5d49b42c73`
- Status/health/restarts/OOM: running / healthy / 0 / false
- Readiness/liveliness: HTTP 200 / HTTP 200
- Mounts: 5

Stable remained held and was not moved:

- Stable manifest: `sha256:b52c0949442e8855289df706621725670d1cff28738a277c245b273b388873e0`
- Stable promotion performed: false

Result: **NAS AND STABLE ISOLATION PASS**
