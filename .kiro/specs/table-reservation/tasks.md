# TableReserve: Vazifalar hujjati (Tasks)

> Kafe stol rezervatsiyasi platformasi
> Fan: DevOps va CI/CD texnologiyalari (Amaliy mashg'ulot)
> Muallif: Sadullayev Jaxongir
> Spec-driven jarayonning 3-bosqichi (`requirements.md` -> `design.md` -> **`tasks.md`**)
> Til: interfeys va hujjatlar o'zbek (lotin); kod identifikatorlari, fayl yo'llari va commit xabarlari ingliz tilida.

---

## Hujjatning maqsadi

Ushbu hujjat tasdiqlangan [`requirements.md`](./requirements.md) (funksional `FR-01..FR-30`
va nofunksional `NFR-01..NFR-12`) va [`design.md`](./design.md) hujjatlariga asoslangan
**amalga oshirish rejasi**dir. U butun loyihani (muhit, Django ilovalari, servislar,
template/UI, REST API, testlar, UML diagrammalar, Docker, GitHub Actions, steering,
hooks, hujjatlar va GitHub'ga yuklash) raqamlangan, ketma-ket va tekshiriladigan
vazifalarga ajratadi. Har bir vazifa `- [ ]` checkbox ko'rinishida bo'lib, bajarilgani
belgilab boriladi. Har bir vazifa qaysi talab (FR/NFR) va/yoki dizayn bo'limini (§)
qondirishi bilan izohlangan hamda qanday tekshirilishi ko'rsatilgan.

**Muhim izoh (approval gate):** Bu hujjat spec-driven jarayonning 3-bosqichi va faqat
REJA. Men (muallif/foydalanuvchi) ushbu `tasks.md` ni tasdiqlaganimdan keyingina
vazifalar birma-bir bajarilishi boshlanadi. Tasdiqdan oldin hech qanday kod yozilmaydi.

**GitHub yuklash izohi:** Bu rejadagi push, pull request, release/tag va repo
sozlamalariga oid qadamlar reja sifatida sanab o'tilgan. Tayyorlovchi (coder)
kontent va lokal commitlarni tayyorlaydi; haqiqiy `git push`, PR ochish va release/tag
yaratishni orkestrator (orchestrator) bajaradi.

**Ketma-ketlik tamoyili (dependency ordering):** muhit va qat'iy bog'liqliklar ->
sozlamalar va `core` ilovasi -> domen ilovalari (modellar -> servislar ->
view/template/API) -> backendni qoplovchi testlar -> frontend -> Docker -> Docker'ni
build qiladigan CI/CD -> hujjatlar -> GitHub release. Har bir faza o'zidan oldingi
fazaga tayanadi.

---

## Faza 1. Muhit, bog'liqliklar va Django skeleti

- [x] **1.1. Katalog skeletini yaratish.** `design.md` §9 dagi tuzilmaga mos ravishda
  `config/`, `apps/`, `templates/`, `static/`, `docs/`, `docs/diagrams/`,
  `requirements/`, `scripts/`, `tests/`, `.github/workflows/` papkalarini va har bir
  `apps/<app>` ichidagi `__init__.py` ni yaratish.
  *Tekshirish:* `find` bilan barcha papkalar mavjudligi; har bir Python paketi
  `__init__.py` ga ega. (`design.md` §7, §9)
- [x] **1.2. Pinned bog'liqliklar fayllari.** `requirements/base.txt` (Django 5.x,
  djangorestframework, drf-spectacular, django-filter, psycopg2-binary, Pillow,
  python-dotenv/django-environ, gunicorn, whitenoise), `requirements/dev.txt`
  (`-r base.txt` + pytest, pytest-django, pytest-cov, factory_boy, ruff, mypy,
  django-stubs, pre-commit), `requirements/prod.txt` (`-r base.txt` + prod-only).
  Barcha versiyalar qat'iy pin (`==`) qilinadi.
  *Tekshirish:* har bir qator `paket==versiya` ko'rinishida; `pip install -r
  requirements/dev.txt` xatosiz. (`NFR-10`, `NFR-11`, `design.md` §9)
- [x] **1.3. `pyproject.toml` konfiguratsiyasi.** `ruff` (lint + format qoidalari,
  target 3.11), `mypy` (django-stubs plugin, strict-ish), `pytest`
  (`DJANGO_SETTINGS_MODULE=config.settings.test`, `--cov`, testpaths), va
  `coverage` (`fail_under = 80`) bo'limlarini yozish.
  *Tekshirish:* `ruff check`, `mypy` va `pytest` konfiguratsiyani o'qiydi; xato bermaydi.
  (`NFR-05`, `NFR-09`, `NFR-10`)
- [x] **1.4. `.env.example` yaratish.** `SECRET_KEY`, `DJANGO_SETTINGS_MODULE`,
  `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL`/`POSTGRES_*`, `EMAIL_*`,
  `DJANGO_LOG_LEVEL`, `CSRF_TRUSTED_ORIGINS` namunaviy (sirlar yo'q) o'zgaruvchilar
  bilan. Haqiqiy `.env` `.gitignore` ga qo'shiladi.
  *Tekshirish:* fayl mavjud, sir qiymat yo'q; `.gitignore` `.env` ni istisno qiladi.
  (`NFR-02`)
- [x] **1.5. `manage.py` va `config/` paketi.** `manage.py` (default
  `config.settings.dev`), `config/__init__.py`, `config/wsgi.py`, `config/asgi.py`
  yaratish.
  *Tekshirish:* `python manage.py --help` ishlaydi. (`design.md` §9)

## Faza 2. Sozlamalar (settings split), URL va logging

- [x] **2.1. `config/settings/base.py`.** Umumiy sozlamalar: `INSTALLED_APPS`
  (barcha `apps.*`, DRF, drf-spectacular, django-filter), `AUTH_USER_MODEL =
  "accounts.User"`, `.env` dan sir o'qish, `TEMPLATES`, `STATIC`/`MEDIA`,
  `REST_FRAMEWORK` (Token + Session auth, drf-spectacular schema class),
  `SPECTACULAR_SETTINGS`, til/time zone.
  *Tekshirish:* `python manage.py check` xatosiz. (`FR-06`, `FR-24`, `NFR-11`,
  `design.md` §2.2, §8.1)
- [x] **2.2. `config/settings/dev.py`.** `DEBUG=True`, SQLite baza, console email
  backend, `DJANGO_LOG_LEVEL=DEBUG`.
  *Tekshirish:* `DJANGO_SETTINGS_MODULE=config.settings.dev python manage.py check`
  xatosiz. (`FR-27`, `NFR-11`)
- [x] **2.3. `config/settings/prod.py`.** PostgreSQL baza, SMTP email, xavfsizlik
  sarlavhalari: `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`,
  `SECURE_HSTS_*`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`,
  `CSRF_TRUSTED_ORIGINS`; whitenoise static.
  *Tekshirish:* `python manage.py check --deploy` ogohlantirishsiz o'tadi. (`NFR-02`,
  `NFR-11`, `design.md` §9)
