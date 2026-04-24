FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

ARG UV_NO_DEV=0

#  system
ENV PATH="/root/.local/bin/:$PATH"
#  uv
ENV UV_NO_DEV=$UV_NO_DEV
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_PYTHON_CACHE_DIR=/root/.cache/uv/python
#  python
ENV PYTHONPATH=/app
#  misc
ENV HOME=/app

RUN groupadd --system --gid 1000 nonroot \
  && useradd --system --gid 1000 --uid 1000 --create-home nonroot \
  && apt-get update && apt-get install -y --no-install-recommends libyajl2\
  && rm -rf /var/lib/apt/lists/*

USER nonroot

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
     uv sync --package etl --no-install-workspace

COPY --chown=nonroot:nonroot . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --package etl --locked

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []

CMD ["uv", "run", "python3", "workers/ledger.py"]


