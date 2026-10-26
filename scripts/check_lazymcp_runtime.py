#!/usr/bin/env python3
"""Check runtime DNS and a metadata operation through the real LazyMCP gateway."""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import socket
import sys
import time
from typing import Final
from urllib.parse import urlsplit

import anyio
import httpx2
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.types import CallToolResult, TextContent
from pydantic import BaseModel, ConfigDict, Field


class Options(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    env_key: str
    server: str
    tool: str
    dns_host: tuple[str, ...]
    max_dns_latency: float = Field(gt=0, allow_inf_nan=False)
    timeout: float = Field(gt=0, allow_inf_nan=False)
    cleanup_timeout: float = Field(gt=0, allow_inf_nan=False)


class DNSResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ok: bool
    seconds: float
    address_count: int = 0
    error_type: str | None = None


class DescribedTool(BaseModel):
    name: str


class Description(BaseModel):
    tools: tuple[DescribedTool, ...] = ()
    auth_status: str | None = None
    error: str | None = None


class GatewayResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ok: bool
    seconds: float
    gateway_tool_count: int = 0
    described_tool_count: int = 0
    metadata_ok: bool = False
    cleanup_complete: bool = False
    cleanup_seconds: float | None = None
    error_type: str | None = None


class RuntimeResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ok: bool
    dns: tuple[DNSResult, ...]
    gateway: GatewayResult


class MissingCredentialError(Exception):
    pass


class GatewayToolsMissingError(Exception):
    pass


class ListingFailedError(Exception):
    pass


class MetadataFailedError(Exception):
    pass


def description(result: CallToolResult) -> Description:
    if result.is_error:
        raise ListingFailedError
    text: Final = tuple(item.text for item in result.content if isinstance(item, TextContent))
    if len(text) != 1:
        raise ListingFailedError
    parsed: Final = Description.model_validate_json(text[0])
    if parsed.error is not None or parsed.auth_status not in (None, "not_required", "connected"):
        raise ListingFailedError
    return parsed


async def check_dns(host: str, maximum: float) -> DNSResult:
    start: Final = time.monotonic()
    try:
        with anyio.fail_after(maximum):
            addresses: Final = await asyncio.get_running_loop().getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        elapsed: Final = time.monotonic() - start
        return DNSResult(ok=bool(addresses) and elapsed <= maximum, seconds=elapsed, address_count=len(addresses))
    except Exception as error:
        return DNSResult(ok=False, seconds=time.monotonic() - start, error_type=type(error).__name__)


async def check_gateway(options: Options) -> GatewayResult:
    start: Final = time.monotonic()
    try:
        credential: Final = os.environ.get(options.env_key)
        if not credential:
            raise MissingCredentialError
        with anyio.fail_after(options.timeout) as lifecycle:
            async with httpx2.AsyncClient(
                headers={"Authorization": f"Bearer {credential}"}, timeout=options.timeout
            ) as client:
                async with streamable_http_client(options.url, http_client=client) as (reader, writer):
                    async with ClientSession(reader, writer, read_timeout_seconds=options.timeout) as session:
                        await session.initialize()
                        listed: Final = await session.list_tools()
                        names: Final = frozenset(tool.name for tool in listed.tools)
                        if not {"mcp_describe", "mcp_call"}.issubset(names):
                            raise GatewayToolsMissingError
                        described: Final = description(
                            await session.call_tool("mcp_describe", arguments={"server": options.server})
                        )
                        if options.tool not in frozenset(tool.name for tool in described.tools):
                            raise ListingFailedError
                        metadata: Final = await session.call_tool(
                            "mcp_call", arguments={"server": options.server, "tool": options.tool, "arguments": {}}
                        )
                        if metadata.is_error:
                            raise MetadataFailedError
                        cleanup_started: Final = time.monotonic()
                        lifecycle.deadline = anyio.current_time() + options.cleanup_timeout
        return GatewayResult(
            ok=True,
            seconds=time.monotonic() - start,
            gateway_tool_count=len(listed.tools),
            described_tool_count=len(described.tools),
            metadata_ok=True,
            cleanup_complete=True,
            cleanup_seconds=time.monotonic() - cleanup_started,
        )
    except Exception as error:
        return GatewayResult(ok=False, seconds=time.monotonic() - start, error_type=type(error).__name__)


async def check(options: Options) -> RuntimeResult:
    dns: Final = tuple(await asyncio.gather(*(check_dns(host, options.max_dns_latency) for host in options.dns_host)))
    gateway: Final = await check_gateway(options)
    return RuntimeResult(ok=all(item.ok for item in dns) and gateway.ok, dns=dns, gateway=gateway)


def parse_options() -> Options:
    parser: Final = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Existing LazyMCP gateway URL, including its path")
    parser.add_argument(
        "--env-key", default="LITELLM_MASTER_KEY", help="Environment variable containing the gateway key"
    )
    parser.add_argument("--server", required=True)
    parser.add_argument("--tool", required=True, help="Metadata tool that accepts empty arguments")
    parser.add_argument("--dns-host", action="append", default=[], help="Additional DNS hostname to check; repeatable")
    parser.add_argument("--max-dns-latency", type=float, default=1.0, help="Maximum DNS latency in seconds")
    parser.add_argument("--timeout", type=float, default=90.0, help="Gateway operation deadline in seconds")
    parser.add_argument("--cleanup-timeout", type=float, default=5.0, help="Gateway cleanup deadline in seconds")
    options: Final = Options.model_validate(vars(parser.parse_args()))
    url: Final = urlsplit(options.url)
    if (
        url.scheme not in ("http", "https")
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
    ):
        parser.error("--url must be an HTTP(S) endpoint without embedded credentials, query, or fragment")
    return options.model_copy(update={"dns_host": tuple(dict.fromkeys((url.hostname, *options.dns_host)))})


def main() -> int:
    logging.disable(logging.CRITICAL)
    options: Final = parse_options()
    if os.environ.get("LITELLM_EVENT_LOOP") == "asyncio" or sys.platform == "win32":
        result: Final = asyncio.run(check(options))
        sys.stdout.write(result.model_dump_json() + "\n")
        return 0 if result.ok else 1
    import uvloop

    with asyncio.Runner(loop_factory=uvloop.new_event_loop) as runner:
        result_uv: Final = runner.run(check(options))
    sys.stdout.write(result_uv.model_dump_json() + "\n")
    return 0 if result_uv.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
