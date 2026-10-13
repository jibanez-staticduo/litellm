# LiteLLM Modular Extension Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for bounded implementation tasks and independent reviews. Track completion in the execution ledger.

**Goal:** Implement the approved complete option B with a versioned in-process StaticDuo extension, then validate and promote Fedora before publishing main and deploying NAS

**Architecture:** Own behavior lives in extensions/staticduo-litellm/src/staticduo_litellm. Existing LiteLLM entrypoints remain thin compatible adapters where upstream hooks do not suffice. Upstream remains the authority for authentication, MCP permissions, routing and lifecycle

**Tech Stack:** Python 3.13 runtime, LiteLLM 1.106 source, uv workspace, independent extension wheel, FastAPI/MCP, Redis, existing TypeScript dashboard, immutable registry images

**Spec:** docs/superpowers/specs/2026-10-13-litellm-modular-b.md

## Global Constraints

- Base main f5eaab5396f957c5529456bbb545e52ce0b48c46; upstream integrated 541e3ed5305a530ebef74d5684d3aca2632c1009
- Preserve dirty original checkout, host configuration, credentials, aliases, provider identity, costs, database schema and unrelated services
- No main push until final Fedora production acceptance. Candidate branch commits and registry publication are authorized
- Final order: isolated validation, published registry digest, Fedora acceptance, regular main push, NAS same digest and acceptance
- No login/logout, production token edits, monkeypatch loader or textual runtime patching. Staging uses isolated data and read-only access snapshots
- Pricing reference of memory aliases remains canonical GPT-6 Luna when current policy applies, independently of actual backend identity
- Nine mandatory promotion checks remain, with Claude provider availability informational. No waived checks unless user explicitly authorizes
- Existing budgets and coverage thresholds stay unchanged. Moved code remains covered by lint/type/test gates
- Existing configuration imports remain compatible. Callback leaf-class hook detection requires concrete-class exports or explicit wrappers
- Nightly integration lock held during candidate work; timer remains enabled and is released after completion

## Review Focus

1. Callback config loading must dispatch actual pre-call and streaming methods, including inherited-class detection
2. MCP cache and execution must retain authenticated ownership, current authority, revocation and separate gateway/upstream credentials
3. OAuth read-only mode must avoid file locks, writes, login and refresh requests, failing cleanly on expired snapshots
4. Canonical memory cost must precede spend/budget recording and remain distinct from real backend attribution
5. Wheel/build must contain every moved module and native dependency; no editable-only or missing source behavior

## Task 0: Execution inventory and isolated validation

- [ ] Record customization manifest with core insertion points and mapped existing tests
- [ ] Capture unchanged Fedora baseline and prepare private temporary stack with independent DB/Redis and read-only auth snapshots
- [ ] Run representative baseline contract tests from the candidate checkout and preserve results

## Task 1: Package and Portable Codex

Files: create extensions/staticduo-litellm/pyproject.toml and src/staticduo_litellm/{codex,compatibility}; modify root pyproject.toml/uv.lock/Dockerfile and litellm/proxy/hooks/portable_codex_agents.py; tests/unit/proxy/hooks/test_portable_codex_agents.py and extension-specific loading tests

Interface: preserve PortableCodexAgents, ReplayStore, RedisReplayStore and portable_codex_agents exports. The callback registered through old configuration must be the concrete new class, preserving leaf-method discovery

- [ ] Add/run a failing configuration-loading test asserting pre-call rewrite and completed SSE through actual dispatcher
- [ ] Extract callback/pure policies into package and isolate LiteLLM-specific dependencies in compatibility
- [ ] Add independent wheel packaging and uv workspace dependency without a circular LiteLLM package dependency
- [ ] Run existing Portable contracts plus package import/wheel/dispatcher tests; configure lint/types to include extension without budget relaxation
- [ ] Review and commit only task-owned files through parent coordinator

## Task 2: Pricing overlay and customization manifest

Files: extension pricing modules/data; build generator and tests; model_prices_and_context_window.json and backup; litellm/litellm_core_utils/memory_luna_pricing.py and its adapters as required

Interface: deterministic overlay operations add/replace/remove on fresh upstream catalog; preserve existing effective catalog. Existing memory_luna_reference/response exports remain compatible

- [ ] Test overlay equivalence, explicit field deletion and repeated fresh regeneration before implementation
- [ ] Move private catalog delta to versioned overlay with provenance and integrate generation into release build
- [ ] Extract memory pricing policy behind adapter, preserving call ordering before spend/budgets
- [ ] Run price/reload/canonical-memory accounting contracts, review and parent commit

