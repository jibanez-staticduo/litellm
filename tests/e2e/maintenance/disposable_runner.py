from __future__ import annotations

import errno
import hashlib
import json
import os
import secrets
import signal
import subprocess
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from threading import Event, Timer
from types import FrameType
from typing import Final, Protocol, TypeAlias

import httpx
from pydantic import TypeAdapter

from .dcr_maintenance_client import (
    DEFEND_SERVER_ID,
    DEFEND_TOOL_NAME,
    DcrMaintenanceClient,
    DisposableCandidateInspector,
    ExactCandidate,
    SessionFactory,
    ToolsetTool,
    exact_candidate_from_disposable,
)


CANDIDATE_REF: Final = (
    "docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3"
)
CANDIDATE_IMAGE_ID: Final = "sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915"
POSTGRES_REF: Final = (
    "docker.io/library/postgres@sha256:075f7ba66bc9b3ce7d6b8b635208ff61cd7cf1a67d71ec530eec5d7ae0cbe571"
)
POSTGRES_CONFIG: Final = "sha256:75f5a96988cdf694a215073c3e9c001b706b371e2f94df3967f2efdec2787f6b"
POSTGRES_VERSION: Final = "16.15"
REDIS_REF: Final = "docker.io/library/redis@sha256:1db42ccef14898aa29bae778452d567534b59c107129cbc1163fb552de184d3c"
REDIS_CONFIG: Final = "sha256:5509c0097c6064aa8a3b1df58f1d950e67090fffa6678ae8f3f1dc2385f12deb"
REDIS_VERSION: Final = "7.4.11"
PLATFORM: Final = "linux/amd64"
DOCKER_CONTEXT: Final = "default"
DOCKER_ENDPOINT: Final = "unix:///var/run/docker.sock"
DOCKER_DAEMON_NAME: Final = "nas"
DOCKER_DAEMON_ID: Final = "8d5cc9c3-ebfb-43e7-b6ff-bb2112a49b4f"
TASK_ID: Final = "TASK-2026-09-03-018-fix-dcr-maintenance-client"
OWNER: Final = "disposable-dcr-validation"
PRODUCTION_CONTAINER: Final = "litellm"
STRING_TUPLE_ADAPTER: Final = TypeAdapter(tuple[str, ...])


@dataclass(frozen=True, slots=True)
class DockerRepositoryIdentity:
    repository: str
    digest: str

    @classmethod
    def parse(cls, reference: str) -> DockerRepositoryIdentity:
        repository, separator, digest = reference.rpartition("@")
        if separator != "@" or not repository or not digest.startswith("sha256:"):
            raise ValueError("Docker repository digest reference is invalid")
        digest_value: Final = digest.removeprefix("sha256:")
        if len(digest_value) != 64 or any(character not in "0123456789abcdef" for character in digest_value):
            raise ValueError("Docker repository digest is not canonical sha256")
        return cls(repository=cls._canonical_repository(repository), digest=digest)

    @staticmethod
    def _canonical_repository(repository: str) -> str:
        parts: Final = repository.split("/")
        first: Final = parts[0]
        has_registry: Final = "." in first or ":" in first or first == "localhost"
        if has_registry and first not in ("docker.io", "index.docker.io", "registry-1.docker.io"):
            return repository
        path_parts = parts[1:] if has_registry else parts
        if len(path_parts) == 1:
            path_parts = ["library", path_parts[0]]
        return f"docker.io/{'/'.join(path_parts)}"


class ProcessResult(Protocol):
    @property
    def returncode(self) -> int: ...

    @property
    def stdout(self) -> str: ...


CommandExecutor = Callable[[Sequence[str], Mapping[str, str], float], ProcessResult]
SignalHandler: TypeAlias = int | signal.Handlers | Callable[[int, FrameType | None], None] | None
ReadinessProbe = Callable[[str], bool]
LifecycleRunner = Callable[
    [SessionFactory, ExactCandidate, float, Callable[[], bool]],
    Mapping[str, bool | int | str | tuple[int, ...]],
]


class DeadlineTimer(Protocol):
    daemon: bool

    def start(self) -> None: ...

    def cancel(self) -> None: ...


