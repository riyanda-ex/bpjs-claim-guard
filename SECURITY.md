# Keamanan

## Jangan Laporkan Data Klaim Asli di Issue Publik
Jangan pernah upload No. SEP, No. Kartu BPJS, NIK, nama pasien, atau PDF klaim ke GitHub Issue.

## Melaporkan Celah Keamanan
Hubungi pemilik repo melalui GitHub secara privat.
Jelaskan: file yang bermasalah, langkah reproduksi, dan dampaknya.

## Prinsip
- Data klaim asli tidak pernah disimpan di repo ini.
- Hanya ID anonim (`KLAIM-001`) dan contoh sintetis yang boleh di-commit.
- File PDF / Excel klaim diblokir oleh `.gitignore`.
