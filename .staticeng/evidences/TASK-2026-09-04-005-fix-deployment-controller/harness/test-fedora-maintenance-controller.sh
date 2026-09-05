#!/bin/bash
set -euo pipefail

H=$(cd "$(dirname "$0")" && pwd)
readonly H
readonly CONTROLLER="$H/fedora-maintenance-controller.sh"
W=$(mktemp -d)
readonly W
P=
trap 'if [ -n "$P" ]; then kill -KILL "$P" 2>/dev/null || :; wait "$P" 2>/dev/null || :; fi; if [ "${KEEP_TEST_WORKSPACE:-0}" = 1 ]; then printf "workspace=%s\n" "$W"; else rm -rf "$W"; fi' EXIT

readonly CANDIDATE_REF='docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3'
readonly CANDIDATE_CONFIG='sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915'
readonly ROLLBACK_REF='docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04'
readonly MOCK="$W/mock"
mkdir -p "$MOCK"

cat >"$MOCK/docker" <<'SH'
#!/bin/bash
set -euo pipefail
[ -s "$VALIDATION_MARKER" ] || exit 91
case "${1:-}" in
    compose)
        printf 'compose\n' >>"$EVENTS"
        exit "${COMPOSE_STATUS:-0}"
        ;;
    inspect)
        health=healthy
        [ "$SCENARIO" != startup_failure ] || health=starting
        printf 'cid|%s|%s|4242|running|%s|0|false|2026-09-05T00:00:00Z\n' "$TEST_CANDIDATE_CONFIG" "$TEST_CANDIDATE_REF" "$health"
        ;;
    *) exit 93 ;;
esac
SH
cat >"$MOCK/curl" <<'SH'
#!/bin/bash
set -euo pipefail
printf '200'
SH
chmod 0700 "$MOCK/docker" "$MOCK/curl"

prepare_case() {
    local case_name=$1
    ROOT="$W/$case_name/root"
    ATTEMPT="$ROOT/releases/attempt"
    mkdir -p "$ATTEMPT/rollback" "$ATTEMPT/raw" "$ATTEMPT/safe"
    printf 'LITELLM_IMAGE=%s\nUNCHANGED=value\n' "$ROLLBACK_REF" >"$ROOT/.env"
    SELECTOR_BEFORE=$(sha256sum "$ROOT/.env")
    printf 'credential-bytes-must-not-change\n' >"$ATTEMPT/safe/administrator-credential.fixture"
    printf 'placeholder  file\n' >"$ATTEMPT/safe/protected-baseline.sha256"
    printf 'pass\n' >"$ATTEMPT/safe/control-state"
    printf '999999999\n' >"$ATTEMPT/safe/maintenance-deadline-monotonic"
    printf 'armed\n' >"$ATTEMPT/safe/rollback-confidence"
    printf 'expected-dependencies\n' >"$ATTEMPT/safe/dependencies.digest"
    printf '2026-09-05T00:00:00Z\n' >"$ATTEMPT/safe/watchdog-start-wall"
    CREDENTIAL_BEFORE=$(sha256sum "$ATTEMPT/safe/administrator-credential.fixture")
    EVENTS="$W/$case_name/events"
    ROLLBACK_MARKER="$W/$case_name/rollback.marker"
    REQUEST_MARKER="$W/$case_name/request.marker"
    : >"$EVENTS"

    cat >"$ATTEMPT/rollback/watchdog.sh" <<'SH'
#!/bin/bash
set -euo pipefail
trap 'exit 0' TERM
while :; do
    phase=$(cat "$WATCHDOG_ATTEMPT/safe/watchdog-phase")
    case "$phase" in
        pre-start)
            printf 'phase=pre-start\ndependencies=expected-dependencies\nprotected=pass\n' >"$WATCHDOG_ATTEMPT/safe/watchdog-pre-start.$$"
            mv "$WATCHDOG_ATTEMPT/safe/watchdog-pre-start.$$" "$WATCHDOG_ATTEMPT/safe/watchdog-pre-start"
            ;;
        active)
            cat >"$WATCHDOG_ATTEMPT/safe/watchdog-active.$$" <<EOF
