# Dockerfile for Historical K(t) Reproducibility
#
# This container provides a complete, reproducible environment for
# computing the K-index of civilizational coherence (3000 BCE - 2020 CE).
#
# Usage:
#   docker build -t historical-k:v1.0.0 .
#   docker run -v $(pwd)/data:/app/data historical-k:v1.0.0 make extended-compute
#
# Contents:
#   - Python 3.11 with all dependencies
#   - Historical K(t) modules (all phases 1-3)
#   - Data processing pipelines
#   - Visualization tools

FROM python:3.11-slim

LABEL maintainer="Luminous Dynamics <contact@luminousdynamics.org>"
LABEL description="Historical K(t) - 5000 Year Civilizational Coherence Index"
LABEL version="1.0.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    ca-certificates \
    libnetcdf-dev \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python dependencies
COPY pyproject.toml poetry.lock* ./

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install Python dependencies
RUN poetry install --no-root --no-interaction --no-ansi

# Install additional dependencies for production
RUN pip install --no-cache-dir \
    netCDF4==1.6.4 \
    pymc==5.10.0 \
    arviz==0.17.0 \
    networkx==3.2.1

# Copy application code
COPY historical_k/ ./historical_k/
COPY data/ ./data/
COPY Makefile ./
COPY README.md ./

# Create output directories
RUN mkdir -p logs/historical_k \
             logs/historical_k_extended \
             logs/sensitivity \
             logs/validation_external \
             logs/robustness \
             data/sources/seshat \
             data/sources/hyde \
             data/sources/external

# Set Python path
ENV PYTHONPATH=/app

# Default command: show help
CMD ["make", "help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import historical_k; print('OK')" || exit 1

# Expose no ports (batch processing container)

# Metadata
ENV APP_VERSION=1.0.0
ENV COMPUTE_CORES=4
ENV PYTHON_VERSION=3.11
