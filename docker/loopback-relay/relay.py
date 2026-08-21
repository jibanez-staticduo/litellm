from __future__ import annotations

import json
import os
import socket
import socketserver
import stat
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from http import HTTPStatus
from typing import Final, Protocol

LISTEN_HOST: Final = "0.0.0.0"
LISTEN_PORT: Final = 8080
COMPLETION_URL: Final = "http://litellm:4000/v1/mcp/loopback-oauth/complete"
READY_URL: Final = "http://litellm:4000/v1/mcp/loopback-oauth/ready"
SECRET_FILE_ENV: Final = "LOOPBACK_RELAY_SECRET_FILE"
DEFAULT_SECRET_FILE: Final = "/run/secrets/litellm_loopback_oauth_relay"
MAX_REQUEST_TARGET: Final = 4096
MAX_HEADER_BYTES: Final = 8192
MAX_CONNECTIONS: Final = 32
CLIENT_READ_TIMEOUT_SECONDS: Final = 2.0
MAX_RESPONSE_BODY: Final = 4096
UPSTREAM_TIMEOUT_SECONDS: Final = 5.0
LOVABLE_ISSUER: Final = "https://lovable.dev/oauth"
LOVABLE_SCOPES: Final = frozenset(
    ("offline", "projects:read", "projects:write", "projects:create", "workspaces:read", "workspaces:write")
)
MAX_SCOPE_LENGTH: Final = 512

PAGE_HEADERS: Final = {
    "Cache-Control": "no-store",
    "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
}


@dataclass(frozen=True, slots=True)
class Page:
    status: HTTPStatus
    title: str
    message: str


CONNECTED: Final = Page(HTTPStatus.OK, "Connection complete", "You can close this window and return to LiteLLM.")
DENIED: Final = Page(HTTPStatus.OK, "Connection not completed", "No credential was saved. You can close this window.")
INVALID: Final = Page(HTTPStatus.BAD_REQUEST, "Invalid request", "Start a new connection from LiteLLM and try again.")
EXPIRED: Final = Page(HTTPStatus.GONE, "Connection expired", "Start a new connection from LiteLLM and try again.")
RETRY: Final = Page(
    HTTPStatus.BAD_GATEWAY, "Connection unavailable", "Start a new connection from LiteLLM and try again."
)
NOT_FOUND: Final = Page(HTTPStatus.NOT_FOUND, "Not found", "This endpoint does not exist.")
READY: Final = Page(HTTPStatus.OK, "Tunnel ready", "Return to LiteLLM to continue.")


class Forwarder(Protocol):
    def complete(self, payload: Mapping[str, str]) -> Page: ...

    def ready(self, transaction_id: str) -> Page: ...


def load_secret(path: str) -> str:
    descriptor: Final = os.open(path, os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW)
    try:
        metadata: Final = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 4096:
            raise ValueError("relay secret file is invalid")
        raw: Final = os.read(descriptor, 4097)
    finally:
        os.close(descriptor)
    secret: Final = raw.decode("utf-8").strip()
    if len(secret) < 32 or len(secret) > 4096 or any(character.isspace() for character in secret):
        raise ValueError("relay secret is invalid")
    return secret


def parse_callback(target: str) -> Mapping[str, str] | None:
    if len(target) > MAX_REQUEST_TARGET or not target.startswith("/callback?"):
        return None
    if not _valid_percent_encoding(target):
        return None
    parsed: Final = urllib.parse.urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.path != "/callback" or parsed.fragment:
        return None
    try:
        pairs: Final = urllib.parse.parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
            encoding="utf-8",
            errors="strict",
            max_num_fields=5,
            separator="&",
        )
    except (UnicodeDecodeError, ValueError):
        return None
    if len({key for key, _ in pairs}) != len(pairs):
        return None
    values: Final = dict(pairs)
    keys: Final = frozenset(values)
    success: Final = frozenset(("state", "code")) <= keys and keys <= frozenset(("state", "code", "iss", "scope"))
    error: Final = keys in (
        frozenset(("state", "error")),
        frozenset(("state", "error", "error_description")),
    )
    if not success and not error:
        return None
    state: Final = values["state"]
    if not 43 <= len(state) <= 128 or _contains_control(state):
        return None
    if success:
        code: Final = values["code"]
        if not 1 <= len(code) <= 2048 or _contains_control(code):
            return None
        issuer: Final = values.get("iss")
        if issuer is not None and issuer != LOVABLE_ISSUER:
            return None
        scope: Final = values.get("scope")
        if scope is not None and not _valid_scope(scope):
            return None
        return {"state": state, "code": code}
    oauth_error: Final = values["error"]
    description: Final = values.get("error_description", "")
    valid_error: Final = 1 <= len(oauth_error) <= 128 and not _contains_control(oauth_error)
    valid_description: Final = len(description) <= 512 and not _contains_control(description)
    return values if valid_error and valid_description else None


