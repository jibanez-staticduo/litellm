import datetime
import gc
import weakref

import pytest
from starlette.requests import Request

from litellm import Router
from litellm.litellm_core_utils.litellm_logging import Logging


def _record_failed_request(router, metadata_key):
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
    logging_obj.model_call_details["litellm_params"] = {metadata_key: {"previous_models": list(router.previous_models)}}
    kwargs = {
        "model": "test-model",
        metadata_key: {"session_id": "test-session"},
        "litellm_logging_obj": logging_obj,
    }
    try:
        raise ValueError("failed attempt")
    except ValueError as exception:
        logging_obj.model_call_details["exception"] = exception
        router.log_retry(kwargs=kwargs, e=exception)

    return weakref.ref(request), weakref.ref(logging_obj)


@pytest.mark.parametrize("metadata_key", ["metadata", "litellm_metadata"])
def test_retry_breadcrumbs_do_not_retain_completed_request_graphs(metadata_key):
    router = Router(model_list=[])
    references = [_record_failed_request(router, metadata_key) for _ in range(25)]

    # Distinguish an actual router-owned reference from ordinary collectable
    # exception/frame cycles; collecting cannot free router-owned requests.
    gc.collect()

    assert all(request() is None and logger() is None for request, logger in references)
    assert len(router.previous_models) == 4
    for breadcrumb in router.previous_models:
        assert "litellm_logging_obj" not in breadcrumb
        assert breadcrumb["model"] == "test-model"
        assert breadcrumb["exception_type"] == "ValueError"
        assert breadcrumb["exception_string"] == "failed attempt"
        assert breadcrumb[metadata_key] == {"session_id": "test-session"}
