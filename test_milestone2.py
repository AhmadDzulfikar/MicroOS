# File: test_milestone2.py
# Deskripsi: Script untuk menguji MemoryManager dan algoritma page replacement.

from core_models import Process
from memory_manager import MemoryManager

def print_memory_state(mm: MemoryManager):
    """Fungsi helper untuk mencetak status memori dan antrian algoritma."""
    print(f"  > Memori Fisik: {mm.physical_memory.frames}")
    if mm.algorithm == 'FIFO':
        print(f"  > Antrian FIFO  : {list(mm.fifo_queue)}")
    elif mm.algorithm == 'LRU':
        print(f"  > Tracker LRU   : {mm.lru_tracker} (Kiri=Terlama, Kanan=Terbaru)")


def test_fifo_logic():
    print("\n=========================================")
    print("  [TEST 1] Menguji Logika FIFO           ")
    print("=========================================")
    
    # Setup: 3 frame, algoritma FIFO
    mm = MemoryManager(total_frames=3, replacement_algorithm='FIFO')
    
    Process.reset_id_counter()
    p0 = Process(burst_time=5, process_size=8192) # 2 halaman
    p1 = Process(burst_time=5, process_size=8192) # 2 halaman
    mm.register_process(p0)
    mm.register_process(p1)

    print("Langkah 1: Mengisi memori hingga penuh...")
    
    # P0:H0 -> F0
    result1 = mm.access_page(p0, 0)
    print(f"Akses P0:H0 -> Status: {result1['status']}, Frame: {result1['loaded_into_frame']}")
    
    # P0:H1 -> F1
    result2 = mm.access_page(p0, 1)
    print(f"Akses P0:H1 -> Status: {result2['status']}, Frame: {result2['loaded_into_frame']}")

    # P1:H0 -> F2
    result3 = mm.access_page(p1, 0)
    print(f"Akses P1:H0 -> Status: {result3['status']}, Frame: {result3['loaded_into_frame']}")

    print("\nKeadaan setelah memori penuh:")
    print_memory_state(mm)
    assert mm.physical_memory.is_full()
    
    print("\nLangkah 2: Memicu Page Replacement...")
    # Akses P1:H1. Memori sudah penuh.
    # Korban FIFO seharusnya adalah yang pertama masuk: P0:H0 di Frame 0.
    result4 = mm.access_page(p1, 1)
    
    print(f"Akses P1:H1 -> Status: {result4['status']}")
    print(f"  > Halaman baru dimuat ke Frame: {result4['loaded_into_frame']}")
    print(f"  > Halaman yang diusir: {result4['evicted_page_info']}")
    
    print("\nKeadaan akhir memori:")
    print_memory_state(mm)

    # Verifikasi
    assert result4['loaded_into_frame'] == 0, "Seharusnya frame 0 yang digunakan kembali."
    assert result4['evicted_page_info']['process_id'] == 'P0', "Proses yang diusir salah."
    assert result4['evicted_page_info']['page_number'] == 0, "Halaman yang diusir salah."
    print("\n✅ Verifikasi FIFO BERHASIL.")


def test_lru_logic():
    print("\n=========================================")
    print("  [TEST 2] Menguji Logika LRU            ")
    print("=========================================")
    
    # Setup: 3 frame, algoritma LRU
    mm = MemoryManager(total_frames=3, replacement_algorithm='LRU')

    Process.reset_id_counter()
    p0 = Process(burst_time=5, process_size=8192) # 2 halaman
    p1 = Process(burst_time=5, process_size=8192) # 2 halaman
    mm.register_process(p0)
    mm.register_process(p1)
    
    print("Langkah 1: Mengisi memori...")
    mm.access_page(p0, 0) # P0:H0 -> F0. LRU: [0]
    mm.access_page(p0, 1) # P0:H1 -> F1. LRU: [0, 1]
    mm.access_page(p1, 0) # P1:H0 -> F2. LRU: [0, 1, 2]. Memori penuh.
    
    print("Keadaan setelah memori penuh:")
    print_memory_state(mm)
    
    print("\nLangkah 2: Melakukan akses yang mengubah urutan LRU (Page Hit)...")
    # Akses P0:H0 lagi. Ini ada di Frame 0.
    # Seharusnya ini memindahkan Frame 0 ke posisi paling baru (paling kanan).
    # Urutan LRU harusnya menjadi [1, 2, 0].
    result_hit = mm.access_page(p0, 0)
    print(f"Akses P0:H0 -> Status: {result_hit['status']}")
    print("Keadaan setelah Page Hit:")
    print_memory_state(mm)
    assert mm.lru_tracker == [1, 2, 0], "Update LRU saat HIT salah!"

    print("\nLangkah 3: Memicu Page Replacement...")
    # Akses P1:H1. Memori penuh.
    # Korban LRU seharusnya adalah yang paling lama tidak digunakan: Frame 1.
    result_fault = mm.access_page(p1, 1)

    print(f"Akses P1:H1 -> Status: {result_fault['status']}")
    print(f"  > Halaman baru dimuat ke Frame: {result_fault['loaded_into_frame']}")
    print(f"  > Halaman yang diusir: {result_fault['evicted_page_info']}")
    
    print("\nKeadaan akhir memori:")
    print_memory_state(mm)

    # Verifikasi
    assert result_fault['loaded_into_frame'] == 1, "Seharusnya frame 1 yang digunakan kembali."
    assert result_fault['evicted_page_info']['process_id'] == 'P0', "Proses yang diusir salah."
    assert result_fault['evicted_page_info']['page_number'] == 1, "Halaman yang diusir salah."
    print("\n✅ Verifikasi LRU BERHASIL.")

if __name__ == "__main__":
    test_fifo_logic()
    test_lru_logic()