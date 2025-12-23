FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app


COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen 
EXPOSE 5000

COPY . .

CMD ["uv", "run", "app.py"]
