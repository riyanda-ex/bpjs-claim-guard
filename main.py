# BPJS Claim Guard - V1.1 FINAL (100% Aman & Sistematis)
# Input: Data klaim (ID anonim, diagnosis, ICD-10, obat, dokumen)
# Output: Status LAYAK / PERLU PERBAIKAN / DITOLAK + Alasan + Saran
# DISCLAIMER: Alat bantu cek administrasi, BUKAN keputusan resmi BPJS.
# Keputusan akhir ada di BPJS & verifikator. Wajib verifikasi manusia.

import json
import os
import re
from datetime import datetime

class BPJSClaimGuard:
    def __init__(self, config_path="config.json"):
        self.config = self.load_config(config_path)
        self.aturan_icd = self.config.get("aturan_icd", {})
        self.obat_fornas = set(self.config.get("obat_fornas", []))
        self.dokumen_wajib = self.config.get("dokumen_wajib", [])

    def load_config(self, path):
        base = os.path.dirname(__file__)
        full = os.path.join(base, path)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("WARNING: config.json tidak ditemukan, pakai aturan cadangan")
            return {
                "aturan_icd": {"demam": "R50.9"},
                "obat_fornas": ["paracetamol"],
                "dokumen_wajib": ["sep", "resume_medis"]
            }

    def anonymize_id(self, id_klaim):
        if not id_klaim or not str(id_klaim).strip():
            return "KLAIM-000"
        bersih = re.sub(r'[^A-Za-z0-9-_]', '', str(id_klaim).strip())
        return bersih[:20] if bersih else "KLAIM-000"

    def normalisasi_obat(self, nama_obat):
        # FIX V1.1: "Paracetamol 500mg" -> "paracetamol" biar tetap ke-detect Fornas
        # Ambil kata pertama aja, buang dosis & huruf besar
        if not nama_obat:
            return ""
        kata_pertama = str(nama_obat).lower().strip().split()[0] if str(nama_obat).strip() else ""
        return re.sub(r'[^a-z]', '', kata_pertama)

    def cek_klaim(self, id_klaim, diagnosis, kode_icd, daftar_obat, dokumen_ada, simpan=True):
        # Validasi input
        if not diagnosis or not str(diagnosis).strip():
            print("ERROR: Diagnosis kosong, klaim tidak diproses.")
            return None
        if not kode_icd or not str(kode_icd).strip():
            print("ERROR: Kode ICD-10 kosong, klaim tidak diproses.")
            return None

        id_aman = self.anonymize_id(id_klaim)
        diagnosis_bersih = str(diagnosis).lower().strip()
        kode_bersih = str(kode_icd).upper().strip()
        obat_list = [str(o).lower().strip() for o in (daftar_obat or [])]
        dokumen_list = [str(d).lower().strip() for d in (dokumen_ada or [])]

        masalah = []
        saran = []

        # 1. CEK ICD-10 COCOK SAMA DIAGNOSIS?
        kode_benar = self.aturan_icd.get(diagnosis_bersih)
        if kode_benar:
            if kode_benar != kode_bersih:
                masalah.append(f"ICD-10 tidak cocok: {diagnosis} harusnya {kode_benar}, bukan {kode_bersih}")
                saran.append(f"Perbaiki kode ICD-10 jadi {kode_benar}")
        else:
            masalah.append(f"Diagnosis '{diagnosis}' tidak ada di kamus aturan, cek manual ke ICD-10 WHO")
            saran.append("Verifikasi kode ICD-10 ke buku ICD-10 / verifikator BPJS")

        # 2. CEK DOKUMEN WAJIB
        dokumen_kurang = [d for d in self.dokumen_wajib if d not in dokumen_list]
        if dokumen_kurang:
            masalah.append(f"Dokumen kurang: {', '.join(dokumen_kurang)}")
            saran.append(f"Lengkapi dokumen: {', '.join(dokumen_kurang)} sebelum submit")

        # 3. CEK OBAT FORNAS (di luar Fornas = rawan ditolak)
        obat_non_fornas = []
        for o in obat_list:
            if o and self.normalisasi_obat(o) not in self.obat_fornas:
                obat_non_fornas.append(o)
        if obat_non_fornas:
            masalah.append(f"Obat di luar Fornas: {', '.join(obat_non_fornas)}")
            saran.append("Cek Fornas / siapkan justifikasi dokter untuk obat non-Fornas")

        # 4. TENTUKAN STATUS
        if not masalah:
            status = "LAYAK KLAIM"
            skor = 100
        elif len(masalah) == 1 and not dokumen_kurang and kode_benar == kode_bersih:
            # Cuma 1 masalah ringan (misal obat non-Fornas saja)
            status = "PERLU PERBAIKAN"
            skor = 70
        elif dokumen_kurang or (kode_benar and kode_benar != kode_bersih):
            status = "PERLU PERBAIKAN"
            skor = 50
        else:
            status = "DITOLAK - CEK MANUAL"
            skor = 30

        hasil = {
            "id_klaim_anonim": id_aman,
            "tanggal_cek": datetime.now().strftime("%d %B %Y %H:%M"),
            "diagnosis": diagnosis_bersih,
            "kode_icd10_input": kode_bersih,
            "kode_icd10_benar": kode_benar or "-",
            "obat": obat_list,
            "dokumen_ada": dokumen_list,
            "dokumen_kurang": dokumen_kurang,
            "masalah": masalah,
            "saran_perbaikan": saran,
            "status": status,
            "skor_kelayakan": skor,
            "disclaimer": "Alat bantu cek administrasi, BUKAN keputusan resmi BPJS. Wajib verifikasi manusia.",
        }

        self.tampilkan_hasil(hasil)
        if simpan:
            self.simpan_laporan(hasil)
        return hasil

    def simpan_laporan(self, hasil):
        folder = os.path.join(os.path.dirname(__file__), "laporan")
        os.makedirs(folder, exist_ok=True)
        nama_file = f"{hasil['id_klaim_anonim']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(folder, nama_file)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        print(f"Laporan disimpan: {path}")

    def tampilkan_hasil(self, h):
        print("\n========== HASIL CEK KLAIM BPJS ==========")
        print(f"ID Klaim: {h['id_klaim_anonim']}")
        print(f"Tanggal: {h['tanggal_cek']}")
        print(f"Diagnosis: {h['diagnosis']} | ICD-10: {h['kode_icd10_input']} (benar: {h['kode_icd10_benar']})")
        print(f"Obat: {', '.join(h['obat']) if h['obat'] else '-'}")
        print(f"Dokumen Kurang: {', '.join(h['dokumen_kurang']) if h['dokumen_kurang'] else 'Lengkap'}")
        print(f"Status: {h['status']} | Skor: {h['skor_kelayakan']}/100")
        if h['masalah']:
            print("Masalah:")
            for m in h['masalah']:
                print(f" - {m}")
        if h['saran_perbaikan']:
            print("Saran:")
            for s in h['saran_perbaikan']:
                print(f" - {s}")
        print("===========================================")
        print("DISCLAIMER: Bukan keputusan resmi BPJS.")

if __name__ == "__main__":
    print("=== BPJS Claim Guard ===")
    print("DISCLAIMER: Alat bantu cek administrasi, BUKAN keputusan resmi BPJS.")
    guard = BPJSClaimGuard()

    # CONTOH - PAKAI ID ANONIM, BUKAN DATA ASLI
    guard.cek_klaim("KLAIM-001", "demam", "R50.9", ["paracetamol"], ["sep", "resume_medis", "kwitansi"])
    guard.cek_klaim("KLAIM-002", "demam", "J00", ["paracetamol"], ["sep"])
    guard.cek_klaim("KLAIM-003", "hipertensi", "I10", ["amlodipine", "obat_herbal_x"], ["sep", "resume_medis"])
    guard.cek_klaim("KLAIM-004", "diare", "A09.9", ["oralit"], ["sep", "resume_medis", "kwitansi", "hasil_lab"])
