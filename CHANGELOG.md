# O'zgarishlar jurnali (Changelog)

Ushbu loyiha [Keep a Changelog](https://keepachangelog.com/) uslubiga va
[Semantic Versioning](https://semver.org/) ga amal qiladi.

## [1.0.0] - 2025-01-01

Birinchi barqaror reliz — TableReserve kafe stol rezervatsiyasi platformasi.

### Added

- Maxsus `User` modeli (email login, `role`), RBAC va DRF permissions (FR-01..FR-07).
- Kafe, zona va stol boshqaruvi (CRUD) hamda servislar (FR-08..FR-10).
- Bo'sh stol qidiruvi va 3 qadamli bron wizardi (FR-11, FR-12).
- Double-booking himoyasi: `transaction.atomic` + `select_for_update` +
  PostgreSQL `ExclusionConstraint` (FR-13).
- Ish vaqti, o'tmish va sig'im validatsiyasi (FR-14, FR-15).
- Bron holatlari mashinasi va 2 soat bekor qilish qoidasi (FR-16..FR-18).
- "Mening bronlarim" va menejer kunlik jadvali (FR-19, FR-20).
- Yakunlangan bron uchun bir martalik sharh (FR-21).
- Chart.js statistika paneli (FR-22), REST API va OpenAPI hujjati (FR-23, FR-24).
- Health-check, audit log, maxsus 403/404/500 sahifalari, mavzu toggle (FR-25..FR-30).
- Iliq "cafe" dizayn tili, interaktiv zal/stol sxemasi, responsiv va accessible UI.
- `seed_demo_data` idempotent management komandasi (FR-28).
- pytest test to'plami (80+ test), qamrov darvozasi >= 80%.
- 10 ta UML diagramma manbasi va Kroki render skripti (graceful degrade).
- Multi-stage Dockerfile (non-root, HEALTHCHECK), entrypoint, docker-compose (web+db+nginx), dev compose.
- GitHub Actions: ci, security (bandit/pip-audit/CodeQL), docker (GHCR + Trivy),
  cd (staging -> production, approval, /health/ smoke-test), release, docs, stale, labeler.
- Repo meta: dependabot, PR/issue shablonlari, CODEOWNERS, CONTRIBUTING, SECURITY,
  CODE_OF_CONDUCT, pre-commit, Makefile, MIT litsenziya.
- Hujjatlar (o'zbek, lotin): README, requirements, architecture, cicd, deployment, HIMOYA, HISOBOT.

### Security

- Sirlar faqat `.env` / GitHub Secrets orqali; prod'da HTTPS redirect, HSTS,
  secure cookie, `X-Frame-Options: DENY`.
- Pinned dependencies (`==`), avtomatik CVE va SAST skanerlari.

[1.0.0]: https://github.com/dasturland/devOPS/releases/tag/v1.0.0
