# TableReserve: Talablar hujjati (Requirements)

> Kafe stol rezervatsiyasi platformasi
> Fan: DevOps va CI/CD texnologiyalari (Amaliy mashg'ulot)
> Muallif: Sadullayev Jaxongir
> Hujjat formati: EARS (Easy Approach to Requirements Syntax)
> Til: interfeys va hujjatlar o'zbek (lotin); kod va commit xabarlari ingliz tilida.

---

## 1. Kirish va hujjatning maqsadi

Ushbu hujjat **TableReserve** platformasining funksional va nofunksional talablarini
EARS formatida ("WHEN ... THE SYSTEM SHALL ...") belgilaydi. Hujjat spec-driven
jarayonning birinchi bosqichi bo'lib, keyingi `design.md` va `tasks.md` hujjatlari
uchun asos bo'lib xizmat qiladi.

Har bir talab quyidagi atributlarga ega:

- **Identifikator**: `FR-NN` (funksional) yoki `NFR-NN` (nofunksional).
- **EARS bayoni**: talabning rasmiy ifodasi.
- **Qabul mezonlari**: talab bajarilganini tasdiqlovchi, tekshiriladigan shartlar.

### 1.1. EARS shablonlari

| Shablon | Qo'llanilishi |
|---------|---------------|
| **Ubiquitous**: THE SYSTEM SHALL ... | Doimiy amal qiluvchi talab |
| **Event-driven**: WHEN <hodisa> THE SYSTEM SHALL ... | Hodisaga javob |
| **State-driven**: WHILE <holat> THE SYSTEM SHALL ... | Holat davomida |
| **Unwanted behaviour**: IF <shart> THEN THE SYSTEM SHALL ... | Xato/istisno holat |
| **Optional**: WHERE <xususiyat> THE SYSTEM SHALL ... | Shartli imkoniyat |

---

## 2. Tizimning maqsadi va vazifalari

### 2.1. Maqsad

Kafe va restoranlarda stollarni **onlayn band qilish** jarayonini
avtomatlashtirish. Platforma mijozlarga qulay bron qilish imkonini beradi, kafe
xodimlariga bandlikni nazorat qilish va tartibga solish vositasini taqdim etadi
hamda **ikki marta band qilish (double booking)** va qo'lda yuritiladigan
qog'oz daftarlarni butunlay bartaraf etadi.

### 2.2. Asosiy vazifalar

| # | Vazifa | Tavsif |
|---|--------|--------|
| V1 | Kafe, zona va stollarni boshqarish | Kafelar, zonalar (zal/terrasa/VIP) va stollarni ro'yxatga olish va CRUD |
| V2 | Bo'sh stollarni qidirish | Sana, vaqt, davomiylik, odam soni va zona bo'yicha bo'sh stollarni topish |
| V3 | Onlayn bron qilish | Mijoz tomonidan 3 qadamli (vaqt → stol → tasdiqlash) bron yaratish |
| V4 | Bronni boshqarish | Bronni tasdiqlash, rad etish, bajarildi va bekor qilish |
| V5 | Vaqt to'qnashuvining oldini olish | Bir stol uchun bir vaqt oralig'ida faqat bitta faol bron |
| V6 | Foydalanuvchilarni rollar bo'yicha boshqarish | Administrator, Kafe menejeri, Mijoz, (ixtiyoriy) Ofitsiant |
| V7 | Statistika va hisobotlar | Kunlik/haftalik bronlar, eng band stollar, bekor qilish foizi, grafiklar |
| V8 | Bildirishnomalar | Email (dev rejimda konsol backend) orqali holat o'zgarishlari xabari |
| V9 | Sharhlar va baholash | Yakunlangan bronlar uchun 1–5 yulduzli sharh va izoh |

---

## 3. Foydalanuvchilar (aktyorlar)

### 3.1. Asosiy aktyorlar

| Aktyor | Tavsif | Asosiy huquqlar | Asosiy amallar |
|--------|--------|------------------|----------------|
| **Mehmon** (ro'yxatdan o'tmagan) | Tizimga kirmagan foydalanuvchi | Faqat ko'rish | Bosh sahifani ko'rish, kafelarni ko'rish, bo'sh stollarni qidirish, ro'yxatdan o'tish |
| **Mijoz** (`CUSTOMER`) | Ro'yxatdan o'tgan oddiy foydalanuvchi | O'z bronlarini boshqarish | Bron yaratish, "Mening bronlarim"ni ko'rish, bronni bekor qilish, sharh qoldirish, profilni tahrirlash |
| **Kafe menejeri** (`MANAGER`) | Muayyan kafega biriktirilgan xodim | O'z kafesini boshqarish | Kelgan bronlarni tasdiqlash/rad etish, kunlik jadval va stol bandligini ko'rish, zona/stollarni boshqarish, kafe statistikasi |
| **Administrator** (`ADMIN`) | Platforma ma'muri | To'liq boshqaruv | Foydalanuvchilar, barcha kafelar, global statistika, audit log, tizim sozlamalari |
| **Ofitsiant** (`WAITER`, ixtiyoriy) | Kafega biriktirilgan xizmat xodimi | Cheklangan operatsion | Kunlik jadvalni ko'rish, bron holatini `COMPLETED`/`NO_SHOW` ga o'zgartirish |

### 3.2. Tashqi aktyorlar

| Aktyor | Tavsif | Integratsiya nuqtasi |
|--------|--------|----------------------|
| **Email xizmati** | SMTP provayderi (prod); konsol backend (dev) | Bron holati o'zgarganda xabar yuborish |
| **GitHub Actions (CI/CD)** | Avtomatlashtirilgan quvur tizimi | Lint, test, security scan, build, deploy, release |
| **Konteyner registri (GHCR)** | Docker image saqlovchi | Image push/pull |
| **Deploy platformasi** (Render/Railway/VPS) | Ishga tushirish muhiti | `/health/` smoke-test, deploy |

---

## 4. Funksional talablar (FR)

### 4.1. Autentifikatsiya va hisob boshqaruvi

**FR-01: Ro'yxatdan o'tish**
WHEN mehmon ro'yxatdan o'tish formasini to'g'ri ma'lumotlar (email, parol, ism) bilan yuborsa, THE SYSTEM SHALL yangi `CUSTOMER` rolidagi foydalanuvchi hisobini yaratsin va uni tizimga kiritsin.
*Qabul mezonlari:*
- Email takrorlanmas (unique) bo'lishi tekshiriladi; takroriy email uchun o'zbekcha xato ko'rsatiladi.
- Parol Django parol validatorlaridan (minimal uzunlik, umumiylik) o'tishi shart.
- Parol bazada xeshlangan holda saqlanadi (ochiq matnda emas).

**FR-02: Tizimga kirish (login)**
WHEN foydalanuvchi to'g'ri email va parol bilan login formasini yuborsa, THE SYSTEM SHALL seansni (session) ochib, foydalanuvchini rolига mos bosh panelga yo'naltirsin.
*Qabul mezonlari:*
- Noto'g'ri ma'lumotda "Email yoki parol noto'g'ri" xatosi ko'rsatiladi.
- Muvaffaqiyatli kirishda sessiya cookie o'rnatiladi.

**FR-03: Tizimdan chiqish (logout)**
WHEN tizimga kirgan foydalanuvchi "Chiqish" amalini bajarsa, THE SYSTEM SHALL uning seansini tugatib, bosh sahifaga yo'naltirsin.
*Qabul mezonlari:* Chiqishdan so'ng himoyalangan sahifalarga kirish login sahifasiga yo'naltiradi.

**FR-04: Parolni o'zgartirish**
WHILE foydalanuvchi tizimga kirgan holatda bo'lsa, THE SYSTEM SHALL joriy parolni tasdiqlash orqali yangi parol o'rnatish imkonini bersin.
*Qabul mezonlari:* Joriy parol noto'g'ri bo'lsa o'zgartirish rad etiladi; yangi parol validatsiyadan o'tadi.

**FR-05: Parolni tiklash**
WHEN foydalanuvchi parolni tiklash uchun o'z emailini kiritsa, THE SYSTEM SHALL tiklash havolasini (token bilan) email orqali yuborsin va havola orqali yangi parol o'rnatishga ruxsat bersin.
*Qabul mezonlari:*
- Mavjud bo'lmagan email uchun ham tizim mavjudlik haqida ma'lumot oshkor qilmaydi (xavfsizlik).
- Tiklash tokeni muddatli va bir martalik bo'ladi.

### 4.2. Rollar va ruxsatlar

**FR-06: Rolga asoslangan kirishni boshqarish (RBAC)**
THE SYSTEM SHALL har bir foydalanuvchiga `ADMIN`, `MANAGER`, `CUSTOMER` yoki `WAITER` rolini bersin va har bir sahifa/amalga faqat tegishli rol(lar)ga ruxsat bersin.
*Qabul mezonlari:*
- Maxsus `User` modeli `AbstractUser` + `role` maydoni bilan amalga oshiriladi.
- Ruxsat mixin, dekorator va DRF permission klasslari orqali qo'llanadi.

**FR-07: Ruxsatsiz kirishni rad etish**
IF foydalanuvchi roliga mos kelmaydigan sahifa yoki amalga kirishga urinsa, THEN THE SYSTEM SHALL 403 (Taqiqlangan) javobini chiroyli xato sahifasi bilan qaytarsin.
*Qabul mezonlari:* Menejer boshqa kafe bronlarini ko'ra/o'zgartira olmaydi; mijoz menejer paneliga kira olmaydi.

### 4.3. Kafe, zona va stol boshqaruvi (CRUD)

**FR-08: Kafe CRUD**
WHERE foydalanuvchi `ADMIN` yoki tegishli `MANAGER` bo'lsa, THE SYSTEM SHALL kafe yozuvini (nom, manzil, ish vaqti, telefon, tavsif, rasm) yaratish, ko'rish, tahrirlash va o'chirish imkonini bersin.
*Qabul mezonlari:* Ish vaqti (ochilish/yopilish) saqlanadi va bron tekshiruvida ishlatiladi.

**FR-09: Zona CRUD**
WHERE foydalanuvchi tegishli `MANAGER` yoki `ADMIN` bo'lsa, THE SYSTEM SHALL kafega tegishli zonalarni (`HALL`, `TERRACE`, `VIP`) yaratish va boshqarish imkonini bersin.
*Qabul mezonlari:* Har bir zona bitta kafega bog'langan (ManyToOne).

**FR-10: Stol CRUD**
WHERE foydalanuvchi tegishli `MANAGER` yoki `ADMIN` bo'lsa, THE SYSTEM SHALL zonaga tegishli stollarni (raqam, sig'im, holat) yaratish va boshqarish imkonini bersin.
*Qabul mezonlari:* Stol raqami kafe doirasida takrorlanmas; sig'im ≥ 1.

