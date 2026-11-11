import json
import os
import re
from datetime import datetime


class BPJSClaimGuard:
    def __init__(self, config_path="config.json"):
        self.base_dir = self._get_base_dir()
        self.config = self.load_config(config_path)

        # FIX 2: Normalisasi data dari config.json agar kebal huruf besar/kecil
        raw_icd = self.config.get("aturan_icd", {})
        self.aturan_icd = {
            str(k).lower().strip(): str(v).upper().strip()
            for k, v in raw_icd.items()
        }

        raw_obat = self.config.get("obat_fornas", [])
        self.obat_fornas = {
            self.normalisasi_obat(o) for o in raw_obat if str(o).strip()
        }

        raw_dok = self.config.get("dokumen_wajib", [])
        self.dokumen_wajib = [
            str(d).lower().strip() for d in raw_dok if str(d).strip()
        ]

    def _get_base_dir(self):
        # FIX 1: Aman dijalankan baik sebagai file .py maupun di interactive shell/Jupyter
        try:
            return os.path.dirname(os.path.abspath(__file__))
        except NameError:
            return os.getcwd()

    def load_config(self, path):
        full = os.path.join(self.base_dir, path)
        fallback = {
            "aturan_icd": {"demam": "R50.9"},
            "obat_fornas": ["paracetamol"],
            "dokumen_wajib": ["sep", "resume_medis"],
        }
        try:
            with open(full, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print("[WARNING] config.json tidak ditemukan, pakai aturan cadangan.")
            return fallback
        except json.JSONDecodeError:
            # FIX 5A: Mencegah crash jika format JSON rusak
            print("[WARNING] Format config.json rusak, pakai aturan cadangan.")
            return fallback

    def anonymize_id(self, id_klaim):
        if not id_klaim or not str(id_klaim).strip():
            return "KLAIM-000"
        bersih = re.sub(r"[^A-Za-z0-9_-]", "", str(id_klaim).strip())
        return bersih[:20] if bersih else "KLAIM-000"

    def normalisasi_obat(self, nama_obat):
        """
        FIX 4: Mendukung nama obat lebih dari 1 kata (misal: 'Asam Mefenamat 500mg' -> 'asam mefenamat')
        dengan menghapus dosis dan satuan medis, bukan memotong kata pertama.
        """
        if not nama_obat:
            return ""
        teks = str(nama_obat).lower().strip()
        # Hapus angka beserta satuan dosis umum (mg, ml, g, mcg, tab, kap, syr, inj, %)
        teks = re.sub(r"\b\d+(?:[.,]\d+)?\s*(?:mg|ml|g|gr|mcg|iu|tab|kap|kapsul|syr|inj|%)?\b", "", teks)
        # Hapus karakter non-alfabet kecuali spasi
        teks = re.sub(r"[^a-z\s]", "", teks)
        # Rapikan spasi berlebih
        return " ".join(teks.split())

    def cek_klaim(self, id_klaim, diagnosis, kode_icd, daftar_obat, dokumen_ada, simpan=True):
        # Validasi input dasar
        if not diagnosis or not str(diagnosis).strip():
            print("[ERROR] Diagnosis kosong, klaim tidak diproses.")
            return None
        if not kode_icd or not str(kode_icd).strip():
            print("[ERROR] Kode ICD-10 kosong, klaim tidak diproses.")
            return None

        # FIX 5B: Jaga-jaga jika input daftar_obat / dokumen_ada berupa string tunggal, bukan list
        if isinstance(daftar_obat, str):
            daftar_obat = [daftar_obat]
        if isinstance(dokumen_ada, str):
            dokumen_ada = [dokumen_ada]

        id_aman = self.anonymize_id(id_klaim)
        diagnosis_bersih = str(diagnosis).lower().strip()
        kode_bersih = str(kode_icd).upper().strip()
        obat_list = [str(o).lower().strip() for o in (daftar_obat or []) if str(o).strip()]
        dokumen_list = [str(d).lower().strip() for d in (dokumen_ada or []) if str(d).strip()]

        masalah = []
        saran = []

        # 1. CEK ICD-10 COCOK SAMA DIAGNOSIS
        kode_benar = self.aturan_icd.get(diagnosis_bersih)
        icd_salah = False
        if kode_benar:
            if kode_benar != kode_bersih:
                icd_salah = True
                masalah.append(f"ICD-10 tidak cocok: '{diagnosis}' harusnya {kode_benar}, bukan {kode_bersih}")
                saran.append(f"Perbaiki kode ICD-10 jadi {kode_benar}")
        else:
            masalah.append(f"Diagnosis '{diagnosis}' tidak ada di kamus aturan (cek manual ke ICD-10 WHO)")
            saran.append("Verifikasi kode ICD-10 ke buku ICD-10 / verifikator BPJS")

        # 2. CEK DOKUMEN WAJIB
        dokumen_kurang = [d for d in self.dokumen_wajib if d not in dokumen_list]
        if dokumen_kurang:
            masalah.append(f"Dokumen kurang: {', '.join(dokumen_kurang)}")
            saran.append(f"Lengkapi dokumen ({', '.join(dokumen_kurang)}) sebelum submit")

        # 3. CEK OBAT FORNAS
        obat_non_fornas = []
        for o in obat_list:
            if self.normalisasi_obat(o) not in self.obat_fornas:
                obat_non_fornas.append(o)
        if obat_non_fornas:
            masalah.append(f"Obat di luar Fornas: {', '.join(obat_non_fornas)}")
            saran.append("Cek Fornas / siapkan justifikasi dokter untuk obat non-Fornas")

        # 4. TENTUKAN STATUS (FIX 3: Logika bertingkat yang lebih akurat)
        if not masalah:
            status = "LAYAK KLAIM"
            skor = 100
        elif len(masalah) == 1 and obat_non_fornas and not dokumen_kurang and not icd_salah and kode_benar:
            # Hanya masalah ringan: obat di luar Fornas saja
            status = "PERLU PERBAIKAN"
            skor = 70
        elif (dokumen_kurang and icd_salah) or len(masalah) >= 3 or not kode_benar:
            # Masalah berat/kombinasi fatal
            status = "DITOLAK / CEK MANUAL"
            skor = 30
        else:
            # Hanya 1 masalah administrasi (dokumen kurang saja ATAU kode ICD salah saja)
            status = "PERLU PERBAIKAN"
            skor = 50

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
        folder = os.path.join(self.base_dir, "laporan")
        os.makedirs(folder, exist_ok=True)
        # Tambahkan mikrodetik (%f) agar tidak tertimpa jika mengecek 2 klaim dalam 1 detik yang sama
        nama_file = f"hasil_{hasil['id_klaim_anonim']}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.json"
        path = os.path.join(folder, nama_file)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(hasil, f, indent=2, ensure_ascii=False)
        print(f"  Laporan disimpan: {path}")

    def tampilkan_hasil(self, h):
        print("\n" + "=" * 55)
        print("  HASIL CEK KLAIM BPJS")
        print("=" * 55)
        print(f"  ID Klaim       : {h['id_klaim_anonim']}")
        print(f"  Tanggal        : {h['tanggal_cek']}")
        print(f"  Diagnosis      : {h['diagnosis']} | ICD-10: {h['kode_icd10_input']} (benar: {h['kode_icd10_benar']})")
        print(f"  Obat           : {', '.join(h['obat']) if h['obat'] else '-'}")
        print(f"  Dokumen Kurang : {', '.join(h['dokumen_kurang']) if h['dokumen_kurang'] else 'Lengkap'}")
        print(f"  Status         : {h['status']} (Skor: {h['skor_kelayakan']}/100)")
        if h["masalah"]:
            print("  Masalah:")
            for m in h["masalah"]:
                print(f"    - {m}")
        if h["saran_perbaikan"]:
            print("  Saran:")
            for s in h["saran_perbaikan"]:
                print(f"    -> {s}")
        print("=" * 55)
        print("  DISCLAIMER: Bukan keputusan resmi BPJS.")
