# Loyiha tuzilmasi (Structure)

```
devOPS/
├── config/                  # Django loyiha konfiguratsiyasi
│   ├── settings/            # base / dev / prod / test (split settings)
│   ├── urls.py              # root URLConf (+ handler403/404/500)
│   ├── wsgi.py / asgi.py
├── apps/                    # domen ilovalari
│   ├── core/                # TimeStampedModel, AuditLog, health, exceptions,
│   │   └── management/commands/seed_demo_data.py
│   ├── accounts/            # User (role), auth, RBAC, DRF permissions
│   ├── cafes/               # Cafe, Zone
│   ├── tables/              # Table
│   ├── reservations/        # qidiruv, bron wizardi, to'qnashuv, holat mashinasi
│   ├── reviews/             # Review (completed-only, once-per-reservation)
│   ├── dashboard/           # statistika servislari va view'lari
│   └── api/                 # DRF routerlar + drf-spectacular schema/docs
├── templates/               # Django shablonlari (base.html, errors/, ...)
├── static/                  # css/main.css, js/theme.js, js/ui.js, img/
├── tests/                   # pytest: conftest, factories, test_*.py
├── docs/                    # requirements, architecture, cicd, deployment, HIMOYA,
│   └── diagrams/            # 10 ta UML manba (.puml/.mmd) + render natijalari
├── scripts/render_diagrams.py
├── requirements/            # base.txt / dev.txt / prod.txt (pinned ==)
├── .github/                 # workflows/, dependabot.yml, templates, CODEOWNERS
├── .kiro/                   # specs/ (requirements, design, tasks), steering/, hooks/
├── Dockerfile, entrypoint.sh, docker-compose*.yml, nginx/
├── Makefile, pyproject.toml, LICENSE
```

## Qatlamlar (layered architecture)

1. **Prezentatsiya** — Django views/templates va DRF ViewSet/Serializer/Permission.
2. **Biznes-logika** — har ilovaning `services.py` (asosiy qoidalar shu yerda).
3. **Ma'lumotlar** — Django ORM modellari (indekslar va cheklovlar bilan).

So'rov faqat quyidagi qatlamga tushadi; `views` ingichka, logika `services` da.

## Konvensiyalar

- Model abstraksiyasi: barcha domen modellari `core.TimeStampedModel` dan meros.
- Maxsus User: `accounts.User` (email = USERNAME_FIELD, `role` maydoni).
- Holatlar: `ReservationStatus`, `TableStatus`, `ZoneType`, `Role` — `TextChoices`.
- Audit: muhim amallar `core.services.record_audit` orqali `AuditLog` ga yoziladi.
- Sozlamalar split: `config.settings.{base,dev,prod,test}`.