TimerFactory = Callable[[float, Callable[[], None]], DeadlineTimer]


class SecretFileOperations(Protocol):
    def mkdir(self, path: Path, mode: int) -> None: ...

    def open(self, path: Path, flags: int, mode: int) -> int: ...

    def write(self, descriptor: int, data: bytes) -> int: ...

    def fsync(self, descriptor: int) -> None: ...

    def close(self, descriptor: int) -> None: ...

    def is_open(self, descriptor: int) -> bool: ...

    def unlink(self, path: Path) -> None: ...

    def rmdir(self, path: Path) -> None: ...


@dataclass(frozen=True, slots=True)
class OsSecretFileOperations:
    def mkdir(self, path: Path, mode: int) -> None:
        os.mkdir(path, mode)

    def open(self, path: Path, flags: int, mode: int) -> int:
        return os.open(path, flags, mode)

    def write(self, descriptor: int, data: bytes) -> int:
        return os.write(descriptor, data)

    def fsync(self, descriptor: int) -> None:
        os.fsync(descriptor)

    def close(self, descriptor: int) -> None:
        os.close(descriptor)

    def is_open(self, descriptor: int) -> bool:
        try:
            os.fstat(descriptor)
        except OSError as exc:
            if exc.errno == errno.EBADF:
                return False
            raise
        return True

    def unlink(self, path: Path) -> None:
        path.unlink(missing_ok=True)

    def rmdir(self, path: Path) -> None:
        path.rmdir()


class SecretDescriptorSettlementError(OSError):
    pass


@dataclass(slots=True)
class AtomicSecretDirectory:
    operations: SecretFileOperations = OsSecretFileOperations()
    close_attempts: int = 2
    unresolved_descriptors: set[int] = field(default_factory=set, init=False)

    def create(self, base: Path, name: str, values: Mapping[str, str]) -> Path:
        if self.unresolved_descriptors:
            raise SecretDescriptorSettlementError("unresolved secret descriptor ownership blocks creation")
        directory: Final = base / name
        created_paths: list[Path] = []
        open_descriptors: set[int] = set()
        previous_umask: Final = os.umask(0o077)
        try:
            self.operations.mkdir(directory, 0o700)
            for filename, value in values.items():
                path = directory / filename
                descriptor = self.operations.open(
                    path,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_CLOEXEC,
                    0o400,
                )
                created_paths.append(path)
                open_descriptors.add(descriptor)
                operation_error: Exception | None = None
                try:
                    data = value.encode("utf-8")
                    offset = 0
                    while offset < len(data):
                        written = self.operations.write(descriptor, data[offset:])
                        if written <= 0:
                            raise OSError("secret file write made no progress")
                        offset += written
                    self.operations.fsync(descriptor)
                except Exception as exc:
                    operation_error = exc
                settled, close_error = self._settle_descriptor(descriptor)
                if settled:
                    open_descriptors.remove(descriptor)
                else:
                    self.unresolved_descriptors.add(descriptor)
                    raise SecretDescriptorSettlementError(
                        "secret descriptor could not be proven closed"
                    ) from operation_error
                if operation_error is not None:
                    raise operation_error
                if close_error is not None:
                    raise close_error
            return directory
        except Exception:
            for descriptor in tuple(open_descriptors):
                settled, _close_error = self._settle_descriptor(descriptor)
                if not settled:
                    self.unresolved_descriptors.add(descriptor)
            for path in reversed(created_paths):
                self.operations.unlink(path)
            try:
                self.operations.rmdir(directory)
            except FileNotFoundError:
                pass
            if self.unresolved_descriptors:
                raise SecretDescriptorSettlementError(
                    f"{len(self.unresolved_descriptors)} secret descriptor(s) remain unresolved"
                )
            raise
        finally:
            os.umask(previous_umask)

    def _settle_descriptor(self, descriptor: int) -> tuple[bool, Exception | None]:
        first_error: Exception | None = None
        for _attempt in range(self.close_attempts):
            try:
                self.operations.close(descriptor)
            except Exception as exc:
                if first_error is None:
                    first_error = exc
                if not self.operations.is_open(descriptor):
                    self.unresolved_descriptors.discard(descriptor)
                    return True, first_error
                continue
            if not self.operations.is_open(descriptor):
                self.unresolved_descriptors.discard(descriptor)
                return True, first_error
        return False, first_error


