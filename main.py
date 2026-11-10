import pandas as pd
import re

def cek_klaim(file_excel):
    df = pd.read_excel(file_excel)
    masalah = []

    for i, row in df.iterrows():
        baris = i + 2  # +2 karena header + index 0
        
        # 1. Cek NIK harus 16 digit angka
        nik = str(row.get('nik', ''))
        if not re.match(r'^\d{16}$', nik):
            masalah.append(f"Baris {baris}: NIK {nik} salah, harus 16 digit angka")
        
        # 2. Cek Kode Diagnosa harus ada (ICD-10)
        diagnosa = str(row.get('kode_diagnosa', ''))
        if diagnosa == '' or diagnosa == 'nan':
            masalah.append(f"Baris {baris}: Kode diagnosa kosong, klaim pasti ditolak!")

        # 3. Cek Nama Pasien kosong
        if pd.isna(row.get('nama_pasien')):
            masalah.append(f"Baris {baris}: Nama pasien kosong")

        # 4. Cek Biaya tidak boleh 0
        if row.get('biaya', 0) == 0:
            masalah.append(f"Baris {baris}: Biaya 0, cek lagi")

    # Laporan
    print("=== HASIL CEK KLAIM BPJS ===")
    if not masalah:
        print("AMAN! Semua data valid, siap kirim ke BPJS.")
    else:
        print(f"DITEMUKAN {len(masalah)} MASALAH:")
        for m in masalah:
            print(f"- {m}")
        print(f"\nPotensi uang terselamatkan: Rp {len(masalah) * 150000:,}")

    return masalah

# Cara pakai
if __name__ == "__main__":
    cek_klaim('klaim_bpjs.xlsx')
