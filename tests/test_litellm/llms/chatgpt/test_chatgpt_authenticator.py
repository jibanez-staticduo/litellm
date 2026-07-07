import base64
import json
import os
import time
from unittest.mock import mock_open, patch

import pytest

from litellm.llms.chatgpt.authenticator import Authenticator


def _make_jwt(payload: dict) -> str:
    header = {"alg": "none", "typ": "JWT"}

    def _b64(obj: dict) -> str:
        raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")

    return f"{_b64(header)}.{_b64(payload)}."


class TestChatGPTAuthenticator:
    @pytest.fixture
    def authenticator(self):
        with patch("os.path.exists", return_value=True):
            return Authenticator()

    def test_get_access_token_from_file(self, authenticator):
        future_time = time.time() + 3600
        auth_data = json.dumps({"access_token": "token-123", "expires_at": future_time})

        with patch("builtins.open", mock_open(read_data=auth_data)):
            token = authenticator.get_access_token()
            assert token == "token-123"

    def test_get_access_token_refresh(self, authenticator):
        past_time = time.time() - 10
        auth_data = json.dumps(
            {
                "access_token": "token-old",
                "refresh_token": "refresh-123",
                "expires_at": past_time,
            }
        )
        refreshed = {
            "access_token": "token-new",
            "refresh_token": "refresh-123",
            "id_token": "id-123",
        }

        with (
            patch("builtins.open", mock_open(read_data=auth_data)),
            patch.object(authenticator, "_refresh_tokens", return_value=refreshed),
        ):
            token = authenticator.get_access_token()
            assert token == "token-new"

    def test_get_account_id_from_id_token(self, authenticator):
        id_token = _make_jwt({"https://api.openai.com/auth": {"chatgpt_account_id": "acct-123"}})
        auth_data = json.dumps({"id_token": id_token})

        with (
            patch("builtins.open", mock_open(read_data=auth_data)),
            patch.object(authenticator, "_write_auth_file") as mock_write,
        ):
            account_id = authenticator.get_account_id()
            assert account_id == "acct-123"
            mock_write.assert_called_once()
            assert mock_write.call_args[0][0]["account_id"] == "acct-123"

    def test_default_auth_file_uses_environment_fallbacks(self, tmp_path, monkeypatch):
        token_dir = tmp_path / "default"
        monkeypatch.setenv("CHATGPT_TOKEN_DIR", str(token_dir))
        monkeypatch.setenv("CHATGPT_AUTH_FILE", "env-auth.json")

        authenticator = Authenticator()

        assert authenticator.token_dir == str(token_dir)
        assert authenticator.auth_file == os.path.join(str(token_dir), "env-auth.json")
        assert token_dir.exists()

    def test_auth_profile_selects_profile_auth_file(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CHATGPT_TOKEN_DIR", raising=False)
        monkeypatch.delenv("CHATGPT_AUTH_FILE", raising=False)
        token_dir = tmp_path / "profiles"

        authenticator = Authenticator(
            {
                "chatgpt_token_dir": str(token_dir),
                "chatgpt_auth_profile": "account2",
            }
        )

        assert authenticator.token_dir == str(token_dir)
        assert authenticator.auth_file == os.path.join(str(token_dir), "account2.json")

    @pytest.mark.parametrize(
        "profile_name",
        [
            "",
            "   ",
            ".",
            "..",
            "../account2",
            "account2/other",
            "account2\\other",
            "/account2",
            "account2.json",
            "account 2",
            "account:2",
        ],
    )
    def test_auth_profile_rejects_unsafe_logical_names(self, tmp_path, profile_name):
        with pytest.raises(ValueError, match="chatgpt_auth_profile"):
            Authenticator(
                {
                    "chatgpt_token_dir": str(tmp_path),
                    "chatgpt_auth_profile": profile_name,
                }
            )

    def test_explicit_relative_auth_file_uses_configured_token_dir(self, tmp_path):
        token_dir = tmp_path / "explicit"

        authenticator = Authenticator(
            {
                "chatgpt_token_dir": str(token_dir),
                "chatgpt_auth_file": "nested/auth.json",
            }
        )

        assert authenticator.token_dir == str(token_dir)
        assert authenticator.auth_file == os.path.join(str(token_dir), "nested", "auth.json")
        assert (token_dir / "nested").exists()

    def test_explicit_absolute_auth_file_isolated_from_token_dir(self, tmp_path):
        token_dir = tmp_path / "token-root"
        auth_file = tmp_path / "separate" / "auth.json"

        authenticator = Authenticator(
            {
                "chatgpt_token_dir": str(token_dir),
                "chatgpt_auth_file": str(auth_file),
            }
        )

        assert authenticator.token_dir == str(token_dir)
        assert authenticator.auth_file == str(auth_file)
        assert auth_file.parent.exists()

    def test_profile_auth_files_do_not_share_tokens(self, tmp_path):
        auth_one = Authenticator(
            {
                "chatgpt_token_dir": str(tmp_path),
                "chatgpt_auth_profile": "one",
            }
        )
        auth_two = Authenticator(
            {
                "chatgpt_token_dir": str(tmp_path),
                "chatgpt_auth_profile": "two",
            }
        )
        auth_one._write_auth_file(
            {
                "access_token": "token-one",
                "expires_at": time.time() + 3600,
            }
        )
        auth_two._write_auth_file(
            {
                "access_token": "token-two",
                "expires_at": time.time() + 3600,
            }
        )

        assert auth_one.get_access_token() == "token-one"
        assert auth_two.get_access_token() == "token-two"
        assert auth_one.auth_file != auth_two.auth_file