def execute_command(arguments: Sequence[str], environment: Mapping[str, str], timeout_seconds: float) -> ProcessResult:
    return subprocess.run(
        arguments,
        check=False,
        capture_output=True,
        text=True,
        env=environment,
        timeout=timeout_seconds,
    )


def readiness_probe(url: str) -> bool:
    try:
        return httpx.get(url, timeout=2).status_code == 200
    except httpx.HTTPError:
        return False


def run_lifecycle(
    session_factory: SessionFactory,
    candidate: ExactCandidate,
    deadline_seconds: float,
    cancelled: Callable[[], bool],
) -> Mapping[str, bool | int | str | tuple[int, ...]]:
    return (
        DcrMaintenanceClient(
            session_factory=session_factory,
            candidate=candidate,
            cancelled=cancelled,
        )
        .validate(deadline_seconds=deadline_seconds)
        .evidence()
    )


@dataclass(frozen=True, slots=True)
class DisposableNames:
    run_id: str
    prefix: str
    network: str
    volume: str
    postgres: str
    redis: str
    upstream: str
    candidate: str

    @classmethod
    def create(cls) -> DisposableNames:
        run_id: Final = secrets.token_hex(16)
        prefix: Final = f"task018-{run_id}"
        return cls(
            run_id=run_id,
            prefix=prefix,
            network=f"{prefix}-network",
            volume=f"{prefix}-postgres",
            postgres=f"{prefix}-postgres",
            redis=f"{prefix}-redis",
            upstream=f"{prefix}-mcp",
            candidate=f"{prefix}-candidate",
        )


@dataclass(frozen=True, slots=True)
class OwnedResource:
    kind: str
    name: str
    object_id: str


@dataclass(frozen=True, slots=True)
class ProductionInvariant:
    container_id: str
    image_id: str
    running: str
    config_digest: str
    mounts: str
    networks: str
    ports: str
    restart_count: str


