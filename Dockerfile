#------------------------------------------------
# Builder: install Python dependencies
#------------------------------------------------
ARG BASE_IMAGE=ghcr.io/lncrawl/lncrawl-base:latest

FROM ${BASE_IMAGE} AS builder

RUN apt-get update -yq && \
    apt-get install -yq --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --all-extras --all-groups

#------------------------------------------------
# Runtime
#------------------------------------------------
FROM ${BASE_IMAGE}

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY pyproject.toml uv.lock ./
COPY lncrawl ./lncrawl
COPY sources ./sources

ENV LNCRAWL_DATA_PATH=/data

ENTRYPOINT ["/app/.venv/bin/python", "-m", "lncrawl"]
