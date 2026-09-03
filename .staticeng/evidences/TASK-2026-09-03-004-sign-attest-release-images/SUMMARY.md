# TASK-2026-09-03-004 Evidence Summary

## Summary

PASS. Exact qualified builder and final configs were published under unique quarantine tags, resolved to immutable registry digests, proven through manifest config equality, signed by the PMA-approved dedicated StaticDuo trust root, and attested with exact SPDX, CycloneDX, and SLSA provenance v1 predicates. Fresh verification passed for cryptography, transparency-log inclusion, exact subjects, source revision, predicate content, and registry persistence. No mutable tag or deployment changed

## Work Performed

- Rechecked approved signer availability without reading secret values. No existing approved StaticDuo release identity existed, so created dedicated self-managed signer `staticduo-litellm-release-self-managed-v1` under PMA's explicit fallback approval
- Kept encrypted private material and password in separate owner-only files outside the repository and Syncthing; retained only the public key and SHA-256 fingerprints
- Published exact local builder config `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and final config `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915` under their reserved unique quarantine tags
- Resolved and froze immutable manifest digests, then proved each manifest config digest equals the qualified local image ID
- Signed both registry digests and attached exact Reopen 6 SPDX/CycloneDX plus SLSA provenance v1 predicates bound to qualified source `bf58974a935521fa570fa7e280c51a00b2e5b54e` and qualification checksums
- Ran fresh public-key verification for signatures and all six attestations, parsed every DSSE statement for sole exact subject/type/source/content, and redownloaded all four OCI referrers per digest to prove persistence
- Ran `staticeng_validate`; result PASS with zero warnings

## Acceptance Criteria Coverage

- **AC-1: PASS.** No existing approved signer was available. The PMA-approved dedicated identity was created with owner-only encrypted private material and separate password outside repository/Syncthing. Public key file SHA-256 is `3983a067c0f99ec9e44e91b58f0991e6a065c74a11c6e70095abe178904005ec`; SPKI SHA-256 is `2b3b91453b283be502c0cd035d835d5b58faa42b1f638297c45da75b09a15e71`
- **AC-2: PASS.** Exact retained builder/final configs were published only to unique quarantine tags. No mutable release tag moved
- **AC-3: PASS.** Builder manifest `sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa` config equals the exact qualified builder ID. Final manifest `sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` config equals the exact qualified final ID
- **AC-4: PASS.** Both immutable registry digests have one image signature plus SPDX, CycloneDX, and SLSA provenance v1 attestations. Predicates bind exact source/tree, target/platform/tooling/config IDs, and qualification evidence checksums
- **AC-5: PASS.** Fresh processes verified signatures, expected predicate types, one exact subject per statement, exact source revision, predicate JSON equality, four persisted bundles per digest, and transparency-log inclusion
- **AC-6: PASS.** No secret material is tracked or retained in evidence. Publication used only successful unique quarantine identities; no failed remote tag/referrer remains. No Fedora, NAS, stable, configuration, database, container, or deployment mutation occurred

## Exact Signed Registry References

```text
builder: docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa
final: docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
```

## Documentation Impact

Product, architecture, technical, and CodeMap documentation are not required because this release operation changes no product behavior, source structure, API, schema, route, or maintained tooling. The trust root and exact operational result are retained in task evidence

## Open Risks

- This self-managed key is host-controlled rather than hardware-backed. Future rotation, backup, recovery, and signer access policy remain release-owner responsibilities
- The private registry exposes the signed artifacts through Cosign's OCI referrer path rather than legacy `.sig`/`.att` tags. Consumers must use Cosign 3.x or another OCI-referrer-aware verifier
- Publication/signing clears only this prerequisite. Fedora deployment still requires PMA/Tech Lead reauthorization, a fresh protected database backup/restore unit, exact preflight, digest-only selector change, full post-deploy gates, and 15-minute soak

## Recommended Next Step

PMA should accept this signed PASS, reopen the Fedora readiness decision with TASK-003's migration PASS and these exact signed registry digests, then activate the Fedora-only release only if the remaining fresh backup/preflight gates are authorized. Keep NAS and mutable tags untouched

## Signed Handoff

[Agent Message] From: tech_lead To: product_manager

PASS. Exact qualified builder `docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa` and final `docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3` are published under unique quarantine tags, proven to contain qualified configs `sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac` and `sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915`, signed by `staticduo-litellm-release-self-managed-v1`, and freshly verified with SPDX, CycloneDX, and SLSA provenance v1 attestations bound to source `bf58974a935521fa570fa7e280c51a00b2e5b54e`. No secret, mutable tag, deployment, Fedora, or NAS mutation occurred
