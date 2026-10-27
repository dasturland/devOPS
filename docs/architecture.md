# Arxitektura (Architecture)

To'liq texnik dizayn: [`.kiro/specs/table-reservation/design.md`](../.kiro/specs/table-reservation/design.md).
Ushbu hujjat amaliy xulosa va diagramma havolalarini beradi.

## Qatlamli arxitektura

```
Brauzer (Bootstrap 5 + Chart.js)
        │
┌───────▼─────────────────────────────┐
│ Prezentatsiya qatlami                │
│  • Django views + templates          │
│  • DRF ViewSets + Serializers + Perms│
└───────┬─────────────────────────────┘
        │
┌───────▼─────────────────────────────┐
│ Biznes-logika (services.py)          │
│  accounts/cafes/tables/reservations/ │
│  reviews/dashboard/core              │
└───────┬─────────────────────────────┘
        │
┌───────▼─────────────────────────────┐
│ Ma'lumotlar (Django ORM modellari)   │
└───────┬─────────────────────────────┘
        │
   PostgreSQL / SQLite
```

Tamoyil: so'rov yuqoridan pastga faqat bevosita quyidagi qatlam orqali o'tadi;
biznes qoidalari `services.py` da to'planadi, view'lar ingichka.

## Ilovalar (apps)

| Ilova | Mas'uliyat |
|-------|-----------|
| `core` | `TimeStampedModel`, `AuditLog`, health-check, exceptions, mixins, seed |
| `accounts` | `User` (role), auth, RBAC, DRF permissions |
| `cafes` | `Cafe`, `Zone` CRUD va servislar |
| `tables` | `Table` CRUD va noyoblik tekshiruvi |
| `reservations` | qidiruv, bron yaratish, to'qnashuv, holat mashinasi |
| `reviews` | `Review` (completed-only, once-per-reservation) |
| `dashboard` | statistika agregatsiyasi, Chart.js konteksti |
| `api` | DRF routerlar, drf-spectacular schema/docs |

## To'qnashuvning oldini olish (FR-13)

1. `transaction.atomic` ichida stol `select_for_update` bilan qulflanadi.
2. Faol (PENDING/CONFIRMED) bronlar bilan vaqt kesishmasi tekshiriladi.
3. PostgreSQL'da qo'shimcha kafolat — `btree_gist` + `ExclusionConstraint`
   (shartli migratsiya, faqat `connection.vendor == "postgresql"`).
4. SQLite'da service-darajadagi `select_for_update` + overlap tekshiruvi.

## Holat mashinasi (FR-16)

```
PENDING ──confirm──▶ CONFIRMED ──complete──▶ COMPLETED (terminal)
   │                     │
   ├──reject──▶ REJECTED │──no_show──▶ NO_SHOW (terminal)
   └──cancel──▶ CANCELLED (terminal)   │
                      CONFIRMED ──cancel──▶ CANCELLED
```

Noqonuniy o'tishda `InvalidTransitionError`; har o'tishda audit + xabar.

## UML diagrammalar

Manbalar [`docs/diagrams/`](./diagrams/) da (Kroki orqali render qilinadi):

| # | Diagramma | Fayl |
|---|-----------|------|
| 1 | Use case | `usecase.puml` |
| 2 | Activity — bron yaratish | `activity-reservation.puml` |
| 3 | Activity — tasdiqlash/rad etish | `activity-approval.puml` |
| 4 | Activity — bekor qilish | `activity-cancellation.puml` |
| 5 | Class | `class.puml` |
| 6 | Sequence — bron yaratish | `sequence-reservation.puml` |
| 7 | ER | `er.mmd` |
| 8 | Deployment | `deployment.puml` |
| 9 | Component | `component.puml` |
| 10 | CI/CD pipeline | `cicd-pipeline.puml` |

Render: `make diagrams` (tarmoq bo'lmasa, manbalar o'zgarmaydi — graceful degrade).
