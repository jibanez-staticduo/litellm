from __future__ import annotations

import hashlib
import os
import signal
import stat
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

import pytest

from .disposable_runner import (
    AtomicSecretDirectory,
    CANDIDATE_IMAGE_ID,
    DOCKER_DAEMON_ID,
    DOCKER_DAEMON_NAME,
    DOCKER_ENDPOINT,
    OWNER,
    POSTGRES_CONFIG,
    POSTGRES_REF,
    POSTGRES_VERSION,
    REDIS_CONFIG,
    REDIS_REF,
    REDIS_VERSION,
    TASK_ID,
    DisposableRunner,
    DockerRepositoryIdentity,
    OsSecretFileOperations,
    SecretDescriptorSettlementError,
)
from .candidate_secret_wrapper import run as run_candidate_wrapper
from .dcr_maintenance_client import ExactCandidate, MaintenanceSession


@dataclass(frozen=True, slots=True)
class Result:
    returncode: int = 0
    stdout: str = ""


@dataclass(slots=True)
class FakeDocker:
    daemon_name: str = DOCKER_DAEMON_NAME
    daemon_id: str = DOCKER_DAEMON_ID
    context: str = "default"
    endpoint: str = DOCKER_ENDPOINT
    collision: tuple[str, str] | None = None
    ownership_drift: tuple[str, str] | None = None
    production_drift: bool = False
    commands: list[tuple[str, ...]] = field(default_factory=list)
    resources: dict[tuple[str, str], tuple[str, tuple[str, str, str]]] = field(default_factory=dict)
    lifecycle_hook: Callable[[], None] | None = None
    production_rows: tuple[str, ...] = ("litellm",)
    bind_mounts: str = (
        "bind:/volume2/docker/litellm/config.yaml:/app/config.yaml:false;"
        "volume:/volume2/@docker/volumes/data/_data:/data:true;"
    )
    hang_on: str | None = None
    retain_deleted: tuple[str, str] | None = None
    missing_image: str | None = None
    fail_create_kind: str | None = None
    timeouts: list[float] = field(default_factory=list)
    environments: list[dict[str, str]] = field(default_factory=list)
    inspect_fault: Literal["timeout", "failure", "wrong_name", "wrong_id", "wrong_labels"] | None = None
    inspect_fault_target: tuple[str, str] | None = None
    inspect_fault_remaining: int = 0
    repo_digest_spelling: dict[str, str] = field(default_factory=dict)

    def __call__(
        self,
        arguments: Sequence[str],
        _environment: Mapping[str, str],
        timeout_seconds: float,
    ) -> Result:
        command: Final = tuple(arguments)
        self.commands.append(command)
        self.timeouts.append(timeout_seconds)
        self.environments.append(dict(_environment))
        if self.hang_on is not None and self.hang_on in " ".join(command):
            raise subprocess.TimeoutExpired(command, timeout_seconds)
        if command == ("docker", "context", "show"):
            return Result(stdout=f"{self.context}\n")
        if command[:4] == ("docker", "context", "inspect", "default"):
            return Result(stdout=f"{self.endpoint}\n")
        if command[:3] != ("docker", "--host", DOCKER_ENDPOINT):
            return Result(returncode=1)
        args: Final = command[3:]
        if args[:2] == ("info", "--format"):
            return Result(stdout=f"{self.daemon_name}|{self.daemon_id}\n")
        if args and args[0] == "pull":
            return Result(returncode=1 if self.missing_image == args[-1] else 0)
        if args[:2] == ("image", "inspect"):
            reference: Final = args[-1]
            if reference == POSTGRES_REF:
                repository_digest = self.repo_digest_spelling.get(reference, reference)
                return Result(
                    stdout=f'{POSTGRES_CONFIG}|linux|amd64|["{repository_digest}"]|["PG_VERSION={POSTGRES_VERSION}"]\n'
                )
            if reference == REDIS_REF:
                repository_digest = self.repo_digest_spelling.get(reference, reference)
                return Result(
                    stdout=f'{REDIS_CONFIG}|linux|amd64|["{repository_digest}"]|["REDIS_VERSION={REDIS_VERSION}"]\n'
                )
            return Result(returncode=1)
        if args and args[0] == "ps" and "label=com.docker.compose.service=litellm" in args:
            return Result(stdout="\n".join(self.production_rows) + ("\n" if self.production_rows else ""))
        if len(args) >= 3 and args[1] == "inspect":
            return self._inspect(args)
        if len(args) >= 2 and args[0] in ("network", "volume") and args[1] == "create":
            return self._create(args[0], args[-1], args)
        if args and args[0] == "create":
            name: Final = str(args[args.index("--name") + 1])
            return self._create("container", name, args)
        if args and args[0] == "start":
            return Result()
        if args and args[0] == "exec":
            if "sha256sum" in args:
                config: Final = Path(__file__).with_name("disposable_candidate_config.yaml")
                return Result(stdout=f"{hashlib.sha256(config.read_bytes()).hexdigest()}  {args[-1]}\n")
            return Result(stdout="PONG\n" if "redis-cli" in args else "ready\n")
        if args and args[0] == "port":
            return Result(stdout="127.0.0.1:49152\n")
        if len(args) >= 2 and (args[:2] == ("rm", "--force") or (args[0] in ("network", "volume") and args[1] == "rm")):
            kind: Final = "container" if args[0] == "rm" else args[0]
            if self.retain_deleted != (kind, args[-1]):
                self.resources.pop((kind, args[-1]), None)
            return Result()
        if args and args[0] in ("ps", "network", "volume") and "--filter" in args:
            return Result(stdout=self._matching_ids(args))
        return Result(returncode=1)

    def _create(self, kind: str, name: str, args: tuple[str, ...]) -> Result:
        if self.fail_create_kind == kind:
            return Result(returncode=1)
        label_values: Final = tuple(
            args[index + 1].split("=", 1)[1] for index, value in enumerate(args) if value == "--label"
        )
        if len(label_values) != 3:
            return Result(returncode=1)
        labels: Final = (label_values[0], label_values[1], label_values[2])
        object_id: Final = f"id-{name}"
        self.resources[(kind, name)] = (object_id, labels)
        return Result(stdout=f"{object_id}\n")

    def _inspect(self, args: tuple[str, ...]) -> Result:
        kind: Final = args[0]
        name = args[-1]
        template: Final = args[-2] if "--format" in args else ""
        if kind == "container" and name == "litellm":
            values: Final = {
                "{{.Id}}": "prod-id",
                "{{.Image}}": "prod-image-drift" if self.production_drift else "prod-image",
                "{{.State.Running}}": "true",
                '{{index .Config.Labels "com.docker.compose.config-hash"}}': "prod-config",
                "{{range .Mounts}}{{.Type}}:{{.Source}}:{{.Destination}}:{{.RW}};{{end}}": self.bind_mounts,
                "{{range $name,$network := .NetworkSettings.Networks}}{{$name}}:{{$network.NetworkID}};{{end}}": "prod:net-id;",
                "{{json .NetworkSettings.Ports}}": '{"4000/tcp":[{"HostIp":"127.0.0.1","HostPort":"4000"}]}',
                "{{.RestartCount}}": "0",
            }
            return Result(stdout=f"{values[template]}\n")
        if self.collision == (kind, name) and (kind, name) not in self.resources:
            return Result(stdout="collision\n")
        resource = self.resources.get((kind, name))
        if resource is None:
            named: Final = next(
                (
                    (resource_name, value)
                    for (resource_kind, resource_name), value in self.resources.items()
                    if resource_kind == kind and value[0] == name
                ),
                None,
            )
            if named is not None:
                name, resource = named
        if resource is None:
            return Result(returncode=1)
        object_id, labels = resource
        if self.ownership_drift == (kind, name):
            labels = (TASK_ID, OWNER, "wrong-run")
        if "staticeng.task" in template:
            shown_name = f"/{name}" if kind == "container" else name
            if self.inspect_fault_target == (kind, name) and self.inspect_fault_remaining > 0:
                self.inspect_fault_remaining -= 1
                match self.inspect_fault:
                    case "timeout":
                        raise subprocess.TimeoutExpired(args, 1)
                    case "failure":
                        return Result(returncode=1)
                    case "wrong_name":
                        shown_name = "wrong-name"
                    case "wrong_id":
                        object_id = "wrong-id"
                    case "wrong_labels":
                        labels = (TASK_ID, OWNER, "wrong-run")
                    case None:
                        pass
            return Result(stdout=f"{shown_name}|{object_id}|{'|'.join(labels)}\n")
        if template == "{{.Internal}}":
            return Result(stdout="true\n")
        if "NetworkSettings.Networks" in template:
            network: Final = next(value for resource_kind, value in self.resources if resource_kind == "network")
            return Result(stdout=f"{network};\n")
        if template == "{{json .HostConfig.PortBindings}}":
            return Result(stdout='{"4000/tcp":[{"HostIp":"127.0.0.1"}]}\n' if name.endswith("candidate") else "null\n")
        if template == "{{.State.Running}}":
            return Result(stdout="true\n")
        if template == "{{.Image}}":
            return Result(stdout=f"{CANDIDATE_IMAGE_ID}\n")
        if template in ("{{.Id}}", "{{.Name}}"):
            return Result(stdout=f"{object_id}\n")
        return Result(returncode=1)

    def _matching_ids(self, args: tuple[str, ...]) -> str:
        expected: Final = {
            value.removeprefix("label=").split("=", 1)[1]
            for index, value in enumerate(args)
            if args[index - 1] == "--filter"
        }
        ids: Final = [object_id for object_id, labels in self.resources.values() if expected.issubset(labels)]
        return "\n".join(ids)