- [x] **2.4. `config/settings/test.py`.** Tez test sozlamalari (in-memory yoki tezroq
  hasher, SQLite, email `locmem`).
  *Tekshirish:* `pytest` shu sozlama bilan yuklanadi. (`NFR-05`)
- [x] **2.5. `config/urls.py` root URLConf.** `/admin/`, `/health/`, `/api/`
  (api ilovasi), web ilova URL'lari; `handler403/404/500` ni ro'yxatdan o'tkazish.
  *Tekshirish:* `python manage.py show_urls` yoki `check` orqali URL'lar yuklanadi.
  (`FR-25`, `FR-29`, `design.md` §10.1)
- [x] **2.6. LOGGING konfiguratsiyasi.** `base.py` da `console` handler (barcha
  muhit) va aylanuvchi `file` handler (`logs/app.log`); daraja
  `DJANGO_LOG_LEVEL` orqali.
  *Tekshirish:* ishga tushganda log konfiguratsiya xatosi yo'q; test ichida log
  yozilishi tasdiqlanadi. (`NFR-08`, `design.md` §10.2)

## Faza 3. `core` ilovasi (abstrakt model, audit, istisnolar, health, xato sahifalar)

- [x] **3.1. `core/models.py`.** `TimeStampedModel` (abstrakt, `created_at`
  `auto_now_add` + `db_index`, `updated_at` `auto_now`) va `AuditLog` modeli
  (`actor`, `action`, `object_type`, `object_id`, `changes` JSON, `created_at`) +
  `AuditAction` TextChoices (`CREATE/UPDATE/DELETE`).
  *Tekshirish:* `makemigrations core` migratsiya yaratadi; `migrate` o'tadi.
  (`FR-26`, `design.md` §3.2, §3.8)
- [x] **3.2. `core/exceptions.py`.** Domen istisnolari: `ValidationError`,
  `ConflictError`, `InvalidTransitionError`, `PermissionError` (o'zbekcha xabarlar bilan).
  *Tekshirish:* import va `raise` unit-testda ishlaydi. (`FR-13`, `FR-16`, `FR-29`,
  `design.md` §10.1)
- [x] **3.3. `core/mixins.py`.** Umumiy view mixinlari (rolга asoslangan kirishni
  tekshiruvchi `LoginRequired`/role mixinlar, audit yordamchi mixin).
  *Tekshirish:* mixin importlanadi va view testida qo'llanadi. (`FR-06`, `FR-07`,
  `design.md` §7)
- [x] **3.4. `core/services.py`.** `record_audit(actor, action, instance, changes)`,
  `send_notification(user, template, context)`, `check_database()`.
  *Tekshirish:* `record_audit` `AuditLog` yozuvi yaratadi; `send_notification`
  `locmem` backendga xabar yozadi; `check_database` SELECT 1 bajaradi (unit-test).
  (`FR-25`, `FR-26`, `FR-27`, `design.md` §4)
- [x] **3.5. `core/views.py` health-check.** `GET /health/` -> `health_check`:
  DB `SELECT 1`; muvaffaqiyat 200 `{"status":"ok","database":"ok"}`, nosozlikda 503
  `{"status":"error","database":"down"}`.
  *Tekshirish:* test `/health/` 200 qaytarishini va JSON tanani tekshiradi. (`FR-25`,
  `design.md` §10.3)
