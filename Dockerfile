# --- Base Build Stage ---
    FROM python:3.12-slim-bookworm AS base

    ENV PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        PIP_NO_CACHE_DIR=true \
        PIP_DEFAULT_TIMEOUT=100 \
        PIP_DISABLE_PIP_VERSION_CHECK=on \
        PYTHONPATH=/myapp
    
    WORKDIR /myapp
    
    RUN apt-get update \
        && apt-get install -y --no-install-recommends gcc libpq-dev \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    RUN apt-get update \
        && apt-get install --only-upgrade -y perl-base \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*
    
    COPY requirements.txt .
    
    RUN python -m venv /.venv \
        && /.venv/bin/pip install --upgrade pip \
        && /.venv/bin/pip install -r requirements.txt
    
    # --- Final Runtime Stage ---
    FROM python:3.12-slim-bookworm AS final
    
    ENV PATH="/.venv/bin:$PATH" \
        PYTHONUNBUFFERED=1 \
        PYTHONFAULTHANDLER=1 \
        QR_CODE_DIR=/myapp/qr_codes \
        PYTHONPATH=/myapp
    
    WORKDIR /myapp
    
    RUN addgroup --system myuser && adduser --system --ingroup myuser myuser
    
    COPY --from=base /.venv /.venv
    COPY --chown=myuser:myuser . .
    
    USER myuser
    
    CMD ["/.venv/bin/uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
    