### 4.4. Qidirish va bron qilish

**FR-11: Bo'sh stollarni qidirish**
WHEN foydalanuvchi sana, boshlanish vaqti, davomiylik, odam soni va (ixtiyoriy) zonani kiritsa, THE SYSTEM SHALL shu mezonlarga mos keladigan va tanlangan oraliqda boshqa faol broni bo'lmagan bo'sh stollar ro'yxatini qaytarsin.
*Qabul mezonlari:*
- Odam soni stol sig'imidan oshmaydigan stollar qaytariladi.
- Band stollar natijaga kiritilmaydi.
- So'rov `select_related`/`prefetch_related` bilan optimallashtiriladi.

**FR-12: Onlayn bron yaratish (wizard)**
WHEN mijoz 3 qadamli bron wizardini (vaqt → stol → tasdiqlash) yakunlasa, THE SYSTEM SHALL `PENDING` holatidagi yangi bron yozuvini yaratib, mijozga va tegishli menejerga bildirishnoma yuborsin.
*Qabul mezonlari:* Bron mijoz, stol, boshlanish vaqti, davomiylik, odam soni va holat bilan saqlanadi.

**FR-13: Vaqt to'qnashuvining oldini olish**
IF so'ralgan stol va vaqt oralig'i mavjud faol bron (`PENDING`/`CONFIRMED`) bilan to'qnashsa, THEN THE SYSTEM SHALL bron yaratishni rad etib, o'zbekcha xato xabarini ko'rsatsin.
*Qabul mezonlari:*
- Tekshiruv `transaction.atomic` + `select_for_update` bilan race-condition'dan himoyalanadi.
- DB darajasida himoya: PostgreSQL'da `ExclusionConstraint`, fallback sifatida model `clean()` va servis tekshiruvi.
- Ikki parallel bir xil bron urinishidan faqat bittasi muvaffaqiyatli bo'ladi.

