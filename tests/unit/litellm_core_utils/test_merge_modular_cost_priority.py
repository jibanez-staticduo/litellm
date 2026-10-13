"""Regression for canonical alias pricing alongside provider-reported costs."""

import copy
import datetime
import json
import time

import pytest

import litellm
from litellm.litellm_core_utils.litellm_logging import Logging
from litellm.types.utils import ModelResponse, Usage


@pytest.fixture
def canonical_luna(monkeypatch, tmp_path):
    from litellm.proxy import proxy_server

    monkeypatch.setattr(litellm, "model_cost", copy.deepcopy(litellm.model_cost))
    (tmp_path / "auth.json").write_text(
        json.dumps({"access_token": "synthetic-unit-test", "expires_at": time.time() + 86400})
    )
    monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(tmp_path))
    router = litellm.Router(
        model_list=[
            {
                "model_name": "gpt-6-luna",
                "litellm_params": {"model": "chatgpt/gpt-6-luna", "api_key": "synthetic-unit-test"},
                "model_info": {
                    "id": "merge-canonical-luna",
                    "input_cost_per_token": 1e-7,
                    "output_cost_per_token": 5e-7,
                    "cache_read_input_token_cost": 1e-8,
                    "input_cost_per_token_above_272k_tokens": 2e-7,
                    "output_cost_per_token_above_272k_tokens": 7.5e-7,
                    "cache_read_input_token_cost_above_272k_tokens": 2e-8,
                },
            }
        ]
    )
    monkeypatch.setattr(proxy_server, "llm_router", router)


@pytest.mark.parametrize("request_model", ["memory-model", "memory_model"])
@pytest.mark.parametrize("reported_cost", [0.0, 9.0])
@pytest.mark.parametrize("prompt_tokens", [100, 300_000])
@pytest.mark.parametrize("cache_hit", [False, True])
def test_memory_alias_overrides_provider_header_before_logging(
    canonical_luna, request_model, reported_cost, prompt_tokens, cache_hit
):
    started = datetime.datetime.now()
    logging_obj = Logging(
        model="hosted_vllm/qwen3.8-flash-next",
        messages=[{"role": "user", "content": "canonical price"}],
        stream=False,
        call_type="completion",
        start_time=started,
        litellm_call_id="merge-cost-priority",
        function_id="merge-cost-priority",
    )
    logging_obj.update_environment_variables(
        litellm_params={
            "proxy_server_request": {"body": {"model": request_model}},
            "metadata": {"model_group": "qwen3.8-flash-next", "original_model_group": request_model},
        },
        optional_params={},
        custom_llm_provider="hosted_vllm",
    )
    logging_obj._provider_reported_cost = reported_cost
    logging_obj.model_call_details["cache_hit"] = cache_hit
    response = ModelResponse(
        model="qwen3.8-flash-next",
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=20,
            prompt_tokens_details={"cached_tokens": 40},
            cost=reported_cost,
        ),
    )
    response._hidden_params = {"response_cost": reported_cost}
    logging_obj._process_hidden_params_and_response_cost(response, started, started)
    expected = (
        0.0
        if cache_hit
        else (
            (prompt_tokens - 40) * 1e-7 + 40 * 1e-8 + 20 * 5e-7
            if prompt_tokens <= 272_000
            else (prompt_tokens - 40) * 2e-7 + 40 * 2e-8 + 20 * 7.5e-7
        )
    )
    assert response._hidden_params["response_cost"] == pytest.approx(expected)
    assert logging_obj.model_call_details["response_cost"] == pytest.approx(expected)
    payload = logging_obj.model_call_details["standard_logging_object"]
    assert payload["response_cost"] == pytest.approx(expected)
    assert payload["model"] == "hosted_vllm/qwen3.8-flash-next"
    assert payload["custom_llm_provider"] == "hosted_vllm"
    assert response.model == "qwen3.8-flash-next"
    assert response.usage.cost == reported_cost
    if not cache_hit:
        assert logging_obj.cost_breakdown["pricing_reference_model"] == "gpt-6-luna"
