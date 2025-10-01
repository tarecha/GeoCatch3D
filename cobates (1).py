from modul.mapping import mapping
from modul.seleksiRHD import seleksiRHD
from modul.seleksiBF import seleksiBF
import time


# Contoh penggunaan
lat, lon = -8.5, 112.5
baris, kolom = mapping(lat, lon)
print(f"Baris: {baris}, Kolom: {kolom}")

start_time = time.time()
baris, kolom = seleksiBF(1801.5, 1801.5)
print(f"BF: Baris = {baris}, Kolom = {kolom}")
# Berhenti timer (toc)
end_time = time.time()
# Hitung durasi
elapsed_time = end_time - start_time
print(f"Waktu eksekusi: {elapsed_time:.5f} detik")

start_time = time.time()
baris, kolom = seleksiRHD(1801.55, 1801.5)
print(f"RHD: Baris = {baris}, Kolom = {kolom}")
# Berhenti timer (toc)
end_time = time.time()
# Hitung durasi
elapsed_time = end_time - start_time
print(f"Waktu eksekusi: {elapsed_time:.5f} detik")