- [x] **3.6. Xato handlerlari va shablonlari.** `handler403/404/500` funksiyalari
  va `templates/errors/403.html`, `404.html`, `500.html` (mavzuga mos dizayn).
  *Tekshirish:* `DEBUG=False` da noto'g'ri URL 404 shablonini ko'rsatadi (test).
  (`FR-29`, `design.md` §10.1)

## Faza 4. `accounts` ilovasi (User, auth, RBAC)

- [x] **4.1. `accounts/models.py` va `managers.py`.** `User(AbstractUser)` +
  `role`, `phone`; `email` `USERNAME_FIELD` (unique); `Role` TextChoices
  (`ADMIN/MANAGER/CUSTOMER/WAITER`); `UserManager` (`create_user`/`create_superuser`
  email asosida); `is_admin/is_manager/is_customer/is_waiter` xususiyatlari;
  `role` indeksi.
  *Tekshirish:* `makemigrations`/`migrate`; test email bilan user yaratadi. (`FR-01`,
  `FR-06`, `design.md` §3.3)
- [x] **4.2. `accounts/services.py`.** `register_customer(data)`,
  `change_password(user, old, new)`, `issue_password_reset(email)`,
  `confirm_password_reset(token, new)`.
  *Tekshirish:* unit-testlar ro'yxat, parol o'zgartirish va tiklash oqimini qoplaydi;
  mavjud bo'lmagan email mavjudlikni oshkor qilmaydi. (`FR-01`, `FR-04`, `FR-05`,
  `design.md` §4)
- [x] **4.3. `accounts/forms.py`.** Registratsiya, login, parol o'zgartirish/tiklash,
  profil formalari (Django parol validatorlari bilan).
  *Tekshirish:* form validatsiyasi testda ishlaydi. (`FR-01`, `FR-04`, `NFR-01`)
- [x] **4.4. `accounts/views.py` va `urls.py`.** Login, logout, register, profil
  view'lari va rolга mos yo'naltirish.
  *Tekshirish:* view testlari login/logout/register/profil oqimini qoplaydi.
  (`FR-02`, `FR-03`, `design.md` §7)
- [x] **4.5. `accounts/permissions.py` (DRF).** `IsAdmin`, `IsManager`,
  `IsManagerOfCafe`, `IsCustomer`, `IsOwnerOrReadOnly`.
  *Tekshirish:* permission testlari har rol uchun ruxsat/rad holatini qoplaydi.
  (`FR-06`, `FR-07`, `design.md` §8.1)
- [x] **4.6. `accounts/serializers.py` va admin ro'yxatga olish.** User serializer;
  `admin.py` da `User` va `AuditLog` (read-only) ro'yxatga olinadi.
  *Tekshirish:* admin paneldan `AuditLog` read-only ko'rinadi (test/manual).
  (`FR-24`, `FR-26`)

## Faza 5. `cafes` ilovasi (Cafe, Zone)

- [x] **5.1. `cafes/models.py`.** `Cafe` (manager FK `PROTECT`, `slug` unique,
  `opening_time`/`closing_time`, `image`, `is_active`) va `Zone` (cafe FK CASCADE,
  `zone_type`); `ZoneType` TextChoices; `UniqueConstraint(cafe,name)`; indekslar
  (`slug`, `is_active`, `name`).
  *Tekshirish:* `makemigrations`/`migrate`; cheklov testi dublikat zonani rad etadi.
  (`FR-08`, `FR-09`, `design.md` §3.4)
- [x] **5.2. `cafes/services.py`.** `create_cafe`, `update_cafe`, `manage_zone`,
  `cafe_average_rating(cafe)` (annotation orqali).
  *Tekshirish:* servis testlari CRUD va o'rtacha reytingni tekshiradi. (`FR-08`,
  `FR-09`, `FR-21`, `design.md` §4)
- [x] **5.3. `cafes/forms.py`, `views.py`, `urls.py`.** Kafe/zona CRUD view'lari
  (ruxsat: ADMIN yoki tegishli MANAGER).
  *Tekshirish:* view testlari CRUD va ruxsatni qoplaydi. (`FR-08`, `FR-09`, `FR-07`)
- [x] **5.4. `cafes/serializers.py` va `filters.py`.** DRF serializerlar va
  `django-filter` filtrlari (nom/manzil bo'yicha qidiruv, saralash).
  *Tekshirish:* API ro'yxat filtr/qidiruvni qaytaradi (test). (`FR-23`, `FR-24`,
  `NFR-03`)

## Faza 6. `tables` ilovasi (Table)

- [x] **6.1. `tables/models.py`.** `Table` (zone FK CASCADE, `number`, `capacity`,
  `status`); `TableStatus` TextChoices (`AVAILABLE/INACTIVE`);
  `CheckConstraint(capacity>=1)`, `UniqueConstraint(zone,number)`; `(zone,status)`
  indeksi; `cafe` xususiyati.
  *Tekshirish:* `makemigrations`/`migrate`; `capacity=0` va dublikat raqam cheklov
  xatosi beradi (test). (`FR-10`, `design.md` §3.5)
- [x] **6.2. `tables/services.py`.** `create_table`,
  `ensure_unique_number(cafe, number)` (kafe doirasida takrorlanmaslik).
  *Tekshirish:* servis testi kafe bo'yicha takroriy raqamni rad etadi. (`FR-10`,
  `design.md` §4)
