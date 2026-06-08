---
id: TASK-2026-06-08-003
title: Fix MCP update with null tool display maps
status: active
complexity: standard
track: implementation
slice: logic
assigned_to: developer
handoff_from: product_manager
created_at: 2026-06-08
scr: none
parent: TASK-2026-06-08-002
---

# Task: Fix MCP Update With Null Tool Display Maps

## Classification

- Complexity: `standard`
- Track: `implementation`
- Slice: `logic`

## Production Evidence

After deploying TASK-2026-06-08-002, editing the Memory MCP still fails on save.

Recent production logs show repeated `PUT /v1/mcp/server` 500 with:

```text
prisma.errors.MissingRequiredValueError: Unable to match input value to any allowed input type for the field.
Parse errors: [`data.tool_name_to_display_name`: A value is required but not set, ...]
```

The Memory MCP currently has `tool_name_to_display_name: null` and `tool_name_to_description: null` in list output. UI save appears to submit one or both null values, and update data passes them to Prisma incorrectly.

## Acceptance Criteria

- AC-1: MCP update accepts UI payloads that include nullable optional map fields such as `tool_name_to_display_name` and `tool_name_to_description` without producing Prisma `MissingRequiredValueError`.
- AC-2: Preserve explicit non-null map updates.
- AC-3: Do not wipe existing maps unintentionally during partial update unless caller explicitly provides a valid empty map.
- AC-4: Add focused regression test for update payload with `tool_name_to_display_name=None` and/or `tool_name_to_description=None`.
- AC-5: Run focused tests and ruff.
- AC-6: Produce evidence under `.staticeng/evidences/TASK-2026-06-08-003-fix-mcp-null-tool-display-update/`.

## Constraints

- Keep scope to MCP update null optional map fields.
- No production DB mutation except deploy verification endpoints.
- Do not expose secrets.

## Handoff

[Agent Message] From: product_manager To: developer

Fix the remaining MCP Memory save failure caused by nullable optional map fields being passed to Prisma update. Add regression coverage and evidence. Do not deploy; PMA will deploy after review.
