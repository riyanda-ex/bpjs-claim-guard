# Test otomatis - BPJS Claim Guard V1.1
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from main import BPJSClaimGuard

def test(nama, kondisi):
    print(f"{'✅' if kondisi else '❌'} {nama}")
    return kondisi

if __name__ == "__main__":
    print("=== TEST BPJS Claim Guard ===\n")
    g = BPJSClaimGuard()
    hasil = []

    # 1. Klaim sempurna -> LAYAK
    r1 = g.cek_klaim("KLAIM-TEST-1", "demam", "R50.9", ["paracetamol"], ["sep", "resume_medis", "kwitansi"], simpan=False)
    hasil.append(test("1. Klaim sempurna -> LAYAK KLAIM", r1["status"] == "LAYAK KLAIM" and r1["skor_kelayakan"] == 100))
    # 2. ICD salah -> PERLU PERBAIKAN
    r2 = g.cek_klaim("KLAIM-TEST-2", "demam", "J00", ["paracetamol"], ["sep", "resume_medis", "kwitansi"], simpan=False)
    hasil.append(test("2. ICD salah ketahuan", "tidak cocok" in " ".join(r2["masalah"]).lower() and r2["status"] == "PERLU PERBAIKAN"))
    # 3. Dokumen kurang -> ketahuan
    r3 = g.cek_klaim("KLAIM-TEST-3", "demam", "R50.9", ["paracetamol"], ["sep"], simpan=False)
    hasil.append(test("3. Dokumen kurang ketahuan", "resume_medis" in r3["dokumen_kurang"] and "kwitansi" in r3["dokumen_kurang"]))
    # 4. Obat non-Fornas ketahuan
    r4 = g.cek_klaim("KLAIM-TEST-4", "hipertensi", "I10", ["obat_herbal_x"], ["sep", "resume_medis", "kwitansi"], simpan=False)
    hasil.append(test("4. Obat non-Fornas ketahuan", any("fornas" in m.lower() for m in r4["masalah"])))
    # 5. Diagnosis kosong ditolak
    r5 = g.cek_klaim("KLAIM-TEST-5", "", "R50.9", [], [], simpan=False)
    hasil.append(test("5. Diagnosis kosong ditolak", r5 is None))
    # 6. ICD kosong ditolak
    r6 = g.cek_klaim("KLAIM-TEST-6", "demam", "", [], [], simpan=False)
    hasil.append(test("6. ICD kosong ditolak", r6 is None))
    # 7. Anonimisasi
    r7 = g.cek_klaim("Klaim Budi!!!", "demam", "R50.9", ["paracetamol"], ["sep", "resume_medis", "kwitansi"], simpan=False)
    hasil.append(test("7. ID dianonimkan", " " not in r7["id_klaim_anonim"] and "!" not in r7["id_klaim_anonim"]))
    # 8. Disclaimer ada
    hasil.append(test("8. Disclaimer ada", "bukan keputusan resmi" in r1["disclaimer"].lower()))
    # 9. Saran perbaikan ada saat ada masalah
    hasil.append(test("9. Saran perbaikan ada", len(r2["saran_perbaikan"]) >= 1))
    # 10. Config terload - FIX V1.1: aturan_icd
    hasil.append(test("10. Config terload", "demam" in g.aturan_icd and len(g.obat_fornas) >= 5))
    # 11. BONUS V1.1: Obat dengan dosis tetap ke-detect Fornas
    r11 = g.cek_klaim("KLAIM-TEST-11", "demam", "R50.9", ["Paracetamol 500mg"], ["sep", "resume_medis", "kwitansi"], simpan=False)
    hasil.append(test("11. Obat 'Paracetamol 500mg' tetap Fornas", r11["status"] == "LAYAK KLAIM"))

    lulus = sum(hasil)
    print(f"\nHASIL: {lulus}/{len(hasil)} lulus")
    if lulus == len(hasil):
        print("🎉 SEMUA TEST LULUS!")
    else:
        print("⚠️ Ada test gagal, cek di atas.")
        sys.exit(1)
