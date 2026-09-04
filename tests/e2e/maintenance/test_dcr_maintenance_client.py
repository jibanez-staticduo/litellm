from __future__ import annotations

import hashlib
import json
from base64 import urlsafe_b64encode
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from http.cookiejar import Cookie, CookieJar
from pathlib import Path
from typing import Final, Literal
from urllib.parse import urlencode

import pytest
from pydantic import TypeAdapter

from .dcr_maintenance_client import (
    Clock,
    DcrMaintenanceClient,
    DisposableCandidateInspector,
    ExactCandidate,
    MaintenanceClientError,
    MaintenanceDeadlineExceeded,
    MaintenanceResponse,
    McpRequestBody,
    ToolsetTool,
    exact_candidate_from_disposable,
    httpx_session_factory,
)

MASTER_KEY: Final = "synthetic-master-secret"
UI_KEY: Final = "synthetic-ui-secret"
CLIENT_ID: Final = "llm_dcrc_synthetic-client-secret"
ACCESS_TOKEN: Final = "llm_session_synthetic-access-secret"
REFRESH_TOKEN: Final = "llm_srefresh_synthetic-refresh-secret"
CODE: Final = "llm_gcode_synthetic-code-secret"
FLOW: Final = "synthetic-flow-secret"
TOOLSET_ID: Final = "synthetic-toolset-id"
DEFEND_SERVER_ID: Final = "54a0ad17239e9f184882cf47e3ac277c"
DEFEND_NAME: Final = "defend_memory"
DEFEND_TOOL: Final = "find"
EXPECTED_IMAGE: Final = "sha256:disposable-exact-candidate"
EXACT_RESOURCE: Final = "https://candidate.invalid/toolset/defend_memory/lazymcp"
EXACT_PATH: Final = "/toolset/defend_memory/lazymcp"
CROSS_PATHS: Final = ("/lazymcp", "/lazymcp/other-scope", "/mcp")
SENSITIVE_VALUES: Final = (MASTER_KEY, UI_KEY, CLIENT_ID, ACCESS_TOKEN, REFRESH_TOKEN, CODE, FLOW)
OBJECT_MAP_ADAPTER: Final = TypeAdapter(dict[str, object])


def _cookie(name: str, value: str) -> Cookie:
    return Cookie(
        version=0,
        name=name,
        value=value,
        port=None,
        port_specified=False,
        domain="candidate.invalid",
        domain_specified=True,
        domain_initial_dot=False,
        path="/",
        path_specified=True,
        secure=True,
        expires=None,
        discard=True,
        comment=None,
        comment_url=None,
        rest={"HttpOnly": ""},
        rfc2109=False,
    )


def _jwt_with_key(key: str) -> str:
    header: Final = urlsafe_b64encode(b'{"alg":"none"}').rstrip(b"=").decode()
    payload: Final = urlsafe_b64encode(json.dumps({"key": key}, separators=(",", ":")).encode()).rstrip(b"=").decode()
    return f"{header}.{payload}.signature"


@dataclass(frozen=True, slots=True)
class FakeResponse:
    status_code: int
    payload: object = field(default_factory=lambda: {})
    headers: Mapping[str, str] = field(default_factory=lambda: {})
    text: str = ""

    def json(self) -> object:
        return self.payload


@dataclass(frozen=True, slots=True)
class FakeCommandResult:
    returncode: int
    stdout: str


