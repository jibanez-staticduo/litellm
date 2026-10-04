from __future__ import annotations

import argparse
import datetime as dt
import http.client
import json
import math
import os
import re
import ssl
import sys
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final, TypeAlias, cast
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

Json: TypeAlias = None | bool | int | float | str | list["Json"] | dict[str, "Json"]
Transport: TypeAlias = Callable[[str], tuple[int, bytes]]
MAX_BODY: Final = 262144
SCOPED_WINDOWS: Final = ("seven_day_opus", "seven_day_sonnet", "seven_day_oauth_apps", "seven_day_cowork", "seven_day_omelette")


@dataclass(frozen=True, slots=True)
class Window:
    used_percent: float
    reset_at: str | None
    limit_window_seconds: int


@dataclass(frozen=True, slots=True)
class ExtraUsage:
    enabled: bool | None
    monthly_limit: float | None
    used_credits: float | None
    utilization: float | None


@dataclass(frozen=True, slots=True)
class Error:
    code: str
    http_status: int | None = None


@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    plan: str | None = None
    status: str = "unavailable"
    five_hour: Window | None = None
    weekly: Window | None = None
    scoped_windows: tuple[tuple[str, Window | None], ...] = ()
    extra_usage: ExtraUsage | None = None
    error: Error | None = None


@dataclass(frozen=True, slots=True)
class Credentials:
    access_token: str
    plan: str | None


class Options(argparse.Namespace):
    json: bool
    profiles: list[str] | None
    profiles_dir: Path
    timezone: str


def number(value: Json, maximum: float | None = None) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    try:
        result: Final = float(value)
    except OverflowError:
        return None
    if not math.isfinite(result) or result < 0 or (maximum is not None and result > maximum):
        return None
    return result


def decode(raw: bytes) -> dict[str, Json] | None:
    if len(raw) > MAX_BODY:
        return None
    try:
        value: Final = cast(object, json.loads(raw))
    except (ValueError, RecursionError, UnicodeError):
        return None
    return cast(dict[str, Json], value) if isinstance(value, dict) else None


def credentials(home: Path) -> Credentials | Error:
    try:
        with (home / ".credentials.json").open("rb") as handle:
            raw: Final = handle.read(MAX_BODY + 1)
    except FileNotFoundError:
        return Error("auth_missing")
    except OSError:
        return Error("auth_unreadable")
    auth: Final = decode(raw)
    oauth: Final = auth.get("claudeAiOauth") if auth is not None else None
    if not isinstance(oauth, dict):
        return Error("auth_malformed")
    token: Final = oauth.get("accessToken")
    if not isinstance(token, str) or not token or any(ord(char) < 33 or ord(char) > 126 for char in token):
        return Error("auth_malformed")
    expiry: Final = number(oauth.get("expiresAt"))
    if expiry is not None and expiry <= dt.datetime.now(dt.timezone.utc).timestamp() * 1000:
        return Error("auth_expired")
    plan: Final = oauth.get("subscriptionType")
    return Credentials(token, plan if isinstance(plan, str) and plan in ("pro", "max", "team", "enterprise") else None)


def request(token: str) -> tuple[int, bytes]:
    connection: Final = http.client.HTTPSConnection("api.anthropic.com", timeout=15, context=ssl.create_default_context())
    try:
        connection.request("GET", "/api/oauth/usage", headers={
            "Authorization": "Bearer " + token,
            "anthropic-beta": "oauth-2025-04-20",
            "User-Agent": "claude-usage/1.0",
            "Accept": "application/json",
        })
        response: Final = connection.getresponse()
        return response.status, response.read(MAX_BODY + 1)
    finally:
        connection.close()


def window(value: Json, seconds: int) -> Window | Error | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        return Error("usage_malformed")
    used: Final = number(value.get("utilization"), 100)
    reset: Final = value.get("resets_at")
    if used is None:
        return Error("usage_malformed")
    if reset is None:
        return Window(used, None, seconds)
    if not isinstance(reset, str):
        return Error("usage_malformed")
    try:
        parsed: Final = dt.datetime.fromisoformat(reset.replace("Z", "+00:00"))
    except ValueError:
        return Error("usage_malformed")
    if parsed.tzinfo is None:
        return Error("usage_malformed")
    return Window(used, parsed.astimezone(dt.timezone.utc).isoformat(), seconds)


