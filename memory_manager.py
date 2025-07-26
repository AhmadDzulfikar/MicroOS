# File: memory_manager.py
# Deskripsi: Mengimplementasikan mesin manajemen memori virtual.
# Bertanggung jawab atas translasi, penanganan page fault, dan algoritma page replacement.
# Dikerjakan oleh: Tim Struktur Data (Backend)

from collections import deque
from core_models import PhysicalMemory, Process

class MemoryManager:
    """
    Kelas utama untuk mengelola memori.
    Ini adalah "otak" di balik semua operasi memori.
    """
    def __init__(self, total_frames: int, replacement_algorithm: str):
        """
        Inisialisasi Memory Manager.
        
        Args:
            total_frames (int): Jumlah total frame di memori fisik.
            replacement_algorithm (str): Algoritma yang digunakan ('FIFO' atau 'LRU').
        """
        if replacement_algorithm.upper() not in ['FIFO', 'LRU']:
            raise ValueError("Algoritma harus 'FIFO' atau 'LRU'")
            
        self.physical_memory = PhysicalMemory(total_frames)
        self.algorithm = replacement_algorithm.upper()
        
        # Struktur data untuk membantu algoritma page replacement
        # self.processes akan dibutuhkan untuk men-set valid bit jadi 0 saat eviksi
        self.processes = {} 
        
        # Antrian untuk melacak urutan kedatangan frame (untuk FIFO)
        self.fifo_queue = deque()
        # List untuk melacak urutan penggunaan frame (untuk LRU)
        # Indeks 0 = paling lama tidak digunakan, Indeks terakhir = paling baru digunakan
        self.lru_tracker = []

    def register_process(self, process: Process):
        """Menambahkan proses ke dalam daftar yang dikelola oleh MMU."""
        self.processes[process.process_id] = process

    def access_page(self, process: Process, page_number: int) -> dict:
        """
        Fungsi utama yang menjadi "pintu depan" untuk semua akses memori.
        Mencoba mengakses halaman untuk sebuah proses.
        
        Returns:
            dict: Sebuah dictionary yang berisi hasil dari operasi akses.
        """
        # --- Langkah 1: Cek Page Table untuk Page Hit atau Page Fault ---
        page_table_entry = process.page_table.get(page_number)
        
        if page_table_entry and page_table_entry[1] == 1:  # valid_bit == 1
            # --- PAGE HIT ---
            frame_number = page_table_entry[0]
            if self.algorithm == 'LRU':
                self._update_lru_tracker(frame_number)
                
            return {
                "status": "HIT",
                "process_id": process.process_id,
                "page_number": page_number,
                "frame_number": frame_number
            }
        
        else:
            # --- PAGE FAULT ---
            # Cek apakah ada frame kosong
            if not self.physical_memory.is_full():
                target_frame = self.physical_memory.get_empty_frame_index()
                self._load_page_to_frame(process, page_number, target_frame)
                return {
                    "status": "FAULT",
                    "process_id": process.process_id,
                    "page_number": page_number,
                    "loaded_into_frame": target_frame,
                    "evicted_page_info": None # Tidak ada yang diusir
                }
            else:
                # Memori penuh, perlu page replacement
                if self.algorithm == 'FIFO':
                    victim_frame = self._run_fifo_replacement()
                else: # LRU
                    victim_frame = self._run_lru_replacement()
                
                # Dapatkan info halaman lama sebelum ditimpa
                evicted_info = self.physical_memory.frames[victim_frame].copy()
                
                # Usir halaman lama
                self._evict_page_from_frame(victim_frame)
                
                # Muat halaman baru ke frame korban
                self._load_page_to_frame(process, page_number, victim_frame)
                
                return {
                    "status": "FAULT",
                    "process_id": process.process_id,
                    "page_number": page_number,
                    "loaded_into_frame": victim_frame,
                    "evicted_page_info": evicted_info
                }

    # --- Fungsi Helper Internal (Private Methods) ---

    def _load_page_to_frame(self, process: Process, page_number: int, frame_number: int):
        """Memuat halaman ke frame fisik dan mengupdate semua struktur data."""
        # 1. Update memori fisik
        self.physical_memory.frames[frame_number] = {
            "process_id": process.process_id,
            "page_number": page_number
        }
        
        # 2. Update page table proses
        process.page_table[page_number][0] = frame_number
        process.page_table[page_number][1] = 1 # Set valid bit
        
        # 3. Update struktur data algoritma
        if self.algorithm == 'FIFO' and frame_number not in self.fifo_queue:
            self.fifo_queue.append(frame_number)
        
        if self.algorithm == 'LRU':
            self._update_lru_tracker(frame_number)

    def _evict_page_from_frame(self, frame_number: int):
        """Membersihkan frame dan men-set page table lama menjadi tidak valid."""
        page_info = self.physical_memory.frames[frame_number]
        if not page_info: return
        
        process_id = page_info['process_id']
        page_number = page_info['page_number']
        
        # Dapatkan objek proses lama dari daftar terdaftar
        old_process = self.processes.get(process_id)
        if old_process:
            # Set page table-nya menjadi tidak valid
            old_process.page_table[page_number][0] = None
            old_process.page_table[page_number][1] = 0
            
        # Kosongkan frame di memori fisik
        self.physical_memory.frames[frame_number] = None

    def _update_lru_tracker(self, accessed_frame: int):
        """Memindahkan frame yang diakses ke akhir list (paling baru)."""
        if accessed_frame in self.lru_tracker:
            self.lru_tracker.remove(accessed_frame)
        self.lru_tracker.append(accessed_frame)

    def _run_fifo_replacement(self) -> int:
        """Menentukan frame korban berdasarkan FIFO."""
        # Frame korban adalah yang paling depan di antrian
        victim_frame = self.fifo_queue.popleft()
        return victim_frame

    def _run_lru_replacement(self) -> int:
        """Menentukan frame korban berdasarkan LRU."""
        # Frame korban adalah yang paling awal di list (paling lama tidak digunakan)
        victim_frame = self.lru_tracker.pop(0)
        return victim_frame