#!/usr/bin/env python3
import argparse
import hashlib
import http.server
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.request


RETIRED = ("gpt-5.3-codex", "gpt-5.3-codex-spark")
OPENCODE_ROWS = {
    "gpt-5.4": ("none", "low", "medium", "high", "xhigh"),
    "gpt-5.4-mini": ("none", "low", "medium", "high", "xhigh"),
    "gpt-5.5": ("none", "low", "medium", "high", "xhigh"),
    "gpt-5.6-luna": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.6-sol": ("none", "low", "medium", "high", "xhigh", "max"),
    "gpt-5.6-terra": ("none", "low", "medium", "high", "xhigh", "max"),
    "deepseek-v4-flash-fp8-mtp": ("off", "low", "high", "max"),
    "qwen3.8-27b-refusal-dial": ("off", "low", "medium", "xhigh"),
}
CODEX_ROWS = {
    **{key: value for key, value in OPENCODE_ROWS.items() if not key.startswith(("deepseek", "qwen"))},
    "deepseek-v4-flash-fp8-mtp": ("none", "low", "high", "max"),
    "qwen3.8-27b-refusal-dial": ("low", "medium", "xhigh"),
}
ALIAS_CLASSES = {
    **{
        family: tuple(
            alias
            for alias in (
                family,
                f"chatgpt/{family}",
                f"chatgpt-account2/{family}",
                f"chatgpt-account3/{family}",
            )
        )
        for family in tuple(OPENCODE_ROWS)[:6]
    },
    "deepseek-v4-flash-fp8-mtp": (
        "deepseek-v4-flash-fp8-mtp",
        "deepseek-v4-flash-fp8-mtp-norefusal",
    ),
    "qwen3.8-27b-refusal-dial": ("qwen3.8-27b-refusal-dial",),
}


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