## Task 3: LazyMCP package and UI boundaries

Files: extension lazy/{schema,resolver,cache,catalog,service,transport}, compatibility/mcp; existing MCP server.py/lazymcp_routes.py/lazymcp_public_resource.py/loopback_oauth.py and minimal manager invalidation adapters; dashboard LazyMCP-specific components/hooks

Interface: same public routes and describe/call/status schemas; upstream authenticated OperationContext and catalog authority remain canonical. Compatibility layer owns private LiteLLM imports

- [ ] Run existing selected authorization/cache/transport contracts and add extraction-boundary tests
- [ ] Extract own blocks while keeping manager startup/lifespan and upstream operations integrated
- [ ] Keep request-local principal/scope/credentials, revocation and rate-admission behavior; no global principal state
- [ ] Extract UI-specific connective logic without changing user flows
- [ ] Run MCP routing, OAuth resource, empty-scope denial, cache revocation, cancellation and existing loopback tests; review and parent commit

## Task 4: Provider OAuth, codecs and auxiliary routes

Files: extension providers/auth and codex Responses/reasoning/summary modules; compatibility/provider; existing ChatGPT/Anthropic authenticator/native transport policy modules and provider-specific Responses adapters

Interface: preserve existing exported authenticators/policy constructors, profile identity and per-deployment binding. STATICDUO_AUTH_READ_ONLY=true explicitly forbids every auth mutation and interactive or refresh network request

- [ ] Add readonly snapshot tests: valid reads without locks/writes, expired snapshots reject before network, unavailable profile rejects without login
- [ ] Extract credential stores and pure identity/reasoning policies, retaining enforcement before cache/retry/fallback
- [ ] Extract own summary/tool-search/reasoning codecs and auxiliary Live/Realtime behavior behind thin protocol adapters, preserving SSE state-machine boundaries
- [ ] Keep CustomLLM limitations explicit; no conversion to a different provider path merely to fit extension APIs
- [ ] Run OAuth/cross-profile/reasoning/replay/sync/async/cancellation/auxiliary-cost and Live/Realtime contracts; review and parent commit

## Task 5: Headroom and compression

Files: extension compression; existing headroom guardrail/native_text and translation entrypoints; existing Headroom tests

Interface: preserve request content roundtrip, tool namespaces, retrieval ordering, timeout/fail-open and token counters; no monetary pricing inside compressor

- [ ] Run baseline roundtrip and native translation tests; add external-module adapter dispatch tests
- [ ] Extract client/policies/native content handling while retaining required guardrail translation seams
- [ ] Run compression, failure/cancel, multimodal/tools and counters contracts; review and parent commit

## Task 6: Compatibility, release and nightly

Files: extension compatibility manifest/checks; release image/source manifest; nightly maintenance prompt/helpers and corresponding tests; operator controller/broker release documentation and source manifest

Interface: explicit core/extension/runtime/native ABI versions with compatibility rejection before promotion, no silent behavior fallback

- [ ] Add wheel installed-in-clean-environment and compatibility mismatch regressions
- [ ] Reuse upstream-equivalent functionality instead of retaining duplicate private implementation
- [ ] Integrate extension package checks, generated artifacts and fork-conflict inventory into nightly candidate validation
- [ ] Build complete committed candidate and publish/verify digest in docker.staticduo.com
- [ ] Validate temporary Fedora core/extension package and live priority contracts against isolated data
- [ ] Perform proportional whole-candidate review, make check and required coverage gates without relaxed thresholds

## Task 7: Final promotion

- [ ] Capture fresh private backups and preservation baseline for Fedora and NAS
- [ ] Deploy only Fedora LiteLLM to candidate registry digest; verify all mandatory functional/runtime/accounting checks
- [ ] Revalidate origin/main and regular-push tested candidate only after Fedora acceptance
- [ ] Deploy same verified digest only to NAS LiteLLM; verify functional acceptance, preservation and UGREEN registration
- [ ] Remove only task-owned temporary stage, retain private evidence/backups, release integration lock and verify timer next 04:00 Madrid
- [ ] Record final measurements of remaining fork insertion points, tests, runtime evidence and rollback image

All code ownership, concrete interface decisions, test commands and results are recorded in the execution ledger. Parent reconciles component results before publishing shared branches or promoting production
