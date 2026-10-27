# CI/CD quvuri (CI/CD Pipeline)

Barcha workflow'lar [`.github/workflows/`](../.github/workflows/) da. Har birida
`concurrency`, minimal `permissions` va `timeout-minutes` belgilangan.

> **Xavfsizlik qoidasi:** workflow'larda butun muhitni dump qiluvchi buyruqlar
> (`printenv`, `env`, `os.environ` dump va h.k.) ishlatilmaydi. Sirlar faqat
> kerakli qadamga, aniq o'zgaruvchi sifatida beriladi.

## 1. `ci.yml` - Continuous Integration

Trigger: `push`/`pull_request` (`main`, `develop`).

**lint** job (Python 3.12):
1. `actions/checkout`
2. `setup-python` (pip cache, `requirements/dev.txt`)
3. `pip install -r requirements/dev.txt`
4. `ruff check .`
5. `ruff format --check .`
6. `mypy apps config`

**test** job (matritsa: 3.11, 3.12; PostgreSQL 16 service):
1. checkout + setup-python (pip cache)
2. `pip install -r requirements/dev.txt`
3. `python manage.py check`
4. `python manage.py makemigrations --check --dry-run`
5. `pytest --cov ...` - qamrov < 80% bo'lsa fail (`pyproject.toml`: `fail_under = 80`)
6. coverage (`coverage.xml` + `htmlcov/`) artifact sifatida yuklanadi

Test runi `DATABASE_URL` orqali PostgreSQL service konteyneriga ulanadi
(`config.settings.test` `DATABASE_URL` bo'lsa Postgres'ni, aks holda SQLite'ni ishlatadi).

## 2. `security.yml` - Xavfsizlik

Trigger: `push`/`pull_request` (`main`) + haftalik cron (`0 6 * * 1`).

- **audit**: `bandit -r apps config -ll`, `pip-audit -r requirements/prod.txt`.
- **codeql**: `github/codeql-action` (Python), `security-events: write`.

## 3. `docker.yml` - Image build va GHCR push

Trigger: `push` (`main`, `v*.*.*` teglari), `pull_request` (`main`).

1. Buildx sozlanadi.
2. GHCR'ga login (PR'larda emas - fork xavfsizligi).
3. `docker/metadata-action` teglar: branch, `sha`, `semver` versiya, `latest`.
4. Image lokal build (`load: true`) -> **Trivy** skan (CRITICAL/HIGH) -> SARIF upload.
5. PR bo'lmasa, GHCR'ga push; buildx gha cache.

## 4. `cd.yml` - Deploy (staging -> production)

Trigger: `Docker` workflow muvaffaqiyatli tugaganda (`workflow_run`) yoki `workflow_dispatch`.

- **staging** job: `environment: staging`, deploy + `/health/` smoke-test.
- **production** job: `needs: staging`, `environment: production` -
  **manual approval** (GitHub Environment reviewer) talab qilinadi; deploy + `/health/` smoke-test.

## 5. `release.yml` - Release

Trigger: `v*.*.*` tag push. `CHANGELOG.md` dan tegishli versiya bo'limini ajratib
oladi va `softprops/action-gh-release` bilan GitHub Release yaratadi
(`permissions: contents: write`).

## 6. `docs.yml` - Diagrammalar

Trigger: `docs/diagrams/**` yoki render skripti o'zgarsa. `render_diagrams.py` ni
ishga tushiradi va natijalarni artifact qiladi (offline'da graceful degrade).

## 7–8. `stale.yml`, `labeler.yml`

- `stale.yml`: eski issue/PR'larni belgilaydi/yopadi (kunlik cron).
- `labeler.yml`: `.github/labeler.yml` qoidalari bo'yicha PR'larni yorliqlaydi.

## Kerakli secrets va variables

| Nomi | Turi | Ishlatilishi |
|------|------|-------------|
| `GITHUB_TOKEN` | avtomatik | GHCR push, SARIF upload, release |
| `STAGING_HOST` | Secret | staging deploy maqsadi |
| `PRODUCTION_HOST` | Secret | production deploy maqsadi |
| `STAGING_URL` | Variable (env) | staging `/health/` smoke-test |
| `PRODUCTION_URL` | Variable (env) | production `/health/` smoke-test |

Ilova sirlarini (`SECRET_KEY`, `POSTGRES_*`, `EMAIL_*`) deploy muhitida secret
sifatida bering - hech qachon kodga yozmang.

## Branch protection (tavsiya etilgan)

`main` branchi uchun:

- PR majburiy; kamida 1 ta review (CODEOWNERS).
- `CI / lint` va `CI / test (3.11, 3.12)` statuslari majburiy (yashil).
- Linear history; force-push taqiqlangan.
- `production` Environment uchun majburiy reviewer (manual approval).
