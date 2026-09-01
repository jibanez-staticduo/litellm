---
id: SCR-2026-09-01-001-upstream-main-integration
status: approved
requested_by: user
approved_by: user
date: 2026-09-01
---

# SCR: Upstream Main Integration

## Problem and Outcome

The StaticDuo LiteLLM fork is behind current upstream `main`, while the fork contains intentional product, security, protocol, model-policy, and operational behavior that must not be lost during integration. Advancing the fork without an exact upstream snapshot, explicit conflict decisions, broad regression coverage, and isolated release qualification could silently remove fork behavior or expose Fedora production to an unqualified image

The approved outcome is a reviewed fork revision that contains every upstream commit through one recorded upstream `main` commit, preserves every intentional fork behavior or adopts a proven upstream equivalent, passes comprehensive source verification, and produces one immutable isolated candidate. Only after independent source, runtime, and security approval may the reviewed commits advance fork `main` and that exact qualified digest deploy to Fedora. NAS remains unchanged and outside this release

## Approved Delivery Sequence

The work must proceed in this order, with each stage blocking the next until its evidence receives the required review:

1. Record the full upstream `main` commit SHA selected by the read-only architecture review and freeze it as the integration boundary
2. Attribute, reconcile, test, and commit all intentional pre-existing fork work in logical commits without pushing or dropping unrelated work
3. Integrate the frozen upstream snapshot, resolve every conflict explicitly, and complete source-level verification without pushing or deploying
4. Build and qualify one clean immutable candidate in an isolated Docker environment that is separate from Fedora and NAS
5. Obtain independent QA, security, and Tech Lead approval for the exact source commits, builder, final image, registry identity, and evidence packet
6. Push only the approved commits to fork `main`, without force, and prove the remote contains the frozen upstream snapshot and reviewed fork commits
7. Publish or promote only the exact approved candidate digest, then deploy that digest to Fedora with rollback readiness and observation

No later-stage success waives an earlier gate. A change to source, tests, dependency or lock resolution, migrations, build inputs, base images, toolchains, candidate configuration, qualification harness, builder, final image, or vulnerability database invalidates affected evidence and requires the relevant gates to run again

## Exact Upstream Inclusion and Git Contract

- The architecture handoff must record the reviewed upstream commit as a full SHA. A moving branch name, tag, version label, abbreviated SHA, or later upstream head is not an acceptable integration identity
- The completed integration must prove that the recorded upstream commit is an ancestor and that no upstream commit through that snapshot was omitted. Upstream content may change only where an intentional fork requirement demands a conflict resolution or follow-up compatibility fix
- Merge versus replay is a technical decision for the read-only architecture review. The chosen strategy must minimize destructive history rewriting, preserve fork `main` history, retain attribution, and incorporate the complete frozen upstream snapshot
- Every pre-existing tracked and untracked path must be attributed before integration. Intended work must be committed in logical task-owned commits or explicitly preserved outside the integration; unexplained drift is a stop condition
- Every textual, semantic, dependency, generated-file, migration, Docker, UI, and StaticEng conflict must appear in a conflict ledger with the selected resolution, preserved requirement, reviewer, and verification evidence. Conflict markers, unclassified deletions, and broad take-ours or take-theirs resolutions are prohibited
- An upstream implementation may replace a local patch only when the ledger shows that it provides equivalent or stronger observable behavior and the fork preservation tests pass. Redundant local code may then be removed deliberately rather than retained by default
- Required source, tests, documentation, CodeMaps, task records, and evidence must be finalized before the final reviewed integration commit. No push occurs during pre-merge or integration implementation tasks
- Release must push only to the StaticDuo fork `main`, never to the upstream repository, and must not force-push. If fork `main` moves after candidate freeze, release stops until ancestry, diff, and candidate validity are reviewed again

## Fork Preservation Contract

Before resolving conflicts, implementation must produce a preservation manifest that maps every intentional fork commit and behavior to its owning task or specification, affected paths, upstream overlap, resolution, and mutation-sensitive verification. At minimum, the manifest and regression plan must protect:

- LazyMCP transport, selection, discovery, exact OAuth challenges, DCR resource binding, audience isolation, toolset handling, permissions, and the approved steady-state contract in `.staticeng/docs/architecture/lazymcp-oauth-discovery-contract.md`
- Existing MCP transports and REST surfaces, server and tool permissions, access groups, key/team/user boundaries, delegated and upstream authentication, credential separation, delete behavior, and tool invocation
- ChatGPT subscription authentication profiles, multi-account routing and fallback behavior, native Responses streaming, fake-stream bypass, empty-output handling, usage normalization, telemetry safety, and Chat Completions/Responses compatibility
- Approved model aliases, model inventory, provider routing, reasoning-mode contracts, fallback policy, pricing behavior, and rejection or normalization rules owned by the fork
- Authentication and authorization boundaries, OAuth trust and audience rules, secret handling, log and access-log redaction, hostile-input handling, and all other security hardening introduced by governed fork work
- Health and readiness behavior, database migration safety, Redis and coordination behavior, spend and usage logging, onboarding/session behavior, startup and release packaging, and other governed operational fixes

This list is a minimum, not a substitute for the complete manifest. No intentional fork behavior may be dropped because it was absent from this summary. Product behavior, configuration semantics, catalog identities, credentials, routing intent, and permission outcomes remain unchanged unless this SCR or a separately approved SCR explicitly changes them

## Source Verification Contract

The architecture handoff must define the exact command and environment matrix after inspecting the frozen upstream snapshot and conflict map. Verification must include all focused and mapped tests for changed or conflict-adjacent areas plus the repository's normal complete gates applicable to the integrated tree, including:

- Python core, proxy, provider, router, model policy, authentication, MCP, LazyMCP, ChatGPT, Responses, logging, migration, and security suites
- UI dependency integrity, formatting, lint, type checking, unit tests, and production build where the upstream snapshot or conflict set affects UI inputs or output
- Rust formatting, lint, type or compile checks, and tests where the upstream snapshot or conflict set affects Rust crates or Python/Rust boundaries
- Dependency declaration and lock consistency, generated artifact checks, migration validation, packaging, Dockerfile, entrypoint, and import or ABI checks
- Focused regressions for every preservation-manifest item and every conflict-ledger decision, including negative and fail-closed cases for authentication, permissions, audience isolation, unknown resources, model-policy rejection, and credential separation

All required gates must pass from the clean reviewed revision. A failure, unexplained warning, required skip, quarantine, flaky retry dependency, reduced assertion, or test disabled to accommodate the integration blocks candidate construction. RestrictedPython must resolve to a policy-approved fixed version, at least 8.5 for this integration, and all dependency security remediations present in the frozen upstream snapshot must remain effective

## Isolated Candidate Qualification

The candidate must be built from a clean checkout of only the reviewed commits in an isolated workspace under `/tmp/opencode` or an equivalently isolated non-production location. Its containers, network, volumes, database, configuration, catalog, keys, and credentials must be disposable and separate from Fedora and NAS. Production databases, Docker sockets, bind mounts, credential files, encrypted records, and service networks must not be attached

Authorized test-only provider and MCP credentials may be provisioned solely through the isolated harness when needed for real behavior. They must not be copied from production, printed, committed, or retained in evidence. If a production-equivalent catalog or encryption state cannot be reproduced safely, qualification stops rather than substituting a production gateway result or waiving the gate

The exact target-platform builder and final image must be retained by immutable identity. Runtime qualification must prove, through the candidate itself:

- Readiness, liveness, startup, database creation and upgrade from the approved baseline, imports, entrypoint, reconnects, and clean shutdown
- Expected model inventory plus at least one authorized real model request through Chat Completions and Responses, including streaming, tool-call round trips, usage, error, and logging behavior relevant to preserved fork features
- MCP management and REST behavior, standard MCP initialization, LazyMCP aggregate/scoped/toolset discovery and exact challenges, OAuth discovery, DCR, authorization-code and refresh binding, cross-audience rejection, permissions, reconnect behavior, and one permitted registered upstream tool invocation
- Existing upstream-auth credential separation, unknown-name and unauthorized failures, model-policy outcomes, health surfaces, migrations, operational logs, and all preservation-manifest smoke gates
- No secret leakage, repeated discovery errors, unhandled traceback, new error burst, permission expansion, aggregate fallback, unexpected model/catalog drift, or mutation of either production environment

