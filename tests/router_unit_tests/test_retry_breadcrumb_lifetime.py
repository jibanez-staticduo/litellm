import datetime
import gc
import weakref
from collections.abc import Mapping
from typing import Final

import pytest
from starlette.requests import Request

from litellm import Router
from litellm.litellm_core_utils.litellm_logging import Logging


def _record_failed_request(router, metadata_key, prior_breadcrumbs=()):
    request = Request({"type": "http", "method": "POST", "path": "/v1/chat/completions", "headers": []})
    request._body = b"x" * 65536
    logging_obj = Logging(
        model="test-model",
        messages=[],
        stream=False,
        call_type="acompletion",
        start_time=datetime.datetime.now(),
        litellm_call_id="test-call",
        function_id="test-function",
    )
    logging_obj.model_call_details["litellm_params"] = {metadata_key: {"previous_models": list(prior_breadcrumbs)}}
    kwargs = {
        "model": "test-model",
        metadata_key: {"session_id": "test-session", "previous_models": prior_breadcrumbs},
        "litellm_logging_obj": logging_obj,
    }
    try:
        raise ValueError("failed attempt")
    except ValueError as exception:
        logging_obj.model_call_details["exception"] = exception
        router.log_retry(kwargs=kwargs, e=exception)

    return weakref.ref(request), weakref.ref(logging_obj), kwargs[metadata_key]["previous_models"]


@pytest.mark.parametrize("metadata_key", ["metadata", "litellm_metadata"])
def test_retry_breadcrumbs_do_not_retain_completed_request_graphs(metadata_key):
    router = Router(model_list=[])
    records: Final = tuple(_record_failed_request(router, metadata_key) for _ in range(25))
    gc.collect()

    assert all(request() is None and logger() is None for request, logger, _ in records)
    assert all(len(breadcrumbs) == 1 for _, _, breadcrumbs in records)
    for _, _, breadcrumbs in records:
        assert breadcrumbs == (
            {
                "model_group": "test-model",
                "deployment_id": None,
                "model": None,
                "base_model": None,
                "exception_type": "ValueError",
                "exception_string": "failed attempt",
                "attempted_retries": None,
            },
        )


@pytest.mark.parametrize("metadata_key", ["metadata", "litellm_metadata"])
def test_retry_breadcrumbs_keep_only_four_attempts_for_one_request(metadata_key):
    router: Final = Router(model_list=[])
    prior: Final = tuple({"exception_string": str(index)} for index in range(25))
    request, logger, breadcrumbs = _record_failed_request(router, metadata_key, prior)
    gc.collect()

    assert request() is None and logger() is None
    assert len(breadcrumbs) == 4
    assert breadcrumbs[:3] == prior[-3:]
    assert isinstance(breadcrumbs[-1], Mapping)
    assert breadcrumbs[-1]["exception_string"] == "failed attempt"
