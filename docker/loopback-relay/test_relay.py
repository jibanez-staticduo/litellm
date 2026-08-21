from __future__ import annotations

import concurrent.futures
import http.client
import socket
import tempfile
import threading
import time
import unittest
from collections.abc import Mapping
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Final

import relay

STATE: Final = "s" * 43


class RecordingForwarder:
    def __init__(self, page: relay.Page = relay.CONNECTED) -> None:
        self.page: Final = page
        self._payloads: list[Mapping[str, str]] = []
        self._lock: Final = threading.Lock()

    @property
    def payloads(self) -> tuple[Mapping[str, str], ...]:
        with self._lock:
            return tuple(self._payloads)

    def complete(self, payload: Mapping[str, str]) -> relay.Page:
        with self._lock:
            self._payloads.append(payload)
        return self.page

    def ready(self, transaction_id: str) -> relay.Page:
        with self._lock:
            self._payloads.append({"transaction_id": transaction_id})
        return relay.READY


class RelayServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.forwarder: Final = RecordingForwarder()
        self.server: Final = relay.BoundedThreadingServer(("127.0.0.1", 0), relay.handler_for(self.forwarder))
        self.thread: Final = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, target: str, method: str = "GET") -> tuple[int, bytes]:
        connection: Final = http.client.HTTPConnection("127.0.0.1", self.server.server_address[1], timeout=2)
        connection.request(method, target)
        response: Final = connection.getresponse()
        result: Final = (response.status, response.read())
        connection.close()
        return result

    def raw_request(self, request: bytes) -> bytes:
        connection: Final = socket.create_connection(("127.0.0.1", self.server.server_address[1]), timeout=2)
        connection.sendall(request)
        response: Final = connection.recv(16384)
        connection.close()
        return response

    def test_health_and_unknown_routes_do_not_forward(self) -> None:
        self.assertEqual(self.request("/healthz"), (HTTPStatus.OK, b"ok\n"))
        self.assertEqual(self.request("/healthz?query=forbidden")[0], HTTPStatus.NOT_FOUND)
        self.assertEqual(self.request("/callback", "POST")[0], HTTPStatus.BAD_REQUEST)
        self.assertEqual(self.request("/other")[0], HTTPStatus.NOT_FOUND)
        self.assertEqual(self.forwarder.payloads, ())

    def test_ready_requires_exact_transaction_id_and_forwards_once(self) -> None:
        transaction_id: Final = "t" * 43
        self.assertEqual(self.request(f"/ready?transaction_id={transaction_id}")[0], HTTPStatus.OK)
        self.assertEqual(self.forwarder.payloads, ({"transaction_id": transaction_id},))
        for target in ("/ready", "/ready?transaction_id=short", f"/ready?transaction_id={transaction_id}&extra=x"):
            self.assertEqual(self.request(target)[0], HTTPStatus.BAD_REQUEST)

    def test_success_and_error_shapes_forward_once(self) -> None:
        self.assertEqual(self.request(f"/callback?state={STATE}&code=opaque")[0], HTTPStatus.OK)
        self.assertEqual(
            self.request(f"/callback?state={STATE}&error=access_denied&error_description=no")[0], HTTPStatus.OK
        )
        self.assertEqual(len(self.forwarder.payloads), 2)
        self.assertEqual(self.forwarder.payloads[0], {"state": STATE, "code": "opaque"})

    def test_success_metadata_is_validated_but_not_forwarded(self) -> None:
        scope: Final = "offline projects:read projects:write projects:create workspaces:read workspaces:write"
        target: Final = (
            f"/callback?code=synthetic&state={STATE}&iss=https%3A%2F%2Flovable.dev%2Foauth&scope="
            + scope.replace(" ", "+")
        )
        self.assertEqual(self.request(target)[0], HTTPStatus.OK)
        self.assertEqual(self.request(f"/callback?code=synthetic-two&state={STATE}")[0], HTTPStatus.OK)
        self.assertEqual(
            self.forwarder.payloads,
            ({"code": "synthetic", "state": STATE}, {"code": "synthetic-two", "state": STATE}),
        )

    def test_invalid_success_metadata_never_forwards(self) -> None:
        targets: Final = (
            f"/callback?code=x&state={STATE}&iss=https%3A%2F%2Fattacker.invalid",
            f"/callback?code=x&state={STATE}&iss=https%3A%2F%2Flovable.dev%2Foauth&iss=https%3A%2F%2Flovable.dev%2Foauth",
            f"/callback?code=x&state={STATE}&scope=projects%3Aread&scope=projects%3Awrite",
            f"/callback?code=x&state={STATE}&scope=projects%3Aread+unknown",
            f"/callback?code=x&state={STATE}&scope=projects%3Aread+projects%3Aread",
            f"/callback?code=x&state={STATE}&scope=projects%3Aread%20%20projects%3Awrite",
            f"/callback?code=x&state={STATE}&scope=%ZZ",
            f"/callback?code=x&state={STATE}&scope={'x' * (relay.MAX_SCOPE_LENGTH + 1)}",
            f"/callback?code=x&state={STATE}&unexpected=value",
        )
        for target in targets:
            with self.subTest(target=target[:100]):
                self.assertEqual(self.request(target)[0], HTTPStatus.BAD_REQUEST)
        self.assertEqual(self.forwarder.payloads, ())

    def test_invalid_callbacks_never_forward(self) -> None:
        targets: Final = (
            "/callback",
            f"/callback?code=x&state={STATE}&state={STATE}",
            f"/callback?state={STATE}&code=x&error=no",
            f"/callback?state={STATE}&code=",
            "/callback?state=short&code=x",
            f"/callback?state={STATE}&code=x&extra=y",
            f"/callback?state={STATE}&error=denied&error_description={'x' * 513}",
            f"/callback?state={STATE}&code={'x' * 2049}",
            f"/callback?state={STATE}&code=%0Asecret",
            "/callback?state=%FF&code=x",
            f"/callback?state={STATE}&code=%ZZ",
            f"/callback?state={STATE}&code=%",
            f"http://attacker.invalid/callback?state={STATE}&code=x",
        )
        for target in targets:
            with self.subTest(target=target[:80]):
                self.assertEqual(self.request(target)[0], HTTPStatus.BAD_REQUEST)
        self.assertEqual(self.forwarder.payloads, ())

    def test_absolute_form_and_oversized_headers_never_forward(self) -> None:
        absolute: Final = (
            f"GET http://attacker.invalid/callback?state={STATE}&code=x HTTP/1.1\r\nHost: relay\r\n\r\n"
        ).encode()
        oversized: Final = (
            f"GET /callback?state={STATE}&code=x HTTP/1.1\r\nHost: relay\r\nX-Fill: "
            + "x" * relay.MAX_HEADER_BYTES
            + "\r\n\r\n"
        ).encode()
        self.assertIn(b" 400 ", self.raw_request(absolute))
        self.assertIn(b" 400 ", self.raw_request(oversized))
        self.assertEqual(self.forwarder.payloads, ())

    def test_slow_clients_are_bounded_and_health_recovers(self) -> None:
        clients: Final = tuple(
            socket.create_connection(("127.0.0.1", self.server.server_address[1]), timeout=2)
            for _ in range(relay.MAX_CONNECTIONS)
        )
        for client in clients:
            client.sendall(b"GET /callback?")
        stop: Final = threading.Event()

        def trickle(client: socket.socket) -> None:
            while not stop.wait(relay.CLIENT_READ_TIMEOUT_SECONDS / 4):
                try:
                    client.sendall(b"x")
                except OSError:
                    return

        tricklers: Final = tuple(threading.Thread(target=trickle, args=(client,), daemon=True) for client in clients)
        for trickler in tricklers:
            trickler.start()
        started: Final = time.monotonic()
        health: tuple[int, bytes] | None = None
        while health is None and time.monotonic() - started < relay.CLIENT_READ_TIMEOUT_SECONDS + 1:
            try:
                health = self.request("/healthz")
            except (ConnectionError, http.client.HTTPException):
                time.sleep(0.05)
        self.assertEqual(health, (HTTPStatus.OK, b"ok\n"))
        self.assertLess(time.monotonic() - started, relay.CLIENT_READ_TIMEOUT_SECONDS + 1)
        stop.set()
        for client in clients:
            client.close()
        for trickler in tricklers:
            trickler.join()
        self.assertEqual(self.forwarder.payloads, ())

    def test_declared_and_split_bodies_never_forward(self) -> None:
        target: Final = f"/callback?state={STATE}&code=x"
        requests: Final = (
            f"GET {target} HTTP/1.1\r\nHost: relay\r\nContent-Length: 0\r\n\r\n",
            f"GET {target} HTTP/1.1\r\nHost: relay\r\ncontent-length: 1\r\n\r\nx",
            f"GET {target} HTTP/1.1\r\nHost: relay\r\nTransfer-Encoding: chunked\r\n\r\n",
            f"GET {target} HTTP/1.1\r\nHost: relay\r\nX: y\r\nTRANSFER-ENCODING: identity, chunked\r\n\r\n",
        )
        for request in requests:
            with self.subTest(request=request.split("\r\n")[2]):
                self.assertIn(b" 400 ", self.raw_request(request.encode()))

        connection: Final = socket.create_connection(("127.0.0.1", self.server.server_address[1]), timeout=2)
        connection.sendall(f"GET {target} HTTP/1.1\r\nHost: relay\r\nContent-Length: 1\r\n\r\n".encode())
        time.sleep(0.1)
        connection.sendall(b"x")
        response: Final = connection.recv(16384)
        connection.close()
        self.assertIn(b" 400 ", response)
        self.assertEqual(self.forwarder.payloads, ())

    def test_concurrent_callbacks_each_make_exactly_one_forward(self) -> None:
        count: Final = 20
        with concurrent.futures.ThreadPoolExecutor(max_workers=count) as executor:
            statuses: Final = tuple(
                executor.map(lambda index: self.request(f"/callback?state={STATE}&code=code{index}")[0], range(count))
            )
        self.assertEqual(statuses, (HTTPStatus.OK,) * count)
        self.assertEqual(len(self.forwarder.payloads), count)

    def test_response_does_not_reflect_callback_values(self) -> None:
        marker: Final = "do-not-reflect"
        _, body = self.request(f"/callback?state={STATE}&code={marker}")
        self.assertNotIn(marker.encode(), body)
        self.assertNotIn(STATE.encode(), body)