def parse_ready(target: str) -> str | None:
    if len(target) > MAX_REQUEST_TARGET or not target.startswith("/ready?") or not _valid_percent_encoding(target):
        return None
    parsed: Final = urllib.parse.urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.path != "/ready" or parsed.fragment:
        return None
    try:
        pairs: Final = urllib.parse.parse_qsl(parsed.query, strict_parsing=True, max_num_fields=1)
    except ValueError:
        return None
    if len(pairs) != 1 or pairs[0][0] != "transaction_id":
        return None
    transaction_id: Final = pairs[0][1]
    return transaction_id if 43 <= len(transaction_id) <= 128 and not _contains_control(transaction_id) else None


def _contains_control(value: str) -> bool:
    return any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)


def _valid_scope(value: str) -> bool:
    if not 1 <= len(value) <= MAX_SCOPE_LENGTH or _contains_control(value):
        return False
    scopes: Final = value.split(" ")
    return "" not in scopes and len(scopes) == len(set(scopes)) and set(scopes) <= LOVABLE_SCOPES


def _valid_percent_encoding(value: str) -> bool:
    index: int = 0
    while index < len(value):
        if value[index] != "%":
            index += 1
            continue
        if index + 2 >= len(value) or any(
            character not in "0123456789abcdefABCDEF" for character in value[index + 1 : index + 3]
        ):
            return False
        index += 3
    return True


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        request: urllib.request.Request,
        file_pointer: object,
        code: int,
        message: str,
        headers: Mapping[str, str],
        new_url: str,
    ) -> None:
        return None


class CompletionClient:
    def __init__(self, secret: str, completion_url: str = COMPLETION_URL, ready_url: str = READY_URL) -> None:
        self._secret: Final = secret
        self._completion_url: Final = completion_url
        self._ready_url: Final = ready_url
        self._opener: Final = urllib.request.build_opener(NoRedirectHandler())

    def complete(self, payload: Mapping[str, str]) -> Page:
        return self._post(self._completion_url, payload)

    def ready(self, transaction_id: str) -> Page:
        return self._post(self._ready_url, {"transaction_id": transaction_id}, ready=True)

    def _post(self, url: str, payload: Mapping[str, str], ready: bool = False) -> Page:
        body: Final = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        request: Final = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._secret}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener.open(request, timeout=UPSTREAM_TIMEOUT_SECONDS) as response:
                response_body: Final = response.read(MAX_RESPONSE_BODY + 1)
                if len(response_body) > MAX_RESPONSE_BODY:
                    return RETRY
                return self._page_for_response(response.status, response_body, ready=ready)
        except urllib.error.HTTPError as error:
            try:
                error.read(MAX_RESPONSE_BODY + 1)
                if error.code == HTTPStatus.BAD_REQUEST:
                    return INVALID
                if error.code == HTTPStatus.GONE:
                    return EXPIRED
                return RETRY
            finally:
                error.close()
        except (OSError, TimeoutError, urllib.error.URLError):
            return RETRY

    @staticmethod
    def _page_for_response(status: int, body: bytes, ready: bool = False) -> Page:
        if status != HTTPStatus.OK:
            return RETRY
        try:
            parsed: Final = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError):
            return RETRY
        if ready:
            return READY if parsed == {"status": "ready"} else RETRY
        if parsed == {"outcome": "connected"}:
            return CONNECTED
        if parsed == {"outcome": "denied"}:
            return DENIED
        return RETRY


