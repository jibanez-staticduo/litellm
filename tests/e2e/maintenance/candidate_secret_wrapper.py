from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Protocol


class CandidateRuntime(Protocol):
    def getenv(self, name: str) -> str: ...

    def setenv(self, name: str, value: str) -> None: ...

    def read_text(self, path: Path) -> str: ...

    def execvp(self, file: str, args: tuple[str, ...]) -> None: ...


class OsCandidateRuntime:
    def getenv(self, name: str) -> str:
        return os.environ[name]

    def setenv(self, name: str, value: str) -> None:
        os.environ[name] = value

    def read_text(self, path: Path) -> str:
        return path.read_text()

    def execvp(self, file: str, args: tuple[str, ...]) -> None:
        os.execvp(file, args)


def _secret(runtime: CandidateRuntime, name: str) -> str:
    value: Final = runtime.read_text(Path(f"/run/task018-secrets/{name}")).strip()
    if not value:
        raise RuntimeError("disposable secret file is empty")
    return value


def run(runtime: CandidateRuntime) -> None:
    postgres_password: Final = _secret(runtime, "postgres_password")
    runtime.setenv(
        "DATABASE_URL",
        f"postgresql://litellm:{postgres_password}@{runtime.getenv('TASK018_POSTGRES_HOST')}:5432/litellm",
    )
    runtime.setenv("LITELLM_MASTER_KEY", _secret(runtime, "master_key"))
    runtime.setenv("LITELLM_SALT_KEY", _secret(runtime, "salt_key"))
    runtime.execvp(
        "litellm",
        (
            "litellm",
            "--config",
            "/app/disposable_candidate_config.yaml",
            "--port",
            "4000",
        ),
    )


def main() -> None:
    run(OsCandidateRuntime())


if __name__ == "__main__":
    main()
