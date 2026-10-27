# Hissa qo'shish bo'yicha qo'llanma (Contributing)

TableReserve loyihasiga hissa qo'shganingiz uchun rahmat! Ushbu hujjat ishlab
chiqish jarayoni, kod uslubi va PR qoidalarini tushuntiradi.

## Muhitni sozlash

```bash
python -m venv .venv && source .venv/bin/activate
make install          # requirements/dev.txt
make migrate
make seed              # demo ma'lumotlar
make run               # http://127.0.0.1:8000
```

## Branch strategiyasi

- `main` — barqaror, relizga tayyor kod (himoyalangan branch).
- `develop` — integratsiya branchi.
- `feature/<qisqa-nom>` — yangi funksiya.
- `fix/<qisqa-nom>` — xatolik tuzatish.

Ish oqimi: `feature/*` -> PR -> `develop` -> PR -> `main`.

## Kod uslubi

- Kod, identifikatorlar va commit xabarlari **ingliz tilida**.
- Interfeys matni va hujjatlar **o'zbek (lotin)** tilida.
- Biznes-logika `services.py` ichida; view'lar yupqa.
- Formatlash va lint: `ruff` (`make format`, `make lint`).
- Tiplar: `mypy` (`make typecheck`).
- Har bir dependency `==` bilan qat'iy pin qilinadi (NFR-10).

## Commit uslubi (Conventional Commits)

```
feat: yangi funksiya
fix: xatolik tuzatish
docs: hujjat
refactor: qayta tuzish
test: testlar
ci: CI/CD
chore: boshqa
```

## Testlar

```bash
make test             # pytest --cov, qamrov >= 80%
```

Yangi yoki o'zgargan xatti-harakat testlar bilan qoplanishi shart.

## Pull Request

1. `make lint && make typecheck && make test` lokal toza bo'lsin.
2. PR shablonini to'ldiring (`.github/PULL_REQUEST_TEMPLATE.md`).
3. Tegishli issue/talab (FR/NFR) ga havola qiling.
4. CI yashil bo'lgach, kod egalari (CODEOWNERS) ko'rib chiqadi.

## Sirlar (secrets)

Hech qachon maxfiy kalit, parol yoki token kodga qo'shmang. Ularni faqat
`.env` (lokal) yoki GitHub Secrets (CI) orqali bering. `.env` git'ga tushmaydi.
