# Fedora Agent Defaults to GPT-5.6 Terra

## Summary

Fedora Hermes and OpenClaw defaults were changed to the default-account GPT-5.6 Terra model. Only the verified default fields were changed. Catalogs, fallbacks, provider entries, and unrelated settings were preserved

## Defaults

| Agent | Previous | New |
| --- | --- | --- |
| Hermes `model.default` | `chatgpt/gpt-5.5` | `chatgpt/gpt-5.6-terra` |
| OpenClaw `agents.defaults.model.primary` | `litellm/chatgpt/gpt-5.5` | `litellm/chatgpt/gpt-5.6-terra` |

## Backups

- Hermes: `/home/staticduo/.hermes/config.yaml.bak-terra-20260710T235442+0200` with mode `0600`
- OpenClaw: `/home/staticduo/.openclaw/openclaw.json.bak-terra-20260710T235442+0200` with mode `0600`
- Exact rollback commands: `backups-and-rollback.log`

## Validation And Status

- YAML and JSON parsing passed
- `hermes config check` passed with exit 0
- `hermes doctor` passed with exit 0; only optional provider/tool configuration warnings were reported
- `openclaw config validate` passed with exit 0 via the installed Node entry point
- Both user gateways restarted successfully
- Systemd and native gateway status report both gateways active/running
- OpenClaw retained 2 providers and 19 catalog models; catalog and fallback digests were unchanged
- No authentication or inference/completion calls were made

## Evidence Files

- `pre-inspection.log`
- `post-validation.log`
- `status.log`
- `backups-and-rollback.log`
