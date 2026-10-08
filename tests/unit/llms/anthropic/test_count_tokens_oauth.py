"""
Tests for Anthropic CountTokens API OAuth token handling.

Verifies that get_required_headers() correctly handles OAuth tokens
(sk-ant-oat*) by delegating to optionally_handle_anthropic_oauth().

Regression test for https://github.com/BerriAI/litellm/issues/22040
"""

import os
import sys
from typing import Final

import httpx
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../..")))

from litellm.llms.anthropic.count_tokens.transformation import (
    AnthropicCountTokensConfig,
)

# Fake tokens for testing (not real secrets)
FAKE_OAUTH_TOKEN = "sk-ant-oat01-fake-token-for-testing-123456789abcdef"
FAKE_REGULAR_KEY = "sk-ant-api03-regular-key-for-testing-123456789"


@pytest.mark.asyncio
async def test_count_tokens_native_beta_cannot_override_selected_oauth_credential():
    from litellm.llms.anthropic.count_tokens.handler import AnthropicCountTokensHandler
    from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler

    def upstream(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {FAKE_OAUTH_TOKEN}"
        assert "x-api-key" not in request.headers
        assert "x-litellm-api-key" not in request.headers
        assert "native-beta" in request.headers["anthropic-beta"].split(",")
        assert "oauth" in request.headers["anthropic-beta"]
        assert "token-counting" in request.headers["anthropic-beta"]
        return httpx.Response(200, json={"input_tokens": 27})

    client: Final = AsyncHTTPHandler(transport=httpx.MockTransport(upstream))
    handler: Final = AnthropicCountTokensHandler(http_client=client)
    try:
        result: Final = await handler.handle_count_tokens_request(
            model="claude-test-model",
            messages=[{"role": "user", "content": "hi"}],
            api_key=FAKE_OAUTH_TOKEN,
            extra_headers={
                "Anthropic-Beta": "native-beta",
                "authorization": "Bearer override-must-not-be-used",
                "x-api-key": FAKE_REGULAR_KEY,
                "x-litellm-api-key": "proxy-key-must-not-be-forwarded",
            },
        )
        assert result == {"input_tokens": 27}
    finally:
        await client.client.aclose()


@pytest.mark.asyncio
async def test_native_client_count_preserves_headers_and_original_body():
    import json
    from litellm.llms.anthropic.count_tokens.handler import AnthropicCountTokensHandler
    from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler

    body: Final = {
        "model": "native-model",
        "messages": [{"role": "user", "content": "hello"}],
        "system": [{"type": "text", "text": "native billing"}],
        "native_feature": {"keep": True},
    }
    client_headers: Final = {
        "User-Agent": "claude-cli/native",
        "anthropic-beta": "native-beta",
        "anthropic-version": "native-version",
        "authorization": "Bearer wrong-account",
        "Host": "proxy-host",
        "Content-Length": "999",
        "x-litellm-api-key": "proxy-key",
    }

    def upstream(request: httpx.Request) -> httpx.Response:
        assert request.headers["authorization"] == f"Bearer {FAKE_OAUTH_TOKEN}"
        assert request.headers["user-agent"] == client_headers["User-Agent"]
        assert request.headers["anthropic-beta"] == client_headers["anthropic-beta"]
        assert "x-litellm-api-key" not in request.headers
        assert request.headers["host"] == "api.anthropic.com"
        assert json.loads(request.content) == body
        return httpx.Response(200, json={"input_tokens": 7})

    client: Final = AsyncHTTPHandler(transport=httpx.MockTransport(upstream))
    try:
        result: Final = await AnthropicCountTokensHandler(http_client=client).handle_count_tokens_request(
            model="native-model",
            messages=body["messages"],
            api_key=FAKE_OAUTH_TOKEN,
            optional_params=body,
            extra_headers=client_headers,
            native_client=True,
        )
        assert result == {"input_tokens": 7}
    finally:
        await client.client.aclose()


class TestCountTokensOAuthHeaders:
    """Tests that count_tokens headers are correct for both regular and OAuth keys."""

    def test_regular_api_key_uses_x_api_key(self):
        """Regular API keys should be sent via x-api-key header."""
        config = AnthropicCountTokensConfig()
        headers = config.get_required_headers(FAKE_REGULAR_KEY)

        assert headers["x-api-key"] == FAKE_REGULAR_KEY
        assert "authorization" not in headers

    def test_oauth_key_uses_bearer_authorization(self):
        """OAuth tokens (sk-ant-oat*) should be sent via Authorization: Bearer."""
        config = AnthropicCountTokensConfig()
        headers = config.get_required_headers(FAKE_OAUTH_TOKEN)

        assert headers.get("authorization") == f"Bearer {FAKE_OAUTH_TOKEN}"
        assert "x-api-key" not in headers

    def test_oauth_key_sets_oauth_beta_header(self):
        """OAuth tokens should trigger the anthropic-beta oauth header."""
        config = AnthropicCountTokensConfig()
        headers = config.get_required_headers(FAKE_OAUTH_TOKEN)

        assert "oauth-2025-04-20" in headers.get("anthropic-beta", "")

    def test_regular_key_preserves_token_counting_beta(self):
        """Regular keys should keep the token-counting beta header."""
        config = AnthropicCountTokensConfig()
        headers = config.get_required_headers(FAKE_REGULAR_KEY)

        assert "token-counting" in headers.get("anthropic-beta", "")

    def test_headers_always_have_content_type(self):
        """Both regular and OAuth paths should have Content-Type."""
        config = AnthropicCountTokensConfig()

        for key in [FAKE_REGULAR_KEY, FAKE_OAUTH_TOKEN]:
            headers = config.get_required_headers(key)
            assert headers["Content-Type"] == "application/json"

    def test_headers_always_have_anthropic_version(self):
        """Both paths should have anthropic-version."""
        config = AnthropicCountTokensConfig()

        for key in [FAKE_REGULAR_KEY, FAKE_OAUTH_TOKEN]:
            headers = config.get_required_headers(key)
            assert headers["anthropic-version"] == "2023-06-01"

    def test_oauth_key_preserves_token_counting_beta(self):
        """OAuth tokens must preserve the token-counting beta alongside the OAuth beta."""
        config = AnthropicCountTokensConfig()
        headers = config.get_required_headers(FAKE_OAUTH_TOKEN)

        beta_value = headers.get("anthropic-beta", "")
        assert "token-counting" in beta_value, f"token-counting beta missing from OAuth headers: {beta_value}"
        assert "oauth-2025-04-20" in beta_value, f"oauth beta missing from OAuth headers: {beta_value}"
