import base64
import json
import multiprocessing
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest

from litellm.llms.chatgpt import authenticator as authenticator_module
from litellm.llms.chatgpt.authenticator import Authenticator


def _multiprocess_get_token(token_dir, counter, start_event, result_queue):
    authenticator = Authenticator({"chatgpt_token_dir": token_dir})

    def login():
        with counter.get_lock():
            counter.value += 1
        time.sleep(0.1)
        data = {"access_token": "shared-token", "expires_at": time.time() + 3600}
        authenticator._write_auth_file(data)
        return data

    authenticator._login_device_code = login
    start_event.wait()
    result_queue.put(authenticator.get_access_token())


def _multiprocess_add_account_id(token_dir, start_event):
    authenticator = Authenticator({"chatgpt_token_dir": token_dir})
    start_event.wait()
    authenticator.get_account_id()


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

        with patch.object(authenticator, "_read_auth_file", return_value=json.loads(auth_data)):
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
            patch.object(authenticator, "_read_auth_file", return_value=json.loads(auth_data)),
            patch.object(authenticator, "_refresh_tokens", return_value=refreshed),
        ):
            token = authenticator.get_access_token()
            assert token == "token-new"

    def test_get_account_id_from_id_token(self, authenticator):
        id_token = _make_jwt({"https://api.openai.com/auth": {"chatgpt_account_id": "acct-123"}})
        auth_data = json.dumps({"id_token": id_token})

        with (
            patch.object(authenticator, "_read_auth_file", return_value=json.loads(auth_data)),
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

    def test_device_auth_is_single_flight_per_auth_file(self, tmp_path):
        authenticator = Authenticator({"chatgpt_token_dir": str(tmp_path)})
        calls = 0
        calls_lock = threading.Lock()

        def login():
            nonlocal calls
            with calls_lock:
                calls += 1
            authenticator._write_auth_file({"access_token": "token", "expires_at": time.time() + 3600})
            return {"access_token": "token"}

        with patch.object(authenticator, "_login_device_code", side_effect=login):
            with ThreadPoolExecutor(max_workers=4) as executor:
                tokens = list(executor.map(lambda _: authenticator.get_access_token(), range(4)))

        assert tokens == ["token"] * 4
        assert calls == 1

    def test_auth_write_is_atomic_and_owner_only(self, tmp_path):
        authenticator = Authenticator({"chatgpt_token_dir": str(tmp_path)})
        authenticator._write_auth_file({"access_token": "token"})

        with open(authenticator.auth_file) as auth_file:
            assert json.load(auth_file) == {"access_token": "token"}
        assert os.stat(authenticator.auth_file).st_mode & 0o777 == 0o600
        assert list(tmp_path.glob(".chatgpt-auth-*")) == []

    def test_windows_locking_path_uses_msvcrt(self, tmp_path):
        fake_msvcrt = type("FakeMsvcrt", (), {"LK_LOCK": 1, "locking": Mock()})()
        lock_path = tmp_path / "auth.lock"
        with (
            patch.object(authenticator_module, "fcntl", None),
            patch.object(authenticator_module, "msvcrt", fake_msvcrt),
            open(lock_path, "a+") as lock_file,
        ):
            authenticator_module._lock_auth_file(lock_file)

        fake_msvcrt.locking.assert_called_once()

    def test_auth_write_without_directory_fsync_support(self, tmp_path):
        authenticator = Authenticator({"chatgpt_token_dir": str(tmp_path)})
        with patch.object(authenticator_module.os, "O_DIRECTORY", create=True, new=None):
            authenticator._write_auth_file({"access_token": "portable"})
        with open(authenticator.auth_file) as auth_file:
            assert json.load(auth_file)["access_token"] == "portable"

    def test_windows_write_path_without_fchmod(self, tmp_path):
        authenticator = Authenticator({"chatgpt_token_dir": str(tmp_path)})
        original_fchmod = getattr(authenticator_module.os, "fchmod", None)
        try:
            if original_fchmod is not None:
                delattr(authenticator_module.os, "fchmod")
            with (
                patch.object(authenticator_module.os, "O_DIRECTORY", create=True, new=None),
                patch.object(authenticator_module.os, "chmod", wraps=os.chmod) as chmod,
            ):
                authenticator._write_auth_file({"access_token": "windows-portable"})
        finally:
            if original_fchmod is not None:
                setattr(authenticator_module.os, "fchmod", original_fchmod)

        chmod.assert_called()
        with open(authenticator.auth_file) as auth_file:
            assert json.load(auth_file)["access_token"] == "windows-portable"

    def test_existing_token_directory_mode_is_preserved(self, tmp_path):
        existing = tmp_path / "shared"
        existing.mkdir(mode=0o755)
        os.chmod(existing, 0o755)

        Authenticator({"chatgpt_token_dir": str(existing)})

        assert os.stat(existing).st_mode & 0o777 == 0o755

    def test_new_token_directory_gets_restrictive_mode(self, tmp_path):
        token_dir = tmp_path / "new-private-token-dir"

        Authenticator({"chatgpt_token_dir": str(token_dir)})

        assert token_dir.is_dir()
        assert os.stat(token_dir).st_mode & 0o777 == 0o700

    def test_multiprocess_device_auth_single_flight(self, tmp_path):
        context = multiprocessing.get_context("spawn" if os.name == "nt" else "fork")
        counter = context.Value("i", 0)
        start_event = context.Event()
        result_queue = context.Queue()
        processes = [
            context.Process(
                target=_multiprocess_get_token,
                args=(str(tmp_path), counter, start_event, result_queue),
            )
            for _ in range(4)
        ]
        for process in processes:
            process.start()
        start_event.set()
        for process in processes:
            process.join(10)
            assert process.exitcode == 0

        assert [result_queue.get(timeout=1) for _ in processes] == ["shared-token"] * 4
        assert counter.value == 1

    def test_multiprocess_account_id_merge_preserves_refreshed_token(self, tmp_path):
        context = multiprocessing.get_context("spawn" if os.name == "nt" else "fork")
        authenticator = Authenticator({"chatgpt_token_dir": str(tmp_path)})
        id_token = _make_jwt({"https://api.openai.com/auth": {"chatgpt_account_id": "acct-123"}})
        authenticator._write_auth_file({"access_token": "old", "id_token": id_token})
        start_event = context.Event()
        process = context.Process(target=_multiprocess_add_account_id, args=(str(tmp_path), start_event))
        process.start()
        authenticator._write_auth_file(
            {"access_token": "refreshed", "id_token": id_token, "expires_at": time.time() + 3600}
        )
        start_event.set()
        process.join(10)
        assert process.exitcode == 0

        with open(authenticator.auth_file) as auth_file:
            final_state = json.load(auth_file)
        assert final_state["access_token"] == "refreshed"
        assert final_state["account_id"] == "acct-123"
