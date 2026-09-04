from __future__ import annotations

import hashlib
import html
import json
import secrets
import subprocess
import time
from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from http.cookiejar import CookieJar
from pathlib import Path
from typing import Final, Literal, Protocol, Self, TypeVar
from urllib.parse import parse_qs, urlparse

import httpx
from pydantic import BaseModel, Field, RootModel, TypeAdapter


class MaintenanceResponse(Protocol):
    @property
    def status_code(self) -> int: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def text(self) -> str: ...

    def json(self) -> object: ...


class MaintenanceSession(Protocol):
    @property
    def cookies(self) -> CookieJar: ...

    def post(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: Mapping[str, object] | None = None,
        data: Mapping[str, str] | None = None,
        follow_redirects: bool = False,
        timeout: float,
    ) -> MaintenanceResponse: ...

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        follow_redirects: bool = False,
        timeout: float,
    ) -> MaintenanceResponse: ...

    def delete(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float,
    ) -> MaintenanceResponse: ...

    def close(self) -> None: ...


SessionFactory = Callable[[], MaintenanceSession]
Clock = Callable[[], float]
ResponseModelT = TypeVar("ResponseModelT", bound=BaseModel)
JWT_PAYLOAD_ADAPTER: Final = TypeAdapter(dict[str, object])
OBJECT_MAP_ADAPTER: Final = TypeAdapter(dict[str, object])
DEFEND_SERVER_ID: Final = "54a0ad17239e9f184882cf47e3ac277c"
DEFEND_SERVER_NAME: Final = "defend_memory"
DEFEND_SERVER_ALIAS: Final = "defend_memory"
DEFEND_TRANSPORT: Final = "http"
DEFEND_AUTH_TYPE: Final = "none"
DEFEND_APPROVAL_STATUS: Final = "active"
DEFEND_TOOL_NAME: Final = "find"
DEFEND_MEMBERSHIP_SHA256: Final = "e08d6ac35d8ceea4eaaaaccce855a9df910684f3f54cff9cce26797dd33ae6cd"
DEFEND_MCP_ACCESS_GROUPS: Final = ("defend_memory",)
DEFEND_ALLOW_ALL_KEYS: Final = False
DEFEND_AVAILABLE_ON_PUBLIC_INTERNET: Final = False
DEFEND_DISALLOWED_TOOLS: Final[tuple[str, ...]] = ()


@dataclass(slots=True)
class HttpxMaintenanceSession:
    client: httpx.Client

    @property
    def cookies(self) -> CookieJar:
        return self.client.cookies.jar

    def post(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        json: Mapping[str, object] | None = None,
        data: Mapping[str, str] | None = None,
        follow_redirects: bool = False,
        timeout: float,
    ) -> MaintenanceResponse:
        return self.client.post(
            path,
            headers=headers,
            json=json,
            data=data,
            follow_redirects=follow_redirects,
            timeout=timeout,
        )

    def get(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        follow_redirects: bool = False,
        timeout: float,
    ) -> MaintenanceResponse:
        return self.client.get(
            path,
            headers=headers,
            params=params,
            follow_redirects=follow_redirects,
            timeout=timeout,
        )

    def delete(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float,
    ) -> MaintenanceResponse:
        return self.client.delete(path, headers=headers, timeout=timeout)

    def close(self) -> None:
        self.client.close()


def httpx_session_factory(base_url: str) -> SessionFactory:
    def create() -> MaintenanceSession:
        return HttpxMaintenanceSession(httpx.Client(base_url=base_url, follow_redirects=False))

    return create


class MaintenanceClientError(RuntimeError):
    pass


class MaintenanceDeadlineExceeded(MaintenanceClientError):
    pass


class MaintenanceCancelled(MaintenanceClientError):
    pass


class CommandResult(Protocol):
    @property
    def returncode(self) -> int: ...

    @property
    def stdout(self) -> str: ...


CommandRunner = Callable[[tuple[str, ...]], CommandResult]