- [x] **6.3. `tables/forms.py`, `views.py`, `serializers.py`, `urls.py`.** Stol CRUD
  view va API (ruxsat: tegishli MANAGER/ADMIN).
  *Tekshirish:* view va API testlari CRUD va ruxsatni qoplaydi. (`FR-10`, `FR-07`,
  `FR-24`)

## Faza 7. `reservations` ilovasi (qidiruv, bron wizardi, to'qnashuv, holat mashinasi)

- [x] **7.1. `reservations/models.py` va `managers.py`.** `Reservation` (customer FK
  `PROTECT`, table FK `PROTECT`, `start_time` indeksli, `duration_minutes`,
  `guests_count`, `status`, `note`, `time_range` DateTimeRangeField);
  `ReservationStatus` TextChoices (6 holat); `end_time` xususiyati;
  CheckConstraintlar (`guests>=1`, `duration>=30`); indekslar
  (`(table,start_time)`, `status`, `(customer,status)`); `ReservationQuerySet`
  (`active`, `for_customer`, `for_cafe`, `on_date`) + `select_related`.
  *Tekshirish:* `makemigrations`/`migrate`; QuerySet metodlari testda ishlaydi;
  cheklov testlari o'tadi. (`FR-12`, `FR-15`, `FR-16`, `FR-19`, `FR-20`, `NFR-03`,
  `design.md` §3.6)
- [x] **7.2. Shartli ExclusionConstraint migratsiyasi.** `btree_gist` kengaytmasi va
  `ExclusionConstraint` (bir xil `table`, faol status uchun `time_range` kesishmasin)
  ni **faqat** `connection.vendor == "postgresql"` bo'lganda qo'llaydigan
  shartli migratsiya operatsiyasi; SQLite'da e'tiborsiz qoldiriladi.
  *Tekshirish:* `makemigrations --check` toza; SQLite'da `migrate` o'tadi, Postgres
  muhitida cheklov yaratiladi (test). (`FR-13`, `NFR-11`, `design.md` §5.1)
- [x] **7.3. `reservations/services.py` qidiruv va yaratish.**
  `search_available_tables(criteria)` (sana/vaqt/davomiylik/guests/zona bo'yicha,
  `select_related`/`prefetch_related` bilan) va `create_reservation(customer, data)`
  (`transaction.atomic` + `select_for_update`; ish vaqti/o'tmish `FR-14`, sig'im
  `FR-15`, overlap `s1<e2 AND s2<e1` tekshiruvi; to'qnashuvda `ConflictError`).
  *Tekshirish:* servis testlari off-hours, o'tmish, sig'imdan oshish va to'qnashuv
  edge-case'larini qoplaydi. (`FR-11`, `FR-12`, `FR-13`, `FR-14`, `FR-15`,
  `design.md` §5.2, §5.3)
- [x] **7.4. `reservations/services.py` holat mashinasi.**
  `transition(reservation, target, actor)` (qonuniy o'tishlar jadvali, noqonuniyda
  `InvalidTransitionError`), hamda `confirm`, `reject`, `cancel` (2 soat qoidasi
  `FR-18`), `complete`, `mark_no_show`; har o'tishda `record_audit` +
  `send_notification`.
  *Tekshirish:* servis testlari qonuniy/noqonuniy o'tishlar, 2 soat qoidasi va
  kafe egaligini qoplaydi. (`FR-16`, `FR-17`, `FR-18`, `FR-27`, `design.md` §6)
- [x] **7.5. `reservations/forms.py`, `views.py`, `urls.py` (3 qadamli wizard).**
  Vaqt -> stol -> tasdiqlash wizardi; "Mening bronlarim" (filtr/pagination `FR-19`);
  menejer kunlik jadvali va stol bandligi (`FR-20`); action view'lari
  (confirm/reject/cancel/complete/no-show).
  *Tekshirish:* view testlari wizard oqimi, mening bronlarim va manager jadvalini
  qoplaydi. (`FR-12`, `FR-19`, `FR-20`, `design.md` §7)
- [x] **7.6. `reservations/serializers.py`, `filters.py`, action endpointlari.** DRF
  reservation serializer, filtrlar va
  `/reservations/{id}/{confirm,reject,cancel,complete,no-show}/` action'lari (rolга
  qarab ruxsat).
  *Tekshirish:* API testlari yaratish, ro'yxat, filtr va action'larni rol
  ruxsatlari bilan qoplaydi. (`FR-12`, `FR-17`, `FR-18`, `FR-23`, `FR-24`)

## Faza 8. `reviews` ilovasi (Review)

- [x] **8.1. `reviews/models.py`.** `Review` (reservation OneToOne CASCADE, cafe FK,
  author FK, `rating`, `comment`); `CheckConstraint(1<=rating<=5)`; `(cafe,rating)`
  indeksi.
  *Tekshirish:* `makemigrations`/`migrate`; `rating=0`/`6` cheklov xatosi (test).
  (`FR-21`, `design.md` §3.7)
- [x] **8.2. `reviews/services.py`.** `create_review(customer, reservation, rating,
  comment)`: faqat `reservation.status == COMPLETED` va `author == reservation.customer`,
  va bir marta.
  *Tekshirish:* servis testi COMPLETED bo'lmagan bron, boshqa muallif va takroriy
  sharhni rad etadi. (`FR-21`, `design.md` §6.3)
