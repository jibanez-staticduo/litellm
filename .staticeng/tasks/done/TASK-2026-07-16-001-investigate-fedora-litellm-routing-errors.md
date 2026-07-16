---
id: TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors
complexity: standard
track: investigation
slice: foundation
status: done
scr: null
parent: null
assigned_to: explorer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-16-001 - Investigate Fedora LiteLLM Routing Errors

## Classification
- **complexity:** standard
- **track:** investigation
- **slice:** foundation

## Objective
Determine whether the Fedora LiteLLM deployment has the same failures shown in the supplied logs, identify each independent root cause, and define the minimal safe repair without changing runtime state.

## Scope
- Inspect this repository's deployment configuration and the running Fedora Docker services read-only.
- Diagnose the ChatGPT deployment cooldowns caused by one 401 and one context-window failure.
- Diagnose the invalid public model name `qwen3.6-35b-a3b-uncensored-nvfp4`.
- Compare configured, database-backed, and client-requested model names where safely observable.
- Do not print secrets, auth material, prompts, responses, keys, headers, account identifiers, or full environment/config files.
- Do not mutate containers, databases, credentials, model configuration, or OpenCode configuration.

## Acceptance Criteria
- [x] AC-1: Report whether Fedora reproduces each supplied failure class.
- [x] AC-2: Map each failure to its immediate and underlying cause with sanitized evidence.
- [x] AC-3: Identify the exact configuration/runtime surfaces requiring repair.
- [x] AC-4: Propose a minimal repair and verification plan that preserves unrelated models and settings.
- [x] AC-5: Evidence packet exists under `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/` with `SUMMARY.md` and sanitized logs.

## Handoff
[Agent Message] From: product_manager To: explorer

Investigate read-only on Fedora using this task file. Inspect repository deployment files, running Docker state, sanitized recent logs, model inventory, and relevant client model configuration. Distinguish 401 authentication, context overflow/cooldown behavior, and invalid model alias failures. Return the shared output contract and create the required evidence packet. Do not mutate runtime or expose secrets.

# Post Implementation Task Updates

## Explorer: Post Implementation Expectations

- Investigation completed read-only against Fedora runtime, deployment files, recent logs, runtime model inventory, repository router paths, and sanitized client configuration
- AC-1: PASS. Fedora reproduces ChatGPT 401/cooldown exhaustion and the invalid Qwen alias; no context-window overflow marker appears in the inspected 36-hour window
- AC-2: PASS. Immediate and underlying causes are mapped in the evidence summary with request-level counts and sanitized code/config evidence
- AC-3: PASS. Exact repair surfaces are the affected ChatGPT auth profile, database-backed model/router settings where proven necessary, Fedora live router config, and Fedora OpenCode catalog/overrides
- AC-4: PASS. The minimal repair and verification plan preserves unrelated models, profiles, and settings
- AC-5: PASS. Evidence packet exists at `.staticeng/evidences/TASK-2026-07-16-001-investigate-fedora-litellm-routing-errors/`
- Runtime, Docker services, databases, credentials, auth material, LiteLLM configuration, and OpenCode configuration were not changed
