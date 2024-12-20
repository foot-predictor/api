FROM python:latest

ENV PYTHONUNBUFFERED=1

ARG ENV

COPY --from=ghcr.io/astral-sh/uv:0.4.15 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

WORKDIR /app/

# Install dependencies
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY . .

# Sync the project
# Ref: https://docs.astral.sh/uv/guides/integration/docker/#intermediate-layers
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

#CMD ["fastapi", "run", "--workers", "4", "--host", "0.0.0.0", "--port", "10000"]
CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "10000"]