- [x] **8.3. `reviews/forms.py`, `views.py`, `serializers.py`, `urls.py`.** Sharh
  qoldirish view va API (POST uchun `IsCustomer` + COMPLETED).
  *Tekshirish:* view/API testlari sharh qoidasini qoplaydi. (`FR-21`, `FR-24`)

## Faza 9. `dashboard` ilovasi (statistika, grafiklar)

- [x] **9.1. `dashboard/services.py`.** `admin_stats(date_range)`,
  `manager_daily_schedule(cafe, date)`, `cancellation_rate`, `busiest_tables`
  (real ma'lumotlardan hisoblanadi).
  *Tekshirish:* servis testlari sanalar oralig'i bo'yicha to'g'ri agregatsiyani
  tekshiradi. (`FR-20`, `FR-22`, `design.md` §4)
- [x] **9.2. `dashboard/views.py`, `urls.py`, `templatetags/`.** Admin/menejer
  dashboard view'lari; sana filtri; Chart.js uchun kontekst; statistik kartalar.
  *Tekshirish:* view testi ADMIN uchun statistika sahifasini va sana filtrini
  qoplaydi; ruxsatsiz rol 403 oladi. (`FR-22`, `FR-07`)

## Faza 10. `api` ilovasi (DRF yig'indisi, OpenAPI)

- [x] **10.1. `api/routers.py` va `api/urls.py`.** Barcha domen ViewSet'larini
  `/api/v1/` ostida yig'ish (cafes, zones, tables, availability, reservations +
  action'lar, reviews) `design.md` §8.2 jadvaliga mos.
  *Tekshirish:* `GET /api/v1/` router root ishlaydi; endpointlar testda mavjud.
  (`FR-24`, `design.md` §8.2)
- [x] **10.2. `api/schema.py` va OpenAPI.** `drf-spectacular` orqali
  `/api/schema/` va `/api/docs/` (Swagger UI); Token + Session auth; `@extend_schema`
  bilan o'zbekcha tavsiflar.
  *Tekshirish:* `/api/schema/` va `/api/docs/` 200 qaytaradi (test); schema
  generatsiyasi xatosiz. (`FR-24`, `design.md` §8.3)

## Faza 11. Frontend va UI dizayni

- [x] **11.1. `templates/base.html` va static tashkiloti.** `base.html` (semantik
  HTML, meta, blok tuzilmasi, CSRF); `static/css/`, `static/js/`, `static/img/`
  papkalari; Inter/Poppins shriftlar va Bootstrap Icons ulanishi; Bootstrap 5
  responsive grid.
  *Tekshirish:* sahifa render bo'ladi; mobil/planshet/desktop'da grid ishlaydi
  (manual + responsive tekshiruv). (`NFR-04`, `design.md` §2.2)
- [x] **11.2. CSS mavzu o'zgaruvchilari va dizayn tili.** Iliq "cafe" palitrasi
  CSS o'zgaruvchilari (yorug'/qorong'i), kartalar, tugmalar, toast, bo'sh-holat
  (empty-state) va yuklash indikatorlari uslublari.
  *Tekshirish:* yorug'/qorong'i palitra elementlarda qo'llanadi (manual). (`NFR-04`,
  `FR-30`)
- [x] **11.3. Qorong'i/yorug' mavzu toggle (JS).** `static/js/theme.js`: toggle
  tanlovini `localStorage` da saqlash va qayta yuklaganda tiklash.
  *Tekshirish:* toggle bosilganda mavzu almashadi va reload'dan keyin saqlanadi
  (manual/JS test). (`FR-30`)
- [x] **11.4. Bosh sahifa (hero + qidiruv).** Hero bo'limi va bo'sh stol qidiruv
  formasi (sana/vaqt/davomiylik/guests/zona).
  *Tekshirish:* qidiruv formasi natija sahifasiga yuboradi (view testi + manual).
  (`FR-11`, `NFR-04`)
