# --- Base Build Stage ---
    FROM python:3.12-slim-bookworm AS base

    # Set environment variables early
    ENV PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=true \
        PIP_DEFAULT_TIMEOUT=100 \
        PIP_DISABLE_PIP_VERSION_CHECK=on
    
    # Set working directory
    WORKDIR /myapp
    
    # Install build dependencies (minimal and cleanly)
    RUN apt-get update \
        && apt-get install -y --no-install-recommends gcc libpq-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    # Manually upgrade perl-base to fix CVE-2024-56406 until base image is updated.
    RUN apt-get update && apt-get install --only-upgrade -y perl-base \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy only the requirements first for better layer caching
    COPY requirements.txt .
    
    # Create virtual environment manually
    RUN python -m venv /.venv \
        && /.venv/bin/pip install --upgrade pip \
        && /.venv/bin/pip install -r requirements.txt
    
    # --- Final Runtime Stage ---
    FROM python:3.12-slim-bookworm AS final
    
    # Set environment variables
    ENV PATH="/.venv/bin:$PATH" \
        PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        QR_CODE_DIR=/myapp/qr_codes
    
    # Set working directory
    WORKDIR /myapp
    
    # Create non-root user
    RUN addgroup --system myuser && adduser --system --ingroup myuser myuser
    
    # Copy installed venv and app source code
    COPY --from=base /.venv /.venv
    COPY --chown=myuser:myuser . .
    
    # Switch to non-root user
    USER myuser
    