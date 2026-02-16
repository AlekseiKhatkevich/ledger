# https://docs.astral.sh/uv/guides/integration/docker/
# https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile

FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

ARG UV_NO_DEV='0'
ARG GRANIAN_RELOAD='0'

#  system
ENV PATH="/root/.local/bin/:$PATH"
#  uv
ENV UV_NO_DEV=$UV_NO_DEV
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_TOOL_BIN_DIR=/usr/local/bin
ENV UV_PYTHON_DOWNLOADS=never
#  python
ENV PYTHONPATH=/app
# granian
ENV GRANIAN_RELOAD=$GRANIAN_RELOAD
ENV GRANIAN_INTERFACE='asgi'
ENV GRANIAN_LOOP='uvloop'
ENV GRANIAN_HOST='0.0.0.0'

RUN groupadd --system --gid 999 nonroot \
 && useradd --system --gid 999 --uid 999 --create-home nonroot

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked \
    && chown -R 999:999 /app  #  для Tilt, чтобы работал live update для не-рут юзера

ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT []

USER nonroot

# add uv run befor in case of env troubles, might help...
CMD ["granian", "main:app"]

