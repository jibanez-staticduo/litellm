---
id: TASK-2026-08-26-011-audit-gpt-thinking-alignment
complexity: complex
track: investigation
slice: foundation
status: done

# Post Implementation Task Updates

## Technical Architect: Post Implementation Expectations
- Audit found public GPT aliases missing reasoning metadata and therefore missing OpenCode variants.
- GPT-5.6 qualified routes omit native `max`; Codex catalogs omit `none` and may contain client-only `ultra` that must not be sent as raw effort.
- No runtime/configuration changes were made during the audit.
scr: null
parent: null
assigned_to: technical_architect
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-08-26-011 - Audit GPT Thinking Alignment

## Objective
Audit every GPT/ChatGPT model exposed by NAS and Fedora LiteLLM and determine whether LiteLLM metadata, `opencode-litellm`, official OpenCode, and local Codex expose the exact reasoning levels actually accepted by each resolved upstream model.

## Acceptance Criteria
- [ ] AC-1: Inventory every GPT/ChatGPT public group on both proxies, deployment/provider/account route, resolved upstream model, and differences between hosts.
- [ ] AC-2: Determine authoritative accepted reasoning controls/levels and defaults for each distinct upstream model using current official provider documentation and safe schema/probes where needed.
- [ ] AC-3: Compare LiteLLM `supports_reasoning`, supported parameters, model/group metadata, and request transformations against upstream capability.
- [ ] AC-4: Compare generated `opencode-litellm`/official OpenCode variants and local Codex catalog levels against the same capability matrix.
- [ ] AC-5: Explain specifically why `gpt-5.6-sol` currently has no selectable thinking level in OpenCode.
- [ ] AC-6: Return a per-model aligned/misaligned matrix and an atomic remediation plan; make no changes during this audit.

## Expected Evidence
- Signed read-only handoff with secrets/account credentials redacted, official source URLs, live metadata paths, versions, and safe probe results.

## Acceptance Criteria Verification Map
- [ ] AC-1
  - **Method:** live NAS/Fedora registry inspection
  - **Evidence:** signed handoff
- [ ] AC-2
  - **Method:** official docs and safe provider probes
  - **Evidence:** signed handoff
- [ ] AC-3
  - **Method:** LiteLLM metadata/transformation comparison
  - **Evidence:** signed handoff
- [ ] AC-4
  - **Method:** plugin/OpenCode/Codex resolved-config inspection
  - **Evidence:** signed handoff
- [ ] AC-5
  - **Method:** end-to-end trace for `gpt-5.6-sol`
  - **Evidence:** signed handoff
- [ ] AC-6
  - **Method:** architecture review
  - **Evidence:** signed handoff
