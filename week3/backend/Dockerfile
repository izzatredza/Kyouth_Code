FROM python:3.14.5-bookworm

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src/ ./src/

RUN uv sync --frozen

EXPOSE 8001

ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "--port", "8001", "app:app"]