phase=active
container_id=cid
started_at=2026-09-05T00:00:00Z
configured_image=$TEST_CANDIDATE_REF
runtime_image=$TEST_CANDIDATE_CONFIG
config_identity=$TEST_CANDIDATE_CONFIG
source_identity=source
health=healthy
liveliness=200
readiness=200
EOF
            mv "$WATCHDOG_ATTEMPT/safe/watchdog-active.$$" "$WATCHDOG_ATTEMPT/safe/watchdog-active"
            if [ -e "$WATCHDOG_ATTEMPT/safe/ready-request" ] && grep -qx 'state=active' "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"; then
                exec 8>"$WATCHDOG_ATTEMPT/safe/watchdog-ownership.lock"
                flock 8
                nonce=$(cat "$WATCHDOG_ATTEMPT/safe/watchdog-nonce")
                if ! grep -qx 'state=active' "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"; then flock -u 8; exit 0; fi
                if [ "$SCENARIO" = ready_rollback_race ]; then
                    printf 'nonce=%s\nstate=rollback\n' "$nonce" >"$WATCHDOG_ATTEMPT/safe/watchdog-ownership.$$"
                    mv "$WATCHDOG_ATTEMPT/safe/watchdog-ownership.$$" "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"
                    printf 'reason=test_ready_rollback_race\nnonce=%s\n' "$nonce" >"$WATCHDOG_ATTEMPT/safe/trigger"
                    rm -f "$WATCHDOG_ATTEMPT/safe/candidate-ready"
                    flock -u 8
                    "$ROLLBACK"
                    exit 0
                fi
                printf 'nonce=%s\ncandidate=ready\nwatchdog=armed\nphase=active\ncontainer_id=cid\nstarted_at=2026-09-05T00:00:00Z\nconfigured_image=%s\nconfig_identity=%s\n' "$nonce" "$TEST_CANDIDATE_REF" "$TEST_CANDIDATE_CONFIG" >"$WATCHDOG_ATTEMPT/safe/candidate-ready.$$"
                mv "$WATCHDOG_ATTEMPT/safe/candidate-ready.$$" "$WATCHDOG_ATTEMPT/safe/candidate-ready"
                printf 'nonce=%s\nstate=ready\n' "$nonce" >"$WATCHDOG_ATTEMPT/safe/watchdog-ownership.$$"
                mv "$WATCHDOG_ATTEMPT/safe/watchdog-ownership.$$" "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"
                flock -u 8
            fi
            ;;
        *) exit 1 ;;
    esac
    sleep 0.01
done
SH
    cat >"$ATTEMPT/rollback/rollback.sh" <<'SH'
#!/bin/bash
set -euo pipefail
printf 'rollback_invoked\n' >>"$ROLLBACK_MARKER"
if [ "${ROLLBACK_FAIL_BEFORE_RESTORE:-0}" = 1 ]; then exit 23; fi
if [ -s "$WATCHDOG_ATTEMPT/safe/prior-selector.env" ]; then
    cp "$WATCHDOG_ATTEMPT/safe/prior-selector.env" "$TEST_SELECTOR"
else
    printf 'LITELLM_IMAGE=%s\nUNCHANGED=value\n' "$TEST_ROLLBACK_REF" >"$TEST_SELECTOR"
fi
if [ "${ROLLBACK_STATUS:-0}" -ne 0 ]; then exit "$ROLLBACK_STATUS"; fi
rm -f "$WATCHDOG_ATTEMPT/safe/candidate-ready" "$WATCHDOG_ATTEMPT/safe/ready-request" "$WATCHDOG_ATTEMPT/safe/watchdog-active" "$WATCHDOG_ATTEMPT/safe/watchdog-pre-start" "$WATCHDOG_ATTEMPT/safe/rollback-required"
exit 0
SH
    cat >"$ATTEMPT/rollback/collect-watchdog-sample.sh" <<'SH'
