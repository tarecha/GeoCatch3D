# %{
# kolom
# 0          1800          3600
# -------------------------- 1
# |          | |           |
# |   1      |6|     2     |
# |          | |           |
# --------------------------
# |   9      |5|     7     | 1801  baris
# --------------------------
# |          | |           |
# |   4      |8|     3     |
# |          | |           |
# -------------------------- 3601

# ukuran matrix 3601. titik tengah = (3601 + 1) / 2 = 1801
# posisi titik utama adalah 1 2 3 4
# posisi titik yang memungkinkan pas di tengah adalah 5 6 7 8 9


# A = | A1 A2 |
#     | A4 A3 |


# file GDEM ASTER hanya memuat data elevasi, jika laut maka nilainya 0
# untuk wilayah 1 x 1 derajat yang 1 file semua merupakan laut maka file
# itu tidak disediakan. oleh karena itu file yang tidak ada maka wilayah
# laut diberi matrix 3601 x 3601 bernilai 0.
# %}


#improvemen menyimpan max 8 tile file dalam ram. jadi di lokasi yang sama tidak perlu baca dari
#disk terus. menghemat waktu. memori kurang lebih 200 mb dipakai

import numpy as np
import rasterio
import os
from functools import lru_cache
from modul.generateFile import generateFileDEM


# 1. Fungsi inti yang dibungkus lru_cache (Hanya jalan jika data TIDAK ADA di RAM)
@lru_cache(maxsize=8)
def _baca_harddisk(file_path):
    if os.path.exists(file_path):
        with rasterio.open(file_path) as src:
            print(f"💾 Membaca dari HDD: {file_path}")
            return src.read(1)
    else:
        print(f"⚠️ File tidak ada, membuat array 0: {file_path}")
        return np.zeros((3601, 3601), dtype=np.int16)


# 2. Fungsi perantara untuk mendeteksi dan memunculkan tulisan (HDD vs RAM)
def readgeoraster(file_path):
    # Cek rekam jejak memori (hits) sebelum fungsi dijalankan
    hits_sebelum = _baca_harddisk.cache_info().hits

    # Jalankan pencarian file
    fileDEM = _baca_harddisk(file_path)

    # Cek rekam jejak memori (hits) setelah fungsi dijalankan
    hits_sesudah = _baca_harddisk.cache_info().hits

    # Jika angka hits bertambah, berarti data berhasil "dicuri" dari RAM!
    if hits_sesudah > hits_sebelum:
        print(f"⚡ Membaca dari RAM: {file_path}")

    return fileDEM

def pilih(baris, kolom, latitude, longitude):
    """Fungsi untuk memilih dan menggabungkan 4 file DEM sesuai posisi baris dan kolom."""
    if (baris < 1800) and (kolom < 1800):  # 1
        fileA1 = generateFileDEM(latitude + 1, longitude - 1)
        fileA2 = generateFileDEM(latitude + 1, longitude)
        fileA3 = generateFileDEM(latitude, longitude)
        fileA4 = generateFileDEM(latitude, longitude - 1)
        baris += 3600
        kolom += 3600
        #print("#1")
    elif (baris < 1800) and (kolom > 1800):  # 2
        fileA1 = generateFileDEM(latitude + 1, longitude)
        fileA2 = generateFileDEM(latitude + 1, longitude + 1)
        fileA3 = generateFileDEM(latitude, longitude + 1)
        fileA4 = generateFileDEM(latitude, longitude)
        baris += 3600
        #print("#2")
    elif (baris > 1800) and (kolom > 1800):  # 3
        fileA1 = generateFileDEM(latitude, longitude)
        fileA2 = generateFileDEM(latitude, longitude + 1)
        fileA3 = generateFileDEM(latitude - 1, longitude + 1)
        fileA4 = generateFileDEM(latitude - 1, longitude)

        #print("#3")
    elif (baris > 1800) and (kolom < 1800):  # 4
        fileA1 = generateFileDEM(latitude, longitude - 1)
        fileA2 = generateFileDEM(latitude, longitude)
        fileA3 = generateFileDEM(latitude - 1, longitude)
        fileA4 = generateFileDEM(latitude - 1, longitude - 1)
        kolom += 3600
        #print("#4")
    elif (baris == 1800) and (kolom == 1800):  # 5
        fileA1 = generateFileDEM(latitude + 1, longitude - 1)
        fileA2 = generateFileDEM(latitude + 1, longitude)
        fileA3 = generateFileDEM(latitude, longitude)
        fileA4 = generateFileDEM(latitude, longitude - 1)
        baris += 3600
        kolom += 3600
        #print("#5")
    elif (baris < 1800) and (kolom == 1800):  # 6
        fileA1 = generateFileDEM(latitude + 1, longitude)
        fileA2 = generateFileDEM(latitude + 1, longitude + 1)
        fileA3 = generateFileDEM(latitude, longitude + 1)
        fileA4 = generateFileDEM(latitude, longitude)
        baris += 3600
        #print("#6")
    elif (baris == 1800) and (kolom > 1800):  # 7
        fileA1 = generateFileDEM(latitude, longitude)
        fileA2 = generateFileDEM(latitude, longitude + 1)
        fileA3 = generateFileDEM(latitude - 1, longitude + 1)
        fileA4 = generateFileDEM(latitude - 1, longitude)
        #print("#7")
    elif (baris > 1800) and (kolom == 1800):  # 8
        fileA1 = generateFileDEM(latitude, longitude - 1)
        fileA2 = generateFileDEM(latitude, longitude)
        fileA3 = generateFileDEM(latitude - 1, longitude)
        fileA4 = generateFileDEM(latitude - 1, longitude - 1)
        kolom += 3600
        #print("#8")
    elif (baris == 1800) and (kolom < 1800):  # 9
        fileA1 = generateFileDEM(latitude + 1, longitude - 1)
        fileA2 = generateFileDEM(latitude + 1, longitude)
        fileA3 = generateFileDEM(latitude, longitude)
        fileA4 = generateFileDEM(latitude, longitude - 1)
        baris += 3600
        kolom += 3600
        #print("#9")
    else:
        fileA1 = generateFileDEM(latitude + 1, longitude - 1)
        fileA2 = generateFileDEM(latitude + 1, longitude)
        fileA3 = generateFileDEM(latitude, longitude)
        fileA4 = generateFileDEM(latitude, longitude - 1)
        baris += 3600
        kolom += 3600
        #print("#10")


    print(f"fileA1 : {fileA1}")
    print(f"fileA2 : {fileA2}")
    print(f"fileA3 : {fileA3}")
    print(f"fileA4 : {fileA4}")
    # Baca data dari file atau isi dengan nol jika file tidak ada
    A1 = readgeoraster(fileA1)
    A2 = readgeoraster(fileA2)
    A3 = readgeoraster(fileA3)
    A4 = readgeoraster(fileA4)
    #print(f"baris : {baris}, kolom : {kolom}, A1 : {A1[baris,kolom]}")
    A1 = A1[:, :]
    A2 = A2[:, 1:]
    A4 = A4[1:, :]
    A3 = A3[1:, 1:]

    # Gabungkan 4 kuadran
    A = np.block([[A1, A2], [A4, A3]])
    ketinggianmax = np.max(A)
    print(f"ketinggianmax {ketinggianmax}")
    if ketinggianmax == 0:
        raise ValueError(f"Tidak ditemukan daratan. Cek input koordinat apakah lautan ? atau cek keberadaan file dataset GDEM ASTER. {fileA1} {fileA2} {fileA3} {fileA4}")

    return A, baris, kolom