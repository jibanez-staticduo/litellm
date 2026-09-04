#!/bin/bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
    printf 'usage: %s OUTPUT_DIRECTORY\n' "$0" >&2
    exit 64
fi

output_directory=$1
mkdir -p "$output_directory"

cat >"$output_directory/rollback.sh" <<'SH'
#!/bin/bash
set -euo pipefail
R=/home/staticduo/docker/litellm
A=$(cat "$R/releases/TASK-2026-09-03-006.active")
P=docker.staticduo.com/litellm@sha256:1b7a6dc4514b0f43902a6ac38dfde269aeb902497e3d1bb5a09f75a1ccd5cc04
exec 9>"$A/rollback/lock"
flock 9
[ ! -e "$A/safe/rollback-complete" ] || exit 0
date -u +%FT%TZ >"$A/safe/rollback-start"
python3 - "$R/.env" "$P" <<'PY'
import os,pathlib,sys,tempfile
p=pathlib.Path(sys.argv[1]);r=sys.argv[2];s=p.stat();x=p.read_text().splitlines();assert sum(a.startswith('LITELLM_IMAGE=')for a in x)==1;y='\n'.join(('LITELLM_IMAGE='+r)if a.startswith('LITELLM_IMAGE=')else a for a in x)+'\n';f,t=tempfile.mkstemp(prefix='.r7.',dir=p.parent);os.fchmod(f,s.st_mode&511);os.write(f,y.encode());os.fsync(f);os.close(f);os.chown(t,s.st_uid,s.st_gid);os.replace(t,p)
PY
cd "$R"
docker compose --env-file .env -f docker-compose.yaml up -d --no-deps litellm >>"$A/raw/rollback.log" 2>&1
touch "$A/safe/rollback-complete"
SH

cat >"$output_directory/collect-watchdog-sample.sh" <<'SH'
#!/bin/bash
set -euo pipefail

R=/home/staticduo/docker/litellm
A=${WATCHDOG_ATTEMPT:-$(cat "$R/releases/TASK-2026-09-03-006.active")}
C=docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
C_RUNTIME=sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
if [ "${WATCHDOG_PROOF_ROLLBACK:-0}" = 1 ]; then
    COMMAND_TIMEOUT=${WATCHDOG_COMMAND_TIMEOUT:-1.00}
else
    COMMAND_TIMEOUT=${WATCHDOG_COMMAND_TIMEOUT:-0.20}
fi

bounded() {
    timeout --foreground --kill-after=0.05 "$COMMAND_TIMEOUT" "$@"
}

probe_kernel_oom() {
    journal_output=$(bounded sudo -n journalctl -k --since "$(bounded cat "$A/safe/watchdog-start-wall")" --no-pager) || return
    set +e
    bounded grep -Eq 'Out of memory: Killed process|oom-kill:' <<<"$journal_output"
    journal_match=$?
    set -e
    case "$journal_match" in
        0) printf '1\n' ;;
        1) printf '0\n' ;;
        *) return "$journal_match" ;;
    esac
}

if [ -n "${WATCHDOG_COMMAND_TEST:-}" ]; then
    case "$WATCHDOG_COMMAND_TEST" in
        docker) bounded docker inspect litellm >/dev/null ;;
        postgres) bounded docker exec postgresql psql -U postgres -d litellm -Atqc 'select count(*) from pg_stat_activity' >/dev/null ;;
        redis) bounded docker exec litellm-redis sh -lc 'export REDISCLI_AUTH="${REDIS_PASSWORD:?}"; exec redis-cli --raw INFO clients' >/dev/null ;;
        health) bounded curl -sS -o /dev/null --max-time "$COMMAND_TIMEOUT" http://127.0.0.1:4000/health/liveliness ;;
        dependency) bounded docker inspect postgresql >/dev/null ;;
        journal) probe_kernel_oom ;;
        *) exit 64 ;;
    esac
    exit
fi

