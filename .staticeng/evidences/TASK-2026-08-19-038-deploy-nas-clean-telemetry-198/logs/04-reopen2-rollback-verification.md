# Reopen 2 Rollback Verification

- Restored manifest/config: `42d36549...115b` / `45a01917...b42c73`
- Rollback container: `bb3874c83acf...`
- Observation: 600 seconds / 21 polls
- Status/health/restarts/OOM: running / healthy / 0 / false
- Exact 32-model/16-rule topology and zero account3: PASS
- Credential metadata: PASS, one approved zero-byte lock ctime advance
- Dependencies, mounts/networks, non-image environment, and protected hashes: exact
- Fedora pinned identity and runtime projection: unchanged
- Stable: unchanged/missing
- Standard logging, stream, auth/device, migration/schema/patch errors: zero
- Inherited rollback cache NameError matches: present
- Generic rollback tracebacks: present and attributable to the inherited cache defect
- Evidence hierarchy: root-owned 0700 directories / 0600 files
- Complete hierarchy hash chain: reverified

Result: **ROLLBACK HEALTHY; RELEASE REJECTED**
