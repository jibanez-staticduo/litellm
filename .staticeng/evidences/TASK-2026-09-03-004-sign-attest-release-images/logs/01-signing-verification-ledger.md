# Signing And Verification Ledger

## Safety Boundary

No existing approved StaticDuo Cosign key, KMS identity, or frozen keyless workflow identity was available. The repository `cosign.pub` remains the upstream BerriAI trust root and was not reused. PMA's fallback approval was therefore exercised for signer `staticduo-litellm-release-self-managed-v1`

The encrypted private key and its separately generated password are owner-only outside the repository and all configured Syncthing folders. Their paths and values are omitted. Evidence retains only the public key, key fingerprints, signer identifier, predicate checksums, and secret-free verification results. No command tracing, environment dump, registry credential, private key, or password was captured

```text
key directory mode: 0700
encrypted private key mode: 0600
password file mode: 0600
public key file SHA-256: 3983a067c0f99ec9e44e91b58f0991e6a065c74a11c6e70095abe178904005ec
public key SPKI SHA-256: 2b3b91453b283be502c0cd035d835d5b58faa42b1f638297c45da75b09a15e71
private or password material tracked: no
configured Syncthing path used: no
```

## Tooling

Cosign v3.1.3 was downloaded from its exact release URL, verified before execution against SHA-256 `4629c757b7618056f8ddd7e2625ae9fdd94c0372a65049520bc7d9df9efc7f71`, and removed after verification. Docker 26.1.0, Buildx 0.32.1, OpenSSL, jq, and SHA-256 tooling were used. No insecure registry, HTTP registry, disabled-claim, or disabled-transparency-log option was used

## Exact Source And Published Subjects

The qualified source is commit `bf58974a935521fa570fa7e280c51a00b2e5b54e`, tree `5bb1b3185d25ba851482ee022503178996df3341`. Current `main` contains later StaticEng evidence commits only; no source or build input changed after qualification

```text
builder quarantine tag: docker.staticduo.com/litellm:quarantine-task011-r6-builder-bf58974a9355-eb673f1c4f02
builder registry digest: docker.staticduo.com/litellm@sha256:8ff106da74054123f9e5fb742e8c008656b11f46148e40d742fde9332d101daa
builder manifest config: sha256:eb673f1c4f02a3c0e9cf93d2b73703308664276aea50ea6a57c759956a3788ac
builder config equality: PASS

final quarantine tag: docker.staticduo.com/litellm:quarantine-task011-r6-final-bf58974a9355-ad33017b518b
final registry digest: docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
final manifest config: sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
final config equality: PASS
```

Only these two unique quarantine tags were created. No stable, latest, release, deployment, Fedora, or NAS selector was changed

## Attestation Predicates

The exact TASK-011 Reopen 6 SPDX and CycloneDX documents were copied byte-for-byte. SLSA provenance v1 predicates bind the exact source revision/tree, Dockerfile and target, empty build-argument set, linux/amd64 platform, BuildKit version, qualified config ID, and qualification SBOM/scan/database checksums

```text
builder SPDX SHA-256: dfa593c6231e1cae1b0a243573766238408693fa0778099768a6eec693d556f2
builder CycloneDX SHA-256: 274f45081b3369c93d670d981b13a4da78a0d623cbe0a1233597b416b1fb1067
builder SLSA v1 SHA-256: 896bc560b946560594bcfe4f8a2633ed13c2ec0dc8481047f1613f9177da7bdd
final SPDX SHA-256: 765bb011c6395d3ab8564164463e8b9e07bf6600781944dbf2f4710a11da2d50
final CycloneDX SHA-256: 1662bdb044ef4f7bd961b47ce049bdc5fbb387c463dadd2a16cd888bab3ad783
final SLSA v1 SHA-256: d4ce84588fc4616b99d20620a0784d36962041e4b1ac55e0245885e8399e4842
```

## Fresh Verification

Fresh read-only Cosign processes verified each digest with the retained public key. Each subject has exactly four signed bundles: one image signature plus SPDX, CycloneDX, and SLSA provenance v1 attestations. Every DSSE statement has exactly one subject whose SHA-256 equals the requested registry manifest. The image signatures carry exact task `TASK-2026-09-01-011-r6` and exact source revision annotations

For both builder and final:

```text
signature cryptographic verification: PASS
signature claim and annotation verification: PASS
SPDX attestation cryptographic/type verification: PASS
CycloneDX attestation cryptographic/type verification: PASS
SLSA provenance v1 cryptographic/type verification: PASS
sole exact registry subject on all four statements: PASS
SLSA source revision: bf58974a935521fa570fa7e280c51a00b2e5b54e
decoded predicate byte-equivalent JSON: PASS for all three predicates
fresh registry download bundle count: 4
fresh registry persistence: PASS
```

The registry uses Cosign's OCI referrer storage, so legacy signature tags do not resolve and `cosign tree` returns no legacy-tag listing. Fresh `cosign download signature` discovery nevertheless returned all four OCI referrers per digest, and every returned bundle passed public-key, transparency-log, type, subject, source, and predicate-content validation

## Cleanup And Preservation

Transient decoded bundles, fresh-process downloads, and the checksum-pinned Cosign binary were destroyed after reducing them to secret-free verification summaries. The two qualified local image IDs and their two new quarantine tags remain intentionally retained. Fedora and NAS were not accessed or mutated during publication/signing

Result: PASS for AC-1 through AC-6
