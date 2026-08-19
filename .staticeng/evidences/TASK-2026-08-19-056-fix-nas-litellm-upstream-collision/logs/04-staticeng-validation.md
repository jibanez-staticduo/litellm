# StaticEng Validation

`staticeng_validate` was run after task and evidence closure and failed on inherited repository-wide StaticEng metadata debt:

- Broken links in `.staticeng/codemap.yml`
- Rule-of-local-knowledge violations in `.staticeng/codemap.yml`
- Missing CodeMaps across existing source directories

`staticeng_repair` dry-run was then run as required. It proposed hundreds of broad unrelated CodeMap creations plus normalization of artifacts owned by other tasks. No repair was applied to preserve unrelated worktree artifacts and task scope

Task-local `git diff --check` passed, and the evidence packet contains no detected key, bearer-token, or secret-variable values