def run_inspection_command(arguments: tuple[str, ...]) -> CommandResult:
    try:
        return subprocess.run(arguments, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise MaintenanceClientError("disposable candidate inspection could not start") from exc


@dataclass(frozen=True, slots=True)
class DisposableCandidateInspector:
    container_name: str
    config_path: Path
    container_config_path: str
    expected_image_id: str
    expected_config_sha256: str
    command_runner: CommandRunner = run_inspection_command

    def inspect(self) -> str:
        config_digest: Final = hashlib.sha256(self.config_path.read_bytes()).hexdigest()
        if config_digest != self.expected_config_sha256:
            raise MaintenanceClientError("disposable candidate config identity mismatch")
        running: Final = self._inspect_field("{{.State.Running}}")
        image_id: Final = self._inspect_field("{{.Image}}")
        if running != "true":
            raise MaintenanceClientError("disposable candidate container is not running")
        if image_id != self.expected_image_id:
            raise MaintenanceClientError("disposable candidate running image identity mismatch")
        configured_digest: Final = self._running_config_digest()
        if configured_digest != self.expected_config_sha256:
            raise MaintenanceClientError("running candidate is not bound to the exact disposable config")
        return image_id

    def _inspect_field(self, template: str) -> str:
        result: Final = self.command_runner(
            ("docker", "inspect", "--type", "container", "--format", template, self.container_name)
        )
        if result.returncode != 0:
            raise MaintenanceClientError("disposable candidate inspection failed")
        return result.stdout.strip()

    def _running_config_digest(self) -> str:
        result: Final = self.command_runner(
            ("docker", "exec", self.container_name, "sha256sum", self.container_config_path)
        )
        if result.returncode != 0:
            raise MaintenanceClientError("disposable candidate config inspection failed")
        digest: Final = result.stdout.partition(" ")[0].strip()
        if len(digest) != 64:
            raise MaintenanceClientError("disposable candidate config inspection returned an invalid digest")
        return digest


def exact_candidate_from_disposable(
    *,
    base_url: str,
    master_key: str,
    inspector: DisposableCandidateInspector,
    toolset_name: str,
    toolset_description: str,
    tool: ToolsetTool,
    cross_audience_paths: tuple[str, ...],
) -> tuple[SessionFactory, ExactCandidate]:
    resource: Final = f"{base_url.rstrip('/')}/toolset/{toolset_name}/lazymcp"
    return (
        httpx_session_factory(base_url),
        ExactCandidate(
            inspect_image_id=inspector.inspect,
            master_key=master_key,
            toolset_name=toolset_name,
            toolset_description=toolset_description,
            tool=tool,
            exact_resource=resource,
            cross_audience_paths=cross_audience_paths,
        ),
    )


class KeyDeleteBody(BaseModel):
    keys: tuple[str, ...]


class KeyInfoParams(BaseModel):
    key: str


class KeyInfo(BaseModel):
    user_id: str | None = None
    team_id: str | None = None


class KeyInfoResponse(BaseModel):
    info: KeyInfo


class KeyListParams(BaseModel):
    user_id: str
    page: int = 1
    size: int = 100


class KeyListResponse(BaseModel):
    total_count: int


class ObjectPermission(BaseModel):
    mcp_servers: tuple[str, ...] = ()
    mcp_access_groups: tuple[str, ...] = ()
    mcp_tool_permissions: Mapping[str, tuple[str, ...]] = Field(default_factory=dict)
    mcp_toolsets: tuple[str, ...] = ()
    blocked_tools: tuple[str, ...] = ()
    vector_stores: tuple[str, ...] = ()
    agents: tuple[str, ...] = ()
    agent_access_groups: tuple[str, ...] = ()
    models: tuple[str, ...] = ()
    search_tools: tuple[str, ...] = ()
    mcp_tool_search_enabled: bool = False

    @classmethod
    def exact_toolset(cls, toolset_id: str) -> Self:
        return cls(mcp_toolsets=(toolset_id,))


class UserCreateBody(BaseModel):
    user_id: str
    user_email: str
    user_role: Literal["internal_user_viewer"] = "internal_user_viewer"
    models: tuple[str, ...] = ("no-default-models",)
    auto_create_key: bool = False
    send_invite_email: bool = False
    object_permission: ObjectPermission


class UserCreateResponse(BaseModel):
    user_id: str


class UserUpdateBody(BaseModel):
    user_id: str
    password: str | None = None
    object_permission: ObjectPermission | None = None


class UserDeleteBody(BaseModel):
    user_ids: tuple[str, ...]


class UserDeleteResponse(RootModel[int]):
    pass


class UserInfoParams(BaseModel):
    user_id: str


class UserListRow(BaseModel):
    user_id: str
    user_email: str | None = None
    user_role: str | None = None
    models: tuple[str, ...] = ()
    object_permission_id: str | None = None
    teams: tuple[str, ...] = ()
    key_count: int = 0


class UserData(UserListRow):
    object_permission: ObjectPermission | None = None


class RelatedResource(BaseModel):
    pass


class UserInfoResponse(BaseModel):
    user_id: str
    user_info: UserData
    keys: tuple[RelatedResource, ...] = ()
    teams: tuple[RelatedResource, ...] = ()


class UserInfoV2Response(UserData):
    pass


class UserListParams(BaseModel):
    user_ids: str | None = None
    page: int = 1
    page_size: int = 100
    sort_by: Literal["user_id"] = "user_id"
    sort_order: Literal["asc"] = "asc"


class UserListResponse(BaseModel):
    users: tuple[UserListRow, ...]
    total: int
    page: int
    page_size: int
    total_pages: int


class ToolsetTool(BaseModel):
    server_id: str
    tool_name: str


class ToolsetCreateBody(BaseModel):
    toolset_name: str
    description: str
    tools: tuple[ToolsetTool, ...]


class ToolsetResponse(BaseModel):
    toolset_id: str
    toolset_name: str
    description: str | None = None
    tools: tuple[ToolsetTool, ...] = ()


class ToolsetListResponse(RootModel[tuple[ToolsetResponse, ...]]):
    pass


class McpServerResponse(BaseModel):
    server_id: str
    server_name: str | None = None
    alias: str | None = None
    url: str | None = None
    transport: str | None = None
    auth_type: str | None = None
    allow_all_keys: bool | None = None
    available_on_public_internet: bool | None = None
    allowed_tools: tuple[str, ...] | None = None
    disallowed_tools: tuple[str, ...] | None = None
    mcp_access_groups: tuple[str, ...] = ()
    approval_status: str | None = None


class McpServerListResponse(RootModel[tuple[McpServerResponse, ...]]):
    pass


class McpToolsParams(BaseModel):
    server_id: str
    include_disabled_tools: bool = True


class PrincipalToolsParams(BaseModel):
    toolset_name: str


class McpToolInfo(BaseModel):
    server_id: str
    server_name: str | None = None
    alias: str | None = None


class McpToolResponse(BaseModel):
    name: str
    mcp_info: McpToolInfo


class McpToolsResponse(BaseModel):
    tools: tuple[McpToolResponse, ...]
    error: str | None = None


class McpServerProjection(BaseModel):
    server_id: str
    server_name: str | None
    alias: str | None
    url: str | None
    transport: str | None
    auth_type: str | None
    allow_all_keys: bool | None
    available_on_public_internet: bool | None
    allowed_tools: tuple[str, ...] | None
    disallowed_tools: tuple[str, ...] | None
    mcp_access_groups: tuple[str, ...]
    approval_status: str | None
    upstream_tool_count: int
    upstream_tool_membership_sha256: str


class UserProjection(BaseModel):
    user_id: str
    teams: tuple[str, ...]
    key_count: int
    mcp_toolsets: tuple[str, ...]


class CollectionProof(BaseModel):
    cardinality: int
    canonical_sha256: str


class MaintenanceBaseline(BaseModel):
    task_user_count: int
    task_key_count: int
    users: tuple[UserProjection, ...]
    toolsets: tuple[ToolsetResponse, ...]
    servers: tuple[McpServerProjection, ...]
    user_collection: CollectionProof
    toolset_collection: CollectionProof
    server_collection: CollectionProof
    upstream_tool_collection: CollectionProof
    catalog_tools: tuple[McpToolResponse, ...]


class UserBaseline(BaseModel):
    task_user_count: int
    task_key_count: int
    users: tuple[UserProjection, ...]
    user_collection: CollectionProof


class LoginBody(BaseModel):
    username: str
    password: str


class ClientRegistrationBody(BaseModel):
    redirect_uris: tuple[str, ...]
    token_endpoint_auth_method: Literal["none"] = "none"
    grant_types: tuple[Literal["authorization_code", "refresh_token"], ...] = (
        "authorization_code",
        "refresh_token",
    )
    response_types: tuple[Literal["code"], ...] = ("code",)


class ClientRegistrationResponse(BaseModel):
    client_id: str
    redirect_uris: tuple[str, ...]
    token_endpoint_auth_method: Literal["none"]


class AuthorizeParams(BaseModel):
    response_type: Literal["code"] = "code"
    client_id: str
    redirect_uri: str
    state: str
    code_challenge: str
    code_challenge_method: Literal["S256"] = "S256"
    resource: str


class AuthorizeCompleteBody(BaseModel):
    flow: str
    delivery: Literal["manual"] = "manual"


class TokenBody(BaseModel):
    grant_type: Literal["authorization_code"] = "authorization_code"
    code: str
    redirect_uri: str
    client_id: str
    code_verifier: str
    resource: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["Bearer"]
    expires_in: int


class RevokeBody(BaseModel):
    token: str
    client_id: str


class McpRequestBody(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    id: int = 1
    method: Literal["initialize"] = "initialize"
    params: Mapping[str, object] = Field(
        default_factory=lambda: {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "maintenance-validation", "version": "1"},
        }
    )


class MaintenanceStatus(BaseModel):
    image_id: str
    email_login: bool
    cookie_count_after_login: int
    pkce_method: Literal["S256"]
    public_client: bool
    exact_audience_status: int
    cross_audience_statuses: tuple[int, ...]
    refresh_revoked: bool
    ui_key_deleted: bool
    client_destroyed: bool
    principal_deleted: bool
    toolset_deleted: bool
    cookies_cleared: bool
    restoration_verified: bool

    @property
    def cleanup_complete(self) -> bool:
        return all(
            (
                self.refresh_revoked,
                self.ui_key_deleted,
                self.client_destroyed,
                self.principal_deleted,
                self.toolset_deleted,
                self.cookies_cleared,
                self.restoration_verified,
            )
        )

    def evidence(self) -> Mapping[str, bool | int | str | tuple[int, ...]]:
        return {
            "email_login": self.email_login,
            "cookie_count_after_login": self.cookie_count_after_login,
            "pkce_method": self.pkce_method,
            "public_client": self.public_client,
            "exact_audience_status": self.exact_audience_status,
            "cross_audience_statuses": self.cross_audience_statuses,
            "refresh_revoked": self.refresh_revoked,
            "ui_key_deleted": self.ui_key_deleted,
            "client_destroyed": self.client_destroyed,
            "principal_deleted": self.principal_deleted,
            "toolset_deleted": self.toolset_deleted,
            "cookies_cleared": self.cookies_cleared,
            "restoration_verified": self.restoration_verified,
        }


@dataclass(frozen=True, slots=True)
class SyntheticIdentity:
    user_id: str
    email: str
    password: str

    @classmethod
    def create(cls) -> Self:
        marker: Final = secrets.token_hex(16)
        return cls(
            user_id=f"maintenance-{marker}",
            email=f"maintenance-{marker}@example.invalid",
            password=secrets.token_urlsafe(48),
        )


@dataclass(frozen=True, slots=True)
class PkceMaterial:
    verifier: str
    challenge: str
    state: str

    @classmethod
    def create(cls) -> Self:
        verifier: Final = secrets.token_urlsafe(64)
        challenge: Final = urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode()
        return cls(verifier=verifier, challenge=challenge, state=secrets.token_urlsafe(32))


@dataclass(frozen=True, slots=True)
class ExactCandidate:
    inspect_image_id: Callable[[], str]
    master_key: str
    toolset_name: str
    toolset_description: str
    tool: ToolsetTool
    exact_resource: str
    cross_audience_paths: tuple[str, ...]
    redirect_uri: str = "http://127.0.0.1:39173/callback"

    def validate_identity(self) -> str:
        return self.inspect_image_id()


@dataclass(slots=True)
class _LifecycleState:
    session: MaintenanceSession
    identity: SyntheticIdentity
    deadline: float
    toolset_id: str | None = None
    toolset_owned: bool = False
    collision_observed: bool = False
    pre_principal_restoration_verified: bool = False
    toolset_creation_attempted: bool = False
    user_creation_attempted: bool = False
    user_created: bool = False
    ui_key: str | None = None
    ui_key_verified: bool = False
    client_id: str | None = None
    authorization_code: str | None = None
    pkce_verifier: str | None = None
    oauth_state: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    refresh_revoked: bool = False
    ui_key_deleted: bool = False
    grant_cleared: bool = False
    principal_absent: bool = False
    ui_key_absent: bool = False
    task_association_absent: bool = False
    restoration_prerequisites_met: bool = False
    principal_deleted: bool = False
    toolset_deleted: bool = False
    client_destroyed: bool = False
    cleanup_started: bool = False


@dataclass(frozen=True, slots=True)
class DcrMaintenanceClient:
    session_factory: SessionFactory
    candidate: ExactCandidate
    timeout_seconds: float = 30.0
    clock: Clock = time.monotonic
    cancelled: Callable[[], bool] = lambda: False

    def validate(self, *, deadline_seconds: float = 120.0) -> MaintenanceStatus:
        image_id: Final = self.candidate.validate_identity()
        self._require_approved_candidate_contract()
        session: Final = self.session_factory()
        state: Final = _LifecycleState(
            session=session,
            identity=SyntheticIdentity.create(),
            deadline=self.clock() + deadline_seconds,
        )
        primary_error: Exception | None = None
        status: MaintenanceStatus | None = None
        baseline: MaintenanceBaseline | None = None
        try:
            baseline = self._capture_baseline(state)
            if (
                baseline.task_user_count != 0
                or baseline.task_key_count != 0
                or any(item.toolset_name == self.candidate.toolset_name for item in baseline.toolsets)
            ):
                raise MaintenanceClientError(
                    "synthetic identity or exact toolset name collided with disposable baseline"
                )
            self._require_candidate_catalog_member(baseline)
            toolset: Final = self._create_toolset(state, baseline)
            self._create_principal(state, toolset.toolset_id)
            self._login(state)
            self._require_principal_tool_resolution(state, baseline)
            registration: Final = self._register(state)
            state.client_id = registration.client_id
            token: Final = self._authorize_and_redeem(state, registration.client_id)
            state.access_token = token.access_token
            state.refresh_token = token.refresh_token
            exact_status: Final = self._audience_status(state, urlparse(self.candidate.exact_resource).path)
            if not 200 <= exact_status < 300:
                raise MaintenanceClientError("exact audience rejected the issued access token")
            cross_statuses: Final = tuple(
                self._audience_status(state, path) for path in self.candidate.cross_audience_paths
            )
            if any(value not in (401, 403) for value in cross_statuses):
                raise MaintenanceClientError("cross-audience request was not rejected")
            status = MaintenanceStatus(
                image_id=image_id,
                email_login=True,
                cookie_count_after_login=len(session.cookies),
                pkce_method="S256",
                public_client=True,
                exact_audience_status=exact_status,
                cross_audience_statuses=cross_statuses,
                refresh_revoked=False,
                ui_key_deleted=False,
                client_destroyed=False,
                principal_deleted=False,
                toolset_deleted=False,
                cookies_cleared=False,
                restoration_verified=False,
            )
        except Exception as exc:
            primary_error = exc
        cleanup_errors: Final = self._cleanup(state, baseline)
        restoration_errors: tuple[Exception, ...] = ()
        if state.toolset_creation_attempted or state.user_creation_attempted:
            if baseline is None:
                restoration_errors = (MaintenanceClientError("maintenance baseline was not captured"),)
            else:
                restoration_errors = self._restoration_errors(state, baseline)
        all_cleanup_errors: Final = (*cleanup_errors, *restoration_errors)
        if primary_error is not None:
            if all_cleanup_errors:
                raise MaintenanceClientError(
                    f"maintenance validation failed and {len(all_cleanup_errors)} cleanup or restoration action(s) failed"
                ) from primary_error
            raise primary_error
        if all_cleanup_errors:
            raise MaintenanceClientError(
                f"{len(all_cleanup_errors)} maintenance cleanup or restoration action(s) failed"
            ) from all_cleanup_errors[0]
        if status is None:
            raise MaintenanceClientError("maintenance validation completed without a status")
        if baseline is None:
            raise MaintenanceClientError("maintenance baseline was not captured")
        final_status: Final = status.model_copy(
            update={
                "refresh_revoked": state.refresh_revoked,
                "ui_key_deleted": state.ui_key_deleted,
                "client_destroyed": state.client_destroyed,
                "principal_deleted": state.principal_deleted,
                "toolset_deleted": state.toolset_deleted,
                "cookies_cleared": len(session.cookies) == 0,
                "restoration_verified": not all_cleanup_errors,
            }
        )
        if not final_status.cleanup_complete:
            raise MaintenanceClientError("maintenance cleanup was not completely proven")
        return final_status

    def _check_deadline(self, state: _LifecycleState) -> None:
        if not state.cleanup_started and self.cancelled():
            raise MaintenanceCancelled("maintenance validation cancelled")
        if self.clock() >= state.deadline:
            raise MaintenanceDeadlineExceeded("maintenance validation deadline exceeded")

    def _headers(self, key: str) -> Mapping[str, str]:
        return {"Authorization": f"Bearer {key}"}

    @staticmethod
    def _form(model: BaseModel) -> dict[str, str]:
        dumped: Final = OBJECT_MAP_ADAPTER.validate_python(model.model_dump(mode="json", exclude_none=True))
        return {key: DcrMaintenanceClient._query_value(value) for key, value in dumped.items()}

    @staticmethod
    def _query_value(value: object) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)
        raise MaintenanceClientError("request form or query contains a non-scalar value")

    @staticmethod
    def _body(model: BaseModel) -> dict[str, object]:
        return OBJECT_MAP_ADAPTER.validate_python(model.model_dump(mode="json", exclude_none=True))

    def _json_request(
        self,
        state: _LifecycleState,
        method: Literal["get", "post"],
        path: str,
        response_type: type[ResponseModelT],
        *,
        headers: Mapping[str, str],
        body: BaseModel | None = None,
        params: BaseModel | None = None,
        expected_status: int = 200,
    ) -> ResponseModelT:
        self._check_deadline(state)
        response: Final = (
            state.session.post(
                path,
                headers=headers,
                json=self._body(body) if body is not None else None,
                timeout=self.timeout_seconds,
            )
            if method == "post"
            else state.session.get(
                path,
                headers=headers,
                params=self._form(params) if params is not None else {},
                timeout=self.timeout_seconds,
            )
        )
        if response.status_code != expected_status:
            raise MaintenanceClientError(f"{path} returned unexpected HTTP {response.status_code}")
        return response_type.model_validate(response.json())

    def _list_toolsets(self, state: _LifecycleState) -> tuple[ToolsetResponse, ...]:
        first: Final = self._json_request(
            state, "get", "/v1/mcp/toolset", ToolsetListResponse, headers=self._headers(self.candidate.master_key)
        )
        second: Final = self._json_request(
            state, "get", "/v1/mcp/toolset", ToolsetListResponse, headers=self._headers(self.candidate.master_key)
        )
        assert isinstance(first, ToolsetListResponse)
        assert isinstance(second, ToolsetListResponse)
        identities: Final = tuple(toolset.toolset_id for toolset in first.root)
        if len(set(identities)) != len(identities) or tuple(sorted(identities)) != identities:
            raise MaintenanceClientError("complete unpaginated toolset collection could not be proven")
        if first.root != second.root:
            raise MaintenanceClientError("unpaginated toolset collection cardinality or digest was unstable")
        return first.root

    def _user_count(self, state: _LifecycleState, user_id: str) -> int:
        response: Final = self._json_request(
            state,
            "get",
            "/user/list",
            UserListResponse,
            headers=self._headers(self.candidate.master_key),
            params=UserListParams(user_ids=user_id),
        )
        assert isinstance(response, UserListResponse)
        return response.total

    def _capture_baseline(self, state: _LifecycleState) -> MaintenanceBaseline:
        user_baseline: Final = self._capture_user_baseline(state)
        servers, server_proof, tool_proof, tools = self._capture_server_catalog(state)
        toolsets: Final = tuple(sorted(self._list_toolsets(state), key=lambda toolset: toolset.toolset_id))
        return MaintenanceBaseline(
            task_user_count=user_baseline.task_user_count,
            task_key_count=user_baseline.task_key_count,
            users=user_baseline.users,
            toolsets=toolsets,
            servers=servers,
            user_collection=user_baseline.user_collection,
            toolset_collection=self._collection_proof(toolsets),
            server_collection=server_proof,
            upstream_tool_collection=tool_proof,
            catalog_tools=tools,
        )

    def _capture_user_baseline(self, state: _LifecycleState) -> UserBaseline:
        first_page: Final = self._user_page(state, 1)
        page_count: Final = max(1, first_page.total_pages)
        remaining_pages: Final = tuple(self._user_page(state, page) for page in range(2, page_count + 1))
        users: Final = (*first_page.users, *(user for page in remaining_pages for user in page.users))
        expected_pages: Final = tuple(range(1, page_count + 1))
        actual_pages: Final = (first_page.page, *(page.page for page in remaining_pages))
        user_ids: Final = tuple(user.user_id for user in users)
        if (
            first_page.page_size != 100
            or actual_pages != expected_pages
            or any(page.total != first_page.total or page.total_pages != page_count for page in remaining_pages)
            or len(users) != first_page.total
            or len(set(user_ids)) != len(user_ids)
            or tuple(sorted(user_ids)) != user_ids
        ):
            raise MaintenanceClientError("complete paginated user baseline could not be captured")
        projected_users: Final = tuple(self._user_projection(state, user) for user in users)
        return UserBaseline(
            task_user_count=self._user_count(state, state.identity.user_id),
            task_key_count=self._task_key_count(state),
            users=projected_users,
            user_collection=self._collection_proof(projected_users),
        )

    def _capture_server_catalog(
        self, state: _LifecycleState
    ) -> tuple[
        tuple[McpServerProjection, ...],
        CollectionProof,
        CollectionProof,
        tuple[McpToolResponse, ...],
    ]:
        servers_response: Final = self._json_request(
            state,
            "get",
            "/v1/mcp/server",
            McpServerListResponse,
            headers=self._headers(self.candidate.master_key),
        )
        servers_confirmation: Final = self._json_request(
            state,
            "get",
            "/v1/mcp/server",
            McpServerListResponse,
            headers=self._headers(self.candidate.master_key),
        )
        assert isinstance(servers_response, McpServerListResponse)
        assert isinstance(servers_confirmation, McpServerListResponse)
        if servers_response.root != servers_confirmation.root:
            raise MaintenanceClientError("unpaginated MCP server collection cardinality or digest was unstable")
        server_ids: Final = tuple(server.server_id for server in servers_response.root)
        if tuple(sorted(server_ids)) != server_ids:
            raise MaintenanceClientError("complete unpaginated MCP server collection could not be proven")
        tools: Final = tuple(
            tool for server in servers_response.root for tool in self._list_mcp_tools(state, server.server_id)
        )
        tool_identities: Final = tuple((tool.mcp_info.server_id, tool.name) for tool in tools)
        if len(set(tool_identities)) != len(tool_identities):
            raise MaintenanceClientError("MCP upstream tool collection contains duplicate memberships")
        servers: Final = self._canonical_servers(servers_response.root, tools)
        canonical_tools: Final = tuple(sorted(tools, key=lambda tool: (tool.mcp_info.server_id, tool.name)))
        return (
            servers,
            self._collection_proof(servers),
            self._collection_proof(tuple(sorted(tool_identities))),
            canonical_tools,
        )

    def _user_page(self, state: _LifecycleState, page: int) -> UserListResponse:
        response: Final = self._json_request(
            state,
            "get",
            "/user/list",
            UserListResponse,
            headers=self._headers(self.candidate.master_key),
            params=UserListParams(page=page),
        )
        assert isinstance(response, UserListResponse)
        return response

    def _user_projection(self, state: _LifecycleState, user: UserListRow) -> UserProjection:
        info: Final = self._json_request(
            state,
            "get",
            "/v2/user/info",
            UserInfoV2Response,
            headers=self._headers(self.candidate.master_key),
            params=UserInfoParams(user_id=user.user_id),
        )
        assert isinstance(info, UserInfoV2Response)
        if info.user_id != user.user_id or info.teams != user.teams:
            raise MaintenanceClientError("user list and relation-bearing user info disagree")
        return UserProjection(
            user_id=user.user_id,
            teams=tuple(sorted(set(info.teams))),
            key_count=user.key_count,
            mcp_toolsets=tuple(sorted(set((info.object_permission or ObjectPermission()).mcp_toolsets))),
        )

    def _list_mcp_tools(self, state: _LifecycleState, server_id: str) -> tuple[McpToolResponse, ...]:
        response: Final = self._json_request(
            state,
            "get",
            "/mcp-rest/tools/list",
            McpToolsResponse,
            headers=self._headers(self.candidate.master_key),
            params=McpToolsParams(server_id=server_id),
        )
        confirmation: Final = self._json_request(
            state,
            "get",
            "/mcp-rest/tools/list",
            McpToolsResponse,
            headers=self._headers(self.candidate.master_key),
            params=McpToolsParams(server_id=server_id),
        )
        assert isinstance(response, McpToolsResponse)
        assert isinstance(confirmation, McpToolsResponse)
        if response != confirmation:
            raise MaintenanceClientError("unpaginated MCP upstream tool cardinality or digest was unstable")
        if response.error is not None:
            raise MaintenanceClientError("complete MCP upstream tool collection could not be captured")
        identities: Final = tuple((tool.mcp_info.server_id, tool.name) for tool in response.tools)
        if (
            any(tool.mcp_info.server_id != server_id for tool in response.tools)
            or len(set(identities)) != len(identities)
            or tuple(sorted(identities)) != identities
        ):
            raise MaintenanceClientError("MCP upstream tool collection is not canonical and unique")
        return response.tools

    @staticmethod
    def _canonical_servers(
        servers: tuple[McpServerResponse, ...], tools: tuple[McpToolResponse, ...]
    ) -> tuple[McpServerProjection, ...]:
        server_ids: Final = tuple(server.server_id for server in servers)
        if len(set(server_ids)) != len(server_ids):
            raise MaintenanceClientError("MCP server collection contains duplicate identities")
        tool_server_ids: Final = frozenset(tool.mcp_info.server_id for tool in tools)
        if not tool_server_ids.issubset(server_ids):
            raise MaintenanceClientError("MCP upstream tool collection names an unknown server")
        if any(
            tool.mcp_info.server_name not in (None, server.server_name, server.alias)
            or tool.mcp_info.alias not in (None, server.alias)
            for server in servers
            for tool in tools
            if tool.mcp_info.server_id == server.server_id
        ):
            raise MaintenanceClientError("MCP upstream tool identity does not match its server")
        return tuple(
            sorted(
                (
                    McpServerProjection(
                        server_id=server.server_id,
                        server_name=server.server_name,
                        alias=server.alias,
                        url=server.url,
                        transport=server.transport,
                        auth_type=server.auth_type,
                        allow_all_keys=server.allow_all_keys,
                        available_on_public_internet=server.available_on_public_internet,
                        allowed_tools=(
                            tuple(sorted(set(server.allowed_tools))) if server.allowed_tools is not None else None
                        ),
                        disallowed_tools=(
                            tuple(sorted(set(server.disallowed_tools))) if server.disallowed_tools is not None else None
                        ),
                        mcp_access_groups=tuple(sorted(set(server.mcp_access_groups))),
                        approval_status=server.approval_status,
                        upstream_tool_count=len(
                            tuple(tool for tool in tools if tool.mcp_info.server_id == server.server_id)
                        ),
                        upstream_tool_membership_sha256=DcrMaintenanceClient._membership_digest(
                            tuple(sorted(tool.name for tool in tools if tool.mcp_info.server_id == server.server_id))
                        ),
                    )
                    for server in servers
                ),
                key=lambda server: server.server_id,
            )
        )

    @staticmethod
    def _membership_digest(tool_names: tuple[str, ...]) -> str:
        canonical: Final = json.dumps(tool_names, ensure_ascii=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @staticmethod
    def _collection_proof(values: tuple[object, ...]) -> CollectionProof:
        wire: Final = tuple(
            value.model_dump(mode="json") if isinstance(value, BaseModel) else value for value in values
        )
        canonical: Final = json.dumps(wire, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
        return CollectionProof(cardinality=len(values), canonical_sha256=hashlib.sha256(canonical.encode()).hexdigest())

    def _key_info(self, state: _LifecycleState, key: str) -> KeyInfo:
        response: Final = self._json_request(
            state,
            "get",
            "/key/info",
            KeyInfoResponse,
            headers=self._headers(self.candidate.master_key),
            params=KeyInfoParams(key=key),
        )
        assert isinstance(response, KeyInfoResponse)
        return response.info

    def _key_absent(self, state: _LifecycleState, key: str) -> bool:
        self._check_deadline(state)
        response: Final = state.session.get(
            "/key/info",
            headers=self._headers(self.candidate.master_key),
            params=self._form(KeyInfoParams(key=key)),
            timeout=self.timeout_seconds,
        )
        if response.status_code == 404:
            return True
        if response.status_code == 200:
            return False
        raise MaintenanceClientError(f"/key/info returned unexpected HTTP {response.status_code}")

    def _require_approved_candidate_contract(self) -> None:
        canonical: Final = json.dumps(
            [{"server_id": self.candidate.tool.server_id, "tool_name": self.candidate.tool.tool_name}],
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
        if (
            self.candidate.toolset_name != DEFEND_SERVER_ALIAS
            or self.candidate.tool.server_id != DEFEND_SERVER_ID
            or self.candidate.tool.tool_name != DEFEND_TOOL_NAME
            or hashlib.sha256(canonical.encode()).hexdigest() != DEFEND_MEMBERSHIP_SHA256
        ):
            raise MaintenanceClientError("candidate does not match the exact approved Defend toolset contract")

    def _require_candidate_catalog_member(self, baseline: MaintenanceBaseline) -> None:
        server: Final = next(
            (server for server in baseline.servers if server.server_id == self.candidate.tool.server_id),
            None,
        )
        if (
            server is None
            or server.server_id != DEFEND_SERVER_ID
            or server.server_name != DEFEND_SERVER_NAME
            or server.alias != DEFEND_SERVER_ALIAS
            or server.transport != DEFEND_TRANSPORT
            or server.auth_type != DEFEND_AUTH_TYPE
            or server.approval_status != DEFEND_APPROVAL_STATUS
            or server.allowed_tools != ()
            or server.mcp_access_groups != DEFEND_MCP_ACCESS_GROUPS
            or server.allow_all_keys is not DEFEND_ALLOW_ALL_KEYS
            or server.available_on_public_internet is not DEFEND_AVAILABLE_ON_PUBLIC_INTERNET
            or server.disallowed_tools != DEFEND_DISALLOWED_TOOLS
        ):
            raise MaintenanceClientError("candidate catalog does not match the exact approved Defend server identity")
        matches: Final = tuple(
            tool
            for tool in baseline.catalog_tools
            if tool.mcp_info.server_id == self.candidate.tool.server_id and tool.name == self.candidate.tool.tool_name
        )
        if (
            len(matches) != 1
            or matches[0].mcp_info.server_name != server.server_name
            or matches[0].mcp_info.alias != server.alias
        ):
            raise MaintenanceClientError("candidate toolset member does not match the exact server catalog metadata")

    def _create_toolset(self, state: _LifecycleState, baseline: MaintenanceBaseline) -> ToolsetResponse:
        state.toolset_creation_attempted = True
        response: Final = self._json_request(
            state,
            "post",
            "/v1/mcp/toolset",
            ToolsetResponse,
            headers=self._headers(self.candidate.master_key),
            body=ToolsetCreateBody(
                toolset_name=self.candidate.toolset_name,
                description=self.candidate.toolset_description,
                tools=(self.candidate.tool,),
            ),
            expected_status=201,
        )
        assert isinstance(response, ToolsetResponse)
        state.toolset_id = response.toolset_id
        if response.toolset_name != self.candidate.toolset_name or response.tools != (self.candidate.tool,):
            raise MaintenanceClientError("created toolset did not match the exact synthetic request")
        state.toolset_owned = self._returned_toolset_is_owned(state, response)
        self._verify_created_toolset(state, baseline, response)
        return response

    def _returned_toolset_is_owned(self, state: _LifecycleState, created: ToolsetResponse) -> bool:
        expected: Final = ToolsetResponse(
            toolset_id=created.toolset_id,
            toolset_name=self.candidate.toolset_name,
            description=self.candidate.toolset_description,
            tools=(self.candidate.tool,),
        )
        listed: Final = self._list_toolsets(state)
        id_matches: Final = tuple(toolset for toolset in listed if toolset.toolset_id == created.toolset_id)
        name_matches: Final = tuple(
            toolset for toolset in listed if toolset.toolset_name == self.candidate.toolset_name
        )
        return id_matches == (expected,) and expected in name_matches

    def _verify_created_toolset(
        self,
        state: _LifecycleState,
        baseline: MaintenanceBaseline,
        created: ToolsetResponse,
    ) -> None:
        expected: Final = ToolsetResponse(
            toolset_id=created.toolset_id,
            toolset_name=self.candidate.toolset_name,
            description=self.candidate.toolset_description,
            tools=(self.candidate.tool,),
        )
        listed: Final = self._list_toolsets(state)
        task_name_matches: Final = tuple(
            toolset for toolset in listed if toolset.toolset_name == self.candidate.toolset_name
        )
        task_id_matches: Final = tuple(toolset for toolset in listed if toolset.toolset_id == created.toolset_id)
        state.collision_observed = any(toolset.toolset_id != created.toolset_id for toolset in task_name_matches)
        non_task: Final = tuple(toolset for toolset in listed if toolset.toolset_id != created.toolset_id)
        by_id: Final = self._json_request(
            state,
            "get",
            f"/v1/mcp/toolset/{created.toolset_id}",
            ToolsetResponse,
            headers=self._headers(self.candidate.master_key),
        )
        assert isinstance(by_id, ToolsetResponse)
        if not state.toolset_owned:
            raise MaintenanceClientError("returned toolset ID was not proven task-owned")
        current_servers, current_server_proof, current_tool_proof, current_tools = self._capture_server_catalog(state)
        current_user_baseline: Final = self._capture_user_baseline(state)
        if (
            task_name_matches != (expected,)
            or task_id_matches != (expected,)
            or by_id != expected
            or non_task != baseline.toolsets
            or current_servers != baseline.servers
            or current_server_proof != baseline.server_collection
            or current_tool_proof != baseline.upstream_tool_collection
            or current_tools != baseline.catalog_tools
            or current_user_baseline.task_user_count != 0
            or current_user_baseline.task_key_count != 0
            or current_user_baseline.users != baseline.users
            or current_user_baseline.user_collection != baseline.user_collection
        ):
            raise MaintenanceClientError(
                "created toolset ownership, collision, membership, or non-task baseline verification failed"
            )
        state.pre_principal_restoration_verified = True

    def _create_principal(self, state: _LifecycleState, toolset_id: str) -> None:
        if not state.toolset_owned or not state.pre_principal_restoration_verified:
            raise MaintenanceClientError(
                "task ownership and non-task restoration must be proven before principal creation"
            )
        state.user_creation_attempted = True
        response: Final = self._json_request(
            state,
            "post",
            "/user/new",
            UserCreateResponse,
            headers=self._headers(self.candidate.master_key),
            body=UserCreateBody(
                user_id=state.identity.user_id,
                user_email=state.identity.email,
                object_permission=ObjectPermission.exact_toolset(toolset_id),
            ),
        )
        assert isinstance(response, UserCreateResponse)
        if response.user_id != state.identity.user_id:
            raise MaintenanceClientError("principal create returned an unexpected user id")
        state.user_created = True
        _ = self._json_request(
            state,
            "post",
            "/user/update",
            UserData,
            headers=self._headers(self.candidate.master_key),
            body=UserUpdateBody(user_id=state.identity.user_id, password=state.identity.password),
        )
        info: Final = self._json_request(
            state,
            "get",
            "/v2/user/info",
            UserInfoV2Response,
            headers=self._headers(self.candidate.master_key),
            params=UserInfoParams(user_id=state.identity.user_id),
        )
        assert isinstance(info, UserInfoV2Response)
        legacy_info: Final = self._json_request(
            state,
            "get",
            "/user/info",
            UserInfoResponse,
            headers=self._headers(self.candidate.master_key),
            params=UserInfoParams(user_id=state.identity.user_id),
        )
        assert isinstance(legacy_info, UserInfoResponse)
        if (
            info.user_email != state.identity.email
            or info.user_role != "internal_user_viewer"
            or info.models != ("no-default-models",)
            or info.object_permission != ObjectPermission.exact_toolset(toolset_id)
            or info.teams
            or legacy_info.keys
            or legacy_info.teams
        ):
            raise MaintenanceClientError("principal read-back was not exact least privilege")

    def _login(self, state: _LifecycleState) -> None:
        self._check_deadline(state)
        response: Final = state.session.post(
            "/login",
            data=self._form(LoginBody(username=state.identity.email, password=state.identity.password)),
            follow_redirects=False,
            timeout=self.timeout_seconds,
        )
        if response.status_code != 303 or len(state.session.cookies) == 0:
            raise MaintenanceClientError("email login did not establish an in-memory cookie session")
        token_cookie: Final = next((cookie.value for cookie in state.session.cookies if cookie.name == "token"), None)
        if token_cookie is None:
            raise MaintenanceClientError("email login did not return the UI token cookie")
        state.ui_key = self._ui_key_from_cookie(token_cookie)
        key_info: Final = self._key_info(state, state.ui_key)
        if key_info.user_id != state.identity.user_id or key_info.team_id != "litellm-dashboard":
            raise MaintenanceClientError("UI session key ownership read-back did not match the task principal")
        state.ui_key_verified = True

    def _require_principal_tool_resolution(self, state: _LifecycleState, baseline: MaintenanceBaseline) -> None:
        if state.ui_key is None:
            raise MaintenanceClientError("principal session key was not established")
        response: Final = self._json_request(
            state,
            "get",
            "/mcp-rest/tools/list",
            McpToolsResponse,
            headers={"x-litellm-api-key": state.ui_key},
            params=PrincipalToolsParams(toolset_name=self.candidate.toolset_name),
        )
        assert isinstance(response, McpToolsResponse)
        server: Final = next(
            (server for server in baseline.servers if server.server_id == self.candidate.tool.server_id),
            None,
        )
        if server is None or server.server_name is None or server.alias is None:
            raise MaintenanceClientError("candidate server metadata is incomplete")
        expected: Final = (
            self.candidate.tool.server_id,
            self.candidate.tool.tool_name,
            server.server_name,
            server.alias,
        )
        actual: Final = tuple(
            (tool.mcp_info.server_id, tool.name, tool.mcp_info.server_name, tool.mcp_info.alias)
            for tool in response.tools
        )
        if response.error is not None or actual != (expected,):
            raise MaintenanceClientError("principal toolset scope did not resolve exactly the intended one tool")

    def _register(self, state: _LifecycleState) -> ClientRegistrationResponse:
        self._check_deadline(state)
        response: Final = state.session.post(
            "/register",
            headers={},
            json=self._body(ClientRegistrationBody(redirect_uris=(self.candidate.redirect_uri,))),
            timeout=self.timeout_seconds,
        )
        if response.status_code != 201:
            raise MaintenanceClientError(f"/register returned unexpected HTTP {response.status_code}")
        raw: Final = OBJECT_MAP_ADAPTER.validate_python(response.json())
        if "client_secret" in raw:
            raise MaintenanceClientError("maintenance DCR registration returned a client secret")
        registration: Final = ClientRegistrationResponse.model_validate(raw)
        if registration.redirect_uris != (self.candidate.redirect_uri,):
            raise MaintenanceClientError("DCR registration changed the loopback redirect")
        return registration

    def _authorize_and_redeem(self, state: _LifecycleState, client_id: str) -> TokenResponse:
        pkce: Final = PkceMaterial.create()
        state.pkce_verifier = pkce.verifier
        state.oauth_state = pkce.state
        self._check_deadline(state)
        authorize: Final = state.session.get(
            "/authorize",
            params=self._form(
                AuthorizeParams(
                    client_id=client_id,
                    redirect_uri=self.candidate.redirect_uri,
                    state=pkce.state,
                    code_challenge=pkce.challenge,
                    resource=self.candidate.exact_resource,
                )
            ),
            follow_redirects=False,
            timeout=self.timeout_seconds,
        )
        if authorize.status_code != 303:
            raise MaintenanceClientError(f"authorize returned unexpected HTTP {authorize.status_code}")
        flow: Final = parse_qs(urlparse(self._header(authorize, "location")).query).get("connect_flow", [None])[0]
        if not isinstance(flow, str):
            raise MaintenanceClientError("authorize redirect omitted connect_flow")
        self._check_deadline(state)
        complete: Final = state.session.post(
            "/authorize/complete",
            data=self._form(AuthorizeCompleteBody(flow=flow)),
            follow_redirects=False,
            timeout=self.timeout_seconds,
        )
        if complete.status_code != 200:
            raise MaintenanceClientError(f"authorize complete returned unexpected HTTP {complete.status_code}")
        callback_url: Final = self._manual_callback_url(complete.text)
        parsed_callback: Final = urlparse(callback_url)
        if f"{parsed_callback.scheme}://{parsed_callback.netloc}{parsed_callback.path}" != self.candidate.redirect_uri:
            raise MaintenanceClientError("manual callback did not match the registered loopback redirect")
        callback_params: Final = parse_qs(parsed_callback.query)
        if callback_params.get("state") != [pkce.state] or not callback_params.get("code"):
            raise MaintenanceClientError("manual callback state or code was invalid")
        state.authorization_code = callback_params["code"][0]
        self._check_deadline(state)
        token_body: Final = TokenBody(
            code=state.authorization_code,
            redirect_uri=self.candidate.redirect_uri,
            client_id=client_id,
            code_verifier=pkce.verifier,
            resource=self.candidate.exact_resource,
        )
        token_response: Final = state.session.post(
            "/token",
            data=self._form(token_body),
            timeout=self.timeout_seconds,
        )
        if token_response.status_code != 200:
            raise MaintenanceClientError(f"token returned unexpected HTTP {token_response.status_code}")
        return TokenResponse.model_validate(token_response.json())

    def _audience_status(self, state: _LifecycleState, path: str) -> int:
        self._check_deadline(state)
        if state.access_token is None:
            raise MaintenanceClientError("access token was not minted")
        response: Final = state.session.post(
            path,
            headers={
                **self._headers(state.access_token),
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json",
            },
            json=self._body(McpRequestBody()),
            timeout=self.timeout_seconds,
        )
        return response.status_code

    def _cleanup(self, state: _LifecycleState, baseline: MaintenanceBaseline | None) -> tuple[Exception, ...]:
        errors: list[Exception] = []
        state.cleanup_started = True
        state.deadline = self.clock() + max(self.timeout_seconds * 8, 30.0)

        def attempt(action: Callable[[], None]) -> None:
            try:
                action()
            except Exception as exc:
                errors.append(exc)

        if state.refresh_token is not None and state.client_id is not None:
            attempt(lambda: self._revoke(state))
        if state.ui_key is not None:
            attempt(lambda: self._delete_ui_key(state))
        if state.user_created:
            attempt(lambda: self._clear_grant(state))
            if state.grant_cleared:
                attempt(lambda: self._delete_principal(state))
        if state.access_token is not None and state.principal_deleted:
            attempt(lambda: self._require_deleted_principal_denial(state))
        if state.toolset_id is not None and state.toolset_owned:
            attempt(lambda: self._verify_principal_prerequisites(state))
        if (
            state.toolset_id is not None
            and state.toolset_owned
            and not state.user_creation_attempted
            and self._principal_cleanup_prerequisites_met(state)
        ):
            if baseline is None:
                errors.append(MaintenanceClientError("toolset cleanup has no authoritative baseline"))
            else:
                attempt(lambda: self._verify_pre_principal_cleanup_safety(state, baseline))
        elif state.toolset_id is not None and state.toolset_owned and self._principal_cleanup_prerequisites_met(state):
            if baseline is None:
                errors.append(MaintenanceClientError("toolset cleanup has no authoritative baseline"))
            else:
                attempt(lambda: self._verify_pre_toolset_restoration(state, baseline))
        if state.toolset_id is not None and state.toolset_owned and self._toolset_delete_prerequisites_met(state):
            attempt(lambda: self._delete_toolset(state))

        state.access_token = None
        state.refresh_token = None
        state.ui_key = None
        state.client_id = None
        state.authorization_code = None
        state.pkce_verifier = None
        state.oauth_state = None
        state.client_destroyed = True
        state.session.cookies.clear()
        state.session.close()
        return tuple(errors)

    def _revoke(self, state: _LifecycleState) -> None:
        assert state.refresh_token is not None and state.client_id is not None
        response: Final = state.session.post(
            "/revoke",
            data=self._form(RevokeBody(token=state.refresh_token, client_id=state.client_id)),
            timeout=self.timeout_seconds,
        )
        if response.status_code != 200:
            raise MaintenanceClientError(f"refresh revocation returned HTTP {response.status_code}")
        state.refresh_revoked = True

    def _delete_ui_key(self, state: _LifecycleState) -> None:
        if state.ui_key is None or not state.ui_key_verified:
            raise MaintenanceClientError("UI session key was not ownership-verified")
        response: Final = state.session.post(
            "/key/delete",
            headers=self._headers(self.candidate.master_key),
            json=self._body(KeyDeleteBody(keys=(state.ui_key,))),
            timeout=self.timeout_seconds,
        )
        if response.status_code != 200:
            raise MaintenanceClientError(f"UI key deletion returned HTTP {response.status_code}")
        if not self._key_absent(state, state.ui_key):
            raise MaintenanceClientError("UI session key remained present after deletion")
        state.ui_key_deleted = True
        state.ui_key_absent = True

    def _clear_grant(self, state: _LifecycleState) -> None:
        _ = self._json_request(
            state,
            "post",
            "/user/update",
            UserData,
            headers=self._headers(self.candidate.master_key),
            body=UserUpdateBody(user_id=state.identity.user_id, object_permission=ObjectPermission()),
        )
        info: Final = self._json_request(
            state,
            "get",
            "/v2/user/info",
            UserInfoV2Response,
            headers=self._headers(self.candidate.master_key),
            params=UserInfoParams(user_id=state.identity.user_id),
        )
        assert isinstance(info, UserInfoV2Response)
        if info.object_permission is not None and info.object_permission != ObjectPermission():
            raise MaintenanceClientError("principal grant remained after clear")
        state.grant_cleared = True
        state.task_association_absent = True

    def _delete_principal(self, state: _LifecycleState) -> None:
        _ = self._json_request(
            state,
            "post",
            "/user/delete",
            UserDeleteResponse,
            headers=self._headers(self.candidate.master_key),
            body=UserDeleteBody(user_ids=(state.identity.user_id,)),
        )
        state.principal_deleted = True

    def _verify_principal_prerequisites(self, state: _LifecycleState) -> None:
        if not state.user_created:
            if self._user_count(state, state.identity.user_id) != 0:
                raise MaintenanceClientError("ambiguous principal creation remains visible")
            if self._task_key_count(state) != 0:
                raise MaintenanceClientError("ambiguous principal creation left task keys")
            state.grant_cleared = True
            state.task_association_absent = True
            state.principal_deleted = True
            state.principal_absent = True
            state.ui_key_deleted = True
            state.ui_key_absent = True
            return
        if not state.principal_deleted:
            raise MaintenanceClientError("principal deletion was not confirmed")
        if self._user_count(state, state.identity.user_id) != 0:
            raise MaintenanceClientError("principal remained after deletion")
        state.principal_absent = True
        if self._task_key_count(state) != 0:
            raise MaintenanceClientError("task principal keys remained after deletion")
        if state.ui_key is not None:
            if not state.ui_key_deleted or not self._key_absent(state, state.ui_key):
                raise MaintenanceClientError("UI session key cleanup was not confirmed")
            state.ui_key_absent = True
        else:
            state.ui_key_deleted = True
            state.ui_key_absent = True
        if not state.grant_cleared or not state.task_association_absent:
            raise MaintenanceClientError("principal grant restoration prerequisite was not confirmed")

    def _task_key_count(self, state: _LifecycleState) -> int:
        response: Final = self._json_request(
            state,
            "get",
            "/key/list",
            KeyListResponse,
            headers=self._headers(self.candidate.master_key),
            params=KeyListParams(user_id=state.identity.user_id),
        )
        assert isinstance(response, KeyListResponse)
        return response.total_count

    @staticmethod
    def _principal_cleanup_prerequisites_met(state: _LifecycleState) -> bool:
        return all(
            (
                state.grant_cleared,
                state.task_association_absent,
                state.principal_deleted,
                state.principal_absent,
                state.ui_key_deleted,
                state.ui_key_absent,
            )
        )

    @staticmethod
    def _toolset_delete_prerequisites_met(state: _LifecycleState) -> bool:
        return DcrMaintenanceClient._principal_cleanup_prerequisites_met(state) and state.restoration_prerequisites_met

    def _verify_pre_toolset_restoration(self, state: _LifecycleState, baseline: MaintenanceBaseline) -> None:
        assert state.toolset_id is not None
        current: Final = self._capture_baseline(state)
        task_toolsets: Final = tuple(toolset for toolset in current.toolsets if toolset.toolset_id == state.toolset_id)
        non_task_toolsets: Final = tuple(
            toolset for toolset in current.toolsets if toolset.toolset_id != state.toolset_id
        )
        if (
            current.task_user_count != baseline.task_user_count
            or current.task_key_count != baseline.task_key_count
            or current.users != baseline.users
            or current.servers != baseline.servers
            or non_task_toolsets != baseline.toolsets
            or len(task_toolsets) != 1
            or task_toolsets[0].toolset_name != self.candidate.toolset_name
            or task_toolsets[0].description != self.candidate.toolset_description
            or task_toolsets[0].tools != (self.candidate.tool,)
        ):
            raise MaintenanceClientError(
                "pre-toolset user, key, membership, association, server, or toolset restoration failed"
            )
        state.restoration_prerequisites_met = True

    def _verify_pre_principal_cleanup_safety(self, state: _LifecycleState, baseline: MaintenanceBaseline) -> None:
        users: Final = self._capture_user_baseline(state)
        servers, server_proof, tool_proof, tools = self._capture_server_catalog(state)
        listed: Final = self._list_toolsets(state)
        non_task: Final = tuple(toolset for toolset in listed if toolset.toolset_id != state.toolset_id)
        late_collision_preserved: Final = (
            len(non_task) == len(baseline.toolsets) + 1
            and all(toolset in non_task for toolset in baseline.toolsets)
            and len(
                tuple(
                    toolset
                    for toolset in non_task
                    if toolset not in baseline.toolsets and toolset.toolset_name == self.candidate.toolset_name
                )
            )
            == 1
        )
        if (
            users.task_user_count != 0
            or users.task_key_count != 0
            or users.users != baseline.users
            or users.user_collection != baseline.user_collection
            or servers != baseline.servers
            or server_proof != baseline.server_collection
            or tool_proof != baseline.upstream_tool_collection
            or tools != baseline.catalog_tools
            or (not late_collision_preserved if state.collision_observed else non_task != baseline.toolsets)
        ):
            raise MaintenanceClientError("pre-principal task identity or non-task baseline cleanup safety failed")
        state.restoration_prerequisites_met = True

    def _require_deleted_principal_denial(self, state: _LifecycleState) -> None:
        status: Final = self._audience_status(state, urlparse(self.candidate.exact_resource).path)
        if status not in (401, 403):
            raise MaintenanceClientError("deleted principal access token remained admitted")

    def _delete_toolset(self, state: _LifecycleState) -> None:
        assert state.toolset_id is not None
        response: Final = state.session.delete(
            f"/v1/mcp/toolset/{state.toolset_id}",
            headers=self._headers(self.candidate.master_key),
            timeout=self.timeout_seconds,
        )
        if response.status_code != 202:
            raise MaintenanceClientError(f"toolset deletion returned HTTP {response.status_code}")
        if not self._toolset_absent(state, state.toolset_id):
            raise MaintenanceClientError("toolset remained present after deletion")
        state.toolset_deleted = True

    def _toolset_absent(self, state: _LifecycleState, toolset_id: str) -> bool:
        self._check_deadline(state)
        response: Final = state.session.get(
            f"/v1/mcp/toolset/{toolset_id}",
            headers=self._headers(self.candidate.master_key),
            timeout=self.timeout_seconds,
        )
        if response.status_code == 404:
            return True
        if response.status_code == 200:
            return False
        raise MaintenanceClientError(f"toolset read-back returned unexpected HTTP {response.status_code}")

    def _restoration_errors(
        self,
        state: _LifecycleState,
        baseline: MaintenanceBaseline,
    ) -> tuple[Exception, ...]:
        try:
            self._assert_restored(state, baseline)
        except Exception as exc:
            return (exc,)
        return ()

    def _assert_restored(
        self,
        state: _LifecycleState,
        baseline: MaintenanceBaseline,
    ) -> None:
        verification_session: Final = self.session_factory()
        verification_state: Final = _LifecycleState(
            session=verification_session,
            identity=state.identity,
            deadline=self.clock() + self.timeout_seconds,
        )
        try:
            captured: Final = self._capture_baseline(verification_state)
            restored: MaintenanceBaseline
            if state.collision_observed:
                restored_toolsets: Final = tuple(
                    toolset
                    for toolset in captured.toolsets
                    if not (
                        toolset.toolset_name == self.candidate.toolset_name and toolset.toolset_id != state.toolset_id
                    )
                )
                restored = captured.model_copy(
                    update={
                        "toolsets": restored_toolsets,
                        "toolset_collection": self._collection_proof(restored_toolsets),
                    }
                )
            else:
                restored = captured
            if restored != baseline:
                raise MaintenanceClientError(
                    "user, key, membership, association, toolset, or server baseline was not restored"
                )
            if state.user_created and not all(
                (
                    state.grant_cleared,
                    state.task_association_absent,
                    state.principal_deleted,
                    state.principal_absent,
                    state.ui_key_deleted,
                    state.ui_key_absent,
                )
            ):
                raise MaintenanceClientError("principal, grant, membership, or key restoration was not proven")
            if any(
                artifact is not None
                for artifact in (
                    state.access_token,
                    state.refresh_token,
                    state.ui_key,
                    state.client_id,
                    state.authorization_code,
                    state.pkce_verifier,
                    state.oauth_state,
                )
            ):
                raise MaintenanceClientError("client credential artifacts remain in memory")
        finally:
            verification_session.cookies.clear()
            verification_session.close()

    @staticmethod
    def _header(response: MaintenanceResponse, name: str) -> str:
        value: Final = next((value for key, value in response.headers.items() if key.lower() == name.lower()), None)
        if value is None:
            raise MaintenanceClientError(f"response omitted {name} header")
        return value

    @staticmethod
    def _manual_callback_url(body: str) -> str:
        marker: Final = 'value="'
        start: Final = body.find(marker)
        if start < 0:
            raise MaintenanceClientError("manual completion page omitted callback URL")
        end: Final = body.find('"', start + len(marker))
        if end < 0:
            raise MaintenanceClientError("manual completion page had malformed callback URL")
        return html.unescape(body[start + len(marker) : end])

    @staticmethod
    def _ui_key_from_cookie(token: str) -> str:
        payload_parts: Final = token.split(".")
        if len(payload_parts) != 3:
            raise MaintenanceClientError("UI token cookie was not a JWT")
        segment: Final = payload_parts[1]
        try:
            payload: Final = JWT_PAYLOAD_ADAPTER.validate_json(urlsafe_b64decode(segment + "=" * (-len(segment) % 4)))
        except ValueError as exc:
            raise MaintenanceClientError("UI token cookie payload was invalid") from exc
        key: Final = payload.get("key")
        if not isinstance(key, str) or not key:
            raise MaintenanceClientError("UI token cookie omitted the session key")
        return key