i=$(bounded docker inspect litellm)
im=$(bounded jq -er '.[0].Config.Image | strings | select(length>0)' <<<"$i")
runtime=$(bounded jq -er '.[0].Image | strings | select(length>0)' <<<"$i")
cid=$(bounded jq -er '.[0].Id | strings | select(length>0)' <<<"$i")
started=$(bounded jq -er '.[0].State.StartedAt | strings | select(length>0)' <<<"$i")
pid=$(bounded jq -er '.[0].State.Pid | numbers | select(.>0)' <<<"$i")
exit_code=$(bounded jq -er '.[0].State.ExitCode | numbers' <<<"$i")
restart=$(bounded jq -er '.[0].RestartCount | numbers | select(.>=0)' <<<"$i")
oom=$(bounded jq -r '.[0].State.OOMKilled | booleans' <<<"$i")
case "$oom" in true|false) : ;; *) exit 1 ;; esac
health=$(bounded jq -er '.[0].State.Health.Status | strings | select(length>0)' <<<"$i")
config_identity=$(bounded docker image inspect "$im" | bounded jq -er '.[0].Id | strings | select(length>0)')
source_identity=$(bounded docker image inspect "$im" | bounded jq -er '.[0].Config.Labels["org.opencontainers.image.revision"] | strings | select(length>0)')
cg=$(bounded awk -F: '$1=="0"{print $3}' "/proc/$pid/cgroup")
[ -n "$cg" ]
cb="/sys/fs/cgroup$cg"
cur=$(bounded cat "$cb/memory.current")
peak=$(bounded cat "$cb/memory.peak")
cgroup_swap=$(bounded cat "$cb/memory.swap.current")
pids=$(bounded cat "$cb/pids.current")
oom_event=$(bounded awk '$1=="oom"{print $2}' "$cb/memory.events")
oom_kill_event=$(bounded awk '$1=="oom_kill"{print $2}' "$cb/memory.events")
available=$(bounded awk '/MemAvailable/{print $2*1024}' /proc/meminfo)
host_swap=$(bounded awk '/SwapTotal/{t=$2}/SwapFree/{print(t-$2)*1024}' /proc/meminfo)
psi=$(bounded awk '/^full/{for(i=1;i<=NF;i++)if($i~/^avg10=/){sub("avg10=","",$i);print $i}}' /proc/pressure/memory)
process_totals=$(bounded sudo -n python3 - "$cb/cgroup.procs" <<'PY'
import os,pathlib,sys
pids=pathlib.Path(sys.argv[1]).read_text().split()
if not pids: raise SystemExit(1)
rss=anonymous=dirty=threads=fds=0
for pid in pids:
    status=pathlib.Path('/proc',pid,'status').read_text().splitlines()
    fields={line.split(':',1)[0]:line.split()[1] for line in status if ':' in line and len(line.split())>1}
    rss+=int(fields['VmRSS'])*1024;threads+=int(fields['Threads'])
    smaps=pathlib.Path('/proc',pid,'smaps_rollup').read_text().splitlines()
    values={line.split(':',1)[0]:line.split()[1] for line in smaps if ':' in line and len(line.split())>1}
    anonymous+=int(values['Anonymous'])*1024;dirty+=int(values['Private_Dirty'])*1024
    fds+=len(tuple(pathlib.Path('/proc',pid,'fd').iterdir()))
print(rss,anonymous,dirty,threads,fds,','.join(pids))
PY
)
read -r rss anonymous private_dirty threads fds pid_list <<<"$process_totals"
sockets=$(bounded sudo -n ss -Htanp | bounded awk -v ids="$pid_list" 'BEGIN{n=split(ids,a,",")} {for(i=1;i<=n;i++)if(index($0,"pid=" a[i] ",")){count++;break}} END{print count+0}')
cpu=$(bounded awk '$1=="usage_usec"{print $2}' "$cb/cpu.stat")
postgres_connections=$(bounded docker exec postgresql psql -U postgres -d litellm -Atqc 'select count(*) from pg_stat_activity')
redis_info=$(bounded docker exec litellm-redis sh -lc 'export REDISCLI_AUTH="${REDIS_PASSWORD:?}"; exec redis-cli --raw INFO clients')
redis_clients=$(bounded awk -F: '$1=="connected_clients"{gsub(/\r/,"",$2);print $2}' <<<"$redis_info")
redis_blocked=$(bounded awk -F: '$1=="blocked_clients"{gsub(/\r/,"",$2);print $2}' <<<"$redis_info")
read -r disk_bytes disk_percent < <(bounded df -PB1 "$R" | bounded awk 'NR==2{gsub(/%/,"",$5);print $4,$5}')
dependencies=$(for dependency in postgresql litellm-redis defend-memory-mcp defend-memory-memory-agent-gateway defend-memory-postgres defend-memory-qdrant defend-memory-neo4j; do bounded docker inspect "$dependency" | bounded jq -er '.[0]|[.Id,.Image,.State.StartedAt,.State.Status,(.State.Health.Status//"none"),.RestartCount,.State.OOMKilled]|@tsv'; done | bounded sha256sum | bounded cut -d' ' -f1)
[ -s "$A/safe/protected-baseline.sha256" ]
(cd "$R" && bounded sha256sum --check --status "$A/safe/protected-baseline.sha256")
protected=pass
live=$(bounded curl -sS -o /dev/null --max-time "$COMMAND_TIMEOUT" -w '%{http_code}' http://127.0.0.1:4000/health/liveliness)
ready=$(bounded curl -sS -o /dev/null --max-time "$COMMAND_TIMEOUT" -w '%{http_code}' http://127.0.0.1:4000/health/readiness)
kernel_oom=$(probe_kernel_oom)
request_state=pre
[ ! -e "$A/safe/request-active" ] || request_state=active
[ ! -e "$A/safe/request-ended" ] || request_state=post
control=$(bounded cat "$A/safe/control-state")
rollback_confidence=$(bounded cat "$A/safe/rollback-confidence")
deadline=$(bounded cat "$A/safe/maintenance-deadline-monotonic")
now=$(bounded cut -d' ' -f1 /proc/uptime)
bounded awk -v now="$now" -v deadline="$deadline" 'BEGIN{exit !(deadline>now)}'
[ "$rollback_confidence" = armed ]
phase=candidate
if [ "${WATCHDOG_PROOF_ROLLBACK:-0}" = 1 ]; then
    phase=rollback
elif [ "$im" != "$C" ] || [ "$runtime" != "$C_RUNTIME" ]; then
    printf 'identity_image\n' >&2
    exit 1
fi
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(bounded date -u +%FT%TZ)" "$now" "$phase" "$cid" "$started" "$im" "$runtime" "$config_identity" "$source_identity" "$exit_code" \
    "$cur" "$peak" "$cgroup_swap" "$oom_event" "$oom_kill_event" "$available" "$host_swap" "$psi" "$pids" "$cpu" \
    "$restart" "$oom" "$health" "$rss" "$anonymous" "$private_dirty" "$threads" "$fds" "$sockets" \
    "$postgres_connections" "$redis_clients" "$redis_blocked" "$disk_bytes" "$disk_percent" "$dependencies" "$protected" \
    "$live" "$ready" "$kernel_oom" "$request_state" "$control" "$rollback_confidence" "$deadline"
SH

cat >"$output_directory/watchdog.sh" <<'SH'
#!/bin/bash
set -uo pipefail

R=/home/staticduo/docker/litellm
A=${WATCHDOG_ATTEMPT:-$(cat "$R/releases/TASK-2026-09-03-006.active")}
C=docker.staticduo.com/litellm@sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
C_RUNTIME=sha256:b4c960ce7630a7bb7af475ce5e93c6b19a51cacd944b4cbcda6e1a9243af83b3
EXPECTED_CONFIG=sha256:ad33017b518b66d9dc81ec272b8a91ce1eda935f25b851e8ab7d2e8fa7d0d915
EXPECTED_SOURCE=bf58974a935521fa570fa7e280c51a00b2e5b54e
COLLECTOR=${WATCHDOG_COLLECTOR:-$A/rollback/collect-watchdog-sample.sh}
ROLLBACK=${WATCHDOG_ROLLBACK:-$A/rollback/rollback.sh}
L=${WATCHDOG_LOG:-$A/raw/watchdog.tsv}
SAMPLE_SECONDS=${WATCHDOG_SAMPLE_SECONDS:-1}
SAMPLE_TIMEOUT=${WATCHDOG_SAMPLE_TIMEOUT:-0.75}
PROOF_SAMPLE_LIMIT=${WATCHDOG_PROOF_SAMPLE_LIMIT:-0}
PROOF_STOP_FILE=${WATCHDOG_PROOF_STOP_FILE:-}
EXPECTED_DEPENDENCIES=${WATCHDOG_EXPECTED_DEPENDENCIES:-}
missed=0
samples=0
baseline_count=0
baseline_frozen=0
base=0
rate_count=0
cpu_count=0
previous_cpu=
previous_mono=
blocked_count=0
initial_oom=-1
initial_oom_kill=-1
identity=
previous_post=
memory_growth=0
rss_growth=0
anonymous_growth=0
dirty_growth=0
threads_growth=0
pids_growth=0
fds_growth=0
collector_pid=
declare -a baseline_ring=()

trip() {
    trap - HUP INT TERM
    if [ -n "$collector_pid" ]; then
        kill "$collector_pid" 2>/dev/null || :
        wait "$collector_pid" 2>/dev/null || :
        collector_pid=
    fi
    printf 'reason=%s\nutc=%s\nmonotonic=%s\nlast_memory=%s\n' "$1" "$(date -u +%FT%TZ)" "$(cut -d' ' -f1 /proc/uptime)" "${cur:-unknown}" >"$A/safe/trigger"
    if [ -s "$A/safe/client.pid" ]; then
        client_pid=$(cat "$A/safe/client.pid")
        kill "$client_pid" 2>/dev/null || :
        for _ in $(seq 1 50); do
            kill -0 "$client_pid" 2>/dev/null || break
            sleep 0.01
        done
        kill -0 "$client_pid" 2>/dev/null && kill -KILL "$client_pid" 2>/dev/null || :
        wait "$client_pid" 2>/dev/null || :
    fi
    "$ROLLBACK"
    rollback_status=$?
    exit "$rollback_status"
}

lost_sample() {
    missed=$((missed + 1))
    [ "$missed" -le 2 ] || trip "instrumentation_${1}"
}

finish_cycle() {
    cycle_end=$(cut -d' ' -f1 /proc/uptime)
    delay=$(awk -v target="$SAMPLE_SECONDS" -v start="$cycle_start" -v end="$cycle_end" 'BEGIN{d=target-(end-start);if(d>0)printf "%.3f",d;else print 0}')
    if awk -v d="$delay" 'BEGIN{exit !(d>0)}'; then sleep "$delay"; fi
}

trap 'trip signal_hup' HUP
trap 'trip signal_int' INT
trap 'trip signal_term' TERM

for prerequisite in protected-baseline.sha256 control-state maintenance-deadline-monotonic rollback-confidence dependencies.digest watchdog-start-wall; do
    [ -s "$A/safe/$prerequisite" ] || trip "prerequisite_${prerequisite//./_}"
done
EXPECTED_DEPENDENCIES=$(cat "$A/safe/dependencies.digest")
[ -n "$EXPECTED_DEPENDENCIES" ] || trip prerequisite_dependencies
[ "$(cat "$A/safe/rollback-confidence")" = armed ] || trip prerequisite_rollback_confidence
case "$(cat "$A/safe/control-state")" in pass) : ;; *) trip prerequisite_control ;; esac
deadline=$(cat "$A/safe/maintenance-deadline-monotonic")
now=$(cut -d' ' -f1 /proc/uptime)
awk -v now="$now" -v deadline="$deadline" 'BEGIN{exit !(deadline>now)}' || trip prerequisite_deadline
header='utc\tmono\tphase\tcontainer_id\tstarted_at\tconfigured_image\truntime_image\tconfig_identity\tsource_identity\texit_code\tmemory_current\tmemory_peak\tcgroup_swap\tcgroup_oom\tcgroup_oom_kill\tmem_available\thost_swap\tpsi_full_avg10\tpids\tcpu_usage_usec\trestarts\toom_killed\thealth\trss\tanonymous\tprivate_dirty\tthreads\tfds\tsockets\tpostgres_connections\tredis_clients\tredis_blocked\tdisk_available\tdisk_used_percent\tdependencies_digest\tprotected_state\tliveliness\treadiness\tkernel_oom\trequest_state\tcontrol\trollback_confidence\tdeadline'
printf '%b\n' "$header" >"$L"
exec 3>>"$L"

