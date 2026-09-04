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
utc=2026-09-04T00:00:00Z; mono=$n; phase=candidate; cid=cid; started=start; configured="$CANDIDATE"; runtime="$CANDIDATE_RUNTIME"; config="$CONFIG"; source="$SOURCE"; exit_code=0
cur=1073741824; peak=1073741824; cgroup_swap=0; oom_event=0; oom_kill_event=0; available=68719476736; host_swap=0; psi=0.00
pids=10; cpu=$((n * 10000)); restart=0; oom=false; health=healthy; rss=536870912; anonymous=268435456; private_dirty=134217728; threads=10; fds=20; sockets=2
postgres=10; redis_clients=10; redis_blocked=0; disk_bytes=107374182400; disk_percent=20; dependencies=expected-dependencies; protected=pass
live=200; ready=200; kernel_oom=0; request=pre; control=pass
case "$s" in
    healthy) ;;
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
case "${COMMAND_MODE:-}" in
    timeout) sleep 10 ;;
    error) exit 19 ;;
esac
case "${1:-}" in
    inspect)
        if [ "${2:-}" = litellm ]; then
            printf '[{"Config":{"Image":"candidate"},"Image":"runtime","Id":"cid","State":{"StartedAt":"start","Pid":4242,"ExitCode":0,"OOMKilled":false,"Health":{"Status":"healthy"}},"RestartCount":0}]\n'
        else
            printf '[{"Id":"dep","Image":"dep-image","State":{"StartedAt":"start","Status":"running","Health":{"Status":"healthy"},"OOMKilled":false},"RestartCount":0}]\n'
        fi
        ;;
    image)
        printf '[{"Id":"config","Config":{"Labels":{"org.opencontainers.image.revision":"source"}}}]\n'
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
CANDIDATE_RUNTIME=sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
CONFIG=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
SOURCE=bf58974a935521fa570fa7e280c51a00b2e5b54e

reset_run() {
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
    start_run "$scenario"
    wait "$P"
    P=
    grep -qx "reason=$reason" "$A/safe/trigger"
    [ "$(wc -l <"$W/marker")" -eq 1 ]
    printf '%s=pass\n' "$reason"
}

for signal in HUP INT TERM; do
    reset_run
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
    [ "$status" -ne 0 ]
    printf 'generated_%s_%s=pass\n' "$command_name" "$command_mode"
}
for command_name in docker postgres redis health dependency journal; do
    run_generated_collector_case "$command_name" timeout
    run_generated_collector_case "$command_name" error
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

grep -Fq 'docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm' "$G/rollback.sh"
grep -Fq 'sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04' "$G/rollback.sh"
printf 'exact_rollback=pass\ntests=pass\n'
