# File: test_milestone3.py
# Deskripsi: Script untuk menguji CPUScheduler dan algoritma FCFS & RR.

from core_models import Process
from cpu_scheduler import CPUScheduler

def test_fcfs_scheduler():
    print("\n=========================================")
    print("  [TEST 1] Menguji Logika FCFS           ")
    print("=========================================")
    
    # Setup
    Process.reset_id_counter()
    p0 = Process(burst_time=3, process_size=4096)
    p1 = Process(burst_time=4, process_size=4096)
    process_list = [p0, p1]
    
    scheduler = CPUScheduler(algorithm='FCFS', process_list=process_list)
    
    execution_order = []
    total_time = p0.burst_time_total + p1.burst_time_total # Total 7 "detik"

    print("Memulai simulasi FCFS...")
    for time_step in range(total_time):
        current_p = scheduler.select_next_process()
        if current_p:
            execution_order.append(current_p.process_id)
            current_p.burst_time_remaining -= 1 # Simulasikan kerja
            print(f"Detik {time_step}: Menjalankan {current_p.process_id}, sisa burst: {current_p.burst_time_remaining}")
            
    print("\nUrutan eksekusi yang dihasilkan:", execution_order)
    expected_order = ['P0', 'P0', 'P0', 'P1', 'P1', 'P1', 'P1']
    print("Urutan eksekusi yang diharapkan:", expected_order)
    
    # Verifikasi
    assert execution_order == expected_order, "Urutan eksekusi FCFS salah!"
    print("\n✅ Verifikasi FCFS BERHASIL.")

def test_rr_scheduler():
    print("\n=========================================")
    print("  [TEST 2] Menguji Logika Round Robin (RR) ")
    print("=========================================")
    
    # Setup
    Process.reset_id_counter()
    p0 = Process(burst_time=5, process_size=4096)
    p1 = Process(burst_time=4, process_size=4096)
    process_list = [p0, p1]
    
    scheduler = CPUScheduler(algorithm='RR', process_list=process_list)
    
    execution_order = []
    # Total waktu bisa lebih lama jika ada idle, tapi kita asumsikan berjalan terus
    total_time = p0.burst_time_total + p1.burst_time_total # Total 9 "detik"

    print(f"Memulai simulasi RR (Time Quantum = {scheduler.time_quantum})...")
    for time_step in range(total_time):
        current_p = scheduler.select_next_process()
        if current_p:
            execution_order.append(current_p.process_id)
            current_p.burst_time_remaining -= 1
            print(f"Detik {time_step}: Menjalankan {current_p.process_id}, sisa burst: {current_p.burst_time_remaining}, sisa kuantum: {scheduler.quantum_counter}")
            # PENTING: Panggil tick() setelah setiap langkah
            scheduler.tick()

    print("\nUrutan eksekusi yang dihasilkan:", execution_order)
    # P0 (3), P1 (3), P0 (2), P1 (1)
    expected_order = ['P0', 'P0', 'P0', 'P1', 'P1', 'P1', 'P0', 'P0', 'P1']
    print("Urutan eksekusi yang diharapkan:", expected_order)

    # Verifikasi
    assert execution_order == expected_order, "Urutan eksekusi RR salah!"
    print("\n✅ Verifikasi Round Robin BERHASIL.")


if __name__ == "__main__":
    test_fcfs_scheduler()
    test_rr_scheduler()