**FR-14: Ish vaqti va o'tmish cheklovi**
IF so'ralgan bron vaqti kafe ish vaqtidan tashqarida yoki o'tmishda bo'lsa, THEN THE SYSTEM SHALL bronni rad etib, tegishli o'zbekcha xato xabarini ko'rsatsin.
*Qabul mezonlari:* Boshlanish < hozirgi vaqt yoki oraliq ish vaqtidan chetga chiqsa rad etiladi.

**FR-15: Sig'im cheklovi**
IF bronga so'ralgan odam soni stol sig'imidan katta bo'lsa, THEN THE SYSTEM SHALL bronni rad etib, xato xabarini ko'rsatsin.
*Qabul mezonlari:* `guests_count > table.capacity` holatida bron saqlanmaydi.

### 4.5. Bron holatlari va boshqaruv

**FR-16: Bron holatlari hayot sikli**
THE SYSTEM SHALL bron holatini quyidagi o'tishlar bilan boshqarsin: `PENDING → CONFIRMED → COMPLETED`; hamda `CANCELLED`, `REJECTED`, `NO_SHOW`.
*Qabul mezonlari:* Noqonuniy holat o'tishlari (masalan, `COMPLETED → PENDING`) taqiqlanadi.

**FR-17: Menejer tomonidan tasdiqlash/rad etish**
WHEN menejer o'z kafesidagi `PENDING` bronni tasdiqlasa yoki rad etsa, THE SYSTEM SHALL bron holatini `CONFIRMED`/`REJECTED` ga o'zgartirib, mijozga bildirishnoma yuborsin.
*Qabul mezonlari:* Menejer faqat o'z kafesi bronlarini boshqara oladi; har o'zgarish audit logga yoziladi.

