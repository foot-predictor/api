FROM python:latest

ARG ENV
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"
ENV UV_LINK_MODE=copy

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --frozen --no-cache

# Run the application.
CMD ["uvicorn", "main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "10000"]
