# Xavfsizlik siyosati (Security Policy)

## Qo'llab-quvvatlanadigan versiyalar

| Versiya | Qo'llab-quvvatlanadi |
|---------|----------------------|
| 1.x     | ✅                   |

## Zaiflik haqida xabar berish

Xavfsizlik zaifligini topsangiz, iltimos uni **ommaviy issue sifatida
ochmang**. Buning o'rniga repo egasiga shaxsiy (private) xabar yuboring yoki
GitHub Security Advisory orqali maxfiy xabar bering.

Xabarda quyidagilarni kiriting:

- Zaiflik tavsifi va ta'sir doirasi.
- Takrorlash qadamlari (PoC).
- Ta'sirlangan versiya(lar).

Biz 72 soat ichida javob berishga va tasdiqlangan zaiflikni imkon qadar tez
tuzatishga harakat qilamiz.

## Xavfsizlik amaliyotlari

- Barcha sirlar GitHub Secrets / `.env` orqali beriladi, kodga yozilmaydi (NFR-02).
- CI'da `bandit`, `pip-audit`, CodeQL va Trivy skanerlari ishlaydi (`security.yml`, `docker.yml`).
- Dependabot bog'liqliklarni muntazam yangilaydi.
- Prod sozlamalari HTTPS redirect, HSTS, secure cookie va `X-Frame-Options: DENY` ni yoqadi.
- `detect-secrets` pre-commit hooki sirlarni commitdan oldin ushlaydi.
