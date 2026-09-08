FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

RUN apt-get update -yq && \
    apt-get install -yq --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --extra lsp

#------------------------------------------------
# Runtime
#------------------------------------------------
FROM python:3.14-slim-trixie

ENV LNCRAWL_DATA_PATH=/data \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Firefox, from Mozilla
RUN apt-get update -yq && \
    apt-get install -yq --no-install-recommends ca-certificates wget xz-utils tini \
    libgtk-3-0 libdbus-glib-1-2 libasound2t64 libx11-xcb1 libxtst6 libxt6 libpci3 \
    fonts-liberation fonts-dejavu && \
    case "$(dpkg --print-architecture)" in \
    amd64) MOZ_OS=linux64 ;; \
    arm64) MOZ_OS=linux64-aarch64 ;; \
    *) MOZ_OS= ;; \
    esac && \
    if [ -n "$MOZ_OS" ]; then \
    wget -qO /tmp/firefox.tar.xz "https://download.mozilla.org/?product=firefox-latest-ssl&os=$MOZ_OS&lang=en-US" && \
    tar -xJf /tmp/firefox.tar.xz -C /opt && rm -f /tmp/firefox.tar.xz && \
    ln -s /opt/firefox/firefox /usr/local/bin/firefox; \
    fi && \
    apt-get purge -yq wget xz-utils && apt-get autoremove -yq && \
    rm -rf /var/lib/apt/lists/*

# Required for spoofing
ENV TZ=UTC

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY pyproject.toml uv.lock ./
COPY lncrawl ./lncrawl
COPY sources ./sources

ENTRYPOINT ["/usr/bin/tini", "--", "/app/.venv/bin/python", "-m", "lncrawl"]