class CaptureServer(http.server.ThreadingHTTPServer):
    def __init__(self, address, metadata):
        self.metadata = metadata
        self.captures = []
        super().__init__(address, Handler)


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_args):
        return

    def do_GET(self):
        if self.path.endswith("/model/info"):
            self.reply_json(self.server.metadata["model/info"])
            return
        if self.path.endswith("/model_group/info"):
            self.reply_json({"data": self.server.metadata["model_group/info"]})
            return
        self.send_error(404)

    def do_POST(self):
        size = int(self.headers.get("content-length", "0"))
        body = json.loads(self.rfile.read(size) or b"{}")
        effort = body.get("reasoning_effort")
        if effort is None and isinstance(body.get("reasoning"), dict):
            effort = body["reasoning"].get("effort")
        thinking = body.get("chat_template_kwargs")
        self.server.captures.append(
            {
                "path": self.path,
                "model": body.get("model"),
                "effort": effort,
                "thinking": thinking,
                "input_present": bool(body.get("input") or body.get("messages")),
                "authorization_present": "authorization" in {key.lower() for key in self.headers},
            }
        )
        if self.path.endswith("/responses"):
            payload = (
                'event: response.completed\ndata: {"type":"response.completed","response":'
                '{"id":"resp_test","object":"response","created_at":0,"status":"completed",'
                '"model":"test","output":[],"parallel_tool_calls":true,"tool_choice":"auto",'
                '"tools":[],"usage":{"input_tokens":1,"output_tokens":1,"total_tokens":2}}}\n\n'
            ).encode()
            self.send_response(200)
            self.send_header("content-type", "text/event-stream")
            self.send_header("content-length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        payload = (
            'data: {"id":"chatcmpl-test","object":"chat.completion.chunk","created":0,'
            '"model":"test","choices":[{"index":0,"delta":{"content":"ok"},"finish_reason":null}]}\n\n'
            'data: {"id":"chatcmpl-test","object":"chat.completion.chunk","created":0,'
            '"model":"test","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}\n\n'
            "data: [DONE]\n\n"
        ).encode()
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def reply_json(self, value):
        payload = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def request_json(url, method="GET", body=None):
    payload = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(url, data=payload, method=method, headers={"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read()
        return None if not raw else json.loads(raw)


def wait_http(url):
    for _ in range(100):
        try:
            request_json(url)
            return
        except Exception:
            time.sleep(0.1)
    raise RuntimeError(f"timeout waiting for {url}")


def model_shape(model):
    variants = model.get("variants") or {}
    if isinstance(variants, list):
        variants = {row["id"]: row.get("body", {}) for row in variants}
    return {
        "default": (model.get("options") or {}).get("variantDefault"),
        "variants": variants,
    }


def run_opencode(args):
    metadata = json.loads(pathlib.Path(args.metadata).read_text())
    server = CaptureServer(("127.0.0.1", 0), metadata)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    capture_port = server.server_address[1]
    with tempfile.TemporaryDirectory(prefix="task005-opencode-") as root:
        env = {
            **os.environ,
            "XDG_DATA_HOME": root + "/data",
            "XDG_STATE_HOME": root + "/state",
            "XDG_CACHE_HOME": root + "/cache",
            "XDG_CONFIG_HOME": root + "/config",
            "OPENCODE_CONFIG_CONTENT": json.dumps(
                {
                    "plugin": [
                        [
                            pathlib.Path(args.plugin).as_uri(),
                            {
                                "baseURL": f"http://127.0.0.1:{capture_port}/v1",
                                "apiKey": "loopback-placeholder",
                                "providerKey": "LiteLLM",
                                "providerName": "LiteLLM",
                                "strict": True,
                            },
                        ]
                    ]
                }
            ),
        }
        log_path = pathlib.Path(root) / "opencode.log"
        with log_path.open("w") as log:
            process = subprocess.Popen(
                [args.opencode, "serve", "--hostname", "127.0.0.1", "--port", str(args.port), "--print-logs", "--log-level", "DEBUG"],
                cwd=root,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
        try:
            base = f"http://127.0.0.1:{args.port}"
            wait_http(base + "/config")
            config = request_json(base + "/config")
            provider = (config.get("provider") or {}).get("LiteLLM", {})
            models = provider.get("models") or {}
            selector = {key: model_shape(models[key]) for key in OPENCODE_ROWS if key in models}
            for model, modes in OPENCODE_ROWS.items():
                for mode in (*modes, None):
                    session = request_json(base + "/session", "POST", {"title": "qa", "model": {"id": model, "providerID": "LiteLLM", **({"variant": mode} if mode else {})}})
                    body = {
                        "model": {"providerID": "LiteLLM", "modelID": model},
                        "parts": [{"type": "text", "text": "x"}],
                        **({"variant": mode} if mode else {}),
                    }
                    request_json(base + f"/session/{session['id']}/prompt_async", "POST", body)
                    deadline = time.time() + 15
                    expected = len(server.captures) + 1
                    while len(server.captures) < expected and time.time() < deadline:
                        time.sleep(0.05)
            time.sleep(0.5)
        finally:
            process.terminate()
            process.wait(timeout=10)
        log_text = log_path.read_text(errors="replace")
        package = json.loads(pathlib.Path(args.package).read_text())
        aliases = {
            name: family
            for name in models
            for family, members in ALIAS_CLASSES.items()
            if name in members
        }
        near_matches = [
            name
            for name in models
            if name not in aliases and any(family in name for family in OPENCODE_ROWS)
        ]
        result = {
            "client": "opencode",
            "version": subprocess.check_output([args.opencode, "--version"], text=True).strip(),
            "metadata_source": args.source,
            "plugin_version": package["version"],
            "plugin_sha256": sha256(args.plugin),
            "model_count": len(models),
            "selector": selector,
            "alias_equivalence": aliases,
            "near_matches": near_matches,
            "retired_present": [name for name in models if any(retired in name for retired in RETIRED)],
            "captures": server.captures,
            "scoped_log": {
                "loaded_count": log_text.count("loaded LiteLLM provider metadata"),
                "failure_count": log_text.count("failed to load LiteLLM provider metadata"),
                "stale_version_count": log_text.count("0.1.9") + log_text.count("0.2.1"),
                "double_load": log_text.count("loaded LiteLLM provider metadata") != 1,
            },
        }
    server.shutdown()
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2) + "\n")


def codex_config(active, catalog_path, port):
    lines = pathlib.Path(active).read_text().splitlines()
    active_values = {}
    for line in lines:
        if "=" in line and not line.startswith("["):
            key, value = (part.strip() for part in line.split("=", 1))
            if key in {"model", "model_provider", "model_reasoning_effort", "personality"}:
                active_values[key] = value
    return "\n".join(
        [
            f"model = {active_values['model']}",
            'model_provider = "nas_litellm"',
            f'model_catalog_json = "{catalog_path}"',
            f"model_reasoning_effort = {active_values['model_reasoning_effort']}",
            f"personality = {active_values.get('personality', '" + '"pragmatic"' + "')}",
            'approval_policy = "never"',
            'sandbox_mode = "read-only"',
            "",
            "[model_providers.nas_litellm]",
            'name = "NAS LiteLLM loopback"',
            f'base_url = "http://127.0.0.1:{port}/v1"',
            'wire_api = "responses"',
            "request_max_retries = 0",
            "stream_max_retries = 0",
            "",
            "[model_providers.nas_litellm.auth]",
            f'command = "{pathlib.Path(active).parent / "qa-token"}"',
            "timeout_ms = 5000",
            "refresh_interval_ms = 0",
            "",
        ]
    )


def run_codex(args):
    server = CaptureServer(("127.0.0.1", 0), {})
    threading.Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    before = {path: (sha256(path), pathlib.Path(path).stat().st_mtime_ns) for path in (args.config, args.catalog, args.cache)}
    with tempfile.TemporaryDirectory(prefix="task005-codex-") as root:
        home = pathlib.Path(root)
        catalog = home / "catalog.json"
        shutil.copyfile(args.catalog, catalog)
        token = pathlib.Path(args.config).parent / "qa-token"
        isolated_token = home / "qa-token"
        isolated_token.write_text("#!/bin/sh\nprintf loopback-placeholder\n")
        isolated_token.chmod(0o700)
        config_text = codex_config(args.config, catalog, port).replace(str(token), str(isolated_token))
        (home / "config.toml").write_text(config_text)
        env = {**os.environ, "CODEX_HOME": root, "XDG_STATE_HOME": root + "/state", "XDG_CACHE_HOME": root + "/cache"}
        failures = []
        sequence = [(model, effort) for model, efforts in CODEX_ROWS.items() for effort in efforts]
        switches = [(model, efforts[0]) for model, efforts in reversed(tuple(CODEX_ROWS.items()))]
        for model, effort in (*sequence, *switches):
            command = [
                args.codex,
                "exec",
                "--ephemeral",
                "--strict-config",
                "--skip-git-repo-check",
                "--ignore-rules",
                "--color",
                "never",
                "-m",
                model,
                "-c",
                f'model_reasoning_effort="{effort}"',
                "-c",
                "features.memories=false",
                "x",
            ]
            completed = subprocess.run(command, cwd=root, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, timeout=30)
            if completed.returncode:
                lines = [line for line in completed.stderr.splitlines() if line.strip()]
                failures.append({"model": model, "effort": effort, "returncode": completed.returncode, "error_class": " | ".join(lines[-8:])[:500] if lines else "unknown"})
        catalog_data = json.loads(catalog.read_text())["models"]
        rows = {
            row["slug"]: {
                "default": row["default_reasoning_level"],
                "levels": [value["effort"] for value in row["supported_reasoning_levels"]],
            }
            for row in catalog_data
        }
    server.shutdown()
    after = {path: (sha256(path), pathlib.Path(path).stat().st_mtime_ns) for path in (args.config, args.catalog, args.cache)}
    result = {
        "client": "codex",
        "version": subprocess.check_output([args.codex, "--version"], text=True).strip(),
        "active_model": json.loads(json.dumps(pathlib.Path(args.config).read_text().splitlines()[0].split("=", 1)[1].strip().strip('"'))),
        "active_effort": pathlib.Path(args.config).read_text().splitlines()[3].split("=", 1)[1].strip().strip('"'),
        "wire_api": "responses",
        "rows": rows,
        "retired_present": [row for row in rows if any(retired in row for retired in RETIRED)],
        "captures": server.captures,
        "mode_capture_count": len(sequence),
        "switch_capture_count": len(switches),
        "failures": failures,
        "production_files_unchanged": before == after,
        "production_hashes": {path: values[0] for path, values in before.items()},
    }
    pathlib.Path(args.output).write_text(json.dumps(result, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(required=True)
    opencode = subparsers.add_parser("opencode")
    opencode.add_argument("--opencode", required=True)
    opencode.add_argument("--plugin", required=True)
    opencode.add_argument("--package", required=True)
    opencode.add_argument("--metadata", required=True)
    opencode.add_argument("--source", required=True)
    opencode.add_argument("--port", type=int, required=True)
    opencode.add_argument("--output", required=True)
    opencode.set_defaults(handler=run_opencode)
    codex = subparsers.add_parser("codex")
    codex.add_argument("--codex", required=True)
    codex.add_argument("--config", required=True)
    codex.add_argument("--catalog", required=True)
    codex.add_argument("--cache", required=True)
    codex.add_argument("--output", required=True)
    codex.set_defaults(handler=run_codex)
    args = parser.parse_args()
    args.handler(args)


if __name__ == "__main__":
    main()
