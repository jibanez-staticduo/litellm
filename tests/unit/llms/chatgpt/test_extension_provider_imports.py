"""Core-dependent concrete exports must load in either fresh-process import order."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Final

import pytest

_ENTRYPOINTS: Final = (
    (
        "staticduo_litellm.providers.anthropic.authenticator",
        "litellm.llms.anthropic.authenticator",
        "AnthropicAuthenticator",
    ),
    (
        "staticduo_litellm.codex.summary",
        "litellm.responses.litellm_completion_transformation.hosted_vllm_codex_summary",
        "HostedVLLMCodexSummaryStream",
    ),
)


@pytest.mark.parametrize("extension,facade,symbol", _ENTRYPOINTS)
@pytest.mark.parametrize("core_first", (False, True))
def test_provider_extension_import_order_in_fresh_process(extension, facade, symbol, core_first, tmp_path):
    root: Final = Path(__file__).resolve().parents[4]
    prefix: Final = "import litellm\n" if core_first else ""
    script: Final = (
        prefix
        + f"""
import importlib
import json
from pathlib import Path
module = importlib.import_module({extension!r})
legacy = importlib.import_module({facade!r})
assert getattr(module, {symbol!r}) is getattr(legacy, {symbol!r})
import litellm
if {symbol!r} == "AnthropicAuthenticator":
    directory = Path({str(tmp_path)!r})
    record = directory / "auth.json"
    record.write_text(json.dumps({{"access_token":"sk-ant-oat01-offline", "expires_at":4000.0, "scope":"user:inference"}}))
    before = record.read_bytes()
    auth = module.AnthropicAuthenticator(module.AnthropicOAuthConfig(use_anthropic_oauth=True, anthropic_token_dir=str(directory)), clock=lambda:2000.0)
    assert auth.get_access_token() == "sk-ant-oat01-offline"
    assert record.read_bytes() == before
    assert tuple(directory.iterdir()) == (record,)
else:
    from litellm.responses.streaming_iterator import BaseResponsesAPIStreamingIterator
    assert issubclass(module.HostedVLLMCodexSummaryStream, BaseResponsesAPIStreamingIterator)
    assert module.summary_requested("hosted_vllm_codex", {{"reasoning":{{"summary":"auto"}}}})
    assert not module.summary_requested("openai", {{"reasoning":{{"summary":"auto"}}}})
print("import-order-contract-ok")
"""
    )
    environment: Final = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join((str(root), str(root / "extensions/staticduo-litellm/src"))),
        "LITELLM_LOCAL_MODEL_COST_MAP": "True",
        "STATICDUO_AUTH_READ_ONLY": "true",
    }
    result: Final = subprocess.run(
        [sys.executable, "-c", script], cwd=tmp_path, env=environment, capture_output=True, text=True, timeout=30
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "import-order-contract-ok"