A simulated tool, mocked provider response, production gateway result, or database-free initialize request does not satisfy a required real candidate-bound model or tool gate

## Supply-Chain and Security Qualification

- Freeze and record source commits, dependency and lock files, build arguments, target platform, base-image digests, package repositories, downloaded artifacts and checksums, toolchains, builder identity, final image identity, registry manifest, registry config digest, and vulnerability database identity
- Retain the exact builder that emitted the candidate. A reconstructed, earlier, later, or inferred builder cannot qualify the final image
- Generate durable, machine-readable and secret-free SBOMs for the exact builder and final image in SPDX and CycloneDX forms. Also retain the base-image and comparative artifacts required to distinguish inherited, removed, and introduced findings
- Scan the old base, selected base, exact builder, and exact final image with one current frozen vulnerability database. Zero Critical findings and zero fixable High findings are permitted across release subjects. Every non-fixable or inherited High and every newly introduced finding requires independent documented disposition; an exception requires a separate Product Owner-approved, time-bounded SCR before release
- Verify publisher provenance, checksums, signatures, or explicitly approved alternate provenance for base images, package inputs, uv, Rust, UI, and other external build inputs. Missing provenance is blocking unless a separately approved policy exception exists
- Publish a candidate only under a unique non-production identity until approval. Sign and attest the exact registry digest using the approved release identity, verify the signature and provenance/SBOM attestations, and prove the registry manifest's config identity corresponds to the retained qualified image
- The repository evidence packet must retain artifact checksums and sufficient sanitized machine-readable outputs for independent reproduction. Temporary files or summary-only conclusions do not satisfy release approval

Independent QA, security review, and Tech Lead review must each return a signed pass for the same immutable subjects. Approval is fail-closed: silence, partial pass, environment block, deferred check, or evidence from another image is not approval

## Fork Main and Fedora Release Contract

Release begins only after PMA activates the release task with the signed source and candidate approvals. The reviewed source commits must advance fork `main` first. Release must verify exact remote ancestry and content without force before any Fedora selector change

The exact qualified candidate may then be promoted without rebuilding. Before Fedora mutation, record the current image digest, service and selector baseline, health, model inventory, Responses, MCP/LazyMCP, error-log baseline, database backup or snapshot, and a tested rollback procedure. Any upstream migration must have passed isolated upgrade and prior-digest compatibility testing; an irreversible or rollback-incompatible migration blocks deployment until separately reviewed and approved

Fedora deployment must:

- Select the exact qualified registry digest, not a mutable tag, and recreate only the LiteLLM service through the established release mechanism
- Preserve host configuration, credentials, database content, model catalog and aliases, routing and fallbacks, auth profiles, MCP registrations and permissions, networks, volumes, and unrelated services. Direct database edits and unrelated host changes are prohibited
- Pass readiness, model inventory, real Chat Completions and Responses behavior, MCP and LazyMCP discovery/auth/audience/initialize/real-tool behavior, permission and upstream-auth checks, reconnects, migrations, and sanitized log review against the recorded baseline
- Complete a minimum 15-minute observation with stable health and no new authentication, audience, permission, routing, migration, traceback, discovery, tool, model, or error-rate regression

Any failed release gate triggers an immediate stop and the authorized digest-based rollback procedure. Rollback must restore the prior LiteLLM digest and verify health, model inventory, Responses, MCP/LazyMCP, real tool behavior, and logs. If safe rollback cannot be proven before deployment, deployment is prohibited

## NAS Exclusion and Production Preservation

NAS deployment is explicitly out of scope. This SCR does not authorize a NAS image pull, tag or selector change, container recreation or restart, configuration edit, database or credential access, migration, registry promotion for NAS, or any other NAS mutation. NAS may be released only through a separate user-approved SCR and governed task

Fedora and NAS production remain unchanged throughout specification, architecture, pre-merge, source integration, and isolated qualification. No production mutation is permitted until all earlier gates pass and PMA activates the Fedora release task

