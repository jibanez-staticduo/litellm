from __future__ import annotations

import json
import math
import os
import stat
import sys
import time
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, cast

PROFILES: Final = ("staticduo", "defend1")
MAX_BYTES: Final = 262144
DIR_FLAGS: Final = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class ExpiredAccess(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class Snapshot:
    token: str = field(repr=False)
    expires: float
    scopes: tuple[str, ...]
    account: str
    subscription: str | None

    def credentials(self) -> bytes:
        oauth: Final = {
            "accessToken": self.token,
            "expiresAt": self.expires,
            "scopes": self.scopes,
            **({"subscriptionType": self.subscription} if self.subscription is not None else {}),
        }
        return json.dumps({"claudeAiOauth": oauth}, separators=(",", ":")).encode()

    def settings(self) -> bytes:
        return json.dumps({"oauthAccount": {"accountUuid": self.account}}, separators=(",", ":")).encode()


def mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Invalid native profile")
    return cast(Mapping[str, object], value)


def snapshot(credentials: object, settings: object, now: float) -> Snapshot:
    oauth: Final = mapping(mapping(credentials).get("claudeAiOauth"))
    account: Final = mapping(mapping(settings).get("oauthAccount")).get("accountUuid")
    token: Final = oauth.get("accessToken")
    expires: Final = oauth.get("expiresAt")
    scopes: Final = oauth.get("scopes")
    subscription: Final = oauth.get("subscriptionType")
    if not isinstance(token, str) or not token or not isinstance(account, str) or not account:
        raise ValueError("Invalid native profile")
    if isinstance(expires, bool) or not isinstance(expires, (int, float)) or not math.isfinite(expires):
        raise ValueError("Invalid native expiry")
    if not isinstance(scopes, list) or not all(isinstance(scope, str) for scope in scopes):
        raise ValueError("Invalid native scopes")
    scope_names: Final = tuple(cast(list[str], scopes))
    if "user:inference" not in scope_names:
        raise ValueError("Native profile lacks user:inference")
    if subscription is not None and not isinstance(subscription, str):
        raise ValueError("Invalid native subscription")
    if expires / 1000 <= now + 60:
        raise ExpiredAccess("Access expired or expires soon; run native Claude on Fedora, then sync again")
    return Snapshot(token, expires, scope_names, account, subscription)


@contextmanager
def directory(path: Path, create: bool = False) -> Iterator[int]:
    absolute: Final = Path(os.path.abspath(path))
    with _directory_parts(absolute.parts, create) as fd:
        yield fd


@contextmanager
def _directory_parts(parts: tuple[str, ...], create: bool, parent: int | None = None) -> Iterator[int]:
    name: Final = parts[0] if parts else "/"
    if create and parts:
        try:
            os.mkdir(name, 0o700, dir_fd=parent)
        except FileExistsError:
            pass
    fd: Final = os.open(name, DIR_FLAGS, dir_fd=parent)
    try:
        if len(parts) > 1:
            with _directory_parts(parts[1:], create, fd) as child:
                yield child
        else:
            yield fd
    finally:
        os.close(fd)


def read_json(fd: int, name: str) -> object:
    file_fd: Final = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
    with os.fdopen(file_fd, "rb") as handle:
        if not stat.S_ISREG(os.fstat(handle.fileno()).st_mode):
            raise ValueError("Native profile must be a regular file")
        body: Final = handle.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("Native profile exceeds size limit")
    return cast(object, json.loads(body))


def export_profile(root: Path, profile: str, now: float) -> Snapshot:
    if profile not in PROFILES:
        raise ValueError("Unknown native profile")
    with directory(root / profile) as home_fd:
        settings: Final = read_json(home_fd, ".claude.json")
        credentials: Final = read_json(home_fd, ".credentials.json")
    return snapshot(credentials, settings, now)


def available_profiles(root: Path, now: float) -> Iterator[tuple[str, Snapshot]]:
    for name in PROFILES:
        try:
            value: Final = export_profile(root, name, now)
        except ExpiredAccess:
            sys.stderr.write(f"{name}: access expired or expires soon; run native Claude on Fedora, then sync again\n")
            continue
        yield name, value


def export_snapshots(root: Path, now: float) -> bytes:
    available: Final = tuple(available_profiles(root, now))
    if not available:
        raise ExpiredAccess("No native profile has current access; run native Claude on Fedora, then sync again")
    profiles: Final = {
        name: {"credentials": json.loads(value.credentials()), "settings": json.loads(value.settings())}
        for name, value in available
    }
    body: Final = json.dumps(profiles, separators=(",", ":")).encode()
    if len(body) > MAX_BYTES:
        raise ValueError("Export exceeds size limit")
    return body


def main() -> int:
    if sys.stdout.isatty():
        sys.stderr.write("Export requires a private pipe\n")
        return 1
    try:
        body: Final = export_snapshots(Path.home() / ".claude-homes", time.time())
        sys.stdout.buffer.write(body)
        return 0
    except (OSError, ValueError, TypeError, OverflowError):
        sys.stderr.write("Native access export failed; run native Claude on Fedora, then sync again\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
