# BPJS Claim Guard

Jangan sampai klaim BPJS klinik kamu ditolak lagi.

### Masalah
Klinik di Indonesia kehilangan jutaan rupiah setiap bulan karena klaim BPJS ditolak akibat kesalahan kecil: NIK salah, kode diagnosa kosong, atau data tidak lengkap. Kesalahan baru ketahuan setelah 30 hari.

### Solusi
Tool Python ini mengecek file klaim Excel dalam 3 detik SEBELUM dikirim ke BPJS.
Mendeteksi NIK salah, diagnosa kosong, nama kosong, dan biaya 0.

### Teknologi
- Python
- Pandas
- Regex Validation

### Cara Pakai
1. Siapkan file `klaim_bpjs.xlsx` dengan kolom: nik, nama_pasien, kode_diagnosa, biaya
2. Jalankan `python main.py`
3. Perbaiki yang ditandai merah, baru kirim ke BPJS.

### Dampak
Mencegah kerugian klinik dan mempercepat pencairan dana BPJS.
