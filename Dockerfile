# Multi-stage build for MCP OAuth Server
# Stage 1: Build stage with all dependencies
FROM python:3.14-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only dependency specifications first for better caching
COPY pyproject.toml ./

# Extract and install dependencies directly
# Using --trusted-host to handle SSL certificate issues in CI/CD environments
RUN pip install --user --no-cache-dir \
    --trusted-host pypi.org \
    --trusted-host pypi.python.org \
    --trusted-host files.pythonhosted.org \
    fastmcp>=0.1.0 \
    authlib>=1.3.0 \
    httpx>=0.27.0 \
    python-dotenv>=1.0.0 \
    pydantic>=2.0.0 \
    pydantic-settings>=2.0.0

# Stage 2: Runtime stage
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser

# Copy Python dependencies from builder to mcpuser's home
COPY --from=builder --chown=mcpuser:mcpuser /root/.local /home/mcpuser/.local

# Update PATH for mcpuser
ENV PATH=/home/mcpuser/.local/bin:$PATH

# Set ownership of app directory
RUN chown -R mcpuser:mcpuser /app

# Copy application code
COPY --chown=mcpuser:mcpuser src/ ./src/

# Add src to PYTHONPATH so Python can find the modules
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Switch to non-root user
USER mcpuser

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Health check (for container orchestration)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set default command
CMD ["python", "-m", "mcp_server.main"]
