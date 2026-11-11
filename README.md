# 🛡️ BPJS Claim Guard

[Python](https://img.shields.io/badge/Python-3.11-blue)
[Tests](https://github.com/riyanda-ex/bpjs-claim-guard/actions/workflows/test.yml/badge.svg)
[License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red)
[Status](https://img.shields.io/badge/Status-Selesai-green)
[Klinik](https://img.shields.io/badge/Klinik-Al%20Madina%20Husada-teal)

Cek kelayakan klaim BPJS otomatis sebelum submit. Cegah klaim ditolak karena ICD-10 salah, dokumen kurang, atau obat di luar Fornas.

Dibuat untuk Klinik Al Madina Husada, Nganjuk.

> **Disclaimer:** Alat bantu cek administrasi, BUKAN keputusan resmi BPJS. Keputusan akhir ada di BPJS & verifikator. Wajib verifikasi manusia.

## ✨ Fitur
- Cek ICD-10 cocok dengan diagnosis (25+ aturan)
- Cek dokumen wajib: SEP, Resume Medis, Kwitansi
- Cek obat Fornas vs Non-Fornas
- Skor kelayakan 0-100 + Status: LAYAK / PERLU PERBAIKAN / DITOLAK
- Saran perbaikan otomatis
- Simpan laporan JSON ke `laporan/` (ID Anonim)
- 10 Test Otomatis

## 🚀 Cara Pakai
```bash
python main.py
# atau
python test.py