## Evidence and Stop Conditions

Evidence must map each numbered acceptance criterion to exact reviewed subjects and verification results. It must include the upstream snapshot, preservation manifest, conflict ledger, test matrix, source results, immutable builder/final/registry identities, SBOM and scan checksums, signature and attestation verification, isolated runtime results, production-preservation checks, approvals, Fedora baseline, deployment result, observation, and rollback result or readiness

Stop and return to PMA without broadening scope when any path or behavior cannot be attributed, a conflict lacks an approved requirement, a required test or real integration cannot run, a secret-safe isolated equivalent cannot be built, identity or provenance is ambiguous, a security finding violates policy, fork `main` moves, production differs from the approved baseline, migration rollback is unsafe, or a required reviewer does not approve

## Documentation Impact

This SCR is the approved behavior and release-governance source for the integration. The architecture task must cross-link its exact integration and qualification design to this SCR. Implementation must update affected steady-state product, architecture, technical, and CodeMap documentation when conflict resolution changes those truths; operational evidence must remain in task evidence rather than being represented as steady-state product behavior

No `PRODUCT_OVERVIEW.md` or `FEATURES_LIST.md` exists in this repository, and the approved integration does not add an advertised product capability. Those files are not required for this specification task. If integration changes advertised behavior rather than preserving or adopting an equivalent, PMA must route that change through a separate SCR before implementation

## Non-Goals

- Adding product features, changing public behavior, redesigning fork policies, or accepting upstream defaults that conflict with approved fork behavior
- Editing source or tests, fetching or changing Git refs, committing, pushing, building, publishing, signing, scanning, accessing hosts, changing registries, or deploying during this specification task
- Deploying to NAS or using NAS as a candidate, canary, test dependency, credential source, or fallback environment
- Changing Fedora configuration, credentials, catalog, database, auth profiles, routing, fallbacks, networks, volumes, or unrelated services beyond the later approved exact-digest LiteLLM release
- Waiving required tests, real model/tool behavior, security findings, provenance, builder retention, signatures, attestations, SBOMs, scans, rollback readiness, or observation

## Numbered Acceptance Criteria

- **AC-1:** The integration includes every upstream commit through one exact reviewed upstream `main` SHA and preserves every intentional fork commit and behavior through an exhaustive preservation manifest, conflict ledger, and verified equivalent-or-local resolution
- **AC-2:** All conflicts are resolved intentionally without dropping LazyMCP, MCP, ChatGPT/Responses, model-policy, security, authentication, permission, migration, logging, or operational behavior, and no unexplained drift or unresolved conflict remains
- **AC-3:** The clean reviewed integration passes all focused, mapped, and repository-wide applicable source gates with no required failure or skip, then produces a fully isolated immutable Docker candidate outside Fedora and NAS
- **AC-4:** The exact candidate passes health, migrations, models, Chat Completions, Responses, MCP, LazyMCP, OAuth discovery/challenges/DCR/audience isolation, permissions, upstream authentication, real registered-tool execution, reconnect, log, and preservation gates using isolated test-owned state
- **AC-5:** The exact retained builder and final image have complete reproducible provenance, verified signatures and attestations, durable SBOM and same-database scan evidence, zero Critical and zero fixable High findings, and independent disposition of every remaining High or introduced finding
- **AC-6:** Only after signed independent approval are the reviewed commits pushed without force to fork `main`; the unchanged exact qualified digest then deploys to Fedora only with proven baseline, rollback, full smoke verification, and at least 15 minutes of successful observation
- **AC-7:** NAS remains unmodified and unauthorized for deployment, both production environments remain unchanged until all prior gates pass, and any identity, evidence, test, security, migration, preservation, or release failure stops progression and fails closed

## Approval

Approved directly by the user on 2026-09-01 and relayed by the Product Manager. Approval is limited to the behavior, sequencing, preservation requirements, security gates, Fedora-only release, and exclusions in this SCR. It does not authorize this specification task to edit source or tests, change Git refs, commit, push, build, publish, access or mutate hosts, change registries, or deploy
