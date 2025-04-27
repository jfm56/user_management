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
    
    # Install build dependencies (minimal)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install Python deps into /.venv
    COPY requirements.txt .
    
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
    
    # Create non-root user and group
    RUN addgroup --system myuser && adduser --system --ingroup myuser myuser
    
    # Copy only the venv and app code
    COPY --from=base /.venv /.venv
    COPY --chown=myuser:myuser . .
    
    # Switch to non-root user
    USER myuser
    
    # Expose port
    EXPOSE 8000
    
    # Use ENTRYPOINT and CMD separately (better practice)
    ENTRYPOINT ["uvicorn"]
    CMD ["app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    