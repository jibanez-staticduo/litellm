# TASK-2026-08-26-007 Evidence Summary

## Result

Published `@staticeng/opencode-litellm@0.1.9`, pushed reconciled commit `1e32745a9d30d3a83d37a37dc197b47c86fb5339`, and replaced the active shared configuration's local plugin path with unversioned `@staticeng/opencode-litellm` as explicitly requested.

## Acceptance Criteria

- AC-1: PASS. Reconciled candidate passed 52/52 tests and prior official OpenCode 1.18.23 DeepSeek/Qwen reasoning verification.
- AC-2: PASS. The final 17-file tarball is reproducible at SHA-256 `b4c8e8d800b794cef692e02ca4ab6296f3a12b5501cd1d07eb7f5a55d3de28d2`.
- AC-3: PASS. Reconciled head `1e32745a9d30d3a83d37a37dc197b47c86fb5339` was pushed non-force and equals `origin/main`.
- AC-4: PASS. npm published `0.1.9`; registry integrity is `sha512-IBMwNMkPmCTyOlElGJ3rraWJ/TNRKTPFEUNdY6+CCgk6pNDzCTOv07YzR8Yfs8QQ4Z7+RNtZL02rbmer3fZYbw==`, SHA-1 is `7423338211d46d9800ba1d0313a89739def52134`, and downloaded registry tarball SHA-256 matches the candidate.
- AC-5: PASS. Backup `/home/staticduo/.config/opencode/opencode.json.backup-task-007-20260826T063449Z` is mode `0600`. Active config is valid JSON, mode `0600`, and changed only the tuple reference while preserving options hash `27438fdb4f05a11ba17c27dae4b1fae469957534b44d391f2178f5b1f137ba7c`.
- AC-6: PASS. Active config contains exactly one `@staticeng/opencode-litellm`, zero `file://`, and zero local repository paths. Official OpenCode 1.18.23 resolved the active npm plugin and discovered 29 LiteLLM models without production inference.
- AC-7: PASS. Pre-change config SHA-256 was `66772b3d57d1b6c8983c7ec4884d348ca48e1c91f63ed6f1315b6441c172f75f`; post-change SHA-256 is `77167c4b2aba293dd8215529b09ccc250c9204b7cc68008ce5f3c2f12edb6bc2`. Rollback is restoring the recorded backup or changing only the tuple reference to `@staticeng/opencode-litellm@0.1.8`.

## Verification Notes

- A first immediate post-publish registry pack hit transient npm cache propagation (`ETARGET`); after clearing npm cache, the registry pack succeeded and matched all metadata and content gates.
- An isolated synthetic discovery attempt resolved the published plugin but the one-shot mock response did not populate fixture models. Active non-production config resolution then succeeded with 29 discovered models. No user inference request was sent.
- No OpenCode core, LiteLLM source, Codex configuration, or unrelated plugin working-tree artifacts were modified for release execution.

## Documentation Impact

No further product or architecture documentation change is required. The package README and CodeMaps were already included in the reconciled release.
