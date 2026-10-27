# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: builder — install dependencies into a virtualenv (NFR-06, NFR-10).
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Build tools needed to compile psycopg2 / Pillow wheels.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated virtualenv we can copy into the runtime stage.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements/ requirements/
RUN pip install --upgrade pip && pip install -r requirements/prod.txt

# ---------------------------------------------------------------------------
# Stage 2: runtime — slim, non-root image (NFR-06).
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=config.settings.prod

WORKDIR /app

# Runtime libraries only (no compilers) + curl for the HEALTHCHECK.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system app && adduser --system --ingroup app app

# Bring the prebuilt virtualenv over from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Application source.
COPY . .

# Collect static assets at build time; a dummy key keeps settings importable.
RUN SECRET_KEY=build-only DJANGO_SETTINGS_MODULE=config.settings.prod \
    ALLOWED_HOSTS=localhost \
    python manage.py collectstatic --noinput

RUN chmod +x entrypoint.sh && chown -R app:app /app
USER app

EXPOSE 8000

# Container health is the application /health/ endpoint (FR-25, §10.3).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8000/health/ || exit 1

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
