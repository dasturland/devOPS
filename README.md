# TableReserve - kafe stol rezervatsiyasi platformasi

[![CI](https://github.com/dasturland/devOPS/actions/workflows/ci.yml/badge.svg)](https://github.com/dasturland/devOPS/actions/workflows/ci.yml)
[![Security](https://github.com/dasturland/devOPS/actions/workflows/security.yml/badge.svg)](https://github.com/dasturland/devOPS/actions/workflows/security.yml)
[![Docker](https://github.com/dasturland/devOPS/actions/workflows/docker.yml/badge.svg)](https://github.com/dasturland/devOPS/actions/workflows/docker.yml)
[![CD](https://github.com/dasturland/devOPS/actions/workflows/cd.yml/badge.svg)](https://github.com/dasturland/devOPS/actions/workflows/cd.yml)
[![Docs](https://github.com/dasturland/devOPS/actions/workflows/docs.yml/badge.svg)](https://github.com/dasturland/devOPS/actions/workflows/docs.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)

> Fan: **DevOps va CI/CD texnologiyalari** (amaliy mashg'ulot)
> Muallif: **Sadullayev Jaxongir**
> Til: interfeys va hujjatlar o'zbek (lotin); kod ingliz tilida.

---

## Loyiha haqida

**TableReserve** - kafelar uchun onlayn stol rezervatsiyasi platformasi. Mijozlar
bo'sh stolni sana, vaqt, davomiylik va odam soniga ko'ra topib bron qiladi; kafe
menejerlari bronlarni tasdiqlaydi/rad etadi va kunlik jadvalni boshqaradi;
administrator butun platforma statistikasini ko'radi.

Loyiha spec-driven (Kiro) jarayonida ishlab chiqilgan: `requirements.md` ->
`design.md` -> `tasks.md` -> amalga oshirish. Asosiy e'tibor **DevOps/CI-CD** quvuriga:
Docker, GitHub Actions (CI, xavfsizlik, image build, deploy, release), test qamrovi
va avtomatlashtirilgan sifat tekshiruvlariga qaratilgan.

## Asosiy imkoniyatlar

- Bo'sh stol qidiruvi va **3 qadamli bron wizardi** (vaqt -> stol -> tasdiqlash).
- **To'qnashuvdan himoyalangan** bron: `transaction.atomic` + `select_for_update` +
  PostgreSQL `ExclusionConstraint` (SQLite'da service-darajadagi tekshiruv).
- **Holatlar mashinasi**: PENDING -> CONFIRMED/REJECTED/CANCELLED -> COMPLETED/NO_SHOW.
- **2 soat qoidasi** bilan bekor qilish; yakunlangan bron uchun bir martalik sharh.
- **RBAC**: ADMIN / MANAGER / CUSTOMER / WAITER rollari.
- **Chart.js** statistika paneli; `/health/` health-check; **REST API** (OpenAPI).
- Iliq "cafe" dizayn tili, **yorug'/qorong'i mavzu**, responsiv va accessible UI.

## Texnologiyalar

| Qatlam | Texnologiya |
|--------|-------------|
| Backend | Python 3.11/3.12, Django 5.1, DRF 3.15, drf-spectacular, django-filter |
| Baza | PostgreSQL (prod/CI), SQLite (lokal/test) |
| Frontend | Bootstrap 5, Bootstrap Icons, Inter/Poppins, Chart.js, vanilla JS |
| Server | gunicorn, whitenoise, nginx |
| Test/Sifat | pytest, pytest-django, pytest-cov, factory_boy, ruff, mypy, pre-commit |
| DevOps | Docker (multi-stage), docker-compose, GitHub Actions, Dependabot, Trivy, CodeQL |

## O'rnatish - lokal

```bash
git clone https://github.com/dasturland/devOPS.git
cd devOPS

python -m venv .venv && source .venv/bin/activate
make install            # pip install -r requirements/dev.txt

cp .env.example .env     # kerakli qiymatlarni to'ldiring (SECRET_KEY, ...)

make migrate
make seed                # demo ma'lumotlar (idempotent)
make run                 # http://127.0.0.1:8000
```

## O'rnatish - Docker

```bash
cp .env.example .env     # SECRET_KEY va POSTGRES_* ni to'ldiring
make docker-up           # docker compose up -d --build
# Ilova: http://localhost  (nginx -> web),  health: http://localhost/health/
make docker-down
```

Dev stek (runserver + Postgres): `docker compose -f docker-compose.dev.yml up --build`.

## Demo akkauntlar

`make seed` quyidagi akkauntlarni yaratadi (parol hammasiga: **`demo12345`**):

| Rol | Email |
|-----|-------|
| Admin | `admin@tablereserve.uz` |
| Menejer 1 | `manager1@tablereserve.uz` |
| Menejer 2 | `manager2@tablereserve.uz` |
| Mijozlar | `customer1@tablereserve.uz` … `customer5@tablereserve.uz` |

## Loyiha strukturasi

```
config/        Django sozlamalari (base/dev/prod/test), urls, wsgi/asgi
apps/          core, accounts, cafes, tables, reservations, reviews, dashboard, api
templates/     Django shablonlari (base.html, errors/, ...)
static/        css/js/img (mavzu toggle, zal sxemasi, toaster, Chart.js)
tests/         pytest: conftest, factories, test_*.py (>= 80% qamrov)
docs/          requirements, architecture, cicd, deployment, HIMOYA, HISOBOT, diagrams/
scripts/       render_diagrams.py (Kroki)
.github/       workflows/, dependabot.yml, templates, CODEOWNERS
.kiro/         specs/, steering/, hooks/
Dockerfile, entrypoint.sh, docker-compose*.yml, nginx/, Makefile
```

To'liq tuzilma: [`docs/architecture.md`](./docs/architecture.md).

## CI/CD

8 ta GitHub Actions workflow'i quvurni tashkil qiladi:

- **ci.yml** - ruff lint + format, mypy, `manage.py check`, migratsiya tekshiruvi,
  Python 3.11/3.12 matritsasida PostgreSQL servisi bilan `pytest --cov` (qamrov < 80% => fail), coverage artifact.
- **security.yml** - bandit, pip-audit, CodeQL (haftalik cron).
- **docker.yml** - image build, Trivy skan, GHCR'ga push (latest/SHA/versiya teglari), buildx cache.
- **cd.yml** - staging -> production (GitHub Environments + manual approval), `/health/` smoke-test.
- **release.yml** - `v*.*.*` tag -> GitHub Release + changelog.
- **docs.yml** - `render_diagrams.py` (Kroki).
- **stale.yml**, **labeler.yml** - repo gigienasi.

Qadam-baqadam tushuntirish, secrets ro'yxati va branch protection: [`docs/cicd.md`](./docs/cicd.md).

## API hujjati

- OpenAPI schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- Health-check: `/health/` -> `{"status":"ok","database":"ok"}`

## Hujjatlar

- [Talablar](./docs/requirements.md) · [Arxitektura](./docs/architecture.md)
- [CI/CD](./docs/cicd.md) · [Deploy](./docs/deployment.md)
- [Himoya taqdimoti](./docs/HIMOYA.md) · [Amaliy ish hisoboti](./docs/HISOBOT.md)
- [O'zgarishlar jurnali](./CHANGELOG.md)

## Litsenziya

[MIT](./LICENSE) © 2025 Sadullayev Jaxongir.
