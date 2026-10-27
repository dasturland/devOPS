# Amaliy ish hisoboti (HISOBOT)

> Fan: **DevOps va CI/CD texnologiyalari** · Amaliy mashg'ulot
> Mavzu: **TableReserve** — kafe stol rezervatsiyasi platformasi
> Muallif: **Sadullayev Jaxongir**

## 1. Ishning maqsadi

To'liq funksional web-ilovani (Django) spec-driven jarayonda ishlab chiqish va
unga zamonaviy **DevOps/CI-CD** amaliyotlarini qo'llash: konteynerlashtirish,
avtomatlashtirilgan testlar va sifat tekshiruvlari, xavfsizlik skanerlari,
avtomatik image build/deploy va reliz jarayoni.

## 2. Qo'yilgan vazifalar

1. Talablar (requirements) va dizayn (design) hujjatlarini tayyorlash.
2. Django ilovasini qatlamli arxitekturada qurish (8 ilova).
3. Biznes qoidalarini amalga oshirish: qidiruv, bron, to'qnashuv, holat mashinasi, sharh.
4. Frontend: iliq dizayn tili, mavzu toggle, interaktiv zal sxemasi, dashboard.
5. Testlar: >= 40 test, qamrov >= 80%, edge-case'lar.
6. UML diagrammalar (10 ta) va Kroki render skripti.
7. Docker va GitHub Actions CI/CD quvuri (8 workflow).
8. Hujjatlar (o'zbek, lotin) va repo meta fayllari.

## 3. Bajarilgan ishlar

### 3.1. Backend

- Maxsus `User` modeli (email login, `role`), RBAC, DRF permissions.
- `Cafe`/`Zone`/`Table`/`Reservation`/`Review`/`AuditLog` modellari, indekslar va cheklovlar.
- `services.py` qatlamida biznes logika; `transaction.atomic` + `select_for_update`
  + PostgreSQL `ExclusionConstraint` bilan double-booking himoyasi.
- Holat mashinasi (`ALLOWED_TRANSITIONS`), 2 soat bekor qilish qoidasi.
- REST API (DRF) + OpenAPI (drf-spectacular), `/health/` health-check, audit log.

### 3.2. Frontend

- Bootstrap 5 + Bootstrap Icons, Inter/Poppins; iliq "cafe" palitra (CSS custom properties).
- Yorug'/qorong'i mavzu toggle (localStorage); responsiv va accessible (skip-link, aria, kontrast).
- Bosh sahifa (hero + qidiruv + kafelar + "qanday ishlaydi" + sharhlar), 3 qadamli
  bron wizardi, interaktiv zal/stol sxemasi, Chart.js dashboard, toast, empty/loading, 403/404/500.

### 3.3. Sifat va test

- `pytest` + `factory_boy`; 80+ test; qamrov darvozasi >= 80% (`pyproject.toml`).
- `ruff` (lint + format), `mypy` (django-stubs), `pre-commit` (ruff, check-yaml, detect-secrets).

### 3.4. DevOps / CI-CD

- Multi-stage Dockerfile (non-root, HEALTHCHECK), entrypoint, compose (web+db+nginx), dev compose.
- 8 ta GitHub Actions workflow'i (ci, security, docker, cd, release, docs, stale, labeler).
- Dependabot (pip, docker, github-actions); pinned dependencies (`==`).

### 3.5. Hujjatlar

- README (badge'lar, o'rnatish, demo akkauntlar, struktura, CI/CD), docs/* (talablar,
  arxitektura, cicd, deployment, HIMOYA), 10 UML diagramma, CHANGELOG.

## 4. Qiyinchiliklar va yechimlar

| Qiyinchilik | Yechim |
|-------------|--------|
| Double-booking (parallel so'rovlar) | `transaction.atomic` + `select_for_update` + exclusion constraint |
| PostgreSQL-ga xos cheklov SQLite'da ishlamaydi | Shartli migratsiya (`connection.vendor`) + service-darajadagi tekshiruv |
| Sirlar CI'da | GitHub Secrets/Environments; workflow'da env dump yo'q |
| Diagramma render tarmoqqa bog'liq | Kroki + graceful degrade (offline'da manbalar qoladi, exit 0) |

## 5. Natijalar

To'liq ishlaydigan, testlangan va konteynerlangan platforma; avtomatlashtirilgan
CI/CD quvuri; spec-driven hujjatlar to'plami. Loyiha barcha funksional (FR-01..FR-30)
va nofunksional (NFR-01..NFR-12) talablarni qondiradi.

## 6. Xulosa

Amaliy ish davomida Django asosida real web-ilova qurildi va unga zamonaviy
DevOps amaliyotlari (Docker, GitHub Actions, avtomatik test/qamrov darvozasi,
xavfsizlik skanerlari, image registry va boshqariladigan deploy) to'liq qo'llanildi.
Spec-driven yondashuv talablardan kodgacha bo'lgan izchil, kuzatiladigan jarayonni
ta'minladi.