- [x] **11.5. Interaktiv zal/stol sxemasi.** Vanilla JS + SVG/CSS orqali vizual
  stol xaritasi (bo'sh/band holatlar rangda); stolni tanlash wizardga uzatadi.
  *Tekshirish:* xarita stollar holatini aks ettiradi va tanlash ishlaydi (manual).
  (`FR-11`, `FR-12`, `design.md` §5.3)
- [x] **11.6. 3 qadamli bron wizardi UI.** Vaqt -> stol -> tasdiqlash qadamlari;
  qadamlar orasida holat saqlanishi; validatsiya xatolarining o'zbekcha ko'rinishi.
  *Tekshirish:* wizard uchdan-uch qadamni yakunlab bron yaratadi (view testi +
  manual). (`FR-12`, `FR-13`, `FR-14`, `FR-15`)
- [x] **11.7. Chart.js dashboard UI.** Dashboard sahifasida statistik kartalar va
  Chart.js grafiklari (sana filtri bilan).
  *Tekshirish:* grafiklar real ma'lumot bilan render bo'ladi (manual). (`FR-22`)
- [x] **11.8. Xato sahifalari UI.** `templates/errors/403.html`, `404.html`,
  `500.html` ni mavzuga mos qilib bezash (Faza 3.6 shablonlari ustida).
  *Tekshirish:* `DEBUG=False` da chiroyli xato sahifalari ko'rinadi (manual).
  (`FR-29`)

## Faza 12. Demo ma'lumotlar generatsiyasi

- [x] **12.1. `seed_demo_data` management komandasi.**
  `apps/core/management/commands/seed_demo_data.py`: idempotent; 1 admin, 2 menejer,
  5 mijoz, 3 kafe, 30+ stol, 40+ turli holatdagi bron va bir nechta sharh yaratadi.
  *Tekshirish:* komandani ikki marta ishga tushirish dublikat yaratmaydi; yaratilgan
  obyektlar soni talabga mos (test/manual). (`FR-28`)

## Faza 13. Testlar (pytest, >=40 test, qamrov >=80%)

- [x] **13.1. Test infratuzilmasi va factory_boy.** `conftest.py`, umumiy fixture'lar
  va har model uchun `factory_boy` fabrikalari (User/Cafe/Zone/Table/Reservation/Review).
  *Tekshirish:* `pytest` fabrikalarni yuklaydi; namuna test o'tadi. (`NFR-05`)
- [x] **13.2. Model va servis testlari.** core/accounts/cafes/tables/reservations/
  reviews/dashboard modellari va servislari; jumladan bron edge-case'lari: off-hours,
  o'tmish vaqt, sig'imdan oshish, parallel double-booking, 2 soat bekor qilish
  qoidasi, noqonuniy holat o'tishi.
  *Tekshirish:* ushbu edge-case testlari mavjud va o'tadi. (`FR-13`, `FR-14`, `FR-15`,
  `FR-16`, `FR-18`, `FR-21`, `NFR-05`)
- [x] **13.3. View, API, permission va health testlari.** Auth/login/register,
  CRUD view'lari, DRF endpointlari, rol ruxsatlari (ruxsatsiz kirish 403) va
  `/health/` 200/503.
  *Tekshirish:* view/API/permission/health testlari o'tadi. (`FR-02`, `FR-07`,
  `FR-24`, `FR-25`, `NFR-05`)
- [x] **13.4. Qamrov darvozasi.** Umumiy test soni >=40 va `pytest --cov` qamrovi
  >=80% (aks holda fail).
  *Tekshirish:* `pytest --cov` o'tadi; qamrov >=80%; test soni >=40. (`NFR-05`)

## Faza 14. UML diagrammalar va render skripti

- [x] **14.1. Diagramma manba fayllari (`docs/diagrams/`).** `design.md` §11 dagi
  o'nta diagrammaning manbalari: `usecase.puml`, `activity-reservation.puml`,
  `activity-approval.puml`, `activity-cancellation.puml`, `class.puml`,
  `sequence-reservation.puml`, `er.mmd`, `deployment.puml`, `component.puml`,
  `cicd-pipeline.puml`.
  *Tekshirish:* o'nta manba fayl mavjud va sintaktik to'g'ri. (`NFR-12`,
  `design.md` §11)
- [x] **14.2. `scripts/render_diagrams.py`.** Kroki API orqali `.puml`/`.mmd`
  manbalarni PNG/SVG ga render qiladi; tarmoq yo'q bo'lsa graceful degrade qilib
  manbalarni qoldiradi (xato bermaydi).
  *Tekshirish:* tarmoq bo'lsa render, bo'lmasa toza chiqib ketadi; skript xatosiz
  ishlaydi. (`NFR-12`)
- [x] **14.3. `make diagrams` maqsadi.** Makefile'da `diagrams` target
  (`render_diagrams.py` ni chaqiradi).
  *Tekshirish:* `make diagrams` ishlaydi. (`NFR-12`)

## Faza 15. Docker (konteynerlashtirish)

- [x] **15.1. Multi-stage `Dockerfile`.** `python:3.12-slim`, build/runtime bosqichlari,
  non-root foydalanuvchi, `collectstatic`, `HEALTHCHECK` `/health/` ga murojaat qiladi.
  *Tekshirish:* `docker build` image yaratadi; HEALTHCHECK sog'liqni tekshiradi.
  (`NFR-06`, `FR-25`, `design.md` §10.3)
- [x] **15.2. `entrypoint.sh`.** `migrate`, `collectstatic`, gunicorn ishga tushirish.
  *Tekshirish:* konteyner ishga tushganda migratsiya/server ishlaydi. (`NFR-06`)
- [x] **15.3. `docker-compose.yml` va `docker-compose.dev.yml`.** Prod compose
  (web + db PostgreSQL + nginx) va dev compose (tezroq sozlash); `.dockerignore`.
  *Tekshirish:* `docker compose up --build` ilovani ishga tushiradi va `/health/`
  200 qaytaradi. (`NFR-06`, `NFR-11`)

## Faza 16. GitHub Actions workflow'lari (sakkiztasi)

- [x] **16.1. `.github/workflows/ci.yml`.** Lint (`ruff check` + `ruff format
  --check`) + `mypy`; test matritsasi (3.11, 3.12) `pytest --cov` qamrov darvozasi
  bilan; `python manage.py check` va `makemigrations --check --dry-run`;
  `concurrency`, `permissions`, `timeout-minutes`.
  *Tekshirish:* workflow YAML `yamllint`/`actionlint` toza; mantiq lint+test+check
  bosqichlarini qamraydi. (`NFR-05`, `NFR-07`, `NFR-09`, `NFR-10`)
