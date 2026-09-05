#!/bin/bash
set -euo pipefail

H=$(cd "$(dirname "$0")" && pwd)
W=$(mktemp -d)
P=
trap 'if [ -n "$P" ]; then kill -KILL "$P" 2>/dev/null || :; wait "$P" 2>/dev/null || :; fi; rm -rf "$W"' EXIT
G="$W/generated"
"$H/generate-watchdog-harness.sh" "$G" >"$W/generation.log"
for script in "$G"/*.sh; do bash -n "$script"; done

A="$W/attempt"
mkdir -p "$A/rollback" "$A/raw" "$A/safe" "$W/mock"
cp "$G/watchdog.sh" "$A/rollback/watchdog.sh"
printf 'expected-dependencies\n' >"$A/safe/dependencies.digest"
printf 'placeholder  file\n' >"$A/safe/protected-baseline.sha256"
printf 'pass\n' >"$A/safe/control-state"
printf '999999999\n' >"$A/safe/maintenance-deadline-monotonic"
printf 'armed\n' >"$A/safe/rollback-confidence"
printf '2026-09-04T00:00:00Z\n' >"$A/safe/watchdog-start-wall"
printf 'active\n' >"$A/safe/watchdog-phase"
printf 'test-nonce\n' >"$A/safe/watchdog-nonce"
printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"

cat >"$A/rollback/rollback.sh" <<'SH'
#!/bin/bash
printf 'rollback\n' >>"$MARKER"
if [ -s "${CLIENT_PID_FILE:-}" ]; then
    client_pid=$(cat "$CLIENT_PID_FILE")
    if kill -0 "$client_pid" 2>/dev/null; then
        printf 'client_alive\n' >>"$MARKER"
    else
        printf 'client_stopped\n' >>"$MARKER"
    fi
fi
exit "${ROLLBACK_RC:-0}"
SH
chmod 0700 "$A/rollback/rollback.sh"
bash -n "$A/rollback/rollback.sh"

cat >"$W/mock/collector.sh" <<'SH'
#!/bin/bash
set -euo pipefail
n=$(cat "$MOCK/count")
n=$((n + 1))
printf '%s\n' "$n" >"$MOCK/count"
s=$SCENARIO
if [[ "$s" == failure_* ]]; then printf '%s\n' "${s#failure_}" >&2; exit 1; fi
phase=active
if [[ "$s" == startup_* ]]; then phase=pre-start; s=${s#startup_}; fi
utc=2026-09-04T00:00:00Z; mono=$n; cid=cid; started=start; configured="$CANDIDATE"; runtime="$CANDIDATE_RUNTIME"; config="$CONFIG"; source="$SOURCE"; exit_code=0
cur=1073741824; peak=1073741824; cgroup_swap=0; oom_event=0; oom_kill_event=0; available=68719476736; host_swap=0; psi=0.00
pids=10; cpu=$((n * 10000)); restart=0; oom=false; health=healthy; rss=536870912; anonymous=268435456; private_dirty=134217728; threads=10; fds=20; sockets=2
postgres=10; redis_clients=10; redis_blocked=0; disk_bytes=107374182400; disk_percent=20; dependencies=expected-dependencies; protected=pass
live=200; ready=200; kernel_oom=0; request=pre; control=pass
case "$s" in
    healthy) ;;
    starting) health=starting; live=0; ready=0 ;;
    initial_oom_event) oom_event=1 ;;
    memory_absolute) cur=8589934592 ;;
    available) available=34359738367 ;;
    swap) host_swap=536870913 ;;
    psi) psi=0.11 ;;
    restart) restart=1 ;;
    oom) oom=true ;;
    exit_137) exit_code=137 ;;
    pids) pids=501 ;;
    fds) fds=8193 ;;
    postgres) postgres=80 ;;
    redis_clients) redis_clients=500 ;;
    disk_bytes) disk_bytes=21474836479 ;;
    disk_percent) disk_percent=86 ;;
    dependency) dependencies=drift ;;
    protected) protected=fail ;;
    liveliness) live=503 ;;
    readiness) ready=503 ;;
    kernel_oom) kernel_oom=1 ;;
    health) health=unhealthy ;;
    identity_image) configured=wrong ;;
    identity_config) config=wrong ;;
    identity_source) source=wrong ;;
    identity_container) if [ "$n" -gt 1 ]; then cid=changed; fi ;;
    cgroup_oom) if [ "$n" -gt 1 ]; then oom_event=1; fi ;;
    cgroup_oom_kill) if [ "$n" -gt 1 ]; then oom_kill_event=1; fi ;;
    cpu) cpu=$((n * 90000000)) ;;
    redis_blocked) redis_blocked=1 ;;
    rate) cur=$((1073741824 + (n - 1) * 536870912)) ;;
    baseline) request=active ;;
    memory)
        if [ "$n" -le 30 ]; then cur=1073741824; [ "$n" -ne 17 ] || cur=7516192768; else request=active; cur=9663676416; fi
        ;;
    baseline_max)
        if [ "$n" -le 30 ]; then cur=1073741824; [ "$n" -ne 17 ] || cur=7516192768; else request=active; cur=9126805504; fi
        ;;
    memory_steady)
        if [ "$n" -gt 30 ]; then request=post; cur=1610612736; fi
        ;;
    post_memory_growth|post_rss_growth|post_anonymous_growth|post_dirty_growth|post_threads_growth|post_pids_growth|post_fds_growth)
        if [ "$n" -gt 30 ]; then
            request=post; d=$((n - 30))
            case "$s" in
                post_memory_growth) cur=$((1073741824 + d)) ;;
                post_rss_growth) rss=$((536870912 + d)) ;;
                post_anonymous_growth) anonymous=$((268435456 + d)) ;;
                post_dirty_growth) private_dirty=$((134217728 + d)) ;;
                post_threads_growth) threads=$((10 + d)) ;;
                post_pids_growth) pids=$((10 + d)) ;;
                post_fds_growth) fds=$((20 + d)) ;;
            esac
        fi
        ;;
    control_*) control=${s#control_} ;;
    malformed_schema) printf 'bad\n'; exit 0 ;;
    malformed_numeric) cur=bad ;;
    malformed_enum) oom=maybe ;;
    sample_hang) sleep 10 ;;
    *) printf 'unknown scenario\n' >&2; exit 1 ;;
esac
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
 "$utc" "$mono" "$phase" "$cid" "$started" "$configured" "$runtime" "$config" "$source" "$exit_code" "$cur" "$peak" "$cgroup_swap" "$oom_event" "$oom_kill_event" "$available" "$host_swap" "$psi" "$pids" "$cpu" "$restart" "$oom" "$health" "$rss" "$anonymous" "$private_dirty" "$threads" "$fds" "$sockets" "$postgres" "$redis_clients" "$redis_blocked" "$disk_bytes" "$disk_percent" "$dependencies" "$protected" "$live" "$ready" "$kernel_oom" "$request" "$control" armed 999999999
SH
chmod 0700 "$W/mock/collector.sh"
bash -n "$W/mock/collector.sh"

cat >"$W/mock/docker" <<'SH'
#!/bin/bash
case "${1:-}" in
    inspect)
        [ "$#" -eq 6 ] && [ "$2" = --type ] && [ "$3" = container ] && [ "$4" = --format ] || exit 97
        if [ "$6" = litellm ]; then
            expected='[{{json .Config.Image}},{{json .Image}},{{json .Id}},{{json .State.StartedAt}},{{json .State.Pid}},{{json .State.ExitCode}},{{json .RestartCount}},{{json .State.OOMKilled}},{{if .State.Health}}{{json .State.Health.Status}}{{else}}"none"{{end}}]'
        else
            case "$6" in postgresql|litellm-redis|defend-memory-mcp|defend-memory-memory-agent-gateway|defend-memory-postgres|defend-memory-qdrant|defend-memory-neo4j) : ;; *) exit 97 ;; esac
            expected='[{{json .Id}},{{json .Image}},{{json .State.StartedAt}},{{json .State.Status}},{{if .State.Health}}{{json .State.Health.Status}}{{else}}"none"{{end}},{{json .RestartCount}},{{json .State.OOMKilled}}]'
        fi
        [ "$5" = "$expected" ] || exit 97
        ;;
    image)
        [ "$#" -eq 5 ] && [ "$2" = inspect ] && [ "$3" = --format ] || exit 97
        [ "$4" = '[{{json .Id}},{{json (index .Config.Labels "org.opencontainers.image.revision")}}]' ] || exit 97
        ;;
esac
case "${COMMAND_MODE:-}" in
    timeout) sleep 10 ;;
    error) exit 19 ;;
esac
case "${1:-}" in
    inspect)
        if [ "$6" = litellm ]; then
            printf '["candidate","runtime","cid","start",4242,0,0,false,"healthy"]\n'
        else
            printf '["dep","dep-image","start","running","healthy",0,false]\n'
        fi
        ;;
    image)
        printf '["config","source"]\n'
        ;;
    exec)
        case "${2:-}" in
            postgresql)
                printf '10\n'
                ;;
            litellm-redis)
                printf 'connected_clients:10\nblocked_clients:0\n'
                ;;
        esac
        ;;
esac
SH
cat >"$W/mock/curl" <<'SH'
#!/bin/bash
case "${COMMAND_MODE:-}" in timeout) sleep 10 ;; error) exit 22 ;; esac
printf '200'
SH
cat >"$W/mock/sudo" <<'SH'
#!/bin/bash
if [ "${1:-}" = -n ]; then shift; fi
if [ "${1:-}" = journalctl ]; then
    case "${COMMAND_MODE:-}" in timeout) sleep 10 ;; error) exit 23 ;; match) printf 'oom-kill: test\n'; exit 0 ;; esac
    exit 0
fi
exec "$@"
SH
chmod 0700 "$W/mock/docker" "$W/mock/curl" "$W/mock/sudo"

CANDIDATE=docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
CANDIDATE_RUNTIME=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
CONFIG=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
SOURCE=bf58974a935521fa570fa7e280c51a00b2e5b54e

reset_run() {
    rm -f "$A/safe/rollback-intent" "$A/safe/ready-request" "$A/safe/candidate-ready" "$A/safe/watchdog-active"
    rm -f "$A/safe/trigger" "$A/safe/collector-error" "$A/raw/watchdog.tsv" "$W/marker" "$W/out"
    printf '0\n' >"$W/mock/count"
    P=
}

start_run() {
    scenario=$1
    limit=${2:-0}
    MOCK="$W/mock" SCENARIO="$scenario" CANDIDATE="$CANDIDATE" CANDIDATE_RUNTIME="$CANDIDATE_RUNTIME" CONFIG="$CONFIG" SOURCE="$SOURCE" \
        MARKER="$W/marker" WATCHDOG_ATTEMPT="$A" WATCHDOG_COLLECTOR="$W/mock/collector.sh" \
        WATCHDOG_ROLLBACK="$A/rollback/rollback.sh" WATCHDOG_SAMPLE_SECONDS=0.001 WATCHDOG_SAMPLE_TIMEOUT=0.10 WATCHDOG_PROOF_SAMPLE_LIMIT="$limit" \
        WATCHDOG_EXPECTED_DEPENDENCIES=expected-dependencies "$A/rollback/watchdog.sh" >"$W/out" 2>&1 &
    P=$!
}

expect_trip() {
    scenario=$1
    reason=$2
    reset_run
    if [[ "$scenario" == startup_* ]]; then printf 'pre-start\n' >"$A/safe/watchdog-phase"; else printf 'active\n' >"$A/safe/watchdog-phase"; fi
    printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
    start_run "$scenario"
    wait "$P"
    P=
    grep -qx "reason=$reason" "$A/safe/trigger"
    [ "$(wc -l <"$W/marker")" -eq 1 ]
    printf '%s=pass\n' "$reason"
}

while read -r scenario reason; do expect_trip "$scenario" "$reason"; done <<'STARTUP_CASES'
startup_memory_absolute memory_absolute
startup_rate rate
startup_cgroup_oom cgroup_oom
startup_cgroup_oom_kill cgroup_oom_kill
startup_restart restart
startup_pids pids
startup_fds fds
startup_initial_oom_event cgroup_oom
startup_oom oom
startup_exit_137 exit_137
STARTUP_CASES
printf 'startup_candidate_resource_gates=pass\n'

reset_run
printf 'pre-start\n' >"$A/safe/watchdog-phase"
printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
start_run startup_starting 4
wait "$P"
P=
[ ! -e "$W/marker" ]
[ -s "$A/safe/watchdog-pre-start" ]
[ ! -e "$A/safe/candidate-ready" ]
printf 'startup_health_tolerant_resources_sampled=pass\n'

reset_run
printf 'active\n' >"$A/safe/watchdog-phase"
printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
printf 'nonce=test-nonce\nrequest=ready\n' >"$A/safe/ready-request"
start_run healthy 2
wait "$P"
P=
grep -qx 'nonce=test-nonce' "$A/safe/candidate-ready"
grep -qx 'state=ready' "$A/safe/watchdog-ownership"
[ ! -e "$W/marker" ]
printf 'generated_watcher_nonce_ready=pass\n'

reset_run
printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
printf 'nonce=stale-nonce\nrequest=ready\n' >"$A/safe/ready-request"
start_run healthy
wait "$P"
P=
grep -qx 'reason=ready_handshake' "$A/safe/trigger"
grep -qx 'state=rollback' "$A/safe/watchdog-ownership"
[ ! -e "$A/safe/candidate-ready" ]
printf 'generated_watcher_stale_nonce_rejected=pass\n'

reset_run
printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
printf 'nonce=test-nonce\nrequest=ready\n' >"$A/safe/ready-request"
touch "$A/safe/rollback-intent"
start_run healthy
wait "$P"
P=
grep -qx 'reason=ready_handshake' "$A/safe/trigger"
[ ! -e "$A/safe/candidate-ready" ]
printf 'generated_watcher_rollback_intent_wins=pass\n'

for signal in HUP INT TERM; do
    reset_run
    printf 'active\n' >"$A/safe/watchdog-phase"
    printf 'nonce=test-nonce\nstate=active\n' >"$A/safe/watchdog-ownership"
    set +e
    MOCK="$W/mock" SCENARIO=healthy CANDIDATE="$CANDIDATE" CANDIDATE_RUNTIME="$CANDIDATE_RUNTIME" CONFIG="$CONFIG" SOURCE="$SOURCE" MARKER="$W/marker" \
        WATCHDOG_ATTEMPT="$A" WATCHDOG_COLLECTOR="$W/mock/collector.sh" WATCHDOG_ROLLBACK="$A/rollback/rollback.sh" \
        WATCHDOG_SAMPLE_SECONDS=0.001 WATCHDOG_SAMPLE_TIMEOUT=0.10 WATCHDOG_EXPECTED_DEPENDENCIES=expected-dependencies \
        timeout --preserve-status --signal="$signal" 0.05 "$A/rollback/watchdog.sh" >"$W/out" 2>&1
    signal_status=$?
    set -e
    [ "$signal_status" -eq 0 ]
    grep -qx "reason=signal_$(tr '[:upper:]' '[:lower:]' <<<"$signal")" "$A/safe/trigger"
    [ "$(wc -l <"$W/marker")" -eq 1 ]
    printf 'signal_%s=pass\n' "$(tr '[:upper:]' '[:lower:]' <<<"$signal")"
done

while read -r scenario reason; do expect_trip "$scenario" "$reason"; done <<'CASES'
memory_absolute memory_absolute
available available
swap swap
psi psi
restart restart
oom oom
exit_137 exit_137
pids pids
fds fds
postgres postgres
redis_clients redis_clients
disk_bytes disk_bytes
disk_percent disk_percent
dependency dependency
protected protected
liveliness liveliness
readiness readiness
kernel_oom kernel_oom
health health
identity_image identity_image
identity_config identity_config
identity_source identity_source
identity_container identity_container
cgroup_oom cgroup_oom
cgroup_oom_kill cgroup_oom_kill
cpu cpu
redis_blocked redis_blocked
rate rate
baseline baseline
memory memory
memory_steady memory_steady
post_memory_growth post_memory_growth
post_rss_growth post_rss_growth
post_anonymous_growth post_anonymous_growth
post_dirty_growth post_dirty_growth
post_threads_growth post_threads_growth
post_pids_growth post_pids_growth
post_fds_growth post_fds_growth
control_data control_data
control_security control_security
control_secret control_secret
control_observability control_observability
control_rollback_confidence control_rollback_confidence
control_maintenance_deadline control_maintenance_deadline
malformed_schema instrumentation_schema
malformed_numeric instrumentation_numeric
malformed_enum instrumentation_oom
sample_hang instrumentation_sample_timeout
CASES

for failure in jq cgroup proc psi process fd socket cpu postgres redis disk dependency health identity oom data security secret observability; do
    expect_trip "failure_$failure" "instrumentation_$failure"
done

COLLECTOR_SANDBOX="$W/collector-sandbox"
mkdir -p "$COLLECTOR_SANDBOX/rollback" "$COLLECTOR_SANDBOX/safe"
cp "$G/collect-watchdog-sample.sh" "$COLLECTOR_SANDBOX/rollback/collect-watchdog-sample.sh"
printf '2026-09-04T00:00:00Z\n' >"$COLLECTOR_SANDBOX/safe/watchdog-start-wall"
printf 'active\n' >"$COLLECTOR_SANDBOX/safe/watchdog-phase"
printf 'test-nonce\n' >"$COLLECTOR_SANDBOX/safe/watchdog-nonce"
printf 'nonce=test-nonce\nstate=active\n' >"$COLLECTOR_SANDBOX/safe/watchdog-ownership"
printf 'pass\n' >"$COLLECTOR_SANDBOX/safe/control-state"
printf 'armed\n' >"$COLLECTOR_SANDBOX/safe/rollback-confidence"
printf '999999999\n' >"$COLLECTOR_SANDBOX/safe/maintenance-deadline-monotonic"
printf 'placeholder  file\n' >"$COLLECTOR_SANDBOX/safe/protected-baseline.sha256"
run_generated_collector_case() {
    command_name=$1
    command_mode=$2
    set +e
    PATH="$W/mock:$PATH" COMMAND_MODE="$command_mode" WATCHDOG_COMMAND_TEST="$command_name" WATCHDOG_ATTEMPT="$COLLECTOR_SANDBOX" WATCHDOG_COMMAND_TIMEOUT=0.02 \
        "$COLLECTOR_SANDBOX/rollback/collect-watchdog-sample.sh" >"$W/collector.out" 2>"$W/collector.err"
    status=$?
    set -e
    if [ "$command_mode" = timeout ]; then [ "$status" -eq 124 ]; else [ "$status" -ne 0 ] && [ "$status" -ne 97 ]; fi
    printf 'generated_%s_%s=pass\n' "$command_name" "$command_mode"
}
for command_name in docker image postgres redis health dependency journal; do
    run_generated_collector_case "$command_name" timeout
    run_generated_collector_case "$command_name" error
done

for command_name in docker image dependency; do
    PATH="$W/mock:$PATH" COMMAND_MODE=success WATCHDOG_COMMAND_TEST="$command_name" WATCHDOG_ATTEMPT="$COLLECTOR_SANDBOX" WATCHDOG_COMMAND_TIMEOUT=1 \
        "$COLLECTOR_SANDBOX/rollback/collect-watchdog-sample.sh" >"$W/collector.out"
    case "$command_name" in
        docker) expected='["candidate","runtime","cid","start",4242,0,0,false,"healthy"]' ;;
        image) expected='["config","source"]' ;;
        dependency) expected='["dep","dep-image","start","running","healthy",0,false]' ;;
    esac
    [ "$(cat "$W/collector.out")" = "$expected" ]
    printf 'fixed_projection_%s=pass\n' "$command_name"
done

PATH="$W/mock:$PATH" COMMAND_MODE=match WATCHDOG_COMMAND_TEST=journal WATCHDOG_ATTEMPT="$COLLECTOR_SANDBOX" WATCHDOG_COMMAND_TIMEOUT=0.02 \
    "$COLLECTOR_SANDBOX/rollback/collect-watchdog-sample.sh" >"$W/collector.out" 2>"$W/collector.err"
grep -qx 1 "$W/collector.out"
PATH="$W/mock:$PATH" COMMAND_MODE=nomatch WATCHDOG_COMMAND_TEST=journal WATCHDOG_ATTEMPT="$COLLECTOR_SANDBOX" WATCHDOG_COMMAND_TIMEOUT=0.02 \
    "$COLLECTOR_SANDBOX/rollback/collect-watchdog-sample.sh" >"$W/collector.out" 2>"$W/collector.err"
grep -qx 0 "$W/collector.out"
printf 'generated_journal_match_distinct=pass\n'

reset_run
start=$(date +%s.%N)
MOCK="$W/mock" SCENARIO=sample_hang CANDIDATE="$CANDIDATE" CANDIDATE_RUNTIME="$CANDIDATE_RUNTIME" CONFIG="$CONFIG" SOURCE="$SOURCE" \
    MARKER="$W/marker" WATCHDOG_ATTEMPT="$A" WATCHDOG_COLLECTOR="$W/mock/collector.sh" WATCHDOG_ROLLBACK="$A/rollback/rollback.sh" \
    WATCHDOG_SAMPLE_SECONDS=1 WATCHDOG_SAMPLE_TIMEOUT=0.75 WATCHDOG_EXPECTED_DEPENDENCIES=expected-dependencies \
    "$A/rollback/watchdog.sh" >"$W/out" 2>&1 &
P=$!
wait "$P"
P=
end=$(date +%s.%N)
elapsed=$(awk -v s="$start" -v e="$end" 'BEGIN{printf "%.3f",e-s}')
awk -v elapsed="$elapsed" 'BEGIN{exit !(elapsed>=2.70 && elapsed<3.50)}'
grep -qx 'reason=instrumentation_sample_timeout' "$A/safe/trigger"
printf 'three_timeout_cycles_elapsed_%s=pass\n' "$elapsed"

for prerequisite in protected-baseline.sha256 control-state maintenance-deadline-monotonic rollback-confidence dependencies.digest watchdog-start-wall; do
    reset_run
    mv "$A/safe/$prerequisite" "$A/safe/$prerequisite.saved"
    start_run healthy
    wait "$P"
    P=
    mv "$A/safe/$prerequisite.saved" "$A/safe/$prerequisite"
    reason=${prerequisite//./_}
    grep -qx "reason=prerequisite_$reason" "$A/safe/trigger"
    [ "$(wc -l <"$W/marker")" -eq 1 ]
    printf 'missing_%s=pass\n' "$reason"
done

reset_run
printf 'expired\n' >"$A/safe/rollback-confidence"
start_run healthy
wait "$P"
P=
grep -qx 'reason=prerequisite_rollback_confidence' "$A/safe/trigger"
printf 'invalid_rollback_confidence=pass\n'
printf 'armed\n' >"$A/safe/rollback-confidence"

reset_run
printf 'blocked\n' >"$A/safe/control-state"
start_run healthy
wait "$P"
P=
grep -qx 'reason=prerequisite_control' "$A/safe/trigger"
printf 'invalid_control=pass\n'
printf 'pass\n' >"$A/safe/control-state"

reset_run
printf '0\n' >"$A/safe/maintenance-deadline-monotonic"
start_run healthy
wait "$P"
P=
grep -qx 'reason=prerequisite_deadline' "$A/safe/trigger"
printf 'expired_deadline=pass\n'
printf '999999999\n' >"$A/safe/maintenance-deadline-monotonic"

reset_run
sleep 10 &
client_pid=$!
printf '%s\n' "$client_pid" >"$A/safe/client.pid"
CLIENT_PID_FILE="$A/safe/client.pid"
export CLIENT_PID_FILE
start_run sample_hang
sleep 0.005
kill -TERM "$P"
wait "$P"
P=
unset CLIENT_PID_FILE
grep -qx 'reason=signal_term' "$A/safe/trigger"
grep -qx 'client_stopped' "$W/marker"
if kill -0 "$client_pid" 2>/dev/null; then exit 1; fi
rm -f "$A/safe/client.pid"
printf 'signal_hung_sample_client_before_rollback=pass\n'

reset_run
start_run baseline_max 31
wait "$P"
P=
[ ! -e "$W/marker" ]
[ ! -e "$A/safe/trigger" ]
[ "$(awk 'END{print NR-1}' "$A/raw/watchdog.tsv")" -eq 31 ]
printf 'baseline_final_30_max=pass\n'

reset_run
ROLLBACK_RC=23
export ROLLBACK_RC
start_run pids
set +e
wait "$P"
status=$?
set -e
P=
unset ROLLBACK_RC
[ "$status" -eq 23 ]
grep -qx 'reason=pids' "$A/safe/trigger"
printf 'rollback_failure=pass\n'

PRODUCTION_ROOT="$W/production"
PRODUCTION_ATTEMPT="$W/production-attempt"
PROOF_ROOT="$W/proof"
mkdir -p "$PRODUCTION_ROOT/releases" "$PRODUCTION_ATTEMPT/raw" "$PRODUCTION_ATTEMPT/safe" "$PROOF_ROOT/attempt/raw" "$PROOF_ROOT/attempt/safe"
PRODUCTION_POINTER="$PRODUCTION_ROOT/releases/TASK-2026-09-03-006.active"
printf '%s\n' "$PRODUCTION_ATTEMPT" >"$PRODUCTION_POINTER"
printf 'production-selector\n' >"$PRODUCTION_ROOT/.env"
printf 'production-recreate\n' >"$PRODUCTION_ATTEMPT/raw/rollback.log"
printf 'production-control\n' >"$PRODUCTION_ATTEMPT/safe/control-state"
PRODUCTION_STATE_BEFORE=$(sha256sum "$PRODUCTION_POINTER" "$PRODUCTION_ROOT/.env" "$PRODUCTION_ATTEMPT/raw/rollback.log" "$PRODUCTION_ATTEMPT/safe/control-state")

PROOF_ATTEMPT="$PROOF_ROOT/attempt"
printf 'expected-dependencies\n' >"$PROOF_ATTEMPT/safe/dependencies.digest"
printf 'placeholder  file\n' >"$PROOF_ATTEMPT/safe/protected-baseline.sha256"
printf 'pass\n' >"$PROOF_ATTEMPT/safe/control-state"
printf '999999999\n' >"$PROOF_ATTEMPT/safe/maintenance-deadline-monotonic"
printf 'armed\n' >"$PROOF_ATTEMPT/safe/rollback-confidence"
printf '2026-09-04T00:00:00Z\n' >"$PROOF_ATTEMPT/safe/watchdog-start-wall"
printf 'rollback\n' >"$PROOF_ATTEMPT/safe/watchdog-phase"
cp "$W/mock/collector.sh" "$W/mock/proof-collector.sh"
python3 - "$W/mock/proof-collector.sh" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
path.write_text(path.read_text().replace("phase=active", "phase=rollback", 1))
PY
chmod 0700 "$W/mock/proof-collector.sh"

MOCK="$W/mock" SCENARIO=healthy CANDIDATE="$CANDIDATE" CANDIDATE_RUNTIME="$CANDIDATE_RUNTIME" CONFIG="$CONFIG" SOURCE="$SOURCE" \
    WATCHDOG_ROOT="$PRODUCTION_ROOT" WATCHDOG_PROOF_COLLECTOR="$W/mock/proof-collector.sh" WATCHDOG_SAMPLE_SECONDS=0.001 WATCHDOG_SAMPLE_TIMEOUT=0.10 \
    "$G/run-watchdog-proof.sh" "$PROOF_ROOT" >"$W/proof.out"
PRODUCTION_STATE_AFTER=$(sha256sum "$PRODUCTION_POINTER" "$PRODUCTION_ROOT/.env" "$PRODUCTION_ATTEMPT/raw/rollback.log" "$PRODUCTION_ATTEMPT/safe/control-state")
[ "$PRODUCTION_STATE_BEFORE" = "$PRODUCTION_STATE_AFTER" ]
[ "$(cat "$PROOF_ROOT/TASK-2026-09-03-006.proof.active")" = "$PROOF_ATTEMPT" ]
[ "$(awk 'END{print NR-1}' "$PROOF_ATTEMPT/raw/watchdog.tsv")" -eq 31 ]
[ ! -e "$PROOF_ATTEMPT/safe/proof-rollback-invoked" ]
[ ! -e "$PROOF_ATTEMPT/raw/proof-rollback.log" ]
[ ! -e "$PRODUCTION_ATTEMPT/safe/trigger" ]
grep -qx 'proof_samples=31' "$W/proof.out"
printf 'proof_31_samples=pass\nproof_owned_pointer_log_control=pass\nproof_no_cross_state_mutation=pass\n'

reset_run
set +e
MOCK="$W/mock" SCENARIO=failure_jq CANDIDATE="$CANDIDATE" CANDIDATE_RUNTIME="$CANDIDATE_RUNTIME" CONFIG="$CONFIG" SOURCE="$SOURCE" \
    WATCHDOG_ROOT="$PRODUCTION_ROOT" WATCHDOG_PROOF_COLLECTOR="$W/mock/proof-collector.sh" WATCHDOG_SAMPLE_SECONDS=0.001 WATCHDOG_SAMPLE_TIMEOUT=0.10 \
    "$G/run-watchdog-proof.sh" "$PROOF_ROOT" >"$W/proof-trip.out" 2>&1
proof_trip_status=$?
set -e
[ "$proof_trip_status" -eq 1 ]
grep -qx 'proof_rollback_invoked' "$PROOF_ATTEMPT/raw/proof-rollback.log"
[ "$PRODUCTION_STATE_BEFORE" = "$(sha256sum "$PRODUCTION_POINTER" "$PRODUCTION_ROOT/.env" "$PRODUCTION_ATTEMPT/raw/rollback.log" "$PRODUCTION_ATTEMPT/safe/control-state")" ]
printf 'proof_failure_noop_rollback=pass\nproof_failure_no_cross_state_mutation=pass\n'

rm -f "$PROOF_ROOT/TASK-2026-09-03-006.proof.active"
ln -s "$PRODUCTION_POINTER" "$PROOF_ROOT/TASK-2026-09-03-006.proof.active"
set +e
WATCHDOG_ROOT="$PRODUCTION_ROOT" "$G/run-watchdog-proof.sh" "$PROOF_ROOT" >"$W/linked-pointer.out" 2>&1
linked_pointer_status=$?
set -e
[ "$linked_pointer_status" -eq 66 ]
rm "$PROOF_ROOT/TASK-2026-09-03-006.proof.active"
printf 'proof_rejects_production_pointer_link=pass\n'

mv "$PROOF_ATTEMPT/safe/control-state" "$PROOF_ATTEMPT/safe/control-state.saved"
ln -s "$PRODUCTION_ATTEMPT/safe/control-state" "$PROOF_ATTEMPT/safe/control-state"
set +e
WATCHDOG_ROOT="$PRODUCTION_ROOT" "$G/run-watchdog-proof.sh" "$PROOF_ROOT" >"$W/linked-control.out" 2>&1
linked_control_status=$?
set -e
[ "$linked_control_status" -eq 66 ]
rm "$PROOF_ATTEMPT/safe/control-state"
mv "$PROOF_ATTEMPT/safe/control-state.saved" "$PROOF_ATTEMPT/safe/control-state"
printf 'proof_rejects_production_control_link=pass\n'

mv "$PROOF_ATTEMPT/raw" "$PROOF_ATTEMPT/raw.saved"
ln -s "$PRODUCTION_ATTEMPT/raw" "$PROOF_ATTEMPT/raw"
set +e
WATCHDOG_ROOT="$PRODUCTION_ROOT" "$G/run-watchdog-proof.sh" "$PROOF_ROOT" >"$W/linked-log.out" 2>&1
linked_log_status=$?
set -e
[ "$linked_log_status" -eq 66 ]
rm "$PROOF_ATTEMPT/raw"
mv "$PROOF_ATTEMPT/raw.saved" "$PROOF_ATTEMPT/raw"
[ "$PRODUCTION_STATE_BEFORE" = "$(sha256sum "$PRODUCTION_POINTER" "$PRODUCTION_ROOT/.env" "$PRODUCTION_ATTEMPT/raw/rollback.log" "$PRODUCTION_ATTEMPT/safe/control-state")" ]
printf 'proof_rejects_production_log_link=pass\n'

set +e
WATCHDOG_ROOT="$PRODUCTION_ROOT" "$G/run-watchdog-proof.sh" "$PRODUCTION_ROOT/proof" >"$W/unsafe-proof.out" 2>&1
unsafe_proof_status=$?
set -e
[ "$unsafe_proof_status" -eq 65 ]
printf 'proof_rejects_production_root=pass\n'

grep -Fq 'docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm' "$G/rollback.sh"
grep -Fq 'sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04' "$G/rollback.sh"
# shellcheck disable=SC2016
grep -Fq 'ROLLBACK=${WATCHDOG_ROLLBACK:-$A/rollback/rollback.sh}' "$G/watchdog.sh"
# shellcheck disable=SC2016
grep -Fq 'ROLLBACK="$SCRIPT_DIRECTORY/proof-rollback.sh"' "$G/run-watchdog-proof.sh"
printf 'exact_rollback=pass\nreal_watcher_exact_rollback=pass\nproof_real_rollback_separation=pass\ntests=pass\n'
