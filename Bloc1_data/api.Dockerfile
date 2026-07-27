FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "src.C5_api.api:app", "--host", "0.0.0.0", "--port", "8001"]
