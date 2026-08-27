# Redacted `/model/new` Recreation Payloads

Exact credential-bearing payloads are stored only in each protected host-local task directory. The following redacted projections prove the payload shape, identity, upstream, and critical routing metadata without exposing credentials or authorization material

## Fedora

```json
[
  {
    "model_name": "chatgpt/gpt-5.3-codex",
    "litellm_params": {
      "model": "chatgpt/gpt-5.3-codex",
      "drop_params": true,
      "additional_drop_params": ["max_output_tokens"],
      "merge_reasoning_content_in_choices": false
    },
    "model_info": {
      "id": "b175303a-eb59-43e4-ad65-22c42a98c649",
      "db_model": true,
      "direct_access": true,
      "blocked": false,
      "access_via_team_ids": "[REDACTED: one exact team ID retained on host]"
    }
  },
  {
    "model_name": "chatgpt-account2/gpt-5.3-codex",
    "litellm_params": {
      "model": "chatgpt/gpt-5.3-codex",
      "chatgpt_auth_profile": "account2",
      "drop_params": true,
      "additional_drop_params": ["max_output_tokens"],
      "merge_reasoning_content_in_choices": false
    },
    "model_info": {
      "id": "51d9260e-ac4d-4294-ab95-930afdb5a012",
      "db_model": true
    }
  }
]
```

## NAS

```json
[
  {
    "model_name": "gpt-5.3-codex",
    "litellm_params": {"model": "chatgpt/gpt-5.3-codex"},
    "model_info": {"id": "83500e6b-6faf-44c8-a4d2-d557f72d11ec", "db_model": true, "direct_access": true, "blocked": false}
  },
  {
    "model_name": "chatgpt/gpt-5.3-codex",
    "litellm_params": {"model": "chatgpt/gpt-5.3-codex", "drop_params": true, "additional_drop_params": ["max_output_tokens"]},
    "model_info": {"id": "72c9e569-3317-4412-ba67-566e172b295d", "db_model": true, "access_via_team_ids": "[REDACTED: two exact team IDs retained on host]"}
  },
  {
    "model_name": "chatgpt-account2/gpt-5.3-codex",
    "litellm_params": {"model": "chatgpt/gpt-5.3-codex", "chatgpt_auth_profile": "account2", "drop_params": true, "additional_drop_params": ["max_output_tokens"]},
    "model_info": {"id": "94126f16-fdbb-48e7-9586-b8a1a68719d5", "db_model": true, "access_via_team_ids": "[REDACTED: two exact team IDs retained on host]"}
  },
  {
    "model_name": "defend/gpt-5.5",
    "litellm_params": {"model": "openai/chatgpt/gpt-5.5", "api_base": "[REDACTED]", "api_key": "[REDACTED]"},
    "model_info": {"id": "67c996f8-38d7-4406-833b-601735d8a364", "db_model": true, "direct_access": true, "access_via_team_ids": "[REDACTED: two exact team IDs retained on host]"}
  }
]
```

The protected payloads also retain every exact optional LiteLLM parameter and model-info field returned by the raw database rows. Recreation would preserve each original UUID through `model_info.id`
