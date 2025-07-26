# File: cpu_scheduler.py
# Deskripsi: Mengimplementasikan mesin penjadwalan CPU.
# Bertanggung jawab atas pengelolaan antrian proses dan pemilihan proses berikutnya
# berdasarkan algoritma FCFS atau Round Robin.
# Dikerjakan oleh: Tim Struktur Data (Backend)

from collections import deque
from core_models import Process

class CPUScheduler:
    """
    Kelas yang mengelola antrian proses dan memutuskan proses mana
    yang akan dieksekusi selanjutnya.
    """
    def __init__(self, algorithm: str, process_list: list[Process]):
        """
        Inisialisasi Penjadwal CPU.
        
        Args:
            algorithm (str): Algoritma yang digunakan ('FCFS' atau 'RR').
            process_list (list[Process]): Daftar semua proses yang akan dijadwalkan.
        """
        if algorithm.upper() not in ['FCFS', 'RR']:
            raise ValueError("Algoritma harus 'FCFS' atau 'RR'")
        
        self.algorithm = algorithm.upper()
        
        # Urutkan proses berdasarkan ID untuk memastikan FCFS bekerja dengan benar
        # jika beberapa proses "datang" bersamaan.
        sorted_processes = sorted(process_list, key=lambda p: p.process_id)
        self.ready_queue = deque(sorted_processes)
        
        # State untuk melacak proses yang sedang berjalan
        self.current_process: Process | None = None
        
        # State khusus untuk Round Robin
        self.time_quantum = 3  # Hardcoded sesuai kesepakatan
        self.quantum_counter = 0

    def select_next_process(self) -> Process | None:
        """
        Fungsi utama yang memilih proses berikutnya untuk dijalankan.
        Ini adalah "pintu depan" ke modul ini.
        
        Returns:
            Process | None: Objek proses yang akan berjalan, atau None jika tidak ada.
        """
        if self.algorithm == 'FCFS':
            return self._select_fcfs()
        elif self.algorithm == 'RR':
            return self._select_rr()
        return None

    def tick(self):
        """
        Fungsi pembantu yang dipanggil setiap "detik" simulasi.
        Hanya relevan untuk Round Robin untuk mengurangi sisa kuantum.
        """
        if self.algorithm == 'RR':
            if self.quantum_counter > 0:
                self.quantum_counter -= 1

    def _select_fcfs(self) -> Process | None:
        """Logika pemilihan untuk FCFS."""
        # Jika tidak ada proses yang berjalan atau proses saat ini sudah selesai
        if self.current_process is None or self.current_process.burst_time_remaining <= 0:
            if not self.ready_queue:
                self.current_process = None
                return None # Tidak ada lagi proses di antrian
            
            # Ambil proses berikutnya dari depan antrian
            self.current_process = self.ready_queue.popleft()
        
        # Kembalikan proses yang sama sampai selesai
        return self.current_process

    def _select_rr(self) -> Process | None:
        """Logika pemilihan untuk Round Robin."""
        quantum_expired = self.quantum_counter <= 0
        process_finished = self.current_process is not None and self.current_process.burst_time_remaining <= 0

        # Kapan kita perlu memilih proses baru?
        # 1. Jika belum ada proses yang berjalan.
        # 2. Jika kuantum waktu proses saat ini sudah habis.
        # 3. Jika proses saat ini sudah selesai (burst time = 0).
        if self.current_process is None or quantum_expired or process_finished:
            
            # Jika ada proses yang sedang berjalan sebelumnya dan belum selesai,
            # kembalikan ia ke akhir antrian.
            if self.current_process and not process_finished:
                self.ready_queue.append(self.current_process)

            # Jika masih ada proses di antrian, ambil yang berikutnya.
            if self.ready_queue:
                self.current_process = self.ready_queue.popleft()
                self.quantum_counter = self.time_quantum # Reset kuantum untuk proses baru
            else:
                self.current_process = None # Tidak ada proses sama sekali
        
        return self.current_process