@dataclass(slots=True)
class SyntheticStack:
    fail_at: str | None = None
    fail_occurrence: int = 1
    registration_secret: str | None = None
    wrong_ui_key_owner: bool = False
    retain_ui_key_after_delete: bool = False
    retain_grant_after_clear: bool = False
    before_request: Callable[[str], None] | None = None
    persistent_user: bool = False
    retain_toolset_after_delete: bool = False
    persistent_key: bool = False
    leave_task_key_after_delete: bool = False
    extra_user_id: str | None = None
    non_task_users: tuple[dict[str, object], ...] = ()
    page_mutation: Literal["missing", "duplicate", "reordered", "changed"] | None = None
    lifecycle_started: bool = False
    non_task_association_drift: bool = False
    server_drift: bool = False
    tool_drift: bool = False
    server_name_null: bool = False
    fill_null_server_name_after_baseline: bool = False
    access_group_drift: bool = False
    approval_status_drift: bool = False
    reverse_toolsets: bool = False
    duplicate_server: bool = False
    duplicate_tool: bool = False
    unstable_collection: Literal["toolsets", "servers", "tools"] | None = None
    reverse_tool_membership: bool = False
    mismatched_tool_identity: bool = False
    expose_list_object_permission: bool = False
    missing_catalog_member: bool = False
    server_missing_required_metadata: Literal["server_name", "alias"] | None = None
    missing_tool_metadata: Literal["server_name", "alias"] | None = None
    toolset_name_collision: bool = False
    post_create_toolset_name_collision: bool = False
    late_collision_exists: bool = False
    toolset_membership_drift: bool = False
    principal_tools: tuple[str, ...] = (DEFEND_TOOL,)
    user_info_id_mismatch: bool = False
    user_info_team_mismatch: bool = False
    post_create_task_user: bool = False
    post_create_task_key: bool = False
    post_create_association_drift: bool = False
    approved_identity_drift: (
        Literal[
            "server_id",
            "server_name",
            "alias",
            "transport",
            "auth",
            "approval",
            "allowlist",
            "access_groups",
            "allow_all_keys",
            "public",
            "disallowed_tools",
        ]
        | None
    ) = None
    call_counts: dict[str, int] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    user_id: str | None = None
    email: str | None = None
    password: str | None = None
    toolset_exists: bool = False
    principal_exists: bool = False
    grant_present: bool = False
    ui_key_exists: bool = False
    refresh_active: bool = False
    sessions: list[SyntheticSession] = field(default_factory=list)

    def session(self) -> SyntheticSession:
        created: Final = SyntheticSession(stack=self)
        self.sessions.append(created)
        return created

    def respond(
        self,
        session: SyntheticSession,
        method: Literal["GET", "POST", "DELETE"],
        path: str,
        *,
        headers: dict[str, str],
        json_body: dict[str, object],
        form_body: dict[str, str],
        params: dict[str, str],
    ) -> MaintenanceResponse:
        self.events.append(f"{method} {path}")
        if self.before_request is not None:
            self.before_request(path)
        self.call_counts[path] = self.call_counts.get(path, 0) + 1
        failure: Final = self._failure(path)
        if failure is not None:
            return failure
        if method == "GET" and path == "/user/list":
            assert params.get("sort_by") == "user_id"
            assert params.get("sort_order") == "asc"
            task_filter: Final = params.get("user_ids")
            task_visible: Final = self.principal_exists or (self.post_create_task_user and self.toolset_exists)
            include_task: Final = task_visible and (task_filter is None or task_filter == self.user_id)
            include_extra: Final = self.extra_user_id is not None and task_filter is None
            all_non_task: Final = self._non_task_users()
            total: Final = int(include_task) + int(include_extra) + (len(all_non_task) if task_filter is None else 0)
            task_users: Final[list[dict[str, object]]] = (
                [
                    {
                        "user_id": self.user_id,
                        "teams": tuple(),
                        "object_permission_id": "task-permission" if self.grant_present else None,
                        "key_count": int(
                            self.ui_key_exists
                            or self.persistent_key
                            or (self.post_create_task_key and self.toolset_exists)
                        ),
                    }
                ]
                if include_task
                else []
            )
            extra_users: Final[list[dict[str, object]]] = (
                [
                    {
                        "user_id": self.extra_user_id,
                        "teams": tuple(),
                        "object_permission_id": None,
                        "key_count": 0,
                    }
                ]
                if include_extra
                else []
            )
            page: Final = int(params.get("page", "1"))
            page_size: Final = int(params.get("page_size", "100"))
            start: Final = (page - 1) * page_size
            base_page: Final = list(all_non_task[start : start + page_size]) if task_filter is None else []
            mutate_now: Final = self.page_mutation in ("missing", "duplicate") or self.lifecycle_started
            paged_non_task: Final = (
                self._mutate_page(base_page, all_non_task)
                if task_filter is None and page == 2 and self.page_mutation is not None and mutate_now
                else base_page
            )
            source_users: Final = [
                *(task_users if page == 1 else []),
                *(extra_users if page == 1 else []),
                *paged_non_task,
            ]
            users: Final = [
                {**user, "object_permission": {"mcp_toolsets": ["unsupported-list-value"]}}
                if self.expose_list_object_permission and "object_permission" in user
                else {key: value for key, value in user.items() if key != "object_permission"}
                for user in source_users
            ]
            total_pages: Final = max(1, (total + page_size - 1) // page_size)
            return FakeResponse(
                200,
                {
                    "users": users,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                },
            )
        if method == "GET" and path == "/v1/mcp/server":
            server: Final[dict[str, object]] = {
                "server_id": "wrong-id" if self.approved_identity_drift == "server_id" else DEFEND_SERVER_ID,
                "server_name": (
                    DEFEND_NAME
                    if self.server_name_null and self.fill_null_server_name_after_baseline and self.lifecycle_started
                    else None
                    if self.server_name_null
                    else "defend_memory_changed"
                    if self.server_drift or self.approved_identity_drift == "server_name"
                    else DEFEND_NAME
                ),
                "alias": "wrong-alias" if self.approved_identity_drift == "alias" else DEFEND_NAME,
                "url": "http://host.docker.internal:48765/mcp",
                "transport": "sse" if self.approved_identity_drift == "transport" else "http",
                "auth_type": "oauth2" if self.approved_identity_drift == "auth" else "none",
                "allow_all_keys": self.approved_identity_drift == "allow_all_keys",
                "available_on_public_internet": self.approved_identity_drift == "public",
                "allowed_tools": [DEFEND_TOOL] if self.approved_identity_drift == "allowlist" else [],
                "disallowed_tools": ["other"] if self.approved_identity_drift == "disallowed_tools" else [],
                "mcp_access_groups": [
                    "changed-group"
                    if self.access_group_drift or self.approved_identity_drift == "access_groups"
                    else DEFEND_NAME
                ],
                "approval_status": (
                    "rejected" if self.approval_status_drift or self.approved_identity_drift == "approval" else "active"
                ),
            }
            if self.server_missing_required_metadata is not None:
                server[self.server_missing_required_metadata] = None
            stable_servers: Final = [server, *([server] if self.duplicate_server else [])]
            servers: Final = (
                [] if self.unstable_collection == "servers" and self.call_counts[path] % 2 == 0 else stable_servers
            )
            return FakeResponse(200, servers)
        if method == "GET" and path == "/v1/mcp/toolset":
            baseline_rows: Final[list[dict[str, object]]] = [
                {
                    "toolset_id": "baseline-b",
                    "toolset_name": "baseline-b",
                    "description": "baseline",
                    "tools": [],
                },
                {
                    "toolset_id": "baseline-a",
                    "toolset_name": "baseline-a",
                    "description": "baseline",
                    "tools": [],
                },
            ]
            ordered: Final = list(reversed(baseline_rows)) if self.reverse_toolsets else baseline_rows
            if self.toolset_name_collision or self.late_collision_exists:
                ordered.append(
                    {
                        "toolset_id": "collision-id",
                        "toolset_name": DEFEND_NAME,
                        "description": "collision",
                        "tools": [],
                    }
                )
            unsorted_rows: Final = [*ordered, *([self._toolset()] if self.toolset_exists else [])]
            unsorted_rows.sort(key=lambda row: str(row["toolset_id"]))
            if self.reverse_toolsets:
                unsorted_rows.reverse()
            rows: Final = (
                unsorted_rows[:-1]
                if self.unstable_collection == "toolsets" and self.call_counts[path] % 2 == 0
                else unsorted_rows
            )
            return FakeResponse(200, rows)
        if method == "GET" and path == "/mcp-rest/tools/list":
            if "toolset_name" in params:
                assert headers == {"x-litellm-api-key": UI_KEY}
                assert params == {"toolset_name": DEFEND_NAME}
                principal_tool_rows: Final = [self._tool(tool_name) for tool_name in self.principal_tools]
                return FakeResponse(200, {"tools": principal_tool_rows, "error": None})
            assert params == {
                "server_id": "wrong-id" if self.approved_identity_drift == "server_id" else DEFEND_SERVER_ID,
                "include_disabled_tools": "true",
            }
            tool_name: Final = "find-changed" if self.tool_drift else DEFEND_TOOL
            tool: Final = self._tool(tool_name)
            second_tool: Final[dict[str, object]] = {
                **tool,
                "name": "find-z",
            }
            stable_tools: Final = (
                [second_tool, tool]
                if self.reverse_tool_membership
                else ([] if self.missing_catalog_member else [tool, *([tool] if self.duplicate_tool else [])])
            )
            catalog_tool_rows: Final = (
                [] if self.unstable_collection == "tools" and self.call_counts[path] % 2 == 0 else stable_tools
            )
            return FakeResponse(
                200,
                {
                    "tools": catalog_tool_rows,
                    "error": None,
                },
            )
        if method == "GET" and path == f"/v1/mcp/toolset/{TOOLSET_ID}":
            if not self.toolset_exists:
                return FakeResponse(404)
            exact_toolset: Final = self._toolset()
            toolset: Final[dict[str, object]] = (
                {**exact_toolset, "tools": tuple()} if self.toolset_membership_drift else exact_toolset
            )
            return FakeResponse(200, toolset)
        if method == "GET" and path == "/key/info":
            if self.ui_key_exists and params.get("key") == UI_KEY:
                return FakeResponse(
                    200,
                    {
                        "info": {
                            "user_id": "other-user" if self.wrong_ui_key_owner else self.user_id,
                            "team_id": "litellm-dashboard",
                        }
                    },
                )
            return FakeResponse(404)
        if method == "GET" and path == "/key/list":
            total_count: Final = int(
                (self.ui_key_exists or self.persistent_key or (self.post_create_task_key and self.toolset_exists))
                and params.get("user_id") == self.user_id
            )
            return FakeResponse(200, {"total_count": total_count})
        if method == "POST" and path == "/v1/mcp/toolset":
            self.lifecycle_started = True
            self.toolset_exists = True
            self.late_collision_exists = self.post_create_toolset_name_collision
            return FakeResponse(201, self._toolset())
        if method == "POST" and path == "/user/new":
            self.user_id = str(json_body["user_id"])
            self.email = str(json_body["user_email"])
            permission: Final = json_body["object_permission"]
            assert isinstance(permission, dict)
            self.grant_present = permission["mcp_toolsets"] == [TOOLSET_ID]
            self.principal_exists = True
            return FakeResponse(200, {"user_id": self.user_id})
        if method == "POST" and path == "/user/update":
            if "password" in json_body:
                self.password = str(json_body["password"])
            if "object_permission" in json_body:
                updated_permission: Final = OBJECT_MAP_ADAPTER.validate_python(json_body["object_permission"])
                granted_toolsets: Final = updated_permission.get("mcp_toolsets")
                if not self.retain_grant_after_clear:
                    self.grant_present = granted_toolsets == [TOOLSET_ID]
            return FakeResponse(200, {"user_id": self.user_id})
        if method == "GET" and path == "/v2/user/info":
            requested_user_id: Final = params.get("user_id")
            non_task: Final = next(
                (user for user in self._non_task_users() if user["user_id"] == requested_user_id),
                None,
            )
            if non_task is not None:
                association: Final = OBJECT_MAP_ADAPTER.validate_python(non_task["object_permission"])
                return FakeResponse(
                    200,
                    {
                        "user_id": "hostile-id" if self.user_info_id_mismatch else non_task["user_id"],
                        "user_email": f"{non_task['user_id']}@example.invalid",
                        "user_role": "internal_user_viewer",
                        "models": [],
                        "object_permission": association,
                        "teams": ["hostile-team"] if self.user_info_team_mismatch else non_task["teams"],
                    },
                )
            return FakeResponse(
                200,
                {
                    "user_id": self.user_id,
                    "user_email": self.email,
                    "user_role": "internal_user_viewer",
                    "models": ["no-default-models"],
                    "object_permission": {
                        "mcp_servers": [],
                        "mcp_access_groups": [],
                        "mcp_tool_permissions": {},
                        "mcp_toolsets": [TOOLSET_ID] if self.grant_present else [],
                        "blocked_tools": [],
                        "vector_stores": [],
                        "agents": [],
                        "agent_access_groups": [],
                        "models": [],
                        "search_tools": [],
                        "mcp_tool_search_enabled": False,
                    },
                    "teams": [],
                },
            )
        if method == "GET" and path == "/user/info":
            return FakeResponse(
                200,
                {
                    "user_id": self.user_id,
                    "user_info": {
                        "user_id": self.user_id,
                        "user_email": self.email,
                        "user_role": "internal_user_viewer",
                        "models": ["no-default-models"],
                        "object_permission": {
                            "mcp_servers": [],
                            "mcp_access_groups": [],
                            "mcp_tool_permissions": {},
                            "mcp_toolsets": [TOOLSET_ID] if self.grant_present else [],
                            "blocked_tools": [],
                            "vector_stores": [],
                            "agents": [],
                            "agent_access_groups": [],
                            "models": [],
                            "search_tools": [],
                            "mcp_tool_search_enabled": False,
                        },
                    },
                    "keys": [],
                    "teams": [],
                },
            )
        if method == "POST" and path == "/login":
            assert form_body == {"username": self.email, "password": self.password}
            session.cookies.set_cookie(_cookie("token", _jwt_with_key(UI_KEY)))
            self.ui_key_exists = True
            return FakeResponse(303)
        if method == "POST" and path == "/register":
            secret: Final = {"client_secret": self.registration_secret} if self.registration_secret is not None else {}
            return FakeResponse(
                201,
                {
                    "client_id": CLIENT_ID,
                    "redirect_uris": json_body["redirect_uris"],
                    "token_endpoint_auth_method": "none",
                    **secret,
                },
            )
        if method == "GET" and path == "/authorize":
            assert params["code_challenge_method"] == "S256"
            assert params["resource"] == EXACT_RESOURCE
            assert any(cookie.name == "token" for cookie in session.cookies)
            session.cookies.set_cookie(_cookie(f"mcp_gateway_connect_flow_{FLOW}", "sealed-flow"))
            return FakeResponse(
                303, headers={"location": f"https://candidate.invalid/ui/connect?{urlencode({'connect_flow': FLOW})}"}
            )
        if method == "POST" and path == "/authorize/complete":
            assert form_body == {"flow": FLOW, "delivery": "manual"}
            assert any(cookie.name == "token" for cookie in session.cookies)
            callback: Final = f"http://127.0.0.1:39173/callback?{urlencode({'state': 'ignored', 'code': CODE})}"
            state: Final = next(value for event, value in session.authorize_params if event == "state")
            callback_with_state: Final = callback.replace("state=ignored", f"state={state}")
            return FakeResponse(200, text=f'<input value="{callback_with_state}">')
        if method == "POST" and path == "/token":
            assert form_body["code"] == CODE
            assert form_body["resource"] == EXACT_RESOURCE
            assert len(form_body["code_verifier"]) >= 43
            self.refresh_active = True
            return FakeResponse(
                200,
                {
                    "access_token": ACCESS_TOKEN,
                    "refresh_token": REFRESH_TOKEN,
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            )
        if method == "POST" and path in (EXACT_PATH, *CROSS_PATHS):
            assert headers["Authorization"] == f"Bearer {ACCESS_TOKEN}"
            _ = McpRequestBody.model_validate(json_body)
            return FakeResponse(200 if path == EXACT_PATH and self.principal_exists and self.grant_present else 401)
        if method == "POST" and path == "/revoke":
            assert form_body == {"token": REFRESH_TOKEN, "client_id": CLIENT_ID}
            self.refresh_active = False
            return FakeResponse(200)
        if method == "POST" and path == "/key/delete":
            assert headers["Authorization"] == f"Bearer {MASTER_KEY}"
            assert json_body == {"keys": [UI_KEY]}
            if not self.retain_ui_key_after_delete:
                self.ui_key_exists = False
            if self.leave_task_key_after_delete:
                self.persistent_key = True
            return FakeResponse(200)
        if method == "POST" and path == "/user/delete":
            assert not self.grant_present
            if not self.persistent_user:
                self.principal_exists = False
            return FakeResponse(200, 1)
        if method == "DELETE" and path == f"/v1/mcp/toolset/{TOOLSET_ID}":
            assert not self.principal_exists
            if not self.retain_toolset_after_delete:
                self.toolset_exists = False
            return FakeResponse(202)
        return FakeResponse(404)

    def _failure(self, path: str) -> FakeResponse | None:
        if self.fail_at != path or self.call_counts[path] != self.fail_occurrence:
            return None
        self.fail_at = None
        return FakeResponse(500)

    def _non_task_users(self) -> tuple[dict[str, object], ...]:
        if not self.non_task_users:
            return ()
        if not self.lifecycle_started or not (self.non_task_association_drift or self.post_create_association_drift):
            return self.non_task_users
        first: Final = self.non_task_users[0]
        changed: Final = {**first, "object_permission": {"mcp_toolsets": ["changed-toolset"]}}
        return (changed, *self.non_task_users[1:])

    def _mutate_page(
        self, page: list[dict[str, object]], all_users: tuple[dict[str, object], ...]
    ) -> list[dict[str, object]]:
        if not page:
            return page
        match self.page_mutation:
            case "missing":
                return page[1:]
            case "duplicate":
                return [{**all_users[99]}, *page[1:]]
            case "reordered":
                return list(reversed(page))
            case "changed":
                return [{**page[0], "teams": ["changed-boundary-team"]}, *page[1:]]
            case None:
                return page

    @staticmethod
    def _toolset() -> dict[str, object]:
        return {
            "toolset_id": TOOLSET_ID,
            "toolset_name": DEFEND_NAME,
            "description": "Synthetic maintenance lifecycle",
            "tools": [{"server_id": DEFEND_SERVER_ID, "tool_name": DEFEND_TOOL}],
        }

    def _tool(self, tool_name: str) -> dict[str, object]:
        metadata: Final[dict[str, object]] = {
            "server_id": "wrong-id" if self.approved_identity_drift == "server_id" else DEFEND_SERVER_ID,
            "server_name": "mismatched" if self.mismatched_tool_identity else DEFEND_NAME,
            "alias": DEFEND_NAME,
        }
        if self.missing_tool_metadata is not None:
            metadata.pop(self.missing_tool_metadata)
        return {"name": tool_name, "mcp_info": metadata}


def _users(count: int = 102) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "user_id": f"non-task-{index:03d}",
            "teams": [f"team-{index % 3}"],
            "key_count": index % 2,
            "object_permission": {"mcp_toolsets": [f"toolset-{index % 5}"]},
        }
        for index in range(count)
    )


