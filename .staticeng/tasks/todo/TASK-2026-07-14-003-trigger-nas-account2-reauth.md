---
id: TASK-2026-07-14-003-trigger-nas-account2-reauth
complexity: tiny
track: implementation
slice: qa
status: todo
scr: null
parent: null
assigned_to: developer
handoff_from: product_manager
reopened_count: 0
---

# Task: TASK-2026-07-14-003 - Trigger NAS Account2 Reauthentication

## Objective
Safely trigger a fresh device-auth flow for NAS/local `chatgpt-account2/gpt-5.6-sol` and return the transient URL/code directly to the user.

## Acceptance Criteria
- [ ] AC-1: Exactly one account2 auth trigger is made.
- [ ] AC-2: Invalid stale auth state is backed up, not deleted, only if it blocks device auth.
- [ ] AC-3: URL/code are returned transiently and never persisted in repo/evidence/memory/git.
- [ ] AC-4: No login is completed by the agent and no unrelated state is changed.

## Handoff
[Agent Message] From: product_manager To: developer

Trigger NAS/local account2 device auth once. If stale invalid account2 credentials block device flow, atomically rotate them to a mode-0600 timestamped backup, then trigger exactly once. Return URL/code directly only; never write them to files/evidence/git. Do not complete login or commit.