**FR-18: Mijoz tomonidan bekor qilish**
WHEN mijoz o'z bronini boshlanishiga kamida 2 soat qolganda bekor qilsa, THE SYSTEM SHALL holatni `CANCELLED` ga o'zgartirsin.
*Qabul mezonlari:* IF boshlanishgacha 2 soatdan kam qolgan bo'lsa, THEN bekor qilish rad etiladi va xato ko'rsatiladi.

**FR-19: "Mening bronlarim" sahifasi**
WHILE mijoz tizimga kirgan bo'lsa, THE SYSTEM SHALL unga o'z bronlari ro'yxatini (holat, sana, kafe, stol bo'yicha) filtrlash va saralash bilan ko'rsatsin.
*Qabul mezonlari:* Ro'yxat sahifalangan (pagination) va holat bo'yicha filtrlanadi.

**FR-20: Menejer kunlik jadvali va stol bandligi**
WHILE menejer tizimga kirgan bo'lsa, THE SYSTEM SHALL unga tanlangan kun uchun kelgan bronlar jadvalini va stollar bandligini ko'rsatsin.
*Qabul mezonlari:* Jadval sana bo'yicha filtrlanadi; har stol uchun band/bo'sh vaqtlar ko'rinadi.

### 4.6. Sharhlar

**FR-21: Sharh qoldirish**
WHEN mijoz o'zining `COMPLETED` holatidagi broni uchun 1–5 yulduzli baho va izoh yuborsa, THE SYSTEM SHALL sharhni tegishli kafega bog'lab saqlasin.
*Qabul mezonlari:*
- Faqat yakunlangan bron uchun va har bron uchun bir marta sharh beriladi.
- Kafe sahifasida o'rtacha reyting hisoblanadi.

### 4.7. Dashboard, statistika va API

**FR-22: Admin statistika dashboardi**
WHILE `ADMIN` tizimga kirgan bo'lsa, THE SYSTEM SHALL kunlik/haftalik bronlar soni, eng band stollar va bekor qilish foizini statistik kartalar va Chart.js grafiklari bilan ko'rsatsin.
*Qabul mezonlari:* Grafiklar real ma'lumotlardan hisoblanadi; sanalar bo'yicha filtr mavjud.

**FR-23: Qidiruv, filtr, saralash va sahifalash**
THE SYSTEM SHALL ro'yxat sahifalarida (kafelar, bronlar, foydalanuvchilar) qidiruv, filtr, saralash va sahifalashni ta'minlasin.
*Qabul mezonlari:* `django-filter` orqali filtrlash; sahifalash sahifada ko'rinadi.

