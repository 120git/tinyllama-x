# Multi-stage Dockerfile for TinyLlama-X CLI (secure, non-root, headless)
# Stage 1: Builder - compile wheels and install dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ && \
    rm -rf /var/lib/apt/lists/*

# Copy project files needed for build
COPY pyproject.toml ./
COPY tinyllamax/ ./tinyllamax/

# Build wheel and install to /install prefix
RUN pip install --no-cache-dir --upgrade pip setuptools wheel build && \
    python -m build --wheel --outdir dist && \
    pip install --no-cache-dir --prefix=/install dist/*.whl

# Stage 2: Runtime - minimal, secure, non-root
FROM python:3.12-slim

# OCI image labels (org.opencontainers.image.*)
LABEL org.opencontainers.image.title="tinyllamax"
LABEL org.opencontainers.image.description="TinyLlama-X intelligent CLI for package management (headless)"
LABEL org.opencontainers.image.url="https://github.com/120git/tinyllama-x"
LABEL org.opencontainers.image.source="https://github.com/120git/tinyllama-x"
LABEL org.opencontainers.image.vendor="120git"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.authors="TinyLlama-X <dev@example.com>"

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Harden: make /usr/local read-only
RUN chmod -R a-w /usr/local && \
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user (app:app, UID 10001)
RUN adduser --disabled-password --gecos "" --uid 10001 app

# Switch to non-root user
USER app
WORKDIR /home/app

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PATH="/usr/local/bin:${PATH}"

# Entrypoint: tinyllamax CLI
ENTRYPOINT ["tinyllamax"]

# Default command: show help
CMD ["--help"]

# Health check (optional): verify CLI is accessible
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ["tinyllamax", "--help"] || exit 1
