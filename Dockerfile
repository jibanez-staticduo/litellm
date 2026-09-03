# syntax=docker/dockerfile:1.7

# Base image for building
ARG LITELLM_BUILD_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d

# Runtime image
ARG LITELLM_RUNTIME_IMAGE=cgr.dev/chainguard/wolfi-base@sha256:57108e597a8cf3bd376b810f1c3539c21942daefa242cb9dddaae30f8aac735d
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.11.26@sha256:3d868e555f8f1dbc324afa005066cd11e1053fc4743b9808ca8025283e65efa5
ARG RUST_TOOLCHAIN_IMAGE=docker.io/library/rust:1.97.1-slim-bookworm@sha256:2775a09d208ff0d7c1f50490c45b62db929e87ba1dcbc3f2132ac71a704bcdd3
# Pinned by digest like the other base images; bump explicitly on Node upgrades.
ARG UI_BUILD_IMAGE=node:24.19-alpine3.24@sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43

FROM $UV_IMAGE AS uvbin

FROM $RUST_TOOLCHAIN_IMAGE AS rust-toolchain

# Admin UI builder. Pinned to the build platform so the architecture-independent
# Next.js static export compiles once natively even in a multi-arch build,
# instead of once per target arch under QEMU.
FROM --platform=$BUILDPLATFORM $UI_BUILD_IMAGE AS ui-builder

ENV NEXT_TELEMETRY_DISABLED=1 \
    npm_config_fund=false \
    npm_config_audit=false

WORKDIR /ui

COPY ui/litellm-dashboard/package.json ui/litellm-dashboard/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --prefer-offline

COPY ui/litellm-dashboard/ ./
RUN npm run build

# Builder stage
FROM $LITELLM_BUILD_IMAGE AS builder

ARG TARGETARCH

WORKDIR /app
USER root

COPY --from=uvbin /uv /usr/local/bin/uv
COPY --from=uvbin /uvx /usr/local/bin/uvx
COPY --from=rust-toolchain /usr/local/cargo /usr/local/cargo
COPY --from=rust-toolchain /usr/local/rustup /usr/local/rustup

RUN apk add --no-cache \
    bash \
    gcc \
    python-3.13=3.13.15-r4 \
    python-3.13-dev=3.13.15-r4 \
    openssl \
    openssl-dev \
    nodejs \
    npm \
    libsndfile

ENV UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_LINK_MODE=copy \
    CARGO_HOME=/usr/local/cargo \
    RUSTUP_HOME=/usr/local/rustup \
    PATH="/usr/local/cargo/bin:/app/.venv/bin:${PATH}"

RUN case "$TARGETARCH" in \
        amd64) expected_arch=x86_64 ;; \
        arm64) expected_arch=aarch64 ;; \
        *) exit 1 ;; \
    esac && \
    rustc_version="$(rustc -vV)" && \
    test "$(printf '%s\n' "$rustc_version" | grep -c '^release: ')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -Fxc 'release: 1.97.1')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -c '^commit-hash: ')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -Fxc 'commit-hash: 8bab26f4f68e0e26f0bb7960be334d5b520ea452')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -c '^host: ')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -Fxc "host: ${expected_arch}-unknown-linux-gnu")" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -c '^LLVM version: ')" -eq 1 && \
    test "$(printf '%s\n' "$rustc_version" | grep -Fxc 'LLVM version: 22.1.6')" -eq 1 && \
    cargo --version | grep -Eq '^cargo 1\.97\.1 ' && \
    test ! -e /usr/lib/libLLVM.so.22.1 && \
    test ! -L /usr/lib/libLLVM.so.22.1

# Copy dependency metadata first for layer caching
COPY pyproject.toml uv.lock ./
COPY enterprise/pyproject.toml enterprise/
COPY litellm-proxy-extras/pyproject.toml litellm-proxy-extras/

RUN case "$TARGETARCH" in \
        amd64) \
            expected_ml_dtypes_wheel=ml_dtypes-0.5.4-cp313-cp313-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl; \
            expected_ml_dtypes_hash=533ce891ba774eabf607172254f2e7260ba5f57bdd64030c9a4fcfbd99815d0d \
            ;; \
        arm64) \
            expected_ml_dtypes_wheel=ml_dtypes-0.5.4-cp313-cp313-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl; \
            expected_ml_dtypes_hash=ce756d3a10d0c4067172804c9cc276ba9cc0ff47af9078ad439b075d1abdc29b \
            ;; \
        *) exit 1 ;; \
    esac && \
    grep -Fq "$expected_ml_dtypes_wheel" uv.lock && \
    grep -Fq "hash = \"sha256:${expected_ml_dtypes_hash}\"" uv.lock

