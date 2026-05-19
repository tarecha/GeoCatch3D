import rasterio
import numpy as np
from modul import config as cfg
import matplotlib.pyplot as plt
plt.switch_backend('qt5agg')

from whitebox.whitebox_tools import WhiteboxTools  # Library untuk analisis geospasial


# Raster tampilan


#menghitung panjang x lebar visualsisasi menggunakan epsg EPSG:4326
# Ambil path direktori sementara dari konfigurasi
temp_dir = cfg.pathTempMaps

# Inisialisasi alat WhiteboxTools
wbt = WhiteboxTools()


wbt.extract_streams(flow_accum=cfg.fileFlowAccumulationBreachD8, output=cfg.fileExtractstreamsHulu,zero_background=True, threshold=50)
wbt.extract_streams(flow_accum=cfg.fileFlowAccumulationBreachMDInf, output=cfg.fileExtractstreamsHuluMDINF,zero_background=True, threshold=50)

# path ke file GeoTIFF input
input_path = cfg.fileFlowAccumulationBreachD8
input_path2 = cfg.fileFlowAccumulationBreachMDInf
output_path = cfg.fileExtractstreamsHulu255MDINF

# baca file GeoTIFF
with rasterio.open(input_path) as src:
    data = src.read(1)  # baca band pertama
    profile = src.profile  # simpan metadata
    print(f"dtype {data.dtype}")
    print(f"MIN {np.min(data)}")
    print(f"max {np.max(data)}")
    print(f"dtype {data.dtype}")
    print(f"MIN {np.min(data)}")

    with rasterio.open(input_path2) as src:
        data2 = src.read(1)  # baca band pertama
        profile2 = src.profile  # simpan metadata
        print(f"dtype {data.dtype}")
        print(f"MIN {np.min(data)}")
        print(f"max {np.max(data)}")
        print(f"dtype {data.dtype}")
        print(f"MIN {np.min(data)}")

# ubah nilai 1 jadi 255
print(f"MAX data {np.max(data)}")
data_255 = np.where(data > 0, 1, 0).astype(np.int8)
data_255MDINF = np.where(data2 > 0, 5, 0).astype(np.int8)
#data_255 = np.where(data_255 < 0, 0, data)
print(f"MIN data_255 {np.min(data_255)}")
print(f"MAX data_255 {np.max(data_255)}")
print(f"MIN data_255MDINF {np.min(data_255MDINF)}")
print(f"MAX data_255MDINF {np.max(data_255MDINF)}")
print(f"dtype {data_255.dtype}")
# sesuaikan tipe data output (agar tidak terlalu besar)
profile.update(nodata=0 )

# tulis hasil ke file baru
with rasterio.open(output_path, 'w', **profile) as dst:
    dst.write(data_255, 1)


print("Selesai. File hasil disimpan di:", output_path)


mask = data > 0

# gabungkan dua array di area yang bernilai > 0
combined = np.zeros_like(data, dtype=np.int8)
combined[mask] = data_255[mask] + data_255MDINF[mask]

# hasilnya: area 0 tetap 0, area >0 berisi nilai kombinasi
fig, axes = plt.subplots(1, 2, figsize=(12, 6))

# plot kiri: data_255
im1 = axes[0].imshow(np.where(mask, data_255, np.nan), cmap='Blues')
axes[0].set_title("data_255 (nilai > 0 = biru)")
fig.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)

# plot kanan: data_255MDINF
im2 = axes[1].imshow(np.where(mask, data_255MDINF, np.nan), cmap='Reds')
axes[1].set_title("data_255MDINF (nilai > 0 = merah)")
fig.colorbar(im2, ax=axes[1], fraction=0.046, pad=0.04)

# rapikan layout
plt.tight_layout()
plt.show()