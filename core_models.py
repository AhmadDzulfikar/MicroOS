# File: core_models.py
# Deskripsi: Fondasi model data untuk Simulator Sistem Operasi (UPDATE V2).
# Berisi kelas-kelas untuk Memori, Proses, dan Statistik.
# Dikerjakan oleh: Tim Struktur Data (Backend)

import math
import random

# Konstanta sistem yang disepakati bersama.
# Ukuran setiap halaman/frame dalam byte. 4KB adalah nilai yang umum.
PAGE_SIZE = 4096

class PhysicalMemory:
    """
    Merepresentasikan memori fisik (RAM) dalam simulasi.
    Terdiri dari kumpulan frame berukuran tetap.
    """
    def __init__(self, total_frames: int):
        self.size = total_frames
        self.frames = [None] * self.size

    def is_full(self) -> bool:
        """Mengecek apakah semua frame di memori sudah terisi."""
        return None not in self.frames

    def get_empty_frame_index(self) -> int:
        """
        Mencari dan mengembalikan indeks dari frame kosong pertama.
        Returns:
            int: Indeks frame kosong, atau -1 jika tidak ada.
        """
        try:
            return self.frames.index(None)
        except ValueError:
            return -1

    def __repr__(self) -> str:
        """Representasi string untuk debugging."""
        filled_count = self.size - self.frames.count(None)
        return f"PhysicalMemory(size={self.size}, filled_frames={filled_count})"

# ---

class Process:
    """
    Merepresentasikan sebuah proses (Revisi V2).
    Dibuat dengan ukuran (size) dan dikonversi menjadi jumlah halaman.
    Memiliki urutan akses halaman yang dibuat secara acak.
    """
    _id_counter = 0

    def __init__(self, burst_time: int, process_size: int):
        """
        Args:
            burst_time (int): Total waktu yang dibutuhkan proses untuk selesai.
            process_size (int): Ukuran total proses dalam byte.
        """
        self.process_id = f"P{Process._id_counter}"
        Process._id_counter += 1
        
        self.burst_time_total = burst_time
        self.burst_time_remaining = burst_time
        
        # Logika konversi dari ukuran proses ke jumlah halaman
        if process_size <= 0:
            raise ValueError("Ukuran proses harus lebih besar dari 0")
        self.num_pages = math.ceil(process_size / PAGE_SIZE)
        
        # Membuat urutan akses halaman secara acak
        # Proses akan meminta 'burst_time' halaman selama masa hidupnya.
        self.page_access_sequence = random.choices(range(self.num_pages), k=self.burst_time_total)
        self.access_step = 0
        
        self.status = 'ready' # Status awal: 'ready', 'running', 'terminated'
        
        # Page Table: {nomor_halaman_virtual: [nomor_frame_fisik, valid_bit]}
        self.page_table = {i: [None, 0] for i in range(self.num_pages)}

    def get_next_page_to_access(self) -> int | None:
        """Mengambil halaman berikutnya yang perlu diakses dari urutan."""
        if self.access_step < len(self.page_access_sequence):
            page = self.page_access_sequence[self.access_step]
            self.access_step += 1
            return page
        return None

    @classmethod
    def reset_id_counter(cls):
        """Me-reset counter ID, berguna untuk tombol reset di UI."""
        cls._id_counter = 0

    def __repr__(self) -> str:
        """Representasi string untuk debugging."""
        return (f"Process(id={self.process_id}, status='{self.status}', "
                f"burst_rem={self.burst_time_remaining}, pages={self.num_pages})")

# ---

class Statistics:
    """Kelas terpisah untuk melacak dan mengelola statistik performa."""
    def __init__(self):
        self.total_accesses = 0
        self.page_faults = 0
        self.hits = 0

    def increment_faults(self):
        """Mencatat terjadinya sebuah page fault."""
        self.total_accesses += 1
        self.page_faults += 1
        
    def increment_hits(self):
        """Mencatat terjadinya sebuah page hit."""
        self.total_accesses += 1
        self.hits += 1

    def get_hit_ratio(self) -> float:
        """Menghitung hit ratio saat ini (0.0 hingga 1.0)."""
        if self.total_accesses == 0:
            return 0.0
        return self.hits / self.total_accesses

    def reset(self):
        """Mengembalikan semua statistik ke nilai awal."""
        self.total_accesses = 0
        self.page_faults = 0
        self.hits = 0

    def __repr__(self) -> str:
        """Representasi string untuk debugging."""
        hit_ratio_percent = self.get_hit_ratio() * 100
        return (f"Statistics(Accesses={self.total_accesses}, Faults={self.page_faults}, "
                f"Hits={self.hits}, HitRatio={hit_ratio_percent:.2f}%)")