- [x] **16.2. `.github/workflows/security.yml`.** Dependency/kod xavfsizlik skani
  (masalan pip-audit/bandit/CodeQL); `concurrency`, `permissions`, `timeout-minutes`.
  *Tekshirish:* YAML toza; skan ishga tushadi. (`NFR-07`, `NFR-02`)
- [x] **16.3. `.github/workflows/docker.yml`.** Image build va GHCR'ga push;
  `concurrency`, `permissions` (`packages: write`), `timeout-minutes`.
  *Tekshirish:* YAML toza; build/push bosqichlari to'g'ri. (`NFR-06`, `NFR-07`)
- [x] **16.4. `.github/workflows/cd.yml`.** Deploy va `/health/` smoke-test;
  `concurrency`, `permissions`, `timeout-minutes`.
  *Tekshirish:* YAML toza; deploy + health smoke bosqichlari mavjud. (`FR-25`,
  `NFR-07`)
- [x] **16.5. `.github/workflows/release.yml`.** `v1.0.0` tag/release yaratish
  (changelog ilova qilish); `concurrency`, `permissions` (`contents: write`),
  `timeout-minutes`.
  *Tekshirish:* YAML toza; release bosqichi to'g'ri. (`NFR-07`)
- [x] **16.6. `.github/workflows/docs.yml`.** Hujjat/diagramma build (va kerak bo'lsa
  publish); `concurrency`, `permissions`, `timeout-minutes`.
  *Tekshirish:* YAML toza; docs/diagrams build bosqichi mavjud. (`NFR-12`, `NFR-07`)
- [x] **16.7. `.github/workflows/stale.yml`.** Eski issue/PR'larni belgilash;
  `concurrency`, `permissions` (`issues: write`, `pull-requests: write`),
  `timeout-minutes`.
  *Tekshirish:* YAML toza. (`NFR-07`)
- [x] **16.8. `.github/workflows/labeler.yml`.** O'zgargan yo'llar bo'yicha PR
  avtomatik yorliqlash; `concurrency`, `permissions`, `timeout-minutes`.
  *Tekshirish:* YAML toza; `.github/labeler.yml` config bilan bog'langan. (`NFR-07`)
- [ ] **16.9. README status badge'lari.** README'ga workflow holat (status) badge'larini
  qo'shish.
  *Tekshirish:* README'da badge markdownlari mavjud. (`NFR-07`, `NFR-12`)

## Faza 17. Repo meta fayllari

- [x] **17.1. `.github/dependabot.yml`.** pip va github-actions ekotizimlari uchun
  yangilanish jadvali.
  *Tekshirish:* YAML toza va to'g'ri ekotizimlar. (`NFR-07`, `NFR-10`)
- [x] **17.2. PR va issue shablonlari.** `.github/PULL_REQUEST_TEMPLATE.md` va
  `.github/ISSUE_TEMPLATE/` (bug/feature).
  *Tekshirish:* fayllar mavjud va to'g'ri formatda. (`NFR-07`)
- [x] **17.3. `.github/CODEOWNERS` va `.github/labeler.yml` config.** Kod egalari va
  yorliqlash qoidalari.
  *Tekshirish:* fayllar mavjud; labeler config 16.8 bilan mos. (`NFR-07`)
- [x] **17.4. `.pre-commit-config.yaml`.** ruff (lint + format) va mypy hook'lari.
  *Tekshirish:* `pre-commit run --all-files` lokal ishlaydi. (`NFR-09`)
- [x] **17.5. `Makefile`.** Maqsadlar: `install`, `migrate`, `seed`, `run`, `lint`,
  `format`, `type`, `test`, `diagrams`, `docker-build`, `docker-up`.
  *Tekshirish:* `make lint`, `make test`, `make diagrams` ishlaydi. (`NFR-07`,
  `NFR-09`, `NFR-12`)
- [x] **17.6. `LICENSE` (MIT).** MIT litsenziya fayli.
  *Tekshirish:* fayl mavjud, MIT matni to'liq. (`NFR-12`)

## Faza 18. Steering fayllari

- [x] **18.1. `.kiro/steering/product.md`, `tech.md`, `structure.md`.** Mahsulot
  tavsifi, texnologiya to'plami va katalog tuzilmasi steering hujjatlari (o'zbek lotin).
  *Tekshirish:* uchala fayl mavjud va loyiha haqiqatiga mos. (`NFR-12`, `design.md` §9)

## Faza 19. Kiro hooks

- [x] **19.1. `.kiro/hooks/` (kamida 3 ta).** Masalan: saqlashda test/lint ishga
  tushirish, commit oldidan tekshiruv, migratsiya eslatmasi kabi kamida uchta hook.
  *Tekshirish:* `.kiro/hooks/` ichida kamida 3 ta to'g'ri formatdagi hook fayli mavjud.
  (`NFR-07`, `NFR-09`)

## Faza 20. Hujjatlar (o'zbek, lotin)

