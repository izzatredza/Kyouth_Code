FROM python:3.14.5-bookworm

# Install uv globally
RUN pip install uv

# Set working directory inside the container
WORKDIR /app

# Copy dependency specifications and source files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies using uv
RUN uv sync --frozen

# Configure the runtime environment execution instructions matching image_81d71c.png
ENTRYPOINT ["uv", "run", "uvicorn"]
CMD ["--app-dir", "src", "--host", "0.0.0.0", "app:app"]