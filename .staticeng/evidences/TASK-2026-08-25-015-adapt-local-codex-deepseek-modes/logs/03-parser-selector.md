# Parser and Selector Verification

Commands/checks passed:

```text
python3 -m json.tool <catalog>                         PASS
codex debug models                                    PASS
codex exec --strict-config ... --help                 PASS
codex app-server --stdio: initialize + model/list     PASS
```

Sanitized `model/list` target result:

```json
{
  "id": "deepseek-v4-flash-fp8-mtp",
  "defaultReasoningEffort": "max",
  "supportedReasoningEfforts": ["off", "low", "high", "max"],
  "isDefault": false
}
```

The generated Codex `0.147.0` app-server schema defines `ReasoningEffort` as a non-empty advertised string rather than a closed enum. This verifies `off` and `max` are accepted and preserved by this version. `medium` and `xhigh` remain generic parser-compatible strings for unrelated models, but are unavailable for this target because `model/list` does not advertise them. This target-scoped result preserves unrelated model semantics
