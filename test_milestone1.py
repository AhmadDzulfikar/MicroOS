# File: test_milestone1.py
# Deskripsi: Script untuk menguji kelas-kelas model data dari core_models.py.
# Ini adalah cara Tim Struktur Data memastikan fondasi bekerja sebelum melanjutkan
# ke milestone berikutnya.

from core_models import PhysicalMemory, Process, Statistics, PAGE_SIZE

def run_tests():
    """Menjalankan serangkaian tes untuk memverifikasi model data."""
    
    print("=========================================")
    print("  MEMULAI PENGUJIAN MILESTONE 1 (BACKEND)  ")
    print("=========================================")

    # --- 1. Menguji Kelas Process (Revisi V2) ---
    print("\n[TEST 1] Menguji Kelas Process...")
    
    # Skenario: Ukuran proses tidak pas dengan ukuran halaman
    # 10000 bytes / 4096 bytes/page = 2.44 -> harus dibulatkan menjadi 3 halaman.
    test_process_size = 10000
    expected_num_pages = math.ceil(test_process_size / PAGE_SIZE)
    
    # Reset ID counter untuk hasil yang konsisten setiap kali tes dijalankan
    Process.reset_id_counter()
    
    p0 = Process(burst_time=8, process_size=test_process_size)
    
    print(f"  Proses baru dibuat: {p0}")
    print(f"  Ukuran proses yang diberikan: {test_process_size} bytes")
    print(f"  Ukuran halaman (PAGE_SIZE): {PAGE_SIZE} bytes")
    print(f"  Jumlah halaman yang dihitung: {p0.num_pages} (Diharapkan: {expected_num_pages})")
    
    # Verifikasi
    assert p0.num_pages == expected_num_pages, "Perhitungan jumlah halaman salah!"
    assert len(p0.page_table) == expected_num_pages, "Ukuran Page Table tidak cocok!"
    print("  ✅ Verifikasi jumlah halaman dan page table BERHASIL.")

    print(f"  Urutan akses halaman (dibuat acak): {p0.page_access_sequence}")
    print(f"  Panjang urutan akses: {len(p0.page_access_sequence)} (Diharapkan sama dengan burst_time: {p0.burst_time_total})")
    assert len(p0.page_access_sequence) == p0.burst_time_total, "Panjang urutan akses salah!"
    print("  ✅ Verifikasi urutan akses halaman BERHASIL.")

    # Uji proses kedua untuk memastikan ID counter bekerja
    p1 = Process(burst_time=5, process_size=16384) # 16384 bytes = 4 halaman pas
    print(f"\n  Membuat proses kedua: {p1}")
    assert p1.process_id == "P1", "Auto-increment ID tidak bekerja!"
    assert p1.num_pages == 4, "Perhitungan halaman untuk ukuran pas salah!"
    print("  ✅ Verifikasi ID counter dan perhitungan halaman pas BERHASIL.")

    # --- 2. Menguji Kelas PhysicalMemory ---
    print("\n[TEST 2] Menguji Kelas PhysicalMemory...")
    mem = PhysicalMemory(total_frames=8)
    print(f"  Memori awal: {mem}")
    print(f"  Memori penuh? {mem.is_full()}")
    assert not mem.is_full()
    
    empty_idx = mem.get_empty_frame_index()
    print(f"  Indeks frame kosong pertama: {empty_idx}")
    assert empty_idx == 0
    
    mem.frames[0] = {'process_id': 'P0', 'page_number': 0}
    print(f"  Memori setelah frame 0 diisi: {mem}")
    assert mem.get_empty_frame_index() == 1
    print("  ✅ Verifikasi PhysicalMemory BERHASIL.")

    # --- 3. Menguji Kelas Statistics ---
    print("\n[TEST 3] Menguji Kelas Statistics...")
    stats = Statistics()
    print(f"  Statistik awal: {stats}")
    assert stats.total_accesses == 0
    
    stats.increment_hits()
    stats.increment_faults()
    stats.increment_hits()
    print(f"  Statistik setelah 2 Hit, 1 Fault: {stats}")
    assert stats.total_accesses == 3
    assert stats.hits == 2
    assert stats.page_faults == 1
    assert abs(stats.get_hit_ratio() - (2/3)) < 0.001 # Cek float
    print(f"  Hit Ratio: {stats.get_hit_ratio():.2%}")
    
    stats.reset()
    print(f"  Statistik setelah di-reset: {stats}")
    assert stats.total_accesses == 0
    print("  ✅ Verifikasi Statistics BERHASIL.")
    
    print("\n=========================================")
    print("  SEMUA TES MILESTONE 1 BERHASIL!        ")
    print("=========================================")


if __name__ == "__main__":
    # Import math untuk pengujian
    import math
    run_tests()