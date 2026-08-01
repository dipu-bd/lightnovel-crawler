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

# Firefox, from Mozilla, on both architectures — measured 6 of 6 challenged hosts in
# this image. Two things were tried first and neither works, both worth stating so they
# are not retried:
#
# Debian's `chromium` clears almost nothing here, with or without a correct clock,
# because it omits the `Google Chrome` brand from `Sec-CH-UA` and every request carries
# it. That is a property of the binary, so no display or locale setting hides it and a
# virtual display answers the wrong question. Google Chrome has the brand but no arm64
# Linux build exists, so it cannot be the answer on every architecture. Mozilla ships
# both, and Firefox sends no `Sec-CH-UA` at all.
#
# Debian's `firefox-esr` is several major versions behind and cleared 1 of 6 where the
# current build cleared 6, so the tarball is not gratuitous.
RUN apt-get update -yq && \
    apt-get install -yq --no-install-recommends ca-certificates wget xz-utils \
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

# The clock is load-bearing, and this default is a guess that suits nobody exactly.
# A container is UTC unless told otherwise, and a browser whose timezone disagrees with
# where its address geolocates is read as automation: the same binary on the same six
# hosts cleared 1 of 6 under UTC and 6 of 6 with TZ matching the exit. Set this to the
# zone the traffic appears to come from — the host's own zone, unless a proxy moves it.
ENV TZ=UTC

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

COPY pyproject.toml uv.lock ./
COPY lncrawl ./lncrawl
COPY sources ./sources

ENTRYPOINT ["/app/.venv/bin/python", "-m", "lncrawl"]
