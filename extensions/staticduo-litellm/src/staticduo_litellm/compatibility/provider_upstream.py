"""Fail closed when the core OAuth algorithm changes during an upstream update."""

import hashlib
from typing import Final

CHATGPT_OAUTH_UPSTREAM_COMMIT: Final = "2e27a02a9fce9bdc6ece13ba3cb8222dc5b6ecfa"
CHATGPT_OAUTH_UPSTREAM_PATH: Final = "litellm/llms/chatgpt/authenticator.py"
CHATGPT_OAUTH_UPSTREAM_SHA256: Final = "aff9d43414793e2690e7b77b9396051c1b797e09a0b458bc989f398539548d97"
CHATGPT_OAUTH_UPSTREAM_AST_SHA256: Final = "cad2dd1594852752a046c0703830c991e1496bf8161b68a357b89819b219138b"


class ProviderUpstreamDriftError(RuntimeError):
    pass


def check_provider_upstream_source(source: bytes) -> None:
    """Nightly passes the fresh upstream file before preparing a candidate."""
    if hashlib.sha256(source).hexdigest() != CHATGPT_OAUTH_UPSTREAM_SHA256:
        raise ProviderUpstreamDriftError(
            "ChatGPT upstream OAuth changed; reconcile oauth_engine.py and provider contracts before promotion"
        )
