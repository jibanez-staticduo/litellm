import contextlib
import datetime as dt
import io
import json
import tempfile
import unittest
from pathlib import Path
from typing import Final
from zoneinfo import ZoneInfo

import collector


class UsageTests(unittest.TestCase):
    def test_windows_normalize_resets_and_preserve_nulls(self) -> None:
        raw: Final = json.dumps({
            "five_hour": {"utilization": 0, "resets_at": None},
            "seven_day": {"utilization": 100, "resets_at": "2026-10-05T22:00:00+02:00"},
            "seven_day_sonnet": {"utilization": 23.5, "resets_at": "2026-10-04T12:00:00Z"},
            "seven_day_breakdown": {"rows": [{"display_name": "sensitive", "percent": 100}]},
            "extra_usage": {"is_enabled": False, "monthly_limit": None, "used_credits": None},
            "accessToken": "secret",
        }).encode()
        profile: Final = collector.parse_usage("sample", "pro", raw)
        self.assertEqual(profile.status, "ok")
        self.assertEqual(profile.five_hour, collector.Window(0, None, 18000))
        self.assertEqual(profile.weekly, collector.Window(100, "2026-10-05T20:00:00+00:00", 604800))
        self.assertIsNone(dict(profile.scoped_windows)["seven_day_opus"])
        self.assertEqual(dict(profile.scoped_windows)["seven_day_sonnet"],
                         collector.Window(23.5, "2026-10-04T12:00:00+00:00", 604800))
        self.assertEqual(profile.extra_usage, collector.ExtraUsage(False, None, None, None))
        encoded: Final = json.dumps(collector.profile_json(profile))
        self.assertNotIn("sensitive", encoded)
        self.assertNotIn("secret", encoded)
        self.assertIn("2026-10-05 22:00 CEST", collector.render(profile, ZoneInfo("Europe/Brussels")))

    def test_missing_window_is_not_free_quota(self) -> None:
        profile: Final = collector.parse_usage("sample", None, b'{"five_hour":{"utilization":0,"resets_at":null}}')
        self.assertEqual(profile.status, "ok")
        self.assertIsNone(profile.weekly)
        missing: Final = collector.parse_usage("sample", None, b"{}")
        self.assertEqual(missing.error, collector.Error("usage_missing"))
        self.assertIsNone(missing.weekly)

    def test_invalid_quota_and_reset_fail_closed(self) -> None:
        for value in (True, -1, 101, "5", float("nan"), float("inf"), 10**1000, None):
            with self.subTest(value=value):
                self.assertEqual(collector.parse_usage("sample", None, json.dumps({
                    "seven_day": {"utilization": value, "resets_at": None},
                }).encode()).error, collector.Error("usage_malformed"))
        for reset in ("2026-10-04T12:00:00", "private text", 123):
            with self.subTest(reset=reset):
                self.assertEqual(collector.parse_usage("sample", None, json.dumps({
                    "seven_day": {"utilization": 50, "resets_at": reset},
                }).encode()).error, collector.Error("usage_malformed"))

    def test_cli_json_parser_and_credential_transport(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root: Final = Path(directory)
            home: Final = root / "sample"
            home.mkdir()
            (home / ".credentials.json").write_text(json.dumps({"claudeAiOauth": {
                "accessToken": "private-test-token", "subscriptionType": "pro",
                "expiresAt": (dt.datetime.now(dt.timezone.utc).timestamp() + 3600) * 1000,
                "email": "private@example.invalid", "refreshToken": "private-refresh",
            }}))

            def transport(token: str) -> tuple[int, bytes]:
                self.assertEqual(token, "private-test-token")
                return 200, b'{"seven_day":{"utilization":75,"resets_at":null}}'

            output: Final = io.StringIO()
            with contextlib.redirect_stdout(output):
                result: Final = collector.main(("--json", "--profiles-dir", directory, "--profile", "sample"), transport)
            self.assertEqual(result, 0)
            payload: Final = collector.decode(output.getvalue().encode())
            assert payload is not None
            self.assertEqual(payload["schema_version"], 1)
            profiles: Final = payload["profiles"]
            assert isinstance(profiles, list) and isinstance(profiles[0], dict)
            weekly: Final = profiles[0]["weekly"]
            assert isinstance(weekly, dict)
            self.assertEqual(weekly["used_percent"], 75)
            self.assertIsNone(profiles[0]["five_hour"])
            self.assertNotIn("private", output.getvalue())

    def test_rejected_auth_and_transport_errors_do_not_leak_bodies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home: Final = Path(directory)
            (home / ".credentials.json").write_text('{"claudeAiOauth":{"accessToken":"token"}}')
            for status, code in ((401, "auth_rejected"), (403, "auth_rejected"), (429, "rate_limited"),
                                 (302, "service_error"), (503, "service_error")):
                with self.subTest(status=status):
                    def transport(token: str) -> tuple[int, bytes]:
                        return status, b"private provider error body"

                    self.assertEqual(collector.fetch("sample", home, transport).error, collector.Error(code, status))
                    self.assertIsNone(collector.fetch("sample", home, transport).weekly)
                    self.assertNotIn("private", json.dumps(collector.profile_json(collector.fetch("sample", home, transport))))

            def failure(token: str) -> tuple[int, bytes]:
                raise OSError("private endpoint or credential")

            self.assertEqual(collector.fetch("sample", home, failure).error, collector.Error("network_error"))

    def test_expired_credentials_do_not_call_transport_or_write(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home: Final = Path(directory)
            path: Final = home / ".credentials.json"
            content: Final = '{"claudeAiOauth":{"accessToken":"token","expiresAt":1}}'
            path.write_text(content)

            def transport(token: str) -> tuple[int, bytes]:
                self.fail("expired token must not be sent")

            profile: Final = collector.fetch("sample", home, transport)
            self.assertEqual(profile.error, collector.Error("auth_expired"))
            self.assertIn("claude_sample auth login --claudeai", collector.render(profile, ZoneInfo("UTC")))
            self.assertEqual(path.read_text(), content)

    def test_unbounded_or_non_object_payload_is_rejected(self) -> None:
        for payload in (b"[]", b"invalid", b" " * (collector.MAX_BODY + 1)):
            with self.subTest(size=len(payload)):
                self.assertEqual(collector.parse_usage("sample", None, payload).error, collector.Error("usage_malformed"))


if __name__ == "__main__":
    unittest.main()
