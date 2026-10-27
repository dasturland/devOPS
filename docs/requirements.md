# Talablar xulosasi (Requirements)

Ushbu hujjat to'liq spetsifikatsiya
([`.kiro/specs/table-reservation/requirements.md`](../.kiro/specs/table-reservation/requirements.md))
ning qisqartirilgan amaliy xulosasidir. Rasmiy, to'liq EARS formatidagi talablar
spec faylida saqlanadi.

## Aktyorlar (rollar)

| Rol | Vakolatlar |
|-----|-----------|
| Mehmon | Kafelarni ko'rish, bo'sh stol qidirish, ro'yxatdan o'tish |
| Mijoz (CUSTOMER) | Bron qilish, bronlarni boshqarish, bekor qilish, sharh qoldirish |
| Menejer (MANAGER) | Kafe/zona/stol CRUD, bronlarni tasdiqlash/rad etish, kunlik jadval |
| Ofitsiant (WAITER) | Kunlik jadval, bron holatlari |
| Administrator (ADMIN) | Platforma statistikasi, umumiy boshqaruv |

## Funksional talablar (FR) — guruhlar

| FR | Mavzu |
|----|-------|
| FR-01…FR-07 | Auth, ro'yxatdan o'tish, parol tiklash, RBAC |
| FR-08…FR-10 | Kafe, zona va stol CRUD |
| FR-11…FR-15 | Bo'sh stol qidiruvi va bron yaratish (ish vaqti, o'tmish, sig'im, to'qnashuv) |
| FR-16…FR-18 | Holat mashinasi, tasdiqlash/rad etish, 2 soat bekor qilish qoidasi |
| FR-19…FR-20 | "Mening bronlarim", menejer kunlik jadvali |
| FR-21 | Yakunlangan bron uchun bir martalik sharh (1–5) |
| FR-22…FR-24 | Dashboard statistikasi, REST API, OpenAPI |
| FR-25…FR-30 | Health-check, audit log, xato sahifalar, mavzu toggle |

## Nofunksional talablar (NFR) — guruhlar

| NFR | Mavzu |
|-----|-------|
| NFR-01…NFR-02 | Parol xavfsizligi, sirlar boshqaruvi (secrets .env/GitHub Secrets) |
| NFR-03 | Unumdorlik (indekslar, `select_related`/`prefetch_related`) |
| NFR-04 | Responsiv va accessible UI |
| NFR-05 | Test qamrovi >= 80% |
| NFR-06 | Konteynerlashtirish (Docker) |
| NFR-07 | CI/CD (GitHub Actions) |
| NFR-08 | Logging |
| NFR-09 | Kod sifati (ruff, mypy, pre-commit) |
| NFR-10 | Qat'iy pinned bog'liqliklar (`==`) |
| NFR-11 | Baza mosligi (PostgreSQL/SQLite) |
| NFR-12 | Hujjatlar va UML diagrammalar |

## Asosiy biznes qoidalari

- **Double-booking taqiqlanadi**: bir stol uchun faol bronlarning vaqt oraliqlari
  kesishmaydi (`s1 < e2 AND s2 < e1`).
- **Ish vaqti**: bron butunlay kafe ochilish–yopilish vaqti ichida bo'lishi kerak.
- **O'tmish**: o'tgan vaqtga bron qilib bo'lmaydi.
- **Sig'im**: odam soni stol sig'imidan oshmasligi kerak.
- **Bekor qilish**: boshlanishiga kamida 2 soat qolganda mumkin.
- **Sharh**: faqat COMPLETED bron uchun, faqat egasi, faqat bir marta.