- [ ] **20.1. `README.md`.** Loyiha tavsifi, ishga tushirish (lokal + Docker),
  texnologiyalar, status badge'lar (Faza 16.9), API/health havolalari.
  *Tekshirish:* README to'liq va badge'lar bilan. (`NFR-12`, `NFR-06`, `NFR-07`)
- [ ] **20.2. `docs/architecture.md` va `docs/requirements.md`.** Arxitektura
  (qatlamlar, modullar, diagramma havolalari) va talablar xulosasi.
  *Tekshirish:* fayllar `design.md`/`requirements.md` bilan mos. (`NFR-12`)
- [ ] **20.3. `docs/cicd.md` va `docs/deployment.md`.** CI/CD quvuri (8 workflow)
  va deploy (Docker/compose, `/health/` smoke) tavsifi.
  *Tekshirish:* fayllar workflow'lar va Docker bilan mos. (`NFR-07`, `NFR-06`,
  `NFR-12`)
- [ ] **20.4. `docs/HIMOYA.md`, `docs/HISOBOT.md`, `CHANGELOG.md`,
  `docs/screenshots/`.** Himoya (xavfsizlik) hujjati, yakuniy hisobot, o'zgarishlar
  jurnali va skrinshotlar papkasi.
  *Tekshirish:* fayllar/papka mavjud; `CHANGELOG.md` `v1.0.0` ni qamraydi. (`NFR-12`,
  `NFR-02`)

## Faza 21. GitHub'ga yuklash (delivery)

> Izoh: ushbu fazadagi haqiqiy push/PR/release/repo-sozlash qadamlarini **orkestrator**
> bajaradi. Tayyorlovchi (coder) kontent va lokal commitlarni tayyorlaydi.

- [ ] **21.1. Conventional Commits (lokal, >=15 commit).** Fazalar bo'yicha mantiqiy,
  ingliz tilidagi Conventional Commits uslubidagi kamida 15 ta lokal commit tayyorlash
  (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`, `ci:`).
  *Tekshirish:* `git log --oneline` >=15 Conventional Commit ko'rsatadi. (`contribution`)
- [ ] **21.2. Branch strategiyasi (`main`/`develop`/`feature`).** Branch oqimini
  hujjatlashtirish va tayyorlash (push/merge orkestrator tomonidan).
  *Tekshirish:* branch strategiyasi `docs/cicd.md`/README'da hujjatlangan. (`NFR-07`)
- [ ] **21.3. Pull request (shablon bilan).** PR tanasini `PULL_REQUEST_TEMPLATE.md`
  asosida tayyorlash (PR ochishni orkestrator bajaradi).
  *Tekshirish:* PR shabloni to'ldirilgan kontent tayyor. (`NFR-07`)
- [ ] **21.4. CI yashil tekshiruvi.** CI (lint/test/matritsa/qamrov) yashil bo'lishini
  ta'minlaydigan kontent (push va monitoring orkestratorda).
  *Tekshirish:* lokal `make lint && make test` toza. (`NFR-05`, `NFR-07`, `NFR-09`)
- [ ] **21.5. `v1.0.0` release/tag.** Release yozuvi va `CHANGELOG.md` tayyorlash
  (tag/release yaratishni orkestrator bajaradi).
  *Tekshirish:* `CHANGELOG.md` `v1.0.0` bo'limiga ega; release.yml tayyor. (`NFR-07`,
  `NFR-12`)
- [ ] **21.6. Repo About va topics.** Repo tavsifi va mavzular (topics) matnini
  tayyorlash (repo sozlamasini orkestrator qo'llaydi).
  *Tekshirish:* About/topics matni README/docs'da tayyor. (`NFR-12`)

---

## Yakuniy tekshiruv matritsasi

| Faza | Qamrab olingan talablar |
|------|-------------------------|
| 1-2 (muhit, sozlama, URL, log) | `NFR-02`, `NFR-08`, `NFR-10`, `NFR-11`, `FR-06`, `FR-24`, `FR-25`, `FR-29` |
| 3 (core) | `FR-25`, `FR-26`, `FR-27`, `FR-29` |
| 4 (accounts) | `FR-01`..`FR-07` |
| 5-6 (cafes, tables) | `FR-08`, `FR-09`, `FR-10`, `FR-21`, `FR-23` |
| 7 (reservations) | `FR-11`..`FR-20`, `NFR-03`, `NFR-11` |
| 8 (reviews) | `FR-21` |
| 9 (dashboard) | `FR-20`, `FR-22` |
| 10 (api) | `FR-24`, `FR-06`, `FR-07` |
| 11 (frontend) | `FR-29`, `FR-30`, `NFR-04` |
| 12 (seed) | `FR-28` |
| 13 (testlar) | `NFR-05` va barcha FR edge-case'lari |
| 14 (diagrammalar) | `NFR-12` |
| 15 (Docker) | `NFR-06`, `FR-25` |
| 16-17 (CI/CD, meta) | `NFR-07`, `NFR-09`, `NFR-10` |
| 18-19 (steering, hooks) | `NFR-07`, `NFR-09`, `NFR-12` |
| 20 (hujjatlar) | `NFR-12` |
| 21 (delivery) | `NFR-07`, Conventional Commits |

Ushbu `tasks.md` tasdiqlangandan so'ng, vazifalar yuqoridagi ketma-ketlikda birma-bir
bajarilishi boshlanadi.