class UnitTest(unittest.TestCase):
    def test_secret_loader_requires_regular_bounded_secret(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            secret_path: Final = Path(directory) / "secret"
            secret_path.write_text("a" * 32 + "\n", encoding="utf-8")
            self.assertEqual(relay.load_secret(str(secret_path)), "a" * 32)
            secret_path.write_text("too-short", encoding="utf-8")
            with self.assertRaises(ValueError):
                relay.load_secret(str(secret_path))
            symlink_path: Final = Path(directory) / "link"
            symlink_path.symlink_to(secret_path)
            with self.assertRaises(OSError):
                relay.load_secret(str(symlink_path))

    def test_completion_response_mapping_is_generic(self) -> None:
        self.assertEqual(relay.CompletionClient._page_for_response(200, b'{"outcome":"connected"}'), relay.CONNECTED)
        self.assertEqual(relay.CompletionClient._page_for_response(200, b'{"outcome":"denied"}'), relay.DENIED)
        self.assertEqual(
            relay.CompletionClient._page_for_response(200, b'{"outcome":"connected","token":"x"}'), relay.RETRY
        )
        self.assertEqual(relay.CompletionClient._page_for_response(200, b"not-json"), relay.RETRY)

    def test_redirects_do_not_disclose_bearer(self) -> None:
        captured: list[str | None] = []
        redirect_status: list[HTTPStatus] = [HTTPStatus.FOUND]

        class CaptureHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                captured.append(self.headers.get("Authorization"))
                self.send_response(HTTPStatus.OK)
                self.end_headers()

            def log_message(self, format: str, *args: object) -> None:
                return

        capture: Final = ThreadingHTTPServer(("127.0.0.1", 0), CaptureHandler)
        capture_thread: Final = threading.Thread(target=capture.serve_forever, daemon=True)
        capture_thread.start()

        class RedirectHandler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                self.send_response(redirect_status[0])
                self.send_header("Location", f"http://127.0.0.1:{capture.server_port}/stolen")
                self.end_headers()

            def log_message(self, format: str, *args: object) -> None:
                return

        redirect: Final = ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler)
        redirect_thread: Final = threading.Thread(target=redirect.serve_forever, daemon=True)
        redirect_thread.start()
        try:
            client: Final = relay.CompletionClient("x" * 32, f"http://127.0.0.1:{redirect.server_port}/complete")
            for status in (
                HTTPStatus.MOVED_PERMANENTLY,
                HTTPStatus.FOUND,
                HTTPStatus.SEE_OTHER,
                HTTPStatus.TEMPORARY_REDIRECT,
                HTTPStatus.PERMANENT_REDIRECT,
            ):
                redirect_status[0] = status
                with self.subTest(status=status):
                    self.assertEqual(client.complete({"state": STATE, "code": "opaque"}), relay.RETRY)
            self.assertEqual(captured, [])
        finally:
            redirect.shutdown()
            capture.shutdown()
            redirect.server_close()
            capture.server_close()
            redirect_thread.join()
            capture_thread.join()

    def test_container_artifacts_require_runtime_hardening(self) -> None:
        directory: Final = Path(__file__).parent
        dockerfile: Final = (directory / "Dockerfile").read_text(encoding="utf-8")
        compose: Final = (directory / "compose.yaml").read_text(encoding="utf-8")
        self.assertIn("USER 65532:65532", dockerfile)
        for required in (
            'user: "65532:65532"',
            "read_only: true",
            "cap_drop:",
            "- ALL",
            "no-new-privileges:true",
            '"127.0.0.1:43119:8080"',
            "external: true",
        ):
            self.assertIn(required, compose)
        self.assertNotIn("privileged: true", compose)


if __name__ == "__main__":
    unittest.main()
