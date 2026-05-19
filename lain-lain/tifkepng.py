import rasterio
import numpy as np
from PIL import Image
from modul import config as cfg

# Path input dan output
#input_tif = cfg.fileExtractstreamsHulu
#output_png = cfg.fileExtractstreamsPNG

input_tif = r"D:\cc\perbandingan demnas dataran tinggi\tif_stream.tif"
#input_tif = tif_streammdinf
output_png = r"D:\cc\perbandingan demnas dataran tinggi\tif_streamdemnassetaraaster50sebelahbiru.tif"

with rasterio.open(input_tif) as src:
    data = src.read(1)  # band pertama
    mask = src.dataset_mask()  # mask valid (jika ada NoData)

# Buat array RGBA (4 channel)
rgba = np.zeros((data.shape[0], data.shape[1], 4), dtype=np.uint8)

# Jika nilai = 1 → merah penuh
rgba[data == 1] = [00, 80, 216, 255]  # merah solid

# Nilai selain 1 → transparan (alpha = 0)
rgba[data != 1] = [0, 0, 0, 0]

# Jika ada mask rasterio (opsional), buat transparan juga
if mask is not None:
    rgba[mask == 0] = [0, 0, 0, 0]

# --- Tambahan: titik kuning ---
h, w = data.shape
points = [
    (h // 2, w // 2),      # tengah
    (0, 0),                # kiri atas
    (h - 1, w - 1)         # kanan bawah
]

for (y, x) in points:
    rgba[y, x] = [255, 0, 0, 255]  # kuning (R=255, G=255, B=0, A=255)

# Simpan sebagai PNG
Image.fromarray(rgba, mode="RGBA").save(output_png)

print("✅ Selesai! File PNG disimpan di:", output_png)
print("📍 Titik kuning ditambahkan di:")
print(f"   - Tengah: ({points[0][1]}, {points[0][0]})")
print(f"   - Kiri atas: ({points[1][1]}, {points[1][0]})")
print(f"   - Kanan bawah: ({points[2][1]}, {points[2][0]})")