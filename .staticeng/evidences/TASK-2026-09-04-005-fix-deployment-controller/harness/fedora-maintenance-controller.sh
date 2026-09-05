#!/bin/bash
set -Eeuo pipefail
umask 077

readonly CANDIDATE_REF='docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3'
readonly CANDIDATE_CONFIG='sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915'
readonly ROLLBACK_DIGEST='sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04'
readonly INSPECT_FORMAT='{{.Id}}|{{.Image}}|{{.Config.Image}}|{{.State.Pid}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}|{{.RestartCount}}|{{.State.OOMKilled}}|{{.State.StartedAt}}'
readonly STARTUP_ATTEMPTS=${MAINTENANCE_STARTUP_ATTEMPTS:-180}
readonly STARTUP_INTERVAL=${MAINTENANCE_STARTUP_INTERVAL:-1}
readonly WATCHDOG_GRACE=${MAINTENANCE_WATCHDOG_GRACE:-2}

if [ "$#" -ne 0 ]; then
    printf 'usage: %s\n' "$0" >&2
    exit 64
fi

if [ "${MAINTENANCE_TEST_MODE:-0}" = 1 ]; then
    : "${MAINTENANCE_ROOT:?test root is required}"
    : "${MAINTENANCE_ATTEMPT:?test attempt is required}"
    resolved_test_root=$(readlink -f "$MAINTENANCE_ROOT")
    resolved_tmp_root=$(readlink -f "${TMPDIR:-/tmp}")
    case "$resolved_test_root/" in
        /tmp/*|"$resolved_tmp_root"/*) ;;
        *) printf 'test root must be under the temporary directory\n' >&2; exit 64 ;;
    esac
    readonly R=$MAINTENANCE_ROOT
    readonly A=$MAINTENANCE_ATTEMPT
    readonly WATCHDOG=${MAINTENANCE_WATCHDOG:?test watcher is required}
    readonly ROLLBACK=${MAINTENANCE_ROLLBACK:?test rollback is required}
    readonly COLLECTOR=${MAINTENANCE_COLLECTOR:?test collector is required}
else
    readonly R=/home/staticduo/docker/litellm
    readonly ACTIVE_POINTER="$R/releases/TASK-2026-09-03-006.active"
    A=$(cat "$ACTIVE_POINTER")
    readonly A
    readonly WATCHDOG="$A/rollback/watchdog.sh"
    readonly ROLLBACK="$A/rollback/rollback.sh"
    readonly COLLECTOR="$A/rollback/collect-watchdog-sample.sh"
fi

readonly SELECTOR="$R/.env"
readonly VALIDATION_MARKER="$A/safe/controller-validation-complete"
readonly READY_MARKER="$A/safe/candidate-ready"
readonly WATCHDOG_PID_FILE="$A/safe/watchdog.pid"
readonly PHASE_FILE="$A/safe/watchdog-phase"
readonly PRESTART_FILE="$A/safe/watchdog-pre-start"
readonly ACTIVE_FILE="$A/safe/watchdog-active"
readonly READY_REQUEST="$A/safe/ready-request"
readonly ROLLBACK_REQUIRED="$A/safe/rollback-required"
readonly PRIOR_SELECTOR="$A/safe/prior-selector.env"
readonly OWNERSHIP_LOCK="$A/safe/watchdog-ownership.lock"
readonly OWNERSHIP_STATE="$A/safe/watchdog-ownership"
readonly NONCE_FILE="$A/safe/watchdog-nonce"
mutation_started=0
handoff_complete=0
rollback_started=0
watchdog_pid=
selector_temporary=
ownership_locked=0

remove_selector_temporary() {
    if [ -n "$selector_temporary" ]; then
        rm -f "$selector_temporary"
        selector_temporary=
    fi
}

run_rollback() {
    if [ "$rollback_started" -eq 1 ]; then
        return 0
    fi
    rollback_started=1
    if [ "$ownership_locked" -eq 1 ]; then
        flock -u 8
        ownership_locked=0
    fi
    exec 8>"$OWNERSHIP_LOCK"
    flock 8
    printf 'nonce=%s\nstate=rollback\n' "$nonce" >"$OWNERSHIP_STATE.$$"
    mv "$OWNERSHIP_STATE.$$" "$OWNERSHIP_STATE"
    rm -f "$READY_MARKER"
    flock -u 8
    if [ -n "$watchdog_pid" ]; then
        kill "$watchdog_pid" 2>/dev/null || :
        wait "$watchdog_pid" 2>/dev/null || :
        watchdog_pid=
    fi
    remove_selector_temporary
    rm -f "$READY_MARKER" "$WATCHDOG_PID_FILE" "$READY_REQUEST" "$ACTIVE_FILE" "$PRESTART_FILE" "$ROLLBACK_REQUIRED" "$A/safe/controller-owner"
    if "$ROLLBACK"; then
        mutation_started=0
        return 0
    fi
    printf 'rollback failed\n' >&2
    return 1
}

fail_closed() {
    local failure_reason=$1
    local failure_status=${2:-1}
    printf 'controller failure: %s\n' "$failure_reason" >&2
    if [ "$mutation_started" -eq 1 ] || [ -e "$ROLLBACK_REQUIRED" ]; then
        if ! run_rollback; then
            exit 70
        fi
    fi
    exit "$failure_status"
}

on_error() {
    local error_status=$?
    trap - ERR
    remove_selector_temporary
    fail_closed unexpected_error "$error_status"
}

on_signal() {
    trap - HUP INT TERM
    fail_closed "signal_$1" 128
}

cleanup_on_exit() {
    local exit_status="$?"
    trap - EXIT
    if [ "$exit_status" -ne 0 ] && { [ "$mutation_started" -eq 1 ] || [ -e "$ROLLBACK_REQUIRED" ]; }; then
        run_rollback || exit_status=70
    elif [ "$exit_status" -eq 0 ] && [ "$mutation_started" -eq 1 ] && [ "$handoff_complete" -ne 1 ]; then
        run_rollback || exit_status=70
    else
        remove_selector_temporary
        if [ "$handoff_complete" -ne 1 ] && [ -n "$watchdog_pid" ]; then
            kill "$watchdog_pid" 2>/dev/null || :
            wait "$watchdog_pid" 2>/dev/null || :
        fi
    fi
    return "$exit_status"
}

trap on_error ERR
trap 'on_signal hup' HUP
trap 'on_signal int' INT
trap 'on_signal term' TERM
trap cleanup_on_exit EXIT

[ -d "$A/rollback" ] || fail_closed missing_rollback_directory
[ -d "$A/raw" ] || fail_closed missing_raw_directory
[ -d "$A/safe" ] || fail_closed missing_safe_directory
[ -f "$SELECTOR" ] || fail_closed missing_selector
[ -s "$A/safe/protected-baseline.sha256" ] || fail_closed missing_protected_baseline
[ -s "$A/safe/control-state" ] || fail_closed missing_control_state
[ -s "$A/safe/maintenance-deadline-monotonic" ] || fail_closed missing_maintenance_deadline
[ -s "$A/safe/rollback-confidence" ] || fail_closed missing_rollback_confidence
[ -s "$A/safe/dependencies.digest" ] || fail_closed missing_dependency_baseline
[ -s "$A/safe/watchdog-start-wall" ] || fail_closed missing_watchdog_start
[ "$(cat "$A/safe/control-state")" = pass ] || fail_closed invalid_control_state
[ "$(cat "$A/safe/rollback-confidence")" = armed ] || fail_closed invalid_rollback_confidence
deadline=$(cat "$A/safe/maintenance-deadline-monotonic")
now=$(cut -d' ' -f1 /proc/uptime)
awk -v now="$now" -v deadline="$deadline" 'BEGIN{exit !(deadline>now)}' || fail_closed expired_maintenance_deadline
for script in "$0" "$WATCHDOG" "$ROLLBACK" "$COLLECTOR"; do
    if [ ! -f "$script" ] || [ -L "$script" ]; then
        fail_closed invalid_controller_file
    fi
    bash -n "$script" || fail_closed invalid_controller_syntax
done
[ -x "$WATCHDOG" ] || fail_closed watcher_not_executable
[ -x "$ROLLBACK" ] || fail_closed rollback_not_executable
[ -x "$COLLECTOR" ] || fail_closed collector_not_executable
[ -w "$A/safe" ] || fail_closed safe_directory_not_writable
[ -w "$A/rollback" ] || fail_closed rollback_directory_not_writable
[ ! -e "$PRIOR_SELECTOR" ] || fail_closed prior_selector_already_exists

if [ "${MAINTENANCE_TEST_MODE:-0}" != 1 ]; then
    grep -Fq "$ROLLBACK_DIGEST" "$ROLLBACK" || fail_closed rollback_digest_mismatch
    grep -Fq 'docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm' "$ROLLBACK" || fail_closed rollback_command_mismatch
    # shellcheck disable=SC2016
    grep -Fq 'ROLLBACK=${WATCHDOG_ROLLBACK:-$A/rollback/rollback.sh}' "$WATCHDOG" || fail_closed watcher_rollback_wiring_mismatch
fi

rm -f "$VALIDATION_MARKER" "$READY_MARKER" "$WATCHDOG_PID_FILE" "$PHASE_FILE" "$PRESTART_FILE" "$ACTIVE_FILE" "$READY_REQUEST" "$ROLLBACK_REQUIRED" "$OWNERSHIP_STATE" "$NONCE_FILE" "$A/safe/trigger" "$A/safe/rollback-start" "$A/safe/rollback-complete"
printf '%s\n' "$$" >"$A/safe/controller-owner"
printf 'controller=pass\nwatcher=pass\nrollback=pass\ncollector=pass\n' >"$VALIDATION_MARKER"
nonce=$(python3 - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)
printf '%s\n' "$nonce" >"$NONCE_FILE.$$"
mv "$NONCE_FILE.$$" "$NONCE_FILE"
printf 'nonce=%s\nstate=active\n' "$nonce" >"$OWNERSHIP_STATE.$$"
mv "$OWNERSHIP_STATE.$$" "$OWNERSHIP_STATE"
printf 'pre-start\n' >"$PHASE_FILE.$$"
mv "$PHASE_FILE.$$" "$PHASE_FILE"

WATCHDOG_ATTEMPT="$A" "$WATCHDOG" >>"$A/raw/watchdog-controller.log" 2>&1 &
watchdog_pid=$!
printf '%s\n' "$watchdog_pid" >"$WATCHDOG_PID_FILE"
sleep "$WATCHDOG_GRACE"
kill -0 "$watchdog_pid" 2>/dev/null || fail_closed watcher_start_failed
for ((attempt = 1; attempt <= STARTUP_ATTEMPTS; attempt++)); do
    kill -0 "$watchdog_pid" 2>/dev/null || fail_closed watcher_stopped_before_mutation
    [ ! -e "$A/safe/trigger" ] || fail_closed watcher_triggered_before_mutation
    if [ -s "$PRESTART_FILE" ]; then
        break
    fi
    sleep "$STARTUP_INTERVAL"
done
[ -s "$PRESTART_FILE" ] || fail_closed watcher_pre_start_failed

if ! selector_temporary=$(python3 - "$SELECTOR" "$CANDIDATE_REF" <<'PY'
import os
import pathlib
import sys
import tempfile

path = pathlib.Path(sys.argv[1])
candidate = sys.argv[2]
stat = path.stat()
lines = path.read_text().splitlines()
if sum(line.startswith("LITELLM_IMAGE=") for line in lines) != 1:
    raise SystemExit(1)
updated = "\n".join(
    "LITELLM_IMAGE=" + candidate if line.startswith("LITELLM_IMAGE=") else line
    for line in lines
) + "\n"
descriptor, temporary = tempfile.mkstemp(prefix=".maintenance.", dir=path.parent)
try:
    os.fchmod(descriptor, stat.st_mode & 0o777)
    os.write(descriptor, updated.encode())
    os.fsync(descriptor)
finally:
    os.close(descriptor)
os.chown(temporary, stat.st_uid, stat.st_gid)
print(temporary)
PY
); then
    fail_closed selector_prepare_failed
fi
if [ -z "$selector_temporary" ] || [ ! -f "$selector_temporary" ]; then
    fail_closed selector_prepare_failed
fi
if ! python3 - "$SELECTOR" "$PRIOR_SELECTOR" <<'PY'
import os
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
backup = pathlib.Path(sys.argv[2])
expected = 'LITELLM_IMAGE=docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04'
data = source.read_bytes()
if [line for line in data.decode().splitlines() if line.startswith('LITELLM_IMAGE=')] != [expected]:
    raise SystemExit(1)
if backup.exists() or backup.is_symlink():
    raise SystemExit(1)
descriptor = os.open(backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o400)
try:
    with os.fdopen(descriptor, 'wb', closefd=False) as stream:
        stream.write(data)
        stream.flush()
    os.fsync(descriptor)
finally:
    os.close(descriptor)
PY
then
    fail_closed prior_selector_capture_failed
fi
printf 'required\n' >"$ROLLBACK_REQUIRED.$$"
mv "$ROLLBACK_REQUIRED.$$" "$ROLLBACK_REQUIRED"
mutation_started=1
if [ -n "${MAINTENANCE_TEST_SIGNAL_AFTER_ROLLBACK_REQUIRED:-}" ]; then
    kill -s "$MAINTENANCE_TEST_SIGNAL_AFTER_ROLLBACK_REQUIRED" "$$"
fi
exec 8>"$OWNERSHIP_LOCK"
ownership_locked=1
flock 8
if [ "$(cat "$OWNERSHIP_STATE")" != "$(printf 'nonce=%s\nstate=active' "$nonce")" ] || [ -e "$A/safe/rollback-intent" ]; then
    fail_closed rollback_before_selector
fi
if ! mv "$selector_temporary" "$SELECTOR"; then
    fail_closed selector_replace_failed
fi
selector_temporary=
flock -u 8
ownership_locked=0

if ! (cd "$R" && docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm); then
    fail_closed candidate_recreate_failed
fi

startup_ready=0
for ((attempt = 1; attempt <= STARTUP_ATTEMPTS; attempt++)); do
    kill -0 "$watchdog_pid" 2>/dev/null || fail_closed watcher_stopped_during_startup
    container_state=
    liveliness=
    readiness=
    if container_state=$(docker inspect --type container --format "$INSPECT_FORMAT" litellm) &&
        [ "$(printf '%s\n' "$container_state" | wc -l)" -eq 1 ]; then
        IFS='|' read -r container_id runtime_image configured_image container_pid state health restarts oom_killed started_at <<<"$container_state"
        if liveliness=$(curl --silent --show-error --output /dev/null --max-time 1 --write-out '%{http_code}' http://127.0.0.1:4000/health/liveliness) &&
            readiness=$(curl --silent --show-error --output /dev/null --max-time 1 --write-out '%{http_code}' http://127.0.0.1:4000/health/readiness) &&
            [ -n "$container_id" ] &&
            [ "$runtime_image" = "$CANDIDATE_CONFIG" ] &&
            [ "$configured_image" = "$CANDIDATE_REF" ] &&
            [[ "$container_pid" =~ ^[1-9][0-9]*$ ]] &&
            [ "$state" = running ] &&
            [ "$health" = healthy ] &&
            [ "$restarts" = 0 ] &&
            [ "$oom_killed" = false ] &&
            [ -n "$started_at" ] &&
            [ "$liveliness" = 200 ] &&
            [ "$readiness" = 200 ]; then
            startup_ready=1
            break
        fi
    fi
    sleep "$STARTUP_INTERVAL"
done
[ "$startup_ready" -eq 1 ] || fail_closed candidate_startup_failed

printf 'active\n' >"$PHASE_FILE.$$"
mv "$PHASE_FILE.$$" "$PHASE_FILE"
printf 'nonce=%s\nrequest=ready\n' "$nonce" >"$READY_REQUEST.$$"
mv "$READY_REQUEST.$$" "$READY_REQUEST"
if [ -n "${MAINTENANCE_TEST_FINAL_RACE_HOOK:-}" ]; then
    "$MAINTENANCE_TEST_FINAL_RACE_HOOK"
fi
for ((attempt = 1; attempt <= STARTUP_ATTEMPTS; attempt++)); do
    kill -0 "$watchdog_pid" 2>/dev/null || fail_closed watcher_stopped_before_ready
    [ ! -e "$A/safe/trigger" ] || fail_closed watcher_triggered_before_ready
    if [ -s "$READY_MARKER" ]; then
        break
    fi
    sleep "$STARTUP_INTERVAL"
done
if [ -n "${MAINTENANCE_TEST_READY_LOCK_HOOK:-}" ]; then
    "$MAINTENANCE_TEST_READY_LOCK_HOOK"
fi
exec 8>"$OWNERSHIP_LOCK"
ownership_locked=1
flock 8
expected_ready=$(printf 'nonce=%s\nstate=ready' "$nonce")
if ! kill -0 "$watchdog_pid" 2>/dev/null || [ "$(cat "$PHASE_FILE")" != active ] || \
    [ "$(cat "$OWNERSHIP_STATE")" != "$expected_ready" ] || ! grep -qx "nonce=$nonce" "$READY_MARKER" || \
    [ -e "$A/safe/rollback-intent" ] || \
    [ -e "$A/safe/trigger" ] || [ -e "$A/safe/rollback-start" ] || [ -e "$A/safe/rollback-complete" ]; then
    flock -u 8
    ownership_locked=0
    fail_closed watcher_ready_ownership_lost
fi
handoff_complete=1
flock -u 8
ownership_locked=0
printf 'candidate_ready=yes\nwatchdog_armed=yes\n'
