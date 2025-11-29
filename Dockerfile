# Multi-stage build for Django app with ChromaDB
FROM python:3.11-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    libsqlite3-0 \
    libsqlite3-dev \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Set cache environment variables for builder stage
ENV HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers

# Create cache directories in builder
RUN mkdir -p /app/.cache/huggingface /app/.cache/sentence-transformers

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download ML models in builder stage (before copying to production)
COPY download_models.py .
RUN python download_models.py || echo "⚠️ Model download failed in builder stage"

# Production stage
FROM python:3.11-slim-bookworm

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libsqlite3-0 \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create app user (security best practice)
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appuser . .

# IMPORTANT: Copy ML model cache from builder stage to avoid re-downloading at runtime
# This prevents OOM errors caused by downloading 420MB model when worker starts
COPY --from=builder /app/.cache /app/.cache

# Create directories for Django
RUN mkdir -p /app/staticfiles /app/media /app/chromadb_data && \
    chown -R appuser:appuser /app

# Copy and set permissions for entrypoint script (as root before USER switch)
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh && chown appuser:appuser /app/docker-entrypoint.sh

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentence-transformers

# Set correct permissions for cache directory (copied from builder)
RUN chown -R appuser:appuser /app/.cache

# Switch to non-root user
USER appuser

# Note: collectstatic will run in docker-entrypoint.sh with DATABASE_URL available

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/', timeout=5)" || exit 1

# Use entrypoint script to handle PORT variable properly
ENTRYPOINT ["/app/docker-entrypoint.sh"]