def _runner(
    fake: FakeDocker,
    *,
    lifecycle: Callable[..., Mapping[str, bool | int | str | tuple[int, ...]]] | None = None,
) -> DisposableRunner:
    def successful_lifecycle(*_args: object) -> Mapping[str, bool | int | str | tuple[int, ...]]:
        if fake.lifecycle_hook is not None:
            fake.lifecycle_hook()
        return {"cleanup_complete": True, "email_login": True}

    return DisposableRunner(
        repo_root=Path(__file__).resolve().parents[3],
        executor=fake,
        readiness=lambda _url: True,
        lifecycle=lifecycle or successful_lifecycle,
    )


class TestDisposableRunner:
    @pytest.mark.parametrize(
        "reference,expected",
        (
            ("docker.io/library/redis@sha256:" + "a" * 64, "docker.io/library/redis"),
            ("library/redis@sha256:" + "a" * 64, "docker.io/library/redis"),
            ("redis@sha256:" + "a" * 64, "docker.io/library/redis"),
            ("index.docker.io/redis@sha256:" + "a" * 64, "docker.io/library/redis"),
            ("registry-1.docker.io/library/redis@sha256:" + "a" * 64, "docker.io/library/redis"),
        ),
    )
    def test_docker_hub_repository_digest_spellings_are_canonical(self, reference: str, expected: str) -> None:
        identity: Final = DockerRepositoryIdentity.parse(reference)

        assert identity.repository == expected
        assert identity.digest == "sha256:" + "a" * 64

    @pytest.mark.parametrize(
        "reference,observed",
        (
            (POSTGRES_REF, "library/postgres@" + POSTGRES_REF.rsplit("@", 1)[1]),
            (POSTGRES_REF, "postgres@" + POSTGRES_REF.rsplit("@", 1)[1]),
            (REDIS_REF, "library/redis@" + REDIS_REF.rsplit("@", 1)[1]),
            (REDIS_REF, "redis@" + REDIS_REF.rsplit("@", 1)[1]),
        ),
    )
    def test_dependency_preflight_accepts_equivalent_docker_hub_spellings(self, reference: str, observed: str) -> None:
        fake: Final = FakeDocker(repo_digest_spelling={reference: observed})

        assert _runner(fake).run()["zero_resources"] is True

    @pytest.mark.parametrize(
        "reference,observed",
        (
            (REDIS_REF, "evil.example/library/redis@" + REDIS_REF.rsplit("@", 1)[1]),
            (REDIS_REF, "docker.io/other/redis@" + REDIS_REF.rsplit("@", 1)[1]),
            (REDIS_REF, "redis@sha256:" + "0" * 64),
            (REDIS_REF, "redisx@" + REDIS_REF.rsplit("@", 1)[1]),
            (POSTGRES_REF, "postgres@sha256:" + "0" * 64),
            (POSTGRES_REF, "postgresql@" + POSTGRES_REF.rsplit("@", 1)[1]),
        ),
    )
    def test_dependency_preflight_rejects_registry_repository_digest_and_near_matches(
        self, reference: str, observed: str
    ) -> None:
        fake: Final = FakeDocker(repo_digest_spelling={reference: observed})

        with pytest.raises(RuntimeError, match="dependency identity mismatch"):
            _runner(fake).run()

        assert fake.resources == {}

    def test_atomic_secret_mkdir_failure_restores_umask_and_leaves_no_path(self) -> None:
        @dataclass(frozen=True, slots=True)
        class Operations(OsSecretFileOperations):
            def mkdir(self, path: Path, mode: int) -> None:
                raise OSError("mkdir failure")

        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            previous: Final = os.umask(0o022)
            try:
                with pytest.raises(OSError, match="mkdir failure"):
                    AtomicSecretDirectory(Operations()).create(Path(parent), "secrets", {"one": "value"})
                observed: Final = os.umask(0o022)
                assert observed == 0o022
                assert not (Path(parent) / "secrets").exists()
            finally:
                os.umask(previous)

    def test_atomic_secret_open_failure_removes_directory_and_restores_umask(self) -> None:
        @dataclass(frozen=True, slots=True)
        class Operations(OsSecretFileOperations):
            def open(self, path: Path, flags: int, mode: int) -> int:
                raise OSError("open failure")

        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            previous: Final = os.umask(0o002)
            try:
                with pytest.raises(OSError, match="open failure"):
                    AtomicSecretDirectory(Operations()).create(Path(parent), "secrets", {"one": "value"})
                observed: Final = os.umask(0o002)
                assert observed == 0o002
                assert not (Path(parent) / "secrets").exists()
            finally:
                os.umask(previous)

    def test_atomic_secret_close_failure_after_successful_prior_file_removes_all_paths(self) -> None:
        @dataclass(frozen=True, slots=True)
        class Operations(OsSecretFileOperations):
            descriptors: set[int] = field(default_factory=set)
            opens: int = 0
            close_calls: list[int] = field(default_factory=list)

            def open(self, path: Path, flags: int, mode: int) -> int:
                descriptor: Final = os.open(path, flags, mode)
                self.descriptors.add(descriptor)
                object.__setattr__(self, "opens", self.opens + 1)
                return descriptor

            def close(self, descriptor: int) -> None:
                self.close_calls.append(descriptor)
                if self.opens == 2 and len(self.close_calls) == 2:
                    raise OSError("second-file close failure")
                os.close(descriptor)
                self.descriptors.discard(descriptor)

            def is_open(self, descriptor: int) -> bool:
                return descriptor in self.descriptors

        operations: Final = Operations()
        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            directory: Final = Path(parent) / "secrets"
            with pytest.raises(OSError, match="second-file close failure"):
                AtomicSecretDirectory(operations).create(Path(parent), "secrets", {"one": "first", "two": "second"})
            assert operations.descriptors == set()
            assert not directory.exists()

    @pytest.mark.parametrize("failure", ("fsync", "close_before", "close_after"))
    def test_atomic_secret_fsync_and_close_failures_settle_descriptor_and_paths(self, failure: str) -> None:
        @dataclass(frozen=True, slots=True)
        class Operations(OsSecretFileOperations):
            descriptors: set[int] = field(default_factory=set)
            close_calls: list[int] = field(default_factory=list)

            def open(self, path: Path, flags: int, mode: int) -> int:
                descriptor: Final = os.open(path, flags, mode)
                self.descriptors.add(descriptor)
                return descriptor

            def fsync(self, descriptor: int) -> None:
                if failure == "fsync":
                    raise OSError("fsync failure")
                os.fsync(descriptor)

            def close(self, descriptor: int) -> None:
                self.close_calls.append(descriptor)
                if failure == "close_before" and len(self.close_calls) == 1:
                    raise OSError("close-before failure")
                os.close(descriptor)
                self.descriptors.discard(descriptor)
                if failure == "close_after" and len(self.close_calls) == 1:
                    raise OSError("close-after failure")

            def is_open(self, descriptor: int) -> bool:
                return descriptor in self.descriptors

        operations: Final = Operations()
        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            directory: Final = Path(parent) / "secrets"
            previous: Final = os.umask(0o012)
            try:
                with pytest.raises(OSError, match="fsync failure|close-before failure|close-after failure"):
                    AtomicSecretDirectory(operations).create(Path(parent), "secrets", {"one": "value"})
                assert not directory.exists()
                observed: Final = os.umask(0o012)
                assert observed == 0o012
            finally:
                os.umask(previous)
            assert operations.descriptors == set()
            assert len(operations.close_calls) >= 1

    def test_atomic_secret_repeated_close_failure_tracks_unresolved_fd_and_fails_closed(self) -> None:
        @dataclass(frozen=True, slots=True)
        class Operations(OsSecretFileOperations):
            descriptor: list[int] = field(default_factory=list)

            def open(self, path: Path, flags: int, mode: int) -> int:
                opened: Final = os.open(path, flags, mode)
                self.descriptor.append(opened)
                return opened

            def close(self, descriptor: int) -> None:
                raise OSError("persistent close failure")

            def is_open(self, descriptor: int) -> bool:
                return True

        operations: Final = Operations()
        writer: Final = AtomicSecretDirectory(operations)
        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            previous: Final = os.umask(0o027)
            try:
                with pytest.raises(SecretDescriptorSettlementError, match="remain unresolved"):
                    writer.create(Path(parent), "secrets", {"one": "value"})
                observed: Final = os.umask(0o027)
                assert observed == 0o027
                assert writer.unresolved_descriptors == set(operations.descriptor)
                assert not (Path(parent) / "secrets").exists()
                with pytest.raises(SecretDescriptorSettlementError, match="blocks creation"):
                    writer.create(Path(parent), "other", {"two": "value"})
            finally:
                for descriptor in operations.descriptor:
                    os.close(descriptor)
                os.umask(previous)

    def test_atomic_secret_creation_ignores_hostile_umask_and_is_owner_only(self) -> None:
        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            old: Final = os.umask(0)
            try:
                directory: Final = AtomicSecretDirectory().create(
                    Path(parent), "secrets", {"master_key": "secret-value"}
                )
            finally:
                os.umask(old)

            assert stat.S_IMODE(directory.stat().st_mode) == 0o700
            assert stat.S_IMODE((directory / "master_key").stat().st_mode) == 0o400
            assert (directory / "master_key").read_text() == "secret-value"

    def test_atomic_secret_mid_write_failure_closes_and_removes_every_partial(self) -> None:
        @dataclass(frozen=True, slots=True)
        class FailingOperations(OsSecretFileOperations):
            descriptors: list[int] = field(default_factory=list)
            writes: list[int] = field(default_factory=list)

            def open(self, path: Path, flags: int, mode: int) -> int:
                descriptor: Final = os.open(path, flags, mode)
                self.descriptors.append(descriptor)
                return descriptor

            def write(self, descriptor: int, data: bytes) -> int:
                self.writes.append(descriptor)
                if len(self.writes) == 2:
                    raise OSError("injected mid-write failure")
                return min(2, os.write(descriptor, data[:2]))

            def close(self, descriptor: int) -> None:
                os.close(descriptor)
                if descriptor in self.descriptors:
                    self.descriptors.remove(descriptor)

        operations: Final = FailingOperations()
        with tempfile.TemporaryDirectory(dir="/dev/shm") as parent:
            directory: Final = Path(parent) / "secrets"
            with pytest.raises(OSError, match="mid-write"):
                AtomicSecretDirectory(operations).create(Path(parent), "secrets", {"one": "abcdef", "two": "ghijkl"})
            assert not directory.exists()
            assert operations.descriptors == []

    def test_candidate_wrapper_reads_exact_files_builds_internal_env_and_execs_without_output(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        @dataclass(slots=True)
        class Runtime:
            environ: dict[str, str] = field(default_factory=lambda: {"TASK018_POSTGRES_HOST": "task-postgres"})
            reads: list[Path] = field(default_factory=list)
            execution: tuple[str, tuple[str, ...]] | None = None

            def getenv(self, name: str) -> str:
                return self.environ[name]

            def setenv(self, name: str, value: str) -> None:
                self.environ[name] = value

            def read_text(self, path: Path) -> str:
                self.reads.append(path)
                return {
                    "postgres_password": "postgres-secret",
                    "master_key": "master-secret",
                    "salt_key": "salt-secret",
                }[path.name]

            def execvp(self, file: str, args: tuple[str, ...]) -> None:
                self.execution = (file, args)

        runtime: Final = Runtime()
        run_candidate_wrapper(runtime)

        assert runtime.reads == [
            Path("/run/task018-secrets/postgres_password"),
            Path("/run/task018-secrets/master_key"),
            Path("/run/task018-secrets/salt_key"),
        ]
        assert runtime.environ["DATABASE_URL"] == "postgresql://litellm:postgres-secret@task-postgres:5432/litellm"
        assert runtime.environ["LITELLM_MASTER_KEY"] == "master-secret"
        assert runtime.environ["LITELLM_SALT_KEY"] == "salt-secret"
        assert runtime.execution == (
            "litellm",
            ("litellm", "--config", "/app/disposable_candidate_config.yaml", "--port", "4000"),
        )
        captured: Final = capsys.readouterr()
        assert captured.out == captured.err == ""

    def test_run_uses_exact_daemon_internal_network_labels_and_zero_cleanup(self) -> None:
        fake: Final = FakeDocker()
        runner: Final = _runner(fake)

        evidence: Final = runner.run()

        assert evidence["daemon_identity_verified"] is True
        assert evidence["production_invariant_preserved"] is True
        assert evidence["zero_resources"] is True
        assert len(runner.names.run_id) == 32
        assert any("--internal" in command for command in fake.commands)
        pulls: Final = [command for command in fake.commands if "pull" in command]
        assert [command[-1] for command in pulls] == [POSTGRES_REF, REDIS_REF]
        assert all("--platform" in command and "linux/amd64" in command for command in pulls)
        creates: Final = [command for command in fake.commands if command[3:4] == ("create",)]
        assert creates and all("--pull" in command and "never" in command for command in creates)
        first_create: Final = min(fake.commands.index(command) for command in fake.commands if "create" in command)
        last_image_inspect: Final = max(
            fake.commands.index(command) for command in fake.commands if command[3:5] == ("image", "inspect")
        )
        assert last_image_inspect < first_create
        assert all(
            command[:3] == ("docker", "--host", DOCKER_ENDPOINT)
            for command in fake.commands
            if "context" not in command
        )
        assert fake.resources == {}
        assert not any("prune" in command for command in fake.commands)
        assert not any(command[3:5] in (("image", "rm"), ("tag",)) for command in fake.commands)
        assert fake.timeouts and all(0 < timeout <= runner.docker_timeout_seconds for timeout in fake.timeouts)
        forbidden: Final = {"POSTGRES_PASSWORD", "DATABASE_URL", "LITELLM_MASTER_KEY", "LITELLM_SALT_KEY"}
        assert all(not forbidden.intersection(environment) for environment in fake.environments)
        flattened: Final = " ".join(argument for command in fake.commands for argument in command)
        assert runner.secrets_destroyed
        assert "postgresql://" not in flattened
        assert not any(path.startswith("/tmp") for path in flattened.split())

    def test_production_mount_projection_supports_bind_and_named_volume(self) -> None:
        fake: Final = FakeDocker()
        runner: Final = _runner(fake)

        assert runner.run()["production_invariant_preserved"] is True

        assert any(any(".Source" in argument for argument in command) for command in fake.commands)
        assert not any(any(".Name}}:{{.Destination" in argument for argument in command) for command in fake.commands)

    @pytest.mark.parametrize("rows", ((), ("one", "two")))
    def test_production_discovery_rejects_zero_or_multiple_without_fallback(self, rows: tuple[str, ...]) -> None:
        fake: Final = FakeDocker(production_rows=rows)
        runner: Final = _runner(fake)

        with pytest.raises(RuntimeError, match="exactly one Compose-labelled"):
            runner.run()

        assert not any("container inspect" in " ".join(command) and "litellm" in command for command in fake.commands)
        assert fake.resources == {}

    @pytest.mark.parametrize("field", ("context", "endpoint", "name", "id"))
    def test_run_rejects_ambient_daemon_identity_drift_before_creation(self, field: str) -> None:
        fake: Final = FakeDocker()
        if field == "context":
            fake.context = "other"
        elif field == "endpoint":
            fake.endpoint = "tcp://other"
        elif field == "name":
            fake.daemon_name = "other"
        else:
            fake.daemon_id = "other"
        runner: Final = _runner(fake)

        with pytest.raises(RuntimeError, match="daemon identity mismatch"):
            runner.run()

        assert fake.resources == {}
        assert not any("create" in command for command in fake.commands)

    def test_collision_preflight_does_not_adopt_or_delete_object(self) -> None:
        fake: Final = FakeDocker()
        runner: Final = _runner(fake)
        fake.collision = ("volume", runner.names.volume)

        with pytest.raises(RuntimeError, match="name collision"):
            runner.run()

        assert not any(command[-1] == runner.names.volume and "rm" in command for command in fake.commands)

    def test_cleanup_refuses_unowned_object_and_does_not_delete_it(self) -> None:
        fake: Final = FakeDocker()
        runner: Final = _runner(fake)

        def drift() -> None:
            fake.ownership_drift = ("container", runner.names.redis)

        fake.lifecycle_hook = drift
        with pytest.raises(RuntimeError, match="cleanup action"):
            runner.run()

        assert ("container", runner.names.redis) in fake.resources
        assert not any(
            command[-1] == runner.names.redis and command[3:5] == ("rm", "--force") for command in fake.commands
        )

    def test_retained_created_object_id_is_detected_after_delete(self) -> None:
        fake: Final = FakeDocker()
        runner: Final = _runner(fake)
        fake.retain_deleted = ("container", runner.names.redis)

        with pytest.raises(RuntimeError, match="resources remain"):
            runner.run()

        retained_id: Final = f"id-{runner.names.redis}"
        assert any(command[-1] == retained_id and "inspect" in command for command in fake.commands)

    def test_hung_docker_subprocess_is_hard_timed_out_and_cleanup_runs(self) -> None:
        fake: Final = FakeDocker(hang_on="network create")
        runner: Final = _runner(fake)

        with pytest.raises(TimeoutError, match="Docker command deadline"):
            runner.run()

        assert fake.resources == {}
        assert fake.timeouts and max(fake.timeouts) <= runner.docker_timeout_seconds

    @pytest.mark.parametrize("reference", (POSTGRES_REF, REDIS_REF))
    def test_missing_exact_dependency_image_stops_before_resources(self, reference: str) -> None:
        fake: Final = FakeDocker(missing_image=reference)
        runner: Final = _runner(fake)

        with pytest.raises(RuntimeError, match="dependency pull failed"):
            runner.run()

        assert fake.resources == {}
        assert not any("create" in command for command in fake.commands)

    @pytest.mark.parametrize("fault", ("timeout", "failure"))
    def test_create_success_inspect_transient_fault_recovers_and_cleans(
        self, fault: Literal["timeout", "failure"]
    ) -> None:
        fake: Final = FakeDocker(inspect_fault=fault, inspect_fault_remaining=1)
        runner: Final = _runner(fake)
        fake.inspect_fault_target = ("network", runner.names.network)

        if fault == "timeout":
            with pytest.raises(InterruptedError):
                runner.run()
        else:
            assert runner.run()["zero_resources"] is True
        assert fake.resources == {}

    @pytest.mark.parametrize("fault", ("wrong_name", "wrong_id", "wrong_labels"))
    def test_create_success_wrong_identity_is_preserved_and_escalated(
        self, fault: Literal["wrong_name", "wrong_id", "wrong_labels"]
    ) -> None:
        fake: Final = FakeDocker(inspect_fault=fault, inspect_fault_remaining=3)
        runner: Final = _runner(fake)
        fake.inspect_fault_target = ("network", runner.names.network)

        with pytest.raises(RuntimeError, match="bounded cleanup"):
            runner.run()

        assert ("network", runner.names.network) in fake.resources
        assert not any(
            command[-1] == runner.names.network and command[3:5] == ("network", "rm") for command in fake.commands
        )

    @pytest.mark.parametrize("kind", ("volume", "container"))
    def test_partial_create_failure_automatically_reverse_cleans_and_proves_absence(self, kind: str) -> None:
        fake: Final = FakeDocker(fail_create_kind=kind)
        runner: Final = _runner(fake)

        with pytest.raises(RuntimeError, match="Docker create failed"):
            runner.run()

        assert fake.resources == {}
        for resource in runner.created_resources:
            assert any(command[-1] == resource.object_id and "inspect" in command for command in fake.commands)

    def test_signal_during_real_run_reaches_active_lifecycle_and_cleans(self) -> None:
        fake: Final = FakeDocker()
        observed: list[bool] = []
        runner: DisposableRunner

        def lifecycle(
            _factory: Callable[[], MaintenanceSession],
            _candidate: ExactCandidate,
            _deadline: float,
            cancelled: Callable[[], bool],
        ) -> Mapping[str, bool | int | str | tuple[int, ...]]:
            runner.signal_for_test(signal.SIGTERM)
            observed.append(cancelled())
            raise InterruptedError("signal")

        runner = _runner(fake, lifecycle=lifecycle)

        with pytest.raises(InterruptedError):
            runner.run()

        assert observed == [True]
        assert fake.resources == {}

    def test_deadline_cancellation_reaches_active_lifecycle_and_cleans(self) -> None:
        fake: Final = FakeDocker()

        def lifecycle(
            _factory: Callable[[], MaintenanceSession],
            _candidate: ExactCandidate,
            _deadline: float,
            cancelled: Callable[[], bool],
        ) -> Mapping[str, bool | int | str | tuple[int, ...]]:
            assert not cancelled()
            raise TimeoutError("deadline")

        runner: Final = _runner(fake, lifecycle=lifecycle)
        with pytest.raises(TimeoutError):
            runner.run()
        assert fake.resources == {}

    def test_independent_deadline_timer_sets_shared_lifecycle_cancellation(self) -> None:
        fake: Final = FakeDocker()
        observed: list[bool] = []

        @dataclass(slots=True)
        class ImmediateTimer:
            _seconds: float
            callback: Callable[[], None]
            daemon: bool = False

            def start(self) -> None:
                self.callback()

            def cancel(self) -> None:
                pass

        def lifecycle(
            _factory: Callable[[], MaintenanceSession],
            _candidate: ExactCandidate,
            _deadline: float,
            cancelled: Callable[[], bool],
        ) -> Mapping[str, bool | int | str | tuple[int, ...]]:
            observed.append(cancelled())
            raise TimeoutError("deadline")

        runner: Final = _runner(fake, lifecycle=lifecycle)
        runner.timer_factory = ImmediateTimer

        with pytest.raises(TimeoutError):
            runner.run()

        assert observed == [True]
        assert fake.resources == {}

    def test_production_invariant_drift_rejects_after_cleanup(self) -> None:
        fake: Final = FakeDocker()

        def drift() -> None:
            fake.production_drift = True

        fake.lifecycle_hook = drift
        runner: Final = _runner(fake)

        with pytest.raises(RuntimeError, match="production LiteLLM invariant drifted"):
            runner.run()

        assert fake.resources == {}
