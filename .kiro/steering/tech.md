# Texnologiyalar (Tech)

## Backend

- **Python 3.11 / 3.12** (CI matritsasi ikkalasini ham tekshiradi; kod 3.11+ mos).
- **Django 5.1** - web framework.
- **Django REST Framework 3.15** + **drf-spectacular** - REST API va OpenAPI.
- **django-filter** - filtrlash va qidiruv.
- **PostgreSQL** (prod/CI) - asosiy baza; `btree_gist` + `ExclusionConstraint`.
- **SQLite** (lokal/test fallback) - tez va izolyatsiyalangan testlar.
- **gunicorn** + **whitenoise** - prod WSGI server va statik fayllar.
- **psycopg2-binary**, **Pillow**, **python-dotenv**.

## Frontend

- **Bootstrap 5** + **Bootstrap Icons**, **Inter/Poppins** shriftlari.
- Vanilla JS: mavzu toggle (localStorage), interaktiv zal/stol sxemasi, toaster.
- **Chart.js** - dashboard grafiklari.
- Iliq "cafe" rang palitrasi, CSS custom properties, yorug'/qorong'i mavzu.

## Sifat va test

- **pytest** + **pytest-django** + **pytest-cov** + **factory_boy**; qamrov darvozasi >= 80%.
- **ruff** (lint + format), **mypy** (django-stubs) - `pyproject.toml` da sozlangan.
- **pre-commit**: ruff, trailing-whitespace, check-yaml, detect-secrets.

## DevOps / CI-CD

- **Docker**: multi-stage `Dockerfile` (python:3.12-slim, non-root, HEALTHCHECK),
  `entrypoint.sh`, `docker-compose.yml` (web + db + nginx), `docker-compose.dev.yml`.
- **GitHub Actions**: `ci`, `security` (bandit/pip-audit/CodeQL), `docker` (GHCR +
  Trivy), `cd` (staging -> production, GitHub Environments + approval, /health/
  smoke-test), `release`, `docs`, `stale`, `labeler`.
- **Dependabot**: pip, docker, github-actions.

## Qoidalar

- Barcha dependency'lar `==` bilan qat'iy pin qilinadi (NFR-10).
- Sirlar faqat `.env` (lokal) yoki GitHub Secrets (CI) orqali. Workflow'larda
  butun muhitni dump qiluvchi buyruqlar (printenv/env) taqiqlanadi.
- Biznes-logika `services.py` ichida; view'lar yupqa.

## Muhim buyruqlar (Makefile)

- `make install` - dev bog'liqliklar.
- `make migrate` / `make seed` - baza va demo ma'lumotlar.
- `make run` - dev server.
- `make lint` / `make format` / `make typecheck` - sifat.
- `make test` - testlar (qamrov bilan).
- `make diagrams` - UML diagrammalarni render (Kroki).
- `make docker-up` / `make docker-down` - Docker stek.