#!/bin/bash
set -euo pipefail
exit 0
SH
    chmod 0700 "$ATTEMPT/rollback/watchdog.sh" "$ATTEMPT/rollback/rollback.sh" "$ATTEMPT/rollback/collect-watchdog-sample.sh"
}

run_case() {
    local scenario=$1
    shift
    local -a extra_environment=("$@")
    set +e
    /usr/bin/env "${extra_environment[@]}" \
    PATH="$MOCK:$PATH" \
    MAINTENANCE_TEST_MODE=1 \
    MAINTENANCE_ROOT="$ROOT" \
    MAINTENANCE_ATTEMPT="$ATTEMPT" \
    MAINTENANCE_WATCHDOG="$ATTEMPT/rollback/watchdog.sh" \
    MAINTENANCE_ROLLBACK="$ATTEMPT/rollback/rollback.sh" \
    MAINTENANCE_COLLECTOR="$ATTEMPT/rollback/collect-watchdog-sample.sh" \
    MAINTENANCE_STARTUP_ATTEMPTS=100 \
    MAINTENANCE_STARTUP_INTERVAL=0.01 \
    MAINTENANCE_WATCHDOG_GRACE=1 \
    VALIDATION_MARKER="$ATTEMPT/safe/controller-validation-complete" \
    ROLLBACK_MARKER="$ROLLBACK_MARKER" \
    REQUEST_MARKER="$REQUEST_MARKER" \
    TEST_SELECTOR="$ROOT/.env" \
    EVENTS="$EVENTS" \
    SCENARIO="$scenario" \
    WATCHDOG_ATTEMPT="$ATTEMPT" \
    TEST_CANDIDATE_REF="$CANDIDATE_REF" \
    TEST_CANDIDATE_CONFIG="$CANDIDATE_CONFIG" \
    TEST_ROLLBACK_REF="$ROLLBACK_REF" \
    ROLLBACK="$ATTEMPT/rollback/rollback.sh" \
    "$CONTROLLER" >"$W/$scenario.stdout" 2>"$W/$scenario.stderr"
    CASE_STATUS=$?
    set -e
}

assert_preserved() {
    [ "$CREDENTIAL_BEFORE" = "$(sha256sum "$ATTEMPT/safe/administrator-credential.fixture")" ]
    [ ! -e "$REQUEST_MARKER" ]
    grep -qx 'UNCHANGED=value' "$ROOT/.env"
}

bash -n "$CONTROLLER"

prepare_case normal
run_case normal
[ "$CASE_STATUS" -eq 0 ]
[ ! -e "$ROLLBACK_MARKER" ]
grep -qx 'phase=active' "$ATTEMPT/safe/candidate-ready"
[ -e "$ATTEMPT/safe/rollback-required" ]
grep -qx 'state=ready' "$ATTEMPT/safe/watchdog-ownership"
grep -q "^LITELLM_IMAGE=$CANDIDATE_REF$" "$ROOT/.env"
assert_preserved
kill -TERM "$(cat "$ATTEMPT/safe/watchdog.pid")"
printf 'normal_startup_handshake=pass\n'

prepare_case startup_failure
run_case startup_failure MAINTENANCE_STARTUP_ATTEMPTS=1
[ "$CASE_STATUS" -eq 1 ]
grep -qx rollback_invoked "$ROLLBACK_MARKER"
[ ! -e "$ATTEMPT/safe/candidate-ready" ]
grep -q "^LITELLM_IMAGE=$ROLLBACK_REF$" "$ROOT/.env"
assert_preserved
printf 'startup_failure_rollback=pass\n'

