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

# Google Chrome, and specifically not Debian's `chromium`. Measured: in a container
# that build cleared none of six challenged hosts — not headless, not headless with the
# User-Agent corrected, not headed under Xvfb — because it omits the `Google Chrome`
# brand from `Sec-CH-UA`, which every request carries. That is a property of the binary,
# so no display setting hides it and a virtual display is answering the wrong question.
# amd64 only, which is what Google publishes; on arm64 the image simply has no browser
# and a challenged origin fails with an honest diagnosis, as it did before.
RUN apt-get update -yq && \
    apt-get install -yq --no-install-recommends ca-certificates wget gnupg && \
    if [ "$(dpkg --print-architecture)" = "amd64" ]; then \
    wget -qO /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -yq --no-install-recommends /tmp/chrome.deb && \
    rm -f /tmp/chrome.deb; \
    fi && \
    apt-get purge -yq wget gnupg && apt-get autoremove -yq && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY pyproject.toml uv.lock ./
COPY lncrawl ./lncrawl
COPY sources ./sources

ENTRYPOINT ["/app/.venv/bin/python", "-m", "lncrawl"]