while :; do
    cycle_start=$(cut -d' ' -f1 /proc/uptime)
    rm -f "$A/safe/collector-output" "$A/safe/collector-error"
    timeout --foreground --kill-after=0.05 "$SAMPLE_TIMEOUT" "$COLLECTOR" >"$A/safe/collector-output" 2>"$A/safe/collector-error" &
    collector_pid=$!
    wait "$collector_pid"
    collector_status=$?
    collector_pid=
    if [ "$collector_status" -ne 0 ]; then
        failure=$(tr -cd 'a-zA-Z0-9_-' <"$A/safe/collector-error" | cut -c1-48)
        [ "$collector_status" -ne 124 ] || failure=sample_timeout
        lost_sample "${failure:-collector}"
        finish_cycle
        continue
    fi
    sample=$(cat "$A/safe/collector-output")
    if ! awk -F'\t' 'NF!=43{exit 1}' <<<"$sample" >/dev/null; then
        lost_sample schema
        finish_cycle
        continue
    fi
    IFS=$'\t' read -r utc mono phase cid started configured runtime config_identity source_identity exit_code cur peak cgroup_swap oom_event oom_kill_event available host_swap psi pids cpu restart oom health rss anonymous private_dirty threads fds sockets postgres_connections redis_clients redis_blocked disk_bytes disk_percent dependencies protected live ready kernel_oom request_state control rollback_confidence deadline <<<"$sample"
    numeric="$mono $exit_code $cur $peak $cgroup_swap $oom_event $oom_kill_event $available $host_swap $psi $pids $cpu $restart $rss $anonymous $private_dirty $threads $fds $sockets $postgres_connections $redis_clients $redis_blocked $disk_bytes $disk_percent $kernel_oom $deadline"
    if ! awk -v values="$numeric" 'BEGIN{n=split(values,a," ");for(i=1;i<=n;i++)if(a[i]!~/^[0-9]+([.][0-9]+)?$/)exit 1}' </dev/null; then
        lost_sample numeric
        finish_cycle
        continue
    fi
    case "$phase" in rollback|candidate) : ;; *) lost_sample phase; finish_cycle; continue ;; esac
    case "$oom" in true|false) : ;; *) lost_sample oom; finish_cycle; continue ;; esac
    case "$health" in healthy|starting|unhealthy|none) : ;; *) lost_sample health; finish_cycle; continue ;; esac
    case "$protected" in pass|fail) : ;; *) lost_sample protected; finish_cycle; continue ;; esac
    case "$request_state" in pre|active|post) : ;; *) lost_sample request_state; finish_cycle; continue ;; esac
    case "$control" in *[!a-zA-Z0-9_-]*|'') lost_sample control; finish_cycle; continue ;; esac
    case "$rollback_confidence" in armed) : ;; *) lost_sample rollback_confidence; finish_cycle; continue ;; esac
    missed=0
    printf '%s\n' "$sample" >&3
    samples=$((samples + 1))
    [ "$control" = pass ] || trip "control_$control"
    if [ "$phase" = candidate ]; then
        [ -n "$EXPECTED_DEPENDENCIES" ] || trip dependency_baseline
        [ "$dependencies" = "$EXPECTED_DEPENDENCIES" ] || trip dependency
        [ "$protected" = pass ] || trip protected
        [ "$live" = 200 ] || trip liveliness
        [ "$ready" = 200 ] || trip readiness
        [ "$kernel_oom" -eq 0 ] || trip kernel_oom
        [ "$health" = healthy ] || trip health
        [ "$restart" -eq 0 ] || trip restart
        [ "$oom" = false ] || trip oom
        [ "$exit_code" -ne 137 ] || trip exit_137
        [ "$available" -ge 34359738368 ] || trip available
        [ "$host_swap" -le 536870912 ] || trip swap
        awk -v x="$psi" 'BEGIN{exit !(x>0.10)}' && trip psi
        [ "$pids" -le 500 ] || trip pids
        [ "$fds" -le 8192 ] || trip fds
        [ "$postgres_connections" -lt 80 ] || trip postgres
        [ "$redis_clients" -lt 500 ] || trip redis_clients
        [ "$disk_bytes" -ge 21474836480 ] || trip disk_bytes
        [ "$disk_percent" -le 85 ] || trip disk_percent
        if [ -n "$previous_cpu" ]; then
            cpu_percent=$(awk -v c="$cpu" -v p="$previous_cpu" -v m="$mono" -v q="$previous_mono" 'BEGIN{d=m-q;if(d<=0)exit 1;printf "%.2f",(c-p)/(d*10000)}') || trip instrumentation_cpu_delta
            if awk -v x="$cpu_percent" 'BEGIN{exit !(x>800)}'; then cpu_count=$((cpu_count + 1)); else cpu_count=0; fi
        fi
        previous_cpu=$cpu
        previous_mono=$mono
        [ "$cpu_count" -lt 10 ] || trip cpu
        if [ "$redis_blocked" -gt 0 ]; then blocked_count=$((blocked_count + 1)); else blocked_count=0; fi
        [ "$blocked_count" -lt 10 ] || trip redis_blocked
        [ "$configured" = "$C" ] && [ "$runtime" = "$C_RUNTIME" ] || trip identity_image
        [ "$config_identity" = "$EXPECTED_CONFIG" ] || trip identity_config
        [ "$source_identity" = "$EXPECTED_SOURCE" ] || trip identity_source
        current_identity="$cid|$started"
        if [ -z "$identity" ]; then identity=$current_identity; fi
        [ "$current_identity" = "$identity" ] || trip identity_container
        if [ "$initial_oom" -lt 0 ]; then initial_oom=$oom_event; initial_oom_kill=$oom_kill_event; fi
        [ "$oom_event" -le "$initial_oom" ] || trip cgroup_oom
        [ "$oom_kill_event" -le "$initial_oom_kill" ] || trip cgroup_oom_kill
        if [ "$request_state" = pre ]; then
            [ "$cur" -lt 8589934592 ] || trip memory_absolute
            baseline_ring+=("$cur")
            if [ "${#baseline_ring[@]}" -gt 30 ]; then baseline_ring=("${baseline_ring[@]:1}"); fi
            baseline_count=${#baseline_ring[@]}
        elif [ "$baseline_frozen" -eq 0 ]; then
            [ "$baseline_count" -eq 30 ] || trip baseline
            base=0
            for value in "${baseline_ring[@]}"; do [ "$value" -le "$base" ] || base=$value; done
            baseline_frozen=1
        fi
        if [ "$baseline_frozen" -eq 1 ]; then
            limit=$((base + 2147483648))
            [ "$limit" -ge 8589934592 ] || limit=8589934592
            [ "$cur" -lt "$limit" ] || trip memory
            if [ "$request_state" = post ]; then [ "$cur" -lt $((base + 536870912)) ] || trip memory_steady; fi
        fi
        if [ -n "${previous_cur:-}" ] && [ $((cur - previous_cur)) -ge 536870912 ]; then rate_count=$((rate_count + 1)); else rate_count=0; fi
        [ "$rate_count" -lt 3 ] || trip rate
        if [ "$request_state" = post ] && [ -n "$previous_post" ]; then
            IFS=, read -r previous_memory previous_rss previous_anonymous previous_dirty previous_threads previous_pids previous_fds <<<"$previous_post"
            [ "$cur" -gt "$previous_memory" ] && memory_growth=$((memory_growth + 1)) || memory_growth=0
            [ "$rss" -gt "$previous_rss" ] && rss_growth=$((rss_growth + 1)) || rss_growth=0
            [ "$anonymous" -gt "$previous_anonymous" ] && anonymous_growth=$((anonymous_growth + 1)) || anonymous_growth=0
            [ "$private_dirty" -gt "$previous_dirty" ] && dirty_growth=$((dirty_growth + 1)) || dirty_growth=0
            [ "$threads" -gt "$previous_threads" ] && threads_growth=$((threads_growth + 1)) || threads_growth=0
            [ "$pids" -gt "$previous_pids" ] && pids_growth=$((pids_growth + 1)) || pids_growth=0
            [ "$fds" -gt "$previous_fds" ] && fds_growth=$((fds_growth + 1)) || fds_growth=0
            [ "$memory_growth" -lt 5 ] || trip post_memory_growth
            [ "$rss_growth" -lt 5 ] || trip post_rss_growth
            [ "$anonymous_growth" -lt 5 ] || trip post_anonymous_growth
            [ "$dirty_growth" -lt 5 ] || trip post_dirty_growth
            [ "$threads_growth" -lt 5 ] || trip post_threads_growth
            [ "$pids_growth" -lt 5 ] || trip post_pids_growth
            [ "$fds_growth" -lt 5 ] || trip post_fds_growth
        fi
        if [ "$request_state" = post ]; then previous_post="$cur,$rss,$anonymous,$private_dirty,$threads,$pids,$fds"; fi
        previous_cur=$cur
    fi
    if [ "$PROOF_SAMPLE_LIMIT" -gt 0 ] && [ "$samples" -ge "$PROOF_SAMPLE_LIMIT" ]; then exit 0; fi
    if [ -n "$PROOF_STOP_FILE" ] && [ -e "$PROOF_STOP_FILE" ]; then exit 0; fi
    finish_cycle
done
SH

chmod 0700 "$output_directory/rollback.sh" "$output_directory/collect-watchdog-sample.sh" "$output_directory/watchdog.sh"
for generated_script in "$output_directory"/*.sh; do
    bash -n "$generated_script"
done
printf 'generated_scripts=3\nbash_n=pass\n'
