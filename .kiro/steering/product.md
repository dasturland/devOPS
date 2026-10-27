# Mahsulot (Product)

## Nima bu?

**TableReserve** — kafelar uchun stol rezervatsiyasi platformasi. Mijozlar bo'sh
stolni sana, vaqt, davomiylik va odam soniga ko'ra topib, onlayn bron qiladi;
kafe menejerlari bronlarni tasdiqlaydi/rad etadi va kunlik jadvalni boshqaradi;
administrator butun platforma statistikasini ko'radi.

Loyiha "DevOps va CI/CD texnologiyalari" amaliy mashg'uloti doirasida, spec-driven
(Kiro) jarayonida ishlab chiqilgan. Muallif: **Sadullayev Jaxongir**.

## Asosiy foydalanuvchilar (rollar)

- **Mehmon** — kafelarni ko'radi, bo'sh stol qidiradi, ro'yxatdan o'tadi.
- **Mijoz (CUSTOMER)** — stol bron qiladi, bronlarini boshqaradi, sharh qoldiradi.
- **Menejer (MANAGER)** — o'z kafe(lar)ini, zonalarini, stollarini va bronlarini boshqaradi.
- **Ofitsiant (WAITER)** — kunlik jadval va bron holatlari bilan ishlaydi.
- **Administrator (ADMIN)** — platforma statistikasi va umumiy boshqaruv.

## Asosiy imkoniyatlar

- Bo'sh stol qidiruvi va 3 qadamli bron wizardi (vaqt -> stol -> tasdiqlash).
- To'qnashuvdan himoyalangan bron (transaction + select_for_update + PostgreSQL
  exclusion constraint).
- Bron holatlari mashinasi: PENDING -> CONFIRMED/REJECTED/CANCELLED ->
  COMPLETED/NO_SHOW (qonuniy o'tishlar nazorati).
- 2 soat qoidasi bilan bekor qilish.
- Yakunlangan bron uchun bir martalik sharh (1–5 yulduz).
- Chart.js bilan statistika paneli.
- REST API (drf-spectacular / OpenAPI) va `/health/` health-check.

## Mahsulot tamoyillari

- Interfeys va hujjatlar o'zbek (lotin) tilida; kod ingliz tilida.
- Xavfsizlik birinchi o'rinda: sirlar kodga yozilmaydi, RBAC qat'iy.
- Ishonchlilik: double-booking mumkin emas, holat o'tishlari validatsiya qilinadi.
- Kuzatiluvchanlik: har bir muhim amal AuditLog'ga yoziladi.
