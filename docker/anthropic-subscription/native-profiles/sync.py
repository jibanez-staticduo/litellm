from __future__ import annotations

import io
import json
import os
import select
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Final, cast

from export import MAX_BYTES, PROFILES, Snapshot, directory, mapping, snapshot

DESTINATION: Final = Path("/volume2/docker/litellm/anthropic-native-client")
COMMAND: Final = (
    "ssh",
    "-T",
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=10",
    "fedora",
    "python3",
    "/home/staticduo/.local/share/claude-native-profiles/export.py",
)


def receive(command: tuple[str, ...] = COMMAND, timeout: float = 30) -> bytes:
    deadline: Final = time.monotonic() + timeout
    with subprocess.Popen(
        command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    ) as process:
        try:
            if process.stdout is None:
                raise ValueError("Missing export pipe")
            with io.BytesIO() as output:
                while True:
                    remaining: Final = deadline - time.monotonic()
                    if remaining <= 0 or not select.select((process.stdout,), (), (), remaining)[0]:
                        raise ValueError("Native access export timed out")
                    chunk: Final = os.read(process.stdout.fileno(), min(8192, MAX_BYTES + 1 - output.tell()))
                    if not chunk:
                        break
                    output.write(chunk)
                    if output.tell() > MAX_BYTES:
                        raise ValueError("Native access export exceeds size limit")
                if process.wait(timeout=max(0.01, deadline - time.monotonic())) != 0:
                    raise ValueError("Native access export failed; run native Claude on Fedora, then sync again")
                return output.getvalue()
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


def decode(body: bytes, now: float) -> tuple[tuple[str, Snapshot], ...]:
    if len(body) > MAX_BYTES:
        raise ValueError("Native access export exceeds size limit")
    profiles: Final = mapping(cast(object, json.loads(body)))
    if not profiles or not set(profiles).issubset(PROFILES):
        raise ValueError("Unexpected native profiles")
    return tuple(
        (name, snapshot(mapping(profiles[name]).get("credentials"), mapping(profiles[name]).get("settings"), now))
        for name in PROFILES
        if name in profiles
    )


def check_target(fd: int, name: str) -> None:
    try:
        info: Final = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError("Unsafe native snapshot target")


def replace_file(fd: int, name: str, body: bytes) -> None:
    check_target(fd, name)
    temporary: Final = ".snapshot-" + uuid.uuid4().hex
    file_fd: Final = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
    try:
        with os.fdopen(file_fd, "wb") as handle:
            os.fchmod(handle.fileno(), 0o600)
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        check_target(fd, name)
        os.replace(temporary, name, src_dir_fd=fd, dst_dir_fd=fd)
        os.fsync(fd)
    finally:
        try:
            os.unlink(temporary, dir_fd=fd)
        except FileNotFoundError:
            pass


def install(root: Path, profiles: tuple[tuple[str, Snapshot], ...]) -> None:
    with directory(root, create=True) as root_fd:
        os.fchmod(root_fd, 0o700)
        for name, value in profiles:
            if name not in PROFILES:
                raise ValueError("Unexpected native profile")
            with directory(root / name, create=True) as fd:
                os.fchmod(fd, 0o700)
                check_target(fd, ".credentials.json")
                check_target(fd, ".claude.json")
                replace_file(fd, ".claude.json", value.settings())
                replace_file(fd, ".credentials.json", value.credentials())


def main() -> int:
    try:
        profiles: Final = decode(receive(), time.time())
        install(DESTINATION, profiles)
        for name, value in profiles:
            sys.stdout.write(f"{name}: access snapshot synced; expiresAt={value.expires}\n")
        return 0
    except (OSError, ValueError, TypeError, OverflowError, subprocess.SubprocessError):
        sys.stderr.write("Native access sync failed; run native Claude on Fedora, then sync again\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