def handler_for(forwarder: Forwarder) -> type[socketserver.BaseRequestHandler]:
    class RelayHandler(socketserver.BaseRequestHandler):
        request: socket.socket

        def handle(self) -> None:
            self.request.settimeout(CLIENT_READ_TIMEOUT_SECONDS)
            raw_request: Final = self._read_headers()
            if raw_request is None:
                self._send_page(INVALID)
                return
            request_line: Final = raw_request.split(b"\r\n", 1)[0]
            try:
                method, target, version = request_line.decode("ascii").split(" ")
            except (UnicodeDecodeError, ValueError):
                self._send_page(INVALID)
                return
            if self._declares_body(raw_request):
                self._send_page(INVALID)
                return
            if version != "HTTP/1.1" or len(target) > MAX_REQUEST_TARGET or not target.startswith("/"):
                self._send_page(INVALID)
                return
            if method != "GET":
                self._send_page(NOT_FOUND)
                return
            if target == "/healthz":
                self._send(HTTPStatus.OK, b"ok\n", "text/plain; charset=utf-8")
                return
            if target.startswith("/ready"):
                transaction_id: Final = parse_ready(target)
                self._send_page(INVALID if transaction_id is None else forwarder.ready(transaction_id))
                return
            if target.startswith("/callback"):
                payload: Final = parse_callback(target)
                self._send_page(INVALID if payload is None else forwarder.complete(payload))
                return
            self._send_page(NOT_FOUND)

        def _read_headers(self) -> bytes | None:
            received: bytes = b""
            deadline: Final = time.monotonic() + CLIENT_READ_TIMEOUT_SECONDS
            try:
                while b"\r\n\r\n" not in received:
                    if len(received) >= MAX_HEADER_BYTES:
                        return None
                    remaining: Final = deadline - time.monotonic()
                    if remaining <= 0:
                        return None
                    self.request.settimeout(remaining)
                    chunk: Final = self.request.recv(min(1024, MAX_HEADER_BYTES + 1 - len(received)))
                    if not chunk:
                        return None
                    received += chunk
            except (OSError, TimeoutError):
                return None
            header_end: Final = received.find(b"\r\n\r\n") + 4
            if header_end > MAX_HEADER_BYTES or received[header_end:]:
                return None
            return received[:header_end]

        @staticmethod
        def _declares_body(raw_request: bytes) -> bool:
            for line in raw_request.split(b"\r\n")[1:-2]:
                if not line or line[:1] in (b" ", b"\t") or b":" not in line:
                    return True
                name: Final = line.split(b":", 1)[0].strip().lower()
                if name in (b"content-length", b"transfer-encoding"):
                    return True
            return False

        def _send_page(self, page: Page) -> None:
            body: Final = (
                "<!doctype html><html lang=en><meta charset=utf-8>"
                f"<title>{page.title}</title><style>body{{font:18px sans-serif;max-width:40rem;margin:15vh auto;padding:2rem}}"
                f"h1{{font-size:2rem}}</style><h1>{page.title}</h1><p>{page.message}</p>"
            ).encode()
            self._send(page.status, body, "text/html; charset=utf-8")

        def _send(self, status: HTTPStatus, body: bytes, content_type: str) -> None:
            headers: Final = "".join(f"{name}: {value}\r\n" for name, value in PAGE_HEADERS.items())
            response: Final = (
                f"HTTP/1.1 {status.value} {status.phrase}\r\n{headers}Content-Type: {content_type}\r\n"
                f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n"
            ).encode("ascii") + body
            try:
                self.request.sendall(response)
            except OSError:
                return

    return RelayHandler


class BoundedThreadingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address: tuple[str, int], handler: type[socketserver.BaseRequestHandler]) -> None:
        self._connections: Final = threading.BoundedSemaphore(MAX_CONNECTIONS)
        super().__init__(address, handler)

    def verify_request(self, request: socket.socket, client_address: tuple[str, int]) -> bool:
        admitted: Final = self._connections.acquire(blocking=False)
        if not admitted:
            request.close()
        return admitted

    def process_request_thread(self, request: socket.socket, client_address: tuple[str, int]) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._connections.release()


def main() -> None:
    secret_path: Final = os.environ.get(SECRET_FILE_ENV, DEFAULT_SECRET_FILE)
    secret: Final = load_secret(secret_path)
    server: Final = BoundedThreadingServer((LISTEN_HOST, LISTEN_PORT), handler_for(CompletionClient(secret)))
    server.serve_forever()


if __name__ == "__main__":
    main()
