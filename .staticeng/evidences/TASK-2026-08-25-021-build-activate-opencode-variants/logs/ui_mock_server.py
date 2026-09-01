import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


MODELS = (
    "deepseek-v4-flash-fp8-mtp",
    "deepseek-v4-flash-fp8-mtp-norefusal",
    "unrelated-reasoning-model",
)


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
            self.send_json(
                {
                    "data": [
                        {
                            "model_group": model,
                            "mode": "chat",
                            "supports_reasoning": model == "unrelated-reasoning-model",
                        }
                        for model in MODELS
                    ]
                }
            )
            return
        self.send_error(404)


ThreadingHTTPServer(("127.0.0.1", 18765), Handler).serve_forever()
