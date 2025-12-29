# Dockerfile for BetterCodeBetterScience
# Builds an image with all dependencies for running the code examples

FROM python:3.12-slim-bookworm

LABEL maintainer="Russell Poldrack"
LABEL description="Container for BetterCodeBetterScience book code examples"

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    gfortran \
    # Git for datalad and version control
    git \
    git-annex \
    # HDF5 for h5py
    libhdf5-dev \
    # For scientific packages
    libopenblas-dev \
    liblapack-dev \
    # For igraph/leidenalg
    libigraph-dev \
    # For image processing
    libjpeg-dev \
    libpng-dev \
    # For SSL/networking
    libssl-dev \
    libcurl4-openssl-dev \
    # For XML parsing
    libxml2-dev \
    libxslt1-dev \
    # R and dependencies for rpy2
    r-base \
    r-base-dev \
    # Misc utilities
    curl \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set up working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Create virtual environment and install dependencies
RUN uv venv /app/.venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install the project and all dependencies
RUN uv pip install -e .

# Copy remaining project files
COPY book/ ./book/
COPY tests/ ./tests/
COPY data/ ./data/
COPY scripts/ ./scripts/
COPY myst.yml ./

# Set default command
CMD ["python", "--version"]
