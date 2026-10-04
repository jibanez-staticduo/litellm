from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from typing import Final

import export
import sync

NOW: Final = 1000.0


def credentials(token: str = "synthetic-access", expires: float = (NOW + 3600) * 1000) -> dict[str, object]:
    return {
        "claudeAiOauth": {
            "accessToken": token,
            "expiresAt": expires,
            "refreshToken": "synthetic-refresh-never-export",
            "scopes": ["user:inference"],
            "subscriptionType": "synthetic-plan",
            "rateLimitTier": "private-tier",
        }
    }


def settings() -> dict[str, object]:
    return {"oauthAccount": {"accountUuid": "synthetic-account", "emailAddress": "private@example.invalid"}}


def source(root: Path) -> None:
    for name in export.PROFILES:
        profile: Final = root / name
        profile.mkdir(parents=True)
        (profile / ".credentials.json").write_text(json.dumps(credentials()))
        (profile / ".claude.json").write_text(json.dumps(settings()))


class ProfileTests(unittest.TestCase):
    def test_valid_profile_syncs_while_expired_profile_snapshot_stays_unchanged(self) -> None:
        for expired_name in export.PROFILES:
            with self.subTest(expired_name=expired_name), tempfile.TemporaryDirectory() as temporary:
                root: Final = Path(temporary)
                source(root / "source")
                old: Final = export.snapshot(credentials("old-access"), settings(), NOW)
                sync.install(root / "destination", tuple((name, old) for name in export.PROFILES))
                (root / "source" / expired_name / ".credentials.json").write_text(
                    json.dumps(credentials("expired-access", NOW * 1000))
                )
                original: Final = (root / "destination" / expired_name / ".credentials.json").read_bytes()
                warnings: Final = io.StringIO()
                with redirect_stderr(warnings):
                    body: Final = export.export_snapshots(root / "source", NOW)
                profiles: Final = sync.decode(body, NOW)
                self.assertEqual(
                    tuple(name for name, _ in profiles), tuple(name for name in export.PROFILES if name != expired_name)
                )
                sync.install(root / "destination", profiles)
                self.assertEqual((root / "destination" / expired_name / ".credentials.json").read_bytes(), original)
                self.assertIn(expired_name, warnings.getvalue())
                self.assertNotIn("expired-access", warnings.getvalue())
                for name, value in profiles:
                    self.assertEqual(export.export_profile(root / "destination", name, NOW).token, value.token)

    def test_all_expired_profiles_fail_with_no_export(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root: Final = Path(temporary) / ".claude-homes"
            source(root)
            for name in export.PROFILES:
                (root / name / ".credentials.json").write_text(json.dumps(credentials(expires=NOW * 1000)))
            result: Final = subprocess.run(
                (sys.executable, str(Path(export.__file__))),
                env={**os.environ, "HOME": temporary},
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b"")
            self.assertIn(b"native Claude on Fedora", result.stderr)
            self.assertNotIn(b"synthetic-access", result.stderr)

    def test_subset_validation_rejects_empty_unknown_expired_or_malformed_profiles(self) -> None:
        for body in (b"{}", b'{"unknown":{}}'):
            with self.subTest(body=body), self.assertRaises(ValueError):
                sync.decode(body, NOW)
        with tempfile.TemporaryDirectory() as temporary:
            root: Final = Path(temporary)
            source(root)
            (root / "defend1" / ".credentials.json").write_text(
                json.dumps({"claudeAiOauth": {"accessToken": "expired-access", "expiresAt": NOW * 1000, "scopes": []}})
            )
            with self.assertRaises(ValueError) as error:
                export.export_snapshots(root, NOW)
            self.assertNotIsInstance(error.exception, export.ExpiredAccess)
            body: Final = json.dumps(
                {"staticduo": {"credentials": credentials(expires=NOW * 1000), "settings": settings()}}
            ).encode()
            with self.assertRaises(export.ExpiredAccess):
                sync.decode(body, NOW)

    def test_export_whitelist_and_roundtrip_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root: Final = Path(temporary)
            source(root / "source")
            value: Final = export.export_profile(root / "source", "staticduo", NOW)
            body: Final = json.dumps(
                {
                    name: {"credentials": json.loads(value.credentials()), "settings": json.loads(value.settings())}
                    for name in export.PROFILES
                }
            ).encode()
            self.assertNotIn(b"synthetic-refresh", body)
            self.assertNotIn(b"private@example", body)
            self.assertNotIn(b"private-tier", body)
            sync.install(root / "destination", sync.decode(body, NOW))
            newer: Final = export.snapshot(credentials("replacement"), settings(), NOW)
            sync.install(root / "destination", tuple((name, newer) for name in export.PROFILES))
            for name in export.PROFILES:
                profile: Final = root / "destination" / name
                self.assertEqual(export.export_profile(root / "destination", name, NOW).token, "replacement")
                self.assertEqual(profile.stat().st_mode & 0o777, 0o700)
                for filename in (".credentials.json", ".claude.json"):
                    self.assertEqual((profile / filename).stat().st_mode & 0o777, 0o600)

    def test_expiry_boundary_and_scope_rejected(self) -> None:
        for expiry in ((NOW - 1) * 1000, (NOW + 60) * 1000, float("nan"), True):
            with self.subTest(expiry=expiry), self.assertRaises(ValueError):
                export.snapshot(credentials(expires=expiry), settings(), NOW)
        with self.assertRaises(ValueError):
            export.snapshot(
                {"claudeAiOauth": {"accessToken": "secret", "expiresAt": 9e12, "scopes": []}}, settings(), NOW
            )

    def test_source_symlinks_denied(self) -> None:
        for target in ("root", "profile", ".credentials.json", ".claude.json"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root: Final = Path(temporary) / "source"
                source(root)
                path: Final = (
                    root
                    if target == "root"
                    else root / "staticduo"
                    if target == "profile"
                    else root / "staticduo" / target
                )
                moved: Final = path.with_name(path.name + "-real")
                path.rename(moved)
                path.symlink_to(moved)
                with self.assertRaises((OSError, ValueError)):
                    export.export_profile(root, "staticduo", NOW)

    def test_destination_symlinks_denied_without_touching_victim(self) -> None:
        for target in ("root", "profile", ".credentials.json", ".claude.json"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temporary:
                root: Final = Path(temporary) / "destination"
                value: Final = export.snapshot(credentials(), settings(), NOW)
                profiles: Final = tuple((name, value) for name in export.PROFILES)
                sync.install(root, profiles)
                path: Final = (
                    root
                    if target == "root"
                    else root / "staticduo"
                    if target == "profile"
                    else root / "staticduo" / target
                )
                moved: Final = path.with_name(path.name + "-real")
                path.rename(moved)
                path.symlink_to(moved)
                original: Final = moved.read_bytes() if moved.is_file() else None
                with self.assertRaises((OSError, ValueError)):
                    sync.install(root, profiles)
                if original is not None:
                    self.assertEqual(moved.read_bytes(), original)

    def test_oversized_source_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root: Final = Path(temporary)
            source(root)
            (root / "staticduo" / ".credentials.json").write_bytes(b" " * (export.MAX_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "size limit"):
                export.export_profile(root, "staticduo", NOW)

    def test_receive_bounds_failures_and_sanitized_diagnostics(self) -> None:
        with self.assertRaisesRegex(ValueError, "size limit"):
            sync.receive((sys.executable, "-c", f"import sys; sys.stdout.write('x'*{export.MAX_BYTES + 1})"))
        with self.assertRaisesRegex(ValueError, "timed out"):
            sync.receive((sys.executable, "-c", "import time; time.sleep(2)"), timeout=0.05)
        with self.assertRaises(ValueError) as error:
            sync.receive((sys.executable, "-c", "import sys; print('synthetic-secret', file=sys.stderr); sys.exit(1)"))
        self.assertNotIn("synthetic-secret", str(error.exception))

    def test_cli_malformed_source_never_prints_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root: Final = Path(temporary) / ".claude-homes"
            source(root)
            (root / "staticduo" / ".credentials.json").write_text('{"synthetic-secret":')
            result: Final = subprocess.run(
                (sys.executable, str(Path(export.__file__))),
                env={**os.environ, "HOME": temporary},
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, b"")
            self.assertNotIn(b"synthetic-secret", result.stderr)
            self.assertIn(b"native Claude on Fedora", result.stderr)


if __name__ == "__main__":
    unittest.main()
