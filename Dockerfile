# --- Base Build Stage ---
    FROM python:3.12-bookworm AS base

    # Set environment variables
    ENV PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=true \
        PIP_DEFAULT_TIMEOUT=100 \
        PIP_DISABLE_PIP_VERSION_CHECK=on \
        QR_CODE_DIR=/myapp/qr_codes
    
    WORKDIR /myapp
    
    # Update Debian system, apply security patches, and install build dependencies
    RUN apt-get update \
        && apt-get upgrade -y \
        && apt-get install -y --no-install-recommends \
            gcc \
            libpq-dev \
            libc-bin \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    # Install Python dependencies inside a virtual environment
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
    
    WORKDIR /myapp
    
    # Create a non-root user
    RUN useradd -m myuser
    USER myuser
    
    # Copy the virtual environment and application code
    COPY --from=base /.venv /.venv
    COPY --chown=myuser:myuser . .
    
    # Expose the app port
    EXPOSE 8000
    
    # Command to run the app
    ENTRYPOINT ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
    