@dataclass(slots=True)
class SyntheticSession:
    stack: SyntheticStack
    cookies: CookieJar = field(default_factory=CookieJar)
    closed: bool = False
    authorize_params: list[tuple[str, str]] = field(default_factory=list)

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
        assert not follow_redirects
        return self.stack.respond(
            self,
            "POST",
            path,
            headers=dict(headers or {}),
            json_body=dict(json or {}),
            form_body=dict(data or {}),
            params={},
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
        assert not follow_redirects
        if path == "/authorize":
            self.authorize_params = list((params or {}).items())
        return self.stack.respond(
            self,
            "GET",
            path,
            headers=dict(headers or {}),
            json_body={},
            form_body={},
            params=dict(params or {}),
        )

    def delete(
        self,
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float,
    ) -> MaintenanceResponse:
        return self.stack.respond(
            self,
            "DELETE",
            path,
            headers=dict(headers or {}),
            json_body={},
            form_body={},
            params={},
        )

    def close(self) -> None:
        self.closed = True


def _zero_clock() -> float:
    return 0.0


def _wrong_image() -> str:
    raise MaintenanceClientError("disposable candidate running image identity mismatch")


def _client(stack: SyntheticStack, *, clock: Clock = _zero_clock) -> DcrMaintenanceClient:
    return DcrMaintenanceClient(
        session_factory=stack.session,
        candidate=ExactCandidate(
            inspect_image_id=lambda: EXPECTED_IMAGE,
            master_key=MASTER_KEY,
            toolset_name=DEFEND_NAME,
            toolset_description="Synthetic maintenance lifecycle",
            tool=ToolsetTool(server_id=DEFEND_SERVER_ID, tool_name=DEFEND_TOOL),
            exact_resource=EXACT_RESOURCE,
            cross_audience_paths=CROSS_PATHS,
        ),
        clock=clock,
    )


def _candidate_from_inspector(stack: SyntheticStack, inspector: DisposableCandidateInspector) -> DcrMaintenanceClient:
    client: Final = _client(stack)
    return DcrMaintenanceClient(
        session_factory=stack.session,
        candidate=ExactCandidate(
            inspect_image_id=inspector.inspect,
            master_key=client.candidate.master_key,
            toolset_name=client.candidate.toolset_name,
            toolset_description=client.candidate.toolset_description,
            tool=client.candidate.tool,
            exact_resource=client.candidate.exact_resource,
            cross_audience_paths=client.candidate.cross_audience_paths,
        ),
    )


def _assert_destroyed(stack: SyntheticStack) -> None:
    assert not stack.toolset_exists
    assert not stack.principal_exists
    assert not stack.grant_present
    assert not stack.ui_key_exists
    assert not stack.refresh_active
    assert all(session.closed and len(session.cookies) == 0 for session in stack.sessions)


class TestDcrMaintenanceClient:
    @pytest.mark.parametrize(
        "field",
        (
            "server_id",
            "server_name",
            "alias",
            "transport",
            "auth",
            "approval",
            "allowlist",
            "access_groups",
            "allow_all_keys",
            "public",
            "disallowed_tools",
        ),
    )
    def test_exact_approved_defend_identity_is_pinned(
        self,
        field: Literal[
            "server_id",
            "server_name",
            "alias",
            "transport",
            "auth",
            "approval",
            "allowlist",
            "access_groups",
            "allow_all_keys",
            "public",
            "disallowed_tools",
        ],
    ) -> None:
        stack: Final = SyntheticStack(approved_identity_drift=field)

        with pytest.raises(MaintenanceClientError):
            _ = _client(stack).validate()

        assert "POST /v1/mcp/toolset" not in stack.events

    def test_candidate_contract_rejects_non_defend_member_before_session(self) -> None:
        stack: Final = SyntheticStack()
        client: Final = _client(stack)
        wrong: Final = DcrMaintenanceClient(
            session_factory=stack.session,
            candidate=ExactCandidate(
                inspect_image_id=client.candidate.inspect_image_id,
                master_key=client.candidate.master_key,
                toolset_name=client.candidate.toolset_name,
                toolset_description=client.candidate.toolset_description,
                tool=ToolsetTool(server_id=DEFEND_SERVER_ID, tool_name="not-find"),
                exact_resource=client.candidate.exact_resource,
                cross_audience_paths=client.candidate.cross_audience_paths,
            ),
        )

        with pytest.raises(MaintenanceClientError, match="approved Defend toolset contract"):
            _ = wrong.validate()

        assert stack.sessions == []

    @pytest.mark.parametrize("missing", ("server_name", "alias"))
    def test_catalog_preflight_requires_exact_server_id_name_and_alias_metadata(
        self, missing: Literal["server_name", "alias"]
    ) -> None:
        stack: Final = SyntheticStack(
            missing_tool_metadata=missing,
            server_missing_required_metadata=missing,
        )

        with pytest.raises(MaintenanceClientError, match="approved Defend server identity"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists
        assert "POST /user/new" not in stack.events

    def test_catalog_preflight_requires_exact_candidate_member(self) -> None:
        stack: Final = SyntheticStack(missing_catalog_member=True)

        with pytest.raises(MaintenanceClientError, match="candidate toolset member"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists
        assert "POST /user/new" not in stack.events

    def test_baseline_name_collision_blocks_creation(self) -> None:
        stack: Final = SyntheticStack(toolset_name_collision=True)

        with pytest.raises(MaintenanceClientError, match="collided with disposable baseline"):
            _ = _client(stack).validate()

        assert "POST /v1/mcp/toolset" not in stack.events
        assert "POST /user/new" not in stack.events

    def test_post_create_readback_blocks_principal_on_membership_drift(self) -> None:
        stack: Final = SyntheticStack(toolset_membership_drift=True)

        with pytest.raises(MaintenanceClientError, match="toolset ownership"):
            _ = _client(stack).validate()

        assert "POST /user/new" not in stack.events

    def test_post_create_relist_blocks_principal_on_late_name_collision(self) -> None:
        stack: Final = SyntheticStack(post_create_toolset_name_collision=True)

        with pytest.raises(MaintenanceClientError, match="toolset ownership"):
            _ = _client(stack).validate()

        assert "POST /user/new" not in stack.events
        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" in stack.events
        assert not stack.toolset_exists
        assert stack.late_collision_exists
        assert "DELETE /v1/mcp/toolset/collision-id" not in stack.events

    def test_direct_membership_drift_deletes_proven_task_row(self) -> None:
        stack: Final = SyntheticStack(toolset_membership_drift=True)

        with pytest.raises(MaintenanceClientError, match="toolset ownership"):
            _ = _client(stack).validate()

        assert "POST /user/new" not in stack.events
        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" in stack.events
        assert not stack.toolset_exists

    @pytest.mark.parametrize("mutation", ("user", "key", "association"))
    def test_pre_principal_identity_user_key_or_association_mutation_blocks_grant(self, mutation: str) -> None:
        stack: Final = SyntheticStack(
            non_task_users=_users() if mutation == "association" else (),
            post_create_task_user=mutation == "user",
            post_create_task_key=mutation == "key",
            post_create_association_drift=mutation == "association",
        )

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        if mutation == "key":
            assert "POST /user/new" in stack.events
            assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
            assert stack.toolset_exists
        else:
            assert "POST /user/new" not in stack.events
            assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
            assert stack.toolset_exists

    @pytest.mark.parametrize("resolved", ((), (DEFEND_TOOL, "extra-tool"), ("extra-tool",)))
    def test_principal_context_must_resolve_exactly_one_intended_tool_before_dcr(
        self, resolved: tuple[str, ...]
    ) -> None:
        stack: Final = SyntheticStack(principal_tools=resolved)

        with pytest.raises(MaintenanceClientError, match="exactly the intended one tool"):
            _ = _client(stack).validate()

        assert "POST /register" not in stack.events
        _assert_destroyed(stack)

    @pytest.mark.parametrize("fault", ("id", "teams"))
    def test_hostile_user_info_relation_disagreement_fails_closed(self, fault: str) -> None:
        stack: Final = SyntheticStack(
            non_task_users=_users(),
            user_info_id_mismatch=fault == "id",
            user_info_team_mismatch=fault == "teams",
        )

        with pytest.raises(MaintenanceClientError, match="relation-bearing user info disagree"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    def test_real_api_shape_resolves_relations_from_user_info_not_user_list(self) -> None:
        stack: Final = SyntheticStack(non_task_users=_users())

        assert _client(stack).validate().cleanup_complete

        assert stack.call_counts["/v2/user/info"] >= len(stack.non_task_users) * 2
        _assert_destroyed(stack)

    def test_user_list_relation_field_is_ignored_in_favor_of_supported_user_info(self) -> None:
        stack: Final = SyntheticStack(non_task_users=_users(), expose_list_object_permission=True)

        assert _client(stack).validate().cleanup_complete

        _assert_destroyed(stack)

    def test_multi_page_users_assemble_complete_canonical_associations(self) -> None:
        stack: Final = SyntheticStack(non_task_users=_users())

        status: Final = _client(stack).validate()

        assert status.cleanup_complete
        assert "GET /user/list" in stack.events
        assert stack.call_counts["/user/list"] >= 6
        _assert_destroyed(stack)

    @pytest.mark.parametrize("mutation", ("missing", "duplicate", "reordered", "changed"))
    def test_multi_page_user_boundary_mutation_fails_closed(
        self, mutation: Literal["missing", "duplicate", "reordered", "changed"]
    ) -> None:
        stack: Final = SyntheticStack(non_task_users=_users(), page_mutation=mutation)

        with pytest.raises(MaintenanceClientError):
            _ = _client(stack).validate()

        if mutation in ("missing", "duplicate"):
            assert not stack.toolset_exists
        else:
            assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
            assert stack.toolset_exists
        assert stack.sessions[0].closed

    def test_non_task_toolset_association_drift_blocks_restoration(self) -> None:
        stack: Final = SyntheticStack(non_task_users=_users(), non_task_association_drift=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    @pytest.mark.parametrize("drift", ("server", "tool"))
    def test_mcp_server_or_upstream_tool_membership_drift_blocks_restoration(self, drift: str) -> None:
        stack: Final = SyntheticStack(server_drift=drift == "server", tool_drift=drift == "tool")

        def before_request(path: str) -> None:
            if path == "/revoke":
                stack.server_drift = drift == "server"
                stack.tool_drift = drift == "tool"

        stack.server_drift = False
        stack.tool_drift = False
        stack.before_request = before_request

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    def test_nullable_server_name_is_preserved_and_alias_is_not_substituted(self) -> None:
        stack: Final = SyntheticStack(server_name_null=True)

        with pytest.raises(MaintenanceClientError, match="approved Defend server identity"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    def test_null_server_name_to_alias_value_drift_is_detected(self) -> None:
        stack: Final = SyntheticStack(server_name_null=True, fill_null_server_name_after_baseline=True)

        with pytest.raises(MaintenanceClientError, match="approved Defend server identity"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    @pytest.mark.parametrize("field", ("mcp_access_groups", "approval_status"))
    def test_governed_server_field_drift_blocks_restoration(self, field: str) -> None:
        stack: Final = SyntheticStack()

        def before_request(path: str) -> None:
            if path == "/revoke":
                stack.access_group_drift = field == "mcp_access_groups"
                stack.approval_status_drift = field == "approval_status"

        stack.before_request = before_request

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    @pytest.mark.parametrize("collection", ("toolsets", "servers", "tools"))
    def test_unpaginated_collection_requires_canonical_unique_complete_rows(self, collection: str) -> None:
        stack: Final = SyntheticStack(
            reverse_toolsets=collection == "toolsets",
            duplicate_server=collection == "servers",
            duplicate_tool=collection == "tools",
        )

        with pytest.raises(MaintenanceClientError, match="collection"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    def test_upstream_tool_membership_requires_canonical_order(self) -> None:
        stack: Final = SyntheticStack(reverse_tool_membership=True)

        with pytest.raises(MaintenanceClientError, match="tool collection"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    def test_upstream_tool_identity_must_match_server_identity_and_name(self) -> None:
        stack: Final = SyntheticStack(mismatched_tool_identity=True)

        with pytest.raises(MaintenanceClientError, match="identity does not match"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    @pytest.mark.parametrize("collection", ("toolsets", "servers", "tools"))
    def test_unpaginated_collection_requires_cardinality_and_digest_stability(
        self, collection: Literal["toolsets", "servers", "tools"]
    ) -> None:
        stack: Final = SyntheticStack(unstable_collection=collection)

        with pytest.raises(MaintenanceClientError, match="unstable"):
            _ = _client(stack).validate()

        assert not stack.toolset_exists

    def test_concrete_inspector_binds_running_image_and_mounted_config(self) -> None:
        config_path: Final = Path(__file__).with_name("disposable_candidate_config.yaml")
        config_digest: Final = hashlib.sha256(config_path.read_bytes()).hexdigest()
        calls: list[tuple[str, ...]] = []

        def run(arguments: tuple[str, ...]) -> FakeCommandResult:
            calls.append(arguments)
            if arguments[:2] == ("docker", "exec"):
                return FakeCommandResult(0, f"{config_digest}  /app/config.yaml\n")
            template: Final = arguments[-2]
            return FakeCommandResult(0, "true\n" if template == "{{.State.Running}}" else f"{EXPECTED_IMAGE}\n")

        inspector: Final = DisposableCandidateInspector(
            container_name="task018-disposable",
            config_path=config_path,
            container_config_path="/app/config.yaml",
            expected_image_id=EXPECTED_IMAGE,
            expected_config_sha256=config_digest,
            command_runner=run,
        )
        stack: Final = SyntheticStack()

        assert _candidate_from_inspector(stack, inspector).validate().cleanup_complete
        assert calls == [
            (
                "docker",
                "inspect",
                "--type",
                "container",
                "--format",
                "{{.State.Running}}",
                "task018-disposable",
            ),
            (
                "docker",
                "inspect",
                "--type",
                "container",
                "--format",
                "{{.Image}}",
                "task018-disposable",
            ),
            ("docker", "exec", "task018-disposable", "sha256sum", "/app/config.yaml"),
        ]

    def test_disposable_builder_binds_base_url_inspector_and_exact_resource(self) -> None:
        config_path: Final = Path(__file__).with_name("disposable_candidate_config.yaml")
        config_digest: Final = hashlib.sha256(config_path.read_bytes()).hexdigest()
        inspector: Final = DisposableCandidateInspector(
            container_name="task018-disposable",
            config_path=config_path,
            container_config_path="/app/config.yaml",
            expected_image_id=EXPECTED_IMAGE,
            expected_config_sha256=config_digest,
            command_runner=lambda _: FakeCommandResult(1, ""),
        )

        session_factory, candidate = exact_candidate_from_disposable(
            base_url="https://candidate.invalid/",
            master_key=MASTER_KEY,
            inspector=inspector,
            toolset_name=DEFEND_NAME,
            toolset_description="Synthetic maintenance lifecycle",
            tool=ToolsetTool(server_id=DEFEND_SERVER_ID, tool_name=DEFEND_TOOL),
            cross_audience_paths=CROSS_PATHS,
        )
        session: Final = session_factory()

        assert candidate.exact_resource == EXACT_RESOURCE
        assert len(session.cookies) == 0
        session.close()

    def test_concrete_inspector_rejects_config_mismatch_before_session(self) -> None:
        config_path: Final = Path(__file__).with_name("disposable_candidate_config.yaml")
        stack: Final = SyntheticStack()
        inspector: Final = DisposableCandidateInspector(
            container_name="task018-disposable",
            config_path=config_path,
            container_config_path="/app/config.yaml",
            expected_image_id=EXPECTED_IMAGE,
            expected_config_sha256="0" * 64,
            command_runner=lambda _: FakeCommandResult(0, "unused"),
        )

        with pytest.raises(MaintenanceClientError, match="config identity mismatch"):
            _ = _candidate_from_inspector(stack, inspector).validate()

        assert stack.sessions == []

    def test_concrete_inspector_rejects_running_image_mismatch_before_session(self) -> None:
        config_path: Final = Path(__file__).with_name("disposable_candidate_config.yaml")
        config_digest: Final = hashlib.sha256(config_path.read_bytes()).hexdigest()

        def run(arguments: tuple[str, ...]) -> FakeCommandResult:
            template: Final = arguments[-2]
            return FakeCommandResult(0, "true\n" if template == "{{.State.Running}}" else "sha256:wrong\n")

        inspector: Final = DisposableCandidateInspector(
            container_name="task018-disposable",
            config_path=config_path,
            container_config_path="/app/config.yaml",
            expected_image_id=EXPECTED_IMAGE,
            expected_config_sha256=config_digest,
            command_runner=run,
        )
        stack: Final = SyntheticStack()

        with pytest.raises(MaintenanceClientError, match="running image identity mismatch"):
            _ = _candidate_from_inspector(stack, inspector).validate()

        assert stack.sessions == []

    def test_http_adapter_owns_one_in_memory_cookie_jar(self) -> None:
        session: Final = httpx_session_factory("https://candidate.invalid")()

        session.cookies.set_cookie(_cookie("token", _jwt_with_key(UI_KEY)))

        assert len(session.cookies) == 1
        assert not hasattr(session.cookies, "filename")
        session.cookies.clear()
        session.close()

    def test_status_only_evidence_omits_candidate_and_all_credentials(self) -> None:
        stack: Final = SyntheticStack()

        evidence: Final = _client(stack).validate().evidence()

        assert "image_id" not in evidence
        assert all(secret not in repr(evidence) for secret in (*SENSITIVE_VALUES, EXPECTED_IMAGE))
        _assert_destroyed(stack)

    def test_unexpected_client_secret_is_refused_without_disclosure(self) -> None:
        stack: Final = SyntheticStack(registration_secret="returned-secret-must-not-leak")

        with pytest.raises(MaintenanceClientError) as exc_info:
            _ = _client(stack).validate()

        assert "returned-secret-must-not-leak" not in str(exc_info.value)
        _assert_destroyed(stack)

    def test_unowned_ui_key_is_never_deleted_and_cleanup_escalates(self) -> None:
        stack: Final = SyntheticStack(wrong_ui_key_owner=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration") as exc_info:
            _ = _client(stack).validate()

        assert UI_KEY not in str(exc_info.value)
        assert "POST /key/delete" not in stack.events
        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.ui_key_exists
        assert stack.toolset_exists

    def test_ui_key_post_delete_presence_blocks_toolset_and_escalates(self) -> None:
        stack: Final = SyntheticStack(retain_ui_key_after_delete=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.ui_key_exists
        assert stack.toolset_exists

    def test_grant_readback_failure_blocks_principal_and_toolset_delete(self) -> None:
        stack: Final = SyntheticStack(retain_grant_after_clear=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert "POST /user/delete" not in stack.events
        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.principal_exists
        assert stack.toolset_exists

    def test_baseline_failure_still_closes_and_clears_the_session(self) -> None:
        stack: Final = SyntheticStack(fail_at="/user/list")

        with pytest.raises(MaintenanceClientError):
            _ = _client(stack).validate()

        _assert_destroyed(stack)

    def test_one_process_completes_dcr_audience_and_cleanup_without_persistence(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        stack: Final = SyntheticStack()

        status: Final = _client(stack).validate()

        assert status.email_login
        assert status.cookie_count_after_login >= 1
        assert status.pkce_method == "S256"
        assert status.public_client
        assert status.exact_audience_status == 200
        assert status.cross_audience_statuses == (401, 401, 401)
        assert status.refresh_revoked
        assert status.ui_key_deleted
        assert status.client_destroyed
        assert status.principal_deleted
        assert status.toolset_deleted
        assert status.cookies_cleared
        assert status.restoration_verified
        assert status.cleanup_complete
        assert all(secret not in repr(status.evidence()) for secret in SENSITIVE_VALUES)
        assert len(stack.sessions) == 2
        post_create_list_index: Final = stack.events.index("GET /v1/mcp/toolset", 5)
        post_create_id_index: Final = stack.events.index(f"GET /v1/mcp/toolset/{TOOLSET_ID}")
        principal_create_index: Final = stack.events.index("POST /user/new")
        login_index: Final = stack.events.index("POST /login")
        principal_tool_index: Final = stack.events.index("GET /mcp-rest/tools/list", login_index)
        register_index: Final = stack.events.index("POST /register")
        assert post_create_list_index < post_create_id_index < principal_create_index
        assert login_index < principal_tool_index < register_index
        key_delete_index: Final = stack.events.index("POST /key/delete")
        grant_clear_index: Final = stack.events.index("POST /user/update", key_delete_index)
        principal_delete_index: Final = stack.events.index("POST /user/delete")
        toolset_delete_index: Final = stack.events.index(f"DELETE /v1/mcp/toolset/{TOOLSET_ID}")
        pre_toolset_restore_index: Final = stack.events.index("GET /v1/mcp/server", principal_delete_index)
        assert (
            key_delete_index
            < grant_clear_index
            < principal_delete_index
            < pre_toolset_restore_index
            < toolset_delete_index
        )
        _assert_destroyed(stack)
        captured: Final = capsys.readouterr()
        assert all(secret not in captured.out and secret not in captured.err for secret in SENSITIVE_VALUES)

    @pytest.mark.parametrize("fail_at", ("/login", "/authorize", "/token", EXACT_PATH))
    def test_failure_paths_destroy_every_created_resource(self, fail_at: str) -> None:
        stack: Final = SyntheticStack(fail_at=fail_at)

        with pytest.raises(MaintenanceClientError):
            _ = _client(stack).validate()

        _assert_destroyed(stack)

    @pytest.mark.parametrize(
        "fail_at,fail_occurrence",
        (
            ("/key/delete", 1),
            ("/user/update", 2),
            ("/user/delete", 1),
        ),
    )
    def test_cleanup_action_failure_blocks_toolset_delete_and_escalates(
        self, fail_at: str, fail_occurrence: int
    ) -> None:
        stack: Final = SyntheticStack(fail_at=fail_at, fail_occurrence=fail_occurrence)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    def test_toolset_delete_failure_runs_restoration_and_escalates(self) -> None:
        stack: Final = SyntheticStack()

        def arm_delete_failure(path: str) -> None:
            if path == "/user/delete":
                stack.fail_at = f"/v1/mcp/toolset/{TOOLSET_ID}"
                stack.fail_occurrence = stack.call_counts.get(stack.fail_at, 0) + 1

        stack.before_request = arm_delete_failure

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert stack.call_counts["/user/list"] >= 3
        assert stack.call_counts["/v1/mcp/toolset"] >= 2
        assert stack.toolset_exists

    def test_toolset_post_delete_presence_escalates_restoration_failure(self) -> None:
        stack: Final = SyntheticStack(retain_toolset_after_delete=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert stack.toolset_exists
        assert stack.call_counts[f"/v1/mcp/toolset/{TOOLSET_ID}"] >= 1

    def test_restoration_failure_is_checked_after_cleanup_and_escalates(self) -> None:
        stack: Final = SyntheticStack(persistent_user=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert stack.call_counts["/user/list"] >= 3
        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.principal_exists
        assert stack.toolset_exists

    def test_non_task_baseline_drift_blocks_toolset_delete(self) -> None:
        stack: Final = SyntheticStack()

        def before_request(path: str) -> None:
            if path == "/revoke":
                stack.extra_user_id = "unexpected-non-task-user"

        stack.before_request = before_request

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    def test_persistent_task_key_blocks_toolset_delete_and_escalates(self) -> None:
        stack: Final = SyntheticStack(leave_task_key_after_delete=True)

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = _client(stack).validate()

        assert f"DELETE /v1/mcp/toolset/{TOOLSET_ID}" not in stack.events
        assert stack.toolset_exists

    def test_deadline_is_checked_immediately_before_authorize(self) -> None:
        stack: Final = SyntheticStack()
        expired: bool = False

        def before_request(path: str) -> None:
            nonlocal expired
            if path == "/register":
                expired = True

        stack.before_request = before_request

        def clock() -> float:
            return 11.0 if expired else 0.0

        with pytest.raises(MaintenanceDeadlineExceeded):
            _ = _client(stack, clock=clock).validate(deadline_seconds=10.0)

        assert "GET /authorize" not in stack.events
        _assert_destroyed(stack)

    def test_deadline_is_checked_immediately_before_complete(self) -> None:
        stack: Final = SyntheticStack()
        expired: bool = False

        def before_request(path: str) -> None:
            nonlocal expired
            if path == "/authorize":
                expired = True

        stack.before_request = before_request

        def clock() -> float:
            return 11.0 if expired else 0.0

        with pytest.raises(MaintenanceDeadlineExceeded):
            _ = _client(stack, clock=clock).validate(deadline_seconds=10.0)

        assert "GET /authorize" in stack.events
        assert "POST /authorize/complete" not in stack.events
        _assert_destroyed(stack)

    def test_deadline_failure_still_runs_supported_restoration_reads(self) -> None:
        stack: Final = SyntheticStack()
        expired: bool = False

        def before_request(path: str) -> None:
            nonlocal expired
            if path == "/register":
                expired = True

        stack.before_request = before_request

        with pytest.raises(MaintenanceDeadlineExceeded):
            _ = _client(stack, clock=lambda: 11.0 if expired else 0.0).validate(deadline_seconds=10.0)

        assert stack.call_counts["/user/list"] >= 4
        assert stack.call_counts["/v1/mcp/toolset"] >= 2
        assert stack.call_counts["/v1/mcp/server"] >= 2
        _assert_destroyed(stack)

    def test_real_client_observes_cancellation_and_restores_every_resource(self) -> None:
        stack: Final = SyntheticStack()
        cancelled: bool = False

        def before_request(path: str) -> None:
            nonlocal cancelled
            if path == "/login":
                cancelled = True

        stack.before_request = before_request
        base: Final = _client(stack)
        client: Final = DcrMaintenanceClient(
            session_factory=base.session_factory,
            candidate=base.candidate,
            timeout_seconds=base.timeout_seconds,
            clock=base.clock,
            cancelled=lambda: cancelled,
        )

        with pytest.raises(MaintenanceClientError, match="cleanup or restoration"):
            _ = client.validate()

        assert "POST /register" not in stack.events
        assert stack.call_counts["/user/list"] >= 4
        assert not stack.principal_exists
        assert stack.ui_key_exists
        assert stack.toolset_exists

    def test_deadline_failure_runs_cleanup_with_a_reserved_cleanup_budget(self) -> None:
        stack: Final = SyntheticStack()
        expired: bool = False

        def before_request(path: str) -> None:
            nonlocal expired
            if path == "/register":
                expired = True

        stack.before_request = before_request

        with pytest.raises(MaintenanceDeadlineExceeded):
            _ = _client(stack, clock=lambda: 11.0 if expired else 0.0).validate(deadline_seconds=10.0)

        _assert_destroyed(stack)

    def test_rejects_non_exact_candidate_before_opening_a_session(self) -> None:
        stack: Final = SyntheticStack()
        client: Final = _client(stack)
        mismatched: Final = DcrMaintenanceClient(
            session_factory=stack.session,
            candidate=ExactCandidate(
                inspect_image_id=_wrong_image,
                master_key=client.candidate.master_key,
                toolset_name=client.candidate.toolset_name,
                toolset_description=client.candidate.toolset_description,
                tool=client.candidate.tool,
                exact_resource=client.candidate.exact_resource,
                cross_audience_paths=client.candidate.cross_audience_paths,
            ),
        )

        with pytest.raises(MaintenanceClientError, match="running image identity mismatch"):
            _ = mismatched.validate()

        assert stack.sessions == []