**FR-24: REST API (DRF) va OpenAPI hujjati**
THE SYSTEM SHALL kafelar, stollar, bronlar va sharhlar uchun DRF asosidagi REST API'ni token yoki session autentifikatsiya bilan taqdim etsin va `drf-spectacular` orqali Swagger/OpenAPI hujjatini chop etsin.
*Qabul mezonlari:*
- `/api/schema/`, `/api/docs/` (Swagger UI) ishlaydi.
- API endpointlari rol ruxsatlarini hurmat qiladi.

**FR-25: Sog'liq tekshiruvi (health check)**
WHEN `/health/` endpointiga so'rov kelsa, THE SYSTEM SHALL ilova holatini va ma'lumotlar bazasi ulanishini tekshirib, JSON formatida natija qaytarsin.
*Qabul mezonlari:* DB ulanmagan bo'lsa HTTP 503, aks holda 200 va `{"status": "ok", "database": "ok"}`.

**FR-26: Audit log**
WHEN muhim obyektlar (bron, kafe, foydalanuvchi, zona, stol) yaratilsa, o'zgartirilsa yoki o'chirilsa, THE SYSTEM SHALL kim, nimani va qachon bajargani haqida audit yozuvini saqlasin.
*Qabul mezonlari:* Audit yozuvi aktyor, amal turi, obyekt va vaqt tamg'asini o'z ichiga oladi; admin paneldan ko'rinadi.

**FR-27: Bildirishnomalar**
WHEN bron holati o'zgarsa (yaratilish, tasdiqlash, rad etish, bekor qilish), THE SYSTEM SHALL tegishli foydalanuvchiga email bildirishnoma yuborsin (dev rejimda konsol backend orqali).
*Qabul mezonlari:* Dev muhitda xabar konsolga chiqadi; prod muhitda SMTP orqali yuboriladi.

**FR-28: Demo ma'lumotlar generatsiyasi**
WHEN `seed_demo_data` management komandasi ishga tushirilsa, THE SYSTEM SHALL 1 admin, 2 menejer, 5 mijoz, 3 kafe, 30+ stol, 40+ turli holatdagi bron va bir nechta sharh yaratsin.
*Qabul mezonlari:* Komanda idempotent ishlaydi (qayta ishga tushirishda dublikat yaratmaydi yoki tozalab qayta yaratadi).

**FR-29: Chiroyli xato sahifalari**
IF 403, 404 yoki 500 xatosi yuz bersa, THEN THE SYSTEM SHALL mavzuga mos, chiroyli dizaynli xato sahifasini ko'rsatsin.
*Qabul mezonlari:* Har bir xato uchun maxsus shablon mavjud va `DEBUG=False` da ishlaydi.

**FR-30: Mavzu rejimi (qorong'i/yorug')**
WHEN foydalanuvchi mavzu toggle'ini bossa, THE SYSTEM SHALL qorong'i va yorug' rejim o'rtasida almashsin va tanlovni `localStorage` da saqlasin.
*Qabul mezonlari:* Tanlov sahifa qayta yuklanganda saqlanib qoladi.

---

## 5. Nofunksional talablar (NFR)

**NFR-01: Xavfsizlik (web)**
THE SYSTEM SHALL CSRF himoyasi, XSS himoyasi (shablon auto-escaping), parol xeshlash va rol cheklovlarini ta'minlasin.
*Qabul mezonlari:* Barcha POST formalar CSRF token bilan; shablonlarda auto-escaping yoqilgan.

**NFR-02: Xavfsizlik (prod sozlamalari)**
WHERE muhit production bo'lsa, THE SYSTEM SHALL `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` va `CSRF_TRUSTED_ORIGINS` sozlamalarini qo'llasin.
*Qabul mezonlari:* Sirlar `.env` dan o'qiladi; kodga sir yozilmaydi; `.env.example` mavjud.

**NFR-03: Ishlash tezligi (performance)**
THE SYSTEM SHALL ma'lumotlar bazasi so'rovlarini `select_related`/`prefetch_related` va kerakli indekslar bilan optimallashtirsin.
*Qabul mezonlari:* Ro'yxat sahifalarida N+1 so'rov muammosi bo'lmaydi; tez-tez filtrlanadigan maydonlarda indeks mavjud.

**NFR-04: Responsivlik va accessibility**
THE SYSTEM SHALL interfeysni mobil, planshet va desktop ekranlarida to'g'ri ko'rsatsin hamda semantik HTML, alt matnlar, yetarli kontrast va klaviatura bilan boshqarishni ta'minlasin.
*Qabul mezonlari:* Bootstrap 5 grid; asosiy oqimlar klaviatura orqali bajariladi.

