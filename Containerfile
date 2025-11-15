# Multi-stage build for smaller image
FROM python:3.11-slim-bookworm AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-slim-bookworm

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 -s /bin/bash chatuser

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application files
COPY --chown=chatuser:chatuser server.py database.py auth.py ./
COPY --chown=chatuser:chatuser templates ./templates
COPY --chown=chatuser:chatuser static ./static

# Create directories with correct permissions
# Use tmpfs for these in production to reduce SD writes
RUN mkdir -p \
    /app/uploads/thumbnails \
    /app/uploads/files \
    /app/uploads/avatars \
    /app/data \
    /app/tmp \
    && chown -R chatuser:chatuser /app

# Switch to non-root user
USER chatuser

# Environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=server.py \
    DATABASE_PATH=/app/data/chat.db \
    UPLOAD_FOLDER=/app/uploads \
    TMP_FOLDER=/app/tmp

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/api/health', timeout=5)" || exit 1

# Expose port
EXPOSE 5000

# Use tini as init system (proper signal handling)
ENTRYPOINT ["/usr/bin/tini", "--"]

# Run with gunicorn for better performance (2 workers max for Pi Zero)
CMD ["python", "-m", "gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "2", \
     "--worker-class", "gthread", \
     "--threads", "2", \
     "--worker-tmp-dir", "/dev/shm", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "server:app"]
