# Lovable loopback relay runbook

This procedure starts the Lovable callback relay on Fedora and makes it reachable only from a macOS browser through an SSH local forward. It does not start OAuth.

## Fixed deployment values

- Callback and health port: `43119`
- Relay service: `loopback-oauth-relay`
- Fedora address observed on 2026-08-21: `10.71.14.220` (DHCP, revalidate before every use)
- Fedora SSH destination: `staticduo@10.71.14.220`
- Fedora Compose project directory: `/home/staticduo/docker/litellm`

Changing the port requires one coordinated reviewed change to the Fedora host publication, relay callback, LiteLLM redirect constant, and macOS `ssh -L` argument. Do not change only one command.

## Fedora: start and verify

From the deployed LiteLLM Compose project directory:

```bash
docker compose up -d loopback-oauth-relay
docker compose ps loopback-oauth-relay
docker compose exec -T loopback-oauth-relay python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2).read().decode().strip())"
ss -ltn '( sport = :43119 )'
curl --fail --silent --show-error http://127.0.0.1:43119/healthz
```

The container and host health commands must print `ok`. The `ss` output must show only `127.0.0.1:43119`, never `0.0.0.0:43119`, `[::]:43119`, or a LAN address. Stop and correct the Compose publication if that check fails.

## macOS: revalidate Fedora DHCP address

Confirm the current Fedora address from a trusted local source before using the retained address. For example, on Fedora run `ip route get 1.1.1.1` and confirm the preferred source is `10.71.14.220`. Confirm SSH reaches the intended host and verify its host key through the normal trusted process. Replace `10.71.14.220` below if DHCP changed.

## macOS: start, check, and health-test the tunnel

```bash
mkdir -p "$HOME/.ssh/controlmasters"
if lsof -nP -iTCP:43119 -sTCP:LISTEN; then
  echo "Port 43119 is already in use; stop and identify the listener before continuing" >&2
  exit 1
fi
if ! ssh -S "$HOME/.ssh/controlmasters/lovable-relay.sock" -O check staticduo@10.71.14.220; then
  if lsof -nP -iTCP:43119 -sTCP:LISTEN; then
    echo "Control check failed but port 43119 is live; do not remove the socket" >&2
    exit 1
  fi
  rm -f "$HOME/.ssh/controlmasters/lovable-relay.sock"
fi
ssh -fNT -M -S "$HOME/.ssh/controlmasters/lovable-relay.sock" \
  -o ExitOnForwardFailure=yes \
  -o ServerAliveInterval=30 \
  -o ServerAliveCountMax=3 \
  -L 127.0.0.1:43119:127.0.0.1:43119 \
  staticduo@10.71.14.220
ssh -S "$HOME/.ssh/controlmasters/lovable-relay.sock" -O check staticduo@10.71.14.220
curl --fail --silent --show-error http://127.0.0.1:43119/healthz
```

The initial `lsof` command must print nothing. The final command must print only `ok`. Only then use the explicit Lovable Connect action in the authenticated LiteLLM UI.

## macOS: stop and verify

```bash
ssh -S "$HOME/.ssh/controlmasters/lovable-relay.sock" -O exit staticduo@10.71.14.220
lsof -nP -iTCP:43119 -sTCP:LISTEN
```

The final command must print nothing.

## Fedora: stop and verify

From the deployed LiteLLM Compose project directory:

```bash
docker compose stop loopback-oauth-relay
docker compose ps loopback-oauth-relay
ss -ltn '( sport = :43119 )'
```

The service must be stopped and `ss` must show no listener. This scoped command does not stop LiteLLM.

## Failure recovery

- `lsof` reports a listener before tunnel start: stop the stale control connection with the macOS stop command. If another process owns the port, do not start OAuth or choose an ad hoc port.
- The control check fails: the guarded block repeats the listener check. It removes the named socket only when both the control check fails and port `43119` has no listener. If either listener check reports a process, stop and identify it; never remove the socket automatically.
- SSH reports forwarding failure: verify the Fedora address, SSH host identity, Fedora relay status, and Fedora loopback listener, then start a new tunnel.
- Health fails on Fedora: inspect only sanitized service status and logs. Do not paste callback URLs, query strings, authorization headers, state, codes, verifiers, tokens, or relay-secret values into evidence.
- Health passes on Fedora but fails on macOS: close the control socket, revalidate the Fedora DHCP address, and recreate the tunnel.
- The browser window is closed, denied, or times out: cancel in the UI and start a new connection. Transactions are single-use and expire after 300 seconds.