RUN uv --version | grep -Eq '^uv 0\.11\.26 ' && \
    uvx --version | grep -Eq '^uvx 0\.11\.26 '

# Install third-party dependencies (cached unless pyproject.toml/uv.lock change)
RUN uv sync --frozen --no-install-project --no-install-workspace --no-default-groups --no-editable \
    --extra proxy \
    --extra proxy-runtime \
    --extra extra_proxy \
    --extra semantic-router \
    --extra saml \
    --python /usr/bin/python3.13

# Copy full source tree
COPY . .

# Replace the committed UI bundle with the one built from this exact source.
# Clearing first drops the committed bundle's content-hashed chunks that COPY
# would otherwise leave behind alongside the fresh ones.
RUN rm -rf litellm/proxy/_experimental/out
COPY --from=ui-builder /ui/out/. litellm/proxy/_experimental/out/

# Build Admin UI before final sync (applies the enterprise color override when present)
RUN sed -i 's/\r$//' docker/build_admin_ui.sh && chmod +x docker/build_admin_ui.sh && ./docker/build_admin_ui.sh

# Install project and workspace packages (fast - deps already cached)
RUN uv sync --frozen --no-default-groups --no-editable \
    --extra proxy \
    --extra proxy-runtime \
    --extra extra_proxy \
    --extra semantic-router \
    --extra saml \
    --python /usr/bin/python3.13

RUN HOME=/opt/prisma XDG_CACHE_HOME=/opt/prisma/.cache PRISMA_BINARY_CACHE_DIR=/opt/prisma/binaries \
    npm_config_cache=/root/.npm \
    prisma generate --schema=./schema.prisma

RUN uv cache clean && test ! -d /root/.cache/uv/archive-v0 && test ! -d /root/.cache/uv/sdists-v9

RUN sed -i 's/\r$//' docker/entrypoint.sh && chmod +x docker/entrypoint.sh && \
    sed -i 's/\r$//' docker/prod_entrypoint.sh && chmod +x docker/prod_entrypoint.sh

# Runtime stage
FROM $LITELLM_RUNTIME_IMAGE AS runtime

USER root

# node (without npm) is required by the prisma CLI at runtime
RUN apk add --no-cache bash openssl tzdata nodejs python-3.13=3.13.15-r4 libsndfile

WORKDIR /app
ENV PATH="/app/.venv/bin:${PATH}" \
    PRISMA_BINARY_CACHE_DIR=/opt/prisma/binaries \
    PRISMA_CLI_PATH=/opt/prisma/binaries/node_modules/.bin/prisma \
    PRISMA_CLI_QUERY_ENGINE_TYPE=binary \
    PRISMA_OFFLINE_MODE=true

# Copy only what runtime needs. The application is installed inside the venv;
# the rest of the builder's /app is source and build metadata that must not
# ship (manifest-scanning tools attribute everything in it to this image).
# entrypoint.sh invokes litellm/proxy/prisma_migration.py by source path.
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/docker /app/docker
COPY --from=builder /app/schema.prisma /app/schema.prisma
COPY --from=builder /app/litellm/proxy/prisma_migration.py /app/litellm/proxy/prisma_migration.py
# enterprise/ is imported by source path at runtime (proxy_cli puts the
# working directory on sys.path; litellm/proxy/hooks resolves
# enterprise.enterprise_hooks from it)
COPY --from=builder /app/enterprise /app/enterprise
COPY --from=builder /app/litellm-proxy-extras /app/litellm-proxy-extras
# Prisma CLI + engines are baked under /opt/prisma, a fixed path every
# runtime uid can read and that no cache volume mount shadows. The paths are
# pinned via PRISMA_BINARY_CACHE_DIR / PRISMA_CLI_PATH and recorded into the
# generated client at build time, so `prisma migrate deploy` on a fresh
# database needs no npm and no network access (#33650, #24554).
COPY --from=builder /opt/prisma /opt/prisma

RUN find /app/.venv -type f -path "*/tornado/test/*" -delete && \
    find /app/.venv -type d -path "*/tornado/test" -delete && \
    chmod -R a+rX /opt/prisma && \
    test -x /opt/prisma/binaries/node_modules/.bin/prisma && \
    test -f /opt/prisma/binaries/node_modules/prisma/build/index.js && \
    /app/.venv/bin/python -c "from prisma.client import BINARY_PATHS; paths = list(BINARY_PATHS.query_engine.values()); assert paths and all(p.startswith('/opt/prisma/') for p in paths), paths"

EXPOSE 4000/tcp

ENTRYPOINT ["docker/prod_entrypoint.sh"]
CMD ["--port", "4000"]