**NFR-05: Test qamrovi**
THE SYSTEM SHALL kamida 80% test qamrovini ta'minlasin va kamida 40 ta test bo'lsin.
*Qabul mezonlari:* `pytest --cov` qamrov < 80% bo'lsa CI fail bo'ladi.

**NFR-06: Konteynerlashtirish**
THE SYSTEM SHALL multi-stage `Dockerfile` (python:3.12-slim, non-root foydalanuvchi, `HEALTHCHECK`) va `docker-compose` konfiguratsiyasi bilan konteynerlashtirilsin.
*Qabul mezonlari:* `docker compose up --build` ilovani ishga tushiradi.

**NFR-07: Takrorlanuvchan deploy (CI/CD)**
THE SYSTEM SHALL GitHub Actions orqali lint, test, security scan, build va deploy bosqichlarini avtomatlashtirsin.
*Qabul mezonlari:* `ci.yml`, `security.yml`, `docker.yml`, `cd.yml`, `release.yml` workflow'lari mavjud va yashil.

**NFR-08: Kuzatuvchanlik (observability/logging)**
THE SYSTEM SHALL konsol va fayl handlerlari bilan tuzilgan logging konfiguratsiyasiga ega bo'lsin.
*Qabul mezonlari:* Xatolar va muhim hodisalar loglanadi; log darajasi muhit bo'yicha sozlanadi.

**NFR-09: Mahsulot sifati (code quality)**
THE SYSTEM SHALL PEP 8, type hints, docstring'lar va DRY tamoyillariga rioya qilsin; `ruff` va `mypy` tekshiruvlaridan o'tsin.
*Qabul mezonlari:* `ruff check`, `ruff format --check` va `mypy` CI'da xatosiz o'tadi.

**NFR-10: Python moslik va bog'liqliklar**
THE SYSTEM SHALL Python 3.11 va 3.12 bilan mos bo'lsin va bog'liqliklar `requirements/{base,dev,prod}.txt` da qat'iy versiyalar bilan belgilansin.
*Qabul mezonlari:* CI matritsasi (3.11, 3.12) yashil; versiyalar pin qilingan.

**NFR-11: Ma'lumotlar bazasi moslashuvchanligi**
THE SYSTEM SHALL production'da PostgreSQL va lokal rivojlantirishda SQLite fallback'ini qo'llab-quvvatlasin.
*Qabul mezonlari:* DB ulanishi muhit o'zgaruvchisi orqali almashadi; `ExclusionConstraint` faqat PostgreSQL'da yoqiladi.

**NFR-12: Hujjatlashtirish**
THE SYSTEM SHALL o'zbek tilida to'liq hujjatlarni (README, architecture, cicd, deployment, himoya, hisobot) va UML diagrammalarni taqdim etsin.
*Qabul mezonlari:* `docs/` papkasida barcha hujjatlar mavjud; diagrammalar `scripts/render_diagrams.py` orqali render bo'ladi.

---

## 6. Qabul mezonlari matritsasi (umumiy)

| Talab guruhi | Tekshirish usuli |
|--------------|------------------|
| Autentifikatsiya (FR-01…FR-07) | View va API testlari, rol ruxsat testlari |
| CRUD (FR-08…FR-10) | Model va view testlari |
| Qidiruv/bron (FR-11…FR-15) | Servis testlari (to'qnashuv, vaqt, sig'im edge-case'lari) |
| Holatlar (FR-16…FR-21) | Servis va view testlari |
| Dashboard/API/health (FR-22…FR-30) | API testlari, `/health/` testi, UI tekshiruvi |
| NFR-01…NFR-12 | Lint, mypy, coverage, Docker build, CI pipeline |

---

## 7. Qamrovdan tashqari (Out of scope)

- Real to'lov tizimi integratsiyasi (faqat bron, to'lov emas).
- Mobil ilova (faqat responsiv veb).
- Ko'p tilli (i18n) to'liq qo'llab-quvvatlash (interfeys faqat o'zbek tilida).
- SMS bildirishnomalar (faqat email).

---

## 8. Keyingi bosqich

Ushbu `requirements.md` tasdiqlangandan so'ng, `design.md` (arxitektura, ma'lumotlar
modeli, diagrammalar, komponentlar) tayyorlanadi.
