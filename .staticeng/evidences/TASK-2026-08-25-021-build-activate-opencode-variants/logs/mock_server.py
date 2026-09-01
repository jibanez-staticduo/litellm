import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


CAPTURE = Path(sys.argv[1])
ALIASES = ("deepseek-v4-flash-fp8-mtp", "deepseek-v4-flash-fp8-mtp-norefusal")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, _format, *_args):
        return

    def send_json(self, value):
        body = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/v1/model/info":
            self.send_json({"data": []})
            return
        if self.path == "/model_group/info":
            self.send_json({"data": [{"model_group": alias, "mode": "chat"} for alias in ALIASES]})
            return
        self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        request = json.loads(self.rfile.read(length))
        sanitized = {
            "messages": "[REDACTED]",
            "model": request.get("model"),
            "path": self.path,
            "reasoning_effort": request.get("reasoning_effort"),
            "stream": request.get("stream"),
        }
        with CAPTURE.open("a") as output:
            output.write(json.dumps(sanitized, sort_keys=True) + "\n")

        chunks = (
            {"id": "mock", "object": "chat.completion.chunk", "created": 0, "model": request.get("model"), "choices": [{"index": 0, "delta": {"role": "assistant", "content": "mock-ok"}, "finish_reason": None}]},
            {"id": "mock", "object": "chat.completion.chunk", "created": 0, "model": request.get("model"), "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
        )
        body = "".join(f"data: {json.dumps(chunk)}\n\n" for chunk in chunks) + "data: [DONE]\n\n"
        encoded = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


CAPTURE.unlink(missing_ok=True)
ThreadingHTTPServer(("127.0.0.1", 18765), Handler).serve_forever()
