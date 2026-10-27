# Deploy (Deployment)

## Konteyner tuzilishi

- **Dockerfile** — multi-stage (`python:3.12-slim`):
  - *builder* bosqichi: virtualenv + `requirements/prod.txt` (compilers bilan).
  - *runtime* bosqichi: slim, non-root `app` foydalanuvchisi, `collectstatic`,
    `HEALTHCHECK` `/health/` ga `curl` qiladi.
- **entrypoint.sh** — bazani kutadi (TCP poll), `migrate`, `collectstatic`,
  so'ng gunicorn (yoki CMD) ni `exec` qiladi.
- **docker-compose.yml** — `web` (gunicorn) + `db` (PostgreSQL 16) + `nginx`.
- **docker-compose.dev.yml** — `web` (runserver) + `db`, manba mount qilingan.
- **nginx/default.conf** — statik/media'ni to'g'ridan-to'g'ri, qolganini `web`ga proxy.

## Lokal Docker bilan ishga tushirish

```bash
cp .env.example .env
# majburiy: SECRET_KEY; tavsiya: POSTGRES_PASSWORD, ALLOWED_HOSTS
make docker-up                 # docker compose up -d --build
curl -fsS http://localhost/health/   # {"status":"ok","database":"ok"}
make docker-down
```

## Muhit o'zgaruvchilari (prod)

| O'zgaruvchi | Tavsif |
|-------------|--------|
| `SECRET_KEY` | Django maxfiy kaliti (majburiy) |
| `DEBUG` | `0` (prod) |
| `ALLOWED_HOSTS` | vergul bilan ajratilgan hostlar |
| `CSRF_TRUSTED_ORIGINS` | ishonchli originlar |
| `DATABASE_URL` yoki `POSTGRES_*` | PostgreSQL ulanishi |
| `EMAIL_*` | SMTP sozlamalari (FR-27) |
| `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS` | xavfsizlik sarlavhalari |

Barcha qiymatlar `.env` (lokal) yoki deploy platformasi secret'lari orqali beriladi.

## Image (GHCR)

`docker.yml` workflow'i har `main` push va `v*.*.*` tagda image'ni GHCR'ga
yuboradi:

```
ghcr.io/dasturland/devops:latest
ghcr.io/dasturland/devops:sha-<commit>
ghcr.io/dasturland/devops:<versiya>
```

## Deploy oqimi (cd.yml)

1. `Docker` workflow'i image'ni build qilib GHCR'ga yuboradi.
2. `cd.yml` ishga tushadi: avval **staging** ga deploy -> `/health/` smoke-test.
3. **production** job GitHub Environment orqali **manual approval** kutadi.
4. Tasdiqlangach production ga deploy -> `/health/` smoke-test.

## Health-check

`GET /health/`:

- 200 — `{"status":"ok","database":"ok"}` (DB `SELECT 1` muvaffaqiyatli).
- 503 — `{"status":"error","database":"down"}`.

Dockerfile `HEALTHCHECK` va cd.yml smoke-test shu endpointga tayanadi.

## Migratsiya va demo ma'lumotlar

Konteyner ishga tushganda `entrypoint.sh` avtomatik `migrate` qiladi. Demo
ma'lumotlarni yuklash uchun:

```bash
docker compose exec web python manage.py seed_demo_data
```
