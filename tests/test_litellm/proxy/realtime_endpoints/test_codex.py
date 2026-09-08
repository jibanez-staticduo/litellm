import hashlib
import time

import pytest
from fastapi import HTTPException

from litellm.proxy.realtime_endpoints.codex import CodexRealtimeCall, decode_call, encode_call


def test_sideband_token_binds_owner_and_selected_account(monkeypatch):
    monkeypatch.setenv("LITELLM_SALT_KEY", "test-only-salt-for-codex-realtime")
    call = CodexRealtimeCall(
        call_id="rtc_test",
        model="gpt-live-1-codex",
        alias="gpt-live-1-codex",
        profile="account3",
        owner=hashlib.sha256(b"Bearer test-owner").hexdigest(),
        expires_at=time.time() + 300,
    )
    token = encode_call(call)
    assert "/" not in token
    assert "account3" not in token
    assert decode_call(token, "Bearer test-owner") == call
    with pytest.raises(HTTPException) as error:
        decode_call(token, "Bearer different-owner")
    assert error.value.status_code == 403
    with pytest.raises(HTTPException):
        decode_call(token[:30] + "tampered" + token[30:], "Bearer test-owner")


def test_sideband_rejects_expired_token(monkeypatch):
    monkeypatch.setenv("LITELLM_SALT_KEY", "test-only-salt-for-codex-realtime")
    call = CodexRealtimeCall(
        call_id="rtc_test",
        model="gpt-realtime-1.5",
        alias="gpt-realtime-1.5",
        owner=hashlib.sha256(b"Bearer test-owner").hexdigest(),
        expires_at=time.time() - 1,
    )
    with pytest.raises(HTTPException):
        decode_call(encode_call(call), "Bearer test-owner")


@pytest.mark.parametrize("token", ["", "rtc_other", "rtc_litellm_%%%%", "rtc_litellm_a"])
def test_sideband_rejects_malformed_tokens(token):
    with pytest.raises(HTTPException):
        decode_call(token, "Bearer test-owner")
