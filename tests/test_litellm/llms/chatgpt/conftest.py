import json
import time

import pytest


@pytest.fixture
def chatgpt_tokens(tmp_path):
    for profile in ("default", "account2", "account3"):
        name = "auth.json" if profile == "default" else profile + ".json"
        (tmp_path / name).write_text(
            json.dumps(
                {
                    "access_token": "test-token-" + profile,
                    "account_id": "test-account-" + profile,
                    "expires_at": time.time() + 3600,
                }
            )
        )
    return str(tmp_path)
