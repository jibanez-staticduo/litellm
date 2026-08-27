# TASK-2026-08-27-005 Evidence Summary

## Findings

PASS. Fresh independent read-only runtime gates close the three gaps from Task 020. Official OpenCode `1.18.23` with plugin `0.2.2` passed the complete retained selector/default/wire matrix against current sanitized NAS and Fedora discovery shapes. Codex `0.149.1` passed all 40 retained row/mode Responses captures plus eight ordered row-switch captures. Fedora host-local API, read-only PostgreSQL, access-integrity, and eight retired-alias unavailable/no-redirect gates passed

No production configuration, package cache, generated cache, route, database row, access rule, or process was mutated or restarted. Loopback captures retained only path, model, reasoning fields, input presence, and authorization presence; no prompt or response content was retained

## Acceptance Criteria

- **AC-1: PASS.** Two isolated official OpenCode `1.18.23` runs loaded plugin `0.2.2` once each from the installed published package against fresh sanitized live NAS and Fedora metadata. Each exposed all eight retained representative rows, exact ordered modes, and exact defaults. Each produced 40 named-mode plus eight intrinsic-default wire captures, including DeepSeek `off -> none`, Qwen `off -> enable_thinking=false` with no effort, native values unchanged, and default behavior. Twenty-one currently deployed exact aliases mapped equivalently; no near-match or retired alias was present. Scoped process logs contain one successful metadata load, zero load failures, zero stale-version hits, and no double load
- **AC-2: PASS.** Fresh isolated Codex `0.149.1` used a temporary `CODEX_HOME`, state, cache, copied active eight-row catalog, loopback-only Responses provider, and placeholder auth helper. All 40 row/mode runs sent exact `/v1/responses` `reasoning.effort` values. Eight reverse-order row switches sent the newly selected row's first supported effort with no stale DeepSeek `high` or prior-row leakage. DeepSeek exposes `none/low/high/max`; Qwen exposes `low/medium/xhigh`; neither `off` nor `ultra` appears. Active production DeepSeek `high`, config, catalog, and generated-cache hash/mtime remained unchanged
- **AC-3: PASS.** Fedora host-local authenticated `/health/readiness`, `/model/info`, `/model_group/info`, `/router/settings`, and `/v1/models` returned HTTP 200 and contain neither normal GPT-5.3 Codex nor Spark. A PostgreSQL `BEGIN TRANSACTION READ ONLY` check found zero target deployment rows, aliases, team/router dependencies, and access-group dependencies. The authenticated projection/access fingerprint was equal before and after probes
- **AC-4: PASS.** All eight exact retired normal/Spark aliases returned HTTP 400 ordinary unavailable classification, no deployment identity, and no redirect/location. Evidence retains only alias, status, error class, deployment presence, and redirect presence. No output content is retained
- **AC-5: PASS.** This packet was generated independently from live/captured-safe current state rather than accepting implementation logs as proof. Evidence contains no credentials, authorization values, raw configuration, prompt text, response content, deployment IDs, or database payloads

## Runtime Matrix

| Family | OpenCode selector/wire | Default capture | Codex Responses |
| --- | --- | --- | --- |
| GPT-5.4 | `none,low,medium,high,xhigh` unchanged | `none` | same five |
| GPT-5.4 Mini | `none,low,medium,high,xhigh` unchanged | `none` | same five |
| GPT-5.5 | `none,low,medium,high,xhigh` unchanged | `medium` | same five |
| GPT-5.6 Luna | `none,low,medium,high,xhigh,max` unchanged | `medium` | same six |
| GPT-5.6 Sol | `none,low,medium,high,xhigh,max` unchanged | `medium` | same six |
| GPT-5.6 Terra | `none,low,medium,high,xhigh,max` unchanged | `medium` | same six |
| DeepSeek V4 Flash | visible `off,low,high,max`; `off -> none` | `max` | `none,low,high,max` |
| Qwen3.8 | visible `off,low,medium,xhigh`; `off -> enable_thinking=false` only | `xhigh` | `low,medium,xhigh` |

OpenCode totals are 40 named-mode captures and eight intrinsic-default captures per metadata source, 96 total. Codex totals are 40 every-mode captures and eight row-switch captures, 48 total

## Evidence Index

- `logs/opencode-nas.json`: current sanitized NAS metadata shape, selector/default/alias inventory, 49 captures including the additional deployed DeepSeek alias, and scoped OpenCode log audit
- `logs/opencode-fedora.json`: current sanitized Fedora metadata shape with the same complete matrix and scoped OpenCode log audit
- `logs/codex-wire.json`: active eight-row catalog matrix, 40 every-mode plus eight switch captures, zero failures, and production-file non-mutation hashes
- `logs/fedora-api-probes.json`: authenticated host-local API absence, eight bounded retired-alias classifications, and before/after access integrity
- `logs/fedora-raw-db.jsonl`: four read-only aggregate absence/dependency checks
- `scripts/runtime_clients.py`: independent isolated client harness; it stores no secret and targets loopback only

## Validation

- `python3 -m py_compile .../scripts/runtime_clients.py`: PASS
- Official OpenCode harness, NAS metadata: PASS, `1.18.23`, plugin `0.2.2`, 49 captures, zero scoped load failures
- Official OpenCode harness, Fedora metadata: PASS, `1.18.23`, plugin `0.2.2`, 49 captures, zero scoped load failures
- Official Codex harness: PASS, `0.149.1`, 48/48 captures, zero failures, production files unchanged
- Fedora authenticated API and retired probes: PASS, five HTTP-200 read APIs and eight HTTP-400 unavailable/no-deployment/no-redirect rows
- Fedora PostgreSQL transaction: PASS, all eight aggregate target/dependency counts are zero

## Residual Risk

The OpenCode runs use sanitized shapes captured immediately from host-local authenticated NAS and Fedora APIs rather than retaining secret-bearing raw API bodies. This proves official-client serialization against current model identities and safe capability fields while honoring the evidence boundary. It does not perform production inference. The complete deployed alias set is 21 because aliases absent from discovery are intentionally not fabricated

[Agent Message] From: tester To: product_manager

Findings-first handoff: PASS. Fresh independent read-only OpenCode, Codex, and Fedora runtime gates now satisfy Task 005 AC-1 through AC-5 and provide the missing Task 020 closure evidence. No blocker found