def parse_usage(name: str, plan: str | None, raw: bytes) -> Profile:
    usage: Final = decode(raw)
    if usage is None:
        return Profile(name, plan, error=Error("usage_malformed"))
    five: Final = window(usage.get("five_hour"), 18000)
    weekly: Final = window(usage.get("seven_day"), 604800)
    scoped: Final = tuple((key, window(usage.get(key), 604800)) for key in SCOPED_WINDOWS)
    if isinstance(five, Error) or isinstance(weekly, Error) or any(isinstance(value, Error) for _, value in scoped):
        return Profile(name, plan, error=Error("usage_malformed"))
    if five is None and weekly is None:
        return Profile(name, plan, error=Error("usage_missing"))
    extra: Final = usage.get("extra_usage")
    enabled: Final = extra.get("is_enabled") if isinstance(extra, dict) else None
    extra_usage: Final = ExtraUsage(
        enabled if isinstance(enabled, bool) else None,
        number(extra.get("monthly_limit")), number(extra.get("used_credits")), number(extra.get("utilization")),
    ) if isinstance(extra, dict) else None
    return Profile(name, plan, "ok", five, weekly, cast(tuple[tuple[str, Window | None], ...], scoped), extra_usage)


def fetch(name: str, home: Path, transport: Transport = request) -> Profile:
    auth: Final = credentials(home)
    if isinstance(auth, Error):
        return Profile(name, error=auth)
    try:
        status, raw = transport(auth.access_token)
    except TimeoutError:
        return Profile(name, auth.plan, error=Error("timeout"))
    except (OSError, http.client.HTTPException):
        return Profile(name, auth.plan, error=Error("network_error"))
    if status != 200:
        code: Final = "auth_rejected" if status in (401, 403) else "rate_limited" if status == 429 else "service_error"
        return Profile(name, auth.plan, error=Error(code, status))
    return parse_usage(name, auth.plan, raw)


def profile_json(profile: Profile) -> dict[str, object]:
    return {**asdict(profile), "scoped_windows": {key: asdict(value) if value is not None else None
                                                 for key, value in profile.scoped_windows}}


def render_window(label: str, value: Window | None, timezone: ZoneInfo) -> str:
    if value is None:
        return f"  {label}: N/D"
    reset: Final = dt.datetime.fromisoformat(value.reset_at).astimezone(timezone).strftime("%Y-%m-%d %H:%M %Z") \
        if value.reset_at is not None else "N/D"
    return f"  {label}: {value.used_percent:g}% usado, reinicia {reset}"


def render(profile: Profile, timezone: ZoneInfo) -> str:
    title: Final = f"{profile.name} ({profile.plan or 'plan desconocido'})"
    if profile.error is not None:
        login: Final = f"\n  Ejecuta: claude_{profile.name} auth login --claudeai" \
            if profile.error.code in ("auth_missing", "auth_expired", "auth_rejected") else ""
        return f"{title}\n  No disponible: {profile.error.code}{login}"
    scoped: Final = tuple(render_window(key.removeprefix("seven_day_"), value, timezone)
                         for key, value in profile.scoped_windows if value is not None)
    extra: Final = "activado" if profile.extra_usage is not None and profile.extra_usage.enabled is True else \
        "desactivado" if profile.extra_usage is not None and profile.extra_usage.enabled is False else "N/D"
    extra_percent: Final = f", {profile.extra_usage.utilization:g}% usado" \
        if profile.extra_usage is not None and profile.extra_usage.utilization is not None else ""
    return "\n".join((title, render_window("5 horas", profile.five_hour, timezone),
                      render_window("Semana", profile.weekly, timezone), *scoped, f"  Uso extra: {extra}{extra_percent}"))


def profile_name(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value) is None:
        raise argparse.ArgumentTypeError("invalid profile name")
    return value


def main(argv: tuple[str, ...] | None = None, transport: Transport = request) -> int:
    parser: Final = argparse.ArgumentParser(description="Claude subscription usage, without inference or token refresh")
    parser.add_argument("--json", action="store_true", help="emit schema-v1 JSON")
    parser.add_argument("--profile", "--account", action="append", type=profile_name, dest="profiles")
    parser.add_argument("--profiles-dir", type=Path, default=Path(os.environ.get("CLAUDE_USAGE_PROFILES_DIR",
                                                                                str(Path.home() / ".claude-homes"))))
    parser.add_argument("--timezone", default="Europe/Brussels")
    args: Final = parser.parse_args(argv, namespace=Options())
    try:
        timezone: Final = ZoneInfo(args.timezone)
    except (ZoneInfoNotFoundError, ValueError):
        parser.error("unknown timezone")
    names: Final = tuple(dict.fromkeys(args.profiles or ("staticduo", "defend1")))
    profiles: Final = tuple(fetch(name, args.profiles_dir / name, transport) for name in names)
    if args.json:
        sys.stdout.write(json.dumps({"schema_version": 1, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                                     "profiles": tuple(profile_json(profile) for profile in profiles)}, allow_nan=False) + "\n")
    else:
        sys.stdout.write("Claude usage\n\n" + "\n\n".join(render(profile, timezone) for profile in profiles) + "\n")
        sys.stdout.write("\nAnthropic publica porcentajes de cuota, no limites exactos de tokens\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
