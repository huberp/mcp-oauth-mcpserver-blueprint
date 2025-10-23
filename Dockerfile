# Multi-stage build for MCP OAuth Server
# Stage 1: Build stage with all dependencies
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./

# Install Python dependencies to user directory
RUN pip install --user --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --user --no-cache-dir .

# Stage 2: Runtime stage
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Update PATH
ENV PATH=/root/.local/bin:$PATH

# Create non-root user for security
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

# Copy application code
COPY --chown=mcpuser:mcpuser src/ ./src/

# Switch to non-root user
USER mcpuser

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Health check (for container orchestration)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Set default command
CMD ["python", "-m", "mcp_server.main"]
