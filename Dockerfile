FROM python:3.12-slim-bookworm

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy project definition
COPY pyproject.toml .

# Install dependencies
RUN uv sync --frozen --no-install-project

# Copy source code
COPY src/ src/
COPY README.md .

# Install the project
RUN uv sync --frozen

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Verify installation
RUN which mcp-doc-summary

# Default command
CMD ["mcp-doc-summary"]