prepare_case rollback_failure
run_case startup_failure MAINTENANCE_STARTUP_ATTEMPTS=1 ROLLBACK_STATUS=23
[ "$CASE_STATUS" -eq 70 ]
grep -qx rollback_invoked "$ROLLBACK_MARKER"
[ "$SELECTOR_BEFORE" = "$(sha256sum "$ROOT/.env")" ]
assert_preserved
printf 'rollback_failure_restores_prior_selector=pass\n'

prepare_case ready_rollback_race
run_case ready_rollback_race
[ "$CASE_STATUS" -eq 1 ]
grep -qx rollback_invoked "$ROLLBACK_MARKER"
[ ! -e "$ATTEMPT/safe/candidate-ready" ]
grep -q "^LITELLM_IMAGE=$ROLLBACK_REF$" "$ROOT/.env"
assert_preserved
printf 'watcher_ready_rollback_race=pass\n'

prepare_case final_boundary
cat >"$ATTEMPT/rollback/final-trip.sh" <<'SH'
#!/bin/bash
set -euo pipefail
touch "$WATCHDOG_ATTEMPT/safe/rollback-intent"
exec 8>"$WATCHDOG_ATTEMPT/safe/watchdog-ownership.lock"
flock 8
grep -qx 'state=ready' "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"
nonce=$(cat "$WATCHDOG_ATTEMPT/safe/watchdog-nonce")
printf 'nonce=%s\nstate=rollback\n' "$nonce" >"$WATCHDOG_ATTEMPT/safe/watchdog-ownership.tmp"
mv "$WATCHDOG_ATTEMPT/safe/watchdog-ownership.tmp" "$WATCHDOG_ATTEMPT/safe/watchdog-ownership"
rm -f "$WATCHDOG_ATTEMPT/safe/candidate-ready"
SH
chmod 0700 "$ATTEMPT/rollback/final-trip.sh"
run_case final_boundary MAINTENANCE_TEST_READY_LOCK_HOOK="$ATTEMPT/rollback/final-trip.sh"
[ "$CASE_STATUS" -eq 1 ]
grep -qx 'controller failure: watcher_ready_ownership_lost' "$W/final_boundary.stderr"
[ ! -e "$ATTEMPT/safe/candidate-ready" ]
[ "$SELECTOR_BEFORE" = "$(sha256sum "$ROOT/.env")" ]
assert_preserved
printf 'rollback_after_ready_before_acceptance=pass\n'

prepare_case signal_gap
run_case signal_gap MAINTENANCE_TEST_SIGNAL_AFTER_ROLLBACK_REQUIRED=TERM
[ "$CASE_STATUS" -eq 128 ]
grep -qx rollback_invoked "$ROLLBACK_MARKER"
[ ! -e "$ATTEMPT/safe/rollback-required" ]
grep -q "^LITELLM_IMAGE=$ROLLBACK_REF$" "$ROOT/.env"
assert_preserved
printf 'signal_between_state_and_selector_rollback=pass\n'

prepare_case signal_rollback_failure
run_case signal_rollback_failure MAINTENANCE_TEST_SIGNAL_AFTER_ROLLBACK_REQUIRED=TERM ROLLBACK_FAIL_BEFORE_RESTORE=1
[ "$CASE_STATUS" -eq 70 ]
grep -qx rollback_invoked "$ROLLBACK_MARKER"
[ "$SELECTOR_BEFORE" = "$(sha256sum "$ROOT/.env")" ]
assert_preserved
printf 'preselector_signal_rollback_failure_preserves_selector=pass\n'

if grep -Eq '\|\|\{|&&\{' "$CONTROLLER"; then
    exit 1
fi

printf 'controller_bash_n=pass\n'
printf 'watcher_phase_handshake=pass\n'
printf 'credential_unchanged=pass\n'
printf 'request_not_attempted=pass\n'
printf 'compound_fallback_syntax=pass\n'
printf 'tests=pass\n'
