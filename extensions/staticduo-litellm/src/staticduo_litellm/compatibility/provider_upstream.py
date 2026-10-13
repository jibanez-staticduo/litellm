"""Fail closed when the core OAuth algorithm changes during an upstream update."""

import hashlib
from typing import Final

CHATGPT_OAUTH_UPSTREAM_COMMIT: Final = "541e3ed5305a530ebef74d5684d3aca2632c1009"
CHATGPT_OAUTH_UPSTREAM_PATH: Final = "litellm/llms/chatgpt/authenticator.py"
CHATGPT_OAUTH_UPSTREAM_SHA256: Final = "fae5a0af1eb25b060c09c47591f3921bb10c4590ee8b0468f6091d5fb0fa84b6"


CHATGPT_OAUTH_UPSTREAM_AST_SHA256: Final = "c9f9ff21090293b6b22393a8b521828707e757f048d43000e3861853c2c2ded2"


class ProviderUpstreamDriftError(RuntimeError):
    pass


def check_provider_upstream_source(source: bytes) -> None:
    """Nightly passes the fresh upstream file before preparing a candidate."""
    if hashlib.sha256(source).hexdigest() != CHATGPT_OAUTH_UPSTREAM_SHA256:
        raise ProviderUpstreamDriftError(
            "ChatGPT upstream OAuth changed; reconcile oauth_engine.py and provider contracts before promotion"
        )
