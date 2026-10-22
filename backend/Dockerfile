# ---- Backend image (used for Dev, Stage and Live) ----
FROM python:3.13-slim

# uv = fast Python package manager. Copy only its binary from the official image.
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /usr/local/bin/uv

WORKDIR /app

# 1) Install dependencies first (cached layer: only re-runs when the lock file changes)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Then copy the source code
COPY app ./app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Live/Stage default. docker-compose.yml overrides this with --reload for Dev.
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
