# Builder stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy the workspace pyproject.toml and the pipeline module
COPY ../pyproject.toml ./
COPY . ./pipeline/

# Install UV and dependencies (excluding our pipeline package)
RUN cd pipeline && \
    uv pip install --system .

# Final stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PREFECT_SERVER_API_PORT=4200

# Create non-root user
RUN useradd --create-home app
USER app

WORKDIR /app/pipeline

# Copy only the installed packages
COPY --from=builder --chown=app:app /usr/local/lib/python3.12/site-packages/ /usr/local/lib/python3.12/site-packages/

# Copy the pipeline source code to maintain the same structure
COPY --from=builder --chown=app:app /app/pipeline /app/pipeline

# Set PYTHONPATH directly
ENV PYTHONPATH=/app/pipeline

# Expose the Prefect server port
EXPOSE 4200

# Run the Prefect deployment serve script
CMD ["python", "-m", "pipeline.d_runners.scrape_siegessaeule"]
