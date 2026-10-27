# Himoya materiali (5 daqiqalik taqdimot)

> Loyiha: **TableReserve** - kafe stol rezervatsiyasi platformasi
> Muallif: **Sadullayev Jaxongir** · Fan: DevOps va CI/CD texnologiyalari

## 1. 5 daqiqalik taqdimot rejasi

| Vaqt | Bo'lim | Nima aytiladi |
|------|--------|---------------|
| 0:00–0:30 | Kirish | Muammo: kafe stollarini telefon orqali bron qilish noqulay. Yechim: TableReserve. |
| 0:30–1:30 | Arxitektura | Qatlamli dizayn: templates/DRF -> services -> ORM -> PostgreSQL. 8 ta Django ilova. |
| 1:30–2:30 | Asosiy funksiya | 3 qadamli bron wizardi; double-booking'ning oldini olish (atomic + select_for_update + exclusion constraint); holat mashinasi. |
| 2:30–3:30 | DevOps/CI-CD | Docker multi-stage, 8 ta GitHub Actions workflow'i: lint/test matritsa/qamrov darvozasi, security (bandit/pip-audit/CodeQL), image build + Trivy -> GHCR, cd (approval + health smoke), release. |
| 3:30–4:30 | Sifat | >= 40 test, qamrov >= 80%, ruff + mypy + pre-commit, pinned deps, audit log, health-check. |
| 4:30–5:00 | Yakun | Spec-driven jarayon (requirements -> design -> tasks), UML diagrammalar, hujjatlar. Savollar. |

## 2. Demo ssenariysi (jonli ko'rsatish)

1. **Seed**: `make seed` - demo akkauntlar va ma'lumotlar yaratiladi.
2. **Bosh sahifa**: hero + qidiruv paneli, mashhur kafelar, "qanday ishlaydi", sharhlar.
3. **Mavzu**: yorug'/qorong'i toggle (localStorage'da saqlanadi).
4. **Mijoz oqimi**: `customer1@tablereserve.uz / demo12345` bilan kirish ->
   stol qidirish -> zal sxemasidan stolni tanlash -> tasdiqlash -> "Mening bronlarim".
5. **Edge-case**: o'tmishdagi vaqt / sig'imdan ortiq / band stol -> o'zbekcha xato (toast).
6. **Menejer oqimi**: `manager1@tablereserve.uz` -> kunlik jadval -> bronni tasdiqlash/rad etish.
7. **Admin**: `admin@tablereserve.uz` -> dashboard: statistik kartalar + Chart.js grafigi.
8. **API**: `/api/docs/` (Swagger), `/health/` (200 JSON).
9. **CI/CD**: GitHub Actions'da yashil ci/security/docker runlari; PR'da avtomatik label.

## 3. 25 ta savol-javob (ehtimoliy)

1. **Nega Django?** - Batareya bilan to'liq framework: ORM, admin, auth, migratsiya;
   tez va xavfsiz prototip + prod.
2. **Nega qatlamli arxitektura?** - Mas'uliyatlar ajratiladi, test osonlashadi,
   biznes logika view'dan mustaqil (`services.py`).
3. **Double-booking qanday bartaraf etiladi?** - `transaction.atomic` +
   `select_for_update` bilan serializatsiya, overlap tekshiruvi, PostgreSQL'da
   `ExclusionConstraint` yakuniy kafolat.
4. **`s1<e2 AND s2<e1` nima?** - Ikki yarim-ochiq vaqt oralig'ining kesishish sharti.
5. **Nega SQLite va PostgreSQL ikkisi ham?** - Lokal/test uchun tez SQLite; prod va
   CI uchun PostgreSQL (exclusion constraint). Kod ikkalasiga mos (NFR-11).
6. **Exclusion constraint SQLite'da-chi?** - Shartli migratsiya faqat Postgres'da
   qo'llanadi; SQLite'da service-darajadagi tekshiruv kafolat beradi.
7. **Holat mashinasi qanday ishlaydi?** - `ALLOWED_TRANSITIONS` jadvali; noqonuniy
   o'tishda `InvalidTransitionError`.
8. **2 soat qoidasi?** - Bron boshlanishiga < 2 soat qolsa, bekor qilish rad etiladi.
9. **RBAC qanday?** - `User.role` (ADMIN/MANAGER/CUSTOMER/WAITER) + DRF permissions +
   view mixinlari.
10. **Menejer boshqa kafega aralasha oladimi?** - Yo'q, `_require_cafe_manager`
    kafe egaligini tekshiradi.
11. **Sharh qoidalari?** - Faqat COMPLETED bron, faqat egasi, faqat bir marta.
12. **Qamrov qanday ta'minlanadi?** - `pytest --cov`, `fail_under = 80`; CI darvozasi.
13. **Qancha test bor?** - 80+ test funksiyasi (modellar, servislar, view, API,
    permission, edge-case, seed).
14. **Edge-case'lar?** - off-hours, o'tmish, sig'im, double-booking, ruxsatsiz
    kirish (403), 2 soat bekor qilish, noqonuniy holat o'tishi.
15. **Nega multi-stage Dockerfile?** - Build artefaktlarini runtime image'dan
    ajratadi: kichik, xavfsiz (non-root), compilers yo'q.
16. **HEALTHCHECK nima uchun?** - Orkestrator konteyner sog'lig'ini `/health/`
    orqali biladi; cd smoke-test ham shunga tayanadi.
17. **CI matritsasi nega 3.11 va 3.12?** - Ikki versiyada ham mosligini kafolatlash.
18. **Qamrov darvozasi qanday ishlaydi?** - < 80% bo'lsa `pytest` chiqish kodi fail,
    CI qizil bo'ladi.
19. **Xavfsizlik skanerlari?** - bandit (kod), pip-audit (CVE), CodeQL (SAST), Trivy (image).
20. **Sirlar qanday boshqariladi?** - `.env` (lokal, git'da yo'q) va GitHub Secrets;
    workflow'lar muhitni dump qilmaydi; `detect-secrets` pre-commit.
21. **cd.yml'da approval qayerda?** - `production` GitHub Environment reviewer
    tasdiqlamaguncha deploy boshlanmaydi.
22. **GHCR teglari?** - `latest`, `sha-<commit>`, `semver` versiya.
23. **Release qanday yaratiladi?** - `v*.*.*` tag push -> `release.yml` CHANGELOG'dan
    bo'lim oladi -> GitHub Release.
24. **UML diagrammalar qanday render bo'ladi?** - `render_diagrams.py` Kroki API'ga
    POST qiladi; tarmoq yo'q bo'lsa manbalarni qoldirib toza chiqadi (exit 0).
25. **Spec-driven jarayon nima?** - requirements -> design -> tasks ketma-ketligi;
    har bosqich tasdiqlanadi, keyin kod yoziladi (Kiro usuli).