@dataclass(slots=True)
class DisposableRunner:
    repo_root: Path
    executor: CommandExecutor = execute_command
    readiness: ReadinessProbe = readiness_probe
    lifecycle: LifecycleRunner = run_lifecycle
    timer_factory: TimerFactory = Timer
    secret_writer: AtomicSecretDirectory = field(default_factory=AtomicSecretDirectory)
    deadline_seconds: float = 300.0
    docker_timeout_seconds: float = 10.0
    names: DisposableNames = field(default_factory=DisposableNames.create)
    _environment: dict[str, str] = field(default_factory=dict)
    _owned: list[OwnedResource] = field(default_factory=list)
    _created: list[OwnedResource] = field(default_factory=list)
    _cancelled: Event = field(default_factory=Event)
    _cleanup_started: bool = False
    _lifecycle_deadline: float | None = None
    _cleanup_deadline: float | None = None
    _secret_dir: Path | None = None
    _master_key: str | None = None

    @property
    def labels(self) -> tuple[str, str, str]:
        return (
            f"staticeng.task={TASK_ID}",
            f"staticeng.owner={OWNER}",
            f"staticeng.run={self.names.run_id}",
        )

    def run(self) -> Mapping[str, bool | int | str | tuple[int, ...]]:
        deadline: Final = time.monotonic() + self.deadline_seconds
        self._lifecycle_deadline = deadline
        previous: Final = self._install_signal_handlers()
        production_before: ProductionInvariant | None = None
        primary_error: Exception | None = None
        cleanup_error: Exception | None = None
        evidence: Mapping[str, bool | int | str | tuple[int, ...]] | None = None
        try:
            self._prepare_environment()
            self._verify_daemon()
            production_before = self._production_invariant()
            self._preflight_collisions()
            self._prepare_dependency_images()
            self._create_topology()
            self._start_topology(deadline)
            self._inspect_topology()
            port: Final = self._candidate_port()
            base_url: Final = f"http://127.0.0.1:{port}"
            config: Final = self.repo_root / "tests/e2e/maintenance/disposable_candidate_config.yaml"
            inspector: Final = DisposableCandidateInspector(
                container_name=self.names.candidate,
                config_path=config,
                container_config_path="/app/disposable_candidate_config.yaml",
                expected_image_id=CANDIDATE_IMAGE_ID,
                expected_config_sha256=self._sha256(config),
                command_runner=lambda arguments: self._execute_docker(arguments[1:]),
            )
            session_factory, candidate = exact_candidate_from_disposable(
                base_url=base_url,
                master_key=self._required_master_key(),
                inspector=inspector,
                toolset_name="defend_memory",
                toolset_description="Temporary TASK-2026-09-03-018 disposable validation",
                tool=ToolsetTool(server_id=DEFEND_SERVER_ID, tool_name=DEFEND_TOOL_NAME),
                cross_audience_paths=("/lazymcp", "/lazymcp/other-scope", "/mcp"),
            )
            remaining: Final = max(0.001, deadline - time.monotonic())
            deadline_timer: Final = self.timer_factory(remaining, self._cancelled.set)
            deadline_timer.daemon = True
            deadline_timer.start()
            try:
                evidence = self.lifecycle(
                    session_factory,
                    candidate,
                    remaining,
                    self._cancelled.is_set,
                )
            finally:
                deadline_timer.cancel()
        except Exception as exc:
            primary_error = exc
            self._cancelled.set()
        finally:
            try:
                self.cleanup(deadline=time.monotonic() + 30.0)
                self._assert_zero_resources()
                if production_before is not None and self._production_invariant() != production_before:
                    raise RuntimeError("NAS production LiteLLM invariant drifted")
            except Exception as exc:
                cleanup_error = exc
            finally:
                self._environment.clear()
                self._master_key = None
                self._destroy_secret_dir()
                self._restore_signal_handlers(previous)
        if cleanup_error is not None:
            if primary_error is not None:
                raise RuntimeError("disposable run and bounded cleanup both failed") from primary_error
            raise cleanup_error
        if primary_error is not None:
            raise primary_error
        if evidence is None:
            raise RuntimeError("disposable run completed without status evidence")
        return {
            **evidence,
            "daemon_identity_verified": True,
            "production_invariant_preserved": True,
            "zero_resources": True,
        }

    def cleanup(self, *, deadline: float | None = None) -> None:
        self._cleanup_started = True
        cleanup_deadline: Final = deadline or time.monotonic() + 30.0
        self._cleanup_deadline = cleanup_deadline
        failures: list[str] = []
        unresolved: list[OwnedResource] = []
        for resource in reversed(self._owned):
            if time.monotonic() >= cleanup_deadline:
                failures.append("deadline")
                break
            try:
                if not self._ownership_matches(resource):
                    failures.append(resource.kind)
                    unresolved.append(resource)
                    continue
                command = (
                    ("rm", "--force", resource.name)
                    if resource.kind == "container"
                    else (resource.kind, "rm", resource.name)
                )
                if self._execute_docker(command).returncode != 0:
                    failures.append(resource.kind)
                    unresolved.append(resource)
                    continue
                if self._resource_exists(resource.kind, resource.name) or self._resource_exists(
                    resource.kind, resource.object_id
                ):
                    failures.append(resource.kind)
                    unresolved.append(resource)
            except Exception:
                failures.append(resource.kind)
                unresolved.append(resource)
        self._owned = list(reversed(unresolved))
        if failures:
            raise RuntimeError(f"{len(failures)} ownership-checked cleanup action(s) failed")

    def _prepare_environment(self) -> None:
        if os.environ.get("DOCKER_HOST") or os.environ.get("DOCKER_CONTEXT"):
            raise RuntimeError("ambient Docker target selection is prohibited")
        self._environment = {"PATH": os.environ.get("PATH", "/usr/bin:/bin")}
        self._create_secret_dir()

    def _create_secret_dir(self) -> None:
        base: Final = Path("/dev/shm")
        values: Final = {
            "postgres_password": secrets.token_urlsafe(32),
            "master_key": f"sk-{secrets.token_urlsafe(48)}",
            "salt_key": secrets.token_urlsafe(48),
        }
        self._secret_dir = self.secret_writer.create(base, f"{self.names.prefix}-secrets", values)
        self._master_key = values["master_key"]

    def _destroy_secret_dir(self) -> None:
        if self._secret_dir is None:
            return
        for path in self._secret_dir.iterdir():
            path.unlink(missing_ok=True)
        self._secret_dir.rmdir()
        self._secret_dir = None

    def _required_master_key(self) -> str:
        if self._master_key is None:
            raise RuntimeError("disposable master key is unavailable")
        return self._master_key

    def _verify_daemon(self) -> None:
        context: Final = self._execute(("docker", "context", "show"))
        endpoint: Final = self._execute(
            ("docker", "context", "inspect", DOCKER_CONTEXT, "--format", "{{.Endpoints.docker.Host}}")
        )
        daemon: Final = self._execute_docker(("info", "--format", "{{.Name}}|{{.ID}}"))
        if (
            context.returncode != 0
            or context.stdout.strip() != DOCKER_CONTEXT
            or endpoint.returncode != 0
            or endpoint.stdout.strip() != DOCKER_ENDPOINT
            or daemon.returncode != 0
            or daemon.stdout.strip() != f"{DOCKER_DAEMON_NAME}|{DOCKER_DAEMON_ID}"
        ):
            raise RuntimeError("authorized Docker daemon identity mismatch")

    def _production_invariant(self) -> ProductionInvariant:
        fields: Final = (
            "{{.Id}}",
            "{{.Image}}",
            "{{.State.Running}}",
            '{{index .Config.Labels "com.docker.compose.config-hash"}}',
            "{{range .Mounts}}{{.Type}}:{{.Source}}:{{.Destination}}:{{.RW}};{{end}}",
            "{{range $name,$network := .NetworkSettings.Networks}}{{$name}}:{{$network.NetworkID}};{{end}}",
            "{{json .NetworkSettings.Ports}}",
            "{{.RestartCount}}",
        )
        candidates: Final = self._execute_docker(
            (
                "ps",
                "--filter",
                "label=com.docker.compose.service=litellm",
                "--format",
                "{{.Names}}",
            )
        )
        names: Final = tuple(value for value in candidates.stdout.splitlines() if value)
        if len(names) != 1:
            raise RuntimeError("expected exactly one Compose-labelled production LiteLLM container")
        name: Final = names[0]
        values: Final = tuple(self._inspect("container", name, field) for field in fields)
        return ProductionInvariant(*values)

    def _preflight_collisions(self) -> None:
        self._check_cancelled()
        for kind, name in self._intended_resources():
            result = self._execute_docker((kind, "inspect", name))
            if result.returncode == 0:
                raise RuntimeError("disposable resource name collision")
        self._assert_zero_resources()

    def _prepare_dependency_images(self) -> None:
        self._pull_and_verify_image(
            reference=POSTGRES_REF,
            config_id=POSTGRES_CONFIG,
            version_variable="PG_VERSION",
            version=POSTGRES_VERSION,
        )
        self._pull_and_verify_image(
            reference=REDIS_REF,
            config_id=REDIS_CONFIG,
            version_variable="REDIS_VERSION",
            version=REDIS_VERSION,
        )

    def _pull_and_verify_image(
        self,
        *,
        reference: str,
        config_id: str,
        version_variable: str,
        version: str,
    ) -> None:
        pull: Final = self._execute_docker(("pull", "--platform", PLATFORM, reference))
        if pull.returncode != 0:
            raise RuntimeError("exact disposable dependency pull failed")
        inspect: Final = self._execute_docker(
            (
                "image",
                "inspect",
                "--format",
                "{{.Id}}|{{.Os}}|{{.Architecture}}|{{json .RepoDigests}}|{{json .Config.Env}}",
                reference,
            )
        )
        if inspect.returncode != 0:
            raise RuntimeError("exact disposable dependency inspection failed")
        parts: Final = inspect.stdout.strip().split("|", 4)
        if len(parts) != 5:
            raise RuntimeError("exact disposable dependency identity shape mismatch")
        image_id, os_name, architecture, repo_digests_json, environment_json = parts
        try:
            repo_digests: Final = STRING_TUPLE_ADAPTER.validate_json(repo_digests_json)
            image_environment: Final = STRING_TUPLE_ADAPTER.validate_json(environment_json)
        except ValueError as exc:
            raise RuntimeError("exact disposable dependency metadata is invalid") from exc
        expected_repository: Final = DockerRepositoryIdentity.parse(reference)
        try:
            observed_repositories: Final = tuple(DockerRepositoryIdentity.parse(item) for item in repo_digests)
        except ValueError as exc:
            raise RuntimeError("exact disposable dependency repository digest is invalid") from exc
        if (
            image_id != config_id
            or os_name != "linux"
            or architecture != "amd64"
            or expected_repository not in observed_repositories
            or f"{version_variable}={version}" not in image_environment
        ):
            raise RuntimeError("exact disposable dependency identity mismatch")

    def _create_topology(self) -> None:
        if self._secret_dir is None:
            raise RuntimeError("disposable secret directory is unavailable")
        self._create_resource("network", self.names.network, ("network", "create", "--internal", *self._label_args()))
        self._create_resource("volume", self.names.volume, ("volume", "create", *self._label_args()))
        self._create_container(
            self.names.postgres,
            POSTGRES_REF,
            (
                "--network",
                self.names.network,
                "--mount",
                f"type=bind,src={self._secret_dir / 'postgres_password'},dst=/run/secrets/postgres_password,readonly",
                "--env",
                "POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password",
                "--env",
                "POSTGRES_USER=litellm",
                "--env",
                "POSTGRES_DB=litellm",
                "--mount",
                f"type=volume,src={self.names.volume},dst=/var/lib/postgresql/data",
            ),
        )
        self._create_container(self.names.redis, REDIS_REF, ("--network", self.names.network))
        upstream_script: Final = self.repo_root / "tests/e2e/maintenance/synthetic_mcp_server.py"
        self._create_container(
            self.names.upstream,
            CANDIDATE_REF,
            (
                "--network",
                self.names.network,
                "--network-alias",
                "defend-upstream",
                "--entrypoint",
                "python",
                "--mount",
                f"type=bind,src={upstream_script},dst=/app/synthetic_mcp_server.py,readonly",
            ),
            ("/app/synthetic_mcp_server.py",),
        )
        config: Final = self.repo_root / "tests/e2e/maintenance/disposable_candidate_config.yaml"
        wrapper: Final = self.repo_root / "tests/e2e/maintenance/candidate_secret_wrapper.py"
        self._create_container(
            self.names.candidate,
            CANDIDATE_REF,
            (
                "--network",
                self.names.network,
                "--publish",
                "127.0.0.1::4000",
                "--env",
                f"TASK018_POSTGRES_HOST={self.names.postgres}",
                "--env",
                f"REDIS_HOST={self.names.redis}",
                "--env",
                "REDIS_PORT=6379",
                "--entrypoint",
                "python",
                "--mount",
                f"type=bind,src={config},dst=/app/disposable_candidate_config.yaml,readonly",
                "--mount",
                f"type=bind,src={wrapper},dst=/app/candidate_secret_wrapper.py,readonly",
                "--mount",
                f"type=bind,src={self._secret_dir},dst=/run/task018-secrets,readonly",
            ),
            ("/app/candidate_secret_wrapper.py",),
        )

    def _create_container(
        self,
        name: str,
        image: str,
        options: tuple[str, ...],
        command: tuple[str, ...] = (),
    ) -> None:
        self._create_resource(
            "container",
            name,
            (
                "create",
                "--pull",
                "never",
                "--platform",
                PLATFORM,
                "--name",
                name,
                *self._label_args(),
                *options,
                image,
                *command,
            ),
        )

    def _create_resource(self, kind: str, name: str, command_prefix: tuple[str, ...]) -> None:
        self._check_cancelled()
        command: Final = (*command_prefix, name) if kind in ("network", "volume") else command_prefix
        result: Final = self._execute_docker(command)
        if result.returncode != 0:
            raise RuntimeError("disposable Docker create failed")
        created_id: Final = result.stdout.strip()
        if not created_id:
            raise RuntimeError("disposable Docker create returned no object identity")
        resource: Final = OwnedResource(kind=kind, name=name, object_id=created_id)
        self._created.append(resource)
        try:
            owned = self._ownership_matches(resource)
        except (RuntimeError, TimeoutError):
            owned = False
        if not owned:
            if self._recover_provisional(resource):
                return
            raise RuntimeError("created resource ownership could not be proven")
        self._owned.append(resource)

    def _recover_provisional(self, resource: OwnedResource) -> bool:
        for _attempt in range(2):
            try:
                if self._ownership_matches(resource):
                    self._owned.append(resource)
                    return True
            except (RuntimeError, TimeoutError):
                continue
        return False

    def _start_topology(self, deadline: float) -> None:
        for resource in self._owned:
            if resource.kind == "container":
                self._require_success(("start", resource.name))
        self._wait(("exec", self.names.postgres, "pg_isready", "-U", "litellm"), deadline)
        self._wait(("exec", self.names.redis, "redis-cli", "ping"), deadline, expected="PONG")
        port: Final = self._candidate_port()
        while time.monotonic() < deadline:
            self._check_cancelled()
            if self.readiness(f"http://127.0.0.1:{port}/health/liveliness"):
                return
            time.sleep(0.1)
        self._cancelled.set()
        raise TimeoutError("disposable candidate readiness deadline exceeded")

    def _inspect_topology(self) -> None:
        self._check_cancelled()
        if self._inspect("network", self.names.network, "{{.Internal}}") != "true":
            raise RuntimeError("disposable network is not internal")
        for resource in self._owned:
            if resource.kind != "container":
                continue
            networks = self._inspect(
                "container", resource.name, "{{range $name,$network := .NetworkSettings.Networks}}{{$name}};{{end}}"
            )
            ports = self._inspect("container", resource.name, "{{json .HostConfig.PortBindings}}")
            if networks != f"{self.names.network};":
                raise RuntimeError("disposable container has unexpected network attachment")
            if resource.name != self.names.candidate and ports not in ("null", "{}"):
                raise RuntimeError("disposable dependency published a host port")
        _ = self._candidate_port()

    def _wait(self, command: tuple[str, ...], deadline: float, expected: str | None = None) -> None:
        while time.monotonic() < deadline:
            self._check_cancelled()
            result = self._execute_docker(command)
            if result.returncode == 0 and (expected is None or result.stdout.strip() == expected):
                return
            time.sleep(0.1)
        self._cancelled.set()
        raise TimeoutError("disposable dependency readiness deadline exceeded")

    def _candidate_port(self) -> int:
        result: Final = self._require_success(("port", self.names.candidate, "4000/tcp"))
        endpoint: Final = result.stdout.strip()
        if not endpoint.startswith("127.0.0.1:") or endpoint.count("\n"):
            raise RuntimeError("candidate port is not bound exclusively to IPv4 loopback")
        return int(endpoint.rsplit(":", 1)[1])

    def _ownership_matches(self, resource: OwnedResource) -> bool:
        template: Final = (
            '{{.Name}}|{{.Id}}|{{index .Labels "staticeng.task"}}|{{index .Labels "staticeng.owner"}}|{{index .Labels "staticeng.run"}}'
            if resource.kind != "container"
            else '{{.Name}}|{{.Id}}|{{index .Config.Labels "staticeng.task"}}|{{index .Config.Labels "staticeng.owner"}}|{{index .Config.Labels "staticeng.run"}}'
        )
        result: Final = self._execute_docker((resource.kind, "inspect", "--format", template, resource.name))
        expected_name: Final = f"/{resource.name}" if resource.kind == "container" else resource.name
        return result.returncode == 0 and result.stdout.strip() == (
            f"{expected_name}|{resource.object_id}|{TASK_ID}|{OWNER}|{self.names.run_id}"
        )

    def _assert_zero_resources(self) -> None:
        if any(
            self._resource_exists(resource.kind, resource.name)
            or self._resource_exists(resource.kind, resource.object_id)
            for resource in self._created
        ):
            raise RuntimeError("a retained current-run object ID remains")
        filters: Final = tuple(value for label in self.labels for value in ("--filter", f"label={label}"))
        queries: Final = (
            ("ps", "--all", "--quiet", *filters),
            ("network", "ls", "--quiet", *filters),
            ("volume", "ls", "--quiet", *filters),
        )
        if any(self._require_success(query).stdout.strip() for query in queries):
            raise RuntimeError("current-run disposable resources remain")

    def _inspect(self, kind: str, name: str, template: str) -> str:
        result: Final = self._execute_docker((kind, "inspect", "--format", template, name))
        if result.returncode != 0:
            raise RuntimeError("Docker inspection failed")
        return result.stdout.strip()

    def _resource_exists(self, kind: str, identity: str) -> bool:
        return self._execute_docker((kind, "inspect", identity)).returncode == 0

    def _require_success(self, command: tuple[str, ...]) -> ProcessResult:
        self._check_cancelled()
        result: Final = self._execute_docker(command)
        if result.returncode != 0:
            raise RuntimeError("disposable Docker operation failed")
        return result

    def _execute_docker(self, command: Sequence[str]) -> ProcessResult:
        return self._execute(("docker", "--host", DOCKER_ENDPOINT, *command))

    def _execute(self, command: Sequence[str]) -> ProcessResult:
        now: Final = time.monotonic()
        active_deadline: Final = self._cleanup_deadline if self._cleanup_started else self._lifecycle_deadline
        remainder: Final = self.docker_timeout_seconds if active_deadline is None else active_deadline - now
        if remainder <= 0:
            if not self._cleanup_started:
                self._cancelled.set()
            raise TimeoutError("Docker command deadline exceeded")
        try:
            return self.executor(command, self._command_environment(), min(self.docker_timeout_seconds, remainder))
        except subprocess.TimeoutExpired as exc:
            if not self._cleanup_started:
                self._cancelled.set()
            raise TimeoutError("Docker command deadline exceeded") from exc

    def _command_environment(self) -> Mapping[str, str]:
        forbidden: Final = {
            "POSTGRES_PASSWORD",
            "DATABASE_URL",
            "LITELLM_MASTER_KEY",
            "LITELLM_SALT_KEY",
        }
        if forbidden.intersection(self._environment):
            raise RuntimeError("credential material entered Docker subprocess environment")
        return self._environment

    def _check_cancelled(self) -> None:
        if self._cancelled.is_set() and not self._cleanup_started:
            raise InterruptedError("disposable maintenance run cancelled")

    def _label_args(self) -> tuple[str, ...]:
        return tuple(value for label in self.labels for value in ("--label", label))

    def _intended_resources(self) -> tuple[tuple[str, str], ...]:
        return (
            ("network", self.names.network),
            ("volume", self.names.volume),
            ("container", self.names.postgres),
            ("container", self.names.redis),
            ("container", self.names.upstream),
            ("container", self.names.candidate),
        )

    def _install_signal_handlers(self) -> Mapping[signal.Signals, SignalHandler]:
        previous: dict[signal.Signals, SignalHandler] = {}
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.getsignal(signum)
            signal.signal(signum, self._handle_signal)
        return previous

    @staticmethod
    def _restore_signal_handlers(previous: Mapping[signal.Signals, SignalHandler]) -> None:
        for signum, handler in previous.items():
            signal.signal(signum, handler)

    def _handle_signal(self, _signum: int, _frame: FrameType | None) -> None:
        self._cancelled.set()

    def signal_for_test(self, signum: signal.Signals) -> None:
        self._handle_signal(signum, None)

    @property
    def created_resources(self) -> tuple[OwnedResource, ...]:
        return tuple(self._created)

    @property
    def secrets_destroyed(self) -> bool:
        return self._secret_dir is None and self._master_key is None

    @staticmethod
    def _sha256(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    runner: Final = DisposableRunner(repo_root=Path(__file__).resolve().parents[3])
    try:
        print(json.dumps(runner.run(), ensure_ascii=True, separators=(",", ":"), sort_keys=True))
    except Exception:
        print('{"cleanup_complete":false,"status":"failed"}')
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
